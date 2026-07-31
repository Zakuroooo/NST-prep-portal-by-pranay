"""
aggregate.py

Recalculates topicFrequency and difficultyDistribution on every company document 
based on its promoted questions in the `questions` collection.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import sys
import argparse
import logging
import re
from collections import defaultdict
from pymongo import UpdateOne
from dotenv import load_dotenv
from config.db import get_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("aggregate")

def slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r'[^a-z0-9\-]', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

def run(dry_run: bool = False):
    load_dotenv()
    db = get_db()

    logger.info("Fetching all companies...")
    companies = list(db.companies.find({}))
    if not companies:
        logger.error("No companies found.")
        return
        
    company_by_id = {c["_id"]: c for c in companies}
    logger.info(f"Loaded {len(company_by_id)} companies.")

    logger.info("Fetching all questions to calculate aggregations...")
    # We only need companyId, difficulty, topics
    questions = list(db.questions.find({}, {"companyId": 1, "difficulty": 1, "topics": 1}))
    logger.info(f"Loaded {len(questions)} questions.")

    if not questions:
        logger.info("No questions found. Nothing to aggregate.")
        return

    # Aggregate stats per company
    # Stats structure:
    # {
    #    company_id: {
    #        "total_questions": int,
    #        "difficulties": {"Easy": int, "Medium": int, "Hard": int},
    #        "topics": { "Topic Name": int } 
    #    }
    # }
    
    stats = defaultdict(lambda: {
        "total": 0,
        "difficulties": {"Easy": 0, "Medium": 0, "Hard": 0},
        "topics": defaultdict(int)
    })

    for q in questions:
        cid = q.get("companyId")
        if not cid: continue
        
        c_stats = stats[cid]
        c_stats["total"] += 1
        
        diff = q.get("difficulty")
        if diff in c_stats["difficulties"]:
            c_stats["difficulties"][diff] += 1
            
        topics = q.get("topics", [])
        for t in topics:
            c_stats["topics"][t] += 1

    bulk_ops = []
    
    for cid, c_stats in stats.items():
        total = c_stats["total"]
        if total == 0:
            continue
            
        # Calculate Difficulty Distribution as percentages
        diff_dist = {
            "Easy": round((c_stats["difficulties"]["Easy"] / total) * 100, 1),
            "Medium": round((c_stats["difficulties"]["Medium"] / total) * 100, 1),
            "Hard": round((c_stats["difficulties"]["Hard"] / total) * 100, 1)
        }
        
        # Calculate Topic Frequency
        # Sort topics by count descending
        sorted_topics = sorted(c_stats["topics"].items(), key=lambda x: x[1], reverse=True)
        topic_frequency = []
        for topic_name, count in sorted_topics:
            topic_frequency.append({
                "topicSlug": slugify(topic_name),
                "topicName": topic_name,
                "frequencyPct": round((count / total) * 100, 1),
                "questionCount": count
            })
            
        if not dry_run:
            bulk_ops.append(
                UpdateOne(
                    {"_id": cid},
                    {"$set": {
                        "difficultyDistribution": diff_dist,
                        "topicFrequency": topic_frequency
                    }}
                )
            )

    logger.info(f"=== {'DRY RUN' if dry_run else 'LIVE'} RESULTS ===")
    logger.info(f"Companies with questions to aggregate: {len(stats)}")
    
    # Print sample
    if stats:
        sample_cid = list(stats.keys())[0]
        sample_c = company_by_id.get(sample_cid)
        c_name = sample_c["name"] if sample_c else str(sample_cid)
        sample_stats = stats[sample_cid]
        total = sample_stats["total"]
        logger.info(f"Sample Company: {c_name} (Total Questions: {total})")
        logger.info(f"  Difficulty: Easy={round(sample_stats['difficulties']['Easy']/total*100, 1)}% Medium={round(sample_stats['difficulties']['Medium']/total*100, 1)}% Hard={round(sample_stats['difficulties']['Hard']/total*100, 1)}%")
        logger.info(f"  Top 3 Topics: {sorted(sample_stats['topics'].items(), key=lambda x: x[1], reverse=True)[:3]}")

    if not dry_run and bulk_ops:
        logger.info(f"Executing {len(bulk_ops)} bulk updates on companies collection...")
        # Execute in chunks of 1000
        total_modified = 0
        for i in range(0, len(bulk_ops), 1000):
            chunk = bulk_ops[i:i+1000]
            result = db.companies.bulk_write(chunk, ordered=False)
            total_modified += result.modified_count
        logger.info(f"Successfully aggregated {total_modified} companies.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Report stats without writing to DB")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
