import pandas as pd
from transformers import pipeline

# -----------------------------
# 1. Load your trained model
# -----------------------------
classifier = pipeline(
    "text-classification",
    model="./spare_parts_model",
    tokenizer="./spare_parts_model"
)

def is_spare_parts_inquiry(text: str, threshold: float = 0.5):
    """
    Returns a boolean prediction and the confidence score.
    """
    result = classifier(text)[0]
    label = 1 if result['label'] == 'LABEL_1' else 0
    return label == 1, result['score']

# -----------------------------
# 2. Load CSV
# -----------------------------
csv_path = "./data/test.csv"  # your CSV path
df = pd.read_csv(csv_path)

# Ensure 'text' and 'label' columns exist
assert 'text' in df.columns and 'label' in df.columns, "CSV must have 'text' and 'label' columns"

# -----------------------------
# 3. Run inference
# -----------------------------
print(f"{'Text':60} {'Predicted':10} {'Confidence':10} {'Actual':10}")
print("-"*95)

for idx, row in df.iterrows():
    text = row['text']
    true_label = row['label']
    pred, conf = is_spare_parts_inquiry(text)
    print(f"{text[:60]:60} {str(pred):10} {conf:.3f} {true_label:10}")
