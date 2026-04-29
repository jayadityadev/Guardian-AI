#!/usr/bin/env python
"""
Guardian AI - ML Pipeline Training Orchestrator
Runs complete preprocessing and training workflow
"""

import os
import sys
import time

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ml.preprocessing.split_dataset import split_grooming_dataset
from ml.models.grooming_model.train_grooming import train_grooming_model
from ml.models.grooming_model.evaluate_grooming import evaluate_grooming_model
from ml.models.url_model.train_url import train_url_model
from ml.models.url_model.evaluate_url import evaluate_url_model


def print_section(title):
    """Print formatted section title."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def main():
    """Run complete ML pipeline."""
    
    print_section("GUARDIAN AI - ML PIPELINE TRAINING")
    print(f"Project root: {PROJECT_ROOT}\n")
    
    start_time = time.time()
    
    # Step 1: Preprocessing
    print_section("STEP 1: DATA PREPROCESSING & SPLITTING")
    try:
        split_grooming_dataset()
        print("\n✓ Grooming dataset split complete")
    except Exception as e:
        print(f"\n✗ Error during preprocessing: {e}")
        return False
    
    # Step 2: Train Grooming Model
    print_section("STEP 2: TRAINING GROOMING DETECTION MODEL")
    try:
        train_grooming_model()
        print("\n✓ Grooming model training complete")
    except Exception as e:
        print(f"\n✗ Error during grooming model training: {e}")
        return False
    
    # Step 3: Evaluate Grooming Model
    print_section("STEP 3: EVALUATING GROOMING DETECTION MODEL")
    try:
        metrics = evaluate_grooming_model('test')
        print("\n✓ Grooming model evaluation complete")
    except Exception as e:
        print(f"\n✗ Error during grooming model evaluation: {e}")
        return False
    
    # Step 4: Train URL Model
    print_section("STEP 4: TRAINING URL CLASSIFICATION MODEL")
    try:
        train_url_model()
        print("\n✓ URL model training complete")
    except Exception as e:
        print(f"\n✗ Error during URL model training: {e}")
        return False
    
    # Step 5: Evaluate URL Model
    print_section("STEP 5: EVALUATING URL CLASSIFICATION MODEL")
    try:
        metrics = evaluate_url_model()
        print("\n✓ URL model evaluation complete")
    except Exception as e:
        print(f"\n✗ Error during URL model evaluation: {e}")
        return False
    
    # Summary
    elapsed = time.time() - start_time
    print_section("TRAINING PIPELINE COMPLETE")
    print(f"Total time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    print("\nModels ready for inference:")
    print("  - Grooming detection: ml/models/grooming_model/saved_model/")
    print("  - URL classification: ml/models/url_model/saved_model/")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
