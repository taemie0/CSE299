from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import atexit
import os
import time
import json
import yaml
from query_Prompt import query_rag 

app = Flask(__name__)
CORS(app)  

CONFIG_FILE_PATH = 'config.yaml'


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

@app.route('/')
def home():
    return "Backend is running with Ollama!"


# function to query the RAG model
@app.route('/', methods=['POST'])
def handle_message():
    data = request.json
    message = data.get('message', '')
    current_model = data.get('currentModel', '')

    print(f"Received message: {message}")
    print(f"Current model: {current_model}")

    # Run the query prompt script to get the response text
    response_text = query_rag(message)

    print(f"Response text: {response_text}")

    return jsonify({
        'message': response_text
    })

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



if __name__ == "__main__":
    app.run(port=5000)
