"""
MoodMentor: Fine-Tune DistilBERT on GoEmotions (Ekman Taxonomy)
Trains a 7-class emotion classifier using PyTorch & HuggingFace Transformers.
Taxonomy: anger, disgust, fear, joy, sadness, surprise, neutral.
"""

import os
import sys
import time
import json
import argparse
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, f1_score

# Enable UTF-8 console output for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ekman 7-Class Label Taxonomy
ID2LABEL = {
    0: "anger",
    1: "disgust",
    2: "fear",
    3: "joy",
    4: "sadness",
    5: "surprise",
    6: "neutral"
}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}

DATASET_URLS = {
    "train": "https://huggingface.co/datasets/AiLab-IMCS-UL/go_emotions-en/resolve/main/simplified_ekman/train-00000-of-00001.parquet",
    "validation": "https://huggingface.co/datasets/AiLab-IMCS-UL/go_emotions-en/resolve/main/simplified_ekman/validation-00000-of-00001.parquet"
}


class GoEmotionsDataset(Dataset):
    """PyTorch Dataset wrapper for GoEmotions text & Ekman labels."""
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = list(texts)
        self.labels = list(labels)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long)
        }


def load_data(split="train", subset=0, cache_dir="data/go_emotions_ekman"):
    """Loads parquet data from local cache or remote Hugging Face repository."""
    os.makedirs(cache_dir, exist_ok=True)
    local_file = os.path.join(cache_dir, f"{split}.parquet")

    if os.path.exists(local_file):
        print(f"[*] Loading {split} split from local cache: {local_file}")
        df = pd.read_parquet(local_file)
    else:
        url = DATASET_URLS[split]
        print(f"[*] Fetching {split} split from Hugging Face: {url}")
        df = pd.read_parquet(url)
        df.to_parquet(local_file)
        print(f"[+] Cached {split} split locally: {local_file}")

    # Extract primary label from labels_ekman list
    df = df[df["labels_ekman"].apply(lambda x: len(x) > 0)].copy()
    df["primary_label"] = df["labels_ekman"].apply(lambda x: int(x[0]))

    if subset > 0 and subset < len(df):
        print(f"[*] Using a subset of {subset:,} samples for {split} split.")
        df = df.sample(n=subset, random_state=42).reset_index(drop=True)

    print(f"[+] {split.capitalize()} set ready: {len(df):,} samples.")
    return df


def train(args):
    start_time = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("=" * 65)
    print("🧠 MoodMentor: DistilBERT Emotion Model Training")
    print("=" * 65)
    print(f"  - Device          : {device} ({'GPU Acceleration' if device.type == 'cuda' else 'CPU Training'})")
    print(f"  - Base Model      : {args.base_model}")
    print(f"  - Target Classes  : 7 Ekman Emotions")
    print(f"  - Epochs          : {args.epochs}")
    print(f"  - Batch Size      : {args.batch_size}")
    print(f"  - Learning Rate   : {args.lr}")
    print(f"  - Train Subset    : {'Full (' + str(args.subset) + ')' if args.subset > 0 else 'All Available'}")
    print(f"  - Output Dir      : {args.output_dir}")
    print("=" * 65)

    # 1. Load Data
    train_df = load_data("train", subset=args.subset)
    val_subset = max(100, int(args.subset * 0.2)) if args.subset > 0 else 0
    val_df = load_data("validation", subset=val_subset)

    # 2. Tokenizer & Datasets
    print(f"\n[*] Initializing Tokenizer ({args.base_model})...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)

    train_dataset = GoEmotionsDataset(train_df["text"], train_df["primary_label"], tokenizer, args.max_length)
    val_dataset = GoEmotionsDataset(val_df["text"], val_df["primary_label"], tokenizer, args.max_length)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)

    # 3. Model
    print(f"[*] Initializing Sequence Classification Model ({args.base_model})...")
    model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        num_labels=7,
        id2label=ID2LABEL,
        label2id=LABEL2ID
    )
    model.to(device)

    # 4. Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)

    print("\n🚀 Starting Training Loop...\n")

    best_val_f1 = 0.0

    for epoch in range(1, args.epochs + 1):
        epoch_start = time.time()
        model.train()
        total_loss = 0.0
        batch_count = len(train_loader)

        for step, batch in enumerate(train_loader, 1):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            if step % max(1, batch_count // 5) == 0 or step == batch_count:
                print(f"  Epoch [{epoch}/{args.epochs}] - Step [{step}/{batch_count}] - Loss: {loss.item():.4f}")

        avg_train_loss = total_loss / max(1, batch_count)

        # Validation Phase
        model.eval()
        val_preds, val_targets = [], []
        val_loss = 0.0

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"].to(device)

                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                val_loss += outputs.loss.item()

                logits = outputs.logits
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                val_preds.extend(preds)
                val_targets.extend(labels.cpu().numpy())

        avg_val_loss = val_loss / max(1, len(val_loader))
        val_acc = accuracy_score(val_targets, val_preds)
        val_f1 = f1_score(val_targets, val_preds, average="macro", zero_division=0)
        epoch_duration = time.time() - epoch_start

        print(f"\n[Result] Epoch {epoch} Complete ({epoch_duration:.1f}s):")
        print(f"  Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}")
        print(f"  Val Accuracy: {val_acc * 100:.2f}% | Val Macro F1: {val_f1:.4f}\n" + "-" * 50)

        # Save Best Model
        if val_f1 >= best_val_f1:
            best_val_f1 = val_f1
            os.makedirs(args.output_dir, exist_ok=True)
            model.save_pretrained(args.output_dir)
            tokenizer.save_pretrained(args.output_dir)

            meta = {
                "base_model": args.base_model,
                "epochs": args.epochs,
                "best_epoch": epoch,
                "val_accuracy": round(val_acc, 4),
                "val_macro_f1": round(val_f1, 4),
                "val_loss": round(avg_val_loss, 4),
                "labels": ID2LABEL,
                "trained_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(os.path.join(args.output_dir, "training_info.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)

    total_time = time.time() - start_time
    print("=" * 65)
    print(f"🎉 Training Finished Successfully in {total_time:.1f}s!")
    print(f"💾 Model Saved to: {os.path.abspath(args.output_dir)}")
    print(f"   - Best Val Macro F1: {best_val_f1:.4f}")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune DistilBERT on Ekman GoEmotions")
    parser.add_argument("--base-model", type=str, default="distilbert-base-uncased", help="Hugging Face base model")
    parser.add_argument("--subset", type=int, default=1000, help="Number of training samples (0 for all ~43.4k)")
    parser.add_argument("--epochs", type=int, default=2, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=3e-5, help="Learning rate")
    parser.add_argument("--max-length", type=int, default=96, help="Max sequence length")
    parser.add_argument("--output-dir", type=str, default="models/ekman_distilbert", help="Path to save fine-tuned model")
    args = parser.parse_args()

    train(args)
