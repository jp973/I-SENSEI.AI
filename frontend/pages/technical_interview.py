# frontend\pages\technical_interview.py
import streamlit as st
from backend.utils.technical_utils import generate_question_pool, get_random_questions
from backend.utils.voice_utils import question_to_speech, speech_to_text
from audio_recorder_streamlit import audio_recorder

def render():
    st.header("💻 Technical Interview")

    # --- Initialize session state ---
    st.session_state.setdefault('tech_started', False)
    st.session_state.setdefault('tech_questions', [])
    st.session_state.setdefault('tech_current', 0)
    st.session_state.setdefault('tech_answers', [])
    st.session_state.setdefault('tech_job_description', "")
    st.session_state.setdefault('tech_mode', "Text-Based")
    st.session_state.setdefault('tech_question_count', 3)

    # --- Interview not started ---
    if not st.session_state.tech_started:
        st.subheader("📄 Enter Job Description")
        job_desc = st.text_area("Paste the job description here", height=200)

        st.subheader("🎯 Select Number of Questions")
        if st.session_state.tech_mode == "Voice-Based":
            st.info("Voice-Based mode allows only 1 question.")
            st.session_state.tech_question_count = 1
        else:
            st.session_state.tech_question_count = st.slider("How many questions do you want?", min_value=1, max_value=10, value=3)

        st.subheader("🎙️ Select Interview Mode")
        st.session_state.tech_mode = st.radio("Choose mode", ["Text-Based", "Voice-Based"], horizontal=True)

        if st.button("🚀 Start Interview"):
            if job_desc.strip():
                st.session_state.tech_job_description = job_desc
                pool = generate_question_pool(job_desc)

                count = 1 if st.session_state.tech_mode == "Voice-Based" else st.session_state.tech_question_count
                questions = get_random_questions(pool, count)

                st.session_state.tech_questions = questions
                st.session_state.tech_answers = []
                st.session_state.tech_current = 0
                st.session_state.tech_started = True
                st.rerun()
            else:
                st.warning("Please provide a job description.")
        return

    # --- Interview in progress ---
    questions = st.session_state.tech_questions
    index = st.session_state.tech_current
    mode = st.session_state.tech_mode

    if index < len(questions):
        st.subheader(f"🧑‍💻 Question {index + 1}")
        st.write(questions[index])

        if mode == "Text-Based":
            answer = st.text_area("Your Answer", key=f"text_answer_{index}")
            if st.button("Next"):
                if answer.strip():
                    st.session_state.tech_answers.append({
                        "question": questions[index],
                        "answer": answer.strip()
                    })
                    st.session_state.tech_current += 1
                    st.rerun()
                else:
                    st.warning("Please provide an answer before proceeding.")

        elif mode == "Voice-Based":
            if index > 0:
                st.success("✅ Voice-based interview supports only one question.")
                st.markdown("👉 Please go to the **Feedback** tab to view your AI-generated feedback.")
                return
        
            st.info("🔊 Playing question audio...")
            audio_path = question_to_speech(questions[index])
            st.audio(audio_path, format="audio/mp3")
        
            st.info("🎤 Record your answer")
            audio_bytes = audio_recorder(key=f"voice_q{index}")
        
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                st.success("🎧 Audio recorded. Click **Next** to proceed.")
        
                # 🔹 Only transcribe & proceed when user clicks Next
                if st.button("Next", key=f"next_btn_{index}"):
                    audio_file_path = f"tech_user_q{index+1}.wav"
                    with open(audio_file_path, "wb") as f:
                        f.write(audio_bytes)
        
                    try:
                        answer = speech_to_text(audio_file_path)
                        st.session_state.tech_answers.append({
                            "question": questions[index],
                            "answer": answer
                        })
                        st.session_state.tech_current += 1
                        st.rerun()
                    except Exception as e:
                        st.error("❌ Transcription failed.")
                        st.exception(e)
            else:
                st.warning("Please record your voice answer before clicking **Next**.")
        


    else:
        # --- Interview completed ---
        st.success("✅ Interview Completed!")
        st.markdown("👉 Please go to the **Feedback** tab to view your AI-generated feedback.")

        # Store answers for feedback page
        st.session_state['conversation_history'] = st.session_state.tech_answers

        if st.button("🔄 Restart Technical Interview"):
            for key in [
                "tech_started", "tech_questions", "tech_current",
                "tech_answers", "tech_job_description", "tech_mode", "tech_question_count"
            ]:
                st.session_state.pop(key, None)
            st.rerun()
