# =====================================================================
# STEP-BY-STEP MANUAL DISTILBERT EMOTION TRAINING
# Follows the exact steps from the classroom / Colab demonstration.
# =====================================================================

# ---------------------------------------------------------------------
# STEP 1: IMPORT LIBRARIES
# ---------------------------------------------------------------------
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

print("[Step 1] Libraries imported successfully.")

# ---------------------------------------------------------------------
# STEP 2: LOAD THE DATASET
# (In Colab screenshot: dataset = load_dataset("filepath"))
# Here we load the local parquet files we downloaded into data/go_emotions_ekman/
# ---------------------------------------------------------------------
print("\n[Step 2] Loading dataset from local parquet files...")
dataset = load_dataset(
    "parquet",
    data_files={
        "train": "data/go_emotions_ekman/train.parquet",
        "validation": "data/go_emotions_ekman/validation.parquet",
        "test": "data/go_emotions_ekman/test.parquet"
    }
)
print(dataset)

# ---------------------------------------------------------------------
# STEP 3: INSPECT THE SCHEMA
# (In Colab screenshot: print("Columns", dataset['train'].column_names))
# ---------------------------------------------------------------------
print("\n[Step 3] Inspecting Schema:")
print("Columns in train:", dataset["train"].column_names)
print("First row:", dataset["train"][0])

# ---------------------------------------------------------------------
# STEP 4: DEFINE EMOTION LABELS (EKMAN TAXONOMY)
# (In Colab screenshot: anger, disgust, fear, joy, sadness, surprise)
# ---------------------------------------------------------------------
emotions = ["anger", "disgust", "fear", "joy", "sadness", "surprise", "neutral"]
id2label = {i: label for i, label in enumerate(emotions)}
label2id = {label: i for i, label in enumerate(emotions)}

print("\n[Step 4] Emotion classes:")
for idx, name in id2label.items():
    print(f"  {idx} -> {name}")

# ---------------------------------------------------------------------
# STEP 5: TOKENIZE THE DATASET (Convert text into numerical identifiers)
# (In Colab screenshot: import AutoTokenizer)
# ---------------------------------------------------------------------
print("\n[Step 5] Initializing Tokenizer...")
checkpoint = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

def tokenize_function(example):
    # Extract primary emotion label ID from labels_ekman list
    labels = [int(lbl[0]) if len(lbl) > 0 else 6 for lbl in example["labels_ekman"]]
    tokens = tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=96
    )
    tokens["labels"] = labels
    return tokens

# Take a small subset for fast CPU training (e.g. 1,000 train, 200 validation)
train_subset = dataset["train"].select(range(1000))
val_subset = dataset["validation"].select(range(200))

print("Tokenizing train and validation sets...")
tokenized_train = train_subset.map(tokenize_function, batched=True)
tokenized_val = val_subset.map(tokenize_function, batched=True)
print("Tokenized sample keys:", tokenized_train[0].keys())

# ---------------------------------------------------------------------
# STEP 6: CONFIGURE DISTILBERT MODEL
# (In Colab screenshot: configuration of dataset - maximum emotion label)
# ---------------------------------------------------------------------
print("\n[Step 6] Configuring DistilBERT Sequence Classifier...")
model = AutoModelForSequenceClassification.from_pretrained(
    checkpoint,
    num_labels=len(emotions),
    id2label=id2label,
    label2id=label2id
)
print("Model created with 7 emotion output heads.")

# ---------------------------------------------------------------------
# STEP 7: COMPUTE METRICS FUNCTION (Accuracy & Macro F1)
# ---------------------------------------------------------------------
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average="macro", zero_division=0)
    return {"accuracy": acc, "f1": f1}

# ---------------------------------------------------------------------
# STEP 8: TRAINING ARGUMENTS & TRAINER
# ---------------------------------------------------------------------
print("\n[Step 8] Setting up Trainer...")
training_args = TrainingArguments(
    output_dir="models/ekman_distilbert",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=3e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=2,
    weight_decay=0.01,
    logging_steps=15,
    save_total_limit=1,
    use_cpu=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    processing_class=tokenizer,
    compute_metrics=compute_metrics
)

# ---------------------------------------------------------------------
# STEP 9: RUN TRAINING & SAVE
# ---------------------------------------------------------------------
print("\n[Step 9] Starting Training...")
trainer.train()

print("\n[Step 10] Saving final fine-tuned model...")
model.save_pretrained("models/ekman_distilbert")
tokenizer.save_pretrained("models/ekman_distilbert")
print("Done! Model saved to models/ekman_distilbert/")
