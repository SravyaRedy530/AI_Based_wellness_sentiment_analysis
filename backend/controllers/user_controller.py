from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.database import db
from backend.models.user import User
from backend.utils.helpers import success_response, error_response

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Retrieves user profile details and settings."""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)
    return success_response(data={"user": user.to_dict()})


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Updates user personal details, email, preferred support style, and theme.
    All fields are securely persisted in MySQL.
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)

    data = request.get_json() or {}
    full_name = data.get("full_name") or data.get("fullname")
    email = data.get("email")
    preferred_support_style = data.get("preferred_support_style")
    theme = data.get("theme")
    bio = data.get("bio")
    wellness_goal = data.get("wellness_goal")

    # 1. Update Full Name
    if full_name is not None and full_name.strip():
        user.fullname = full_name.strip()

    # 2. Update Email (with duplicate & format check)
    if email is not None and email.strip():
        clean_email = email.strip().lower()
        if clean_email != user.email:
            # Validate format
            import re
            email_regex = r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
            if ".." in clean_email or not re.match(email_regex, clean_email):
                return error_response("Please enter a valid email address.", 400)

            # Check duplicate email in MySQL
            existing = User.query.filter(User.email == clean_email, User.id != user_id).first()
            if existing:
                return error_response("This email is already in use by another account.", 409)

            user.email = clean_email

    # 3. Update Preferred Support Style
    if preferred_support_style is not None:
        user.preferred_support_style = preferred_support_style.strip()

    # 4. Update Theme
    if theme is not None:
        user.theme = theme.strip()

    # 5. Update Bio & Wellness Goal
    if bio is not None:
        user.bio = bio.strip()
    if wellness_goal is not None:
        user.wellness_goal = wellness_goal.strip()

    try:
        db.session.commit()
        return success_response(data={"user": user.to_dict()}, message="Profile updated successfully in MySQL!")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Profile update failed: {str(e)}", 500)


@user_bp.route("/password", methods=["PUT"])
@jwt_required()
def change_password():
    """Updates user account password."""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)

    data = request.get_json() or {}
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not current_password or not new_password:
        return error_response("Current password and new password are required.", 400)

    if not user.check_password(current_password):
        return error_response("Incorrect current password.", 401)

    if len(new_password) < 6:
        return error_response("New password must be at least 6 characters long.", 400)

    try:
        user.set_password(new_password)
        db.session.commit()
        return success_response(message="Password changed successfully!")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to change password: {str(e)}", 500)


@user_bp.route("/delete-account", methods=["DELETE"])
@jwt_required()
def delete_account():
    """
    Permanently deletes user account and all associated journal entries and emotion logs.
    Requires password re-confirmation for safety.
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)

    data = request.get_json() or {}
    password = data.get("password", "")

    if not password:
        return error_response("Please confirm your password to delete your account.", 400)

    if not user.check_password(password):
        return error_response("Incorrect password. Account deletion aborted.", 401)

    try:
        # Cascade deletion handles journal_entries and emotion_logs
        db.session.delete(user)
        db.session.commit()
        return success_response(message="Account and all associated records deleted permanently.")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Account deletion failed: {str(e)}", 500)
