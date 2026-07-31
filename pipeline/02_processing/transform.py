"""
transform.py

Validates pending raw records against the companies collection.
- Match: attaches companyId, sets status="clean"
- No Match: sets status="error", errorType="retryable", errorMessage="Unknown company: [slug]"
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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
logger = logging.getLogger("transformer")

def run_transform(dry_run: bool = False):
    db = get_db()
    
    # Pre-fetch all valid companies to avoid N+1 queries
    logger.info("Fetching valid companies...")
    valid_companies = {c["slug"]: c["_id"] for c in db.companies.find({}, {"slug": 1, "_id": 1})}
    logger.info(f"Loaded {len(valid_companies)} valid companies from database.")
    
    # Query pending records
    pending_count = db.raw_scraped_data.count_documents({"status": "pending"})
    logger.info(f"Found {pending_count} 'pending' records to transform.")
    
    if pending_count == 0:
        return

    clean_count = 0
    error_count = 0
    
    if dry_run:
        logger.info("=== DRY RUN MODE — No database updates ===")
        # Group by slug to quickly summarize outcomes
        pipeline = [
            {"$match": {"status": "pending"}},
            {"$group": {"_id": "$companySlug", "count": {"$sum": 1}}}
        ]
        slug_counts = list(db.raw_scraped_data.aggregate(pipeline))
        
        unknown_slugs = []
        for sc in slug_counts:
            slug = sc["_id"]
            count = sc["count"]
            if slug in valid_companies:
                clean_count += count
            else:
                error_count += count
                unknown_slugs.append((slug, count))
                
        if unknown_slugs:
            logger.warning("The following slugs would error out (Unknown company):")
            for slug, count in sorted(unknown_slugs, key=lambda x: -x[1]):
                logger.warning(f"  - '{slug}': {count} records")
                
        logger.info(f"Dry Run Result: {clean_count} records would become 'clean'.")
        logger.info(f"Dry Run Result: {error_count} records would error out as 'retryable'.")
        return

    # Real run: Use bulk_write
    logger.info("Executing database updates...")
    from pymongo import UpdateOne
    
    bulk_ops = []
    cursor = db.raw_scraped_data.find({"status": "pending"})
    
    for record in cursor:
        slug = record.get("companySlug")
        if slug in valid_companies:
            company_id = valid_companies[slug]
            bulk_ops.append(
                UpdateOne(
                    {"_id": record["_id"]},
                    {"$set": {
                        "status": "clean",
                        "companyId": company_id
                    }}
                )
            )
            clean_count += 1
        else:
            bulk_ops.append(
                UpdateOne(
                    {"_id": record["_id"]},
                    {"$set": {
                        "status": "error",
                        "errorType": "retryable",
                        "errorMessage": f"Unknown company: {slug}"
                    }}
                )
            )
            error_count += 1
            
        # Execute in batches of 1000 to save memory
        if len(bulk_ops) >= 1000:
            db.raw_scraped_data.bulk_write(bulk_ops, ordered=False)
            bulk_ops = []
            
    if bulk_ops:
        db.raw_scraped_data.bulk_write(bulk_ops, ordered=False)
        
    logger.info(f"Successfully marked {clean_count} records as 'clean'.")
    if error_count > 0:
        logger.warning(f"Marked {error_count} records as 'error' due to unknown companies.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transform and validate raw_scraped_data records")
    parser.add_argument("--dry-run", action="store_true", help="Report on transforms without modifying database")
    args = parser.parse_args()
    
    run_transform(dry_run=args.dry_run)
