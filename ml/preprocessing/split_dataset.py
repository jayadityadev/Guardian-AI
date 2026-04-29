import os
import sys
import csv
import pandas as pd
from sklearn.model_selection import train_test_split

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from ml.preprocessing.clean_text import preprocess_grooming_data


def load_labeled_text_csv(file_path):
    """Load a two-column text/label CSV with robust error handling."""
    try:
        # Try pandas first with UTF-8
        df = pd.read_csv(file_path, encoding='utf-8')
        return df
    except (UnicodeDecodeError, pd.errors.ParserError):
        pass
    
    try:
        # Fallback: UTF-8 with error ignore
        df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
        return df
    except Exception as e:
        print(f"Warning: Parsing CSV with errors ignored: {e}")
        # Last resort: manual parsing with error tolerance
        rows = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            header = f.readline()
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.rsplit(',', 1)
                if len(parts) != 2:
                    continue
                
                text, label = parts
                try:
                    rows.append({'text': text, 'label': int(label)})
                except (ValueError, IndexError):
                    continue
        
        return pd.DataFrame(rows) if rows else pd.DataFrame(columns=['text', 'label'])

def split_grooming_dataset():
    """Split grooming dataset into train/val/test."""
    data_path = os.path.join(BASE_DIR, "data", "raw", "grooming_dataset.csv")
    
    df = load_labeled_text_csv(data_path)
    
    # Remove rows with NaN values and convert text to string
    df = df.dropna(subset=['text', 'label'])
    df['text'] = df['text'].astype(str)
    df['label'] = df['label'].astype(int)
    
    print(f"Total samples: {len(df)}")
    print(f"Grooming (label=1): {(df['label']==1).sum()}")
    print(f"Safe (label=0): {(df['label']==0).sum()}")
    
    # Clean text
    df = preprocess_grooming_data(df)
    
    # Split: 95% train, 5% test (maximize training data)
    train, test = train_test_split(df, test_size=0.05, random_state=42, stratify=df['label'])
    # Use train set for both training and validation (val.csv = train.csv for now)
    val = train.sample(frac=0.2, random_state=42)  # Small subset for monitoring
    
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    train.to_csv(os.path.join(processed_dir, "train.csv"), index=False)
    val.to_csv(os.path.join(processed_dir, "val.csv"), index=False)
    test.to_csv(os.path.join(processed_dir, "test.csv"), index=False)
    
    print(f"\nTrain samples: {len(train)}")
    print(f"Val samples: {len(val)}")
    print(f"Test samples: {len(test)}")
    print("Dataset split complete (95/5 - maximized training data).")


if __name__ == "__main__":
    split_grooming_dataset()
