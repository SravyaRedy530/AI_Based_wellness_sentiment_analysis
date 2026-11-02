"""
Unified REST APIs for MoodMentor.
Exposes standard RESTful routes:
- POST /register
- POST /login
- POST /analyze
- GET /journal
- DELETE /journal/<id>
- GET /insights
- GET /profile
- PUT /profile
- GET /export
- DELETE /account

All endpoints return JSON responses and adhere strictly to REST conventions.
"""
from datetime import date
import re
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from sqlalchemy.exc import IntegrityError
from backend.models.database import db
from backend.models.user import User
from backend.services.ai_service import ai_service
from backend.services.journal_service import JournalService
from backend.services.analytics_service import AnalyticsService
from backend.utils.helpers import success_response, error_response

rest_bp = Blueprint("rest_api", __name__)

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"


def is_valid_email(email: str) -> bool:
    if not email or len(email) > 120 or ".." in email:
        return False
    return bool(re.match(EMAIL_REGEX, email))


# ============================================================================
# 1. POST /register
# ============================================================================
@rest_bp.route("/register", methods=["POST"])
def register():
    """
    Registers a new user in MySQL.
    HTTP 201 Created on success.
    HTTP 400 Bad Request on invalid input.
    HTTP 409 Conflict on duplicate email.
    """
    data = request.get_json() or {}
    fullname = (data.get("fullname") or data.get("full_name") or data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password", "")
    username = (data.get("username") or email.split("@")[0] if email else "").strip()

    if not fullname:
        return error_response("Full Name is required.", 400)
    if len(fullname) < 2:
        return error_response("Full Name must be at least 2 characters.", 400)
    if not email:
        return error_response("Email Address is required.", 400)
    if not is_valid_email(email):
        return error_response("Please enter a valid email address.", 400)
    if not password or len(password) < 6:
        return error_response("Password must be at least 6 characters.", 400)

    # Check for existing email in MySQL
    if User.query.filter_by(email=email).first():
        return error_response("Email is already registered. Please log in or use another email.", 409)

    try:
        user = User(
            fullname=fullname,
            email=email,
            username=username,
            wellness_goal=data.get("wellness_goal", "Mindfulness & Stress Reduction"),
            preferred_support_style=data.get("preferred_support_style", "Gentle & Compassionate"),
            theme=data.get("theme", "Light Mode")
        )
        user.set_password(password)  # Salted bcrypt hash
        db.session.add(user)
        db.session.commit()

        # Issue JWT Access Token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"email": user.email, "fullname": user.fullname}
        )

        user_dict = user.to_dict()
        return jsonify({
            "success": True,
            "message": "User registered successfully!",
            "token": access_token,
            "access_token": access_token,
            "user": user_dict,
            "data": {
                "user": user_dict,
                "token": access_token,
                "access_token": access_token
            }
        }), 201

    except IntegrityError:
        db.session.rollback()
        return error_response("Email is already registered. Please use another email.", 409)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Registration failed: {str(e)}", 500)


