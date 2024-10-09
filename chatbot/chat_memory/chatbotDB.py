
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

# def update_collection(bot_response, user_input):
#     try:
#         print("Connected successfully to server")
        

#         # Data to insert
#         new_data = [
#             {
#                 "role": "user",
#                 "content": user_input
#             },
#             {
#                 "role": "assistant",
#                 "content": bot_response
#             }
#         ]

#         # Insert the new data into the collection
#         insert_result = collection.insert_many(new_data)
#         return "Success"
#     except Exception as error:
#         print("Error:", error)
#         return "error in updating collection"





# def reset_and_insert_data():
#     try:
#         # Connect to the MongoDB server
#         print("Connected successfully to server")
        
#         # Delete all data from the collection
#         delete_result = collection.delete_many({})
#         print(f"{delete_result.deleted_count} documents deleted from {collection_name}")

#         # Data to insert
#         new_data = [
#             {
#                 "role": "assistant",
#                 "content": "How may I assist you today?"
#             },
#             {
#                 "role": "user",
#                 "content": "I need help with MongoDB."
#             }
#         ]

#         # Insert the new data into the collection
#         insert_result = collection.insert_many(new_data)
#         print("New data inserted successfully with IDs:", insert_result.inserted_ids)
#     except Exception as error:
#         print("Error:", error)
#     finally:
#         # Close the connection
#         client.close()

# def add_data():
#     try:
#         # Connect to the MongoDB server
#         print("Connected successfully to server")
        

#         # Data to insert
#         new_data = [
#             {
#                 "role": "assistant",
#                 "content": "What specific topics in physics do you need help with?"
#             },
#             {
#                 "role": "user",
#                 "content": "Can you explain Newton's Laws of Motion?"
#             }
#         ]

#         # Insert the new data into the collection
#         insert_result = collection.insert_many(new_data)
#         print(f"{len(insert_result.inserted_ids)} new documents inserted successfully.")
#     except Exception as error:
#         print("Error:", error)
#     finally:
#         # Close the connection
#         client.close()

# def insert_into_new_collection():
#     new_collection_name = 'prompt'
#     try:

#         new_data = {
#             "role": "assistant",
#             "content": "This is a new collection!"
#         }
        
#         # Insert the new data into the new collection
#         collection = db[new_collection_name]  # This will create the collection if it doesn't exist
#         insert_result = collection.insert_one(new_data)
#         print(f"Data inserted into {new_collection_name} collection successfully.")
#     except Exception as error:
#         print("Error:", error)
#     finally:
#         # Close the connection
#         client.close()

# Uncomment the desired function to run
# fetch_data()
# reset_and_insert_data()
# add_data()
# insert_into_new_collection()
