import streamlit as st
from typing import Dict, Any, Optional
from frontend.api_client import api_client


def render_sidebar(user: Optional[Dict[str, Any]] = None) -> str:
    """
    Renders modern sidebar navigation, user card, streak pill, and logout trigger.
    Returns the selected navigation page name:
    - Overview
    - Analyze Text
    - My Journal
    - Insights
    - My Profile
    """
    with st.sidebar:
        # App Branding Header
        st.markdown(
            """
            <div style="text-align: center; padding: 1.25rem 0 1rem 0; border-bottom: 1px solid rgba(139, 92, 246, 0.25); margin-bottom: 1.25rem;">
                <div style="font-size: 2.2rem; margin-bottom: 0.25rem;">🧠</div>
                <h2 style="margin: 0; font-size: 1.45rem; font-weight: 800; background: linear-gradient(135deg, #60a5fa 0%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    MoodMentor
                </h2>
                <div style="font-size: 0.78rem; color: #a5b4fc; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-top: 0.2rem;">
                    AI Emotion & Wellness Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Authenticated User Glass Card
        if user:
            full_name = user.get("full_name") or user.get("fullname") or user.get("username", "Member")
            email = user.get("email", "")
            goal = user.get("wellness_goal", "Mindfulness")
            theme = user.get("theme", "Blue-Purple Modern")

            st.markdown(
                f"""
                <div style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 0.95rem; padding: 0.9rem; margin-bottom: 1.25rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <div style="font-size: 1.9rem; background: rgba(99, 102, 241, 0.25); border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(168, 85, 247, 0.4);">
                            🧘
                        </div>
                        <div style="overflow: hidden;">
                            <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{full_name}</div>
                            <div style="font-size: 0.73rem; color: #94a3b8; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{email}</div>
                        </div>
                    </div>
                    <div style="margin-top: 0.6rem; display: flex; gap: 0.35rem; flex-wrap: wrap;">
                        <span style="font-size: 0.7rem; color: #c4b5fd; background: rgba(124, 58, 237, 0.25); padding: 0.18rem 0.5rem; border-radius: 0.35rem; border: 1px solid rgba(139, 92, 246, 0.3);">
                            🎯 {goal}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Navigation Options requested by user:
        # Overview, Analyze Text, My Journal, Insights, My Profile
        page_map = {
            "🏠 Overview": "Overview",
            "✨ Analyze Text": "Analyze Text",
            "📖 My Journal": "My Journal",
            "📊 Insights": "Insights",
            "👤 My Profile": "My Profile"
        }

        pages = list(page_map.keys())

        # Determine current selection
        current_selection = st.session_state.get("current_page", "Overview")
        default_index = 0
        for idx, (display_label, pure_name) in enumerate(page_map.items()):
            if current_selection == pure_name or current_selection == display_label:
                default_index = idx
                break

        selected_label = st.radio(
            "Navigation",
            options=pages,
            index=default_index,
            label_visibility="collapsed"
        )

        selected_page = page_map[selected_label]
        st.session_state["current_page"] = selected_page

        # Weekly Mindfulness Target Progress Bar
        st.markdown(
            """
            <div style="margin-top: 1.5rem; padding: 0.85rem; background: rgba(255,255,255,0.04); border-radius: 0.85rem; border: 1px solid rgba(255,255,255,0.08);">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.4rem;">
                    <span>🔥 Weekly Check-ins</span>
                    <span style="color: #a855f7;">5 / 7 Days</span>
                </div>
                <div class="custom-progress-container" style="background: rgba(255,255,255,0.1); height: 6px; margin: 0;">
                    <div class="custom-progress-fill" style="width: 71.4%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

        # Logout Trigger Button
        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            api_client.logout()
            st.session_state.clear()
            st.rerun()

        # Footer Meta
        st.markdown(
            """
            <div style="margin-top: 2rem; font-size: 0.7rem; color: #64748b; text-align: center; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 1rem;">
                Powered by <b>DistilBERT & MySQL</b><br>
                RESTful Blue-Purple Edition
            </div>
            """,
            unsafe_allow_html=True
        )

        return selected_page
