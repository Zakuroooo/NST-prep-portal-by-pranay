"""
promote.py

Promotes every "classified" record from raw_scraped_data into the final
questions collection, matching the Question.ts Mongoose schema exactly.

Fields mapped:
  companyId        ← raw_scraped_data.companyId
  companySlug      ← raw_scraped_data.companySlug
  companyName      ← looked up from companies collection
  roundType        ← raw_scraped_data.roundType (default "Coding")
  problemSummary   ← raw_scraped_data.problemSummary
  difficulty       ← raw_scraped_data.difficulty (default "Medium")
  topics           ← raw_scraped_data.topics
  source           ← raw_scraped_data.sourceId → human-readable label
  sourceUrl        ← raw_scraped_data.sourceUrl
  leetcodeUrl      ← raw_scraped_data.leetcodeUrl
  frequencyScore   ← 0.0 (to be updated by aggregate.py)
  xpValue          ← 10 (default)
  isHot            ← False
  verified         ← False
  isSeeded         ← True
"""

import sys
import argparse
import logging
from pymongo import InsertOne, UpdateOne
from bson import ObjectId
from dotenv import load_dotenv
from config.db import get_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("promote")

SOURCE_LABELS = {
    1: "github/snehasishroy-leetcode-companywise",
    3: "github/krishnadey30-leetcode-companywise",
}

VALID_ROUND_TYPES = {"Coding", "System Design", "HR", "Aptitude", "LLD", "Domain", "Managerial"}
VALID_DIFFICULTIES = {"Easy", "Medium", "Hard"}


def run(dry_run: bool = False):
    load_dotenv()
    db = get_db()

    # Build company lookup: _id -> {slug, name}
    logger.info("Building company lookup map...")
    companies = list(db.companies.find({}, {"_id": 1, "slug": 1, "name": 1}))
    company_by_id = {str(c["_id"]): c for c in companies}
    logger.info(f"Loaded {len(company_by_id)} companies.")

    # Build set of already-promoted (problemSummary + companySlug) to skip duplicates
    logger.info("Loading already-promoted question keys...")
    existing = db.questions.find({}, {"problemSummary": 1, "companySlug": 1, "_id": 0})
    promoted_keys = {(q["companySlug"], q["problemSummary"].strip().lower()) for q in existing}
    logger.info(f"Found {len(promoted_keys)} questions already in questions collection.")

    # Fetch all classified records
    records = list(db.raw_scraped_data.find({"status": "classified"}))
    logger.info(f"Found {len(records)} 'classified' records to promote.")

    if not records:
        logger.info("Nothing to promote.")
        return

    to_insert = []
    skipped_duplicate = 0
    skipped_invalid = 0
    raw_ids_to_mark = []
    duplicate_ids_to_mark = []

    for record in records:
        company_id_str = str(record.get("companyId", ""))
        company = company_by_id.get(company_id_str)

        if not company:
            skipped_invalid += 1
            continue

        problem_summary = (record.get("problemSummary") or "").strip()
        if not problem_summary:
            skipped_invalid += 1
            continue

        company_slug = company.get("slug", record.get("companySlug", ""))
        dedup_key = (company_slug, problem_summary.lower())
        if dedup_key in promoted_keys:
            skipped_duplicate += 1
            duplicate_ids_to_mark.append(record["_id"])
            continue

        round_type = record.get("roundType", "Coding")
        if round_type not in VALID_ROUND_TYPES:
            round_type = "Coding"

        difficulty = record.get("difficulty", "Medium")
        if difficulty not in VALID_DIFFICULTIES:
            difficulty = "Medium"

        source_id = record.get("sourceId", 0)
        source_label = SOURCE_LABELS.get(source_id, f"source_{source_id}")

        question_doc = {
            "companyId": record["companyId"],
            "companySlug": company_slug,
            "companyName": company.get("name", ""),
            "roundType": round_type,
            "problemSummary": problem_summary,
            "difficulty": difficulty,
            "topics": record.get("topics", []),
            "source": source_label,
            "sourceUrl": record.get("sourceUrl"),
            "leetcodeUrl": record.get("leetcodeUrl"),
            "frequencyScore": 0.0,
            "xpValue": 10,
            "isHot": False,
            "verified": False,
            "isSeeded": True,
        }

        to_insert.append(question_doc)
        promoted_keys.add(dedup_key)
        raw_ids_to_mark.append(record["_id"])

    total_to_promote = len(to_insert)
    logger.info(f"=== {'DRY RUN' if dry_run else 'LIVE'} RESULTS ===")
    logger.info(f"Classified records evaluated: {len(records)}")
    logger.info(f"Will promote to questions:    {total_to_promote}")
    logger.info(f"Skipped (already promoted):   {skipped_duplicate}")
    logger.info(f"Skipped (invalid/missing data): {skipped_invalid}")

    if dry_run or not to_insert:
        return

    logger.info(f"Inserting {total_to_promote} documents into questions collection...")
    # Insert in chunks of 1000
    total_inserted = 0
    for i in range(0, len(to_insert), 1000):
        chunk = to_insert[i:i+1000]
        result = db.questions.insert_many(chunk, ordered=False)
        total_inserted += len(result.inserted_ids)

    logger.info(f"Inserted {total_inserted} questions.")

    # Mark promoted records in raw_scraped_data
    logger.info(f"Marking {len(raw_ids_to_mark)} records as 'promoted' in raw_scraped_data...")
    mark_ops = [
        UpdateOne({"_id": rid}, {"$set": {"status": "promoted"}})
        for rid in raw_ids_to_mark
    ]
    for i in range(0, len(mark_ops), 1000):
        db.raw_scraped_data.bulk_write(mark_ops[i:i+1000], ordered=False)

    if duplicate_ids_to_mark:
        logger.info(f"Marking {len(duplicate_ids_to_mark)} skipped records as 'duplicate' in raw_scraped_data...")
        dup_ops = [
            UpdateOne({"_id": rid}, {"$set": {"status": "duplicate"}})
            for rid in duplicate_ids_to_mark
        ]
        for i in range(0, len(dup_ops), 1000):
            db.raw_scraped_data.bulk_write(dup_ops[i:i+1000], ordered=False)

    logger.info("Promote complete.")
    logger.info(f"FINAL: {db.questions.count_documents({})} total documents in questions collection.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Report counts without writing to DB")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
