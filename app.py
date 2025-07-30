# app.py
from datetime import datetime, timedelta
import streamlit as st
from frontend.components.share_experience import  render
from frontend.pages import resume_interview, feedback
from frontend.components.contact_us import render_contact_us
from backend.utils.mongo_utils import get_users_collection
from dotenv import load_dotenv
import bcrypt
load_dotenv()


def register(username, password, mobile, email):
    users = get_users_collection()
    if users.find_one({"username": username}):
        return False  # Username already exists
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
  
    users.insert_one({
        "username": username,
        "password": hashed_password,   
        "mobile": mobile,
        "email": email
    })
    return True

# Authenticate user
def authenticate(username, password):
    users = get_users_collection()
    user = users.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        st.session_state.current_user = {
            "username": user["username"],
            "email": user["email"],
            "mobile": user["mobile"]
        }
        return True
    return False


# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "just_registered" not in st.session_state:
    st.session_state.just_registered = False
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0
if "blocked_until" not in st.session_state:
    st.session_state.blocked_until = None


# Login page before main app
if not st.session_state.logged_in:
    st.title("🔐 Login to I-Sensei.ai")

    tab_names = ["Login", "Register"]

    # Track tab manually
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "Login"

    # Force switch to Login after registration
    if st.session_state.just_registered:
        st.session_state.selected_tab = "Login"

    # Tab Buttons (replace st.tabs)
    tab_choice = st.radio("Choose Action", tab_names, index=0 if st.session_state.selected_tab == "Login" else 1,horizontal=True)
    st.session_state.selected_tab = tab_choice
    selected_tab = st.session_state.selected_tab

    if selected_tab == "Login":
        st.subheader("Login")
        if st.session_state.just_registered:
            st.success("Registered successfully! Please login.")
            st.session_state.just_registered = False

        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            # Check if blocked
            if st.session_state.blocked_until and datetime.now() < st.session_state.blocked_until:
                remaining = (st.session_state.blocked_until - datetime.now()).seconds
                st.error(f"🚫 Too many failed attempts. Try again in {remaining} seconds.")
                st.stop()

            # ✅ Reset if block expired
            if st.session_state.blocked_until and datetime.now() >= st.session_state.blocked_until:
                st.session_state.login_attempts = 0
                st.session_state.blocked_until = None
            # Check for empty fields
            if not username:
                st.warning("⚠️ Username cannot be empty.")
            elif not password:
                st.warning("⚠️ Password cannot be empty.")
            # Password length check
            elif len(password) < 6:
                st.warning("⚠️ Password must be at least 6 characters.")
            else:
                # Call your login/authentication logic
                if authenticate(username, password):
                    st.success("✅ Logged in successfully!")
                    st.session_state.logged_in = True
                    st.session_state.login_attempts = 0  # Reset on success
                    st.session_state.blocked_until = None
                    st.experimental_rerun()
                else:
                    st.session_state.login_attempts += 1
                    st.error("❌ Invalid username or password.")

                    # Block after 5 attempts
                    if st.session_state.login_attempts >= 5:
                        st.session_state.blocked_until = datetime.now() + timedelta(minutes=5)
                        st.error("🚫 Too many failed attempts. You are blocked for 5 minutes.")

    elif selected_tab == "Register":
        st.subheader("Register")
        new_user = st.text_input("New Username").strip()
        new_pass = st.text_input("New Password", type="password")
        new_mobile = st.text_input("Mobile Number").strip()
        new_email = st.text_input("Email Address").strip()
    
        if st.button("Register"):
            # Validation checks
            if not new_user:
                st.warning("⚠️ Username is required.")
            elif not new_pass:
                st.warning("⚠️ Password is required.")
            elif len(new_pass) < 6:
                st.warning("⚠️ Password must be at least 6 characters.")
            elif not new_mobile or not new_mobile.isdigit() or len(new_mobile) != 10:
                st.warning("⚠️ Enter a valid 10-digit mobile number.")
            elif not new_email or "@" not in new_email or "." not in new_email:
                st.warning("⚠️ Enter a valid email address.")
            else:
                # Call registration function
                if register(new_user, new_pass, new_mobile, new_email):
                    st.session_state.just_registered = True
                    st.experimental_rerun()
                else:
                    st.warning("❌ Username already exists.")
    
    


else:
         
    from streamlit_option_menu import option_menu

    st.set_page_config(page_title="I-Sensei.ai", layout="centered")

    with st.sidebar:
        selected = option_menu(
            "I-Sensei.ai",
            ["Home", "Technical Interview", "Resume Interview", "Behavioral Interview", "Feedback","Share Experience"],
            icons=["house", "cpu", "file-earmark-person", "chat-dots", "bar-chart","chat-left-text"],
            menu_icon="robot",
            default_index=0,
        )
        render_contact_us()
        st.session_state.selected_tab = selected
        # 🔘 Log out button
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.success("Logged out successfully.")
            st.experimental_rerun()
   
   
    if selected == "Home":
        from frontend.pages import home
        home.render()

    elif selected == "Technical Interview":
        from frontend.pages import technical_interview
        technical_interview.render()

    elif selected == "Resume Interview":
        from frontend.pages import resume_interview
        resume_interview.render()

    elif selected == "Behavioral Interview":
        from frontend.pages import behavioral_interview
        behavioral_interview.render()

    elif selected == "Feedback":
        from frontend.pages import feedback
        feedback.render()
       
    elif selected == "Share Experience":
        render()


    