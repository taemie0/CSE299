from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import yaml
from query_Prompt import query_rag 

app = Flask(__name__)
CORS(app)  # Enable CORS

CONFIG_FILE_PATH = 'config.yaml'

@app.route('/update-model', methods=['POST'])
def update_model():
    try:
        # Get the model_name from the request body
        data = request.get_json()
        model_name = data.get('model_name')

        if not model_name:
            return jsonify({"error": "Model name is required"}), 400

        # Load the existing config
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = yaml.safe_load(f)

        # Update the model_name in the config
        config['model_name'] = model_name

        # Write the updated config back to the file
        with open(CONFIG_FILE_PATH, 'w') as f:
            yaml.safe_dump(config, f)

        return jsonify({"message": f"Config updated to model: {model_name}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# def load_config():
#     with open(CONFIG_FILE, 'r') as f:
#         return yaml.safe_load(f)

# def save_config(config):
#     with open(CONFIG_FILE, 'w') as f:
#         yaml.safe_dump(config, f)

@app.route('/', methods=['POST'])
def handle_message():
    data = request.json
    message = data.get('message', '')
    current_model = data.get('currentModel', '')

    print(f"Received message: {message}")
    print(f"Current model: {current_model}")

    # Call the function to run the query prompt script
    response_text = query_rag(message)

    print(f"Response text: {response_text}")

    return jsonify({
        'message': response_text
    })

# def query_rag(query_text: str) -> str:
#     print(f"query_text: {query_text}")
#     result = subprocess.run(
#         ["python", "query_prompt.py", query_text],
#         capture_output=True,
#         text=True
#     )
#     return result.stdout.strip()

# @app.route("/models", methods=["GET"])
# def get_models():
#     # Replace this part with actual implementation if you have a method to list models.
#     # For now, it will just return a placeholder response.
#     models = {
#         "models": ["gemma2:2b", "mistral","llama3.1:"]
#     }
#     return jsonify(models)

# @app.route('/update-model', methods=['POST'])
# def update_model():
#     data = request.json
#     new_model = data.get('model')
#     if new_model:
#         config = load_config()
#         config['model_name'] = new_model
#         save_config(config)
#         return jsonify({"status": "success", "model": new_model}), 200
#     return jsonify({"status": "error", "message": "No model provided"}), 400


if __name__ == "__main__":
    app.run(port=5000)
