## ML Data Preparation — steps performed

This document records the exact preprocessing and augmentation steps performed during the hackathon.

1. Clean & dedupe
   - Script: `ml/preprocessing/clean_and_split.py`
   - Removes exact duplicates by normalized text + label, normalizes whitespace and case.
   - Writes: `data/processed/clean_train.csv`, `clean_val.csv`, `clean_test.csv`.

2. Enforce strict no-overlap
   - Script: `ml/preprocessing/enforce_no_overlap.py`
   - Removes any normalized-text collisions across splits and writes `final_train.csv`, `final_val.csv`, `final_test.csv`.

3. Hinglish augmentation
   - Script: `ml/preprocessing/augment_hinglish.py`
   - Rule-based code-mix augmentations for positive class (label `1`). Default multiplier = 3 (produces ~3x positives).
   - Writes: `data/processed/augmented_train.csv`.

Current status (after running scripts):

- `data/processed/final_train.csv`: 4045 rows (3710 label `0`, 335 label `1`)
- `data/processed/final_val.csv`: 497 rows (459 label `0`, 38 label `1`)
- `data/processed/final_test.csv`: 503 rows (464 label `0`, 39 label `1`)
- `data/processed/augmented_train.csv`: 4715 rows (3710 label `0`, 1005 label `1`)

What I prepared but did NOT run:

- `ml/train_prepare.py` — helper script that loads `augmented_train.csv`, fits a `TfidfVectorizer`, and writes `ml/models/grooming_model/vectorizer.joblib` and a training manifest. (Training step is intentionally not executed.)
- `ml/train_prepared.py` — the actual handoff trainer. It consumes `data/processed/augmented_train.csv`, `final_val.csv`, and `final_test.csv`, trains a class-weighted TF-IDF + LogisticRegression model, tunes the threshold on validation data, and saves the trained model plus summaries. I did not run it here.

How to reproduce locally (from repo root):

```bash
python3 ml/preprocessing/clean_and_split.py
python3 ml/preprocessing/enforce_no_overlap.py
python3 ml/preprocessing/augment_hinglish.py

# then (optional) prepare vectorizer before training
python3 ml/train_prepare.py

# or run the full prepared-data trainer (does not clean data again)
python3 ml/train_prepared.py
```

If you want stricter augmentation or different rules (back-translation / LLM paraphrase), I can add an optional LLM-backed augmenter, but that requires API keys and runtime time.
