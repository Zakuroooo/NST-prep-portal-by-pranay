import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import sys
from ingest import ingest_records
from setup_mongo_schema import setup_raw_schema, setup_dummy_user

# Set up logging for the test script
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("test_insert")

def run_test():
    logger.info("1. Ensuring schemas and dummy user are setup...")
    setup_raw_schema()
    setup_dummy_user()
    
    logger.info("\n2. Preparing test data...")
    test_data = [
        # Valid Record 1: A structured Question
        {
            "sourceId": 1,
            "sourcePriority": 2,
            "sourceUrl": "https://github.com/example/repo/q1",
            "recordType": "question",
            "companySlug": "google",
            "problemSummary": "Reverse a linked list",
            "difficulty": "Easy",
            "topics": ["Linked List"]
        },
        # Invalid Record 1: Missing required Pydantic fields (e.g., sourceUrl) and invalid Literal
        {
            "sourceId": 2,
            "sourcePriority": 3,
            # Missing sourceUrl
            "recordType": "not_a_valid_type", # Should trigger Literal validation error
            "companySlug": "amazon",
            "problemSummary": "This should fail Pydantic validation and log to JSONL."
        }
    ]
    
    logger.info("3. Running ingestion engine...")
    results = ingest_records(test_data)
    
    logger.info(f"\n4. Test Results: {results}")
    logger.info("If successful, you should see 1 record inserted into MongoDB Atlas.")
    logger.info("You should also see 1 validation error logged to pipeline/logs/rejected_records.jsonl")

if __name__ == "__main__":
    run_test()
