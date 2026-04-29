import os
import sys
import pandas as pd
import json
import re
from urllib.parse import urlparse
import warnings
warnings.filterwarnings('ignore')
import joblib
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Phishing keywords to check for
PHISHING_KEYWORDS = [
    'login',
    'verify', 
    'confirm',
    'secure',
    'account',
    'update',
    'alert',
    'password',
    'session',
    'signin',
    'sign-in',
    'bank',
    'support',
    'free',
    'claim',
    'refund',
]


def tokenize_text(text):
    """
    Tokenize text: break into words.
    Remove special characters, convert to lowercase.
    """
    # Convert to lowercase
    text = str(text).lower()
    # Remove special characters, keep only alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s\-]', ' ', text)
    # Split into words
    tokens = text.split()
    # Remove empty strings
    tokens = [t for t in tokens if t.strip()]
    return tokens


def check_for_phishing_keywords(url):
    """
    Tokenize URL and check if ANY token matches phishing keywords.
    If ANY keyword match found → PHISHING (is_grooming = True)
    If NO keywords found → SAFE (is_grooming = False)
    """
    tokens = tokenize_text(url)
    matched_keywords = []
    
    # Check each token against keywords using OR condition
    for token in tokens:
        for keyword in PHISHING_KEYWORDS:
            if keyword in token or token in keyword:
                if keyword not in matched_keywords:
                    matched_keywords.append(keyword)
    
    # If ANY keyword found → it's phishing/grooming
    is_grooming = len(matched_keywords) > 0
    
    return is_grooming, matched_keywords


def train_url_model():
    """Train URL phishing detection with epoch-based sklearn training."""
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    data_path = os.path.join(BASE_DIR, "data", "raw", "url_dataset.csv")
    
    print("Loading dataset...")
    print(f"\n1. Loading URL dataset from {data_path}")
    df = pd.read_csv(data_path)
    print(f"   - Loaded {len(df)} URL samples")

    print(f"\nTotal samples: {len(df)}")
    print(f"Safe (label=0): {(df['label']==0).sum()}")
    print(f"Unsafe/Grooming (label=1): {(df['label']==1).sum()}")
    
    # Build binary features: one column per keyword (1 if keyword present in tokens)
    print("\nBuilding binary keyword features...")
    texts = df['url'].astype(str).tolist()
    labels = df['label'].astype(int).tolist()

    # Create feature matrix
    feature_rows = []
    for t in texts:
        tokens = tokenize_text(t)
        row = [1 if any((kw in token) or (token in kw) for token in tokens) else 0 for kw in PHISHING_KEYWORDS]
        feature_rows.append(row)

    X = pd.DataFrame(feature_rows, columns=PHISHING_KEYWORDS)
    y = pd.Series(labels)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Epoch-based training using SGDClassifier (logistic loss)
    epochs = 20
    clf = SGDClassifier(loss='log_loss', random_state=42)

    history = []
    print(f"\nTraining for {epochs} epochs...")
    classes = [0, 1]
    for epoch in range(1, epochs + 1):
        # Shuffle each epoch
        shuffled = X_train.copy()
        shuffled['__label__'] = y_train.values
        shuffled = shuffled.sample(frac=1.0, random_state=42 + epoch).reset_index(drop=True)
        y_epoch = shuffled['__label__']
        X_epoch = shuffled.drop(columns=['__label__'])

        if epoch == 1:
            clf.partial_fit(X_epoch, y_epoch, classes=classes)
        else:
            clf.partial_fit(X_epoch, y_epoch)

        train_pred = clf.predict(X_train)
        test_pred = clf.predict(X_test)
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        history.append({
            'epoch': epoch,
            'train_accuracy': float(train_acc),
            'test_accuracy': float(test_acc)
        })
        print(f"Epoch {epoch:02d}/{epochs}: train_acc={train_acc:.4f} test_acc={test_acc:.4f}")

    # Final evaluation
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    print(f"\nFinal test accuracy: {acc:.2%} ({len(y_test)} samples)")

    # Save model and feature names
    model_dir = os.path.dirname(os.path.abspath(__file__))
    saved_model_dir = os.path.join(model_dir, 'saved_model')
    os.makedirs(saved_model_dir, exist_ok=True)

    joblib.dump(clf, os.path.join(saved_model_dir, 'url_keyword_classifier.joblib'))
    joblib.dump(PHISHING_KEYWORDS, os.path.join(saved_model_dir, 'url_keyword_features.joblib'))

    # Save results summary
    results = {
        'detection_method': 'Tokenization + Keyword Features + SGDClassifier(log_loss)',
        'epochs': epochs,
        'epoch_history': history,
        'keywords': PHISHING_KEYWORDS,
        'test_accuracy': acc,
        'classification_report': report,
        'total_samples': len(df)
    }
    with open(os.path.join(saved_model_dir, 'url_detection_results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    # Save keywords as reference
    with open(os.path.join(saved_model_dir, 'phishing_keywords.txt'), 'w') as f:
        for keyword in PHISHING_KEYWORDS:
            f.write(f"{keyword}\n")

    print(f"\nModel and results saved to {saved_model_dir}")
    print(f"- url_keyword_classifier.joblib: trained classifier")
    print(f"- url_keyword_features.joblib: feature keyword list")
    print(f"- url_detection_results.json: evaluation summary")


if __name__ == "__main__":
    train_url_model()

