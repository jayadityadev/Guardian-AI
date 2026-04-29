"""
Interactive BERT Grooming Detection Test
Type text messages and get real-time grooming risk predictions
"""

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.models.grooming_model.predict_grooming_bert import predict_grooming_with_confidence


def print_header():
    """Print welcome header"""
    print("\n" + "=" * 80)
    print("BERT GROOMING DETECTION - INTERACTIVE TEST".center(80))
    print("=" * 80)
    print("\nEnter text messages to test for grooming behavior.")
    print("Type 'exit' or 'quit' to end the test.\n")


def print_result(result):
    """Print formatted prediction result"""
    print("\n" + "-" * 80)
    
    if 'error' in result:
        print(f"ERROR: {result['error']}")
        return
    
    probability = result.get('probability', 0)
    risk_level = result.get('risk_level', 'UNKNOWN')
    confidence = result.get('confidence', 0)
    
    # Color-coded risk level
    if risk_level == 'CRITICAL':
        status = "🔴 CRITICAL"
    elif risk_level == 'HIGH':
        status = "🟠 HIGH"
    elif risk_level == 'MEDIUM':
        status = "🟡 MEDIUM"
    else:
        status = "🟢 LOW"
    
    print(f"\nPrediction Result:")
    print(f"  Risk Level:      {status}")
    print(f"  Probability:     {probability:.2%} grooming")
    print(f"  Safe Prob:       {result.get('safe_prob', 1-probability):.2%}")
    print(f"  Confidence:      {confidence:.2%}")
    print(f"  Classification:  {'GROOMING DETECTED' if result.get('is_grooming') else 'SAFE'}")
    print("-" * 80)


def main():
    """Main interactive loop"""
    print_header()
    
    try:
        test_count = 0
        
        while True:
            # Get user input
            text = input("\nEnter text to analyze (or 'exit'): ").strip()
            
            # Check for exit
            if text.lower() in ['exit', 'quit', 'q']:
                print("\n" + "=" * 80)
                print(f"Test Complete! Analyzed {test_count} messages.".center(80))
                print("=" * 80 + "\n")
                break
            
            # Skip empty input
            if not text:
                print("Please enter some text to analyze.")
                continue
            
            # Get prediction
            result = predict_grooming_with_confidence(text)
            
            # Display result
            print_result(result)
            test_count += 1
            
            # Show example predictions
            if test_count == 1:
                print("\nTip: Try these examples:")
                print("  - 'hey beautiful, want to chat privately?'")
                print("  - 'What do you look like?'")
                print("  - 'Hello, how are you today?'")
                print("  - 'Do your parents know we are talking?'")
    
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        print(f"Analyzed {test_count} messages before exit.\n")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
