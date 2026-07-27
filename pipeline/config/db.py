import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "placeprep")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def get_db():
    return db
