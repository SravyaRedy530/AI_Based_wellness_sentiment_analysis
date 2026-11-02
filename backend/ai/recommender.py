"""
Personalized Wellness Recommendation Engine.
Generates tailored activity suggestions for Joy, Fear, Sadness, Anger, Love, Surprise, and Neutral.
"""
from typing import List, Dict, Any
from backend.services.ai_service import ai_service


def get_personalized_suggestions(emotion: str, support_style: str = "Gentle & Compassionate") -> List[str]:
    """Returns rule-based concise suggestions (e.g. Celebrate achievements for Joy)."""
    return ai_service.get_rule_based_suggestions(emotion)


def get_detailed_action_plan(emotion: str, sentiment_compound: float = 0.0, support_style: str = "Gentle & Compassionate") -> Dict[str, Any]:
    """Generates comprehensive cognitive and wellness action recommendations."""
    return ai_service.generate_personalized_suggestions(emotion, sentiment_compound, support_style)
