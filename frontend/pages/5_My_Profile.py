import os
import sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.views.profile_view import render_profile_view
from frontend.components.sidebar import render_sidebar

st.set_page_config(page_title="My Profile - MoodMentor", page_icon="👤", layout="wide")

css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

user = st.session_state.get("user")
render_sidebar(user)
render_profile_view()
