import requests
import json
from first_prompt import InterviewQuestionGenerator  # Import the class

# Ollama API URL
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # assuming default port, adjust if needed

# Set up headers
headers = {
    "Content-Type": "application/json"
}

def call_llama_model(prompt, max_tokens=8000):
    """
    Function to call the LLaMA 3.1 model via the Ollama API with support for streaming responses.
    Args:
        prompt (str): The input prompt for the model.
        max_tokens (int, optional): Maximum tokens allowed for the response. Adjust based on model's capability.
    Returns:
        str: The model's complete response.
    """
    
    # Build the data payload for the API
    data = {
        "model": "mistral-nemo",  # Specify the model
        "prompt": prompt,
        "max_tokens": max_tokens,  # Set max tokens to model's limit
        "temperature": 0.7,  # Adjust if needed
        "top_p": 0.9,  # Adjust for probability sampling
    }

    try:
        # Make the request to Ollama API and enable streaming
        with requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data), stream=True) as response:

            # Check for successful response
            if response.status_code == 200:
                complete_response = ""

                # Stream the response in chunks
                for chunk in response.iter_lines():
                    if chunk:
                        # Parse each chunk of the streamed response
                        try:
                            chunk_data = json.loads(chunk.decode('utf-8'))
                            complete_response += chunk_data.get("response", "")
                        except json.JSONDecodeError as json_err:
                            return f"Error: Could not parse JSON chunk - {json_err}"

                return complete_response
            else:
                return f"Error: Received status code {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error: {str(e)}"

def chatbot():
    # Paths to JSON file
    json_file_path = 'Viserys1/interview_options.json'  # Replace with your actual path

    # Create an instance of InterviewQuestionGenerator
    question_generator = InterviewQuestionGenerator(json_file_path)

    # Get the generated prompt from InterviewQuestionGenerator
    prompt = question_generator.generate_prompt()

    # Call the LLaMA model with the generated prompt
    response = call_llama_model(prompt)

    try:
        json_data = json.loads(response)

        # Store the JSON data in a file named "Generated_questions.json"
        with open('Generated_questions.json', 'w') as json_file:
            json.dump(json_data, json_file, indent=4)  # Writing with indentation for better readability

        print("JSON data has been saved to 'Generated_questions.json'.")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
if __name__ == "__main__":
    # Start the chatbot
    chatbot()
