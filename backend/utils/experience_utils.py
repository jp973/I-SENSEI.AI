# backend/utils/experience_utils.py
from backend.utils.mongo_utils import get_experience_collection

def save_experience_to_db(name, mobile, experience):
    collection = get_experience_collection()
    experience_data = {
        "name": name,
        "mobile": mobile,
        "experience": experience
    }
    result = collection.insert_one(experience_data)
    return result.inserted_id is not None
