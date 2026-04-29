#!/usr/bin/env python3
import os
import json
from pathlib import Path

print("\n" + "="*80)
print("  MODEL TRAINING STATUS CHECK")
print("="*80 + "\n")

model_base = Path(r"D:\Guardian-AI\ml\models\grooming_model")

# Check for BERT
bert_dir = model_base / "saved_model_bert"
if bert_dir.exists():
    print("✅ BERT Model:")
    bert_files = list(bert_dir.glob("*"))
    print(f"   Location: {bert_dir}")
    print(f"   Files: {len(bert_files)}")
    
    if (bert_dir / "metrics.json").exists():
        with open(bert_dir / "metrics.json") as f:
            metrics = json.load(f)
        print(f"   Accuracy: {metrics.get('accuracy', 'N/A')}")
else:
    print("❌ BERT Model: NOT READY (training in progress or failed)")

# Check for Enhanced Sklearn
sklearn_dir = model_base / "saved_model_enhanced"
if sklearn_dir.exists():
    print("\n✅ Enhanced Sklearn Model:")
    sklearn_files = list(sklearn_dir.glob("*"))
    print(f"   Location: {sklearn_dir}")
    print(f"   Files: {len(sklearn_files)}")
    
    if (sklearn_dir / "metrics.json").exists():
        with open(sklearn_dir / "metrics.json") as f:
            metrics = json.load(f)
        print(f"   Best Model: {metrics.get('best_model', 'N/A')}")
        print(f"   Accuracy: {metrics['all_models'][metrics['best_model']].get('test_accuracy', 'N/A'):.4f}")
else:
    print("\n❌ Enhanced Sklearn Model: NOT FOUND")

# Check for original model
orig_dir = model_base / "saved_model"
if orig_dir.exists():
    print("\n✅ Original Model:")
    orig_files = list(orig_dir.glob("*"))
    print(f"   Location: {orig_dir}")
    print(f"   Files: {len(orig_files)}")
else:
    print("\n❌ Original Model: NOT FOUND")

print("\n" + "="*80)
