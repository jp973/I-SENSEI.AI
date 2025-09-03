# frontend\pages\resume_interview.py
import streamlit as st
from backend.utils.resume_parser import extract_resume_text
import google.generativeai as genai
from dotenv import load_dotenv
import os
from audio_recorder_streamlit import audio_recorder
from backend.utils.voice_utils import question_to_speech, speech_to_text
import tempfile
from backend.utils.faiss_utils import add_to_index, is_similar


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------------
# Generate question using Gemini
# -------------------------------
def generate_resume_question(resume_text, prev_qas=[]):
    conversation = "\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in prev_qas])
    prompt_base = f"""
You are an AI interviewer. Ask a professional, relevant question based on the candidate's resume and past answers. Only ask one question at a time.do not ask lengthy questions.make sure the question is unique and not similar to previous ones.

Resume:
{resume_text}

Conversation so far:
{conversation}

Next Question:
"""
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Try up to 5 times to get a unique (non-similar) question
    for _ in range(5):
        response = model.generate_content(prompt_base)
        question = response.text.strip()

        if not is_similar(question):  # Check against existing ones in FAISS
            add_to_index(question)   # Store in vector index
            return question

    # If all were similar
    return "⚠️ Unable to generate a new unique question. Please try again."


# -------------------------------
# UI Renderer
# -------------------------------
def render():
    st.header("📄 Resume-Based Interview")

    # Initialize session variables
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'resume_total_questions' not in st.session_state:
        st.session_state.resume_total_questions = 3

    # Ended session - feedback prompt
    if st.session_state.get('question_count', 0) >= st.session_state.resume_total_questions:
        st.success("✅ You've completed this interview session.")
        st.markdown("👉 Please go to the **Feedback** page to view your results.")
        if st.button("🔄 Restart Interview"):
            for key in [
                "conversation_history", "current_question",
                "question_count", "interview_started",
                "resume_total_questions"
            ]:
                st.session_state.pop(key, None)
            st.rerun()
        return

    # Resume upload
    uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type="pdf")
    if uploaded_file:
        text = extract_resume_text(uploaded_file)
        st.success("✅ Resume uploaded successfully.")
        st.session_state.resume_text = text

        # Mode selection
        st.subheader("🎛️ Select Interview Mode")
        mode = st.radio("Choose mode", ["Text-Based", "Voice-Based"], horizontal=True)

        # Number of questions
        if not st.session_state.interview_started:
            st.subheader("⚙️ Number of Questions")
            st.session_state.resume_total_questions = st.slider(
                "Select number of questions",
                1, 10, 3
            )

        # Start button
        if not st.session_state.interview_started:
            if st.button("🎤 Start Interview"):
                st.session_state.interview_started = True
                st.session_state.current_question = generate_resume_question(
                    st.session_state.resume_text,
                    st.session_state.conversation_history
                )
                st.rerun()

        elif st.session_state.question_count < st.session_state.resume_total_questions:
            st.markdown(f"**🧑‍💼 Question {st.session_state.question_count + 1}:**")
            st.markdown(st.session_state.current_question)

            if mode == "Text-Based":
                user_answer = st.text_area("✍️ Your Answer", key=f"answer_{st.session_state.question_count}")
                if st.button("Submit Answer"):
                    if user_answer.strip() != "":
                        st.session_state.conversation_history.append({
                            "question": st.session_state.current_question,
                            "answer": user_answer.strip()
                        })
                        st.session_state.question_count += 1
                        if st.session_state.question_count < st.session_state.resume_total_questions:
                            st.session_state.current_question = generate_resume_question(
                                st.session_state.resume_text,
                                st.session_state.conversation_history
                            )
                        else:
                            st.session_state.current_question = None
                        st.rerun()
                    else:
                        st.warning("⚠️ Please enter your answer before submitting.")

            elif mode == "Voice-Based":
                st.info("🔊 Playing interview question...")
                audio_path = question_to_speech(st.session_state.current_question)
                st.audio(audio_path, format="audio/mp3")

                st.info("🎤 Record your answer")
                audio_bytes = audio_recorder(key=f"resume_voice_q{st.session_state.question_count}")
                if audio_bytes and len(audio_bytes) > 1000:
                    audio_file_path = os.path.join(tempfile.gettempdir(), f"resume_user_q{st.session_state.question_count + 1}.wav")
                    with open(audio_file_path, "wb") as f:
                        f.write(audio_bytes)

                    st.audio(audio_bytes, format="audio/wav")
                    st.success("🎧 Audio recorded. Transcribing...")

                    try:
                        user_answer = speech_to_text(audio_file_path)
                        st.write(f"📝 **Transcribed Answer:** `{user_answer}`")

                        st.session_state.conversation_history.append({
                            "question": st.session_state.current_question,
                            "answer": user_answer
                        })
                        st.session_state.question_count += 1
                        if st.session_state.question_count < st.session_state.resume_total_questions:
                            st.session_state.current_question = generate_resume_question(
                                st.session_state.resume_text,
                                st.session_state.conversation_history
                            )
                        else:
                            st.session_state.current_question = None

                        st.rerun()
                    except Exception as e:
                        st.error("❌ Transcription failed.")
                        st.exception(e)
                else:
                    st.warning("⚠️ Please record a longer answer before submitting.")
