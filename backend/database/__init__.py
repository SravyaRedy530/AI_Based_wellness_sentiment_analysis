"""
MoodMentor Database Module.
Exposes database session, connection lifecycle, and initialization utilities.
"""
from backend.models.database import db, init_db, check_db_connection

__all__ = ["db", "init_db", "check_db_connection"]
