"""
classify.py

Fetches records with status="clean", batches them, and sends them to Claude API
for topic classification. Updates the records in MongoDB with the inferred topics
and sets status="classified".
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import logging
import sys
import argparse
import os
import json
import asyncio
from typing import List, Dict, Any
from anthropic import AsyncAnthropic
from pymongo import UpdateOne
from config.db import get_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("classifier")

# Strict topic enum from our prompt design
TOPICS = [
    "Arrays", "Strings", "Linked List", "Trees", "Graphs", 
    "Dynamic Programming", "Math", "Sorting", "Greedy", 
    "Binary Search", "Hash Table", "System Design", "Bit Manipulation"
]

SYSTEM_PROMPT = f"""You are a Data Structures and Algorithms expert. You will receive a JSON list of interview problem titles. For each problem, determine 1 to 3 of the most relevant algorithmic topics from this STRICT list: {json.dumps(TOPICS)}. 
If no topic fits well, return ["Other"]. Do not invent topics outside of this list. Return ONLY a valid JSON array of objects mapping the `id` to the assigned `topics`. No markdown formatting, just raw JSON."""

async def classify_batch(client: AsyncAnthropic, batch: List[Dict[str, str]], model: str) -> List[Dict[str, Any]]:
    prompt = json.dumps(batch, indent=2)
    try:
        response = await client.messages.create(
            model=model,
            max_tokens=1500,
            temperature=0.1,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Anthropic returns the text in content[0].text
        content = response.content[0].text.strip()
        # Clean up any potential markdown wrapper if Claude ignores instructions
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        return json.loads(content.strip())
    except Exception as e:
        logger.error(f"Error calling Claude API: {e}")
        return []

async def process_records(test: bool = False):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not found in environment variables.")
        return
        
    client = AsyncAnthropic(api_key=api_key)
    # Default to Haiku for cost efficiency and speed on simple tasks
    model = "claude-3-haiku-20240307"
    
    db = get_db()
    
    query = {"status": "clean"}
    if test:
        total = 5
        records = list(db.raw_scraped_data.find(query).limit(5))
        logger.info(f"=== TEST MODE ===")
    else:
        total = db.raw_scraped_data.count_documents(query)
        records = list(db.raw_scraped_data.find(query))
        
    logger.info(f"Found {total} records to classify.")
    if total == 0:
        return
        
    # Prepare data for API (only ID and Title)
    payloads = [{"id": str(r["_id"]), "title": r["problemSummary"]} for r in records]
    
    BATCH_SIZE = 50
    CONCURRENCY = 5
    
    batches = [payloads[i:i + BATCH_SIZE] for i in range(0, len(payloads), BATCH_SIZE)]
    logger.info(f"Split into {len(batches)} batches of up to {BATCH_SIZE} records.")
    
    # Process batches concurrently
    sem = asyncio.Semaphore(CONCURRENCY)
    
    async def process_batch_with_semaphore(batch, idx):
        async with sem:
            logger.info(f"Processing batch {idx+1}/{len(batches)}...")
            return await classify_batch(client, batch, model)
            
    tasks = [process_batch_with_semaphore(b, i) for i, b in enumerate(batches)]
    results = await asyncio.gather(*tasks)
    
    # Flatten results
    classified_data = []
    for res in results:
        classified_data.extend(res)
        
    logger.info(f"Received classification for {len(classified_data)} records.")
    
    if test:
        logger.info(f"Sample response: {json.dumps(classified_data[:3], indent=2)}")
        logger.info("Test mode complete. Run without --test to update database.")
        return
        
    # Real run: Bulk update database
    logger.info("Executing database updates...")
    bulk_ops = []
    from bson import ObjectId
    
    for item in classified_data:
        try:
            record_id = ObjectId(item["id"])
            topics = item.get("topics", [])
            
            # Enforce strict enum client-side just in case
            valid_topics = [t for t in topics if t in TOPICS or t == "Other"]
            if not valid_topics:
                valid_topics = ["Other"]
                
            bulk_ops.append(
                UpdateOne(
                    {"_id": record_id},
                    {"$set": {
                        "status": "classified",
                        "topics": valid_topics
                    }}
                )
            )
        except Exception as e:
            logger.warning(f"Failed to prepare update for {item}: {e}")
            
    if bulk_ops:
        # Execute in chunks of 1000
        for i in range(0, len(bulk_ops), 1000):
            chunk = bulk_ops[i:i+1000]
            result = db.raw_scraped_data.bulk_write(chunk, ordered=False)
            logger.info(f"Updated {result.modified_count} records to 'classified'.")
    else:
        logger.info("No updates prepared.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Classify problem titles using Claude")
    parser.add_argument("--test", action="store_true", help="Run on 5 records only without DB writes")
    args = parser.parse_args()
    
    asyncio.run(process_records(test=args.test))
