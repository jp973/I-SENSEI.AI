# backend/utils/technical_utils.py
import google.generativeai as genai
import random
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_question_pool(job_description):
    prompt = f"""
You're an AI mock interviewer.

Generate 20 varied and role-specific technical interview questions for the following job description:

{job_description}
first 5 questions should be easy, next 5 medium, and last 10 hard.
Return only the questions as a numbered list.
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    question_list = [line.split(". ", 1)[-1].strip() for line in response.text.strip().splitlines() if line.strip()]
    return question_list

def get_random_questions(pool, count=10):
    return random.sample(pool, min(count, len(pool)))
