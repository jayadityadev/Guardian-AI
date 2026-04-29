"""
Grooming Detection Predictor - Enhanced Sklearn Model
Best-performing model for backend integration
Uses TF-IDF vectorizer with Logistic Regression
"""

from pathlib import Path
import joblib
import numpy as np

# Global model cache
_model = None
_vectorizer = None


def _get_model_path():
    """Get path to saved enhanced sklearn model"""
    current_dir = Path(__file__).parent
    return current_dir / "saved_model_enhanced"


def _load_model():
    """Lazy-load the sklearn model and vectorizer"""
    global _model, _vectorizer
    
    if _model is not None and _vectorizer is not None:
        return _model, _vectorizer
    
    model_path = _get_model_path()
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"Enhanced sklearn model not found at {model_path}\n"
            f"Run: python train_grooming_enhanced.py"
        )
    
    try:
        _vectorizer = joblib.load(model_path / "vectorizer.joblib")
        _model = joblib.load(model_path / "grooming_classifier.joblib")
        print(f"Successfully loaded enhanced sklearn model from {model_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to load sklearn model: {e}")
    
    return _model, _vectorizer


def predict_grooming(text, threshold=0.5):
    """
    Predict grooming risk score for a single text
    
    Args:
        text (str): Text message to analyze
        threshold (float): Probability threshold for grooming classification (default: 0.5)
    
    Returns:
        float: Grooming probability (0.0-1.0)
    """
    model, vectorizer = _load_model()
    
    text = str(text).strip()
    
    if not text:
        return 0.0
    
    try:
        # Vectorize the text
        text_vector = vectorizer.transform([text])
        
        # Get prediction probability for grooming class
        proba = model.predict_proba(text_vector)[0]
        grooming_prob = proba[1]  # Probability of class 1 (grooming)
        
        return round(float(grooming_prob), 4)
    
    except Exception as e:
        print(f"Error in prediction: {e}")
        return 0.0


def predict_grooming_batch(texts, threshold=0.5):
    """
    Predict grooming risk scores for multiple texts
    
    Args:
        texts (list): List of text messages
        threshold (float): Probability threshold
    
    Returns:
        list: List of grooming probabilities
    """
    return [predict_grooming(text, threshold) for text in texts]


def predict_grooming_with_confidence(text, threshold=0.5):
    """
    Predict grooming with detailed confidence metrics
    
    Args:
        text (str): Text to analyze
        threshold (float): Classification threshold
    
    Returns:
        dict: {
            'probability': float (0.0-1.0),
            'is_grooming': bool,
            'confidence': float,
            'risk_level': str (CRITICAL/HIGH/MEDIUM/LOW),
            'safe_prob': float
        }
    """
    model, vectorizer = _load_model()
    
    text = str(text).strip()
    
    if not text:
        return {
            'probability': 0.0,
            'is_grooming': False,
            'confidence': 1.0,
            'risk_level': 'LOW',
            'safe_prob': 1.0
        }
    
    try:
        # Vectorize and predict
        text_vector = vectorizer.transform([text])
        proba = model.predict_proba(text_vector)[0]
        
        grooming_prob = float(proba[1])
        safe_prob = float(proba[0])
        is_grooming = grooming_prob >= threshold
        confidence = max(grooming_prob, safe_prob)
        
        # Determine risk level
        if grooming_prob >= 0.8:
            risk_level = 'CRITICAL'
        elif grooming_prob >= 0.6:
            risk_level = 'HIGH'
        elif grooming_prob >= 0.4:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'probability': round(grooming_prob, 4),
            'is_grooming': is_grooming,
            'confidence': round(confidence, 4),
            'risk_level': risk_level,
            'safe_prob': round(safe_prob, 4)
        }
    
    except Exception as e:
        return {
            'probability': 0.0,
            'is_grooming': False,
            'confidence': 0.0,
            'risk_level': 'UNKNOWN',
            'error': str(e)
        }


if __name__ == '__main__':
    # Quick test
    print("Enhanced Sklearn Model Test")
    print("=" * 80)
    
    test_texts = [
        "hey beautiful, want to chat privately?",
        "what do you look like?",
        "Hi, how are you today?",
        "can you send me a photo?"
    ]
    
    for text in test_texts:
        result = predict_grooming_with_confidence(text)
        print(f"\nText: {text}")
        print(f"  Probability: {result.get('probability')}")
        print(f"  Risk Level: {result.get('risk_level')}")
        print(f"  Status: {'GROOMING' if result.get('is_grooming') else 'SAFE'}")
