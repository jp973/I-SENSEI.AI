# # frontend/pages/home.py
# import streamlit as st

# def render():
#     # st.set_page_config(layout="wide")
#     st.title("🧠 Welcome to I-Sensei.ai")
    
#     st.markdown(
#         "<h3 style='text-align: center;'>Your AI-powered Mock Interview Trainer</h3>",
#         unsafe_allow_html=True,
#     )

#     # Profile sidebar toggle
#     show_profile = st.sidebar.checkbox("👤 Show Profile")

#     if show_profile and "current_user" in st.session_state:
#         user = st.session_state.current_user
#         st.sidebar.markdown("### 👤 User Profile")
#         st.sidebar.write(f"**Username:** {user['username']}")
#         st.sidebar.write(f"**Email:** {user['email']}")
#         st.sidebar.write(f"**Mobile:** {user['mobile']}")
#     elif show_profile:
#         st.sidebar.warning("⚠️ User data not available.")

#     col1, col2, col3 = st.columns([0.5, 3, 0.5])
#     with col2:
#         st.image("frontend/assets/AI.webp", use_column_width=True)
# frontend/pages/home.py
import streamlit as st

def render():
    st.title("🧠 Welcome to I-Sensei.ai")

    st.markdown(
        "<h3 style='text-align: center;'>Your AI-powered Mock Interview Trainer</h3>",
        unsafe_allow_html=True,
    )

    # Profile toggle (main page, not sidebar)
    show_profile = st.checkbox("👤 Show Profile", key="toggle_profile", help="Click to show/hide your profile")

    # Create layout with 2 columns: Left (image), Right (optional profile)
    col1, col2 = st.columns([3, 1])

    with col2:
        if show_profile:
            if "current_user" in st.session_state:
                user = st.session_state.current_user
                st.markdown("### 👤 User Profile")
                st.info(f"""
                    **Username:** {user['username']}  
                    **Email:** {user['email']}  
                    **Mobile:** {user['mobile']}
                """)
            else:
                st.warning("⚠️ User data not available.")

    with col1:
        st.image("frontend/assets/AI.webp", use_container_width=True)

 
