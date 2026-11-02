import streamlit as st
from typing import Dict, Any, List, Optional
from frontend.config import EMOTION_COLORS, EMOTION_ICONS


def render_header(title: str, subtitle: str = "", badge: str = "🧠 MOODMENTOR INTELLIGENCE"):
    """Renders modern gradient hero header banner with glassmorphic badge."""
    st.markdown(
        f"""
        <div class="mood-header">
            {f'<div class="mood-header-badge">{badge}</div>' if badge else ''}
            <h1>{title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(
    title: str,
    value: str,
    subtext: str = "",
    icon: str = "✨",
    delta: str = "",
    delta_type: str = "pos"
):
    """
    Renders a responsive modern glassmorphism metric card with icon badge and delta indicator.
    """
    delta_class = "metric-delta-pos" if delta_type == "pos" else "metric-delta-neu"
    delta_html = f'<span class="{delta_class}">{delta}</span>' if delta else ""

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-header">
                <span class="metric-title">{title}</span>
                <div class="metric-icon-wrap">{icon}</div>
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">
                {delta_html}
                <span>{subtext}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_progress_card(
    title: str,
    current: float,
    total: float,
    unit: str = "days",
    icon: str = "🎯",
    subtitle: str = ""
):
    """
    Renders a modern progress card with percentage milestone and vibrant gradient bar.
    """
    pct = min(100, max(0, round((current / total) * 100, 1) if total > 0 else 0))
    st.markdown(
        f"""
        <div class="metric-card" style="margin-bottom: 1rem;">
            <div class="metric-header">
                <span class="metric-title">{icon} {title}</span>
                <span style="font-size: 0.85rem; font-weight: 700; color: #4338ca;">{current} / {total} {unit}</span>
            </div>
            <div class="progress-label-row">
                <span>{subtitle or "Progress to Target"}</span>
                <span style="font-weight: 800; color: #7c3aed;">{pct}%</span>
            </div>
            <div class="custom-progress-container">
                <div class="custom-progress-fill" style="width: {pct}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_emotion_badge_html(emotion: str, confidence: Optional[float] = None) -> str:
    """Generates HTML string for an emotion badge with icon and score."""
    emo_lower = str(emotion).lower() if emotion else "neutral"
    icon = EMOTION_ICONS.get(emo_lower, "🌱")
    score_str = f" ({int(confidence * 100)}%)" if confidence is not None else ""
    badge_class = f"badge-{emo_lower}" if emo_lower in EMOTION_ICONS else "badge-neutral"
    return f'<span class="emotion-badge {badge_class}">{icon} {emotion.capitalize()}{score_str}</span>'


def get_sentiment_badge_html(label: str, compound: Optional[float] = None) -> str:
    """Generates HTML for sentiment tag."""
    lbl_lower = str(label).lower() if label else "neutral"
    if lbl_lower == "positive":
        cls = "badge-joy"
        icon = "📈"
    elif lbl_lower == "negative":
        cls = "badge-anger"
        icon = "📉"
    else:
        cls = "badge-neutral"
        icon = "⚖️"

    score_str = f" ({compound:+.2f})" if compound is not None else ""
    return f'<span class="emotion-badge {cls}">{icon} {label}{score_str}</span>'


def render_ai_suggestion(suggestion: str):
    """Renders stylized AI wellness & coping suggestion box."""
    if not suggestion:
        return
    st.markdown(
        f"""
        <div class="suggestion-card">
            <div style="font-weight: 700; margin-bottom: 0.4rem; font-size: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                <span>💡</span> MoodMentor AI Wellness Action Plan
            </div>
            <div style="font-size: 0.95rem; line-height: 1.55;">
                {suggestion.replace(chr(10), '<br>')}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_timeline_entry_card(
    date_str: str,
    title: str,
    content: str,
    emotion: str,
    sentiment: str,
    compound: Optional[float] = None
):
    """Renders a chronological timeline item with styled connector and emotion badges."""
    emo_badge = get_emotion_badge_html(emotion)
    sent_badge = get_sentiment_badge_html(sentiment, compound)

    st.markdown(
        f"""
        <div class="timeline-item">
            <div class="timeline-card">
                <div class="timeline-meta">
                    <span style="font-size: 0.82rem; font-weight: 700; color: #4338ca; background: #e0e7ff; padding: 0.2rem 0.6rem; border-radius: 9999px;">
                        📅 {date_str}
                    </span>
                    <div style="display: flex; gap: 0.4rem;">
                        {emo_badge}
                        {sent_badge}
                    </div>
                </div>
                <div style="font-weight: 700; color: #1e293b; font-size: 1.05rem; margin: 0.4rem 0 0.25rem 0;">
                    {title}
                </div>
                <div style="color: #475569; font-size: 0.92rem; line-height: 1.5;">
                    {content}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
