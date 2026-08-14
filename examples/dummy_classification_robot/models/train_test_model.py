"""Train the relevance classifier.

Usage:
    python models/train_test_model.py

The script expects the training data at:

    models/tiny_data.csv

and writes the trained model to:

    models/classifier.joblib
"""


from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

DATA_PATH = Path( "models/tiny_data.csv")
MODEL_PATH = Path("models/classifier.joblib")
MODEL_PATH.parent.mkdir(exist_ok=True)

LABEL_COLUMN = "technology|18-relevance"

# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------

df = pd.read_csv(DATA_PATH)

# Keep only rows with a label
df = df[df[LABEL_COLUMN].notna()].copy()

# Construct input text
df["text"] = (
    df["title"].fillna("")
    + " "
    + df["abstract"].fillna("")
)

X = df["text"]
y = df[LABEL_COLUMN]

print(f"Training examples: {len(df)}")
print(y.value_counts())

# ------------------------------------------------------------------
# Train/test split
# ------------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

# ------------------------------------------------------------------
# Pipeline
# ------------------------------------------------------------------

pipeline = Pipeline(
    [
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                max_features=20000,
                ngram_range=(1, 2),
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
            ),
        ),
    ]
)

# ------------------------------------------------------------------
# Train
# ------------------------------------------------------------------

pipeline.fit(X_train, y_train)

# ------------------------------------------------------------------
# Evaluate
# ------------------------------------------------------------------

pred = pipeline.predict(X_test)

print(classification_report(y_test, pred))

# ------------------------------------------------------------------
# Save
# ------------------------------------------------------------------

joblib.dump(pipeline, MODEL_PATH)

print(f"Saved model to {MODEL_PATH}")