from datetime import datetime, timezone
import bcrypt
from backend.models.database import db


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    """
    Users Model representing registered members.
    Contains: id, fullname, email, password, created_at
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # Stores salted bcrypt hash
    username = db.Column(db.String(64), unique=True, nullable=True, index=True)
    bio = db.Column(db.Text, nullable=True, default="")
    wellness_goal = db.Column(db.String(255), nullable=True, default="Mindfulness & Stress Reduction")
    preferred_support_style = db.Column(db.String(100), nullable=True, default="Gentle & Compassionate")
    theme = db.Column(db.String(50), nullable=True, default="Light Mode")
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    journal_entries = db.relationship(
        "JournalEntry",
        backref="author",
        lazy="dynamic",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    emotion_logs = db.relationship(
        "EmotionLog",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Aliases for backward/forward compatibility
    @property
    def full_name(self):
        return self.fullname

    @full_name.setter
    def full_name(self, value):
        self.fullname = value

    @property
    def password_hash(self):
        return self.password

    @password_hash.setter
    def password_hash(self, value):
        self.password = value

    def set_password(self, raw_password: str):
        """Hashes password with bcrypt and a secure salt."""
        salt = bcrypt.gensalt(rounds=12)
        self.password = bcrypt.hashpw(raw_password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        """Verifies candidate password against stored bcrypt hash."""
        if not self.password:
            return False
        return bcrypt.checkpw(raw_password.encode("utf-8"), self.password.encode("utf-8"))

    def to_dict(self):
        """Serializes user model to dictionary (never exposing password hash)."""
        return {
            "id": self.id,
            "fullname": self.fullname,
            "full_name": self.fullname,
            "email": self.email,
            "username": self.username or self.email.split("@")[0],
            "bio": self.bio or "",
            "wellness_goal": self.wellness_goal or "Mindfulness & Stress Reduction",
            "preferred_support_style": self.preferred_support_style or "Gentle & Compassionate",
            "theme": self.theme or "Light Mode",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<User {self.id}: {self.email}>"


class TokenBlocklist(db.Model):
    """
    Stores revoked JWT tokens (JTI) for secure server-side logout.
    When a user logs out, their JWT identifier is added here.
    """
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f"<TokenBlocklist {self.jti}>"
