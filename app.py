from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory, send_file
import os
import json
import subprocess
import threading
import logging

app = Flask(__name__)

SAVE_FOLDER = './Viserys1'
FILE_NAME = 'interview_options.json'
RESULTS_FOLDER = './'  # As candidate_results.json is stored in the root folder
RESULT_FILE = 'candidate_results.json'
chat_done = False  # Global flag to indicate if chat.py has finished
chat2_done = False  # Global flag for chat2.py completion
lock = threading.Lock()  # Lock for thread safety

# Path to the responses file
responses_file = 'Candidate_response.json'

# Set up logging
logging.basicConfig(level=logging.INFO)

# Ensure the save folder exists
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Clear the responses file when the app starts
def clear_responses_file():
    with open(responses_file, 'w') as f:
        json.dump([], f)  # Initialize with an empty list

clear_responses_file()  # Call the function to clear or initialize the file

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask-questions')
def ask_questions():
    return send_from_directory('templates', 'ask-questions.html')

@app.route('/save_options', methods=['POST'])
def save_options():
    data = request.json

    if data:
        file_path = os.path.join(SAVE_FOLDER, FILE_NAME)

        try:
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)

            logging.info("JSON data saved successfully. Redirecting to loading page.")
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": f"Error saving file: {e}"}), 500
    else:
        return jsonify({"error": "No data provided"}), 400

@app.route('/loading')
def loading():
    global chat_done
    with lock:
        chat_done = False  # Reset chat_done before starting a new session
    threading.Thread(target=run_chat_script, daemon=True).start()
    return render_template('loading.html')

def run_chat_script():
    global chat_done
    try:
        logging.info("Starting chat.py...")
        subprocess.run(['python', 'chat.py'], check=True)
        with lock:  # Ensure thread safety when updating the flag
            chat_done = True
        logging.info("chat.py execution completed.")
    except Exception as e:
        logging.error(f"Error running chat.py: {e}")

@app.route('/check_status')
def check_status():
    with lock:  # Ensure thread safety when reading the flag
        return jsonify({"done": chat_done})

# Serve the questions once chat.py is completed
@app.route('/questions', methods=['GET'])
def get_questions():
    if (os.path.exists('Generated_questions.json')):
        with open('Generated_questions.json', 'r') as f:
            questions = json.load(f)
        return jsonify(questions)
    return jsonify({'error': 'Questions file not found'}), 404

# Handle response submission
@app.route('/submit', methods=['POST'])
def submit_response():
    response_data = request.json
    with open(responses_file, 'r+') as f:
        responses = json.load(f)
        responses.append(response_data)
        f.seek(0)
        json.dump(responses, f, indent=2)
    return jsonify({'message': 'Response recorded successfully!'}), 200

@app.route('/result_loading')
def result_loading():
    # Display the result_loading.html and start running chat2.py in the background
    global chat2_done
    with lock:
        chat2_done = False  # Reset chat2_done before starting chat2.py
    threading.Thread(target=run_chat2_script, daemon=True).start()
    return render_template('result_loading.html')

def run_chat2_script():
    global chat2_done
    try:
        logging.info("Starting chat2.py...")
        subprocess.run(['python', 'chat2.py'], check=True)
        with lock:
            chat2_done = True
        logging.info("chat2.py execution completed.")
    except Exception as e:
        logging.error(f"Error running chat2.py: {e}")

@app.route('/check_chat2_status')
def check_chat2_status():
    with lock:
        return jsonify({"done": chat2_done})

@app.route('/resultpage')
def result_page():
    return render_template('results.html')

@app.route('/result', methods=['GET'])
def get_result_data():  # Changed function name to avoid conflict
    try:
        logging.info("Trying to read candidate_results.json...")
        with open('candidate_results.json', 'r') as f:
            results = json.load(f)  # Load JSON data from candidate_results.json
        return jsonify(results)  # Return the JSON data
    except FileNotFoundError:
        logging.error("candidate_results.json not found.")
        return jsonify({"error": "Results file not found."}), 404  # Return error if file is not found
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from candidate_results.json.")
        return jsonify({"error": "Error decoding results."}), 500  # Return error if JSON decode fails

# New route for downloading result file
@app.route('/download-results')
def download_result():
    try:
        # Check if the result file exists
        return send_from_directory(RESULTS_FOLDER, RESULT_FILE, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "Results file not found."}), 404


if __name__ == '__main__':
    app.run(debug=True)
