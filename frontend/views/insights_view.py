import streamlit as st
import pandas as pd
from frontend.api_client import api_client
from frontend.components.cards import render_header, render_metric_card, render_progress_card
from frontend.components.charts import (
    render_emotion_pie_chart,
    render_average_sentiment_gauge,
    render_sentiment_line_chart,
    render_monthly_report_chart,
    render_emotion_radar_chart,
    render_keywords_bar_chart
)
from frontend.config import EMOTION_ICONS, EMOTION_COLORS


def render_insights_view():
    """
    Renders Emotion Insights Dashboard.
    Features:
    - Charts:
        1. Emotion Distribution (Pie Chart)
        2. Average Sentiment
        3. Timeline
        4. Monthly Report
    - Metrics:
        - Most Frequent Emotion
        - Total Check-ins
        - Positive %
        - Negative %
    - Progress bars (Sentiment polarity balance & check-in milestone)
    - Plotly charts with blue-purple theme
    - Data fetched from Flask REST APIs
    """
    render_header(
        title="📊 Insights",
        subtitle="Visual analytics on emotional states, sentiment trajectories, and monthly wellness reports powered by Plotly & Flask APIs.",
        badge="📊 PLOTLY ANALYTICS ENGINE"
    )

    # 1. Fetch data from Flask API
    with st.spinner("Fetching emotion insights from Flask REST API..."):
        success, insights = api_client.get_emotion_insights()

    if not success or not insights or not insights.get("has_data"):
        st.info("No journal history found yet. Write a few reflections or analyze thoughts to unlock your Emotion Insights Dashboard!")
        btn_c1, btn_c2 = st.columns([1.2, 4])
        with btn_c1:
            if st.button("✨ Analyze Text Now", type="primary", use_container_width=True):
                st.session_state["current_page"] = "Analyze Text"
                st.rerun()
        return

    # Extract metrics from API response
    total_checkins = insights.get("total_checkins", insights.get("total_entries", 0))
    most_frequent_emotion = insights.get("most_frequent_emotion", "Neutral")
    most_frequent_count = insights.get("most_frequent_emotion_count", 0)
    avg_sentiment = insights.get("avg_sentiment", 0.0)
    sentiment_label = insights.get("sentiment_label", "Neutral")
    positive_pct = insights.get("positive_percentage", 0.0)
    negative_pct = insights.get("negative_percentage", 0.0)
    neutral_pct = insights.get("neutral_percentage", 0.0)

    emo_lower = most_frequent_emotion.lower()
    emo_icon = EMOTION_ICONS.get(emo_lower, "🌟")
    emo_color = EMOTION_COLORS.get(emo_lower, "#6366f1")

    # -------------------------------------------------------------------
    # 2. KEY PERFORMANCE INDICATORS (KPIs)
    # - Most Frequent Emotion
    # - Total Check-ins
    # - Positive %
    # - Negative %
    # -------------------------------------------------------------------
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    # 1. Most Frequent Emotion
    with kpi_col1:
        render_metric_card(
            title="Most Frequent Emotion",
            value=f"{emo_icon} {most_frequent_emotion}",
            subtext=f"{most_frequent_count} occurrences",
            icon="🌟",
            delta="Dominant",
            delta_type="pos"
        )

    # 2. Total Check-ins
    with kpi_col2:
        render_metric_card(
            title="Total Check-ins",
            value=str(total_checkins),
            subtext="Recorded in MySQL",
            icon="📝",
            delta="Stored",
            delta_type="pos"
        )

    # 3. Positive %
    with kpi_col3:
        render_metric_card(
            title="Positive %",
            value=f"{positive_pct}%",
            subtext="Uplifting reflections",
            icon="💚",
            delta="Positive",
            delta_type="pos"
        )

    # 4. Negative %
    with kpi_col4:
        render_metric_card(
            title="Negative %",
            value=f"{negative_pct}%",
            subtext="Challenging reflections",
            icon="❤️‍🩹",
            delta="Monitored",
            delta_type="neu"
        )

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------
    # PROGRESS BARS: Sentiment Polarity Breakdown
    # -------------------------------------------------------------------
    pr_col1, pr_col2 = st.columns(2)
    with pr_col1:
        render_progress_card(
            title="Positive Sentiment Proportion",
            current=positive_pct,
            total=100,
            unit="%",
            icon="📈",
            subtitle=f"{positive_pct}% of check-ins categorized as Positive"
        )

    with pr_col2:
        neutral_calc = round(max(0, 100 - positive_pct - negative_pct), 1)
        render_progress_card(
            title="Emotional Equilibrium",
            current=round(positive_pct + neutral_calc, 1),
            total=100,
            unit="%",
            icon="⚖️",
            subtitle=f"{positive_pct + neutral_calc}% Non-Negative Balance"
        )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------
    # 3. ROW 1 CHARTS:
    # - Emotion Distribution (Pie Chart)
    # - Average Sentiment (Gauge Chart)
    # -------------------------------------------------------------------
    st.markdown("### 🎭 Emotion & Sentiment Breakdown")
    row1_c1, row1_c2 = st.columns(2)

    with row1_c1:
        st.markdown(
            """
            <div style="background: white; border-radius: 1.15rem; padding: 1.35rem 1.5rem; border: 1px solid rgba(199, 210, 254, 0.65); box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.07);">
            """,
            unsafe_allow_html=True
        )
        # 1. EMOTION DISTRIBUTION PIE CHART
        render_emotion_pie_chart(insights.get("emotion_distribution", {}))
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_c2:
        st.markdown(
            """
            <div style="background: white; border-radius: 1.15rem; padding: 1.35rem 1.5rem; border: 1px solid rgba(199, 210, 254, 0.65); box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.07);">
            """,
            unsafe_allow_html=True
        )
        # 2. AVERAGE SENTIMENT GAUGE CHART
        render_average_sentiment_gauge(
            avg_sentiment=avg_sentiment,
            sentiment_label=sentiment_label,
            positive_pct=positive_pct,
            negative_pct=negative_pct
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------
    # 4. ROW 2 CHART:
    # - Timeline (Sentiment & Emotion Progression Over Time)
    # -------------------------------------------------------------------
    st.markdown("### 📈 Sentiment Progression Timeline")
    st.markdown(
        """
        <div style="background: white; border-radius: 1.15rem; padding: 1.35rem 1.5rem; border: 1px solid rgba(199, 210, 254, 0.65); box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.07);">
        """,
        unsafe_allow_html=True
    )
    # 3. TIMELINE CHART
    render_sentiment_line_chart(insights.get("sentiment_timeline", []))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------
    # 5. ROW 3 CHART:
    # - Monthly Report (Monthly Check-ins & Sentiment Breakdown)
    # -------------------------------------------------------------------
    st.markdown("### 📅 Monthly Emotion & Sentiment Report")
    st.markdown(
        """
        <div style="background: white; border-radius: 1.15rem; padding: 1.35rem 1.5rem; border: 1px solid rgba(199, 210, 254, 0.65); box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.07);">
        """,
        unsafe_allow_html=True
    )
    # 4. MONTHLY REPORT CHART
    monthly_report_data = insights.get("monthly_report", [])
    render_monthly_report_chart(monthly_report_data)
    st.markdown("</div>", unsafe_allow_html=True)

    # Monthly Summary Data Table
    if monthly_report_data:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        with st.expander("📋 Detailed Monthly Telemetry Table", expanded=False):
            table_rows = []
            for m in monthly_report_data:
                table_rows.append({
                    "Month": m.get("month_label", ""),
                    "Check-ins": m.get("total_entries", 0),
                    "Dominant Emotion": m.get("dominant_emotion", "Neutral"),
                    "Average Sentiment": f"{m.get('avg_sentiment', 0.0):+.2f}",
                    "Positive Check-ins": m.get("positive_entries", 0),
                    "Negative Check-ins": m.get("negative_entries", 0),
                    "Positive %": f"{m.get('positive_pct', 0.0)}%",
                    "Negative %": f"{m.get('negative_pct', 0.0)}%"
                })
            df_monthly = pd.DataFrame(table_rows)
            st.dataframe(df_monthly, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------
    # 6. ROW 4: DEEP PSYCHOLOGICAL INSIGHTS
    # - Radar Balance & Recurring Trigger Keywords
    # -------------------------------------------------------------------
    st.markdown("### 🔍 Advanced Affective Dimensions")
    row4_c1, row4_c2 = st.columns(2)

    with row4_c1:
        st.markdown(
            """
            <div style="background: white; border-radius: 1.15rem; padding: 1.35rem 1.5rem; border: 1px solid rgba(199, 210, 254, 0.65); box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.07);">
            """,
            unsafe_allow_html=True
        )
        render_emotion_radar_chart(insights.get("radar_data", {}))
        st.markdown("</div>", unsafe_allow_html=True)

    with row4_c2:
        st.markdown(
            """
            <div style="background: white; border-radius: 1.15rem; padding: 1.35rem 1.5rem; border: 1px solid rgba(199, 210, 254, 0.65); box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.07);">
            """,
            unsafe_allow_html=True
        )
        render_keywords_bar_chart(insights.get("top_keywords", []))
        st.markdown("</div>", unsafe_allow_html=True)
