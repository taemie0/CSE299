import pymongo
from datetime import datetime
import uuid

# MongoDB connection (replace with your actual connection details)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['chatbotDB']

# Define the new collection
session_summaries_collection = db['session_summaries']

# New data with summaries
dummy_summaries = [
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-06_13-30-00",
        "created_at": datetime(2024, 10, 6, 13, 30, 0),
        "chat_history": [
            {"role": "user", "content": "What is the theory of relativity?"},
            {"role": "bot", "content": "The theory of relativity, developed by Albert Einstein, describes the relationship between space, time, and gravity."}
        ],
        "summary": "Explained the theory of relativity in brief."
    },
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-06_14-00-00",
        "created_at": datetime(2024, 10, 6, 14, 0, 0),
        "chat_history": [
            {"role": "user", "content": "Can you explain the concept of entropy?"},
            {"role": "bot", "content": "Entropy is a measure of the amount of disorder in a system; it is a central concept in the second law of thermodynamics."}
        ],
        "summary": "Explained the concept of entropy and its significance."
    }
]

# Insert the data into the new collection
session_summaries_collection.insert_many(dummy_summaries)

print("Summaries inserted successfully!")
