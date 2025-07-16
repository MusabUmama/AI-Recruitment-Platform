# AI Recruitment Platform

An AI-powered job matching platform that uses Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to match resumes with job descriptions. The platform extracts structured data from PDF resumes, processes job descriptions, and recommends the top 5 matching jobs based on skills and experience..

## Features

- **Resume Processing**: Upload a PDF resume to extract name, skills, experience, and education using the Google Gemini API.
- **Job Description Processing**: Processes 200 job descriptions stored in MongoDB Atlas, extracting structured data (title, responsibilities, skills, experience, location, company, education).
- **Job Matching**: Uses `sentence-transformers` to generate embeddings and cosine similarity for RAG-based matching of resumes to job descriptions.
- **UI**: Streamlit-based interface.
- **Export**: Download job recommendations as a CSV file.
- **View Full JD**: Select a job to view its full description in JSON format.

## Setup Instructions

1. **Clone the Repository**:

   ```bash
   git clone <repo-url>
   cd AI-Recruitment-Platform
   ```

2. **Install Dependencies**:

Ensure Python 3.11 is installed.
Install required packages:pip install -r requirements.txt

3. **Set Up Environment Variables**:

Copy .env.example to .env:cp .env.example .env

Edit .env with your credentials:GEMINI_API_KEY=your-gemini-api-key
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.<random>.mongodb.net/recruitment_platform?retryWrites=true&w=majority

Obtain GEMINI_API_KEY from Google AI Studio.
Set up MONGO_URI in MongoDB Atlas:
Create a database user with read/write permissions.
Encode special characters in the password (e.g., @ → %40) using urlencoder.org.
Ensure Network Access allows connections from your IP or 0.0.0.0/0.

4. **Generate Job Descriptions**:

Run:python src/generate_jds.py

This generates 200 job descriptions in job_descriptions.json.

5. **Process Job Descriptions**:

Run:python src/process_jds.py

This processes job_descriptions.json and stores structured data in MongoDB Atlas.

6. **Run the Application**:

Run:streamlit run app/app.py

## Deployment

The application is deployed on Streamlit Cloud for easy access.

Deploy on Streamlit Cloud:

Log in to streamlit.io.
Create a new app and link it to your GitHub repository.
Set the app to run app/app.py.
Add environment variables (GEMINI_API_KEY, MONGO_URI) in Streamlit Cloud settings.
Deploy and access the app at the provided URL.

Deployed URL:



## Documentation

See docs/documentation.pdf for detailed project information.
