"""
Interactive terminal test for the best grooming model.
Type a message and get an immediate prediction.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.models.grooming_model.predict_grooming_enhanced import predict_grooming_with_confidence


def main():
    print("Enter text to test the model. Type 'exit' to quit.")
    while True:
        try:
            text = input("> ").strip()
        except EOFError:
            print()
            break

        if text.lower() in {"exit", "quit", "q"}:
            print("bye")
            break

        if not text:
            print("Please enter some text.")
            continue

        result = predict_grooming_with_confidence(text)
        if "error" in result:
            print(f"Error: {result['error']}")
            continue

        print(
            {
                "probability": result.get("probability"),
                "risk_level": result.get("risk_level"),
                "is_grooming": result.get("is_grooming"),
                "confidence": result.get("confidence"),
                "safe_prob": result.get("safe_prob"),
            }
        )


if __name__ == "__main__":
    main()
