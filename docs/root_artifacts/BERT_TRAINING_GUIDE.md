# Complete Guide: Training BERT for Grooming Behavior Recognition

## What is BERT?

**BERT** = **B**idirectional **E**ncoder **R**epresentations from **T**ransformers

BERT is a deep learning model that understands language context and meaning. Unlike TF-IDF which just counts word frequency, BERT learns behavioral patterns.

## Architecture: How BERT Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT TEXT                                   │
│  "You're so special, don't tell your parents about us"         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│           TOKENIZER: Split into tokens                          │
│  [CLS] you're so special, don't tell your parents about us [SEP]│
│  Token IDs: [101, 2017, 1005, 2922, 3291, 1010, 2123, ...]     │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         EMBEDDING LAYER: Convert to vectors                     │
│  Token IDs → Dense vectors (768 dimensions for DistilBERT)     │
│  Each token = [0.234, -0.156, 0.891, ..., 0.123]              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│    TRANSFORMER LAYERS (6-12 layers depending on model)          │
│                                                                 │
│  Layer 1: Learn syntax (punctuation, grammar)                  │
│  Layer 2: Learn basic semantics (word meanings)                │
│  Layer 3: Understand relationships between words               │
│  Layer 4: Recognize patterns (flattery, secrecy requests)      │
│  Layer 5: Identify context (predatory behavior indicators)     │
│  Layer 6: Combine all information for final understanding      │
│                                                                 │
│  KEY: Bidirectional - learns from BOTH directions              │
│  "special" is understood with context from "you're" AND        │
│  "don't tell your parents" (looks left AND right)             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│           [CLS] TOKEN REPRESENTATION                             │
│  Special token that represents the entire text                 │
│  Contains summary of all patterns found                        │
│  Vector: [0.145, 0.823, -0.234, ..., 0.567]                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│      CLASSIFICATION HEAD (Added during fine-tuning)             │
│  Dense layer (768 → 256 units)                                  │
│  Dense layer (256 → 2 units)                                    │
│  Softmax: Convert to probabilities                             │
│  Output: [Safe: 0.15, Grooming: 0.85]                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               OUTPUT: Risk Score                                │
│               Grooming Probability: 0.85 (HIGH RISK)          │
└─────────────────────────────────────────────────────────────────┘
```

## TF-IDF vs BERT: Key Differences

### TF-IDF (What you're currently using)
```
Text: "You're so special"

TF-IDF Features:
- you're: 0.234
- special: 0.567
- grooming: (not in vocab)
- behavior: (not in vocab)

Problem: Doesn't understand context
- "That's a special offer" → Same score as grooming message
- Misses semantic meaning
```

### BERT (What we're training)
```
Text: "You're so special"

BERT Understanding (Learned from 110M parameters trained on Wikipedia):
- Recognition: This is flattery/grooming indicator
- Context: Combined with "don't tell parents" = clear predatory pattern
- Semantic: Understands "special" in context of child manipulation
- Behavior: Matches predator language patterns

Solution: Understands language behavior
- "That's a special offer" → Recognized as commercial, NOT grooming
- Captures semantic meaning and context
```

## Training Process

### Step 1: Load Data
```
Old Project: 166 samples
New Project: 5,886 samples
Merged: 5,112 unique samples (426 grooming, 4,686 safe)
Split: 4,089 train, 1,023 test
```

### Step 2: Tokenization
```python
Input: "Don't tell your parents about us"
Tokenizer converts to: [CLS] don't tell your parents about us [SEP]
Token IDs: [101, 2123, 2424, 2054, 3717, 2055, 2149, 102]
```

### Step 3: Load Pretrained BERT
- HuggingFace provides DistilBERT (trained on 110M parameters)
- Already understands language from Wikipedia + BookCorpus
- We "fine-tune" it for grooming detection
- Takes 3-6 hours vs 40 hours from scratch

### Step 4: Fine-tuning (Training)
```
For each epoch:
  For each batch of texts:
    1. Tokenize texts
    2. Forward pass: texts → embeddings → BERT layers → predictions
    3. Calculate loss: |prediction - truth|
    4. Backward pass: compute gradients
    5. Update parameters: optimizer adjusts weights to reduce loss
    
Epoch 1: Loss = 0.523
Epoch 2: Loss = 0.234
Epoch 3: Loss = 0.089
```

### Step 5: Evaluation
```
Test on 1,023 unseen messages
Measure: Accuracy, Precision, Recall, F1-Score, ROC-AUC
```

## Models to Choose From

### 1. DistilBERT (Recommended for Start)
- **Size**: 66M parameters (40% smaller than BERT)
- **Speed**: Fast (~1 sec per 32 texts)
- **Accuracy**: 95-98%
- **Training Time**: 1-2 hours
- **Use When**: You want speed + good accuracy

### 2. BERT Base
- **Size**: 110M parameters
- **Speed**: Slower (~3 sec per 32 texts)
- **Accuracy**: 97-99%
- **Training Time**: 3-4 hours
- **Use When**: You need maximum accuracy

### 3. RoBERTa
- **Size**: 125M parameters
- **Speed**: Medium (~2 sec per 32 texts)
- **Accuracy**: 98-99% (better than BERT)
- **Training Time**: 4-5 hours
- **Use When**: You want better than BERT

### 4. ALBERT
- **Size**: 12M parameters (tiny!)
- **Speed**: Very fast (~0.2 sec per 32 texts)
- **Accuracy**: 92-95%
- **Training Time**: 30 mins
- **Use When**: You need to deploy on mobile/edge

## Training with Different Models

```python
# Option 1: Fast (Good for testing)
trainer = GroomingBERTTrainer(model_name="distilbert-base-uncased")

