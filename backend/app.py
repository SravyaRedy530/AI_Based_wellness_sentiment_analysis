import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.models.database import db, init_db
from backend.controllers.auth_controller import auth_bp
from backend.controllers.journal_controller import journal_bp
from backend.controllers.emotion_controller import emotion_bp
from backend.controllers.analytics_controller import analytics_bp
from backend.controllers.user_controller import user_bp
from backend.controllers.rest_controller import rest_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Flask Application Factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for frontend and API communication
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize Database
    init_db(app)

    # Initialize JWT Manager
    jwt = JWTManager(app)

    # JWT Blocklist Loader (Checks if token was revoked via logout)
    from backend.models.user import TokenBlocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload.get("jti")
        if not jti:
            return False
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "This session has been logged out. Please sign in again.",
            "error": "token_revoked"
        }), 401

    # Custom JWT Error Handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({
            "success": False,
            "message": "Authorization token required. Please log in.",
            "error": "token_missing"
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({
            "success": False,
            "message": "Invalid token. Please log in again.",
            "error": "token_invalid"
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "Token has expired. Please log in again.",
            "error": "token_expired"
        }), 401

    # Register Blueprints
    app.register_blueprint(rest_bp)  # Root REST routes (/register, /login, /analyze, /journal, /insights, /profile, /export, /account)
    app.register_blueprint(auth_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(emotion_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(user_bp)

    # Health Check Endpoint
    @app.route("/health", methods=["GET"])
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "app_name": "MoodMentor - AI Emotion Journal API",
            "database_type": app.config.get("ACTIVE_DB_TYPE", "Unknown"),
            "ai_model": app.config.get("HF_EMOTION_MODEL"),
            "version": "1.0.0"
        }), 200

    # Global 404 Handler
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "success": False,
            "message": "Endpoint not found."
        }), 404

    # Global 500 Handler
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Internal server error occurred."
        }), 500

    return app


# Application entry point
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print(f"[START] MoodMentor Backend running on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
