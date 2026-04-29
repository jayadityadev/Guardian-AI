import os
import sys
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE_DIR)


def train_grooming_model():
    """Train a lightweight offline text classifier for grooming detection."""

    model_dir = os.path.dirname(os.path.abspath(__file__))
    saved_model_dir = os.path.join(model_dir, 'saved_model')

    train_path = os.path.join(BASE_DIR, "data", "processed", "train.csv")
    df = pd.read_csv(train_path)

    texts = df['text'].astype(str).tolist()
    labels = df['label'].astype(int).tolist()

    print(f"Training samples: {len(texts)}")
    print(f"Positive (grooming): {sum(labels)}")
    print(f"Negative (safe): {len(labels) - sum(labels)}")

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            lowercase=True,
            max_features=5000
        )),
        ("classifier", LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42))
    ])

    print("Training model...")
    model.fit(texts, labels)

    os.makedirs(saved_model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(saved_model_dir, 'grooming_classifier.joblib'))

    train_accuracy = model.score(texts, labels)
    print(f"Train accuracy: {train_accuracy:.4f}")
    print(f"Model saved to {saved_model_dir}")


if __name__ == "__main__":
    train_grooming_model()

