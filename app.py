
from datetime import datetime, timedelta
import bcrypt
import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh

# Local imports (moved to top to avoid repeated imports on rerun)
from frontend.components.share_experience import render as render_experience
from frontend.pages import home, technical_interview, resume_interview, behavioral_interview, feedback
from frontend.components.contact_us import render_contact_us
from backend.utils.mongo_utils import get_users_collection

# ---------- App Config ----------
st.set_page_config(page_title="I-Sensei.ai", layout="centered")
load_dotenv()


def rerun():
    """Safe rerun for Streamlit versions with/without st.rerun."""
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()


@st.cache_resource
def get_users_collection_cached():
    """Cache the DB collection handle to avoid reconnect on every rerun."""
    return get_users_collection()


def register(username: str, password: str, mobile: str, email: str) -> bool:
    users = get_users_collection_cached()
    if users.find_one({"username": username}):
        return False  # Username already exists

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users.insert_one(
        {
            "username": username,
            "password": hashed_password,
            "mobile": mobile,
            "email": email,
        }
    )
    return True


def authenticate(username: str, password: str) -> bool:
    users = get_users_collection_cached()
    user = users.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        st.session_state.current_user = {
            "username": user.get("username"),
            "email": user.get("email"),
            "mobile": user.get("mobile"),
        }
        return True
    return False

def init_session_defaults():
    defaults = {
        "logged_in": False,
        "just_registered": False,
        "login_attempts": 0,
        "blocked_until": None,
        "selected_tab": "Login",  
        "menu_selected": "Home",  
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def show_login_register():
    st.title("🔐 Login to I-Sensei.ai")

    if st.session_state.just_registered:
        st.session_state.selected_tab = "Login"

    tab_names = ["Login", "Register"]
    idx = 0 if st.session_state.selected_tab == "Login" else 1
    tab_choice = st.radio("Choose Action", tab_names, index=idx, horizontal=True)
    st.session_state.selected_tab = tab_choice

    if tab_choice == "Login":
        st.subheader("Login")
        if st.session_state.just_registered:
            st.success("Registered successfully! Please login.")
            st.session_state.just_registered = False

        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password")

        if st.session_state.blocked_until and datetime.now() < st.session_state.blocked_until:
            remaining = (st.session_state.blocked_until - datetime.now()).seconds
            st.error(f"🚫 Too many failed attempts. Try again in {remaining} seconds.")
            st_autorefresh(interval=1000, key="blocked_refresh")  # refresh every second
            return

        if st.button("Login"):
            # If blocked, show remaining time
            
            # If previous block expired, reset counters
            if st.session_state.blocked_until and datetime.now() >= st.session_state.blocked_until:
                st.session_state.login_attempts = 0
                st.session_state.blocked_until = None

              
            if not username:
                st.warning("⚠️ Username cannot be empty.")
            elif not password:
                st.warning("⚠️ Password cannot be empty.")
            elif len(password) < 6:
                st.warning("⚠️ Password must be at least 6 characters.")
            else:
                if authenticate(username, password):
                    st.success("✅ Logged in successfully!")
                    st.session_state.logged_in = True
                    st.session_state.login_attempts = 0
                    st.session_state.blocked_until = None
                    rerun()  # switch view to main app
                else:
                    st.session_state.login_attempts += 1
                    st.error("❌ Invalid username or password.")

                    if st.session_state.login_attempts >= 5:
                        st.session_state.blocked_until = datetime.now() + timedelta(minutes=1)
                        st.error("🚫 Too many failed attempts. You are blocked for 1 minutes.")

    else:   
        st.subheader("Register")
        new_user = st.text_input("New Username").strip()
        new_pass = st.text_input("New Password", type="password")
        new_mobile = st.text_input("Mobile Number").strip()
        new_email = st.text_input("Email Address").strip()

        if st.button("Register"):
             
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
                if register(new_user, new_pass, new_mobile, new_email):
                    st.session_state.just_registered = True
                    rerun()  
                else:
                    st.warning("❌ Username already exists.")


def show_main_app():
    with st.sidebar:
        selected = option_menu(
            "I-Sensei.ai",
            ["Home", "Technical Interview", "Resume Interview", "Behavioral Interview", "Feedback", "Share Experience"],
            icons=["house", "cpu", "file-earmark-person", "chat-dots", "bar-chart", "chat-left-text"],
            menu_icon="robot",
            default_index=0,
        )
        st.session_state.menu_selected = selected

        render_contact_us()

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.success("Logged out successfully.")
            rerun() 

    if st.session_state.menu_selected == "Home":
        home.render()
    elif st.session_state.menu_selected == "Technical Interview":
        technical_interview.render()
    elif st.session_state.menu_selected == "Resume Interview":
        resume_interview.render()
    elif st.session_state.menu_selected == "Behavioral Interview":
        behavioral_interview.render()
    elif st.session_state.menu_selected == "Feedback":
        feedback.render()
    elif st.session_state.menu_selected == "Share Experience":
        render_experience()


def main():
    init_session_defaults()
    if not st.session_state.logged_in:
        show_login_register()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
