import json

class ResponseEvaluator:
    def __init__(self, json_file_path, preprompt=None, postprompt=None):
        self.json_file_path = json_file_path
        # Default prompts if not provided
        self.preprompt = preprompt or """Here is the candidate's response in Json format: """
        self.postprompt = postprompt or """ Evaluate the candiate response against the question he was asked deeply and more accurately
        according to the keys in the following json and give marks out of 100 in each metric:
        {
        "Technical Proficiency": 0,
        "Problem-Solving Ability": 0,
        "Cultural Fit": 0,
        "Communication Skills": 0,
        "Collaboration and Teamwork": 0,
        "Adaptability": 0,
        "Initiative and Proactiveness": 0,
        "Emotional Intelligence": 0
        }
        and strictly return just and just this json back with updated marks.No other opening
        and closing statements needed. In your response you should only return the json of  metrics mentioned befor
        and no expalnation or any other statements from your side. follow this strictly!
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

