import json
import pymongo
import toml
import google.generativeai as genai
import os

# Environment variables
config = toml.load("config.toml")
gemini_api_key = config["GEMINI_API_KEY"]
mongo_uri = config["MONGO_URI"]

# Clients
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.5-flash")
mongo_client = pymongo.MongoClient(mongo_uri)
db = mongo_client["recruitment_platform"]
collection = db["job_descriptions"]

# Prompt for LLM
PROMPT = """
Extract the following from the job description in JSON format:
- title: Job title
- responsibilities: List of responsibilities
- skills: List of required skills (just extract the name of the tools/frameworks. no sentences)
- experience: Years of experience (e.g., '3-5 years')
- location: Job location
- company: Company name
- education: Required education
Input: {jd}
Return only the JSON output.
"""

# Function to process JD
def process_jd(jd: dict) -> dict:
    """Process a single JD using the Gemini API"""
    try:
        jd_text = json.dumps(jd)
        response = model.generate_content(
            PROMPT.format(jd=jd_text),
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error processing JD {jd.get('title', 'unknown')}: {e}")
        return jd  # Return original JD as fallback

def main():
    """Process all JDs and store in MongoDB"""
    with open("job_descriptions.json", "r") as f:
        jds = json.load(f)
    
    for jd in jds:
        processed_jd = process_jd(jd)
        collection.insert_one(processed_jd)
        print(f"Stored JD: {processed_jd['title']}")
    
    print(f"Total JDs stored: {collection.count_documents({})}")

if __name__ == "__main__":
    main()