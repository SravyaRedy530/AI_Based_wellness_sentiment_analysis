import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000/api")

# Color palette for emotional states (supporting GoEmotions Ekman 7-Class taxonomy)
EMOTION_COLORS = {
    "joy": "#10B981",       # Emerald Green
    "love": "#EC4899",      # Pink
    "surprise": "#06B6D4",  # Cyan
    "sadness": "#3B82F6",   # Blue
    "fear": "#8B5CF6",      # Violet / Purple
    "anger": "#EF4444",     # Red / Coral
    "disgust": "#14B8A6",   # Teal / Mint
    "neutral": "#6B7280"    # Gray
}

EMOTION_ICONS = {
    "joy": "😊",
    "love": "💖",
    "surprise": "😲",
    "sadness": "😢",
    "fear": "😨",
    "anger": "😡",
    "disgust": "🤢",
    "neutral": "😐"
}
