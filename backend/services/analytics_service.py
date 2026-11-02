import random
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from collections import Counter
from sqlalchemy import func
from backend.models.database import db
from backend.models.journal import JournalEntry
from backend.models.emotion_log import EmotionLog

WELLNESS_QUOTES = [
    {"quote": "Feelings are just visitors, let them come and go.", "author": "Mooji"},
    {"quote": "Almost everything will work again if you unplug it for a few minutes, including you.", "author": "Anne Lamott"},
    {"quote": "You don't have to control your thoughts. You just have to stop letting them control you.", "author": "Dan Millman"},
    {"quote": "Self-awareness gives you the capacity to learn from your mistakes as well as your successes.", "author": "Lawrence Bossidy"},
    {"quote": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein"},
    {"quote": "Breathe. Let go. And remind yourself that this very moment is the only one you know you have for sure.", "author": "Oprah Winfrey"},
    {"quote": "Caring for myself is not self-indulgence, it is self-preservation.", "author": "Audre Lorde"}
]


class AnalyticsService:
    """Service providing aggregate statistics, streak calculations, and Plotly chart data."""

    @staticmethod
    def get_dashboard_stats(user_id: int) -> Dict[str, Any]:
        """Calculates high-level metrics for dashboard cards and streak counters."""
        entries = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.entry_date.desc()).all()
        total_entries = len(entries)

        if total_entries == 0:
            return {
                "total_entries": 0,
                "current_streak": 0,
                "dominant_emotion": "N/A",
                "avg_sentiment": 0.0,
                "sentiment_label": "No Data",
                "positive_entries": 0,
                "negative_entries": 0,
                "neutral_entries": 0,
                "recent_entries": [],
                "daily_quote": random.choice(WELLNESS_QUOTES)
            }

        # 1. Calculate Writing Streak
        streak = AnalyticsService._calculate_streak(entries)

        # 2. Emotion Counts & Dominant Emotion
        emotions = [e.emotion_log.primary_emotion for e in entries if e.emotion_log]
        emotion_counts = Counter(emotions)
        dominant_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "neutral"

        # 3. Sentiment Averages
        compounds = [e.emotion_log.sentiment_compound for e in entries if e.emotion_log]
        avg_sentiment = sum(compounds) / len(compounds) if compounds else 0.0

        if avg_sentiment >= 0.05:
            sentiment_label = "Positive"
        elif avg_sentiment <= -0.05:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        # 4. Polarity Breakdown
        positive_count = sum(1 for c in compounds if c >= 0.05)
        negative_count = sum(1 for c in compounds if c <= -0.05)
        neutral_count = len(compounds) - positive_count - negative_count

        # 5. Recent 4 entries
        recent = [e.to_dict(include_analysis=True) for e in entries[:4]]

        return {
            "total_entries": total_entries,
            "current_streak": streak,
            "dominant_emotion": dominant_emotion,
            "avg_sentiment": round(avg_sentiment, 3),
            "sentiment_label": sentiment_label,
            "positive_entries": positive_count,
            "negative_entries": negative_count,
            "neutral_entries": neutral_count,
            "recent_entries": recent,
            "daily_quote": random.choice(WELLNESS_QUOTES)
        }

    @staticmethod
    def get_emotion_insights(user_id: int) -> Dict[str, Any]:
        """Prepares comprehensive analytics and structured data for Plotly visualizations."""
        entries = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.entry_date.asc()).all()

        if not entries:
            return {
                "has_data": False,
                "total_entries": 0,
                "total_checkins": 0,
                "most_frequent_emotion": "N/A",
                "most_frequent_emotion_count": 0,
                "avg_sentiment": 0.0,
                "sentiment_label": "No Data",
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "neutral_percentage": 0.0,
                "emotion_distribution": {},
                "sentiment_timeline": [],
                "monthly_report": [],
                "radar_data": {},
                "top_keywords": [],
                "weekly_distribution": {}
            }

        # 1. Total Check-ins
        total_checkins = len(entries)

        # 2. Emotion Distribution & Most Frequent Emotion
        emotions = [
            (e.emotion_log.primary_emotion.capitalize() if e.emotion_log and e.emotion_log.primary_emotion else "Neutral")
            for e in entries
        ]
        emotion_counts = dict(Counter(emotions))
        most_frequent_tuple = Counter(emotions).most_common(1)
        most_frequent_emotion = most_frequent_tuple[0][0] if most_frequent_tuple else "Neutral"
        most_frequent_count = most_frequent_tuple[0][1] if most_frequent_tuple else 0

        # 3. Sentiment Averages & Percentages
        compounds = [e.emotion_log.sentiment_compound for e in entries if e.emotion_log and e.emotion_log.sentiment_compound is not None]
        avg_sentiment = round(sum(compounds) / len(compounds), 3) if compounds else 0.0

        if avg_sentiment >= 0.05:
            sentiment_label = "Positive"
        elif avg_sentiment <= -0.05:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        total_valid = len(compounds) if compounds else 1
        pos_count = sum(1 for c in compounds if c >= 0.05)
        neg_count = sum(1 for c in compounds if c <= -0.05)
        neu_count = len(compounds) - pos_count - neg_count

        positive_pct = round((pos_count / total_valid) * 100, 1) if compounds else 0.0
        negative_pct = round((neg_count / total_valid) * 100, 1) if compounds else 0.0
        neutral_pct = round((neu_count / total_valid) * 100, 1) if compounds else 0.0

        # 4. Sentiment Timeline (Line Chart with progression)
        timeline = []
        for e in entries:
            if e.emotion_log:
                entry_dt_str = e.entry_date.isoformat() if e.entry_date else (e.created_at.strftime("%Y-%m-%d") if e.created_at else "")
                timeline.append({
                    "date": entry_dt_str,
                    "datetime": e.created_at.strftime("%Y-%m-%d %H:%M") if e.created_at else entry_dt_str,
                    "title": e.title,
                    "compound": round(e.emotion_log.sentiment_compound or 0.0, 3),
                    "primary_emotion": (e.emotion_log.primary_emotion or "Neutral").capitalize(),
                    "positive": round(e.emotion_log.sentiment_positive or 0.0, 3),
                    "negative": round(e.emotion_log.sentiment_negative or 0.0, 3)
                })

        # 5. Monthly Report Aggregation
        monthly_dict = {}
        for e in entries:
            dt = e.entry_date or (e.created_at.date() if e.created_at else date.today())
            month_key = dt.strftime("%Y-%m")
            month_label = dt.strftime("%b %Y")
            if month_key not in monthly_dict:
                monthly_dict[month_key] = {
                    "month_key": month_key,
                    "month_label": month_label,
                    "total_entries": 0,
                    "compounds": [],
                    "emotions": []
                }
            monthly_dict[month_key]["total_entries"] += 1
            if e.emotion_log:
                if e.emotion_log.sentiment_compound is not None:
                    monthly_dict[month_key]["compounds"].append(e.emotion_log.sentiment_compound)
                if e.emotion_log.primary_emotion:
                    monthly_dict[month_key]["emotions"].append(e.emotion_log.primary_emotion.capitalize())

        monthly_report = []
        for m_key in sorted(monthly_dict.keys()):
            m_data = monthly_dict[m_key]
            m_compounds = m_data["compounds"]
            m_avg_sent = round(sum(m_compounds) / len(m_compounds), 3) if m_compounds else 0.0
            m_emo_counts = dict(Counter(m_data["emotions"]))
            m_dom_tuple = Counter(m_data["emotions"]).most_common(1)
            m_dom_emo = m_dom_tuple[0][0] if m_dom_tuple else "Neutral"
            m_pos = sum(1 for c in m_compounds if c >= 0.05)
            m_neg = sum(1 for c in m_compounds if c <= -0.05)
            m_total_val = len(m_compounds) if m_compounds else 1
            m_pos_pct = round((m_pos / m_total_val) * 100, 1) if m_compounds else 0.0
            m_neg_pct = round((m_neg / m_total_val) * 100, 1) if m_compounds else 0.0

            monthly_report.append({
                "month_key": m_key,
                "month_label": m_data["month_label"],
                "total_entries": m_data["total_entries"],
                "avg_sentiment": m_avg_sent,
                "dominant_emotion": m_dom_emo,
                "positive_entries": m_pos,
                "negative_entries": m_neg,
                "positive_pct": m_pos_pct,
                "negative_pct": m_neg_pct,
                "emotion_breakdown": m_emo_counts
            })

        # 6. Radar Chart Data (Aggregate average intensity per emotion class)
        radar_accumulator = {"joy": 0.0, "sadness": 0.0, "anger": 0.0, "fear": 0.0, "love": 0.0, "surprise": 0.0}
        radar_counter = {"joy": 0, "sadness": 0, "anger": 0, "fear": 0, "love": 0, "surprise": 0}

        for e in entries:
            elog = e.emotion_log
            if elog and elog.all_emotions:
                items = elog.all_emotions if isinstance(elog.all_emotions, list) else []
                for item in items:
                    emo = item.get("emotion", "").lower()
                    if emo in radar_accumulator:
                        radar_accumulator[emo] += float(item.get("score", 0.0))
                        radar_counter[emo] += 1

        radar_data = {}
        for emo, total_score in radar_accumulator.items():
            count = radar_counter[emo]
            radar_data[emo] = round(total_score / count, 4) if count > 0 else 0.0

        # 7. Top Keywords Aggregation
        all_kw = []
        for e in entries:
            elog = e.emotion_log
            if elog and elog.keywords:
                kw_items = elog.keywords if isinstance(elog.keywords, list) else []
                for kw in kw_items:
                    if isinstance(kw, dict) and "keyword" in kw:
                        all_kw.append(kw["keyword"].lower())
                    elif isinstance(kw, str):
                        all_kw.append(kw.lower())

        top_keywords = [{"keyword": k, "count": v} for k, v in Counter(all_kw).most_common(10)]

        # 8. Day of Week Distribution
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_counts = {d: 0 for d in days}
        for e in entries:
            if e.entry_date:
                day_name = e.entry_date.strftime("%A")
                if day_name in weekly_counts:
                    weekly_counts[day_name] += 1

        return {
            "has_data": True,
            "total_entries": total_checkins,
            "total_checkins": total_checkins,
            "most_frequent_emotion": most_frequent_emotion,
            "most_frequent_emotion_count": most_frequent_count,
            "avg_sentiment": avg_sentiment,
            "sentiment_label": sentiment_label,
            "positive_percentage": positive_pct,
            "negative_percentage": negative_pct,
            "neutral_percentage": neutral_pct,
            "emotion_distribution": emotion_counts,
            "sentiment_timeline": timeline,
            "monthly_report": monthly_report,
            "radar_data": radar_data,
            "top_keywords": top_keywords,
            "weekly_distribution": weekly_counts
        }

    @staticmethod
    def _calculate_streak(entries: List[JournalEntry]) -> int:
        """Computes consecutive days of journaling up to today or yesterday."""
        if not entries:
            return 0

        # Unique dates descending
        dates = sorted(list(set(e.entry_date for e in entries if e.entry_date)), reverse=True)
        if not dates:
            return 0

        today = date.today()
        yesterday = today - timedelta(days=1)

        # If the latest entry isn't today or yesterday, streak is broken
        if dates[0] != today and dates[0] != yesterday:
            return 0

        streak = 1
        current = dates[0]

        for next_date in dates[1:]:
            if current - next_date == timedelta(days=1):
                streak += 1
                current = next_date
            else:
                break

        return streak
