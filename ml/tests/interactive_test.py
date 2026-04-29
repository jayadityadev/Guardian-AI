#!/usr/bin/env python3
"""
Interactive Model Tester
Test grooming detection and URL classification with custom inputs
"""

import sys
from pathlib import Path

# Add repo root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from ml.models.grooming_model.predict_grooming import predict_grooming
from ml.models.url_model.predict_url import predict_url


def test_grooming_interactive():
    """Interactive grooming detection testing"""
    print("\n" + "="*70)
    print("  GROOMING DETECTION - INTERACTIVE TEST")
    print("="*70)
    print("\nEnter text messages to test for grooming patterns.")
    print("After each prediction, you can mark if it was correct (y/n).")
    print("Type 'exit' to return to main menu.\n")
    
    correct = 0
    total = 0
    
    while True:
        text = input("📝 Enter message (or 'exit'): ").strip()
        
        if text.lower() == 'exit':
            break
        
        if not text:
            print("❌ Please enter some text.\n")
            continue
        
        risk_score = predict_grooming(text)
        is_grooming = risk_score > 0.5
        prediction = "🔴 GROOMING" if is_grooming else "🟢 SAFE"
        
        print(f"\n{prediction} | Risk Score: {risk_score:.4f}")
        
        # Get user feedback
        feedback = input("Was this prediction correct? (y/n): ").strip().lower()
        
        if feedback == 'y':
            correct += 1
            print("✅ Marked as correct")
        elif feedback == 'n':
            print("❌ Marked as incorrect")
        else:
            print("⏭️  Skipped")
        
        total += 1
        
        if total > 0:
            accuracy = (correct / total) * 100
            print(f"Current accuracy: {accuracy:.1f}% ({correct}/{total})\n")
    
    if total > 0:
        print(f"\n📊 Final Accuracy: {(correct/total)*100:.1f}% ({correct}/{total} correct)")
    
    return correct, total


def test_url_interactive():
    """Interactive URL classification testing"""
    print("\n" + "="*70)
    print("  URL CLASSIFICATION - INTERACTIVE TEST")
    print("="*70)
    print("\nEnter URLs to test for malicious patterns.")
    print("After each prediction, you can mark if it was correct (y/n).")
    print("Type 'exit' to return to main menu.\n")
    
    correct = 0
    total = 0
    
    while True:
        url = input("🔗 Enter URL (or 'exit'): ").strip()
        
        if url.lower() == 'exit':
            break
        
        if not url:
            print("❌ Please enter a URL.\n")
            continue
        
        result = predict_url(url)
        is_malicious = result['is_malicious']
        risk_score = result['risk_score']
        prediction = "🔴 MALICIOUS" if is_malicious else "🟢 SAFE"
        
        print(f"\n{prediction} | Risk Score: {risk_score:.4f}")
        
        # Get user feedback
        feedback = input("Was this prediction correct? (y/n): ").strip().lower()
        
        if feedback == 'y':
            correct += 1
            print("✅ Marked as correct")
        elif feedback == 'n':
            print("❌ Marked as incorrect")
        else:
            print("⏭️  Skipped")
        
        total += 1
        
        if total > 0:
            accuracy = (correct / total) * 100
            print(f"Current accuracy: {accuracy:.1f}% ({correct}/{total})\n")
    
    if total > 0:
        print(f"\n📊 Final Accuracy: {(correct/total)*100:.1f}% ({correct}/{total} correct)")
    
    return correct, total


def main():
    print("\n" + "="*70)
    print("  GUARDIAN AI - INTERACTIVE MODEL TESTER")
    print("="*70)
    
    grooming_correct = 0
    grooming_total = 0
    url_correct = 0
    url_total = 0
    
    while True:
        print("\n" + "-"*70)
        print("What would you like to test?")
        print("  1. Grooming Detection Model")
        print("  2. URL Classification Model")
        print("  3. Both Models")
        print("  4. View Summary")
        print("  5. Exit")
        print("-"*70)
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            g_correct, g_total = test_grooming_interactive()
            grooming_correct += g_correct
            grooming_total += g_total
            
        elif choice == '2':
            u_correct, u_total = test_url_interactive()
            url_correct += u_correct
            url_total += u_total
            
        elif choice == '3':
            g_correct, g_total = test_grooming_interactive()
            grooming_correct += g_correct
            grooming_total += g_total
            
            u_correct, u_total = test_url_interactive()
            url_correct += u_correct
            url_total += u_total
            
        elif choice == '4':
            print("\n" + "="*70)
            print("  TEST SUMMARY")
            print("="*70)
            
            if grooming_total > 0:
                grooming_acc = (grooming_correct / grooming_total) * 100
                print(f"\n🧬 Grooming Detection:")
                print(f"   Accuracy: {grooming_acc:.1f}% ({grooming_correct}/{grooming_total} correct)")
            else:
                print(f"\n🧬 Grooming Detection: No tests conducted")
            
            if url_total > 0:
                url_acc = (url_correct / url_total) * 100
                print(f"\n🔗 URL Classification:")
                print(f"   Accuracy: {url_acc:.1f}% ({url_correct}/{url_total} correct)")
            else:
                print(f"\n🔗 URL Classification: No tests conducted")
            
            if grooming_total > 0 and url_total > 0:
                overall_acc = ((grooming_correct + url_correct) / (grooming_total + url_total)) * 100
                print(f"\n📊 Overall Accuracy: {overall_acc:.1f}%")
            
            print("\n" + "="*70)
            
        elif choice == '5':
            print("\n✅ Thank you for testing! Goodbye.\n")
            break
        
        else:
            print("❌ Invalid option. Please select 1-5.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
