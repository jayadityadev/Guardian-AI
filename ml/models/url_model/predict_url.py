import os
import re
from urllib.parse import urlparse
import joblib

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


def _load_trained_model():
    """Load trained sklearn keyword classifier if available."""
    model_dir = os.path.dirname(os.path.abspath(__file__))
    saved_model_dir = os.path.join(model_dir, 'saved_model')
    clf_path = os.path.join(saved_model_dir, 'url_keyword_classifier.joblib')
    feats_path = os.path.join(saved_model_dir, 'url_keyword_features.joblib')
    if os.path.exists(clf_path) and os.path.exists(feats_path):
        try:
            clf = joblib.load(clf_path)
            features = joblib.load(feats_path)
            return clf, features
        except Exception:
            return None, None
    return None, None


def predict_url(url):
    """
    Predict if URL is phishing/grooming using tokenization and keyword matching.
    
    Args:
        url (str): URL or text to analyze
        
    Returns:
        dict: Prediction results with classification and matched keywords
    """
    # Strict rule: tokenize and if ANY token matches keywords => unsafe; else safe
    is_rule_grooming, matched_keywords = check_for_phishing_keywords(url)
    if is_rule_grooming:
        if len(matched_keywords) <= 2:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        return {
            'text': url,
            'is_grooming': True,
            'is_malicious': True,
            'predicted_label': 1,
            'risk_score': 1.0,
            'risk_level': risk_level,
            'safe_score': 0.0,
            'matched_keywords': matched_keywords,
            'detection_method': 'token_rule'
        }

    return {
        'text': url,
        'is_grooming': False,
        'is_malicious': False,
        'predicted_label': 0,
        'risk_score': 0.0,
        'risk_level': 'low',
        'safe_score': 1.0,
        'matched_keywords': [],
        'detection_method': 'token_rule'
    }

def predict_url_batch(urls):
    """
    Predict for multiple URLs.
    
    Args:
        urls (list): List of URLs to analyze
        
    Returns:
        list: List of prediction results
    """
    results = []
    for url in urls:
        results.append(predict_url(url))
    return results

