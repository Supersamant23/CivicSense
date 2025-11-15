# backend/app.py

import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import os # Added for API key access

# --- Add backend directory to path ---
# This ensures we can import from 'src'
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))
# ------------------------------------

# Import our quiz engine functions and LLMClient
from src import (
    load_quiz_questions,
    load_manifestos,
    compute_alignment,
    LLMClient # Added import
)

# --- LLM Client Initialization ---
# Load API key from .env (which should be loaded by quiz_engine)
# NOTE: 1_run_analysis.py uses GOOGLE_API_KEY as the default
API_KEY = os.getenv("GOOGLE_API_KEY") 
PROVIDER = "google"
llm = None
if API_KEY:
    try:
        llm = LLMClient(provider=PROVIDER, api_key=API_KEY)
        print(f"--- LLM client for explanations initialized (provider: {PROVIDER}) ---")
    except Exception as e:
        print(f"Warning: Could not initialize LLM client for explanations. {e}")
        print("Falling back to short explanations.")
else:
    print("Warning: GOOGLE_API_KEY not found in .env.")
    print("LLM explanations will be disabled. Falling back to short explanations.")
# ---------------------------------


# Initialize the Flask app
app = Flask(__name__)

# --- Configure CORS ---
# This is CRITICAL for your frontend
# It allows your React app (on a different "origin")
# to make requests to this backend.
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Allow all origins for /api/ routes

# --- API Endpoints ---

@app.route('/api/quiz', methods=['GET'])
def get_quiz():
    """
    Endpoint to send the quiz questions to the frontend.
    """
    questions = load_quiz_questions()
    if not questions:
        return jsonify({"error": "Quiz questions not found."}), 404
    return jsonify(questions)

@app.route('/api/manifestos', methods=['GET'])
def get_manifestos():
    """
    Endpoint to send all manifesto data to the frontend.
    (You might use this to show a "details" page)
    """
    manifestos = load_manifestos()
    if not manifestos:
        return jsonify({"error": "Manifestos not found."}), 404
    return jsonify(manifestos)

@app.route('/api/align', methods=['POST'])
def get_alignment():
    """
    Endpoint to receive user answers and return alignment results.
    """
    # Get the JSON data sent from the frontend
    data = request.get_json()
    
    # Expecting a list of numbers, e.g., {"answers": [5, 4, 3, 2, ...]}
    user_answers = data.get('answers')

    if not user_answers or not isinstance(user_answers, list):
        return jsonify({"error": "Invalid input. 'answers' must be a list."}), 400

    try:
        # Run our existing quiz engine logic!
        # --- MODIFIED: Pass the initialized llm client ---
        results = compute_alignment(user_answers, llm_client=llm)
        return jsonify(results)
    
    except Exception as e:
        print(f"Error computing alignment: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

# --- Health Check Endpoint ---
@app.route('/api/health', methods=['GET'])
def health_check():
    """A simple endpoint to check if the server is running."""
    return jsonify({"status": "ok", "message": "API is running"}), 200

# This allows us to run the app using "python app.py"
if __name__ == '__main__':
    # host='0.0.0.0' makes it accessible on your network
    # debug=True automatically reloads the server when you change code
    app.run(host='0.0.0.0', port=5000, debug=True)