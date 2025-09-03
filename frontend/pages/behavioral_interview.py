# frontend\pages\behavioral_interview.py
import streamlit as st
from backend.utils.voice_utils import question_to_speech, speech_to_text
from audio_recorder_streamlit import audio_recorder
import pandas as pd
import os
import tempfile
import random

# Load questions from Excel
@st.cache_data
def load_behavioral_questions(path="data/Questions.xlsx", column="Questions"):
    df = pd.read_excel(path)
    return df[column].dropna().tolist()

def render():
    st.header("🧠 Behavioral Interview")

    # Load questions from Excel
    questions = load_behavioral_questions()

    # Initialize session state variables
    if "behav_started" not in st.session_state:
        st.session_state.behav_started = False
    if "behav_mode" not in st.session_state:
        st.session_state.behav_mode = "Text-Based"
    if "behav_current" not in st.session_state:
        st.session_state.behav_current = 0
    if "behav_answers" not in st.session_state:
        st.session_state.behav_answers = []
    if "behav_selected_questions" not in st.session_state:
        st.session_state.behav_selected_questions = []
    if "behav_total_questions" not in st.session_state:
        st.session_state.behav_total_questions = 3

    # End of interview check (put this ABOVE question access)
    if st.session_state.behav_started and st.session_state.behav_current >= len(st.session_state.behav_selected_questions):
        st.success("✅ You have completed the behavioral interview!")
        st.markdown("👉 Go to the **Feedback** tab to see your performance.")
        st.session_state["conversation_history"] = st.session_state.behav_answers

        if st.button("🔄 Restart Behavioral Interview"):
            for key in ["behav_started", "behav_mode", "behav_current", "behav_answers", "behav_selected_questions"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        return

    # Before interview starts
    if not st.session_state.behav_started:
        st.subheader("🎙️ Select Interview Mode")
        st.session_state.behav_mode = st.radio("Choose mode", ["Text-Based", "Voice-Based"], horizontal=True)

        st.subheader("⚙️ Number of Questions")
        st.session_state.behav_total_questions = st.slider(
            "Select number of questions",
            1,
            min(len(questions), 20),
            3
        )

        if st.button("🚀 Start Behavioral Interview"):
            first_question = questions[0]
            remaining_questions = questions[1:]
            num_remaining = st.session_state.behav_total_questions - 1

            random_selected = random.sample(remaining_questions, num_remaining) if num_remaining > 0 else []
            st.session_state.behav_selected_questions = [first_question] + random_selected
            st.session_state.behav_started = True
            st.rerun()

        return  # stop here if not started

    # Interview in progress
    question = st.session_state.behav_selected_questions[st.session_state.behav_current]
    st.subheader(f"🧑‍💼 Question {st.session_state.behav_current + 1}")
    st.markdown(question)

    mode = st.session_state.behav_mode

    if mode == "Text-Based":
        answer = st.text_area("✍️ Your Answer", key=f"behav_answer_{st.session_state.behav_current}")
        if st.button("Next"):
            if answer.strip():
                st.session_state.behav_answers.append({
                    "question": question,
                    "answer": answer.strip()
                })
                st.session_state.behav_current += 1
                st.rerun()
            else:
                st.warning("⚠️ Please enter your answer before proceeding.")

    elif mode == "Voice-Based":
        st.info("🔊 Playing question audio...")
        audio_path = question_to_speech(question)
        st.audio(audio_path, format="audio/mp3")

        st.info("🎤 Record your answer")
        audio_bytes = audio_recorder(key=f"behav_voice_{st.session_state.behav_current}")

        if audio_bytes and len(audio_bytes) > 1000:
            audio_file_path = os.path.join(tempfile.gettempdir(), f"behav_user_q{st.session_state.behav_current+1}.wav")
            with open(audio_file_path, "wb") as f:
                f.write(audio_bytes)

            st.audio(audio_bytes, format="audio/wav")
            st.success("🎧 Audio recorded. Transcribing...")

            try:
                answer = speech_to_text(audio_file_path)
                st.write(f"📝 **Transcribed Answer:** `{answer}`")

                st.session_state.behav_answers.append({
                    "question": question,
                    "answer": answer
                })
                st.session_state.behav_current += 1
                st.rerun()

            except Exception as e:
                st.error("❌ Transcription failed.")
                st.exception(e)
        else:
            st.warning("⚠️ Please record a longer answer before clicking Next.")
