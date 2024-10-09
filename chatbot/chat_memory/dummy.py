import pymongo
from datetime import datetime
import uuid

# MongoDB connection (replace with your actual connection details)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['chatbotDB']
sessions_collection = db['sessions']

# Drop the collection if you want to start fresh (optional)
# sessions_collection.drop()

# Dummy data to insert into the database
dummy_sessions = [
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-04_10-20-15",
        "created_at": datetime(2024, 10, 4, 10, 20, 15),
        "chat_history": [
            {"role": "user", "content": "Hello!"},
            {"role": "bot", "content": "Hi, how can I help you with physics today?"}
        ]
    },
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-04_11-45-30",
        "created_at": datetime(2024, 10, 4, 11, 45, 30),
        "chat_history": [
            {"role": "user", "content": "Explain Newton's laws of motion."},
            {"role": "bot", "content": "Newton's first law is..."}
        ]
    },
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-05_09-30-50",
        "created_at": datetime(2024, 10, 5, 9, 30, 50),
        "chat_history": [
            {"role": "user", "content": "What is gravitational force?"},
            {"role": "bot", "content": "Gravitational force is the force of attraction between two masses..."}
        ]
    },
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-05_10-00-00",
        "created_at": datetime(2024, 10, 5, 10, 0, 0),
        "chat_history": [
            {"role": "user", "content": "Can you tell me about black holes?"},
            {"role": "bot", "content": "A black hole is a region of spacetime where gravity is so strong that nothing can escape from it."}
        ]
    },
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-05_11-15-00",
        "created_at": datetime(2024, 10, 5, 11, 15, 0),
        "chat_history": [
            {"role": "user", "content": "What is the speed of light?"},
            {"role": "bot", "content": "The speed of light in a vacuum is approximately 299,792 kilometers per second."}
        ]
    },
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-06_12-00-00",
        "created_at": datetime(2024, 10, 6, 12, 0, 0),
        "chat_history": [
            {"role": "user", "content": "How does a rocket work?"},
            {"role": "bot", "content": "A rocket works on the principle of Newton's third law of motion: for every action, there is an equal and opposite reaction."}
        ]
    },
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-06_12-30-00",
        "created_at": datetime(2024, 10, 6, 12, 30, 0),
        "chat_history": [
            {"role": "user", "content": "What is quantum mechanics?"},
            {"role": "bot", "content": "Quantum mechanics is the branch of physics that deals with the behavior of very small particles, such as atoms and photons."}
        ]
    },
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-06_13-00-00",
        "created_at": datetime(2024, 10, 6, 13, 0, 0),
        "chat_history": [
            {"role": "user", "content": "What causes tides?"},
            {"role": "bot", "content": "Tides are caused primarily by the gravitational pull of the moon and the sun on the Earth's oceans."}
        ]
    },
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-06_13-30-00",
        "created_at": datetime(2024, 10, 6, 13, 30, 0),
        "chat_history": [
            {"role": "user", "content": "What is the theory of relativity?"},
            {"role": "bot", "content": "The theory of relativity, developed by Albert Einstein, describes the relationship between space, time, and gravity."}
        ]
    },
    {
        "session_id": str(uuid.uuid4()),
        "session_name": "Session_2024-10-06_14-00-00",
        "created_at": datetime(2024, 10, 6, 14, 0, 0),
        "chat_history": [
            {"role": "user", "content": "Can you explain the concept of entropy?"},
            {"role": "bot", "content": "Entropy is a measure of the amount of disorder in a system; it is a central concept in the second law of thermodynamics."}
        ]
    }
]

# Insert the dummy data into the MongoDB sessions collection
result = sessions_collection.insert_many(dummy_sessions)

print(f"Inserted {len(result.inserted_ids)} sessions into the database.")
