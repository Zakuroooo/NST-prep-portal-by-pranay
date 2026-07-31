import os
import json
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import sys

# Ensure sys.path allows importing config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.db import get_db

class MongoEncoder(json.JSONEncoder):
    """Custom encoder to convert MongoDB ObjectIds and Datetime objects to strings."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def run():
    load_dotenv()
    db = get_db()
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'data'))
    os.makedirs(output_dir, exist_ok=True)
    
    questions_path = os.path.join(output_dir, 'questions.json')
    companies_path = os.path.join(output_dir, 'companies.json')
    
    print("Fetching companies...")
    companies = list(db.companies.find({}))
    print(f"Exporting {len(companies)} companies to JSON...")
    with open(companies_path, 'w', encoding='utf-8') as f:
        json.dump(companies, f, cls=MongoEncoder, indent=2)
        
    print("Fetching questions...")
    questions = list(db.questions.find({}))
    print(f"Exporting {len(questions)} questions to JSON...")
    with open(questions_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, cls=MongoEncoder, indent=2)
        
    print(f"Export complete!\nFiles saved at:\n- {companies_path}\n- {questions_path}")

if __name__ == "__main__":
    run()
