import json
import random
import google.generativeai as genai
from typing import List, Dict
import toml

# Environment variables
config = toml.load("config.toml")
gemini_api_key = config["GEMINI_API_KEY"]

# Roles for each domain
ROLES = {
    "Machine Learning": [
        "Machine Learning Engineer", "Senior ML Engineer", "ML Research Scientist",
        "Deep Learning Specialist", "NLP Engineer"
    ],
    "Data Science": [
        "Data Scientist", "Senior Data Scientist", "Data Analyst",
        "Statistical Modeler", "Data Engineer"
    ],
    "AI": [
        "AI Engineer", "AI Research Scientist", "Computer Vision Engineer",
        "Robotics AI Specialist", "AI Ethics Researcher"
    ],
    "Business Analytics": [
        "Business Analyst", "BI Specialist", "Data Visualization Expert",
        "Business Intelligence Analyst", "Analytics Consultant"
    ],
    "Project Management": [
        "Project Manager", "Scrum Master", "Product Owner",
        "Program Manager", "Agile Coach"
    ],
    "Software Engineering": [
        "Frontend Developer", "Backend Developer", "Full-Stack Developer",
        "Software Engineer"
    ],
    "DevOps": [
        "DevOps Engineer", "Site Reliability Engineer", "Cloud Specialist"
    ],
    "Quality Assurance": [
        "QA Engineer", "QA Manager"
    ]

}

# Locations and companies
LOCATIONS = [
    "San Francisco, CA", "New York, NY", "London, UK", "Bangalore, India",
    "Remote", "Boston, MA", "Seattle, WA", "Toronto, Canada", "Colombo, Sri Lanka"
]
COMPANIES = [
    "TechCorp", "InnovateAI", "DataWorks", "CloudPeak", "NextGen Solutions",
    "Analytix Inc.", "SmartSys", "FutureTech"
]

# Prompt for JD generation
PROMPT = """
Generate a realistic job description for a {role} in the {domain} domain. Include:
- Job Title
- Company Name
- Location
- Responsibilities (4-6 bullet points)
- Required Skills (Tech Stack, 5-6 tools/frameworks)
- Experience (in years)
- Education (degree and field)
Return the output in JSON format with the fields: title, company, location, responsibilities, skills, experience, education.
Ensure the job description is detailed, professional, and realistic for the role.
"""

# Function to generate JD for a role
def generate_jd(role: str, domain: str) -> Dict:
    """Generate a single job description using the Gemini API"""
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            PROMPT.format(role=role, domain=domain),
            generation_config={"response_mime_type": "application/json"}
        )
        jd_text = response.text
        # Parse JSON response
        jd = json.loads(jd_text)
        # Add company and location
        jd["company"] = random.choice(COMPANIES)
        jd["location"] = random.choice(LOCATIONS)
        return jd
    except Exception as e:
        print(f"Error generating JD for {role}: {e}")
        return {}

# Function to generate 200 JDs
def generate_all_jds() -> List[Dict]:
    """Generate 200 job descriptions across specified domains"""
    jds = []
    # Target distribution
    jd_counts = {
        "Machine Learning": 40,
        "Data Science": 30,
        "AI": 30,
        "Software Engineering": 20,
        "Business Analytics": 20,
        "Project Management": 20,
        "DevOps": 20,
        "Quality Assurance": 20
    }

    for domain, count in jd_counts.items():
        roles = ROLES[domain]
        for _ in range(count):
            role = random.choice(roles)
            jd = generate_jd(role, domain)
            if jd:
                jds.append(jd)
    
    # Exactly 200 JDs
    while len(jds) < 200:
        domain = random.choice(list(ROLES.keys()))
        role = random.choice(ROLES[domain])
        jd = generate_jd(role, domain)
        if jd:
            jds.append(jd)
    
    return jds[:200]  # Trimming to 200 if exceeded

# Function to load the JDs to a JSON File
def save_jds(jds: List[Dict], filename: str = "job_descriptions.json"):
    """Save job descriptions to a JSON file"""
    try:
        with open(filename, "w") as f:
            json.dump(jds, f, indent=4)
        print(f"Saved {len(jds)} job descriptions to {filename}")
    except Exception as e:
        print(f"Error saving JDs: {e}")

def main():
    """Main function to generate and save job descriptions"""
    jds = generate_all_jds()
    save_jds(jds)
    
    # Print sample JD
    if jds:
        print("\nSample Job Description:")
        print(json.dumps(jds[0], indent=4))

if __name__ == "__main__":
    main()