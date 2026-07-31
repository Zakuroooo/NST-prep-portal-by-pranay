"""
github_repos.py — Group A file parsers for Source 1 and Source 3.

Source 1: snehasishroy/leetcode-companywise-interview-questions
  Structure: /{company-slug}/all.csv
  Columns:   ID, URL, Title, Difficulty, Acceptance %, Frequency %

Source 3: krishnadey30/LeetCode-Questions-CompanyWise
  Structure: /{company}_{timeframe}.csv (flat, no subdirectories)
  Columns:   ID, Title, Acceptance, Difficulty, Frequency, Leetcode Question Link

Both repos contain LeetCode questions organized by company.
We only parse the "all" / "alltime" CSVs to avoid duplicate counting
within the same source (e.g. "thirty-days" is a subset of "all").
"""

import csv
import os
import logging
import subprocess
import shutil
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Generator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("github_repos")

TEMP_DIR = Path(__file__).parent / "_temp_repos"

REPOS = {
    1: {
        "url": "https://github.com/snehasishroy/leetcode-companywise-interview-questions.git",
        "dir_name": "source_1",
        "source_priority": 4,
    },
    3: {
        "url": "https://github.com/krishnadey30/LeetCode-Questions-CompanyWise.git",
        "dir_name": "source_3",
        "source_priority": 4,
    },
}


def clone_repo(repo_url: str, target_dir: Path) -> bool:
    """Shallow clone a repo. Returns True on success, False if already exists or on error."""
    if target_dir.exists():
        logger.info(f"Repo already cloned at {target_dir}, skipping clone.")
        return True
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
            check=True, capture_output=True, text=True
        )
        logger.info(f"Cloned {repo_url} to {target_dir}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone {repo_url}: {e.stderr}")
        return False


def slugify_company(name: str) -> str:
    """
    Normalize a company name into a consistent slug.
    e.g. "Goldman Sachs" -> "goldman-sachs", "apple" -> "apple"
    """
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\-]', '-', slug)  # Replace non-alphanumeric with hyphens
    slug = re.sub(r'-+', '-', slug)             # Collapse multiple hyphens
    slug = slug.strip('-')                       # Trim leading/trailing hyphens
    return slug


