import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "moodmentor-default-secret-key-2026")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "moodmentor-jwt-secret-key-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Database Configuration
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "moodmentor_db")
    USE_SQLITE_FALLBACK = os.getenv("USE_SQLITE_FALLBACK", "True").lower() in ("true", "1", "yes")

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # Primary MySQL Connection URI
    if DB_PASSWORD:
        MYSQL_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    else:
        MYSQL_URI = f"mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

    # SQLite Fallback URI
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    SQLITE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'moodmentor.db')}"

    # Default to MySQL URI (Database initialization checks connectivity)
    SQLALCHEMY_DATABASE_URI = MYSQL_URI

    # AI Model Configurations
    HF_EMOTION_MODEL = os.getenv("HF_EMOTION_MODEL", "bhadresh-savani/distilbert-base-uncased-emotion")
    
    # Server configuration
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
