import os
import sys
import streamlit as st

# Ensure project root is available in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.api_client import api_client
from frontend.components.sidebar import render_sidebar
from frontend.views import (
    render_login_view,
    render_register_view,
    render_dashboard_view,
    render_analyze_view,
    render_journal_view,
    render_insights_view,
    render_profile_view,
    render_export_view
)

# -------------------------------------------------------------------
# Streamlit Application Configuration
# -------------------------------------------------------------------
st.set_page_config(
    page_title="MoodMentor - AI Emotion Journal",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and inject custom CSS styling
def load_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()


def main():
    """Main routing and session controller."""
    # Initialize session state variables
    if "token" not in st.session_state:
        st.session_state["token"] = None
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Overview"

    # Verify session if token exists
    if st.session_state["token"] and not st.session_state["user"]:
        is_valid, user_data = api_client.get_me()
        if is_valid and user_data:
            st.session_state["user"] = user_data
        else:
            # Token expired or invalid
            st.session_state["token"] = None
            st.session_state["user"] = None

    # Routing: Unauthenticated Users
    if not st.session_state["token"]:
        if st.session_state["auth_mode"] == "register":
            render_register_view()
        else:
            render_login_view()
        return

    # Routing: Authenticated Users
    user = st.session_state.get("user")
    selected_page = render_sidebar(user)

    if selected_page in ["Overview", "🏠 Overview", "🏠 Dashboard"]:
        render_dashboard_view()
    elif selected_page in ["Analyze Text", "✨ Analyze Text", "⚡ Analyze Emotion"]:
        render_analyze_view()
    elif selected_page in ["My Journal", "📖 My Journal", "📖 Journal"]:
        render_journal_view()
    elif selected_page in ["Insights", "📊 Insights", "📊 Emotion Insights"]:
        render_insights_view()
    elif selected_page in ["My Profile", "👤 My Profile", "👤 User Profile"]:
        render_profile_view()
    elif selected_page in ["Export", "📥 Export Journal (CSV)"]:
        render_export_view()
    else:
        render_dashboard_view()


if __name__ == "__main__":
    main()
