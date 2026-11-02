import streamlit as st
from datetime import datetime
from frontend.api_client import api_client
from frontend.components.cards import (
    render_header,
    render_metric_card,
    render_progress_card,
    get_emotion_badge_html,
    get_sentiment_badge_html,
    render_ai_suggestion,
    render_timeline_entry_card
)
from frontend.components.charts import render_emotion_pie_chart
from frontend.config import EMOTION_ICONS


def render_dashboard_view():
    """
    Renders Overview Page.
    Features:
    - Cards (Glassmorphic Metric Cards, Action Cards, Reflection Cards)
    - Metrics (Total Entries, Current Streak, Dominant Emotion, Average Sentiment)
    - Progress Bars (Weekly Mindfulness Target & Sentiment Polarity Progress)
    - Pie Charts (Plotly Emotion Distribution)
    - Timeline (Chronological Activity & Emotional Trajectory)
    - Icons, Responsive Layout, Professional Blue-Purple Theme.
    """
    user = st.session_state.get("user") or {}
    if not st.session_state.get("token") or not user:
        st.info("🔒 **Welcome to MoodMentor!** Please log in or create an account below to view your personalized dashboard, daily streaks, and emotional telemetry.")
        from frontend.views.login_view import render_login_view
        render_login_view()
        return

    full_name = user.get("full_name") or user.get("fullname") or user.get("username", "Member")

    # Dynamic time-of-day greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    render_header(
        title=f"{greeting}, {full_name} ✨",
        subtitle="Here is your real-time emotional well-being telemetry, daily streak, and AI mindfulness pulse.",
        badge="🌟 OVERVIEW & EMOTION PULSE"
    )

    # 1. Fetch live metrics and insights from backend
    with st.spinner("Connecting to telemetry services..."):
        success, stats = api_client.get_dashboard_stats()
        _, insights = api_client.get_emotion_insights()

    if not success or not stats:
        st.warning("⚠️ Connecting to backend services... Please verify server connectivity.")
        return

    # -----------------------------------------------------------------------
    # 2. METRIC CARDS ROW (Responsive 4-column layout)
    # -----------------------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_entries = stats.get("total_entries", 0)
        render_metric_card(
            title="Total Entries",
            value=str(total_entries),
            subtext="Lifetime reflections",
            icon="📖",
            delta="+1 today" if total_entries > 0 else "0",
            delta_type="pos"
        )

    with col2:
        streak = stats.get("current_streak", 0)
        streak_sub = "Active daily streak!" if streak > 0 else "Start a new streak today"
        render_metric_card(
            title="Mindfulness Streak",
            value=f"{streak} Days",
            subtext=streak_sub,
            icon="🔥",
            delta="Keep it up" if streak > 0 else "Day 1",
            delta_type="pos" if streak > 0 else "neu"
        )

    with col3:
        dom_emo = stats.get("dominant_emotion", "neutral")
        emo_icon = EMOTION_ICONS.get(dom_emo.lower(), "🌱")
        render_metric_card(
            title="Dominant Emotion",
            value=f"{emo_icon} {dom_emo.capitalize()}",
            subtext="Primary affective state",
            icon="🎭",
            delta="Verified",
            delta_type="pos"
        )

    with col4:
        avg_sent = stats.get("avg_sentiment", 0.0)
        sent_label = stats.get("sentiment_label", "Neutral")
        render_metric_card(
            title="Average Sentiment",
            value=f"{avg_sent:+.2f}",
            subtext=f"{sent_label} Polarity",
            icon="📊",
            delta=sent_label,
            delta_type="pos" if avg_sent >= 0.05 else ("neu" if avg_sent > -0.05 else "neu")
        )

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # 3. PROGRESS BARS ROW
    # -----------------------------------------------------------------------
    p_col1, p_col2 = st.columns(2)

    with p_col1:
        # Weekly Target Progress Bar (5 of 7 days)
        render_progress_card(
            title="Weekly Mindfulness Target",
            current=min(7, max(1, streak % 8 if streak > 0 else 1)),
            total=7,
            unit="days",
            icon="🎯",
            subtitle="Consistency milestone toward emotional balance"
        )

    with p_col2:
        # Positive Sentiment Ratio Progress Bar
        pos_entries = stats.get("positive_entries", 0)
        total_valid = max(1, stats.get("total_entries", 1))
        pos_ratio = round((pos_entries / total_valid) * 100, 1)
        render_progress_card(
            title="Positive Wellness Ratio",
            current=pos_ratio,
            total=100,
            unit="%",
            icon="✨",
            subtitle=f"{pos_entries} of {total_valid} reflections marked positive"
        )

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # 4. TWO-COLUMN RESPONSIVE SECTION: Pie Chart & Quick Action Hub
    # -----------------------------------------------------------------------
    ch_col, act_col = st.columns([1.35, 1], gap="medium")

    with ch_col:
        st.markdown(
            """
            <div style="background: white; border-radius: 1.15rem; padding: 1.25rem 1.5rem; border: 1px solid rgba(199, 210, 254, 0.65); box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.07);">
                <div style="font-weight: 700; color: #1e293b; font-size: 1.1rem; margin-bottom: 0.25rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🥧</span> Emotion Breakdown (Pie Chart)
                </div>
                <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 0.75rem;">
                    Cumulative distribution across all your journal records.
                </div>
            """,
            unsafe_allow_html=True
        )

        # Plotly Emotion Pie Chart
        dist_data = (insights or {}).get("emotion_distribution") or {dom_emo: max(1, total_entries)}
        render_emotion_pie_chart(dist_data)
        st.markdown("</div>", unsafe_allow_html=True)

    with act_col:
        # Daily Thought Quote Card
        quote_data = stats.get("daily_quote", {})
        q_text = quote_data.get("quote", "Feelings are just visitors, let them come and go.")
        q_author = quote_data.get("author", "Mindfulness Mentor")

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%); border-left: 5px solid #6366f1; border-radius: 1.15rem; padding: 1.4rem 1.6rem; margin-bottom: 1.25rem; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08);">
                <div style="font-size: 0.75rem; font-weight: 800; color: #4f46e5; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem;">
                    💡 DAILY THOUGHT OF REFLECTION
                </div>
                <div style="font-size: 1.05rem; font-style: italic; color: #1e1b4b; line-height: 1.55;">
                    "{q_text}"
                </div>
                <div style="font-size: 0.85rem; color: #6d28d9; margin-top: 0.6rem; text-align: right; font-weight: 700;">
                    — {q_author}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Quick Navigation & Interaction Card
        st.markdown(
            """
            <div style="background: white; border: 1px solid rgba(199, 210, 254, 0.65); border-radius: 1.15rem; padding: 1.35rem 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <div style="font-size: 0.85rem; font-weight: 800; color: #1e293b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.75rem;">
                    ⚡ Action Hub
                </div>
            """,
            unsafe_allow_html=True
        )

        b1, b2 = st.columns(2)
        with b1:
            if st.button("✨ Analyze Text", use_container_width=True, type="primary"):
                st.session_state["current_page"] = "Analyze Text"
                st.rerun()
        with b2:
            if st.button("📖 My Journal", use_container_width=True):
                st.session_state["current_page"] = "My Journal"
                st.rerun()

        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        if st.button("📊 View Deep Insights", use_container_width=True):
            st.session_state["current_page"] = "Insights"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # 5. RECENT REFLECTION TIMELINE
    # -----------------------------------------------------------------------
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
            <div style="font-size: 1.35rem; font-weight: 800; color: #1e293b; display: flex; align-items: center; gap: 0.5rem;">
                <span>⏳</span> Recent Reflection Timeline
            </div>
            <span style="font-size: 0.82rem; color: #6366f1; font-weight: 700; background: #e0e7ff; padding: 0.25rem 0.75rem; border-radius: 9999px;">
                Chronological Feed
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    recent_entries = stats.get("recent_entries", [])
    if not recent_entries:
        st.info("No journal reflections recorded yet. Click 'Analyze Text' above to capture your first reflection!")
    else:
        st.markdown('<div class="timeline-stream">', unsafe_allow_html=True)
        for entry in recent_entries:
            elog = entry.get("analysis") or {}
            entry_title = entry.get("title", "Reflection")
            entry_date = entry.get("entry_date", datetime.today().strftime("%Y-%m-%d"))
            content = entry.get("content", "")
            snippet = (content[:220] + "...") if len(content) > 220 else content

            primary_emo = elog.get("primary_emotion", "Neutral")
            sent_obj = elog.get("sentiment") or {}
            sent_label = sent_obj.get("label", "Neutral")
            compound = sent_obj.get("compound", 0.0)

            render_timeline_entry_card(
                date_str=entry_date,
                title=entry_title,
                content=snippet,
                emotion=primary_emo,
                sentiment=sent_label,
                compound=compound
            )

        st.markdown('</div>', unsafe_allow_html=True)
