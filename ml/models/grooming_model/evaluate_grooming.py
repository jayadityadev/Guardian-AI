import os
import sys
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE_DIR)

from ml.models.grooming_model.predict_grooming import predict_grooming_batch


def evaluate_grooming_model(test_split='test'):
    """Evaluate grooming model on test set."""
    
    test_path = os.path.join(BASE_DIR, "data", "processed", f"{test_split}.csv")
    df = pd.read_csv(test_path)
    
    # Remove NaN values and convert to string
    df = df.dropna(subset=['text', 'label'])
    df['text'] = df['text'].astype(str)
    
    print(f"Evaluating on {test_split} set ({len(df)} samples)...")
    
    texts = df['text'].tolist()
    true_labels = df['label'].tolist()
    
    # Get predictions
    scores = predict_grooming_batch(texts)
    pred_labels = [1 if score > 0.5 else 0 for score in scores]
    
    # Calculate metrics
    accuracy = accuracy_score(true_labels, pred_labels)
    precision = precision_score(true_labels, pred_labels, zero_division=0)
    recall = recall_score(true_labels, pred_labels, zero_division=0)
    f1 = f1_score(true_labels, pred_labels, zero_division=0)
    roc_auc = roc_auc_score(true_labels, scores) if len(set(true_labels)) > 1 else 0.0
    cm = confusion_matrix(true_labels, pred_labels)
    
    print(f"\n=== Metrics on {test_split} set ===")
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
    evaluate_grooming_model('test')

