"""
classify_from_kaggle.py

Matches "clean" scraped records against the official Kaggle LeetCode dataset to
extract actual topic tags, saving the cost of AI classification.

Matching Strategy:
1. leetcodeUrl match (most reliable)
2. exact title match (fallback)
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import os
import sys
import argparse
import logging
import ast
import pandas as pd
from pymongo import UpdateOne
from dotenv import load_dotenv
from config.db import get_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("classify_kaggle")

# Canonical topic mapping: Kaggle raw tags → our 18 standard categories
# This ensures consistent topic names across all classification methods
TOPIC_MAP = {
    # Arrays
    "Array": "Arrays", "Matrix": "Arrays", "Prefix Sum": "Arrays",
    # Strings
    "String": "Strings", "String Matching": "Strings",
    "Rolling Hash": "Strings", "Suffix Array": "Strings",
    # Linked Lists
    "Linked List": "Linked Lists", "Doubly-Linked List": "Linked Lists",
    # Trees
    "Tree": "Trees", "Binary Tree": "Trees", "Binary Search Tree": "Trees",
    "Trie": "Trees", "Segment Tree": "Trees", "Binary Indexed Tree": "Trees",
    # Graphs
    "Graph": "Graphs", "Breadth-First Search": "Graphs",
    "Depth-First Search": "Graphs", "Union Find": "Graphs",
    "Shortest Path": "Graphs", "Topological Sort": "Graphs",
    "Minimum Spanning Tree": "Graphs", "Strongly Connected Component": "Graphs",
    "Biconnected Component": "Graphs", "Eulerian Circuit": "Graphs",
    # Dynamic Programming
    "Dynamic Programming": "Dynamic Programming", "Memoization": "Dynamic Programming",
    # Greedy
    "Greedy": "Greedy",
    # Binary Search
    "Binary Search": "Binary Search", "Divide and Conquer": "Binary Search",
    # Hash Tables
    "Hash Table": "Hash Tables", "Hash Function": "Hash Tables", "Counting": "Hash Tables",
    # Sorting
    "Sorting": "Sorting", "Merge Sort": "Sorting", "Bucket Sort": "Sorting",
    "Counting Sort": "Sorting", "Radix Sort": "Sorting", "Quickselect": "Sorting",
    # Stacks & Queues
    "Stack": "Stacks & Queues", "Queue": "Stacks & Queues",
    "Monotonic Stack": "Stacks & Queues", "Monotonic Queue": "Stacks & Queues",
    "Heap (Priority Queue)": "Stacks & Queues",
    # Two Pointers
    "Two Pointers": "Two Pointers", "Sliding Window": "Two Pointers",
    # Backtracking
    "Backtracking": "Backtracking", "Recursion": "Backtracking",
    # Bit Manipulation
    "Bit Manipulation": "Bit Manipulation", "Bitmask": "Bit Manipulation",
    # Math
    "Math": "Math", "Number Theory": "Math", "Geometry": "Math",
    "Combinatorics": "Math", "Probability and Statistics": "Math", "Game Theory": "Math",
    # System Design
    "Design": "System Design", "Data Stream": "System Design",
    "Concurrency": "System Design", "Iterator": "System Design", "Interactive": "System Design",
    # Databases
    "Database": "Databases", "Shell": "Databases",
}

def map_topics(raw_topics: list) -> list:
    """Convert Kaggle raw tags to canonical names, deduplicate, skip unmapped as 'Other'."""
    canonical = set()
    has_unmapped = False
    for t in raw_topics:
        mapped = TOPIC_MAP.get(t)
        if mapped:
            canonical.add(mapped)
        else:
            has_unmapped = True
    if has_unmapped and not canonical:
        canonical.add("Other")
    return sorted(list(canonical))

def normalize_url(url: str) -> str:
    if not url or pd.isna(url):
        return ""
    # Strip trailing slashes and common differences
    url = url.strip().rstrip('/')
    url = url.replace("http://", "https://")
    # Sometimes URLs have /description at the end, remove it
    if url.endswith("/description"):
        url = url[:-12]
    return url

def normalize_title(title: str) -> str:
    if not title or pd.isna(title):
        return ""
    return title.strip().lower()

def run(dry_run: bool = False):
    load_dotenv()
    db = get_db()
    
    csv_path = "leetcode_problems.csv"
    if not os.path.exists(csv_path):
        logger.error(f"Dataset not found at {csv_path}. Please download it from Kaggle.")
        return

    logger.info("Loading Kaggle LeetCode Dataset...")
    df = pd.read_csv(csv_path)
    
    # Build lookup dictionaries for O(1) matching
    url_to_topics = {}
    title_to_topics = {}
    
    for _, row in df.iterrows():
        try:
            # Safely evaluate "['Array', 'Hash Table']" string into a list
            topics_str = str(row.get("topics", "[]"))
            if topics_str == "nan":
                topics = []
            else:
                topics = ast.literal_eval(topics_str)
        except Exception:
            topics = []
            
        url = normalize_url(str(row.get("url", "")))
        title = normalize_title(str(row.get("title", "")))
        
        if url:
            url_to_topics[url] = topics
        if title:
            title_to_topics[title] = topics
            
    logger.info(f"Loaded {len(url_to_topics)} unique URLs and {len(title_to_topics)} unique titles from Kaggle dataset.")
    
    # Query MongoDB for unclassified 'clean' records
    query = {"status": "clean"}
    cursor = db.raw_scraped_data.find(query)
    records = list(cursor)
    
    logger.info(f"Found {len(records)} 'clean' records in MongoDB ready for classification.")
    if not records:
        return
        
    matched_by_url = 0
    matched_by_title = 0
    unmatched = 0
    
    bulk_ops = []
    sample_matches = []
    
    for record in records:
        db_url = normalize_url(record.get("leetcodeUrl", ""))
        db_title = normalize_title(record.get("problemSummary", ""))
        
        assigned_topics = None
        
        if db_url and db_url in url_to_topics:
            raw = url_to_topics[db_url]
            assigned_topics = map_topics(raw)
            matched_by_url += 1
            if len(sample_matches) < 10 and assigned_topics:
                sample_matches.append(f"[{record.get('companySlug')}] {db_title} => {assigned_topics}")
        elif db_title and db_title in title_to_topics:
            raw = title_to_topics[db_title]
            assigned_topics = map_topics(raw)
            matched_by_title += 1
            if len(sample_matches) < 10 and assigned_topics:
                sample_matches.append(f"[{record.get('companySlug')}] {db_title} => {assigned_topics}")
        else:
            unmatched += 1
            
        if assigned_topics is not None:
            if not dry_run:
                bulk_ops.append(
                    UpdateOne(
                        {"_id": record["_id"]},
                        {"$set": {
                            "status": "classified",
                            "topics": assigned_topics
                        }}
                    )
                )
                
    total_matched = matched_by_url + matched_by_title
    logger.info(f"=== DRY RUN RESULTS ===" if dry_run else f"=== CLASSIFICATION RESULTS ===")
    logger.info(f"Total clean records evaluated: {len(records)}")
    logger.info(f"Matched by Leetcode URL: {matched_by_url}")
    logger.info(f"Matched by Exact Title:  {matched_by_title}")
    logger.info(f"Total Successfully Matched: {total_matched} ({(total_matched/len(records))*100:.1f}%)")
    logger.info(f"Unmatched (remains 'clean'): {unmatched}")
    
    if dry_run and sample_matches:
        logger.info("=== SAMPLE MATCHES (First 10) ===")
        for s in sample_matches:
            logger.info(s)
            
    if not dry_run and bulk_ops:
        logger.info(f"Executing {len(bulk_ops)} bulk updates in MongoDB...")
        # Execute in chunks of 1000
        total_modified = 0
        for i in range(0, len(bulk_ops), 1000):
            chunk = bulk_ops[i:i+1000]
            result = db.raw_scraped_data.bulk_write(chunk, ordered=False)
            total_modified += result.modified_count
        logger.info(f"Successfully marked {total_modified} records as 'classified'.")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Report counts without writing to DB")
    args = parser.parse_args()
    
    run(dry_run=args.dry_run)
