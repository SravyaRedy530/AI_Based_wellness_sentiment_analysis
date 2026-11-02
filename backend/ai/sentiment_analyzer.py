"""
VADER Sentiment Intensity Analyzer.
Calculates compound, positive, neutral, and negative sentiment scores.
"""
from typing import Dict, Any
from backend.services.ai_service import ai_service


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Calculates granular sentiment polarity using NLTK VADER."""
    return ai_service.analyze_sentiment_vader(text)
