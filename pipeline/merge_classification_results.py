"""
merge_classification_results.py

Takes the JSON labels you got back from Claude (pasted into a labels_N.json file)
and writes the "topics" field back into MongoDB for each matching record.

Usage:
    python merge_classification_results.py --batch-number 0
"""

import json
import argparse
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG: must match export_for_classification.py ---
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("MONGO_DB_NAME", "placeprep_staging")
COLLECTION_NAME = "raw_scraped_data"
ID_FIELD = "_id"
# ---------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-number", type=int, required=True)
    parser.add_argument("--dir", type=str, default="classification_batches")
    args = parser.parse_args()

    labels_path = os.path.join(args.dir, f"labels_{args.batch_number}.json")

    if not os.path.exists(labels_path):
        print(f"File not found: {labels_path}")
        print("Make sure you saved Claude's JSON response with this exact filename.")
        return

    with open(labels_path, "r", encoding="utf-8") as f:
        labels = json.load(f)

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    updated = 0
    skipped = 0

    for item in labels:
        try:
            record_id = item["id"]
            topics = item["topics"]

            # Try as ObjectId first (standard Mongo _id), fall back to string id
            try:
                query_id = ObjectId(record_id)
            except Exception:
                query_id = record_id

            result = collection.update_one(
                {ID_FIELD: query_id},
                {"$set": {"topics": topics}}
            )

            if result.matched_count > 0:
                updated += 1
            else:
                skipped += 1
                print(f"Warning: no matching record found for id {record_id}")

        except KeyError as e:
            print(f"Skipping malformed entry (missing {e}): {item}")
            skipped += 1

    print(f"\nDone. Updated: {updated}, Skipped: {skipped}")
    print(f"Batch {args.batch_number} complete. Move to the next batch with:")
    print(f"  python export_for_classification.py --batch-size 100 --skip {(args.batch_number + 1) * 100}")


if __name__ == "__main__":
    main()
