import io
from datetime import datetime
import pandas as pd
import streamlit as st
from frontend.api_client import api_client
from frontend.components.cards import render_header


def render_profile_view():
    """
    Renders Profile Page.
    Requirements:
    - Full Name
    - Email
    - Preferred Support Style
    - Theme
    - Export Journal CSV
    - Delete Account
    - Update Profile
    - Store in MySQL
    """
    user = st.session_state.get("user") or {}
    if not st.session_state.get("token") or not user:
        st.info("🔒 Please log in or register to manage your personal profile settings.")
        from frontend.views.login_view import render_login_view
        render_login_view()
        return

    render_header(
        title="👤 My Profile",
        subtitle="Manage your personal credentials, support preferences, appearance theme, data export, and account lifecycle stored in MySQL.",
        badge="👤 USER SETTINGS & ARCHIVE"
    )

    # Top Profile Card Summary
    full_name_val = user.get("full_name") or user.get("fullname") or "User"
    email_val = user.get("email") or ""
    support_style_val = user.get("preferred_support_style") or "Gentle & Compassionate"
    theme_val = user.get("theme") or "Light Mode"
    created_at_val = user.get("created_at", "")[:10] if user.get("created_at") else "Recently"

    st.markdown(
        f"""
        <div style="background: white; border-radius: 1rem; padding: 1.5rem; border: 1px solid #e2e8f0; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 3rem; background: #eef2ff; border-radius: 50%; width: 70px; height: 70px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        🧘
                    </div>
                    <div>
                        <h2 style="margin: 0; color: #1e293b; font-size: 1.4rem; font-weight: 800;">{full_name_val}</h2>
                        <div style="color: #64748b; font-size: 0.9rem; font-weight: 500;">✉️ {email_val}</div>
                        <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.2rem;">Member since: <b>{created_at_val}</b></div>
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    <span style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; font-size: 0.8rem; font-weight: 600; padding: 0.35rem 0.75rem; border-radius: 9999px;">
                        🤝 Support: {support_style_val}
                    </span>
                    <span style="background: #f5f3ff; color: #6d28d9; border: 1px solid #ddd6fe; font-size: 0.8rem; font-weight: 600; padding: 0.35rem 0.75rem; border-radius: 9999px;">
                        🎨 Theme: {theme_val}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 1], gap="large")

    # -------------------------------------------------------------------
    # Column 1: Profile Information & Settings (Store in MySQL)
    # - Full Name
    # - Email
    # - Preferred Support Style
    # - Theme
    # - Update Profile Button
    # -------------------------------------------------------------------
    with col1:
        st.markdown("### ✏️ Edit Profile Information")
        st.caption("Changes are permanently saved to your MySQL database record.")

        with st.form("edit_profile_form"):
            # 1. Full Name
            new_full_name = st.text_input(
                "Full Name",
                value=full_name_val,
                placeholder="Enter your full name..."
            )

            # 2. Email
            new_email = st.text_input(
                "Email Address",
                value=email_val,
                placeholder="Enter your email address..."
            )

            # 3. Preferred Support Style
            support_styles = [
                "Gentle & Compassionate",
                "Solution-Oriented & Direct",
                "Mindful & Philosophical",
                "Motivational & Energizing"
            ]
            current_style = support_style_val if support_style_val in support_styles else support_styles[0]
            style_idx = support_styles.index(current_style)
            new_support_style = st.selectbox(
                "Preferred Support Style",
                options=support_styles,
                index=style_idx,
                help="Determines the tone and cognitive framing applied in AI personalized wellness suggestions."
            )

            # 4. Theme
            themes_list = [
                "Light Mode",
                "Dark Mode",
                "Calm Lavender",
                "Nature Green"
            ]
            current_theme = theme_val if theme_val in themes_list else themes_list[0]
            theme_idx = themes_list.index(current_theme)
            new_theme = st.selectbox(
                "Theme",
                options=themes_list,
                index=theme_idx,
                help="Your selected interface and dashboard color mood theme."
            )

            # Additional Profile context
            new_bio = st.text_area(
                "Personal Reflection Bio",
                value=user.get("bio", ""),
                height=75,
                placeholder="Brief summary of your emotional wellness journey..."
            )

            wellness_goals = [
                "Mindfulness & Stress Reduction",
                "Emotional Resilience & Coping",
                "Gratitude & Joy Tracking",
                "Workplace Wellness & Balance",
                "Productivity & Cognitive Clarity"
            ]
            current_goal = user.get("wellness_goal", wellness_goals[0])
            goal_idx = wellness_goals.index(current_goal) if current_goal in wellness_goals else 0
            new_wellness_goal = st.selectbox(
                "Primary Wellness Goal",
                options=wellness_goals,
                index=goal_idx
            )

            # 5. Update Profile Button
            update_profile_clicked = st.form_submit_button(
                "💾 Update Profile (Save to MySQL)",
                type="primary",
                use_container_width=True
            )

            if update_profile_clicked:
                if not new_full_name or not new_full_name.strip():
                    st.error("Full Name cannot be empty.")
                elif not new_email or not new_email.strip():
                    st.error("Email Address cannot be empty.")
                else:
                    with st.spinner("Updating profile in MySQL..."):
                        ok, msg, updated_user = api_client.update_profile(
                            full_name=new_full_name.strip(),
                            email=new_email.strip(),
                            preferred_support_style=new_support_style,
                            theme=new_theme,
                            bio=new_bio.strip() if new_bio else "",
                            wellness_goal=new_wellness_goal
                        )
                        if ok and updated_user:
                            st.session_state["user"] = updated_user
                            st.success("✔ Profile updated successfully in MySQL!")
                            st.rerun()
                        else:
                            st.error(f"Error: {msg}")

    # -------------------------------------------------------------------
    # Column 2: Data Export & Account Deletion
    # - Export Journal CSV
    # - Delete Account
    # -------------------------------------------------------------------
    with col2:
        # 1. EXPORT JOURNAL CSV
        st.markdown("### 📥 Export Journal CSV")
        st.caption("Export your complete reflection log, emotions, and sentiments from MySQL.")

        with st.container():
            st.markdown(
                """
                <div style="background: white; border-radius: 0.85rem; padding: 1.25rem; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03); margin-bottom: 1.25rem;">
                    <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                        <span style="font-size: 2rem;">📊</span>
                        <div>
                            <div style="font-weight: 700; color: #1e293b; font-size: 1rem;">Export Complete Journal Archive (CSV)</div>
                            <div style="color: #64748b; font-size: 0.85rem; margin-top: 0.25rem; line-height: 1.5;">
                                Download your full reflection history as a standard CSV file with exact columns:
                                <br><b style="color: #4338ca;">Date, Emotion, Sentiment, Journal, Confidence</b>.
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("🔄 Generate & Prepare Journal CSV", key="btn_prep_csv", use_container_width=True):
                with st.spinner("Fetching journal records from MySQL..."):
                    csv_ok, csv_content = api_client.export_csv_data(format_type="journal")
                    if csv_ok and csv_content and csv_content.strip():
                        st.session_state["exported_csv_content"] = csv_content
                        st.success("✔ Journal records retrieved from MySQL. Click below to download!")
                    else:
                        st.warning("No journal entries found in MySQL to export.")

            if "exported_csv_content" in st.session_state:
                csv_data = st.session_state["exported_csv_content"]
                try:
                    df_exp = pd.read_csv(io.StringIO(csv_data))
                    st.dataframe(df_exp.head(5), use_container_width=True, hide_index=True)
                except Exception:
                    pass

                fname = f"moodmentor_journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                st.download_button(
                    label="📥 Download Journal CSV",
                    data=csv_data,
                    file_name=fname,
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )

        st.markdown("<hr style='margin: 1.5rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)

        # 2. PASSWORD CHANGE (Security)
        with st.expander("🔒 Change Account Password"):
            with st.form("pwd_change_form"):
                cur_p = st.text_input("Current Password", type="password")
                new_p = st.text_input("New Password (min 6 chars)", type="password")
                conf_p = st.text_input("Confirm New Password", type="password")
                p_btn = st.form_submit_button("Update Password", type="secondary")

                if p_btn:
                    if not cur_p or not new_p:
                        st.error("Please provide both current and new passwords.")
                    elif new_p != conf_p:
                        st.error("New passwords do not match.")
                    elif len(new_p) < 6:
                        st.error("New password must be at least 6 characters.")
                    else:
                        with st.spinner("Updating password in MySQL..."):
                            p_ok, p_msg = api_client.change_password(cur_p, new_p)
                            if p_ok:
                                st.success("✔ Password updated successfully in MySQL!")
                            else:
                                st.error(p_msg)

        # 3. DELETE ACCOUNT (Danger Zone)
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background: #fef2f2; border: 1.5px solid #fecaca; border-radius: 0.85rem; padding: 1.25rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
                    <span style="font-size: 1.3rem;">⚠️</span>
                    <span style="font-weight: 800; color: #991b1b; font-size: 1.05rem;">Danger Zone: Delete Account</span>
                </div>
                <p style="color: #b91c1c; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                    Permanently delete your account and all associated reflections, AI emotion logs, and analytics from the MySQL database. <b>This action cannot be undone.</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("🗑️ Delete Account Permanently", expanded=False):
            st.warning("Confirm your password below to permanently erase your profile and records from MySQL.")
            confirm_pwd = st.text_input(
                "Confirm Account Password",
                type="password",
                placeholder="Enter password to confirm...",
                key="delete_account_confirm_pwd"
            )
            del_account_btn = st.button("Permanently Delete Account", type="primary", use_container_width=True)

            if del_account_btn:
                if not confirm_pwd:
                    st.error("Please enter your password to confirm account deletion.")
                else:
                    with st.spinner("Deleting account and all cascading records from MySQL..."):
                        del_ok, del_msg = api_client.delete_account(confirm_pwd)
                        if del_ok:
                            st.success("Account permanently deleted from MySQL.")
                            st.session_state.clear()
                            st.rerun()
                        else:
                            st.error(f"Deletion failed: {del_msg}")
