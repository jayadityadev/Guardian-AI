#!/usr/bin/env python3
"""
Compare Enhanced Sklearn Model vs BERT Model
Test both models on identical test set and compare metrics
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json
import re
import joblib

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Load enhanced model
print("\n" + "="*80)
print("  LOADING ENHANCED SKLEARN MODEL (TF-IDF + Logistic Regression)")
print("="*80 + "\n")

model_dir_sklearn = project_root / "ml" / "models" / "grooming_model" / "saved_model_enhanced"

try:
    sklearn_model = joblib.load(model_dir_sklearn / 'grooming_classifier.joblib')
    sklearn_vectorizer = joblib.load(model_dir_sklearn / 'vectorizer.joblib')
    
    with open(model_dir_sklearn / 'metrics.json', 'r') as f:
        sklearn_metrics = json.load(f)
    
    print("✓ Enhanced Sklearn Model loaded")
    print(f"  - Model: {sklearn_metrics['best_model']}")
    print(f"  - Training data: {sklearn_metrics['dataset_size']:,} samples")
    print(f"  - Test accuracy: {sklearn_metrics['all_models'][sklearn_metrics['best_model']]['test_accuracy']:.4f}\n")
except Exception as e:
    print(f"❌ Error loading sklearn model: {e}\n")
    sklearn_model = None
    sklearn_metrics = None

# Load BERT model
print("="*80)
print("  LOADING BERT MODEL (DistilBERT + Fine-tuning)")
print("="*80 + "\n")

model_dir_bert = project_root / "ml" / "models" / "grooming_model" / "saved_model_bert"

try:
    import tensorflow as tf
    from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
    
    bert_tokenizer = AutoTokenizer.from_pretrained(str(model_dir_bert))
    bert_model = TFAutoModelForSequenceClassification.from_pretrained(str(model_dir_bert))
    
    with open(model_dir_bert / 'metrics.json', 'r') as f:
        bert_metrics = json.load(f)
    
    print("✓ BERT Model loaded")
    print(f"  - Model: DistilBERT (fine-tuned)")
    print(f"  - Parameters: 66.9M")
    print(f"  - Training data: {bert_metrics['dataset_size']:,} samples")
    print(f"  - Test accuracy: {bert_metrics.get('accuracy', 'N/A')}\n")
except Exception as e:
    print(f"❌ BERT model not trained yet: {e}\n")
    bert_model = None
    bert_metrics = None

# Test samples
test_cases = [
    ("What's your name?", "SAFE"),
    ("How was your day?", "SAFE"),
    ("Can you help me with homework?", "SAFE"),
    ("Want to go to the mall?", "SAFE"),
    ("You're so special", "GROOMING"),
    ("Don't tell your parents about us", "GROOMING"),
    ("I care about you more than anyone", "GROOMING"),
    ("You're so mature for your age", "GROOMING"),
    ("Let's meet somewhere private", "GROOMING"),
    ("Send me a photo", "GROOMING"),
]

def clean_text_sklearn(text):
    """Match sklearn preprocessing"""
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s?!.]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def predict_sklearn(text):
    """Get sklearn prediction"""
    if sklearn_model is None:
        return None
    
    clean = clean_text_sklearn(text)
    X = sklearn_vectorizer.transform([clean])
    
    if hasattr(sklearn_model, 'predict_proba'):
        prob = sklearn_model.predict_proba(X)[0, 1]
    else:
        prob = sklearn_model.predict(X)[0]
    
    return float(prob)

def predict_bert(text):
    """Get BERT prediction"""
    if bert_model is None:
        return None
    
    text = str(text).strip()
    
    inputs = bert_tokenizer(
        text,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_tensors='tf'
    )
    
    outputs = bert_model(inputs)
    logits = outputs.logits
    
    probs = tf.nn.softmax(logits, axis=1).numpy()
    grooming_prob = float(probs[0, 1])
    
    return grooming_prob

# Compare predictions
print("="*80)
print("  COMPARISON: SKLEARN vs BERT ON TEST CASES")
print("="*80 + "\n")

print(f"{'Text':<45} | {'Expected':<10} | {'Sklearn':<12} | {'BERT':<12} | {'Match':<10}")
print("-" * 100)

sklearn_correct = 0
sklearn_total = 0
bert_correct = 0
bert_total = 0

for text, expected in test_cases:
    sklearn_prob = predict_sklearn(text)
    bert_prob = predict_bert(text)
    
    # Predictions
    sklearn_pred = "GROOMING" if sklearn_prob and sklearn_prob > 0.5 else "SAFE" if sklearn_prob is not None else "N/A"
    bert_pred = "GROOMING" if bert_prob and bert_prob > 0.5 else "SAFE" if bert_prob is not None else "N/A"
    
    # Check correctness
    sklearn_correct_pred = (sklearn_pred == expected)
    bert_correct_pred = (bert_pred == expected)
    
    match_status = "✓" if sklearn_correct_pred and bert_correct_pred else "⚠" if sklearn_correct_pred != bert_correct_pred else "✗"
    
    text_display = text[:43] + ".." if len(text) > 45 else text
    
    if sklearn_prob is not None:
        sklearn_total += 1
        if sklearn_correct_pred:
            sklearn_correct += 1
    
    if bert_prob is not None:
        bert_total += 1
        if bert_correct_pred:
            bert_correct += 1
    
    sklearn_display = f"{sklearn_pred} ({sklearn_prob:.2f})" if sklearn_prob is not None else "N/A"
    bert_display = f"{bert_pred} ({bert_prob:.2f})" if bert_prob is not None else "N/A"
    
    print(f"{text_display:<45} | {expected:<10} | {sklearn_display:<12} | {bert_display:<12} | {match_status:<10}")

print("\n" + "="*80)
print("  RESULTS SUMMARY")
print("="*80 + "\n")

if sklearn_metrics and bert_metrics:
    print("SKLEARN MODEL (TF-IDF + Logistic Regression)")
    print(f"  Test Accuracy: {sklearn_metrics['all_models'][sklearn_metrics['best_model']]['test_accuracy']:.4f}")
    print(f"  Precision: {sklearn_metrics['all_models'][sklearn_metrics['best_model']]['precision']:.4f}")
    print(f"  Recall: {sklearn_metrics['all_models'][sklearn_metrics['best_model']]['recall']:.4f}")
    print(f"  F1-Score: {sklearn_metrics['all_models'][sklearn_metrics['best_model']]['f1_score']:.4f}")
    print(f"  ROC-AUC: {sklearn_metrics['all_models'][sklearn_metrics['best_model']]['roc_auc']:.4f}\n")
    
    print("BERT MODEL (DistilBERT + Fine-tuning)")
    print(f"  Test Accuracy: {bert_metrics.get('accuracy', 'N/A')}")
    print(f"  Precision: {bert_metrics.get('precision', 'N/A')}")
    print(f"  Recall: {bert_metrics.get('recall', 'N/A')}")
    print(f"  F1-Score: {bert_metrics.get('f1_score', 'N/A')}")
    print(f"  ROC-AUC: {bert_metrics.get('roc_auc', 'N/A')}\n")

elif sklearn_metrics:
    print("📊 SKLEARN MODEL TEST RESULTS")
    print(f"  Correct: {sklearn_correct}/{sklearn_total}")
    print(f"  Test Accuracy: {(sklearn_correct/sklearn_total*100):.1f}%\n")

if bert_metrics:
    print("📊 BERT MODEL TEST RESULTS")
    print(f"  Correct: {bert_correct}/{bert_total}")
    if bert_total > 0:
        print(f"  Test Accuracy: {(bert_correct/bert_total*100):.1f}%\n")

print("="*80 + "\n")

if sklearn_metrics and bert_metrics:
    print("🏆 RECOMMENDATION:\n")
    sklearn_acc = sklearn_metrics['all_models'][sklearn_metrics['best_model']]['test_accuracy']
    bert_acc = bert_metrics.get('accuracy', 0)
    
    if bert_acc > sklearn_acc:
        print(f"✅ BERT is better! ({bert_acc:.1%} vs {sklearn_acc:.1%})")
        print("   BERT understands language context better and catches more grooming patterns.")
        print("   Use BERT in production for better accuracy.\n")
    else:
        print(f"✅ SKLEARN is better or comparable ({sklearn_acc:.1%} vs {bert_acc:.1%})")
        print("   SKLEARN is faster and still accurate. Use for quick inference.\n")
elif sklearn_metrics:
    print("⏳ BERT training not completed yet.")
    print("   Current SKLEARN model has good accuracy and is ready to use.\n")
elif bert_metrics:
    print("✅ BERT model is ready!")
    print(f"   Test Accuracy: {bert_metrics.get('accuracy', 'N/A')}\n")
