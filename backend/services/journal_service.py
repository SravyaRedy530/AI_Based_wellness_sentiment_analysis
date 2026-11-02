import csv
import io
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from sqlalchemy import desc, asc, func
from backend.models.database import db
from backend.models.journal import JournalEntry
from backend.models.emotion_log import EmotionLog
from backend.services.ai_service import ai_service


class JournalService:
    """Service handling Journal CRUD, AI pipeline orchestration, and filtering."""

    @staticmethod
    def create_entry(user_id: int, title: str, content: str, tags: str = "", entry_date: Optional[str] = None) -> Dict[str, Any]:
        """Creates a new journal entry and runs the full AI emotion analysis pipeline."""
        if not title or not content:
            raise ValueError("Title and content are required.")

        parsed_date = date.today()
        if entry_date:
            try:
                parsed_date = datetime.strptime(str(entry_date), "%Y-%m-%d").date()
            except ValueError:
                parsed_date = date.today()

        # 1. Create Journal Entry
        entry = JournalEntry(
            user_id=user_id,
            title=title.strip(),
            content=content.strip(),
            tags=tags.strip(),
            entry_date=parsed_date
        )
        db.session.add(entry)
        db.session.flush()  # Generates entry.id

        # 2. Run AI Analysis Pipeline
        ai_res = ai_service.analyze_full_entry(content)

        # 3. Create Emotion Log
        emotion_log = EmotionLog(
            journal_id=entry.id,
            user_id=user_id,
            primary_emotion=ai_res["primary_emotion"],
            emotion_confidence=ai_res["emotion_confidence"],
            all_emotions=ai_res["all_emotions"],
            sentiment_compound=ai_res["sentiment"]["compound"],
            sentiment_positive=ai_res["sentiment"]["positive"],
            sentiment_neutral=ai_res["sentiment"]["neutral"],
            sentiment_negative=ai_res["sentiment"]["negative"],
            keywords=ai_res["keywords"],
            coping_suggestion=ai_res["coping_suggestion"]
        )
        db.session.add(emotion_log)
        db.session.commit()

        return entry.to_dict(include_analysis=True)

    @staticmethod
    def get_entries(
        user_id: int,
        search_query: str = "",
        emotion_filter: str = "",
        sentiment_filter: str = "",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sort_by: str = "date_desc"
    ) -> List[Dict[str, Any]]:
        """Retrieves and filters journal entries for a given user."""
        query = JournalEntry.query.filter_by(user_id=user_id)

        # Text search in title or content
        if search_query and search_query.strip():
            term = f"%{search_query.strip()}%"
            query = query.filter((JournalEntry.title.ilike(term)) | (JournalEntry.content.ilike(term)) | (JournalEntry.tags.ilike(term)))

        # Date range filter
        if start_date:
            try:
                s_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(JournalEntry.entry_date >= s_date)
            except ValueError:
                pass

        if end_date:
            try:
                e_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(JournalEntry.entry_date <= e_date)
            except ValueError:
                pass

        # Emotion filter
        if emotion_filter and emotion_filter.lower() != "all":
            query = query.join(EmotionLog, JournalEntry.id == EmotionLog.journal_id).filter(
                func.lower(EmotionLog.primary_emotion) == emotion_filter.lower()
            )

        # Sentiment filter
        if sentiment_filter and sentiment_filter.lower() != "all":
            sf = sentiment_filter.lower()
            if not any(isinstance(c, EmotionLog) for c in query.column_descriptions):
                query = query.join(EmotionLog, JournalEntry.id == EmotionLog.journal_id)
            if sf == "positive":
                query = query.filter(EmotionLog.sentiment_compound >= 0.05)
            elif sf == "negative":
                query = query.filter(EmotionLog.sentiment_compound <= -0.05)
            elif sf == "neutral":
                query = query.filter(EmotionLog.sentiment_compound > -0.05, EmotionLog.sentiment_compound < 0.05)

        # Sorting
        if sort_by == "date_asc":
            query = query.order_by(asc(JournalEntry.entry_date), asc(JournalEntry.id))
        else:
            query = query.order_by(desc(JournalEntry.entry_date), desc(JournalEntry.id))

        entries = query.all()
        return [e.to_dict(include_analysis=True) for e in entries]

    @staticmethod
    def get_entry_by_id(entry_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single journal entry ensuring ownership."""
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return None
        return entry.to_dict(include_analysis=True)

    @staticmethod
    def update_entry(
        entry_id: int,
        user_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[str] = None,
        entry_date: Optional[str] = None,
        reanalyze: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Updates an existing journal entry and refreshes emotion analysis if content changed."""
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return None

        content_changed = False
        if title is not None:
            entry.title = title.strip()
        if content is not None:
            if entry.content != content.strip():
                content_changed = True
            entry.content = content.strip()
        if tags is not None:
            entry.tags = tags.strip()
        if entry_date:
            try:
                entry.entry_date = datetime.strptime(str(entry_date), "%Y-%m-%d").date()
            except ValueError:
                pass

        if (content_changed or reanalyze) and entry.content:
            ai_res = ai_service.analyze_full_entry(entry.content)
            if entry.emotion_log:
                entry.emotion_log.primary_emotion = ai_res["primary_emotion"]
                entry.emotion_log.emotion_confidence = ai_res["emotion_confidence"]
                entry.emotion_log.all_emotions = ai_res["all_emotions"]
                entry.emotion_log.sentiment_compound = ai_res["sentiment"]["compound"]
                entry.emotion_log.sentiment_positive = ai_res["sentiment"]["positive"]
                entry.emotion_log.sentiment_neutral = ai_res["sentiment"]["neutral"]
                entry.emotion_log.sentiment_negative = ai_res["sentiment"]["negative"]
                entry.emotion_log.keywords = ai_res["keywords"]
                entry.emotion_log.coping_suggestion = ai_res["coping_suggestion"]
            else:
                emotion_log = EmotionLog(
                    journal_id=entry.id,
                    user_id=user_id,
                    primary_emotion=ai_res["primary_emotion"],
                    emotion_confidence=ai_res["emotion_confidence"],
                    all_emotions=ai_res["all_emotions"],
                    sentiment_compound=ai_res["sentiment"]["compound"],
                    sentiment_positive=ai_res["sentiment"]["positive"],
                    sentiment_neutral=ai_res["sentiment"]["neutral"],
                    sentiment_negative=ai_res["sentiment"]["negative"],
                    keywords=ai_res["keywords"],
                    coping_suggestion=ai_res["coping_suggestion"]
                )
                db.session.add(emotion_log)

        db.session.commit()
        return entry.to_dict(include_analysis=True)

    @staticmethod
    def delete_entry(entry_id: int, user_id: int) -> bool:
        """Deletes a journal entry belonging to the user."""
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return False
        db.session.delete(entry)
        db.session.commit()
        return True

    @staticmethod
    def export_journal_csv(user_id: int) -> str:
        """
        Exports user's journal entries as CSV with exact columns:
        Date, Emotion, Sentiment, Journal, Confidence
        """
        entries = JournalEntry.query.filter_by(user_id=user_id).order_by(asc(JournalEntry.entry_date), asc(JournalEntry.id)).all()

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Exact columns requested: Date, Emotion, Sentiment, Journal, Confidence
        writer.writerow(["Date", "Emotion", "Sentiment", "Journal", "Confidence"])

        for e in entries:
            elog = e.emotion_log
            date_val = e.entry_date.isoformat() if e.entry_date else ""
            emotion_val = (elog.primary_emotion.capitalize() if elog and elog.primary_emotion else "Neutral")
            sentiment_val = (elog.get_sentiment_label() if elog else "Neutral")
            journal_val = (e.content or "").replace("\r\n", " ").replace("\n", " ").strip()
            confidence_val = f"{round((elog.emotion_confidence or 0.0) * 100, 1)}%" if elog else "0.0%"

            writer.writerow([
                date_val,
                emotion_val,
                sentiment_val,
                journal_val,
                confidence_val
            ])

        return output.getvalue()

    @staticmethod
    def export_csv_data(user_id: int, format_type: str = "standard") -> str:
        """Exports all journal entries and AI analysis for a user as a CSV formatted string."""
        if format_type in ["journal", "simple", "custom"]:
            return JournalService.export_journal_csv(user_id)

        entries = JournalEntry.query.filter_by(user_id=user_id).order_by(asc(JournalEntry.entry_date)).all()

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Header row
        writer.writerow([
            "Entry ID",
            "Date",
            "Title",
            "Content",
            "Tags",
            "Primary Emotion",
            "Emotion Confidence",
            "Sentiment Label",
            "Sentiment Compound",
            "Positive Score",
            "Neutral Score",
            "Negative Score",
            "Top Keywords",
            "AI Coping Suggestion"
        ])

        for e in entries:
            elog = e.emotion_log
            keywords_str = ""
            if elog and elog.keywords:
                try:
                    kw_data = elog.keywords if isinstance(elog.keywords, list) else json.loads(elog.keywords)
                    keywords_str = ", ".join([k.get("keyword", "") for k in kw_data])
                except Exception:
                    keywords_str = str(elog.keywords)

            writer.writerow([
                e.id,
                e.entry_date.isoformat() if e.entry_date else "",
                e.title,
                e.content.replace("\n", " "),
                e.tags or "",
                elog.primary_emotion if elog else "N/A",
                round(elog.emotion_confidence, 4) if elog else 0.0,
                elog.get_sentiment_label() if elog else "N/A",
                round(elog.sentiment_compound, 4) if elog else 0.0,
                round(elog.sentiment_positive, 4) if elog else 0.0,
                round(elog.sentiment_neutral, 4) if elog else 0.0,
                round(elog.sentiment_negative, 4) if elog else 0.0,
                keywords_str,
                elog.coping_suggestion.replace("\n", " ") if elog and elog.coping_suggestion else ""
            ])

        return output.getvalue()

    @staticmethod
    def get_user_entries(
        user_id: int,
        search: str = "",
        emotion: str = "",
        sentiment: str = "",
        sort_by: str = "date_desc",
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Retrieves user's journal entries with search, emotion filter, sorting, and pagination."""
        all_entries = JournalService.get_entries(
            user_id=user_id,
            search_query=search,
            emotion_filter=emotion,
            sentiment_filter=sentiment,
            sort_by=sort_by
        )
        # Add convenient top-level fields for REST clients
        for entry in all_entries:
            analysis = entry.get("analysis") or {}
            entry["emotion"] = analysis.get("primary_emotion", "Neutral")
            entry["sentiment"] = analysis.get("sentiment_label", "Neutral")
            entry["journal_text"] = entry.get("content", "")

        total = len(all_entries)
        if per_page and per_page > 0:
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paged_entries = all_entries[start_idx:end_idx]
            pages = (total + per_page - 1) // per_page if total > 0 else 1
        else:
            paged_entries = all_entries
            pages = 1

        return {
            "entries": paged_entries,
            "total": total,
            "page": page,
            "pages": pages
        }
