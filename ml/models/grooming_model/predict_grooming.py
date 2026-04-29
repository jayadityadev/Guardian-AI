import os
import joblib

model = None
MODEL_LOADED = False


def _load_model():
    """Load the trained model from disk when first needed."""
    global model, tokenizer, MODEL_LOADED

    if MODEL_LOADED:
        return

    model_dir = os.path.join(os.path.dirname(__file__), 'saved_model')

    try:
        model = joblib.load(os.path.join(model_dir, 'grooming_classifier.joblib'))
        MODEL_LOADED = True
    except Exception as e:
        raise RuntimeError(f"Model not found at {model_dir}. Train the model first.") from e


def predict_grooming(text):
    """
    Predict grooming risk score for a text.
    
    Args:
        text (str): Input text to analyze
        
    Returns:
        float: Risk score between 0 and 1 (1 = high grooming risk)
    """
    _load_model()
    
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([text])[0]
        return float(probabilities[1])

    prediction = model.predict([text])[0]
    return float(prediction)


def predict_grooming_batch(texts):
    """
    Predict grooming risk scores for multiple texts.
    
    Args:
        texts (list): List of text samples
        
    Returns:
        list: List of risk scores
    """
    _load_model()
    
    scores = []
    for text in texts:
        scores.append(predict_grooming(text))
    return scores

