from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import atexit
import os
import time
import json
import yaml
from query_appback import query_rag_streaming 
# from app_test import query_rag_streaming 
from MongoDB.chatbotDB import fetch_data, delete_session
from pymongo import MongoClient
from datetime import datetime
from summary_chat import generate_new_summary
from query_with_memory import query_with_memory 
from flask import Response

app = Flask(__name__)
CORS(app)  

CONFIG_FILE_PATH = 'config.yaml'

# MongoDB connection
url = "mongodb://localhost:27017"
client = MongoClient(url)
db_name = "chatbotDB"
collection_name = "session_summaries"
db = client[db_name]
collection = db[collection_name]

@app.route('/available_models', methods=['GET'])
def get_available_models():
    try:
        # Call 'ollama list' to fetch installed models
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        
        # Print the return code and any errors from the subprocess
        print(f"Return code: {result.returncode}")
        if result.returncode != 0:
            print(f"Subprocess error: {result.stderr}")
            return jsonify({"error": "Failed to retrieve models. Check if Ollama is running."}), 500

        # Print the raw output for debugging
        print("ollama list output:", result.stdout)

        # Since the output is not JSON, we need to manually parse the plain text
        lines = result.stdout.strip().splitlines()
        
        # Extract model names by skipping the first 3 lines (header information)
        model_names = []
        for line in lines[3:]:  # Skip the header
            parts = line.split()
            if len(parts) >= 1:
                model_names.append(parts[0])  # The model name is the first part

        # Print the model names for debugging
        print("Available models:", model_names)
        
        return jsonify(models=model_names), 200

    except Exception as e:
        # Log the full exception message for debugging
        print(f"Exception occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500



@app.route('/create_session', methods=['POST'])
def create_session():

    session_data = request.json
    if not session_data or 'session_id' not in session_data or 'session_name' not in session_data:
        return jsonify({"error": "Session ID and name are required"}), 400

    # Convert created_at back to a datetime object
    session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])

    # Insert the session into MongoDB
    collection.insert_one(session_data)
    
    return jsonify({"message": "Session created successfully"}), 201


@app.route('/stream_query', methods=['POST'])
def stream_query():
    data = request.json
    query_text = data.get('message', '')
    current_model = data.get('currentModel', '')
    session_name = data.get('currentSession', '')
    
    print(f"Current model: {current_model}")
    print(f"Session name: {session_name}") 
    print(f"Query text: {query_text}")


    conversation_history = fetch_chat_history(session_name)
    summary= fetch_summary(session_name)
    
    def generate():
        try:
            # Simulate streaming by generating the response incrementally
            for chunk in query_rag_streaming(query_text, conversation_history, summary):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate(), content_type='text/plain')


# Function to fetch chat history from MongoDB
def fetch_chat_history(session_name):

    chat_history = collection.find_one({"session_name": session_name})
    
    if chat_history:
        return chat_history.get('chat_history', [])
    else:
        return None

# Function to fetch the summary from MongoDB
def fetch_summary(session_name):

    summary_record = collection.find_one({"session_name": session_name}, {"summary": 1, "_id": 0})
    
    if summary_record:
        return summary_record.get('summary', "")
    else:
        return None

@app.route('/save_chat_history', methods=['POST'])
def save_chat_history():
    data = request.json
    session_name = data.get('session_name')
    user_message = data.get('user_message')
    bot_response = data.get('bot_response')
    
    print(f"Saving chat history for session: {session_name}")
    print(f"User message: {user_message}")
    print(f"Bot response: {bot_response}")
    if not session_name or not user_message or not bot_response:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        update_session_chat_history(session_name, user_message, bot_response)
        return jsonify({"message": "Chat history saved successfully"}), 200
    except Exception as e:
        print(f"Error saving chat history: {e}")
        return jsonify({"error": str(e)}), 500


def update_summary(session_name, summary, user_message, bot_response):
    """Updates the summary for a given session in the MongoDB collection."""
    recent_conversation = [
        {"role": "user", "content": user_message},
        {"role": "bot", "content": bot_response}
    ]
    new_summary= generate_new_summary(summary, recent_conversation)

    result = collection.update_one(
        {"session_name": session_name},
        {"$set": {"summary": new_summary}}
    )

    if result.matched_count > 0:
        if result.modified_count > 0:
            return {"message": "Summary updated successfully."}
        else:
            return {"message": "Summary is already up-to-date."}
    else:
        return {"error": "Session not found."}


def update_session_chat_history(session_name, user_message, bot_response):
    print(f"Updating chat history for session: {session_name}")  # Check session name
    
    # Add user message
    result_user = collection.update_one(
        {'session_name': session_name}, 
        {'$push': {'chat_history': {'content': user_message, 'role': 'user'}}}
    )
    print(f"User message update result: {result_user.modified_count}")

    # Add bot response
    result_bot = collection.update_one(
        {'session_name': session_name}, 
        {'$push': {'chat_history': {'content': bot_response, 'role': 'bot'}}}
    )
    print(f"Bot response update result: {result_bot.modified_count}")

    # Update the summary
    summary = fetch_summary(session_name)
    update_summary(session_name, summary, user_message, bot_response)


# Update the model name in the config file
@app.route('/update_model', methods=['POST'])
def update_model():
    try:
        data = request.json
        model_name = data.get('model_name')

        if not model_name:
            return jsonify({"error": "Model name is required"}), 400

        with open(CONFIG_FILE_PATH, 'r') as f:
            config = yaml.safe_load(f)

        config['model_name'] = model_name

        with open(CONFIG_FILE_PATH, 'w') as f:
            yaml.safe_dump(config, f)

        return jsonify({"message": f"Config updated to model: {model_name}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def get_sessions():
    session_data = fetch_data(collection)  # Call the modified fetch_data
    return jsonify({'session_data': session_data})  # This should now work without errors

# Route to delete a session
@app.route('/delete_session/<session_name>', methods=['DELETE'])
def handle_delete_session(session_name):
    if delete_session(collection, session_name):  # Pass the collection here
        return jsonify({'message': 'Session deleted successfully'}), 200
    else:
        return jsonify({'message': 'Session not found'}), 404

# @app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    session_name = request.args.get('session_name')
    if not session_name:
        return jsonify({"error": "Session name is required"}), 400
    
    # Fetch chat history from MongoDB
    chat_history = fetch_data(session_name)
    
    # Check if the session exists
    if chat_history is None:
        return jsonify({"error": "Session not found"}), 404

    # Return the chat history
    return jsonify(chat_history), 200

# ========== Backend Connections Utilities ==========

# Function to stream output of the subprocess
def stream_output(process):
    for line in process.stdout:
        print(line, end='')  # Output is already a string, so no need to decode

# Function to start Ollama
def start_ollama():
    try:
        # Redirect stdout and stderr to os.devnull
        with open(os.devnull, 'w') as devnull:
            ollama_process = subprocess.Popen(
                ["ollama", "serve"], 
                stdout=devnull,  # Discard stdout
                stderr=devnull,  # Discard stderr
                shell=True       # Required for Windows
            )
            print("Ollama is starting...", flush=True)
            return ollama_process
    except Exception as e:
        print(f"Error starting Ollama: {e}", flush=True)
        return None



# When Backend starts
ollama_process = start_ollama()

# Stop the Ollama server
def stop_ollama():
    if ollama_process:
        ollama_process.terminate()  
        print("Ollama server stopped.", flush=True)

# Register the stop_ollama function to be called on exit
atexit.register(stop_ollama)



if __name__ == "__main__":
    app.run(port=5000)
