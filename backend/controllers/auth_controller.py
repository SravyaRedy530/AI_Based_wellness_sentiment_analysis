import re
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from sqlalchemy.exc import IntegrityError
from backend.models.database import db
from backend.models.user import User, TokenBlocklist
from backend.utils.helpers import success_response, error_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Strict RFC-compliant email validation regex
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"


def validate_email_format(email: str) -> bool:
    """Validates email format strictly disallowing consecutive dots and malformed domains."""
    if not email or len(email) > 120 or ".." in email:
        return False
    return bool(re.match(EMAIL_REGEX, email))


# -------------------------------------------------------------------
# 1. Register Endpoint
# -------------------------------------------------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registers a new user into the MySQL Users table.
    - Fields: fullname, email, password
    - Email validation
    - Duplicate email prevention (pre-check + MySQL UNIQUE constraint)
    - Password hashing with bcrypt
    - JWT token issuance
    """
    data = request.get_json() or {}

    # Extract fields (supporting fullname / full_name for compatibility)
    fullname = (data.get("fullname") or data.get("full_name") or data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password", "")
    username = (data.get("username") or email.split("@")[0] if email else "").strip()

    # 1. Validate required fields
    if not fullname:
        return error_response("Full name is required.", 400)

    if len(fullname) < 2:
        return error_response("Full name must be at least 2 characters.", 400)

    if not email:
        return error_response("Email address is required.", 400)

    # 2. Strict Email validation
    if not validate_email_format(email):
        return error_response("Please enter a valid email address (e.g., user@example.com).", 400)

    # 3. Password validation
    if not password:
        return error_response("Password is required.", 400)

    if len(password) < 6:
        return error_response("Password must be at least 6 characters long.", 400)

    # 4. Duplicate email prevention (Database check)
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return error_response("Email is already registered. Please log in or use a different email.", 409)

    # 5. Password Hashing & Insertion
    try:
        user = User(
            fullname=fullname,
            email=email,
            username=username
        )
        user.set_password(password)  # Salted bcrypt hash
        db.session.add(user)
        db.session.commit()

        # 6. Issue JWT Access Token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "email": user.email,
                "fullname": user.fullname
            }
        )

        return success_response(
            data={
                "user": user.to_dict(),
                "access_token": access_token
            },
            message="Account registered successfully!",
            status_code=201
        )

    except IntegrityError:
        db.session.rollback()
        # Catches concurrent race-condition duplicate email on MySQL UNIQUE index
        return error_response("Email is already registered. Please use another email.", 409)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Registration failed: {str(e)}", 500)


# -------------------------------------------------------------------
# 2. Login Endpoint
# -------------------------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticates user credentials against stored bcrypt hash in MySQL.
    - Fields: email (or identifier), password
    - Issues JWT access token upon successful verification
    """
    data = request.get_json() or {}
    email = (data.get("email") or data.get("identifier") or "").strip().lower()
    password = data.get("password", "")

    if not email:
        return error_response("Email is required.", 400)

    if not password:
        return error_response("Password is required.", 400)

    # Find user by email (or username as fallback)
    user = User.query.filter(
        (User.email == email) | (User.username == email)
    ).first()

    # Verify password hash
    if not user or not user.check_password(password):
        return error_response("Invalid email or password. Please verify your credentials.", 401)

    # Generate JWT token with user claims
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "email": user.email,
            "fullname": user.fullname
        }
    )

    return success_response(
        data={
            "user": user.to_dict(),
            "access_token": access_token
        },
        message="Login successful!"
    )


# -------------------------------------------------------------------
# 3. Logout Endpoint (JWT Token Revocation)
# -------------------------------------------------------------------
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logs out the authenticated user by adding the token's unique JTI
    to the MySQL TokenBlocklist table.
    Any subsequent request with this token will be blocked with 401 Unauthorized.
    """
    try:
        jwt_payload = get_jwt()
        jti = jwt_payload.get("jti")

        if jti:
            # Store revoked token identifier in MySQL
            revoked_token = TokenBlocklist(jti=jti)
            db.session.add(revoked_token)
            db.session.commit()

        return success_response(message="Logged out successfully. Token has been revoked.")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Logout failed: {str(e)}", 500)


# -------------------------------------------------------------------
# 4. Current User Profile Endpoint
# -------------------------------------------------------------------
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Returns the authenticated user's details."""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)
    return success_response(data={"user": user.to_dict()})
