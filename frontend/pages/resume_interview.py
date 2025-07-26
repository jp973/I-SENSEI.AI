import streamlit as st
from backend.utils.resume_parser import extract_resume_text
import google.generativeai as genai
from dotenv import load_dotenv
import os
from audio_recorder_streamlit import audio_recorder
from backend.utils.voice_utils import question_to_speech, speech_to_text
           

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------------
# Generate question using Gemini
# -------------------------------
def generate_resume_question(resume_text, prev_qas=[]):
    conversation = "\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in prev_qas])
    prompt = f"""
You are an AI interviewer. Ask a professional, relevant question based on the candidate's resume and past answers.only ask one question at a time.

Resume:
{resume_text}

Conversation so far:
{conversation}

Next Question:
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# -------------------------------
# UI Renderer
# -------------------------------
def render():
    st.header("📄 Resume-Based Interview")

    # 1. Initialize session variables
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    
        # If interview is completed and user revisits this page
    if st.session_state.get('question_count', 0) >= 3:
        st.success("✅ You've completed this interview session.")
        st.markdown("👉 Please go to the **Feedback** page to view your results.")

        if st.button("🔄 Restart Interview"):
            st.session_state.conversation_history = []
            st.session_state.current_question = None
            st.session_state.question_count = 0
            st.session_state.interview_started = False
            st.experimental_rerun()
        return  # Exit early until interview is restarted


    # 2. Upload Resume
    uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type="pdf")

    if uploaded_file:
        text = extract_resume_text(uploaded_file)
        st.success("✅ Resume uploaded successfully.")
        st.session_state.resume_text = text

        # 3. Choose Interview Mode (Only Text works for now)
        st.subheader("Select Interview Mode")
        mode = st.radio("Choose mode", ["Text-Based", "Voice-Based"], horizontal=True)

        # 4. Start Interview
        if not st.session_state.interview_started:
            if st.button("🎤 Start Interview"):
                st.session_state.interview_started = True
                st.session_state.current_question = generate_resume_question(
                    st.session_state.resume_text,
                    st.session_state.conversation_history
                )
                st.experimental_rerun()

        elif st.session_state.question_count < 3:
            # Display current question
            st.markdown(f"**🧑‍💼 Question {st.session_state.question_count + 1}:**")
            st.markdown(st.session_state.current_question)

            if mode == "Text-Based":
                user_answer = st.text_area("✍️ Your Answer", key=f"answer_{st.session_state.question_count}")
                if st.button("Submit Answer"):
                    if user_answer.strip() != "":
                        # Save the Q&A
                        st.session_state.conversation_history.append({
                            "question": st.session_state.current_question,
                            "answer": user_answer.strip()
                        })
                        st.session_state.question_count += 1

                        # Prepare next question or end
                        if st.session_state.question_count < 3:
                            st.session_state.current_question = generate_resume_question(
                                st.session_state.resume_text,
                                st.session_state.conversation_history
                            )
                        else:
                            st.session_state.current_question = None
                        st.experimental_rerun()
                    else:
                        st.warning("⚠️ Please enter your answer before submitting.")

            # elif mode == "Voice-Based":
                

            #     # 🔊 1. Convert current question to voice
            #     st.info("🔊 Playing interview question...")
            #     audio_path = question_to_speech(st.session_state.current_question)
            #     st.audio(audio_path, format="audio/mp3")

            #     # 🎙️ 2. Record user response
            #     st.info("🎤 Record your answer")
            #     audio_bytes = audio_recorder()

            #     if audio_bytes:
            #         # Save user audio
            #         audio_file_path = os.path.join("user_audio.wav")
            #         with open(audio_file_path, "wb") as f:
            #             f.write(audio_bytes)

            #         st.audio(audio_bytes, format="audio/wav")
            #         st.success("🎧 Audio recorded. Transcribing...")

            #         # 🔤 3. Transcribe to text
            #         try:
            #             user_answer = speech_to_text(audio_file_path)
            #             st.write(f"📝 Transcribed Answer: `{user_answer}`")

            #             # Save Q&A
            #             st.session_state.conversation_history.append({
            #                 "question": st.session_state.current_question,
            #                 "answer": user_answer
            #             })
            #             st.session_state.question_count += 1

            #             # Next question or finish
            #             if st.session_state.question_count < 3:
            #                 st.session_state.current_question = generate_resume_question(
            #                     st.session_state.resume_text,
            #                     st.session_state.conversation_history
            #                 )
            #             else:
            #                 st.session_state.current_question = None
            #             st.experimental_rerun()

            #         except Exception as e:
            #             st.error("❌ Failed to transcribe audio.")
            #             st.exception(e)
            elif mode == "Voice-Based":
                st.info("🔊 Playing interview question...")
                audio_path = question_to_speech(st.session_state.current_question)
                st.audio(audio_path, format="audio/mp3")
            
                st.info("🎤 Record your answer")
                audio_bytes = audio_recorder(key=f"resume_voice_q{st.session_state.question_count}")
            
                if audio_bytes and len(audio_bytes) > 1000:
                    import tempfile
                    audio_file_path = os.path.join(tempfile.gettempdir(), f"resume_user_q{st.session_state.question_count+1}.wav")
                    with open(audio_file_path, "wb") as f:
                        f.write(audio_bytes)
            
                    st.audio(audio_bytes, format="audio/wav")
                    st.success("🎧 Audio recorded. Transcribing...")
            
                    try:
                        user_answer = speech_to_text(audio_file_path)
                        st.write(f"📝 **Transcribed Answer:** `{user_answer}`")
            
                        # Save Q&A to history
                        st.session_state.conversation_history.append({
                            "question": st.session_state.current_question,
                            "answer": user_answer
                        })
            
                        # Update question count
                        st.session_state.question_count += 1
            
                        # If less than 3, generate next question
                        if st.session_state.question_count < 3:
                            st.session_state.current_question = generate_resume_question(
                                st.session_state.resume_text,
                                st.session_state.conversation_history
                            )
                        else:
                            st.session_state.current_question = None  # End of interview
            
                        st.experimental_rerun()
            
                    except Exception as e:
                        st.error("❌ Transcription failed.")
                        st.exception(e)
            
                else:
                    st.warning("⚠️ Please record a longer answer before clicking Next.")
            
            
        else:
            # After 3 questions
            st.success("✅ Interview Completed!")
            st.markdown("🎉 You've answered all 3 questions.")
            st.markdown("👉 Please go to the **Feedback** page to get your performance summary and rating.")
            if st.button("🔄 Restart Interview"):
                st.session_state.conversation_history = []
                st.session_state.current_question = None
                st.session_state.question_count = 0
                st.session_state.interview_started = False
                st.experimental_rerun()


