"""
MoodMentor Backend Route Blueprints.
Exposes modular routes for Authentication, Journal, Emotion Analysis, Insights, and REST APIs.
"""
from backend.controllers.auth_controller import auth_bp
from backend.controllers.journal_controller import journal_bp
from backend.controllers.emotion_controller import emotion_bp
from backend.controllers.analytics_controller import analytics_bp
from backend.controllers.user_controller import user_bp
from backend.controllers.rest_controller import rest_bp

__all__ = [
    "auth_bp",
    "journal_bp",
    "emotion_bp",
    "analytics_bp",
    "user_bp",
    "rest_bp"
]