# ============================================================================
# 2. POST /login
# ============================================================================
@rest_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticates user credentials against salted bcrypt hash in MySQL.
    HTTP 200 OK on success.
    HTTP 401 Unauthorized on invalid credentials.
    """
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return error_response("Email and password are required.", 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error_response("Invalid email or password.", 401)

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"email": user.email, "fullname": user.fullname}
    )

    user_dict = user.to_dict()
    return jsonify({
        "success": True,
        "message": "Login successful!",
        "token": access_token,
        "access_token": access_token,
        "user": user_dict,
        "data": {
            "user": user_dict,
            "token": access_token,
            "access_token": access_token
        }
    }), 200


# ============================================================================
# 3. POST /analyze
# ============================================================================
@rest_bp.route("/analyze", methods=["POST"])
@jwt_required(optional=True)
def analyze():
    """
    Performs AI emotion and sentiment analysis on submitted text.
    Automatically saves to MySQL journal if user is authenticated.
    Generates personalized suggestions for Joy, Fear, Sadness, etc.
    HTTP 200 OK with JSON response.
    """
    data = request.get_json() or {}
    text = data.get("text", "").strip()

    if not text:
        return error_response("Please enter some text to analyze.", 400)

    try:
        analysis_result = ai_service.analyze_full_entry(text)

        # Auto-save to MySQL if authenticated
        saved_entry = None
        user_identity = get_jwt_identity()

        if user_identity:
            try:
                user_id = int(user_identity)
                clean_title = (text[:40] + "...") if len(text) > 40 else text
                saved_entry = JournalService.create_entry(
                    user_id=user_id,
                    title=f"{analysis_result['emotion']} Reflection: {clean_title}",
                    content=text,
                    tags=f"{analysis_result['emotion'].lower()}, auto-saved",
                    entry_date=date.today().isoformat()
                )
            except Exception:
                saved_entry = None

        return jsonify({
            "success": True,
            "message": "Analysis completed successfully!",
            "emotion": analysis_result["emotion"],
            "primary_emotion": analysis_result["emotion"],
            "sentiment": analysis_result["sentiment_label"],
            "sentiment_label": analysis_result["sentiment_label"],
            "sentiment_score": analysis_result["sentiment_score"],
            "confidence": analysis_result["confidence"],
            "confidence_percentage": analysis_result["confidence_percentage"],
            "suggestions": analysis_result["suggestions"],
            "personalized_suggestions": analysis_result["suggestions"],
            "detailed_suggestions": analysis_result["personalized_suggestions"],
            "recommendations": analysis_result["recommendations"],
            "activities": analysis_result["activities"],
            "auto_saved": saved_entry is not None,
            "saved_entry": saved_entry,
            "data": {
                "emotion": analysis_result["emotion"],
                "primary_emotion": analysis_result["emotion"],
                "sentiment": analysis_result["sentiment_label"],
                "sentiment_label": analysis_result["sentiment_label"],
                "sentiment_score": analysis_result["sentiment_score"],
                "confidence": analysis_result["confidence"],
                "confidence_percentage": analysis_result["confidence_percentage"],
                "suggestions": analysis_result["suggestions"],
                "personalized_suggestions": analysis_result["suggestions"],
                "detailed_suggestions": analysis_result["personalized_suggestions"],
                "recommendations": analysis_result["recommendations"],
                "activities": analysis_result["activities"],
                "auto_saved": saved_entry is not None,
                "saved_entry": saved_entry,
                "analysis": analysis_result
            }
        }), 200

    except Exception as e:
        return error_response(f"Analysis failed: {str(e)}", 500)


# ============================================================================
# 4. GET /journal
# ============================================================================
@rest_bp.route("/journal", methods=["GET"])
@jwt_required()
def get_journal():
    """
    Retrieves user's journal entries from MySQL.
    Supports filtering by keyword search, emotion, and sorting by latest.
    HTTP 200 OK.
    """
    user_id = int(get_jwt_identity())
    search = request.args.get("search", "")
    emotion = request.args.get("emotion", "")
    sentiment = request.args.get("sentiment", "")
    sort_by = request.args.get("sort", request.args.get("sort_by", "date_desc"))
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    try:
        entries_data = JournalService.get_user_entries(
            user_id=user_id,
            search=search,
            emotion=emotion,
            sentiment=sentiment,
            sort_by=sort_by,
            page=page,
            per_page=per_page
        )
        return jsonify({
            "success": True,
            "total": entries_data["total"],
            "entries": entries_data["entries"],
            "page": entries_data["page"],
            "pages": entries_data["pages"],
            "data": entries_data
        }), 200
    except Exception as e:
        return error_response(f"Failed to fetch journal entries: {str(e)}", 500)


# ============================================================================
# 5. DELETE /journal/{id}
# ============================================================================
@rest_bp.route("/journal/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_journal_entry(id: int):
    """
    Deletes specified journal entry by ID from MySQL.
    HTTP 200 OK on success.
    HTTP 404 Not Found if entry does not exist or unauthorized.
    """
    user_id = int(get_jwt_identity())
    deleted = JournalService.delete_entry(id, user_id)
    if not deleted:
        return error_response("Journal entry not found or unauthorized.", 404)

    return jsonify({
        "success": True,
        "message": f"Journal entry {id} deleted successfully."
    }), 200


# ============================================================================
# 6. GET /insights
# ============================================================================
@rest_bp.route("/insights", methods=["GET"])
@jwt_required()
def get_insights():
    """
    Retrieves Emotion Insights analytics (Plotly datasets, KPIs, Monthly Report).
    HTTP 200 OK.
    """
    user_id = int(get_jwt_identity())
    try:
        insights_data = AnalyticsService.get_emotion_insights(user_id)
        # Populate convenient aliases for Plotly visualizations and REST consumers
        insights_data["distribution"] = insights_data.get("emotion_distribution", {})
        insights_data["timeline"] = insights_data.get("sentiment_timeline", [])
        insights_data["kpis"] = {
            "total_checkins": insights_data.get("total_checkins", 0),
            "most_frequent_emotion": insights_data.get("most_frequent_emotion", "N/A"),
            "positive_percentage": insights_data.get("positive_percentage", 0.0),
            "negative_percentage": insights_data.get("negative_percentage", 0.0),
            "neutral_percentage": insights_data.get("neutral_percentage", 0.0),
            "avg_sentiment": insights_data.get("avg_sentiment", 0.0)
        }
        return jsonify({
            "success": True,
            "insights": insights_data,
            "data": {
                "insights": insights_data
            }
        }), 200
    except Exception as e:
        return error_response(f"Failed to load emotion insights: {str(e)}", 500)


# ============================================================================
# 7. GET /profile
# ============================================================================
@rest_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """
    Retrieves user profile details from MySQL.
    HTTP 200 OK.
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)

    user_dict = user.to_dict()
    return jsonify({
        "success": True,
        "user": user_dict,
        "data": {
            "user": user_dict
        }
    }), 200


