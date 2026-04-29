import re

def clean_text(text):
    """Clean and normalize text data."""
    # Convert to lowercase
    text = text.lower()
    # Replace URLs
    text = re.sub(r'http\S+|www\S+', '[URL]', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep apostrophes
    text = re.sub(r"[^a-zA-Z0-9\s']", '', text)
    return text.strip()


def preprocess_grooming_data(df):
    """Preprocess grooming dataset."""
    df['text'] = df['text'].apply(clean_text)
    return df
