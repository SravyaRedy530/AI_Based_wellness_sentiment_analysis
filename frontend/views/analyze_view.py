import json
import streamlit as st
from datetime import date
from frontend.api_client import api_client
from frontend.config import EMOTION_COLORS, EMOTION_ICONS, API_BASE_URL
from frontend.components.cards import render_header, render_progress_card
from frontend.components.charts import render_emotion_probability_bars


EXAMPLE_THOUGHTS = {
    "😊 Joy": "I am so happy and proud of what we achieved today! The whole team came together and celebrated our launch.",
    "😨 Fear": "I have this intense anxiety about the upcoming presentation tomorrow. What if my mind goes blank and I mess up?",
    "😢 Sadness": "I feel so lonely and disheartened lately. It seems like nothing is going right no matter how much effort I put in.",
    "😡 Anger": "I am furious that our project work was dismissed without anyone even reading the technical details. It is completely unfair.",
    "🤢 Disgust": "I felt deeply uncomfortable and repulsed by the toxic office gossip and unethical decisions made in our meeting today.",
    "💖 Love": "I am so grateful for my family and supportive teammates. Their kindness and unconditional warmth mean the world to me.",
    "😲 Surprise": "I had no idea I was being selected for the leadership excellence award! I am in complete shock and amazement.",
    "😐 Neutral": "Completed my routine weekly tasks, organized my desk, and reviewed the checklist for tomorrow's standup meeting."
}


