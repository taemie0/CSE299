
from datetime import datetime
def fetch_data(collection):
    try:
        data = list(collection.find({}).sort('created_at', -1))
        # Convert MongoDB ObjectId to string for JSON serialization
        return [{
            'session_id': session['session_id'],
            'session_name': session['session_name'],
            'created_at': session['created_at'].isoformat() if isinstance(session['created_at'], datetime) else session['created_at'],  # Ensure it's a string
            'chat_history': session['chat_history'],
            '_id': str(session['_id'])  # Convert ObjectId to string
        } for session in data]
    except Exception as error:
        print("Error fetching data:", error)
        return []  # Return empty list on error


def delete_session(collection, session_name):
    try:
        result = collection.delete_one({"session_name": session_name})
        if result.deleted_count > 0:
            print(f"Session '{session_name}' deleted successfully.")
            return True
        else:
            print(f"Session '{session_name}' not found.")
            return False
    except Exception as error:
        print(f"Error deleting session '{session_name}': {error}")
        return False

