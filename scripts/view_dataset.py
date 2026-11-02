"""
GoEmotions Simplified Ekman Dataset Viewer.
Reads parquet files directly from Hugging Face or local cache,
decodes numeric labels to emotion names, and displays or exports rows.
"""

import argparse
import os
import sys
import pandas as pd

# Safe utf-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Mapping of labels_ekman integer IDs to human-readable emotion names
EKMAN_MAPPING = {
    0: "anger",
    1: "disgust",
    2: "fear",
    3: "joy",
    4: "sadness",
    5: "surprise",
    6: "neutral"
}

SPLIT_URLS = {
    "train": "https://huggingface.co/datasets/AiLab-IMCS-UL/go_emotions-en/resolve/main/simplified_ekman/train-00000-of-00001.parquet",
    "validation": "https://huggingface.co/datasets/AiLab-IMCS-UL/go_emotions-en/resolve/main/simplified_ekman/validation-00000-of-00001.parquet",
    "test": "https://huggingface.co/datasets/AiLab-IMCS-UL/go_emotions-en/resolve/main/simplified_ekman/test-00000-of-00001.parquet"
}


def view_dataset(split: str = "train", limit: int = 10, export_csv: str = None, filter_emotion: str = None):
    url = SPLIT_URLS.get(split, SPLIT_URLS["train"])
    print(f"\nLoading '{split}' split from Hugging Face...")
    df = pd.read_parquet(url)

    # Convert numeric labels_ekman array to emotion names
    df["emotions"] = df["labels_ekman"].apply(
        lambda ids: [EKMAN_MAPPING.get(int(i), str(i)) for i in ids]
    )
    df["emotions_str"] = df["emotions"].apply(lambda ems: ", ".join(ems))

    print(f"Total rows in {split} set: {len(df):,}")

    if filter_emotion:
        filter_emotion = filter_emotion.lower()
        df = df[df["emotions"].apply(lambda ems: filter_emotion in ems)]
        print(f"Filtered by emotion '{filter_emotion}': {len(df):,} matching rows found.")

    display_df = df.head(limit)

    print("\n" + "=" * 80)
    print(f"DATASET PREVIEW ({split.upper()} SPLIT - First {min(limit, len(display_df))} rows)")
    print("=" * 80)

    for idx, (_, row) in enumerate(display_df.iterrows(), 1):
        print(f"\n[{idx}] ID: {row['id']}")
        print(f"    Text     : {row['text']}")
        print(f"    Ekman    : {row['emotions_str'].upper()} (IDs: {row['labels_ekman']})")

    print("\n" + "=" * 80)

    if export_csv:
        os.makedirs(os.path.dirname(os.path.abspath(export_csv)), exist_ok=True)
        # Export with clean columns
        export_df = df.head(1000)
        export_df[["id", "text", "emotions_str", "labels_ekman"]].to_csv(export_csv, index=False, encoding="utf-8")
        print(f"Exported sample rows to: {export_csv} (You can open this directly in Excel or VS Code!)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View GoEmotions Simplified Ekman Dataset")
    parser.add_argument("--split", type=str, default="train", choices=["train", "validation", "test"], help="Dataset split")
    parser.add_argument("--limit", type=int, default=10, help="Number of rows to view")
    parser.add_argument("--export-csv", type=str, default=None, help="Path to export as CSV (e.g. data/preview.csv)")
    parser.add_argument("--filter", type=str, default=None, help="Filter by emotion (e.g. joy, anger, sadness)")
    args = parser.parse_args()

    view_dataset(split=args.split, limit=args.limit, export_csv=args.export_csv, filter_emotion=args.filter)
