import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from pymongo.errors import BulkWriteError
from pydantic import ValidationError

from config.db import get_db
from models.raw_record import RawRecord

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ingester")

# Ensure logs directory exists
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
REJECTED_LOG_FILE = LOG_DIR / "rejected_records.jsonl"

def ingest_records(raw_dicts: List[Dict[str, Any]]) -> dict:
    """
    Validates a list of raw dictionaries against the RawRecord Pydantic model
    and bulk inserts them into the raw_scraped_data MongoDB collection.
    
    Returns a dictionary of counts: {inserted, validation_errors, db_errors}.
    """
    db = get_db()
    valid_records = []
    validation_errors = 0
    rejected_entries = []
    
    logger.info(f"Starting ingestion of {len(raw_dicts)} records...")
    
    for raw in raw_dicts:
        try:
            # Validate through Pydantic
            record = RawRecord(**raw)
            # Dump to dict, excluding None to keep Mongo clean 
            # while preserving defaults like status and scrapedAt
            valid_records.append(record.model_dump(exclude_none=True))
        except ValidationError as e:
            source_id = raw.get('sourceId', 'Unknown')
            logger.error(f"Validation failed for record from source {source_id}")
            validation_errors += 1
            
            # Save the rejected raw input alongside its validation errors
            rejected_entries.append({
                "raw_input": raw,
                "validation_errors": e.errors()
            })
            
    # Write rejected records to JSONL if any exist
    if rejected_entries:
        with open(REJECTED_LOG_FILE, "a", encoding="utf-8") as f:
            for entry in rejected_entries:
                f.write(json.dumps(entry, default=str) + "\n")
        logger.info(f"Logged {validation_errors} rejected records to {REJECTED_LOG_FILE}")
            
    if not valid_records:
        logger.warning("No valid records to insert after validation.")
        return {"inserted": 0, "validation_errors": validation_errors, "db_errors": 0}
        
    db_errors = 0
    inserted_count = 0
    
    try:
        # Unordered bulk write: if one fails (e.g. unexpected unique constraint), 
        # the others still get inserted successfully.
        result = db.raw_scraped_data.insert_many(valid_records, ordered=False)
        inserted_count = len(result.inserted_ids)
        logger.info(f"Successfully inserted {inserted_count} records.")
    except BulkWriteError as bwe:
        db_errors = len(bwe.details['writeErrors'])
        inserted_count = bwe.details['nInserted']
        logger.error(f"Bulk insert completed with {db_errors} errors. Inserted {inserted_count}.")
        
    return {
        "inserted": inserted_count,
        "validation_errors": validation_errors,
        "db_errors": db_errors
    }
