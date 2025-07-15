import json
import pymongo
from openai import OpenAI
from dotenv import load_dotenv
import os

# Environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
mongo_uri = os.getenv("MONGO_URI")

# Clients
client = OpenAI(api_key=openai_api_key)
mongo_client = pymongo.MongoClient(mongo_uri)
db = mongo_client["recruitment_platform"]
collection = db["job_descriptions"]

# Prompt for LLM
PROMPT = """
Extract the following from the job description in JSON format:
- title: Job title
- responsibilities: List of responsibilities
- skills: List of required skills
- experience: Years of experience (e.g., '3-5 years')
- location: Job location
- company: Company name
- education: Required education
Input: {jd}
Return only the JSON output.
"""

# Function to process JD
def process_jd(jd: dict) -> dict:
    """Process a single JD using the LLM"""
    try:
        jd_text = json.dumps(jd)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at extracting structured data."},
                {"role": "user", "content": PROMPT.format(jd=jd_text)}
            ],
            temperature=0.5,
            max_tokens=300
        )
        return json.loads(response.choices[0].message.content)
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