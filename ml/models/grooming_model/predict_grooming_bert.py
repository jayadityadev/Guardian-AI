"""
BERT Grooming Detection Predictor
Uses fine-tuned DistilBERT model for predator behavior recognition
PyTorch backend for Windows compatibility and fast startup
"""

from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Global model cache
_model = None
_tokenizer = None


def _get_model_path():
    """Get path to saved BERT model"""
    current_dir = Path(__file__).parent
    return current_dir / "saved_model_bert"


def _load_model():
    """Lazy-load the BERT model and tokenizer from local folder or Hugging Face Hub"""
    global _model, _tokenizer
    
    if _model is not None and _tokenizer is not None:
        return _model, _tokenizer
    
    model_path = _get_model_path()
    
    # 1. Try local path first
    if model_path.exists():
        try:
            _tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _model = AutoModelForSequenceClassification.from_pretrained(str(model_path)).to(device)
            print(f"Successfully loaded BERT model from local path: {model_path} on {device}")
            return _model, _tokenizer
        except Exception as e:
            print(f"Warning: Failed to load from local path: {e}. Falling back to Hugging Face Hub...")
            
    # 2. Fall back to Hugging Face Hub
    hf_model_id = "jayadityadev/guardian-ai-grooming"
    try:
        print(f"Loading BERT model from Hugging Face Hub: {hf_model_id} ...")
        _tokenizer = AutoTokenizer.from_pretrained(hf_model_id)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model = AutoModelForSequenceClassification.from_pretrained(hf_model_id).to(device)
        print(f"Successfully loaded BERT model from Hugging Face Hub on {device}")
    except Exception as e:
        raise RuntimeError(
            f"Failed to load BERT model from both local path and Hugging Face Hub.\n"
            f"Local error: model not found at {model_path}\n"
            f"Hugging Face Hub error ({hf_model_id}): {e}\n"
            f"Please run the Google Colab training notebook to generate the model, or push it to your Hugging Face account."
        )
        
    return _model, _tokenizer


def predict_grooming(text, threshold=0.5):
    """
    Predict grooming risk score for a single text
    
    Args:
        text (str): Text message to analyze
        threshold (float): Probability threshold for grooming classification (default: 0.5)
    
    Returns:
        dict: {
            'probability': float (0.0-1.0),
            'is_grooming': bool (True if probability >= threshold),
            'confidence': float (confidence score)
        }
    """
    model, tokenizer = _load_model()
    
    text = str(text).strip()
    
    if not text:
        return {
            'probability': 0.0,
            'is_grooming': False,
            'confidence': 1.0,
            'error': 'Empty text provided'
        }
    
    try:
        # Determine device model is loaded on
        device = next(model.parameters()).device
        
        # Tokenize input
        inputs = tokenizer(
            text,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        ).to(device)
        
        # Get prediction
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits
        
        # Apply softmax to get probabilities
        probs = torch.softmax(logits, dim=1)
        grooming_prob = float(probs[0, 1].item())  # Probability of class 1 (grooming)
        safe_prob = float(probs[0, 0].item())
        
        is_grooming = grooming_prob >= threshold
        confidence = max(grooming_prob, safe_prob)
        
        return {
            'probability': round(grooming_prob, 4),
            'is_grooming': is_grooming,
            'confidence': round(confidence, 4),
            'safe_prob': round(safe_prob, 4)
        }
    
    except Exception as e:
        return {
            'probability': 0.0,
            'is_grooming': False,
            'confidence': 0.0,
            'error': str(e)
        }


def predict_grooming_batch(texts, threshold=0.5):
    """
    Predict grooming risk scores for multiple texts
    
    Args:
        texts (list): List of text messages
        threshold (float): Probability threshold for grooming classification
    
    Returns:
        list: List of prediction dicts
    """
    return [predict_grooming(text, threshold) for text in texts]


def predict_grooming_with_confidence(text):
    """
    Predict grooming with detailed confidence metrics
    
    Args:
        text (str): Text to analyze
    
    Returns:
        dict: Detailed prediction with confidence scores
    """
    result = predict_grooming(text)
    
    if 'error' in result:
        return result
    
    # Add risk level classification
    prob = result['probability']
    if prob >= 0.8:
        risk_level = 'CRITICAL'
    elif prob >= 0.6:
        risk_level = 'HIGH'
    elif prob >= 0.4:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'
    
    result['risk_level'] = risk_level
    
    return result


if __name__ == '__main__':
    # Test the predictor
    test_texts = [
        "hey beautiful, want to chat privately?",
        "what time are you free today?",
        "I'm 25 and looking for someone to talk to",
        "do you have any photos?"
    ]
    
    print("BERT Grooming Predictions Test")
    print("=" * 80)
    
    for text in test_texts:
        result = predict_grooming_with_confidence(text)
        print(f"\nText: {text}")
        print(f"  Probability: {result.get('probability', 'N/A')}")
        print(f"  Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"  Confidence: {result.get('confidence', 'N/A')}")
