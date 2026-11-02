from datetime import datetime, date, timezone
from backend.models.database import db


def utc_now():
    return datetime.now(timezone.utc)


class JournalEntry(db.Model):
    """JournalEntry Model representing user journal entries."""
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=True, default="")
    entry_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # One-to-one relationship with EmotionLog
    emotion_log = db.relationship(
        "EmotionLog",
        backref="journal_entry",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def to_dict(self, include_analysis=True):
        """Serializes journal entry model to dictionary."""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "tags": [t.strip() for t in self.tags.split(",") if t.strip()] if self.tags else [],
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_analysis:
            data["analysis"] = self.emotion_log.to_dict() if self.emotion_log else None
        return data

    def __repr__(self):
        return f"<JournalEntry {self.id}: {self.title}>"
