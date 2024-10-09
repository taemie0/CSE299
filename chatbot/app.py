from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import atexit
import os
import time
import json
import yaml
from query_Prompt import query_rag 
from chat_memory.chatbotDB import fetch_data, delete_session
from pymongo import MongoClient
from datetime import datetime
# from agents import run_agent

app = Flask(__name__)
CORS(app)  

CONFIG_FILE_PATH = 'config.yaml'

# MongoDB connection
url = "mongodb://localhost:27017"
client = MongoClient(url)
db_name = "chatbotDB"
collection_name = "sessions"
db = client[db_name]
collection = db[collection_name]

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

# function to query the RAG model
@app.route('/query', methods=['POST'])
def handle_message():
    data = request.json
    message = data.get('message', '')
    current_model = data.get('currentModel', '')
    session_name = data.get('currentSession','')  
    
    print(f"Received message: {message}")
    print(f"Current model: {current_model}")
    print(f"Session name: {session_name}")  

    # chat_history = collection.find_one({'session_name': session_name}).get('chat_history', [])
    # Run the query prompt script to get the response text
    # response_text = run_agent(message,chat_history)
    response_text = query_rag(message)
       
    if session_name:
        update_session_chat_history(session_name, message, response_text)

    print(f"Response text: {response_text}")

    return jsonify({
        'message': response_text
    })

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

# @app.route('/')
# def home():
#     return "Backend is running with Ollama!"

# @app.teardown_appcontext
# def close_db(exception=None):
#     client.close()  

if __name__ == "__main__":
    app.run(port=5000)
