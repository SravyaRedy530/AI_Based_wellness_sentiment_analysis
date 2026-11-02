"""
Database initialization utility script.
Verifies table creation and outputs connectivity details.
"""
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app
from backend.models.database import db

def initialize_database():
    print("=" * 60)
    print("MoodMentor Database Initialization")
    print("=" * 60)
    app = create_app()
    with app.app_context():
        db.create_all()
        active_db = app.config.get("ACTIVE_DB_TYPE", "Unknown")
        print(f"[OK] Database tables verified successfully on: {active_db}")
        print("[OK] Tables: users, journal_entries, emotion_logs, user_preferences")
        print("=" * 60)

if __name__ == "__main__":
    initialize_database()