def parse_source_1(repo_dir: Path) -> Generator[Dict[str, Any], None, None]:
    """
    Parse Source 1: snehasishroy/leetcode-companywise-interview-questions
    
    Structure: /{company-slug}/all.csv
    We ONLY read 'all.csv' from each company folder to avoid counting the same
    question multiple times (thirty-days, three-months, six-months are subsets of all).
    
    CSV columns: ID, URL, Title, Difficulty, Acceptance %, Frequency %
    """
    parsed = 0
    skipped = 0
    
    for company_dir in sorted(repo_dir.iterdir()):
        if not company_dir.is_dir() or company_dir.name.startswith('.'):
            continue
            
        all_csv = company_dir / "all.csv"
        if not all_csv.exists():
            logger.warning(f"Source 1: No all.csv found in {company_dir.name}, skipping.")
            skipped += 1
            continue
        
        company_slug = slugify_company(company_dir.name)
        
        with open(all_csv, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("Title", "").strip()
                difficulty = row.get("Difficulty", "").strip()
                leetcode_url = row.get("URL", "").strip()
                
                if not title:
                    skipped += 1
                    continue
                
                # Validate difficulty against our strict enum
                if difficulty not in ("Easy", "Medium", "Hard"):
                    difficulty = None  # Will be filled by classify.py
                
                record = {
                    "sourceId": 1,
                    "sourcePriority": 4,
                    "sourceUrl": leetcode_url or f"https://github.com/snehasishroy/leetcode-companywise-interview-questions/tree/main/{company_dir.name}/all.csv",
                    "recordType": "question",
                    "companySlug": company_slug,
                    "problemSummary": title,
                    "roundType": "Coding",
                    "difficulty": difficulty,
                    "topics": [],  # Not available in this CSV; classify.py will fill
                    "leetcodeUrl": leetcode_url if leetcode_url else None,
                }
                parsed += 1
                yield record
    
    logger.info(f"Source 1 parsing complete: {parsed} records yielded, {skipped} skipped.")


def parse_source_3(repo_dir: Path) -> Generator[Dict[str, Any], None, None]:
    """
    Parse Source 3: krishnadey30/LeetCode-Questions-CompanyWise
    
    Structure: flat CSV files named {company}_{timeframe}.csv
    We ONLY read '*_alltime.csv' files to avoid duplicate counting.
    
    CSV columns: ID, Title, Acceptance, Difficulty, Frequency, Leetcode Question Link
    """
    parsed = 0
    skipped = 0
    
    alltime_csvs = sorted(repo_dir.glob("*_alltime.csv"))
    
    if not alltime_csvs:
        logger.warning("Source 3: No *_alltime.csv files found.")
        return
    
    for csv_file in alltime_csvs:
        # Extract company slug from filename: "amazon_alltime.csv" -> "amazon"
        filename = csv_file.stem  # e.g. "amazon_alltime"
        company_raw = filename.rsplit("_alltime", 1)[0]  # e.g. "amazon"
        company_slug = slugify_company(company_raw)
        
        with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("Title", "").strip()
                difficulty = row.get("Difficulty", "").strip()
                leetcode_url = row.get("Leetcode Question Link", "").strip()
                
                if not title:
                    skipped += 1
                    continue
                
                # Validate difficulty against our strict enum
                if difficulty not in ("Easy", "Medium", "Hard"):
                    difficulty = None  # Will be filled by classify.py
                    
                record = {
                    "sourceId": 3,
                    "sourcePriority": 4,
                    "sourceUrl": leetcode_url or f"https://github.com/krishnadey30/LeetCode-Questions-CompanyWise/blob/main/{csv_file.name}",
                    "recordType": "question",
                    "companySlug": company_slug,
                    "problemSummary": title,
                    "roundType": "Coding",
                    "difficulty": difficulty,
                    "topics": [],  # Not available in this CSV; classify.py will fill
                    "leetcodeUrl": leetcode_url if leetcode_url else None,
                }
                parsed += 1
                yield record
    
    logger.info(f"Source 3 parsing complete: {parsed} records yielded, {skipped} skipped.")


def run(dry_run: bool = False):
    """
    Main entry point. Clones repos (if needed), parses them, and ingests into MongoDB.
    
    Args:
        dry_run: If True, parse and validate but don't insert into MongoDB.
                 Prints the first 5 records from each source for review.
    """
    TEMP_DIR.mkdir(exist_ok=True)
    
    all_records: List[Dict[str, Any]] = []
    
    # --- Source 1 ---
    source_1_dir = TEMP_DIR / REPOS[1]["dir_name"]
    if clone_repo(REPOS[1]["url"], source_1_dir):
        for record in parse_source_1(source_1_dir):
            all_records.append(record)
    
    # --- Source 3 ---
    source_3_dir = TEMP_DIR / REPOS[3]["dir_name"]
    if clone_repo(REPOS[3]["url"], source_3_dir):
        for record in parse_source_3(source_3_dir):
            all_records.append(record)
    
    logger.info(f"Total records parsed: {len(all_records)}")
    
    if dry_run:
        logger.info("=== DRY RUN MODE — No database writes ===")
        
        source_1_records = [r for r in all_records if r["sourceId"] == 1]
        source_3_records = [r for r in all_records if r["sourceId"] == 3]
        
        logger.info(f"Source 1 records: {len(source_1_records)}")
        logger.info(f"Source 3 records: {len(source_3_records)}")
        
        # Show sample records
        logger.info("\n--- Source 1 Sample (first 3) ---")
        for r in source_1_records[:3]:
            logger.info(f"  {r['companySlug']:20s} | {r['difficulty'] or 'TBD':6s} | {r['problemSummary'][:60]}")
        
        logger.info("\n--- Source 3 Sample (first 3) ---")
        for r in source_3_records[:3]:
            logger.info(f"  {r['companySlug']:20s} | {r['difficulty'] or 'TBD':6s} | {r['problemSummary'][:60]}")
        
        # Check for overlap
        source_1_titles = {(r["companySlug"], r["problemSummary"]) for r in source_1_records}
        source_3_titles = {(r["companySlug"], r["problemSummary"]) for r in source_3_records}
        overlap = source_1_titles & source_3_titles
        logger.info(f"\nExact overlap (same company + title): {len(overlap)} records")
        
        # Count unique companies
        all_companies = {r["companySlug"] for r in all_records}
        logger.info(f"Unique companies across both sources: {len(all_companies)}")
        
        # Count records missing difficulty
        missing_diff = sum(1 for r in all_records if r.get("difficulty") is None)
        logger.info(f"Records missing difficulty (needs classify.py): {missing_diff}")
        
        return all_records
    else:
        # Real ingestion
        from ingest import ingest_records
        
        # Ingest in batches of 500 to avoid memory issues
        BATCH_SIZE = 500
        total_inserted = 0
        total_validation_errors = 0
        total_db_errors = 0
        
        for i in range(0, len(all_records), BATCH_SIZE):
            batch = all_records[i:i + BATCH_SIZE]
            result = ingest_records(batch)
            total_inserted += result["inserted"]
            total_validation_errors += result["validation_errors"]
            total_db_errors += result["db_errors"]
            logger.info(f"Batch {i // BATCH_SIZE + 1}: inserted={result['inserted']}, errors={result['validation_errors'] + result['db_errors']}")
        
        logger.info(f"\n=== FINAL RESULTS ===")
        logger.info(f"Total inserted:          {total_inserted}")
        logger.info(f"Total validation errors: {total_validation_errors}")
        logger.info(f"Total DB errors:         {total_db_errors}")
        
        return {
            "inserted": total_inserted,
            "validation_errors": total_validation_errors,
            "db_errors": total_db_errors
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse Group A GitHub repos (Sources 1, 3)")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate without inserting into MongoDB")
    args = parser.parse_args()
    
    run(dry_run=args.dry_run)
