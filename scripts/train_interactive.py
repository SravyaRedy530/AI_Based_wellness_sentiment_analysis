# %% [markdown]
# # Step-by-Step DistilBERT Fine-Tuning on GoEmotions (Ekman Taxonomy)
# This file matches the exact workflow shown in Google Colab.
# In VS Code, you can click "[▶ Run Cell]" above each section!

# %% [1] Step 1: Load the Dataset
from datasets import load_dataset

print("[*] Loading GoEmotions (simplified_ekman) dataset...")
dataset = load_dataset("AiLab-IMCS-UL/go_emotions-en", "simplified_ekman")
print(dataset)

# %% [2] Step 2: Inspect the Schema
print("\n" + "=" * 50)
print("Columns in train split:", dataset["train"].column_names)
print("Features:", dataset["train"].features)
print("Sample row:", dataset["train"][0])
print("=" * 50)

# %% [3] Step 3: Define Emotion Labels (Ekman Taxonomy)
# anger, disgust, fear, joy, sadness, surprise, neutral
emotions = ["anger", "disgust", "fear", "joy", "sadness", "surprise", "neutral"]
id2label = {i: label for i, label in enumerate(emotions)}
label2id = {label: i for i, label in enumerate(emotions)}

print("\nEmotion Label Mapping:")
for i, name in id2label.items():
    print(f"  {i}: {name}")

# %% [4] Step 4: Tokenize the Dataset (Convert Text to Numerical Identifiers)
from transformers import AutoTokenizer

model_checkpoint = "distilbert-base-uncased"
print(f"\n[*] Loading Tokenizer: {model_checkpoint}...")
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)


def preprocess_function(examples):
    # GoEmotions labels_ekman is a list of integers (e.g. [3])
    # Extract the primary label (or 6 for neutral fallback)
    labels = [int(lbl[0]) if len(lbl) > 0 else 6 for lbl in examples["labels_ekman"]]
    tokens = tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=96
    )
    tokens["labels"] = labels
    return tokens


# For quick local execution in VS Code, we can take a subset:
train_small = dataset["train"].select(range(1000))
val_small = dataset["validation"].select(range(200))

print("\n[*] Tokenizing sample dataset...")
tokenized_train = train_small.map(preprocess_function, batched=True)
tokenized_val = val_small.map(preprocess_function, batched=True)
print("Tokenized train example keys:", tokenized_train[0].keys())

# %% [5] Step 5: Model Configuration
from transformers import AutoModelForSequenceClassification

print(f"\n[*] Configuring DistilBERT model with {len(emotions)} classes...")
model = AutoModelForSequenceClassification.from_pretrained(
    model_checkpoint,
    num_labels=len(emotions),
    id2label=id2label,
    label2id=label2id
)
print("Model configured successfully!")

# %% [6] Step 6: Train using our CPU-Optimized Training Script
# In VS Code terminal, you can run:
# python scripts/train_ekman.py --subset 1000 --epochs 2 --batch-size 16
print("\nTo train end-to-end and save model weights, run in VS Code terminal:")
print("python scripts/train_ekman.py --subset 1000 --epochs 2 --batch-size 16")
