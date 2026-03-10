🚀 AI-Powered ATS Resume Evaluator
An intelligent ATS Resume Analyzer that helps candidates optimize resumes and enables recruiters to rank multiple candidates automatically using LLMs and Retrieval-Augmented Generation (RAG).
Built using Python, Streamlit, and Google Gemini API, this system analyzes resumes against job descriptions to identify skill gaps, ATS compatibility, and candidate ranking.

📌 Problem Statement
Most companies use Applicant Tracking Systems (ATS) to filter resumes before a recruiter even sees them.

📉 75% of resumes are rejected automatically because they are not optimized for ATS.

This project solves that problem by providing:

● AI-powered resume analysis
● ATS compatibility scoring
● Skill gap detection
● Recruiter-side candidate ranking

✨ Key Features

👤 Candidate Mode
Upload your resume and job description to receive:

📊 ATS Compatibility Score
🧠 AI Resume Improvement Suggestions
❌ Missing Technical Skills
📈 Keyword Coverage Analysis
💾 Downloadable ATS Feedback

🧑‍💼 Recruiter Mode
Recruiters can upload multiple resumes and:

📂 Analyze multiple candidates simultaneously
🏆 Rank top candidates automatically
📊 Show Top-N resume matches
🔍 Identify skill gaps instantly

🧠 AI Architecture
The system uses Retrieval-Augmented Generation to provide context-aware responses with Gemini 2.5 Flash via the Gemini API.

User Resume + Job Description
            │
            ▼
Text Extraction (PDF / DOCX / TXT)
            │
            ▼
Keyword + Skill Retrieval
            │
            ▼
RAG Context Injection
            │
            ▼
Gemini Flash 2.5 LLM
            │
            ▼
ATS Analysis + Resume Feedback

🖥 Application UI

Candidate Dashboard
Resume analysis with ATS insights.







Recruiter Dashboard
Upload multiple resumes and rank candidates automatically.






🛠 Tech Stack
Core Technologies:
● Python
● Streamlit
● Gemini API
● Gemini 2.5 Flash

Libraries Used:
● pdfplumber
● python-docx
● python-dotenv
● Pillow
● PyPDF2

📂 Project Structure
ATS-Resume-Evaluator
│
├── app.py
├── requirements.txt
├── .env
├── README.md
│
└── assets
    ├── candidate_dashboard.png
    └── recruiter_dashboard.png

⚙️ Installation
Clone the repository:
git clone https://github.com/yourusername/ats-resume-evaluator.git
cd ats-resume-evaluator

Install dependencies:
pip install -r requirements.txt

Add your API key in .env:
GEMINI_API_KEY=your_api_key_here

Run the application:
streamlit run app.py

📊 Example ATS Output
ATS Compatibility Rating: Medium

Missing Skills:
● Docker
● Kubernetes
● CI/CD

Suggestions:
● Add measurable achievements in projects
● Include relevant deployment tools
● Highlight backend architecture experience

🔮 Future Improvements
● Resume rewriting using LLM
● Semantic skill matching
● Resume keyword heatmaps
● Candidate analytics dashboard
● Faster inference with response caching

👩‍💻 Author
Lavanya Ahlawat

⭐ If You Like This Project
Consider giving it a star ⭐ on GitHub.
