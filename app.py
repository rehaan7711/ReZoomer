from dotenv import load_dotenv
load_dotenv()

import streamlit as st 
import os
from PyPDF2 import PdfReader
import google.generativeai as genai
import base64
from io import BytesIO
from docx import Document

# Load API key from .env
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    st.error('Google API key not found. Please set GOOGLE_API_KEY in your .env file.')
    st.stop()
genai.configure(api_key=api_key)

# Add a sidebar for branding, intro, and instructions
st.sidebar.image('myphoto.jpg', width=100)
st.sidebar.title('ATS Resume Analyzer')

# Add your 4-line intro
st.sidebar.markdown('''
**About Me:**

👋 I'm Abdul Rehaan, a final-year Information Technology student at MJCET with a passion for AI, Machine Learning, and Full Stack Development.
🚀 I’ve led impactful tech projects—from IoT Botnet Detection to Smart Resume Analyzers—blending innovation with real-world problem solving.
💼 My journey includes hands-on experience in Python, OpenCV, FastAPI, and AI-driven solutions, backed by internships and volunteer leadership.
🌍 Driven by curiosity and purpose, I aim to build intelligent systems that create meaningful change in society.

.
''')

# Add LinkedIn and GitHub links
st.sidebar.markdown('[LinkedIn](https://linkedin.com/in/abdul-rehaan) | [GitHub](https://github.com/rehaan7711)')

# Main page design
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-top: 2rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: bold;
        box-shadow: 0 4px 14px 0 rgba(0,0,0,0.15);
        transition: 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
        color: #fff;
        transform: scale(1.05);
    }
    .stButton>button:active {
        transform: scale(0.97);
        background: linear-gradient(90deg, #ff9966 0%, #ff5e62 100%);
        color: #fff;
        box-shadow: 0 2px 7px 0 rgba(0,0,0,0.18);
    }
    .stTextArea textarea {
        border-radius: 10px;
        min-height: 120px;
        font-size: 1.05rem;
        background: #f7fafd;
    }
    </style>
""" , unsafe_allow_html=True)

st.markdown('<div class="main">', unsafe_allow_html=True)

# Add a bold, styled heading at the top-middle of the page
st.markdown('''
<div style="text-align:center; margin-bottom: 0.5rem;">
    <span style="font-size:1.15rem; font-weight:600; color:#4B0082; letter-spacing:0.5px;">
        ✨ Upload your resume and <span style="color:#185a9d; font-size:1.18rem; font-weight:bold;">job description</span> to discover how well your profile matches the role!
    </span><br>
    <span style="font-size:1.05rem; color:#333; font-weight:500;">
        Get instant, AI-powered feedback and a personalized, professional resume template to boost your chances of selection.
    </span>
</div>
''', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; font-weight:bold; color:#333; margin-bottom: 1.5rem; letter-spacing:1px; text-shadow: 0 2px 8px #b0c4de;">UPLOAD YOUR RESUME</h2>', unsafe_allow_html=True)

uploaded_file = st.file_uploader('Upload your resume (PDF only)', type=['pdf'])
job_description = st.text_area('Paste the Job Description here:', height=150)

resume_text = ''
ats_score = None

if uploaded_file:
    # Extract text from PDF using PyPDF2
    pdf_reader = PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        resume_text += page.extract_text() or ''

    st.subheader('Extracted Resume Text')
    st.text_area('Resume Text', resume_text, height=200)

    # Calculate ATS score
    if job_description.strip():
        score_prompt = f"You are an ATS (Applicant Tracking System). Analyze the following resume and job description. Give an accurate ATS match score (0-100) for how well the resume matches the job description. Only output the score as a number, nothing else.\n\nJob Description:\n{job_description}\n\nResume:\n{resume_text}"
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            score_response = model.generate_content(score_prompt)
            ats_score = ''.join(filter(str.isdigit, score_response.text.split('\n')[0]))
            if ats_score:
                ats_score = int(ats_score)
        except Exception as e:
            st.warning(f'Could not calculate ATS score: {e}')

    if ats_score is not None:
        st.markdown(f'<div style="text-align:center; margin-top:1rem; margin-bottom:1rem;"><span style="font-size:1.5rem; font-weight:bold; color:#185a9d;">ATS Accurate Score: <span style=\"color:#43cea2;\">{ats_score}/100</span></span></div>', unsafe_allow_html=True)

    if st.button('Analyze Resume & Job Match', key='analyze_btn'):
        with st.spinner('Analyzing...'):
            prompt = f"You are an expert ATS (Applicant Tracking System) and career coach. Compare the following resume to the job description.\n\nJob Description:\n{job_description}\n\nResume:\n{resume_text}\n\n1. Tell me if this resume matches the job description (with a percentage match and reasoning).\n2. List the strengths and weaknesses of the resume for this job.\n3. Suggest specific improvements and what should be added to the resume to increase the chances of selection.\n4. Give a short summary for the candidate.\n5. Based on the job description and the uploaded resume, generate a new, improved resume template for this job role, using relevant information from the uploaded resume and filling in missing sections as needed. Format the resume in a professional way."
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.subheader('ATS Analysis & Suggestions')
                st.write(response.text)

                # Extract the suggested resume from the response (assume it's after a marker)
                if 'RESUME TEMPLATE:' in response.text:
                    suggested_resume = response.text.split('RESUME TEMPLATE:')[-1].strip()
                else:
                    suggested_resume = response.text.split('Resume Template:')[-1].strip() if 'Resume Template:' in response.text else response.text

                st.subheader('Suggested Resume for this Job')
                st.code(suggested_resume, language='markdown')

                # Generate a downloadable .docx file
                doc = Document()
                for line in suggested_resume.split('\n'):
                    doc.add_paragraph(line)
                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                b64 = base64.b64encode(buffer.read()).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="Suggested_Resume.docx"><button style="background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%); color: white; border-radius: 10px; font-size: 1.1rem; font-weight: bold; padding: 0.5rem 1.5rem; border: none; box-shadow: 0 4px 14px 0 rgba(0,0,0,0.15); cursor: pointer;">Download Suggested Resume</button></a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f'Error analyzing resume: {e}')
else:
    st.info('Please upload a PDF resume file to begin.')

st.markdown('</div>', unsafe_allow_html=True)
