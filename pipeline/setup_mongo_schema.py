from config.db import db
from pymongo.errors import CollectionInvalid

def setup_raw_schema():
    """
    Creates the raw_scraped_data collection with JSON Schema validation
    matching our requirements for staging records.
    """
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["sourceId", "sourcePriority", "sourceUrl", "recordType", "status", "scrapedAt"],
            "properties": {
                "sourceId": {
                    "bsonType": "int",
                    "minimum": 1,
                    "maximum": 52,
                    "description": "Must be an integer in 1-52."
                },
                "sourcePriority": {
                    "bsonType": "int",
                    "minimum": 1,
                    "maximum": 7,
                    "description": "Priority 1 (highest) to 7 (lowest) for dedup."
                },
                "sourceUrl": {
                    "bsonType": "string"
                },
                "recordType": {
                    "enum": ["question", "experience"],
                    "description": "Must be either 'question' or 'experience'"
                },
                "status": {
                    "enum": ["pending", "deduped", "clean", "classified", "promoted", "duplicate", "error"],
                    "description": "Pipeline processing lifecycle status"
                },
                "errorType": {
                    "enum": ["retryable", "permanent"],
                    "description": "Determines if pipeline should auto-retry"
                },
                "errorMessage": {
                    "bsonType": "string"
                },
                "promotedQuestionId": {
                    "bsonType": ["objectId", "null"],
                    "description": "Link to the final Question/Experience record"
                },
                "scrapedAt": {
                    "bsonType": "date",
                    "description": "Timestamp for dedup tie-breaking"
                },
                "companySlug": {
                    "bsonType": "string"
                },
                "problemSummary": {
                    "bsonType": "string"
                },
                "experienceText": {
                    "bsonType": "string"
                },
                "cautionSource": {
                    "bsonType": "bool"
                }
            }
        }
    }

    try:
        db.create_collection("raw_scraped_data", validator=validator)
        print("Created raw_scraped_data collection with schema validation.")
    except CollectionInvalid:
        # Collection already exists, update the validator
        db.command("collMod", "raw_scraped_data", validator=validator)
        print("Updated raw_scraped_data collection validation schema.")
        
    # Create indexes for efficient querying during ETL
    db.raw_scraped_data.create_index([("status", 1), ("errorType", 1)]) # Fast retry-querying
    db.raw_scraped_data.create_index([("sourceId", 1)])
    db.raw_scraped_data.create_index([("companySlug", 1), ("recordType", 1), ("scrapedAt", -1)]) # Fast dedup matching

def setup_dummy_user():
    """
    Creates the generic 'Pipeline System User' required for the InterviewExperience studentId field.
    """
    import datetime
    pipeline_email = "pipeline@placeprep.system"
    user = db.users.find_one({"email": pipeline_email})
    
    if not user:
        result = db.users.insert_one({
            "email": pipeline_email,
            "fullName": "Pipeline System User",
            "role": "student",
            "passwordHash": None, # Unusable password
            "isEmailVerified": True,
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        })
        user_id = result.inserted_id
        print(f"Created Pipeline Dummy User with ID: {user_id}")
    else:
        user_id = user["_id"]
        print(f"Pipeline Dummy User already exists with ID: {user_id}")
        
    return user_id

if __name__ == "__main__":
    print("Setting up MongoDB Staging schemas...")
    setup_raw_schema()
    setup_dummy_user()
    print("Done.")
