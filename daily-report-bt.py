import google.generativeai as genai
import os
import json # Added the json library

# --- Configuration ---
# IMPORTANT: Set your Gemini API key as an environment variable
# or replace "YOUR_API_KEY" directly (less secure).
API_KEY = os.getenv("GEMINI_API_KEY", "x")

if API_KEY == "YOUR_API_KEY":
    print("WARNING: Please replace 'YOUR_API_KEY' with your actual Gemini API key or set the GEMINI_API_KEY environment variable.")
    exit()

genai.configure(api_key=API_KEY)

# --- Gemini Model Setup ---
generation_config = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# --- Analysis Function ---
def analyze_post_for_pothole(post_text, reporter_name, post_link):
    """
    Analyzes a given text using Gemini to check for pothole reports
    and extracts the location if found.

    Args:
        post_text (str): The full text of the Facebook post.
        reporter_name (str): The name of the person who made the post.
        post_link (str): The direct link to the Facebook post.

    Returns:
        str: A summary string if a pothole is mentioned, or None otherwise.
    """
    prompt = f"""
    Analyze the following Facebook post text.
    1. Does this post primarily report a pothole or road damage? (Answer YES or NO)
    2. If YES, what is the specific location mentioned? Be as precise as possible (e.g., street name, intersection, landmark). If no specific location is given, state 'Location Unclear'.

    Post Text:
    ---
    {post_text}
    ---

    Respond with ONLY 'YES' or 'NO' on the first line, and the location (or 'Location Unclear') on the second line.
    """

    try:
        response = model.generate_content(prompt)
        lines = response.text.strip().split('\n')

        if len(lines) >= 1 and lines[0].strip().upper() == 'YES':
            location = lines[1].strip() if len(lines) > 1 else "Location Unclear"
            return f"Reporter: {reporter_name}, Location: {location}, Link: {post_link}"
        else:
            return None

    except Exception as e:
        print(f"An error occurred during Gemini API call: {e}")
        return None

# --- Function to Read JSON File ---
def load_posts_from_file(filename="recent_posts.json"):
    """
    Loads post data from a JSON file.

    Args:
        filename (str): The name of the JSON file to read.

    Returns:
        list: A list of post dictionaries, or an empty list if an error occurs.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            posts = json.load(f)
            # Basic validation: Check if it's a list
            if not isinstance(posts, list):
                print(f"Error: JSON file '{filename}' does not contain a list.")
                return []
            return posts
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Please create it.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filename}'. Check its format.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while reading '{filename}': {e}")
        return []

# --- Main Execution Block ---
if __name__ == "__main__":
    # Load posts from the JSON file
    posts_to_analyze = load_posts_from_file()

    if not posts_to_analyze:
        print("No posts loaded. Exiting.")
        exit()

    print("--- Pothole Report Summary ---")
    pothole_reports = []

    for post in posts_to_analyze:
        # Check if the post has the required keys before processing
        if "text" in post and "reporter" in post and "link" in post:
            summary = analyze_post_for_pothole(post["text"], post["reporter"], post["link"])
            if summary:
                pothole_reports.append(summary)
        else:
            print(f"Warning: Skipping a post due to missing data: {post}")


    if pothole_reports:
        for report in pothole_reports:
            print(f"- {report}")
    else:
        print("No pothole reports found in the provided posts.")