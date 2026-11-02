from datetime import datetime, timezone
from backend.models.database import db


def utc_now():
    return datetime.now(timezone.utc)


class Suggestion(db.Model):
    """
    Suggestions Model representing personalized wellness coping activities
    mapped to detected emotional states.
    Foreign Keys: emotion_result_id, user_id
    """
    __tablename__ = "suggestions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emotion_result_id = db.Column(
        db.Integer,
        db.ForeignKey("emotion_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    emotion = db.Column(db.String(50), nullable=False, index=True)
    suggestion_text = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(60), default="Wellness")
    icon = db.Column(db.String(20), default="✨")
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        """Serializes Suggestion record to dictionary."""
        return {
            "id": self.id,
            "emotion_result_id": self.emotion_result_id,
            "user_id": self.user_id,
            "emotion": self.emotion,
            "suggestion_text": self.suggestion_text,
            "category": self.category,
            "icon": self.icon,
            "is_completed": self.is_completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Suggestion {self.id}: {self.emotion} - {self.suggestion_text}>"
