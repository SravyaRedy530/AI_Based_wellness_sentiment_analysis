"""
MoodMentor: Test Custom Text on Fine-Tuned Ekman DistilBERT Model
"""

import sys
import argparse
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def predict(text: str, model_path: str = "models/ekman_distilbert"):
    print(f"\n[*] Loading model checkpoint from: {model_path}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        model.eval()
    except Exception as e:
        print(f"[!] Could not load model from '{model_path}': {e}")
        print("[!] Please run training first: python scripts/train_ekman.py --subset 1000")
        return

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1).squeeze(0).numpy()

    id2label = model.config.id2label
    results = sorted(
        [{"emotion": id2label[i], "confidence": float(probs[i])} for i in range(len(probs))],
        key=lambda x: x["confidence"],
        reverse=True
    )

    primary = results[0]

    print("=" * 60)
    print(f"💬 Input Text : \"{text}\"")
    print("=" * 60)
    print(f"🎯 Primary Emotion : {primary['emotion'].upper()} ({primary['confidence'] * 100:.2f}%)")
    print("-" * 60)
    print("Full Emotion Spectrum:")
    for res in results:
        bar = "█" * int(res["confidence"] * 30)
        print(f"  {res['emotion'].capitalize():<10} : {res['confidence'] * 100:>5.1f}%  {bar}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict Emotion using Fine-Tuned DistilBERT")
    parser.add_argument("--text", type=str, default="I am thrilled and proud with our team's amazing launch today!", help="Text to classify")
    parser.add_argument("--model-path", type=str, default="models/ekman_distilbert", help="Path to saved model")
    args = parser.parse_args()

    predict(args.text, args.model_path)
