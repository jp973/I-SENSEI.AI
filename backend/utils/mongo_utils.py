from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection Setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "isensei"
USERS_COLLECTION_NAME = "users"
EXPERIENCE_COLLECTION_NAME = "user_experience"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db[USERS_COLLECTION_NAME]
experience_collection = db[EXPERIENCE_COLLECTION_NAME]

# Get collection for users
def get_users_collection():
    return users_collection

# ✅ New: Get collection for user experiences
def get_experience_collection():
    return experience_collection
