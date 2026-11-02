import io
import pandas as pd
import streamlit as st
from datetime import datetime
from frontend.api_client import api_client
from frontend.components.cards import render_header


def render_export_view():
    """Renders journal CSV export and backup download interface."""
    render_header(
        title="📥 Export Journal CSV",
        subtitle="Download a complete, portable archive of your journal reflections, emotion scores, and AI insights.",
        badge="📥 DATA PORTABILITY"
    )

    st.markdown(
        """
        <div style="background: white; border-radius: 1.15rem; padding: 1.5rem 1.75rem; border: 1px solid rgba(199, 210, 254, 0.65); margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <h4 style="margin-top: 0; color: #1e1b4b; font-weight: 800;">Data Portability & Backup</h4>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.6;">
                Your emotional wellness data belongs to you. You can export your full journaling history anytime in a clean CSV format compatible with Excel, Google Sheets, Python, and data science analytics.
            </p>
            <div style="font-size: 0.85rem; color: #4338ca; background: #e0e7ff; padding: 0.75rem 1rem; border-radius: 0.65rem; border: 1px solid #c7d2fe;">
                <b>Generated Columns:</b> <code>Date</code>, <code>Emotion</code>, <code>Sentiment</code>, <code>Journal</code>, <code>Confidence</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.spinner("Preparing export archive from MySQL..."):
        success, csv_text = api_client.export_csv_data(format_type="journal")

    if not success or not csv_text or not csv_text.strip():
        st.warning("No journal entries found to export. Start journaling to generate your personal archive!")
        return

    # Parse and preview using pandas
    try:
        df = pd.read_csv(io.StringIO(csv_text))
        st.markdown(f"#### 📋 Archive Preview ({len(df)} Records)")
        st.dataframe(
            df,
            use_container_width=True,
            height=250
        )
    except Exception:
        pass

    filename = f"moodmentor_journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    st.download_button(
        label="📥 Download Journal CSV",
        data=csv_text,
        file_name=filename,
        mime="text/csv",
        type="primary",
        use_container_width=True
    )