def render_analyze_view():
    """
    Renders the AI Emotion Analyzer Page.
    Features:
    - Streamlit textarea for thoughts
    - Analyze button calling Flask API via fetch
    - Emotion Card, Sentiment Card, Confidence Card
    - Progress bars for confidence and multi-class distribution
    - Personalized Suggestion Cards (Joy, Fear, Sadness, etc.)
    - Automatic save indicator to MySQL
    - Professional blue-purple styling
    """
    render_header(
        title="✨ Analyze Text",
        subtitle="Understand your emotional landscape with DistilBERT deep learning, VADER sentiment, and personalized activity suggestions.",
        badge="🧠 REAL-TIME AI EMOTION ANALYZER"
    )

    # -------------------------------------------------------------------
    # Quick Emotion Example Fillers
    # -------------------------------------------------------------------
    st.markdown(
        """
        <div style="font-size: 0.88rem; font-weight: 700; color: #4338ca; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
            💡 Quick Prompt Starters:
        </div>
        """,
        unsafe_allow_html=True
    )
    cols = st.columns(len(EXAMPLE_THOUGHTS))
    for i, (label, text_sample) in enumerate(EXAMPLE_THOUGHTS.items()):
        with cols[i]:
            if st.button(label, key=f"ex_btn_{i}", use_container_width=True):
                st.session_state["analyzer_input"] = text_sample

    current_text = st.session_state.get("analyzer_input", "")

    # -------------------------------------------------------------------
    # 1. Streamlit Textarea Input
    # -------------------------------------------------------------------
    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
    user_thoughts = st.text_area(
        "Enter your thoughts or daily reflection:",
        value=current_text,
        height=140,
        placeholder="Type how you are feeling right now, what happened today, or what is occupying your mind..."
    )

    btn_col1, btn_col2 = st.columns([1.2, 3])
    with btn_col1:
        analyze_clicked = st.button("✨ Analyze Emotion", type="primary", use_container_width=True)

    # -------------------------------------------------------------------
    # 2. Call Flask API & Process Response
    # -------------------------------------------------------------------
    if analyze_clicked:
        if not user_thoughts or not user_thoughts.strip():
            st.warning("Please enter some thoughts before clicking Analyze.")
        else:
            with st.spinner("Classifying emotion and analyzing sentiment via Flask API..."):
                success, msg, data = api_client.analyze_emotion(user_thoughts.strip())
                if success and data:
                    st.session_state["emotion_result"] = data
                    st.session_state["analyzed_thought"] = user_thoughts.strip()
                    if data.get("auto_saved"):
                        st.toast("✔ Automatically saved to My Journal in MySQL!", icon="💾")
                        st.success("✔ Emotion analyzed and automatically saved to My Journal in MySQL!")
                else:
                    st.error(f"Analysis Error: {msg}")

    # -------------------------------------------------------------------
    # 3. Display Analysis Results (Cards, Sentiment, Confidence, Recommendations)
    # -------------------------------------------------------------------
    if "emotion_result" in st.session_state:
        res = st.session_state["emotion_result"]
        analyzed_thought = st.session_state.get("analyzed_thought", "")

        # Extract values
        emotion = res.get("emotion") or res.get("primary_emotion", "Neutral")
        sentiment = res.get("sentiment_label") or res.get("sentiment", "Neutral")
        if isinstance(sentiment, dict):
            sentiment = sentiment.get("label", "Neutral")

        sentiment_score = res.get("sentiment_score", 0.0)
        if isinstance(sentiment_score, dict):
            sentiment_score = sentiment_score.get("compound", 0.0)

        confidence = res.get("confidence") or res.get("emotion_confidence", 0.0)
        confidence_pct = res.get("confidence_percentage", round(float(confidence) * 100, 1))

        recommendations = res.get("recommendations") or res.get("coping_suggestion", "")

        emo_lower = emotion.lower()
        emo_icon = EMOTION_ICONS.get(emo_lower, "🌱")
        emo_color = EMOTION_COLORS.get(emo_lower, "#6366f1")

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("### 📊 AI Emotion Assessment Cards")

        # 3-Card Metric Summary Grid
        card_col1, card_col2, card_col3 = st.columns(3)

        # 1. EMOTION CARD
        with card_col1:
            st.markdown(
                f"""
                <div style="background: white; border-radius: 1.15rem; padding: 1.5rem; border: 2px solid {emo_color}; box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.12); text-align: center; height: 100%;">
                    <div style="font-size: 0.8rem; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem;">
                        🎭 Detected Emotion
                    </div>
                    <div style="font-size: 3.5rem; margin: 0.25rem 0;">{emo_icon}</div>
                    <div style="font-size: 1.85rem; font-weight: 800; color: {emo_color};">
                        {emotion}
                    </div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.35rem; font-weight: 600;">
                        Primary Affective State
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 2. SENTIMENT CARD
        with card_col2:
            sent_lower = str(sentiment).lower()
            if sent_lower == "positive":
                sent_color = "#059669"
                sent_emoji = "📈"
            elif sent_lower == "negative":
                sent_color = "#dc2626"
                sent_emoji = "📉"
            else:
                sent_color = "#475569"
                sent_emoji = "⚖️"

            st.markdown(
                f"""
                <div style="background: white; border-radius: 1.15rem; padding: 1.5rem; border: 1.5px solid rgba(199, 210, 254, 0.7); box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.08); text-align: center; height: 100%;">
                    <div style="font-size: 0.8rem; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem;">
                        📊 Sentiment Analysis
                    </div>
                    <div style="font-size: 3.5rem; margin: 0.25rem 0;">{sent_emoji}</div>
                    <div style="font-size: 1.85rem; font-weight: 800; color: {sent_color};">
                        {sentiment}
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #1e1b4b; margin-top: 0.35rem;">
                        Compound Score: <b>{sentiment_score:+.2f}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 3. CONFIDENCE CARD WITH PROGRESS BAR
        with card_col3:
            st.markdown(
                f"""
                <div style="background: white; border-radius: 1.15rem; padding: 1.5rem; border: 1.5px solid rgba(199, 210, 254, 0.7); box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.08); text-align: center; height: 100%;">
                    <div style="font-size: 0.8rem; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem;">
                        🎯 Model Confidence
                    </div>
                    <div style="font-size: 3.5rem; margin: 0.25rem 0;">🎯</div>
                    <div style="font-size: 1.85rem; font-weight: 800; color: #4338ca;">
                        {confidence_pct}%
                    </div>
                    <div style="margin: 0.6rem 0 0.2rem 0;">
                        <div class="custom-progress-container" style="height: 8px;">
                            <div class="custom-progress-fill" style="width: {confidence_pct}%;"></div>
                        </div>
                    </div>
                    <div style="font-size: 0.78rem; color: #64748b; font-weight: 600;">
                        DistilBERT Deep Learning Model
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)

        # -------------------------------------------------------------------
        # 4. PERSONALIZED SUGGESTIONS CARDS
        # -------------------------------------------------------------------
        st.markdown(f"### 🎯 Personalized Suggestions for {emotion}")

        simple_suggs = res.get("suggestions", [])
        detailed_suggs = res.get("detailed_suggestions") or res.get("personalized_suggestions", [])

        if simple_suggs:
            pills_html = " ".join([
                f'<span class="suggestion-pill">✔ {s}</span>'
                for s in simple_suggs
            ])
            st.markdown(f"<div style='margin-bottom: 1rem;'>{pills_html}</div>", unsafe_allow_html=True)

        if detailed_suggs:
            sugg_cols = st.columns(len(detailed_suggs))
            for idx, sugg in enumerate(detailed_suggs):
                with sugg_cols[idx]:
                    if isinstance(sugg, dict):
                        s_icon = sugg.get("icon", "💡")
                        s_title = sugg.get("title", "Action")
                        s_desc = sugg.get("description", "")
                        s_cat = sugg.get("category", "Wellness")
                    else:
                        s_icon = "✨"
                        s_title = str(sugg)
                        s_desc = f"Action step tailored for emotional state: {emotion}."
                        s_cat = "Activity"

                    st.markdown(
                        f"""
                        <div style="background: white; border-radius: 1rem; padding: 1.25rem; border: 1px solid rgba(199, 210, 254, 0.7); box-shadow: 0 4px 12px rgba(79, 70, 229, 0.06); height: 100%;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <span style="font-size: 1.8rem;">{s_icon}</span>
                                <span style="font-size: 0.72rem; color: #047857; background: #ecfdf5; padding: 0.2rem 0.55rem; border-radius: 9999px; font-weight: 700; border: 1px solid #a7f3d0;">
                                    {s_cat}
                                </span>
                            </div>
                            <div style="font-weight: 800; color: #1e1b4b; font-size: 1.05rem; margin-bottom: 0.35rem;">
                                {s_title}
                            </div>
                            <div style="font-size: 0.88rem; color: #475569; line-height: 1.55;">
                                {s_desc}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # Full emotion vector breakdown chart with progress bars
        analysis_dict = res.get("analysis", {})
        all_emotions = analysis_dict.get("all_emotions", [])
        if all_emotions:
            st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
            with st.expander("📈 Multi-Class Emotion Probability Spectrum"):
                render_emotion_probability_bars(all_emotions)

        # Detailed psychological guidance
        if recommendations:
            st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
            with st.expander("🧘 Comprehensive Cognitive Action Plan"):
                st.markdown(
                    f"""
                    <div style="background: #f8fafc; border-left: 4px solid #6366f1; padding: 1.2rem; border-radius: 0.5rem; color: #1e293b; line-height: 1.6;">
                        {recommendations.replace(chr(10), '<br>')}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # -------------------------------------------------------------------
    # Interactive Fetch API Playground
    # -------------------------------------------------------------------
    with st.expander("🌐 Fetch API Code & REST Specification"):
        st.markdown("##### Real-time Client-Side `fetch()` Integration:")
        st.code(
            f"""
// JavaScript Fetch API Example to analyze thoughts
const response = await fetch('{API_BASE_URL}/analyze', {{
    method: 'POST',
    headers: {{
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + userToken
    }},
    body: JSON.stringify({{ text: "I am feeling happy and accomplished!" }})
}});
const result = await response.json();
console.log('Emotion:', result.emotion);
console.log('Sentiment:', result.sentiment);
console.log('Confidence:', result.confidence);
console.log('Suggestions:', result.suggestions);
            """,
            language="javascript"
        )
