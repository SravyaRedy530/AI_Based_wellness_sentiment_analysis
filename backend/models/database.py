import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text

db = SQLAlchemy()
logger = logging.getLogger(__name__)


def init_db(app):
    """
    Initializes SQLAlchemy database connection.
    Attempts MySQL connection first. If connection fails and fallback is enabled,
    switches gracefully to SQLite so the application is immediately operational.
    """
    mysql_uri = app.config.get("MYSQL_URI")
    sqlite_uri = app.config.get("SQLITE_URI")
    use_fallback = app.config.get("USE_SQLITE_FALLBACK", True)

    db_connected = False

    # Attempt MySQL first
    try:
        engine = create_engine(mysql_uri, connect_args={"connect_timeout": 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        app.config["SQLALCHEMY_DATABASE_URI"] = mysql_uri
        app.config["ACTIVE_DB_TYPE"] = "MySQL"
        db_connected = True
        logger.info("Successfully connected to MySQL database: %s", app.config.get('DB_NAME'))
        print(f"[MoodMentor DB] Connected successfully to MySQL ({app.config.get('DB_NAME')})")
    except Exception as ex:
        logger.warning("Could not connect to MySQL: %s", ex)
        if use_fallback:
            app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_uri
            app.config["ACTIVE_DB_TYPE"] = "SQLite"
            db_connected = True
            logger.info("Falling back to local SQLite database: %s", sqlite_uri)
            print("[MoodMentor DB] MySQL not accessible with current credentials.")
            print("[MoodMentor DB] Activated SQLite fallback (instance/moodmentor.db).")
            print("[MoodMentor DB] To connect to MySQL, update DB_PASSWORD in .env file.")
        else:
            raise ConnectionError(f"Failed to connect to MySQL database: {ex}")

    db.init_app(app)

    with app.app_context():
        # Create all tables if they don't already exist
        db.create_all()
        print(f"[MoodMentor DB] Tables initialized successfully on {app.config['ACTIVE_DB_TYPE']}.")
