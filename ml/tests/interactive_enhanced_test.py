import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))
#!/usr/bin/env python3
"""
Interactive Enhanced Grooming Model Tester
Test the enhanced model with your own custom inputs
"""

import sys
from pathlib import Path
import joblib
import re
import json

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Load model and vectorizer
model_dir = project_root / "ml" / "models" / "grooming_model" / "saved_model_enhanced"

try:
    model = joblib.load(model_dir / 'grooming_classifier.joblib')
    vectorizer = joblib.load(model_dir / 'vectorizer.joblib')
    
    with open(model_dir / 'metrics.json', 'r') as f:
        metrics = json.load(f)
    
    print("✓ Enhanced Grooming Model loaded successfully\n")
except FileNotFoundError:
    print("❌ Model not found. Train first with:")
    print("   python ml/models/grooming_model/train_grooming_enhanced.py")
    sys.exit(1)


def clean_text(text):
    """Match training preprocessing"""
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s?!.]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def predict_grooming(text):
    """Predict grooming risk"""
    clean = clean_text(text)
    X = vectorizer.transform([clean])
    
    if hasattr(model, 'predict_proba'):
        prob = model.predict_proba(X)[0, 1]
    else:
        prob = model.predict(X)[0]
    
    return prob


def display_model_info():
    """Show model information"""
    print("\n" + "="*70)
    print("  MODEL INFORMATION")
    print("="*70)
    print(f"\nBest Model: {metrics['best_model']}")
    print(f"Dataset Size: {metrics['dataset_size']:,} samples")
    print(f"Training Samples: {metrics['train_size']:,}")
    print(f"Test Samples: {metrics['test_size']:,}")
    print(f"\nPerformance Metrics:")
    for metric, value in metrics['all_models'][metrics['best_model']].items():
        print(f"  {metric}: {value:.4f}")
    print("\n" + "="*70)


def interactive_test():
    """Interactive testing mode"""
    print("\n" + "="*70)
    print("  INTERACTIVE GROOMING DETECTION TEST")
    print("="*70)
    print("\nEnter messages to test. The model will predict if they contain")
    print("grooming behavior patterns.")
    print("\nRisk Threshold: 0.5 (≥ 0.5 = Grooming, < 0.5 = Safe)")
    print("Type 'menu' to return to main menu.\n")
    
    correct = 0
    total = 0
    
    while True:
        try:
            text = input("📝 Enter message (or 'menu'): ").strip()
            
            if text.lower() == 'menu':
                break
            
            if not text:
                print("❌ Please enter some text.\n")
                continue
            
            # Get prediction
            risk_score = predict_grooming(text)
            is_grooming = risk_score > 0.5
            
            # Display prediction
            print(f"\n{'='*70}")
            if is_grooming:
                print(f"🔴 GROOMING DETECTED")
            else:
                print(f"🟢 SAFE MESSAGE")
            
            print(f"Risk Score: {risk_score:.4f}")
            print(f"Confidence: {max(risk_score, 1-risk_score)*100:.1f}%")
            print(f"{'='*70}\n")
            
            # Get feedback
            while True:
                feedback = input("Was this prediction correct? (y/n/skip): ").strip().lower()
                
                if feedback == 'y':
                    correct += 1
                    print("✅ Marked as correct\n")
                    break
                elif feedback == 'n':
                    print("❌ Marked as incorrect\n")
                    break
                elif feedback == 'skip':
                    print("⏭️  Skipped\n")
                    break
                else:
                    print("❓ Please enter y, n, or skip: ", end="")
            
            total += 1
            
            if total > 0:
                accuracy = (correct / total) * 100
                print(f"Your Accuracy So Far: {accuracy:.1f}% ({correct}/{total})\n")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}\n")
            continue
    
    if total > 0:
        print(f"\n📊 Final Testing Results:")
        print(f"   Correct: {correct}/{total}")
        print(f"   Accuracy: {(correct/total)*100:.1f}%\n")
    
    return correct, total


def batch_test():
    """Test multiple messages at once"""
    print("\n" + "="*70)
    print("  BATCH TEST MODE")
    print("="*70)
    print("\nEnter messages one per line. Type 'done' when finished.\n")
    
    messages = []
    while True:
        msg = input(f"Message {len(messages)+1} (or 'done'): ").strip()
        if msg.lower() == 'done':
            break
        if msg:
            messages.append(msg)
    
    if not messages:
        print("No messages entered.\n")
        return
    
    print(f"\n{'='*70}")
    print(f"{'Message':<50} | {'Prediction':<12} | {'Risk':<8}")
    print(f"{'='*70}")
    
    for msg in messages:
        risk = predict_grooming(msg)
        pred = "🔴 GROOMING" if risk > 0.5 else "🟢 SAFE"
        msg_display = msg[:48] + ".." if len(msg) > 50 else msg
        print(f"{msg_display:<50} | {pred:<12} | {risk:.4f}")
    
    print(f"{'='*70}\n")


def examples_mode():
    """Show example test cases"""
    print("\n" + "="*70)
    print("  EXAMPLE TEST CASES")
    print("="*70 + "\n")
    
    examples = [
        ("What's your name?", "Safe question"),
        ("How was school today?", "Normal conversation"),
        ("You're so special to me", "Flattery - suspicious"),
        ("Don't tell your parents about us", "Secrecy - grooming indicator"),
        ("Can we chat privately?", "Privacy request - suspicious"),
        ("I love talking to you", "Normal affection"),
        ("You're so mature for your age", "Age comment - grooming indicator"),
        ("Let's meet somewhere private", "Meeting request - suspicious"),
    ]
    
    for text, description in examples:
        risk = predict_grooming(text)
        pred = "🔴 GROOMING" if risk > 0.5 else "🟢 SAFE"
        
        print(f"Text: {text}")
        print(f"Description: {description}")
        print(f"Result: {pred} (Risk: {risk:.4f})\n")


def main():
    """Main menu"""
    print("\n" + "="*70)
    print("  GUARDIAN AI - ENHANCED GROOMING MODEL TESTER")
    print("="*70)
    print(f"\nModel: {metrics['best_model']}")
    print(f"Training Data: {metrics['dataset_size']:,} samples")
    print(f"Test Accuracy: {metrics['all_models'][metrics['best_model']]['test_accuracy']:.2%}")
    
    while True:
        print("\n" + "-"*70)
        print("What would you like to do?")
        print("  1. Interactive Test (one message at a time)")
        print("  2. Batch Test (multiple messages)")
        print("  3. View Examples")
        print("  4. Model Information")
        print("  5. Exit")
        print("-"*70)
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            interactive_test()
        elif choice == '2':
            batch_test()
        elif choice == '3':
            examples_mode()
        elif choice == '4':
            display_model_info()
        elif choice == '5':
            print("\n✅ Goodbye!\n")
            break
        else:
            print("❌ Invalid option. Please select 1-5.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
