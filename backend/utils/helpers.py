from typing import Any, Dict, Optional
from flask import jsonify


def success_response(data: Any = None, message: str = "Success", status_code: int = 200):
    """Formats a consistent JSON success response."""
    payload = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(payload), status_code


def error_response(message: str = "An error occurred", status_code: int = 400, errors: Optional[Any] = None):
    """Formats a consistent JSON error response."""
    payload = {
        "success": False,
        "message": message,
        "errors": errors
    }
    return jsonify(payload), status_code
