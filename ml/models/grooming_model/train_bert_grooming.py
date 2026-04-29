"""
Complete Guide: Training BERT for Grooming Behavior Recognition

This implementation uses TensorFlow + Transformers (avoids PyTorch Windows compatibility issues)
BERT understands language context and can recognize predatory behavior patterns better than TF-IDF
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import json
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

try:
    # Force TensorFlow-only backend (avoid PyTorch)
    import tensorflow as tf
    
    # Import only TensorFlow models (TF prefix)
    from transformers import AutoTokenizer
    from transformers import TFAutoModelForSequenceClassification
    from transformers import create_optimizer
    
    print("TensorFlow and Transformers loaded\n")
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: uv pip install tensorflow transformers --python <python_path>")
    sys.exit(1)
except Exception as e:
    print("Error: PyTorch DLL issue. Uninstall torch: pip uninstall torch -y")
    sys.exit(1)


class GroomingBERTTrainer:
    """Train BERT model for grooming behavior detection"""
    
    def __init__(self, model_name="distilbert-base-uncased"):
        """
        Initialize BERT trainer
        
        Args:
            model_name: HuggingFace model identifier
                - "distilbert-base-uncased": Fast, 40% smaller than BERT
                - "bert-base-uncased": Standard BERT
                - "roberta-base": RoBERTa (better performance)
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.history = None
    
    def load_and_merge_datasets(self):
        """Load and merge grooming datasets from both projects"""
        print("="*70)
        print("  STEP 1: LOADING AND MERGING DATASETS")
        print("="*70 + "\n")
        
        try:
            # Load old project data
            old_grooming = pd.read_csv(
                r'D:\major\child_preditor\childshield-ai\data\raw\grooming_dataset.csv',
                encoding='utf-8',
                on_bad_lines='skip'
            )
        except:
            print("Old project dataset not found")
            old_grooming = pd.DataFrame()
        
        # Load new project data
        new_grooming = pd.read_csv(
            r'D:\Guardian-AI\data\raw\grooming_dataset.csv',
            encoding='utf-8',
            on_bad_lines='skip'
        )
        
        # Merge if old data exists
        if len(old_grooming) > 0:
            merged = pd.concat([old_grooming, new_grooming], ignore_index=True)
        else:
            merged = new_grooming
        
        # Clean
        merged = merged.drop_duplicates()
        merged = merged.dropna()
        
        # Extract
        texts = merged.iloc[:, 0].astype(str).tolist()
        labels = merged.iloc[:, -1].astype(int).tolist()
        
        print(f"Total samples: {len(merged)}")
        print(f"  - Grooming: {sum(labels)} ({100*sum(labels)//len(labels)}%)")
        print(f"  - Safe: {len(labels) - sum(labels)} ({100*(len(labels)-sum(labels))//len(labels)}%)\n")
        
        return texts, labels
    
    def prepare_data(self, texts, labels, max_length=128, batch_size=32):
        """
        Tokenize texts and create TensorFlow datasets
        
        BERT Process:
        1. Tokenizer converts text → token IDs
        2. Adds [CLS] at start, [SEP] at end
        3. Pads/truncates to max_length
        4. Creates attention masks
        """
        print("="*70)
        print("  STEP 2: TOKENIZING AND PREPARING DATA")
        print("="*70 + "\n")
        
        print(f"Loading tokenizer: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Split data
        train_texts, test_texts, train_labels, test_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        print(f"Train: {len(train_texts)} samples")
        print(f"Test: {len(test_texts)} samples\n")
        
        print("Tokenizing texts...")
        
        # Tokenize training data
        train_encodings = self.tokenizer(
            train_texts,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_tensors='tf'
        )
        
        # Tokenize test data
        test_encodings = self.tokenizer(
            test_texts,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_tensors='tf'
        )
        
        print(f"Tokens shape: {train_encodings['input_ids'].shape}\n")
        
        # Create TensorFlow datasets
        train_dataset = tf.data.Dataset.from_tensor_slices((
            dict(train_encodings),
            train_labels
        )).shuffle(1000).batch(batch_size)
        
        test_dataset = tf.data.Dataset.from_tensor_slices((
            dict(test_encodings),
            test_labels
        )).batch(batch_size)
        
        return train_dataset, test_dataset, test_texts, test_labels
    
    def build_model(self, num_labels=2):
        """
        Load pretrained BERT and add classification head
        
        Architecture:
        [Input Text]
             ↓
        [Tokenizer: text → tokens]
             ↓
        [BERT Embedding: tokens → vector]
             ↓
        [BERT Transformer Layers: extract patterns]
             ↓
        [Classification Head: binary classifier]
             ↓
        [Output: Grooming probability]
        """
        print("="*70)
        print("  STEP 3: BUILDING BERT MODEL")
        print("="*70 + "\n")
        
        print(f"Loading model: {self.model_name}")
        
        self.model = TFAutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=num_labels
        )
        
        print(f"Model loaded successfully")
        print(f"Parameters: {self.model.count_params():,}\n")
        
        return self.model
    
    def compile_model(self, learning_rate=2e-5):
        """
        Compile model with optimizer and loss function
        
        Why these settings?
        - AdamW: Optimizer that decays learning rate (good for fine-tuning)
        - learning_rate=2e-5: Standard for BERT fine-tuning
        - SparseCategoricalCrossentropy: For classification
        """
        print("Compiling model...")
        
        # Create optimizer
        optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
        
        # Compile
        self.model.compile(
            optimizer=optimizer,
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=['accuracy']
        )
        
        print("Model compiled\n")
    
    def train(self, train_dataset, test_dataset, epochs=3):
        """
        Train BERT on grooming dataset
        
        Process:
        1. Forward pass: text → predictions
        2. Compute loss: compare with true labels
        3. Backward pass: compute gradients
        4. Update weights: optimizer adjusts parameters
        Repeat for each epoch
        """
        print("="*70)
        print("  STEP 4: TRAINING BERT MODEL")
        print("="*70 + "\n")
        
        print(f"Training for {epochs} epochs...\n")
        
        self.history = self.model.fit(
            train_dataset,
            validation_data=test_dataset,
            epochs=epochs,
            verbose=1
        )
        
        print()
        return self.history
    
    def evaluate(self, test_dataset, test_texts, test_labels):
        """Evaluate model performance"""
        print("="*70)
        print("  STEP 5: EVALUATING MODEL")
        print("="*70 + "\n")
        
        # Get predictions
        predictions = self.model.predict(test_dataset, verbose=0)
        logits = predictions.logits
        preds = np.argmax(logits, axis=1)
        probs = tf.nn.softmax(logits, axis=1).numpy()[:, 1]  # Grooming probability
        
        # Calculate metrics
        accuracy = accuracy_score(test_labels, preds)
        precision = precision_score(test_labels, preds, zero_division=0)
        recall = recall_score(test_labels, preds, zero_division=0)
        f1 = f1_score(test_labels, preds, zero_division=0)
        roc_auc = roc_auc_score(test_labels, probs)
        
        print("=== Test Set Metrics ===")
        print(f"Accuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-Score:  {f1:.4f}")
        print(f"ROC-AUC:   {roc_auc:.4f}\n")
        
        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'roc_auc': float(roc_auc)
        }
    
    def save_model(self, save_path="saved_model_bert"):
        """Save trained model and tokenizer"""
        print("="*70)
        print("  STEP 6: SAVING MODEL")
        print("="*70 + "\n")
        
        save_dir = Path(__file__).resolve().parent / save_path
        save_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Saving to: {save_dir}")
        
        # Save model and tokenizer
        self.model.save_pretrained(str(save_dir))
        self.tokenizer.save_pretrained(str(save_dir))
        
        print("Model saved\n")
        
        return save_dir


