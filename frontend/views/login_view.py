import streamlit as st
from frontend.api_client import api_client
from frontend.components.cards import render_header


def render_login_view():
    """Renders user authentication login view."""
    render_header(
        title="Welcome to MoodMentor",
        subtitle="Your AI-Powered Emotional Companion & Reflective Journal"
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div style="background: white; border-radius: 1rem; padding: 2rem; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">
                <h3 style="margin-top: 0; color: #1e293b; font-weight: 700;">Sign In to Your Account</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Track your emotional well-being with precision AI guidance.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form", clear_on_submit=False):
            identifier = st.text_input("Username or Email", placeholder="e.g. sravya or sravya@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submit:
                if not identifier or not password:
                    st.error("Please enter both username/email and password.")
                else:
                    with st.spinner("Authenticating..."):
                        success, msg, data = api_client.login(identifier, password)
                        if success and data:
                            st.session_state["token"] = data["access_token"]
                            st.session_state["user"] = data["user"]
                            st.session_state["current_page"] = "Overview"
                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error(msg)

        st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
        if st.button("New to MoodMentor? Create an Account", use_container_width=True, type="secondary"):
            st.session_state["auth_mode"] = "register"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
