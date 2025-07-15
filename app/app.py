import streamlit as st
import PyPDF2
import json
import pandas as pd
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pymongo
from dotenv import load_dotenv
import os

# Environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
mongo_uri = os.getenv("MONGO_URI")

# Clients
try:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    mongo_client = pymongo.MongoClient(mongo_uri)
    db = mongo_client["recruitment_platform"]
    collection = db["job_descriptions"]
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    st.error(f"Initialization error: {e}")
    st.stop()

# CSS for UI
st.markdown(
    """
    <style>
    /* background */
    .stApp {
        background: linear-gradient(to bottom right, #E6F0FA, #FFFFFF);
    }
    /* blocks */
    .block-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    /* text */
    h1, h2, h3, .stMarkdown, .stText {
        color: #003087 !important;
    }
    /* buttons */
    .stButton>button {
        background-color: #E6F0FA;
        color: #003087;
        border: 1px solid #003087;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #D1E0F5;
    }
    /* table */
    .stTable table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    .stTable th, .stTable td {
        padding: 10px;
        border: 1px solid #E6F0FA;
        text-align: left;
    }
    .stTable th {
        background-color: #E6F0FA;
        color: #003087;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Prompt for CV processing
CV_PROMPT = """
Extract the following from the resume text in JSON format:
- name: Full name
- skills: List of skills
- experience: Years of experience (e.g., '3-5 years')
- education: Degree and field
Input: {resume_text}
Return only the JSON output.
"""

# Function to extract data from CV
def extract_resume_data(pdf_file, model_name: str = "gemini-2.5-flash"):
    """Extract text from PDF and process with Gemini API"""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = "".join(page.extract_text() for page in reader.pages)
        response = model.generate_content(
            CV_PROMPT.format(resume_text=text),
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error processing resume: {e}")
        return {}

# Function to generate embeddings for data in mongodb
def get_jd_embeddings():
    """Generate embeddings for all JDs in MongoDB"""
    try:
        jds = list(collection.find())
        if not jds:
            st.error("No job descriptions found in MongoDB. Please run process_jds.py first.")
            return [], []
        jd_texts = [" ".join(jd["skills"] + jd["responsibilities"]) for jd in jds]
        return jds, embedder.encode(jd_texts)
    except Exception as e:
        st.error(f"Error fetching JDs from MongoDB: {e}")
        return [], []

# Function to recommend JDs based on CV
def recommend_jobs(resume_data):
    """Recommend top 5 JDs based on resume skills and experience"""
    resume_text = " ".join(resume_data.get("skills", []) + [resume_data.get("experience", "")])
    resume_embedding = embedder.encode([resume_text])[0]
    jds, jd_embeddings = get_jd_embeddings()
    if not jds:
        return []
    similarities = cosine_similarity([resume_embedding], jd_embeddings)[0]
    top_indices = np.argsort(similarities)[-5:][::-1]
    return [(jds[i], similarities[i]) for i in top_indices]

# App
def main():
    st.title("AI Recruitment Platform")
    
    # Columns for layout
    col1, col2 = st.columns([1, 1], gap="medium")
    
    # CV Upload block
    with col1:
        st.markdown('<div class="block-container">', unsafe_allow_html=True)
        st.header("Upload Your Resume")
        uploaded_file = st.file_uploader("Choose a PDF resume", type="pdf", key="resume_uploader")
        
        if uploaded_file:
            with st.spinner("Processing resume..."):
                resume_data = extract_resume_data(uploaded_file)
                if resume_data:
                    st.success("Resume processed successfully!")
                    st.subheader("Extracted Resume Data")
                    st.json(resume_data)
                    # Store CV data in session state
                    st.session_state.resume_data = resume_data
                else:
                    st.error("Failed to process resume. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # JD Search block
    with col2:
        st.markdown('<div class="block-container">', unsafe_allow_html=True)
        st.header("Find Matching Jobs")
        if st.button("Find Jobs", key="find_jobs"):
            if "resume_data" not in st.session_state:
                st.error("Please upload a resume first.")
            else:
                with st.spinner("Finding job recommendations..."):
                    recommendations = recommend_jobs(st.session_state.resume_data)
                    if recommendations:
                        st.subheader("Recommended Jobs")
                        results = [
                            {
                                "Title": jd["title"],
                                "Company": jd["company"],
                                "Location": jd["location"],
                                "Match Score": f"{score:.2%}"
                            }
                            for jd, score in recommendations
                        ]
                        df = pd.DataFrame(results)
                        st.table(df)
                        
                        # Download as CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download Results as CSV",
                            data=csv,
                            file_name="job_recommendations.csv",
                            mime="text/csv",
                            key="download_csv"
                        )
                        
                        # Display full JD on selection
                        st.subheader("View Full Job Description")
                        selected_job = st.selectbox("Select a Job", [jd["title"] for jd, _ in recommendations], key="job_select")
                        for jd, _ in recommendations:
                            if jd["title"] == selected_job:
                                st.json(jd)
                    else:
                        st.error("No job recommendations found.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()