def main():
    """Complete BERT training pipeline"""
    
    print("\n" + "="*70)
    print("  BERT GROOMING BEHAVIOR RECOGNITION TRAINING")
    print("="*70 + "\n")
    
    # Initialize trainer
    trainer = GroomingBERTTrainer(model_name="distilbert-base-uncased")
    
    # Step 1: Load data
    texts, labels = trainer.load_and_merge_datasets()
    
    # Step 2: Prepare data
    train_dataset, test_dataset, test_texts, test_labels = trainer.prepare_data(texts, labels)
    
    # Step 3: Build model
    trainer.build_model()
    
    # Step 4: Compile
    trainer.compile_model()
    
    # Step 5: Train
    trainer.train(train_dataset, test_dataset, epochs=3)
    
    # Step 6: Evaluate
    metrics = trainer.evaluate(test_dataset, test_texts, test_labels)
    
    # Step 7: Save
    save_dir = trainer.save_model()
    
    # Save metrics
    with open(save_dir / 'metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("="*70)
    print("  TRAINING COMPLETE")
    print("="*70 + "\n")
    
    print("Next steps:")
    print("1. Test predictions: python test_bert_predictions.py")
    print("2. Integrate to backend: from ml.models.grooming_model.predict_grooming_bert import predict_grooming")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
