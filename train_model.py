"""Train and save the ticket classification model.

Expects a CSV file `tickets.csv` in the same directory with columns:
    text, category

Usage::
    python train_model.py --data tickets.csv --model_path model/classifier.pkl
"""
import argparse
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib
from sklearn.naive_bayes import MultinomialNB


def train(data_path: Path, model_path: Path):
    df = pd.read_csv(data_path)
    if not {"text", "category"}.issubset(df.columns):
        raise ValueError("CSV must contain 'text' and 'category' columns")

    # Ensure the test split has at least one sample per class when using stratify
    n_classes = df["category"].nunique()
    # Minimum fraction so that each class appears at least once in the test set
    min_test_frac = n_classes / len(df) + 0.01  # safety buffer
    test_size = max(0.2, min_test_frac)

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            df["text"],
            df["category"],
            test_size=test_size,
            random_state=42,
            stratify=df["category"]
        )
    except ValueError:
        # Fallback for very small datasets where stratified split is impossible
        # If dataset very small, skip train/test split and use all data
        if len(df) < 30:
            X_train, X_test, y_train, y_test = df["text"], df["text"], df["category"], df["category"]
            print("[INFO] Small dataset detected – training on full set without hold-out test.")
        else:
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    df["text"],
                    df["category"],
                    test_size=test_size,
                    random_state=42,
                    shuffle=True,
                    stratify=None
                )
            except ValueError:
                print("[WARN] Dataset too small for stratified split – proceeded without stratification.")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1,2), min_df=1, sublinear_tf=True)),
        ("clf", MultinomialNB()),
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Train ticket classifier")
    parser.add_argument("--data", type=Path, default="tickets.csv", help="Path to CSV data file")
    parser.add_argument(
        "--model_path", type=Path, default=Path("model/classifier.pkl"), help="Output model file path"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train(args.data, args.model_path)