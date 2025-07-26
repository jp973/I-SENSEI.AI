# frontend/pages/home.py

import streamlit as st

def render():
    st.title("🧠 Welcome to I-Sensei.ai")
    
    st.markdown(
        "<h3 style='text-align: center;'>Your AI-powered Mock Interview Trainer</h3>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        st.image("frontend/assets/AI.webp", use_column_width=True)
