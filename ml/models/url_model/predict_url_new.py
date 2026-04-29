import os
from urllib.parse import urlparse

SUSPICIOUS_TLDS = {
    'cf', 'ga', 'gq', 'ml', 'tk', 'top', 'xyz', 'ru', 'cn', 'info', 'biz', 'live'
}

TRUSTED_DOMAINS = {
    'amazon.com', 'microsoft.com', 'github.com', 'apple.com', 'linkedin.com',
    'netflix.com', 'dropbox.com', 'wikipedia.org', 'bankofamerica.com', 'chase.com',
    'openai.com', 'twitter.com', 'facebook.com', 'instagram.com', 'youtube.com',
    'google.com', 'microsoftonline.com', 'paypal.com', 'aws.amazon.com',
    'office.com', 'wellsfargo.com', 'citibank.com', 'ibm.com'
}


def _is_trusted_domain(hostname):
    """Return True when hostname is exactly a trusted domain or its subdomain."""
    h = (hostname or '').lower()
    for d in TRUSTED_DOMAINS:
        if h == d or h.endswith('.' + d):
            return True
    return False


def _count_phishing_indicators(url):
    """
    Count phishing indicators in URL.
    If ANY indicator is found, the URL is flagged as malicious.
    Risk score = (indicator_count / max_possible_indicators)
    """
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parsed.query.lower()
    hostname = netloc.split(':')[0]
    parts = hostname.split('.') if hostname else []
    tld = parts[-1] if parts else ''

    indicators = 0
    max_possible = 22  # Total possible indicators
    
    # Check keyword indicators
    keywords = ['login', 'verify', 'confirm', 'secure', 'account', 'update', 'alert', 
                'password', 'session', 'bank', 'support', 'free', 'claim', 'refund']
    for keyword in keywords:
        if keyword in url.lower():
            indicators += 1
    
    # Special check for signin variants
    if 'signin' in url.lower() or 'sign-in' in url.lower():
        indicators += 1
    
    # Path indicators
    if 'doc' in path or 'share' in path:
        indicators += 1
    if 'verify' in path or 'login' in path or 'secure' in path:
        indicators += 1
    
    # Structural indicators
    if tld in SUSPICIOUS_TLDS:
        indicators += 2
    if hostname.replace('.', '').isdigit() and hostname != '':
        indicators += 2
    if parsed.scheme == 'http':
        indicators += 1
    if url.count('-') >= 2:
        indicators += 1
    if len(parts) >= 4:
        indicators += 1
    
    # Normalize to 0-1 range
    risk_score = min(indicators / max_possible, 1.0)

    # Risk levels aligned to dataset behavior:
    # low => no phishing indicators, medium/high => phishing-like behavior.
    if indicators == 0:
        risk_level = 'low'
    elif indicators <= 3:
        risk_level = 'medium'
    else:
        risk_level = 'high'

    return risk_score, indicators, risk_level


def predict_url(url):
    """
    Predict if URL is malicious using indicator-based detection.
    
    Args:
        url (str): URL to analyze
        
    Returns:
        dict: Prediction results with risk score and classification
    """
    parsed = urlparse(url)
    hostname = parsed.netloc.lower().split(':')[0]

    # Trusted HTTPS domains are considered safe to reduce false positives.
    if parsed.scheme == 'https' and _is_trusted_domain(hostname):
        return {
            'url': url,
            'is_grooming': False,
            'is_malicious': False,
            'predicted_label': 0,
            'risk_score': 0.0,
            'risk_level': 'low',
            'safe_score': 1.0,
            'indicator_count': 0,
            'detection_method': 'trusted-allowlist'
        }

    risk_score, indicator_count, risk_level = _count_phishing_indicators(url)

    # User rule: if risk level is low -> false, else true.
    is_grooming = risk_level != 'low'
    predicted_label = 1 if is_grooming else 0
    
    return {
        'url': url,
        'is_grooming': is_grooming,
        'is_malicious': is_grooming,
        'predicted_label': predicted_label,
        'risk_score': round(risk_score, 4),
        'risk_level': risk_level,
        'safe_score': round(1.0 - risk_score, 4),
        'indicator_count': indicator_count,
        'detection_method': 'indicator-based-risk-level'
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
