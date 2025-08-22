# frontend\pages\feedback.py
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from backend.utils.pdf_utils import generate_feedback_pdf
import re


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_feedback(conversation):
    prompt = f"""
You are an interview coach.

Below is a candidate's mock interview Q&A session. Please provide:
1. A brief overall evaluation (max 2 sentences).
2. 2 specific improvement tips in bullet points.
3. A rating out of 10.
4.Recommendation (Hire / Consider / Reject)

Conversation:
{conversation}

Format:
Summary: ...
Tips:
- ...
- ...
Rating: ...
"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

def render():
    st.header("📊 Interview Feedback")
    
    if 'conversation_history' not in st.session_state or not st.session_state['conversation_history']:
        st.warning("No conversation data available. Please complete an interview first.")
        return

    conversation = ""
    for i, pair in enumerate(st.session_state['conversation_history']):
        conversation += f"\nQ{i+1}: {pair['question']}\nA{i+1}: {pair['answer']}\n"

    feedback = generate_feedback(conversation)
    st.markdown("### 📝 AI Feedback")
    st.markdown(feedback)
        # Extract rating for filename (optional but clean)
    rating_line = [line for line in feedback.splitlines() if "Rating:" in line]
    if rating_line:
        rating_text = rating_line[0].split(":")[-1]
        match = re.search(r'\d+', rating_text)
        rating = int(match.group()) if match else 0
    else:
        rating = 0
    # Generate PDF using the utility function
    pdf_buffer = generate_feedback_pdf(feedback, rating)

    # Download button
    st.download_button(
        label="📥 Download Feedback as PDF",
        data=pdf_buffer,
        file_name="interview_feedback.pdf",
        mime="application/pdf"
    )

    
