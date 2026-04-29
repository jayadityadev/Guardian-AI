#!/usr/bin/env python3
"""
Test script for Guardian AI ML models
Tests grooming detection and URL classification models
"""

import sys
import os
from pathlib import Path

# Add repo root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from ml.models.grooming_model.predict_grooming import predict_grooming, predict_grooming_batch
from ml.models.url_model.predict_url import predict_url, predict_url_batch


def test_grooming_model():
    """Test grooming detection model with various test cases"""
    print("\n" + "="*60)
    print("  TESTING GROOMING DETECTION MODEL")
    print("="*60 + "\n")
    
    test_cases = [
        # Safe conversations
        ("What's the weather like today?", False),
        ("Can you help me with my homework?", False),
        ("I'm going to the park tomorrow", False),
        ("Do you like pizza?", False),
        
        # Suspicious/grooming patterns
        ("Hey sweetie, how are you feeling today?", True),
        ("You're so special, do your parents know you talk to me?", True),
        ("Don't tell anyone about our conversations", True),
        ("You look beautiful in that photo", True),
    ]
    
    print(f"{'Text':<50} | {'Prediction':<12} | {'Risk Score':<12}")
    print("-" * 80)
    
    for text, expected_grooming in test_cases:
        risk_score = predict_grooming(text)
        prediction = "🔴 GROOMING" if risk_score > 0.5 else "🟢 SAFE"
        label = "(Expected Grooming)" if expected_grooming else "(Expected Safe)"
        
        text_display = text[:48] + ".." if len(text) > 50 else text
        print(f"{text_display:<50} | {prediction:<12} | {risk_score:.4f} {label}")
    
    # Test batch prediction
    print("\n--- Batch Prediction Test ---")
    batch_texts = [
        "This is a normal conversation about school",
        "Hey baby, you're so cute",
        "What time is lunch?",
    ]
    
    print(f"Testing {len(batch_texts)} texts in batch...")
    batch_results = predict_grooming_batch(batch_texts)
    
    for text, score in zip(batch_texts, batch_results):
        prediction = "🔴 GROOMING" if score > 0.5 else "🟢 SAFE"
        print(f"  {text:<45} → {prediction:<12} ({score:.4f})")


def test_url_model():
    """Test URL classification model"""
    print("\n" + "="*60)
    print("  TESTING URL CLASSIFICATION MODEL")
    print("="*60 + "\n")
    
    test_urls = [
        ("https://google.com", False),
        ("https://github.com", False),
        ("https://www.youtube.com", False),
        ("https://verify-account-login.com", True),
        ("https://confirm-identity-secure.co", True),
        ("https://update-password-alert.xyz", True),
    ]
    
    print(f"{'URL':<50} | {'Classification':<15} | {'Risk Score':<12}")
    print("-" * 80)
    
    for url, expected_malicious in test_urls:
        result = predict_url(url)
        is_malicious = result['is_malicious']
        risk_score = result['risk_score']
        
        classification = "🔴 MALICIOUS" if is_malicious else "🟢 SAFE"
        label = "(Expected Malicious)" if expected_malicious else "(Expected Safe)"
        
        url_display = url[:48] + ".." if len(url) > 50 else url
        print(f"{url_display:<50} | {classification:<15} | {risk_score:.4f} {label}")
    
    # Test batch prediction
    print("\n--- Batch Prediction Test ---")
    batch_urls = [
        "https://google.com",
        "https://fake-login-verify.com",
        "https://github.com",
    ]
    
    print(f"Testing {len(batch_urls)} URLs in batch...")
    batch_results = predict_url_batch(batch_urls)
    
    for result in batch_results:
        classification = "🔴 MALICIOUS" if result['is_malicious'] else "🟢 SAFE"
        print(f"  {result['url']:<45} → {classification:<12} ({result['risk_score']:.4f})")


def main():
    print("\n" + "="*60)
    print("  GUARDIAN AI - MODEL TESTING")
    print("="*60)
    
    try:
        test_grooming_model()
        test_url_model()
        
        print("\n" + "="*60)
        print("  ✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