# ============================================================================
# 8. PUT /profile
# ============================================================================
@rest_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Updates user profile details (Full Name, Email, Preferred Support Style, Theme) in MySQL.
    HTTP 200 OK on success.
    HTTP 409 Conflict if new email is in use by another account.
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)

    data = request.get_json() or {}
    fullname = data.get("fullname") or data.get("full_name")
    email = data.get("email")
    preferred_support_style = data.get("preferred_support_style")
    theme = data.get("theme")
    bio = data.get("bio")
    wellness_goal = data.get("wellness_goal")

    if fullname is not None and fullname.strip():
        user.fullname = fullname.strip()

    if email is not None and email.strip():
        clean_email = email.strip().lower()
        if clean_email != user.email:
            if not is_valid_email(clean_email):
                return error_response("Please enter a valid email address.", 400)
            existing = User.query.filter(User.email == clean_email, User.id != user_id).first()
            if existing:
                return error_response("Email is already in use by another account.", 409)
            user.email = clean_email

    if preferred_support_style is not None:
        user.preferred_support_style = preferred_support_style.strip()

    if theme is not None:
        user.theme = theme.strip()

    if bio is not None:
        user.bio = bio.strip()

    if wellness_goal is not None:
        user.wellness_goal = wellness_goal.strip()

    try:
        db.session.commit()
        user_dict = user.to_dict()
        return jsonify({
            "success": True,
            "message": "Profile updated successfully in MySQL!",
            "user": user_dict,
            "data": {
                "user": user_dict
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Profile update failed: {str(e)}", 500)


# ============================================================================
# 9. GET /export
# ============================================================================
@rest_bp.route("/export", methods=["GET"])
@jwt_required()
def export_journal():
    """
    Exports user's journal entries from MySQL.
    Supports standard CSV file streaming (if Accept: text/csv or format=csv)
    or JSON response.
    HTTP 200 OK.
    """
    user_id = int(get_jwt_identity())
    cols_type = request.args.get("columns", "").lower()
    format_type = "journal" if cols_type in ["journal", "simple", "5"] else "standard"
    csv_content = JournalService.export_csv_data(user_id, format_type=format_type)
    req_format = request.args.get("format", "").lower()
    accept_header = request.headers.get("Accept", "")

    # Stream as CSV file if requested via query or Accept header
    if req_format == "csv" or "text/csv" in accept_header:
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=moodmentor_journal_export.csv"}
        )

    # Return as JSON response following REST conventions
    entries = JournalService.get_user_entries(user_id, per_page=1000)["entries"]
    return jsonify({
        "success": True,
        "message": "Journal export generated successfully.",
        "total_entries": len(entries),
        "csv": csv_content,
        "entries": entries,
        "data": {
            "total_entries": len(entries),
            "csv": csv_content,
            "entries": entries
        }
    }), 200


# ============================================================================
# 10. DELETE /account
# ============================================================================
@rest_bp.route("/account", methods=["DELETE"])
@jwt_required()
def delete_account():
    """
    Permanently deletes authenticated user account and all cascading records from MySQL.
    HTTP 200 OK on success.
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)

    data = request.get_json(silent=True) or {}
    password = data.get("password")

    # If password is provided, verify it for safety
    if password and not user.check_password(password):
        return error_response("Incorrect password. Account deletion aborted.", 401)

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Account and all associated records deleted permanently from MySQL."
        }), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Account deletion failed: {str(e)}", 500)
