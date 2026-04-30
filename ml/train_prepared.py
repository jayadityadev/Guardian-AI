"""Train the grooming model from the prepared cleaned/augmented datasets.

This is the handoff entrypoint for a higher-hardware machine.
It does not perform any data cleaning or augmentation; it consumes the
prepared artifacts already written under `data/processed/`.

Usage:
  python3 ml/train_prepared.py

Expected inputs:
  - data/processed/augmented_train.csv
  - data/processed/final_val.csv
  - data/processed/final_test.csv

Outputs:
  - ml/models/grooming_model/saved_model/grooming_classifier.joblib
  - ml/models/grooming_model/saved_model/training_summary.json
  - ml/models/grooming_model/saved_model/threshold_summary.json
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "ml" / "models" / "grooming_model" / "saved_model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_PATH = DATA_DIR / "augmented_train.csv"
VAL_PATH = DATA_DIR / "final_val.csv"
TEST_PATH = DATA_DIR / "final_test.csv"


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError(f"{path} must contain 'text' and 'label' columns")
    df = df.dropna(subset=["text", "label"]).copy()
    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(int)
    return df


def evaluate(model, df: pd.DataFrame, threshold: float = 0.5) -> dict:
    texts = df["text"].tolist()
    labels = df["label"].tolist()
    scores = model.predict_proba(texts)[:, 1]
    preds = [1 if score >= threshold else 0 for score in scores]
    return {
        "threshold": threshold,
        "accuracy": float(accuracy_score(labels, preds)),
        "precision": float(precision_score(labels, preds, zero_division=0)),
        "recall": float(recall_score(labels, preds, zero_division=0)),
        "f1": float(f1_score(labels, preds, zero_division=0)),
        "roc_auc": float(roc_auc_score(labels, scores)) if len(set(labels)) > 1 else 0.0,
    }


def best_threshold(model, val_df: pd.DataFrame) -> dict:
    texts = val_df["text"].tolist()
    labels = val_df["label"].tolist()
    scores = model.predict_proba(texts)[:, 1]

    best = {"threshold": 0.5, "f1": -1.0, "precision": 0.0, "recall": 0.0}
    for threshold in [i / 100 for i in range(10, 91, 2)]:
        preds = [1 if s >= threshold else 0 for s in scores]
        precision = precision_score(labels, preds, zero_division=0)
        recall = recall_score(labels, preds, zero_division=0)
        f1 = f1_score(labels, preds, zero_division=0)
        if f1 > best["f1"]:
            best = {
                "threshold": threshold,
                "f1": float(f1),
                "precision": float(precision),
                "recall": float(recall),
            }
    return best


def main() -> None:
    train_df = load_csv(TRAIN_PATH)
    val_df = load_csv(VAL_PATH)
    test_df = load_csv(TEST_PATH)

    print(f"Train rows: {len(train_df)}")
    print(f"Val rows:   {len(val_df)}")
    print(f"Test rows:  {len(test_df)}")
    print(f"Train positives: {int(train_df['label'].sum())}")
    print(f"Val positives:   {int(val_df['label'].sum())}")
    print(f"Test positives:  {int(test_df['label'].sum())}")

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                lowercase=True,
                max_features=25000,
                min_df=2,
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])

    model.fit(train_df["text"].tolist(), train_df["label"].tolist())

    val_best = best_threshold(model, val_df)
    test_metrics = evaluate(model, test_df, threshold=val_best["threshold"])

    joblib.dump(model, MODEL_DIR / "grooming_classifier.joblib")
    summary = {
        "train_rows": int(len(train_df)),
        "val_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "validation_best_threshold": val_best,
        "test_metrics": test_metrics,
        "training_data": str(TRAIN_PATH),
    }
    with (MODEL_DIR / "training_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with (MODEL_DIR / "threshold_summary.json").open("w", encoding="utf-8") as f:
        json.dump({"best_threshold": val_best}, f, indent=2)

    print("Saved model to", MODEL_DIR / "grooming_classifier.joblib")
    print("Validation threshold:", val_best)
    print("Test metrics:", test_metrics)


if __name__ == "__main__":
    main()
