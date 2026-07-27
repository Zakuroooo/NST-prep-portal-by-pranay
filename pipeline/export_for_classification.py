"""
export_for_classification.py

Exports a batch of unclassified questions from MongoDB into a plain JSON file.
You then paste that JSON's contents into a chat with Claude, and Claude returns
topic labels for each record. No API key needed - this uses manual chat.

Usage:
    python export_for_classification.py --batch-size 100 --skip 0

This will create a file like: batch_0.json
Next run: python export_for_classification.py --batch-size 100 --skip 100
(increase --skip each time to move to the next batch)
"""

import json
import argparse
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG: update these to match your project ---
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("MONGO_DB_NAME", "placeprep_staging")
COLLECTION_NAME = "raw_scraped_data"  # actual collection name
FIELD_TO_CLASSIFY = "problemSummary"  # actual field containing the question text
ID_FIELD = "_id"  # usually _id, but use a custom id field if you have one
# ----------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--skip", type=int, default=0)
    parser.add_argument("--output-dir", type=str, default="classification_batches")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Only fetch records that haven't been classified yet
    # Records ready for classification have status="clean"
    query = {"status": "clean"}

    cursor = collection.find(query, {ID_FIELD: 1, FIELD_TO_CLASSIFY: 1}) \
                        .skip(args.skip) \
                        .limit(args.batch_size)

    records = []
    for doc in cursor:
        records.append({
            "id": str(doc[ID_FIELD]),
            "text": doc.get(FIELD_TO_CLASSIFY, "")
        })

    if not records:
        print("No more unclassified records found. You're done!")
        return

    batch_number = args.skip // args.batch_size
    output_path = os.path.join(args.output_dir, f"batch_{batch_number}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(records)} records to: {output_path}")
    print(f"Next step: open this file, copy its contents, and paste them into your chat with Claude")
    print(f"along with this instruction:")
    print()
    print('  "Classify each of these interview questions into ONE topic from this list: '
          'Arrays, Strings, Linked List, Trees, Graphs, Dynamic Programming, Recursion, '
          'Sorting, Searching, Stacks/Queues, Hashing, Greedy, Bit Manipulation, '
          'System Design, OOP, DBMS, Operating Systems, Networking, Behavioral, Other. '
          'Return ONLY a JSON array like [{"id": "...", "topics": ["Arrays"]}] with no explanation."')
    print()
    print(f"Then save Claude's JSON response as: {args.output_dir}/labels_{batch_number}.json")
    print(f"Then run: python merge_classification_results.py --batch-number {batch_number}")


if __name__ == "__main__":
    main()
