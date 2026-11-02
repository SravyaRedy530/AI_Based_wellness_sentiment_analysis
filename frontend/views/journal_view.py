import io
import csv
import pandas as pd
from datetime import date, datetime
import streamlit as st
from frontend.api_client import api_client
from frontend.components.cards import (
    render_header,
    get_emotion_badge_html,
    get_sentiment_badge_html,
    render_ai_suggestion
)
from frontend.config import EMOTION_ICONS, EMOTION_COLORS


def render_journal_view():
    """
    Renders My Journal view.
    Features:
    - Every analysis automatically saves to MySQL
    - Display cards (Emotion, Journal text, Sentiment, Date, Delete button)
    - Search by emotion
    - Search by keyword
    - Sort by latest
    - Responsive layout with professional blue-purple theme
    """
    render_header(
        title="📖 My Journal",
        subtitle="Every reflection and analysis automatically saves to your secure MySQL database.",
        badge="📖 SECURE PERSISTENCE ARCHIVE"
    )

    # -------------------------------------------------------------------
    # 1. Quick Thought Box: Auto-analyzes and auto-saves into MySQL
    # -------------------------------------------------------------------
    with st.expander("✍️ Express a New Reflection (Auto-Analyzed & Saved to MySQL)", expanded=False):
        new_thought = st.text_area(
            "What's on your mind today?",
            placeholder="Type your feelings, reflections, or experiences... Clicking Analyze will classify your emotion and save everything into MySQL automatically.",
            height=120,
            key="quick_journal_input"
        )
        col_s1, col_s2 = st.columns([1.3, 3])
        with col_s1:
            save_clicked = st.button("✨ Analyze & Auto-Save", type="primary", use_container_width=True)

        if save_clicked:
            if not new_thought or not new_thought.strip():
                st.warning("Please enter your thoughts before analyzing.")
            else:
                with st.spinner("Analyzing emotion with DistilBERT & auto-saving to MySQL..."):
                    ok, msg, data = api_client.analyze_emotion(new_thought.strip())
                    if ok:
                        st.success("✔ Analysis complete and automatically saved to MySQL!")
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------
    # 2. Filter & Search Bar
    # -------------------------------------------------------------------
    st.markdown(
        """
        <div style="font-size: 1.15rem; font-weight: 800; color: #1e1b4b; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
            <span>🔍</span> Search & Filter Journal Entries
        </div>
        """,
        unsafe_allow_html=True
    )

    f_col1, f_col2, f_col3 = st.columns([2, 1.2, 1.2])

    with f_col1:
        search_query = st.text_input(
            "Search by keyword",
            placeholder="🔍 Search reflection text, title, or topic...",
            key="journal_keyword_search"
        )

    with f_col2:
        emotion_choices = ["All", "Joy", "Fear", "Sadness", "Anger", "Love", "Surprise", "Neutral"]
        selected_emotion = st.selectbox(
            "Search by emotion",
            options=emotion_choices,
            index=0,
            key="journal_emotion_filter"
        )

    with f_col3:
        sort_choices = {
            "Sort by latest (Newest)": "date_desc",
            "Sort by oldest": "date_asc"
        }
        selected_sort = st.selectbox(
            "Sort order",
            options=list(sort_choices.keys()),
            index=0,
            key="journal_sort_order"
        )

    # Fetch entries from backend MySQL database
    success, entries = api_client.get_entries(
        search=search_query,
        emotion=selected_emotion if selected_emotion != "All" else "",
        sort_by=sort_choices[selected_sort]
    )

    st.markdown(
        f"""
        <div style="color: #64748b; font-size: 0.88rem; font-weight: 600; margin: 0.25rem 0 1rem 0;">
            Displaying <b style="color: #4338ca;">{len(entries)}</b> recorded reflections from MySQL database
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------------------------
    # CSV EXPORT SECTION
    # Columns: Date, Emotion, Sentiment, Journal, Confidence
    # -------------------------------------------------------------------
    if entries:
        with st.expander("📥 Export Journal to CSV (Date, Emotion, Sentiment, Journal, Confidence)", expanded=False):
            st.markdown(
                """
                <div style="font-size: 0.88rem; color: #475569; margin-bottom: 0.75rem;">
                    Download your personal reflection archive. The generated CSV contains exactly:
                    <br><code style="color: #4338ca; font-weight: 700;">Date, Emotion, Sentiment, Journal, Confidence</code>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Generate CSV with exact columns
            csv_output = io.StringIO()
            writer = csv.writer(csv_output, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["Date", "Emotion", "Sentiment", "Journal", "Confidence"])

            preview_rows = []
            for e in entries:
                elog = e.get("analysis") or {}
                d_val = e.get("entry_date", "")
                emo_val = elog.get("primary_emotion") or e.get("emotion") or "Neutral"
                sent_val = elog.get("sentiment_label") or e.get("sentiment") or "Neutral"
                if isinstance(sent_val, dict):
                    sent_val = sent_val.get("label", "Neutral")
                j_val = (e.get("content") or "").replace("\r\n", " ").replace("\n", " ").strip()
                conf = elog.get("confidence_percentage") or elog.get("emotion_confidence") or 0.0
                if isinstance(conf, float) and conf <= 1.0:
                    conf_str = f"{round(conf * 100, 1)}%"
                else:
                    conf_str = f"{conf}%" if "%" not in str(conf) else str(conf)

                writer.writerow([d_val, emo_val, sent_val, j_val, conf_str])
                preview_rows.append({
                    "Date": d_val,
                    "Emotion": emo_val,
                    "Sentiment": sent_val,
                    "Journal": (j_val[:65] + "...") if len(j_val) > 65 else j_val,
                    "Confidence": conf_str
                })

            csv_data_str = csv_output.getvalue()

            # Live Table Preview
            if preview_rows:
                st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)

            d_col1, d_col2 = st.columns([1.5, 3])
            with d_col1:
                st.download_button(
                    label="📥 Download Journal CSV",
                    data=csv_data_str,
                    file_name=f"moodmentor_journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )

    st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------
    # 3. Display Journal Cards
    # Each card contains:
    # - Emotion
    # - Journal text
    # - Sentiment
    # - Date
    # - Delete button
    # -------------------------------------------------------------------
    if not entries:
        st.info("No journal reflections found matching your criteria. Express a thought above to auto-save your first entry to MySQL!")
    else:
        for entry in entries:
            entry_id = entry.get("id")
            title = entry.get("title", "Reflection")
            content = entry.get("content", "")
            entry_date = entry.get("entry_date", "")
            created_at = entry.get("created_at", "")
            elog = entry.get("analysis") or {}

            primary_emo = elog.get("primary_emotion") or entry.get("emotion") or "Neutral"
            confidence_pct = elog.get("confidence_percentage", round(float(elog.get("emotion_confidence", 0.0)) * 100, 1))

            sent_obj = elog.get("sentiment") or {}
            if isinstance(sent_obj, dict):
                sentiment_label = sent_obj.get("label") or entry.get("sentiment", "Neutral")
                sentiment_compound = sent_obj.get("compound", 0.0)
            else:
                sentiment_label = elog.get("sentiment_label") or entry.get("sentiment", "Neutral")
                sentiment_compound = elog.get("sentiment_score", 0.0)

            suggestions = elog.get("suggestions", [])

            emo_lower = str(primary_emo).lower()
            emo_icon = EMOTION_ICONS.get(emo_lower, "🌱")
            emo_color = EMOTION_COLORS.get(emo_lower, "#6366f1")

            display_date = entry_date
            if created_at and len(created_at) >= 16:
                display_date = f"{entry_date} • {created_at[11:16]}"

            # Sentiment styling
            if str(sentiment_label).lower() == "positive":
                sent_color = "#059669"
                sent_bg = "#ecfdf5"
                sent_border = "#a7f3d0"
                sent_icon = "📈"
            elif str(sentiment_label).lower() == "negative":
                sent_color = "#dc2626"
                sent_bg = "#fef2f2"
                sent_border = "#fecaca"
                sent_icon = "📉"
            else:
                sent_color = "#475569"
                sent_bg = "#f8fafc"
                sent_border = "#e2e8f0"
                sent_icon = "⚖️"

            # Suggestion badge pills
            sugg_pills_html = ""
            if suggestions:
                pills = [f'<span class="suggestion-pill">✨ {s}</span>' for s in suggestions]
                sugg_pills_html = f"<div style='margin-top: 0.6rem;'>{''.join(pills)}</div>"

            # Render Card Container
            with st.container():
                st.markdown(
                    f"""
                    <div class="journal-card">
                        <div class="journal-header">
                            <!-- EMOTION & SENTIMENT BADGES -->
                            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                                <div style="background: {emo_color}18; border: 1.5px solid {emo_color}; color: {emo_color}; font-weight: 800; font-size: 0.92rem; padding: 0.35rem 0.85rem; border-radius: 9999px; display: inline-flex; align-items: center; gap: 0.4rem;">
                                    <span>{emo_icon}</span>
                                    <span>{primary_emo}</span>
                                    <span style="font-size: 0.75rem; opacity: 0.85;">({confidence_pct}%)</span>
                                </div>
                                <div style="background: {sent_bg}; border: 1px solid {sent_border}; color: {sent_color}; font-weight: 700; font-size: 0.82rem; padding: 0.3rem 0.75rem; border-radius: 9999px; display: inline-flex; align-items: center; gap: 0.3rem;">
                                    <span>{sent_icon}</span>
                                    <span>{sentiment_label}</span>
                                    <span>({sentiment_compound:+.2f})</span>
                                </div>
                            </div>
                            <!-- DATE -->
                            <div class="journal-date">
                                📅 <b>{display_date}</b>
                            </div>
                        </div>

                        <!-- JOURNAL TEXT -->
                        <div class="journal-body">
{content}
                        </div>

                        {sugg_pills_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Card Actions Row (Delete button & Details expander)
                btn_c1, btn_c2 = st.columns([1, 4.5])
                with btn_c1:
                    if st.button("🗑️ Delete", key=f"del_card_{entry_id}", type="secondary", use_container_width=True):
                        with st.spinner("Deleting from MySQL..."):
                            d_ok, d_msg = api_client.delete_entry(entry_id)
                            if d_ok:
                                st.success("Deleted from MySQL.")
                                st.rerun()
                            else:
                                st.error(d_msg)

                with btn_c2:
                    coping_plan = elog.get("coping_suggestion") or elog.get("recommendations")
                    if coping_plan:
                        with st.expander("💡 View Personalized Wellness Plan"):
                            render_ai_suggestion(coping_plan)

                st.markdown("<div style='margin-bottom: 0.85rem;'></div>", unsafe_allow_html=True)
