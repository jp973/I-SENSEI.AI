# backend\resume_parser.py
import PyPDF2
import io

def extract_resume_text(uploaded_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text.strip()
    # st.session_state['resume_text'] = text



