# frontend/pages/share_experience.py
import streamlit as st
from backend.utils.experience_utils import save_experience_to_db

def render():
    st.title("💬 Share Your Experience with I-Sensei.ai")
    st.markdown(
        "<h4 style='text-align: center;'> Tell us how we can improve. We value your feedback! 😊</h4>",
        unsafe_allow_html=True,
    )

    # --- Show success message if previous submission succeeded ---
    if st.session_state.get("experience_success", False):
        st.success("✅ Thank you for sharing your experience!")
        # reset form fields after showing success
        st.session_state["experience_name"] = ""
        st.session_state["experience_mobile"] = ""
        st.session_state["experience_text"] = ""
        st.session_state["experience_success"] = False  # reset flag

    # Set default values for fields if not already set
    st.session_state.setdefault("experience_name", "")
    st.session_state.setdefault("experience_mobile", "")
    st.session_state.setdefault("experience_text", "")

    # Form inputs
    name = st.text_input("Your Name", key="experience_name").strip()
    mobile = st.text_input("Mobile Number", key="experience_mobile").strip()
    experience = st.text_area("Share Your Experience", key="experience_text").strip()

    if st.button("Send"):
        # Validation logic
        if not name:
            st.warning("⚠️ Please enter your name.")
        elif not mobile:
            st.warning("⚠️ Please enter your mobile number.")
        elif not mobile.isdigit() or len(mobile) != 10:
            st.warning("⚠️ Mobile number must be 10 digits.")
        elif not experience:
            st.warning("⚠️ Please share your experience.")
        else:
            save_experience_to_db(name, mobile, experience)
            st.session_state["experience_success"] = True  # set flag
            st.rerun()
