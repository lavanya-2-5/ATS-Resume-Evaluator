from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import pdfplumber
from google import genai
from docx import Document
import time

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
# ---------------- GEMINI SETUP ----------------
@st.cache_resource
def load_gemini_client():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

client = load_gemini_client()
# ---------------- RAG SETUP ----------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def load_knowledge_base():
    with open("knowledge_base/skills.txt", "r") as f:
        docs = f.readlines()
    return [d.strip() for d in docs]

kb_docs = load_knowledge_base()

# create embeddings
kb_embeddings = embedding_model.encode(kb_docs)

# build FAISS index
dimension = kb_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(kb_embeddings))

def retrieve_context(query, top_k=2):
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(np.array(query_embedding), top_k)
    results = [kb_docs[i] for i in indices[0]]
    return "\n".join(results)

# ---------------- ATS TECH KEYWORDS ----------------
TECH_KEYWORDS = {
    "python", "java", "sql", "c++", "javascript",
    "tensorflow", "pytorch", "scikit-learn",
    "pandas", "numpy",
    "machine learning", "deep learning", "nlp",
    "data science", "data analysis",
    "docker", "kubernetes",
    "aws", "gcp", "azure",
    "flask", "django", "react"
}

def filter_relevant_keywords(raw_keywords):
    filtered = []
    for word in raw_keywords:
        w = word.lower().strip()
        if w in TECH_KEYWORDS and len(w) > 2:
            filtered.append(w)
    return list(dict.fromkeys(filtered))[:7]

# ---------------- GEMINI RESPONSE ----------------
@st.cache_data(ttl=600)
def get_gemini_response(prompt, resume_text, job_description):
    try:

        # RAG retrieval
        context = retrieve_context(job_description)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
{prompt}

Retrieved Industry Skill Context:
{context}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}
""" , 
       config={
           "temperature":0.2
       }
        )
        return response.text
    except Exception as e:
         if "429" in str(e):
            time.sleep(60)
            return "API rate limit reached. Please try again in a minute."
         return f"Error generating response: {e}"
    
# ---------------- RESUME TEXT EXTRACTION ----------------
def extract_text_from_resume(uploaded_file):
    try:
        file_type = uploaded_file.name.split(".")[-1].lower()
        if file_type == "pdf":
            text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text.strip()
        elif file_type == "docx":
            doc = Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        elif file_type == "txt":
            return uploaded_file.read().decode("utf-8")
        else:
            st.warning(f"Unsupported file type: {file_type}")
            return ""
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        return ""

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="ATS Resume Expert")
st.title("ATS Resume Evaluation System")

mode = st.radio("Select Dashboard", ["Candidate Mode", "Recruiter Mode"])

# ---------------- PROMPTS ----------------
candidate_prompt_improve = """
You are a career coach and ATS expert.
Provide:
- Top 5 missing or weak technical skills
- 3 concise resume improvement suggestions
- 2 example resume lines (if applicable)
Keep it short, bullet points, under 150 words.
"""

candidate_prompt_ats = """
You are an ATS optimization expert.
Provide:
- ATS compatibility rating (Low / Medium / High)
- Missing technical skills (comma-separated)
- 3 quick ATS improvement tips
Keep output concise and short.
"""

recruiter_prompt_rank = """
You are an ATS recruiter assistant.

Rank resumes by best match with the job description.

IMPORTANT RULES:
- Return ONLY the top N resumes requested.
- Do NOT show more resumes than requested.
- If N = 1, return ONLY the single best resume.

Format:
Resume <number>
Match percentage: <score>
Key ATS skills missing: <skills>

No explanations. No extra text.
"""

# ---------------- CANDIDATE DASHBOARD ----------------
if mode == "Candidate Mode":
    st.subheader("Candidate Dashboard")

    job_desc = st.text_area("Enter Job Description", key="candidate_jd")
    resume_file = st.file_uploader(
        "Upload Your Resume (PDF / DOCX / TXT)",
        type=["pdf", "docx", "txt"]
    )

    col1, col2 = st.columns(2)

    with col1:
        btn_improve = st.button("Resume Improvement Suggestions")

    with col2:
        btn_ats = st.button("ATS Readiness Check")

    # Session state storage
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""

    if resume_file:
        st.session_state.resume_text = extract_text_from_resume(resume_file)

    resume_text = st.session_state.resume_text

    if resume_file and job_desc:

        # Resume Improvement
        if btn_improve:
            with st.spinner("Analyzing resume..."):
                result = get_gemini_response(
                    candidate_prompt_improve,
                    resume_text,
                    job_desc
                )

            st.subheader("Resume Improvement Feedback")
            st.write(result)

            st.download_button(
                "Download Improvements",
                data=result,
                file_name="resume_improvements.txt"
            )

        # ATS Readiness
        if btn_ats:
            with st.spinner("Analyzing ATS readiness..."):
                result = get_gemini_response(
                    candidate_prompt_ats,
                    resume_text,
                    job_desc
                )

            st.subheader("ATS Readiness Feedback")

            formatted_result = result.replace("  ", " ").replace(
                "Missing technical skills:", "\nMissing technical skills:"
            ).replace(
                "3 quick ATS improvement tips:", "\n3 quick ATS improvement tips:"
            )

            st.markdown(formatted_result)

            raw_keywords = [w.strip() for w in result.split(",")]
            relevant_keywords = filter_relevant_keywords(raw_keywords)

            if relevant_keywords:
                st.markdown("**Missing ATS Skill Signals:**")
                st.write(relevant_keywords)
            else:
                st.success("No critical ATS skill gaps detected")

            st.download_button(
                "Download ATS Feedback",
                data=result,
                file_name="ats_feedback.txt"
            )

    elif (btn_improve or btn_ats) and not resume_file:
        st.warning("Please upload your resume and enter the job description.")

# ---------------- RECRUITER DASHBOARD ----------------
else:
    st.subheader("Recruiter Dashboard")
    job_desc = st.text_area("Enter Job Description", key="recruiter_jd")
    resume_files = st.file_uploader(
        "Upload Multiple Resumes (PDF / DOCX / TXT)", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True
    )
    
    top_n = st.number_input("Select number of top resumes to show", min_value=1, max_value=10, value=3)
    btn_rank = st.button("Rank Resumes")
    
    if resume_files and job_desc and btn_rank:
        resumes_texts = [extract_text_from_resume(f) for f in resume_files]
        combined_prompt = recruiter_prompt_rank + f"\nJob Description:\n{job_desc}\nResumes:\n"
        for i, text in enumerate(resumes_texts):
            combined_prompt += f"\nResume {i+1}:\n{text}\n"
        combined_prompt += f"\nReturn ONLY the TOP {top_n} resumes. Do not list others."
        with st.spinner("Ranking resumes..."):
               ranking = get_gemini_response(combined_prompt, "", "")
        st.subheader(f"Top {top_n} Resumes Ranking")
        st.write(ranking)
    
    elif btn_rank and (not resume_files or not job_desc):
        st.warning("Please provide job description and upload multiple resumes for ranking.")
