import streamlit as st
from frontend.api_client import api_client
from frontend.components.cards import render_header


def render_register_view():
    """Renders user registration form view."""
    render_header(
        title="Join MoodMentor",
        subtitle="Embark on a mindful journey of emotional clarity and self-discovery"
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div style="background: white; border-radius: 1rem; padding: 2rem; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">
                <h3 style="margin-top: 0; color: #1e293b; font-weight: 700;">Create Your Account</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Private, encrypted emotional wellness tracking.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("register_form", clear_on_submit=False):
            full_name = st.text_input("Full Name", placeholder="e.g. Sravya Sharma")
            username = st.text_input("Username", placeholder="e.g. sravya_wellness")
            email = st.text_input("Email Address", placeholder="e.g. sravya@example.com")
            password = st.text_input("Password", type="password", placeholder="At least 6 characters")
            confirm_pwd = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")

            submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submit:
                if not full_name or not email or not password:
                    st.error("Please fill in all required fields (Full Name, Email, Password).")
                elif password != confirm_pwd:
                    st.error("Passwords do not match. Please re-enter carefully.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating your account..."):
                        success, msg, data = api_client.register(
                            fullname=full_name,
                            email=email,
                            password=password,
                            username=username or email.split("@")[0]
                        )
                        if success and data:
                            st.session_state["token"] = data["access_token"]
                            st.session_state["user"] = data["user"]
                            st.session_state["current_page"] = "Overview"
                            st.success("Account created successfully! Welcome aboard.")
                            st.rerun()
                        else:
                            st.error(msg)

        st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
        if st.button("Already have an account? Sign In", use_container_width=True, type="secondary"):
            st.session_state["auth_mode"] = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
