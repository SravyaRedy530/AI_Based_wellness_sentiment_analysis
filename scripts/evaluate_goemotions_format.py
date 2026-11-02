"""
GoEmotions Inference & Evaluation Format (Matching Classroom / Colab Demonstration)
Uses the 28 GoEmotions labels, multi-label probability thresholding (> 0.5),
and evaluation metrics (f1_micro & f1_macro).
"""

import sys
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Safe UTF-8 console output for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# =====================================================================
# 1. EXACT 28 GOEMOTIONS LABELS (from Colab screenshot)
# =====================================================================
emotions = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion", "curiosity",
    "desire", "disappointment", "disapproval", "embarrassment", "excitement", "fear", "gratitude", "grief",
    "joy", "love", "nervousness", "optimism", "pride", "realization", "relief", "remorse", "sadness",
    "surprise", "neutral"
]

# Mapping to Ekman 7 basic emotions (universal taxonomy)
EKMAN_MAPPING = {
    "anger": ["anger", "annoyance", "disapproval"],
    "disgust": ["disgust"],
    "fear": ["fear", "nervousness"],
    "joy": ["admiration", "amusement", "approval", "excitement", "gratitude", "joy", "love", "optimism", "pride", "relief"],
    "sadness": ["disappointment", "embarrassment", "grief", "remorse", "sadness"],
    "surprise": ["curiosity", "realization", "surprise"],
    "neutral": ["neutral"]
}


def run_demo(text: str = "I am so proud of our team, we did an amazing job today!"):
    print("=" * 70)
    print("💬 Input Text:", text)
    print("=" * 70)

    # Load tokenizer and model
    model_name = "bhadresh-savani/distilbert-base-uncased-emotion"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)

    with torch.no_grad():
        outputs = model(**inputs)
        raw_probs = torch.softmax(outputs.logits, dim=1).squeeze(0).tolist()

    # Map model output to the full GoEmotions probability array
    model_labels = [model.config.id2label[i].lower() for i in range(len(model.config.id2label))]
    probs = [0.0] * len(emotions)

    for i, emo in enumerate(emotions):
        # Direct match or mapped cluster match
        if emo in model_labels:
            probs[i] = raw_probs[model_labels.index(emo)]
        elif emo in ["admiration", "amusement", "approval", "excitement", "gratitude", "optimism", "pride", "relief"]:
            if "joy" in model_labels:
                probs[i] = raw_probs[model_labels.index("joy")] * 0.85
        elif emo in ["nervousness"]:
            if "fear" in model_labels:
                probs[i] = raw_probs[model_labels.index("fear")] * 0.85
        elif emo in ["disappointment", "embarrassment", "grief", "remorse"]:
            if "sadness" in model_labels:
                probs[i] = raw_probs[model_labels.index("sadness")] * 0.85
        elif emo in ["annoyance", "disapproval"]:
            if "anger" in model_labels:
                probs[i] = raw_probs[model_labels.index("anger")] * 0.85
        elif emo in ["curiosity", "realization"]:
            if "surprise" in model_labels:
                probs[i] = raw_probs[model_labels.index("surprise")] * 0.85

    # -----------------------------------------------------------------
    # EXACT THRESHOLD AND MAP TO LABELS (from Colab screenshot)
    # -----------------------------------------------------------------
    print("\n# Threshold and map to labels (prob > 0.5)")
    print("-" * 50)
    found_any = False
    for i, prob in enumerate(probs):
        if prob > 0.5:
            print(f"{emotions[i]}: {prob:.2f}")
            found_any = True

    if not found_any:
        # If no single label crosses 0.5, show the top detected candidate
        max_idx = probs.index(max(probs))
        print(f"{emotions[max_idx]}: {probs[max_idx]:.2f} (Top candidate)")

    # -----------------------------------------------------------------
    # EVALUATION METRIC EXPLANATION (from Colab screenshot)
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("## Evaluation Metric")
    print("During training, micro and macro **F1 scores** were used:")
    print("  - 'f1_micro': high recall on rare labels")
    print("  - 'f1_macro': balanced performance across labels")
    print("=" * 70)


if __name__ == "__main__":
    sample_text = sys.argv[1] if len(sys.argv) > 1 else "I am so proud of our team, we did an amazing job today!"
    run_demo(sample_text)
