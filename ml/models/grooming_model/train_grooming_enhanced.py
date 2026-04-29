#!/usr/bin/env python3
"""
Enhanced Grooming Detection Model using Scikit-Learn with Improved Preprocessing
Uses merged datasets (5112 samples) with better feature engineering
"""

import sys
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import re
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def advanced_text_cleaning(text):
    """Advanced text cleaning for better pattern recognition"""
    text = str(text).lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Keep important punctuation that might indicate grooming (?, !, ...)
    # Remove other special characters
    text = re.sub(r'[^\w\s?!.]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def load_and_merge_datasets():
    """Load and merge grooming datasets from both projects"""
    print("Loading datasets...")
    
    try:
        # Load old project data
        old_grooming = pd.read_csv(
            r'D:\major\child_preditor\childshield-ai\data\raw\grooming_dataset.csv',
            encoding='utf-8',
            on_bad_lines='skip'
        )
    except:
        print("  ⚠️  Old project dataset not found, using only new dataset")
        old_grooming = pd.DataFrame()
    
    # Load new project data
    new_grooming = pd.read_csv(
        r'D:\Guardian-AI\data\raw\grooming_dataset.csv',
        encoding='utf-8',
        on_bad_lines='skip'
    )
    
    # Merge if old data exists
    if len(old_grooming) > 0:
        merged = pd.concat([old_grooming, new_grooming], ignore_index=True)
    else:
        merged = new_grooming
    
    merged = merged.drop_duplicates()
    merged = merged.dropna()
    
    # Extract text and labels
    texts = merged.iloc[:, 0].astype(str).tolist()
    labels = merged.iloc[:, -1].astype(int).tolist()
    
    print(f"✓ Loaded merged dataset: {len(merged)} samples")
    print(f"  - Grooming: {sum(labels)} samples ({100*sum(labels)//len(labels)}%)")
    print(f"  - Safe: {len(labels) - sum(labels)} samples ({100*(len(labels)-sum(labels))//len(labels)}%)")
    
    return texts, labels


def train_enhanced_grooming_model():
    """Train enhanced grooming detection with multiple models"""
    
    print("\n" + "="*70)
    print("  ENHANCED GROOMING DETECTION MODEL TRAINING")
    print("="*70 + "\n")
    
    # Load data
    texts, labels = load_and_merge_datasets()
    
    # Split data (80/20)
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"\nTrain: {len(train_texts)} samples")
    print(f"Test: {len(test_texts)} samples\n")
    
    # Advanced text preprocessing
    print("Preprocessing text...")
    train_texts_clean = [advanced_text_cleaning(t) for t in train_texts]
    test_texts_clean = [advanced_text_cleaning(t) for t in test_texts]
    
    # Feature extraction with improved TF-IDF
    print("Extracting TF-IDF features...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
        max_features=10000,
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        use_idf=True,
        smooth_idf=True
    )
    
    X_train = vectorizer.fit_transform(train_texts_clean)
    X_test = vectorizer.transform(test_texts_clean)
    
    print(f"Feature matrix shape: {X_train.shape}\n")
    
    # Try multiple models and compare
    models = {
        'LogisticRegression': LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            solver='lbfgs',
            C=0.1
        ),
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=5,
            random_state=42
        ),
        'RandomForest': RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            class_weight='balanced',
            random_state=42
        )
    }
    
    best_model = None
    best_score = 0
    best_model_name = None
    results = {}
    
    for model_name, model in models.items():
        print(f"Training {model_name}...")
        model.fit(X_train, train_labels)
        
        # Predictions
        train_preds = model.predict(X_train)
        test_preds = model.predict(X_test)
        
        # Probabilities for AUC
        if hasattr(model, 'predict_proba'):
            test_probs = model.predict_proba(X_test)[:, 1]
        else:
            test_probs = test_preds
        
        # Metrics
        train_acc = accuracy_score(train_labels, train_preds)
        test_acc = accuracy_score(test_labels, test_preds)
        precision = precision_score(test_labels, test_preds, zero_division=0)
        recall = recall_score(test_labels, test_preds, zero_division=0)
        f1 = f1_score(test_labels, test_preds, zero_division=0)
        roc_auc = roc_auc_score(test_labels, test_probs)
        
        results[model_name] = {
            'train_accuracy': float(train_acc),
            'test_accuracy': float(test_acc),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'roc_auc': float(roc_auc)
        }
        
        print(f"  Train Accuracy: {train_acc:.4f}")
        print(f"  Test Accuracy: {test_acc:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1-Score: {f1:.4f}")
        print(f"  ROC-AUC: {roc_auc:.4f}\n")
        
        # Select best model (prioritize recall for grooming detection)
        if recall > best_score or (recall == best_score and f1 > best_score):
            best_score = recall
            best_model = model
            best_model_name = model_name
    
    print("="*70)
    print(f"✓ Best Model: {best_model_name}")
    print(f"  Recall: {results[best_model_name]['recall']:.4f} (catches more grooming)")
    print("="*70 + "\n")
    
    # Save best model
    model_dir = Path(__file__).parent / "saved_model_enhanced"
    model_dir.mkdir(exist_ok=True)
    
    joblib.dump(best_model, model_dir / 'grooming_classifier.joblib')
    joblib.dump(vectorizer, model_dir / 'vectorizer.joblib')
    
    # Save metrics
    metrics = {
        'best_model': best_model_name,
        'all_models': results,
        'dataset_size': len(texts),
        'train_size': len(train_texts),
        'test_size': len(test_texts),
        'vectorizer': 'TfidfVectorizer(ngram_range=(1,3), max_features=10000)'
    }
    
    with open(model_dir / 'metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✓ Model saved to {model_dir}")
    print(f"✓ Metrics saved to {model_dir}/metrics.json")
    
    return model_dir, results


if __name__ == "__main__":
    try:
        model_dir, results = train_enhanced_grooming_model()
        print("\n✓ TRAINING COMPLETE\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
