import streamlit as st
from backend.utils.technical_utils import generate_question_pool, get_random_questions
from backend.utils.voice_utils import question_to_speech, speech_to_text
from audio_recorder_streamlit import audio_recorder
import os

def render():
    st.header("💻 Technical Interview")

    # Initialize session state
    if 'tech_started' not in st.session_state:
        st.session_state.tech_started = False
    if 'tech_questions' not in st.session_state:
        st.session_state.tech_questions = []
    if 'tech_current' not in st.session_state:
        st.session_state.tech_current = 0
    if 'tech_answers' not in st.session_state:
        st.session_state.tech_answers = []
    if 'tech_job_description' not in st.session_state:
        st.session_state.tech_job_description = ""
    if 'tech_mode' not in st.session_state:
        st.session_state.tech_mode = "Text-Based"

    # If interview not started
    if not st.session_state.tech_started:
        st.subheader("📄 Enter Job Description")
        job_desc = st.text_area("Paste the job description here", height=200, key="tech_job_description")

        st.subheader("🎙️ Select Interview Mode")
        st.session_state.tech_mode = st.radio("Choose mode", ["Text-Based", "Voice-Based"], horizontal=True)

        if st.button("🚀 Start Interview"):
            if job_desc.strip():
                pool = generate_question_pool(job_desc)
                questions = get_random_questions(pool, 10)
                st.session_state.tech_questions = questions
                st.session_state.tech_answers = []
                st.session_state.tech_current = 0
                st.session_state.tech_started = True
                st.experimental_rerun()
            else:
                st.warning("Please provide a job description.")
        return

    # Interview in progress
    questions = st.session_state.tech_questions
    index = st.session_state.tech_current
    mode = st.session_state.tech_mode

    if index < len(questions):
        st.subheader(f"🧑‍💻 Question {index + 1}")
        st.write(questions[index])

        if mode == "Text-Based":
            answer = st.text_area("Your Answer", key=f"tech_answer_{index}")
            if st.button("Next"):
                if answer.strip():
                    st.session_state.tech_answers.append({
                        "question": questions[index],
                        "answer": answer.strip()
                    })
                    st.session_state.tech_current += 1
                    st.experimental_rerun()
                else:
                    st.warning("Please provide an answer before proceeding.")

        elif mode == "Voice-Based":
            st.info("🔊 Playing question audio...")
            audio_path = question_to_speech(questions[index])
            st.audio(audio_path, format="audio/mp3")

            st.info("🎤 Record your answer")
            audio_bytes = audio_recorder()

            if audio_bytes:
                audio_file_path = f"tech_user_q{index+1}.wav"
                with open(audio_file_path, "wb") as f:
                    f.write(audio_bytes)

                st.audio(audio_bytes, format="audio/wav")
                st.success("🎧 Audio recorded. Transcribing...")

                try:
                    answer = speech_to_text(audio_file_path)
                    st.markdown(f"📝 **Transcribed Answer**: `{answer}`")

                    st.session_state.tech_answers.append({
                        "question": questions[index],
                        "answer": answer
                    })
                    st.session_state.tech_current += 1
                    st.experimental_rerun()

                except Exception as e:
                    st.error("❌ Transcription failed.")
                    st.exception(e)
    else:
        st.success("✅ Interview Completed!")
        st.markdown("👉 Please go to the **Feedback** tab to view your AI-generated feedback.")

        # Save for feedback page
        st.session_state['conversation_history'] = st.session_state.tech_answers

        if st.button("🔄 Restart Technical Interview"):
            for key in ["tech_started", "tech_questions", "tech_current", "tech_answers", "tech_job_description", "tech_mode"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()
