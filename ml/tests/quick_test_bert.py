import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
"""
BERT Grooming Detection - Sample Predictions
Test the model with various text samples
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.models.grooming_model.predict_grooming_bert import predict_grooming_with_confidence


def test_samples():
    """Test BERT with sample texts"""
    
    samples = [
        ("hey beautiful want to chat privately", "Potential grooming"),
        ("what do you look like", "Asking for appearance"),
        ("do your parents know were talking", "Hiding from parents"),
        ("send me your photos", "Requesting images"),
        ("hi how are you today", "Safe greeting"),
        ("whats your favorite book", "Safe topic"),
        ("lets play a game", "Innocent activity"),
        ("i can help you with money", "Bribery attempt"),
        ("you dont need to tell anyone", "Encouraging secrecy"),
    ]
    
    print("\n" + "=" * 100)
    print("BERT GROOMING DETECTION - SAMPLE PREDICTIONS".center(100))
    print("=" * 100)
    
    for i, (text, description) in enumerate(samples, 1):
        result = predict_grooming_with_confidence(text)
        
        prob = result.get('probability', 0)
        risk = result.get('risk_level', 'UNKNOWN')
        
        # Format output
        print(f"\n{i}. [{description}]")
        print(f"   Text: \"{text}\"")
        print(f"   Risk Level:  {risk}")
        print(f"   Probability: {prob:.2%} grooming")
        print(f"   Status:      {'GROOMING DETECTED ⚠️' if result.get('is_grooming') else 'SAFE ✓'}")
    
    print("\n" + "=" * 100 + "\n")


if __name__ == "__main__":
    try:
        print("\nLoading BERT model...")
        test_samples()
        print("Test completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