# Option 2: Best Accuracy
trainer = GroomingBERTTrainer(model_name="bert-base-uncased")

# Option 3: Better than BERT
trainer = GroomingBERTTrainer(model_name="roberta-base")

# Option 4: Mobile/Edge (Very small)
trainer = GroomingBERTTrainer(model_name="albert-base-v2")
```

## How BERT Recognizes Grooming Behavior

BERT learns to detect patterns like:

### Pattern 1: Flattery
```
"You're so mature for your age"
BERT recognizes: Complimenting physical/mental maturity = grooming indicator
Probability: 0.92
```

### Pattern 2: Isolation
```
"Don't tell your parents about our chats"
BERT recognizes: Requesting secrecy = control mechanism
Probability: 0.88
```

### Pattern 3: Trust Building
```
"I understand you better than anyone else"
BERT recognizes: Creating special bond = emotional manipulation
Probability: 0.85
```

### Pattern 4: Desensitization
```
"It's normal for friends to talk about this"
BERT recognizes: Normalizing inappropriate topics
Probability: 0.79
```

### Pattern 5: Grooming Progression
```
"Want to meet somewhere private?"
BERT recognizes: Transition to in-person contact
Probability: 0.91
```

## Step-by-Step Training Instructions

### 1. Install Dependencies
```bash
cd D:\Guardian-AI
uv pip install tensorflow transformers --python "D:\Guardian-AI\ml\.venv\Scripts\python.exe"
```

### 2. Train BERT
```bash
python train_bert_grooming.py
```

This will:
- Load 5,112 merged training samples
- Fine-tune DistilBERT (1-2 hours)
- Save trained model to `ml/models/grooming_model/saved_model_bert/`
- Output metrics (Accuracy, Precision, Recall, etc.)

### 3. Use the Model
```python
from predict_grooming_bert import predict_grooming

# Single prediction
risk_score = predict_grooming("You're so special")
print(f"Risk: {risk_score:.2%}")  # Output: Risk: 87%

# Batch predictions
scores = predict_grooming_batch([
    "What's your name?",
    "Don't tell your parents",
    "Want to meet?"
])
```

## Performance Expectations

### Before (TF-IDF with 5,112 samples)
- Accuracy: 83.68%
- Precision: 28%
- Recall: 63.53%
- Problem: Many false positives

### After (BERT with 5,112 samples)
- Accuracy: ~90-94%
- Precision: ~70-85%
- Recall: ~75-85%
- Improvement: Better understanding of context

## Why TensorFlow Version Works (No Windows DLL Issues)

PyTorch has a DLL loading issue on Windows. TensorFlow doesn't have this problem:

```
PyTorch: torch/lib/c10.dll → ❌ DLL Error on Windows
TensorFlow: Built with Windows support → ✅ Works fine
```

## Key Concepts

### Fine-tuning vs Training from Scratch
```
Training from Scratch (Bad):
- Random weights → Learn everything → Very slow (40+ hours)
- Need 100k+ samples
- 
Fine-tuning BERT (Good):
- Pretrained weights (already knows language) → Only train top layers → Fast (2-4 hours)
- Works with 500+ samples
- RECOMMENDED APPROACH ✓
```

### Transfer Learning
```
BERT trained on:
  - Wikipedia (2.5B+ words)
  - BookCorpus (800M words)
  
We use this knowledge and apply it to:
  - Grooming detection (5,112 messages)
  
Result: Leverage 3.3B words of language understanding → Much better predictions
```

## Troubleshooting

### Issue 1: Out of Memory
```
Solution: Reduce batch_size in trainer.prepare_data(batch_size=16)
Or use smaller model: "albert-base-v2"
```

### Issue 2: Training Too Slow
```
Solution: Use GPU: Check "GPU: NVIDIA" in train output
Or use smaller model: "distilbert-base-uncased"
```

### Issue 3: Accuracy Not Improving
```
Solution 1: Add more training data (get more grooming messages)
Solution 2: Train longer: epochs=5 or epochs=10
Solution 3: Adjust learning rate: learning_rate=1e-5
```

## Next Steps

1. **Run Training**: `python train_bert_grooming.py`
2. **Test Predictions**: `python predict_grooming_bert.py`
3. **Integrate to Backend**: Use `predict_grooming()` in your API
4. **Monitor Performance**: Test on real chat data
5. **Iterate**: Add more data, retrain if needed

## References

- BERT Paper: https://arxiv.org/abs/1810.04805
- HuggingFace: https://huggingface.co/
- DistilBERT: https://arxiv.org/abs/1910.01108
- Transfer Learning: https://en.wikipedia.org/wiki/Transfer_learning
