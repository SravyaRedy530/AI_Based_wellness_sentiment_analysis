from datetime import date
import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.ai_service import ai_service
from backend.services.journal_service import JournalService
from backend.utils.helpers import success_response, error_response

logger = logging.getLogger(__name__)
emotion_bp = Blueprint("emotion", __name__, url_prefix="/api/emotion")


@emotion_bp.route("/analyze", methods=["POST"])
@jwt_required(optional=True)
def analyze_text():
    """
    Live Emotion Analysis Endpoint.
    Analyzes raw text using DistilBERT, VADER, and KeyBERT.
    Generates personalized suggestions (Joy, Fear, Sadness, Anger, Love, Surprise, Neutral).
    AUTOMATICALLY saves the analysis and journal text to MySQL if authenticated.
    """
    data = request.get_json() or {}
    text = data.get("text", "").strip()

    if not text:
        return error_response("Please enter some text to analyze.", 400)

    try:
        # 1. Perform Multimodal Analysis & Personalized Suggestions
        analysis_result = ai_service.analyze_full_entry(text)

        # 2. Automatically save into MySQL Journal if user is authenticated
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
            except Exception as save_err:
                logger.warning(f"Auto-save to MySQL failed: {save_err}")

        response_payload = {
            "success": True,
            "message": "Analysis completed and automatically saved to My Journal!" if saved_entry else "Analysis completed successfully!",
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
        }
        return response_payload, 200
    except Exception as e:
        return error_response(f"Analysis failed: {str(e)}", 500)


@emotion_bp.route("/suggestions", methods=["GET", "POST"])
def get_personalized_suggestions_endpoint():
    """
    Dedicated endpoint returning personalized suggestions as JSON.
    - If Joy: Celebrate achievements, Share appreciation, Take photos
    - If Fear: Breathing exercise, Grounding, Positive affirmations, Mindfulness
    - If Sadness: Music, Walk, Friend, Journaling
    Also supports Anger, Love, Surprise, Neutral.
    """
    if request.method == "POST":
        body = request.get_json() or {}
        emotion = body.get("emotion") or body.get("primary_emotion") or ""
    else:
        emotion = request.args.get("emotion") or request.args.get("primary_emotion") or ""

    if not emotion:
        return error_response("Please specify an emotion (e.g. Joy, Fear, Sadness).", 400)

    bundle = ai_service.generate_personalized_suggestions(emotion)
    suggestions_list = bundle.get("simple", [])
    detailed_list = bundle.get("detailed", [])

    return {
        "success": True,
        "emotion": emotion.capitalize(),
        "suggestions": suggestions_list,
        "personalized_suggestions": suggestions_list,
        "detailed_suggestions": detailed_list,
        "data": {
            "emotion": emotion.capitalize(),
            "suggestions": suggestions_list,
            "personalized_suggestions": suggestions_list,
            "detailed_suggestions": detailed_list
        }
    }, 200
