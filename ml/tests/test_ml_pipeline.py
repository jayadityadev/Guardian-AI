import sys
from pathlib import Path
import json

# Ensure project root is in sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.data_loader import load_demo_dataset
from ml.models.grooming_model.predict_grooming import predict_grooming
from ml.models.grooming_model.analyse import analyse

# Expected JSON Contract Keys
EXPECTED_KEYS = {
    "session_id": str,
    "platform": str,
    "timestamp": str,
    "risk_score": int,
    "confidence": float,
    "grooming_stage": str,
    "flags": list,
    "categories": list,
    "stage_progression": dict,
    "recommendation": str,
    "drift_signals": dict
}

def test_model_loading_and_prediction():
    print("\n--- Test 1: Model Loading & Basic Prediction ---")
    try:
        score_grooming = predict_grooming("Don't tell your parents, this is our special secret.")
        score_normal = predict_grooming("Hey, let's play Minecraft tomorrow after school.")
        print(f"Grooming text score: {score_grooming:.4f}")
        print(f"Normal text score:   {score_normal:.4f}")
        
        assert score_grooming > score_normal, "Predatory text score should be higher than normal text score!"
        print("[PASS] Model successfully loaded and distinguishes predatory vs normal text.")
    except Exception as e:
        print("[FAIL] Test failed:", str(e))
        sys.exit(1)

def test_json_contract_conformance(scenario_name, messages):
    print(f"\n--- Test 2: Conformance for {scenario_name} ---")
    try:
        print(f"Testing {len(messages)} messages.")
        
        result = analyse(messages)
        print("Analysis Result:")
        print(json.dumps(result, indent=2))
        
        # Verify JSON Contract Keys & Types
        for key, expected_type in EXPECTED_KEYS.items():
            assert key in result, f"Missing key: {key}"
            assert isinstance(result[key], expected_type), f"Key {key} type mismatch: expected {expected_type}, got {type(result[key])}"
            
        print(f"[PASS] Output for {scenario_name} conforms to API contract.")
        return result
    except Exception as e:
        print("[FAIL] Test failed:", str(e))
        sys.exit(1)

def main():
    test_model_loading_and_prediction()
    
    high_risk_messages = [
        {"sender": "stranger", "text": "hey", "timestamp": "2025-01-01T22:14:00Z"},
        {"sender": "child", "text": "hello", "timestamp": "2025-01-01T22:14:10Z"},
        {"sender": "stranger", "text": "you're so mature for your age", "timestamp": "2025-01-01T22:14:20Z"},
        {"sender": "stranger", "text": "don't tell your parents about this", "timestamp": "2025-01-01T22:14:30Z"},
        {"sender": "stranger", "text": "I'll buy you Robux if you keep this between us", "timestamp": "2025-01-01T22:14:40Z"}
    ]
    
    low_risk_messages = [
        {"sender": "friend", "text": "Hey, what games do you like?", "timestamp": "2025-01-01T22:14:00Z"},
        {"sender": "child", "text": "Let's play Minecraft later", "timestamp": "2025-01-01T22:14:10Z"},
        {"sender": "friend", "text": "Sure, see you at school tomorrow", "timestamp": "2025-01-01T22:14:20Z"}
    ]
    
    hinglish_messages = [
        {"sender": "stranger", "text": "hey", "timestamp": "2025-01-01T22:14:00Z"},
        {"sender": "child", "text": "hello", "timestamp": "2025-01-01T22:14:10Z"},
        {"sender": "stranger", "text": "tu bahut samajhdar hai", "timestamp": "2025-01-01T22:14:20Z"},
        {"sender": "stranger", "text": "yaar kisi ko mat batana", "timestamp": "2025-01-01T22:14:30Z"},
        {"sender": "stranger", "text": "free coins dunga bhai", "timestamp": "2025-01-01T22:14:40Z"},
        {"sender": "stranger", "text": "sirf hamare beech mein rahe", "timestamp": "2025-01-01T22:14:50Z"}
    ]
    
    high_risk_res = test_json_contract_conformance("high_risk", high_risk_messages)
    low_risk_res = test_json_contract_conformance("low_risk", low_risk_messages)
    hinglish_res = test_json_contract_conformance("hinglish", hinglish_messages)
    
    print("\n--- Summary Verification ---")
    print(f"High risk score: {high_risk_res['risk_score']}")
    print(f"Low risk score:  {low_risk_res['risk_score']}")
    print(f"Hinglish score:  {hinglish_res['risk_score']}")
    
    assert high_risk_res['risk_score'] >= 50, "High risk payload score should be >= 50!"
    assert low_risk_res['risk_score'] < 50, "Low risk payload score should be < 50!"
    assert hinglish_res['risk_score'] >= 50, "Hinglish payload score should be >= 50!"
    
    print("\nAll ML pipeline tests PASSED successfully!")

if __name__ == '__main__':
    main()
