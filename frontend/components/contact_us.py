# frontend\components\contact_us.py
import streamlit as st
import webbrowser

def render_contact_us():
    st.markdown("---")
    st.markdown("### 📞 Contact Us")

    # Team Members
    st.markdown("👤 [Jayaprakash](https://www.linkedin.com/in/jayaprakash-shettigar-2b8bb6356?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)  ", unsafe_allow_html=True)
    st.markdown("👤 [Vanana](https://www.linkedin.com/in/vandana-r-poojary-bb586334a?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)  ", unsafe_allow_html=True)

    # # Button to open Share Experience form
    # if st.button("💬 Share Experience"):
    #     st.session_state.show_experience_form = True
