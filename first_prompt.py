import json

class InterviewQuestionGenerator:
    def __init__(self, json_file_path, preprompt=None, postprompt=None):
        self.json_file_path = json_file_path
        # Default prompts if not provided
        self.preprompt = preprompt or """You are an AI that generates interview questions based on given metrics. 
Return strictly only the questions in JSON format, no extra words(no opening and closing lines). Guidelines: """
        self.postprompt = postprompt or """The JSON format must have only "question_id" and "question". Example:
[
    {"question_id": <integer>, "question": "<string>"}
]
Next, I'll provide candidate responses in JSON format.
done
"""
    
    def load_json_data(self):
        """Reads the JSON file and returns the data."""
        try:
            with open(self.json_file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: The file at {self.json_file_path} was not found.")
        except json.JSONDecodeError:
            raise ValueError("Error: The file contains invalid JSON.")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")
    
    def generate_prompt(self):
        """Generates the full prompt with the questions."""
        try:
            # Load the JSON data
            data = self.load_json_data()

            # Convert the data to a single-line JSON string
            json_string = json.dumps(data)  # No indent argument, results in a single-line string

            # Concatenate preprompt, json string, and postprompt
            final_output = self.preprompt + json_string + self.postprompt
            return final_output
        
        except Exception as e:
            return str(e)

