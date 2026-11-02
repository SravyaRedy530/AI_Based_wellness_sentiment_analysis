from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.analytics_service import AnalyticsService
from backend.utils.helpers import success_response, error_response

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard_stats():
    """Retrieves aggregated statistics and recent activity for the user dashboard."""
    user_id = int(get_jwt_identity())
    try:
        stats = AnalyticsService.get_dashboard_stats(user_id)
        return success_response(data={"dashboard": stats})
    except Exception as e:
        return error_response(f"Failed to load dashboard statistics: {str(e)}", 500)


@analytics_bp.route("/insights", methods=["GET"])
@jwt_required()
def emotion_insights():
    """Retrieves deep emotional trends and chart-ready datasets."""
    user_id = int(get_jwt_identity())
    try:
        insights = AnalyticsService.get_emotion_insights(user_id)
        return success_response(data={"insights": insights})
    except Exception as e:
        return error_response(f"Failed to load emotion insights: {str(e)}", 500)
