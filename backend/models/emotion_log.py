import json
from datetime import datetime, timezone
from backend.models.database import db


def utc_now():
    return datetime.now(timezone.utc)


class EmotionLog(db.Model):
    """EmotionLog Model representing AI-generated emotional & sentiment analysis."""
    __tablename__ = "emotion_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    journal_id = db.Column(db.Integer, db.ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    primary_emotion = db.Column(db.String(50), nullable=False)
    emotion_confidence = db.Column(db.Float, nullable=False, default=0.0)
    all_emotions = db.Column(db.JSON, nullable=True)
    
    sentiment_compound = db.Column(db.Float, nullable=False, default=0.0)
    sentiment_positive = db.Column(db.Float, nullable=False, default=0.0)
    sentiment_neutral = db.Column(db.Float, nullable=False, default=0.0)
    sentiment_negative = db.Column(db.Float, nullable=False, default=0.0)
    
    keywords = db.Column(db.JSON, nullable=True)
    coping_suggestion = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        """Serializes emotion log model to dictionary."""
        # Handle JSON decoding for SQLite / MySQL consistency
        emotions_data = self.all_emotions
        if isinstance(emotions_data, str):
            try:
                emotions_data = json.loads(emotions_data)
            except Exception:
                pass

        keywords_data = self.keywords
        if isinstance(keywords_data, str):
            try:
                keywords_data = json.loads(keywords_data)
            except Exception:
                pass

        from backend.services.ai_service import ai_service
        suggs_bundle = ai_service.generate_personalized_suggestions(self.primary_emotion)

        return {
            "id": self.id,
            "journal_id": self.journal_id,
            "user_id": self.user_id,
            "primary_emotion": self.primary_emotion.capitalize(),
            "emotion": self.primary_emotion.capitalize(),
            "emotion_confidence": round(float(self.emotion_confidence), 4),
            "confidence": round(float(self.emotion_confidence), 4),
            "confidence_percentage": round(float(self.emotion_confidence) * 100, 1),
            "all_emotions": emotions_data or [],
            "sentiment": {
                "compound": round(float(self.sentiment_compound), 4),
                "positive": round(float(self.sentiment_positive), 4),
                "neutral": round(float(self.sentiment_neutral), 4),
                "negative": round(float(self.sentiment_negative), 4),
                "label": self.get_sentiment_label()
            },
            "sentiment_label": self.get_sentiment_label(),
            "sentiment_score": round(float(self.sentiment_compound), 4),
            "keywords": keywords_data or [],
            "suggestions": suggs_bundle["simple"],
            "personalized_suggestions": suggs_bundle["detailed"],
            "coping_suggestion": self.coping_suggestion or "",
            "recommendations": self.coping_suggestion or "",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def get_sentiment_label(self) -> str:
        """Categorizes compound score into Positive, Neutral, or Negative."""
        if self.sentiment_compound >= 0.05:
            return "Positive"
        elif self.sentiment_compound <= -0.05:
            return "Negative"
        else:
            return "Neutral"

    def __repr__(self):
        return f"<EmotionLog journal={self.journal_id} emotion={self.primary_emotion}>"
