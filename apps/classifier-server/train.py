

from transformers.training_args import TrainingArguments
from transformers import Trainer, AutoTokenizer, AutoModelForSequenceClassification, pipeline
from datasets import load_dataset

# ----------------------------------------------------------
# 1. LOAD DATASET
# ----------------------------------------------------------
dataset = load_dataset(
    "csv",
    data_files={
        "train": "./data/synthetic_dataset.csv",
        "test": "./data/synthetic_dataset.csv" 
    }
)

# ----------------------------------------------------------
# 2. CHOOSE MULTILINGUAL MODEL
# ----------------------------------------------------------
model_name = "xlm-roberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2
)

# ----------------------------------------------------------
# 3. TOKENIZATION FUNCTION
# ----------------------------------------------------------
def preprocess(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

tokenized_dataset = dataset.map(preprocess, batched=True)
tokenized_dataset.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "label"]
)

# ----------------------------------------------------------
# 4. TRAINING ARGUMENTS
# ----------------------------------------------------------
training_args = TrainingArguments(
    output_dir="./spare_parts_model",
    eval_strategy="epoch",    # evaluate every epoch
    # save_strategy="epoch",        # optional for older transformers
    learning_rate=2e-5,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    weight_decay=0.01,
    logging_dir="./logs",
    load_best_model_at_end=False,   # disable to avoid crash on older transformers
    save_total_limit=1,
)

# ----------------------------------------------------------
# 5. TRAINER
# ----------------------------------------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    tokenizer=tokenizer,
)

# ----------------------------------------------------------
# 6. TRAIN THE MODEL
# ----------------------------------------------------------
trainer.train()

# ----------------------------------------------------------
# 7. SAVE THE MODEL
# ----------------------------------------------------------
model.save_pretrained("./spare_parts_model")
tokenizer.save_pretrained("./spare_parts_model")
print("Model saved to ./spare_parts_model")

# ----------------------------------------------------------
# 8. RUN INFERENCE
# ----------------------------------------------------------
classifier = pipeline(
    "text-classification",
    model="./spare_parts_model",
    tokenizer="./spare_parts_model"
)

test_msgs = [
    "Need a replacement gasket for model TX900",
    "Lunch at 14:00?",
    "Do we have manuals for HF22 engines?",
]

print("\n--- Predictions ---")
for msg in test_msgs:
    print(msg, "->", classifier(msg))
