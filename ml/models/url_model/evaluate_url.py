"""Evaluation module for URL classification model."""

import os
import sys
import pandas as pd
from urllib.parse import urlparse
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE_DIR)

from ml.models.url_model.predict_url import predict_url_batch


def evaluate_url_model():
    """Evaluate URL model on test set."""
    
    data_path = os.path.join(BASE_DIR, "data", "raw", "url_dataset.csv")
    df = pd.read_csv(data_path)
    
    print(f"Evaluating URL model on {len(df)} samples...")
    
    # Get predictions
    results = predict_url_batch(df['url'].tolist())
    pred_labels = [1 if r['is_malicious'] else 0 for r in results]
    scores = [r['risk_score'] for r in results]
    true_labels = df['label'].tolist()
    
    # Calculate metrics
    accuracy = accuracy_score(true_labels, pred_labels)
    precision = precision_score(true_labels, pred_labels, zero_division=0)
    recall = recall_score(true_labels, pred_labels, zero_division=0)
    f1 = f1_score(true_labels, pred_labels, zero_division=0)
    roc_auc = roc_auc_score(true_labels, scores)
    cm = confusion_matrix(true_labels, pred_labels)
    
    print(f"\n=== URL Model Metrics ===")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"\nConfusion Matrix:")
    print(cm)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc,
        'confusion_matrix': cm
    }


if __name__ == "__main__":
    evaluate_url_model()

