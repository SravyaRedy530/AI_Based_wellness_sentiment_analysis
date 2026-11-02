"""
DistilBERT Emotion Classification Pipeline.
Identifies 6 primary emotions: Joy, Fear, Sadness, Anger, Love, Surprise (plus Neutral).
"""
from typing import Dict, Any, List
from backend.services.ai_service import ai_service


def classify_emotion(text: str) -> Dict[str, Any]:
    """Classifies text emotion using HuggingFace DistilBERT model."""
    return ai_service.analyze_emotion_distilbert(text)


def get_emotion_spectrum(text: str) -> List[Dict[str, Any]]:
    """Returns probability distribution across all emotion classes."""
    res = ai_service.analyze_emotion_distilbert(text)
    return res.get("all_emotions", [])
