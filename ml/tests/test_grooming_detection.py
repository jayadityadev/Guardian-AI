import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.models.url_model.predict_url import predict_url
from ml.models.url_model.predict_url import predict_url

print("="*70)
print("URL/Text Grooming Detection - Tokenization + Keyword Matching")
print("="*70)

test_cases = [
    ("https://amazon.com", "Safe URL"),
    ("login to verify account", "Contains login, verify, account"),
    ("secure your password", "Contains secure, password"),
    ("claim your free refund", "Contains claim, free, refund"),
    ("meet me tomorrow alone", "Safe - no keywords"),
    ("update your bank session", "Contains update, bank, session"),
]

for text, description in test_cases:
    result = predict_url(text)
    print(f"\nText: {text}")
    print(f"Description: {description}")
    print(f"  is_grooming: {result['is_grooming']}")
    print(f"  risk_score: {result['risk_score']}")
    print(f"  matched_keywords: {result['matched_keywords']}")
