"""
Comprehensive BERT Predictions Test Suite
Tests BERT model predictions against known grooming and safe text examples
"""

import sys
from pathlib import Path
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml.models.grooming_model.predict_grooming_bert import (
    predict_grooming,
    predict_grooming_batch,
    predict_grooming_with_confidence
)


class GroomingTestSuite:
    """Test suite for BERT grooming detection model"""
    
    def __init__(self):
        self.test_cases = {
            'grooming_high_confidence': [
                "hey beautiful, want to chat privately?",
                "I've been thinking about you. Can we talk in private?",
                "You seem special. Do you have photos to share?",
                "What do you look like? Send me a picture",
                "You're so pretty, I'd love to get to know you better",
                "Let's keep this conversation between us, okay?",
                "I'm much older but I find you very attractive",
                "Do your parents know you're talking to me?",
                "I can help you with money if you spend time with me",
                "You don't need to tell anyone about our chats"
            ],
            'safe_high_confidence': [
                "Hi, how are you doing today?",
                "What's your favorite book?",
                "I went to the store yesterday",
                "The weather is nice today",
                "What time is the meeting tomorrow?",
                "I finished my homework",
                "Let's play some games",
                "My favorite color is blue",
                "I like pizza and ice cream",
                "See you at school tomorrow"
            ],
            'ambiguous': [
                "Can we talk?",
                "What's up?",
                "You seem nice",
                "Let's be friends",
                "Tell me about yourself"
            ]
        }
        
        self.results = {
            'grooming': {'correct': 0, 'total': 0, 'predictions': []},
            'safe': {'correct': 0, 'total': 0, 'predictions': []},
            'ambiguous': {'correct': 0, 'total': 0, 'predictions': []}
        }
    
    def run_all_tests(self, threshold=0.5):
        """Run all test cases"""
        print("\n" + "=" * 100)
        print("BERT GROOMING DETECTION TEST SUITE".center(100))
        print("=" * 100)
        
        # Test grooming texts
        print("\n[1] Testing HIGH-CONFIDENCE GROOMING texts (should have probability > 0.7)")
        print("-" * 100)
        self._test_category('grooming_high_confidence', 'grooming', threshold, min_prob=0.7)
        
        # Test safe texts
        print("\n[2] Testing HIGH-CONFIDENCE SAFE texts (should have probability < 0.3)")
        print("-" * 100)
        self._test_category('safe_high_confidence', 'safe', threshold, max_prob=0.3)
        
        # Test ambiguous
        print("\n[3] Testing AMBIGUOUS texts")
        print("-" * 100)
        self._test_category('ambiguous', 'ambiguous', threshold)
        
        # Print summary
        self._print_summary(threshold)
    
    def _test_category(self, test_key, category, threshold, min_prob=None, max_prob=None):
        """Test a category of texts"""
        texts = self.test_cases[test_key]
        self.results[category]['total'] = len(texts)
        
        for i, text in enumerate(texts, 1):
            result = predict_grooming_with_confidence(text)
            
            # Check for errors
            if 'error' in result:
                print(f"  {i}. ERROR: {result.get('error')}")
                continue
            
            prob = result['probability']
            risk_level = result['risk_level']
            is_correct = False
            
            # Determine if prediction is correct
            if min_prob is not None and prob >= min_prob:
                is_correct = True
            elif max_prob is not None and prob <= max_prob:
                is_correct = True
            elif min_prob is None and max_prob is None:
                is_correct = True  # Ambiguous, no strict requirement
            
            if is_correct:
                self.results[category]['correct'] += 1
            
            # Print result
            status = " [OK]" if is_correct else " [MISMATCH]"
            print(f"  {i}. {status} Prob: {prob:.4f} | Risk: {risk_level:8s} | '{text[:60]}...'")
            
            self.results[category]['predictions'].append({
                'text': text,
                'probability': prob,
                'risk_level': risk_level,
                'expected_category': category
            })
    
    def _print_summary(self, threshold):
        """Print test summary"""
        print("\n" + "=" * 100)
        print("TEST SUMMARY".center(100))
        print("=" * 100)
        
        total_tests = 0
        total_correct = 0
        
        for category in ['grooming', 'safe', 'ambiguous']:
            correct = self.results[category]['correct']
            total = self.results[category]['total']
            total_tests += total
            total_correct += correct
            
            if total > 0:
                accuracy = (correct / total) * 100
                print(f"\n{category.upper():12s} | Accuracy: {accuracy:6.2f}% ({correct}/{total} correct)")
        
        print("\n" + "-" * 100)
        overall_accuracy = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        print(f"{'OVERALL':12s} | Accuracy: {overall_accuracy:6.2f}% ({total_correct}/{total_tests} correct)")
        print("=" * 100)
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        if overall_accuracy >= 90:
            print("  Model performance is EXCELLENT. Ready for production deployment.")
        elif overall_accuracy >= 80:
            print("  Model performance is GOOD. Consider additional fine-tuning for edge cases.")
        elif overall_accuracy >= 70:
            print("  Model performance is ACCEPTABLE. Recommend further training on ambiguous cases.")
        else:
            print("  Model performance is POOR. Recommend retraining with better data or different architecture.")
    
    def batch_test(self):
        """Test batch prediction capability"""
        print("\n" + "=" * 100)
        print("BATCH PREDICTION TEST".center(100))
        print("=" * 100)
        
        test_batch = [
            "Hey, want to chat privately?",
            "What's your favorite food?",
            "Let me see your photos",
            "I enjoy reading books"
        ]
        
        print("\nTesting batch prediction with 4 texts...")
        results = predict_grooming_batch(test_batch)
        
        for text, result in zip(test_batch, results):
            print(f"  Text: '{text}'")
            print(f"    -> Probability: {result.get('probability', 'N/A')}, Risk: {result.get('risk_level', 'N/A')}\n")
        
        print("Batch test completed successfully!")
    
    def threshold_analysis(self):
        """Analyze predictions at different thresholds"""
        print("\n" + "=" * 100)
        print("THRESHOLD SENSITIVITY ANALYSIS".center(100))
        print("=" * 100)
        
        sample_texts = [
            ("High grooming probability", "Send me your photos baby"),
            ("Medium probability", "Tell me about yourself"),
            ("Low probability", "Hello, how are you?")
        ]
        
        thresholds = [0.3, 0.5, 0.7, 0.9]
        
        print(f"\n{'Text':<40} | {'Probability':<12} |", end="")
        for t in thresholds:
            print(f" {t:.1f} ", end="")
        print()
        print("-" * 100)
        
        for label, text in sample_texts:
            result = predict_grooming(text, threshold=0.5)
            prob = result.get('probability', 0)
            print(f"{label:<40} | {prob:<12.4f} |", end="")
            
            for threshold in thresholds:
                decision = "GROOMING" if prob >= threshold else "SAFE"
                print(f" {'G' if prob >= threshold else 'S':<3} ", end="")
            print()
        
        print("=" * 100)
        print("\nNote: G=Grooming detected, S=Safe detected")


def main():
    """Main test execution"""
    print("\n" + ">" * 100)
    print("BERT GROOMING DETECTION PREDICTION TEST".center(100))
    print(">" * 100)
    
    try:
        suite = GroomingTestSuite()
        
        # Run comprehensive tests
        suite.run_all_tests(threshold=0.5)
        
        # Run batch test
        suite.batch_test()
        
        # Run threshold analysis
        suite.threshold_analysis()
        
        # Save results to JSON
        results_path = Path(__file__).parent / "bert_test_results.json"
        with open(results_path, 'w') as f:
            json.dump(suite.results, f, indent=2)
        print(f"\n\nTest results saved to: {results_path}")
        
        print("\n" + ">" * 100)
        print("ALL TESTS COMPLETED SUCCESSFULLY".center(100))
        print(">" * 100 + "\n")
        
    except Exception as e:
        print(f"\nERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
