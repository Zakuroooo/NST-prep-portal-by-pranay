"""
deduplicate.py

Finds and resolves duplicates in the raw_scraped_data staging collection.
A duplicate is defined as records having the same (companySlug, problemSummary, recordType).

Winner selection:
1. Lowest sourcePriority (1 is better than 7).
2. Most recent scrapedAt timestamp.

Non-winners get their status updated to "duplicate".
"""

import logging
import sys
import argparse
from typing import List, Dict, Any
from config.db import get_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("deduplicator")

def find_duplicates(db) -> List[Dict[str, Any]]:
    """
    Returns a list of duplicate groups.
    Each group is a dictionary containing the matching fields and the list of records.
    """
    pipeline = [
        {"$match": {"status": "pending"}},
        {
            "$group": {
                "_id": {
                    "companySlug": "$companySlug",
                    "problemSummary": "$problemSummary",
                    "recordType": "$recordType"
                },
                "count": {"$sum": 1},
                "records": {"$push": "$$ROOT"}
            }
        },
        {"$match": {"count": {"$gt": 1}}}
    ]
    
    logger.info("Aggregating duplicates in MongoDB...")
    duplicate_groups = list(db.raw_scraped_data.aggregate(pipeline, allowDiskUse=True))
    return duplicate_groups

def select_winner(group: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Selects the winning record from a group of duplicates.
    1. Lowest sourcePriority
    2. Most populated fields (highest data completeness)
    3. Most recent scrapedAt
    """
    def count_populated(record):
        return sum(1 for v in record.values() if v is not None and v != "" and v != [])

    def sort_key(record):
        priority = record.get("sourcePriority", 999)
        populated = count_populated(record)
        scraped_at = record.get("scrapedAt")
        ts = scraped_at.timestamp() if scraped_at else 0
        
        # Priority (asc), Populated (desc), ScrapedAt (desc)
        return (priority, -populated, -ts)
        
    sorted_group = sorted(group, key=sort_key)
    return sorted_group[0]

def run_dedup(dry_run: bool = False):
    db = get_db()
    
    duplicate_groups = find_duplicates(db)
    
    total_duplicates_found = sum(group["count"] for group in duplicate_groups)
    total_groups = len(duplicate_groups)
    total_to_mark_duplicate = total_duplicates_found - total_groups
    
    logger.info(f"Found {total_groups} duplicate groups comprising {total_duplicates_found} total records.")
    logger.info(f"Expected to mark {total_to_mark_duplicate} records as 'duplicate'.")
    
    if dry_run:
        logger.info("=== DRY RUN MODE — No database updates ===")
        logger.info("\n--- Sample Duplicate Groups (up to 5) ---")
        
        for i, group in enumerate(duplicate_groups[:5]):
            records = group["records"]
            winner = select_winner(records)
            winner_id = winner["_id"]
            
            logger.info(f"Group {i+1}: company={group['_id']['companySlug']}, summary='{group['_id']['problemSummary'][:60]}'")
            
            for rec in records:
                is_winner = "[WINNER]" if rec["_id"] == winner_id else "[LOSER] "
                logger.info(
                    f"  {is_winner} ID: {rec['_id']} | "
                    f"Source: {rec.get('sourceId')} | "
                    f"Priority: {rec.get('sourcePriority')} | "
                    f"ScrapedAt: {rec.get('scrapedAt')}"
                )
            logger.info("")
            
        return
        
    # Real Run
    logger.info("Executing database updates...")
    
    bulk_ops = []
    from pymongo import UpdateOne
    
    for group in duplicate_groups:
        records = group["records"]
        winner = select_winner(records)
        winner_id = winner["_id"]
        
        merge_updates = {}
        
        for rec in records:
            if rec["_id"] != winner_id:
                # Merge any populated fields from the loser that the winner is missing
                for k, v in rec.items():
                    if k not in ("_id", "sourceId", "sourcePriority", "scrapedAt"):
                        if v is not None and v != "" and v != []:
                            winner_val = winner.get(k)
                            if winner_val is None or winner_val == "" or winner_val == []:
                                merge_updates[k] = v
                                winner[k] = v  # Update local copy so subsequent losers see it
                                
                bulk_ops.append(
                    UpdateOne(
                        {"_id": rec["_id"]},
                        {"$set": {"status": "duplicate"}}
                    )
                )
                
        # If the winner inherited any missing data from losers, update it
        if merge_updates:
            bulk_ops.append(
                UpdateOne(
                    {"_id": winner_id},
                    {"$set": merge_updates}
                )
            )
                
    if bulk_ops:
        result = db.raw_scraped_data.bulk_write(bulk_ops, ordered=False)
        logger.info(f"Successfully marked {result.modified_count} records as 'duplicate'.")
    else:
        logger.info("No duplicates found to update.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate raw_scraped_data records")
    parser.add_argument("--dry-run", action="store_true", help="Report on duplicates without modifying database")
    args = parser.parse_args()
    
    run_dedup(dry_run=args.dry_run)
