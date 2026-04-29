import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))
#!/usr/bin/env python3
"""Test enhanced grooming detection model"""

import sys
from pathlib import Path
import joblib

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

model_dir = project_root / "ml" / "models" / "grooming_model" / "saved_model_enhanced"

try:
    model = joblib.load(model_dir / 'grooming_classifier.joblib')
    vectorizer = joblib.load(model_dir / 'vectorizer.joblib')
    print("✓ Model loaded successfully\n")
except:
    print("❌ Model not found. Train first with train_grooming_enhanced.py")
    sys.exit(1)


def clean_text(text):
    """Match training preprocessing"""
    import re
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s?!.]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


test_cases = [
    ("What's the weather like?", "SAFE"),
    ("Can you help me with math homework?", "SAFE"),
    ("Do your parents know we talk?", "GROOMING"),
    ("You're so mature for your age", "GROOMING"),
    ("Don't tell anyone about us", "GROOMING"),
    ("Want to go to the movies?", "SAFE"),
]

print("="*70)
print("  TESTING ENHANCED GROOMING MODEL")
print("="*70 + "\n")

for text, expected in test_cases:
    clean = clean_text(text)
    X = vectorizer.transform([clean])
    
    if hasattr(model, 'predict_proba'):
        prob = model.predict_proba(X)[0, 1]
    else:
        prob = model.predict(X)[0]
    
    pred = "🔴 GROOMING" if prob > 0.5 else "🟢 SAFE"
    match = "✓" if ((prob > 0.5 and expected == "GROOMING") or (prob <= 0.5 and expected == "SAFE")) else "✗"
    
    print(f"{match} {text:<40} → {pred} ({prob:.3f})")

print("\n" + "="*70)
