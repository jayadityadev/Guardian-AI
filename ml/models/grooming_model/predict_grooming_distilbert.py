"""
DistilBERT Grooming Detection Predictor
Uses fine-tuned DistilBERT model for predator behavior recognition
"""

import torch
from pathlib import Path
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import sys

# Global model cache
_model = None
_tokenizer = None
_device = None


def _get_model_path():
    """Get path to saved DistilBERT model"""
    current_dir = Path(__file__).parent
    return current_dir / "saved_model_distilbert"


def _load_model():
    """Lazy-load the DistilBERT model"""
    global _model, _tokenizer, _device
    
    if _model is not None:
        return _model, _tokenizer, _device
    
    model_path = _get_model_path()
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"DistilBERT model not found at {model_path}\n"
            f"Run: python ml/models/grooming_model/train_grooming_distilbert.py"
        )
    
    _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    _tokenizer = DistilBertTokenizer.from_pretrained(str(model_path))
    _model = DistilBertForSequenceClassification.from_pretrained(str(model_path))
    _model.to(_device)
    _model.eval()
    
    return _model, _tokenizer, _device


def predict_grooming(text):
    """
    Predict grooming risk score for a single text
    
    Args:
        text (str): Text message to analyze
    
    Returns:
        float: Grooming probability (0.0-1.0)
    """
    model, tokenizer, device = _load_model()
    
    text = str(text).strip()
    
    # Tokenize input
    inputs = tokenizer(
        text,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )
    
    # Move to device
    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)
    
    # Get prediction
    with torch.no_grad():
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        logits = outputs.logits
        
        # Apply softmax to get probabilities
        probs = torch.softmax(logits, dim=1)
        grooming_prob = probs[0, 1].item()  # Probability of class 1 (grooming)
    
    return grooming_prob


def predict_grooming_batch(texts):
    """
    Predict grooming risk scores for multiple texts
    
    Args:
        texts (list): List of text messages
    
    Returns:
        list: List of grooming probabilities
    """
    model, tokenizer, device = _load_model()
    
    texts = [str(t).strip() for t in texts]
    results = []
    
    # Process in batches
    batch_size = 16
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        
        # Tokenize batch
        inputs = tokenizer(
            batch_texts,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Move to device
        input_ids = inputs['input_ids'].to(device)
        attention_mask = inputs['attention_mask'].to(device)
        
        # Get predictions
        with torch.no_grad():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            logits = outputs.logits
            
            # Get probabilities
            probs = torch.softmax(logits, dim=1)
            grooming_probs = probs[:, 1].cpu().numpy()  # Probability of grooming
            
            results.extend(grooming_probs.tolist())
    
    return results


if __name__ == "__main__":
    # Test the model
    test_texts = [
        "Hey, how are you feeling today?",
        "You're so special, no one understands you like I do",
        "Let's keep this between us, okay?",
    ]
    
    print("Testing DistilBERT Grooming Predictor:\n")
    
    for text in test_texts:
        score = predict_grooming(text)
        prediction = "🔴 GROOMING" if score > 0.5 else "🟢 SAFE"
        print(f"{text}")
        print(f"  → {prediction} ({score:.4f})\n")
