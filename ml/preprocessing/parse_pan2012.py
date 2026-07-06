import xml.etree.ElementTree as ET
from pathlib import Path
import csv
import random

ROOT = Path(__file__).resolve().parents[2]
TEST_XML = ROOT / "data" / "pan2012" / "pan12-sexual-predator-identification-test-corpus-2012-05-21" / "pan12-sexual-predator-identification-test-corpus-2012-05-21" / "pan12-sexual-predator-identification-test-corpus-2012-05-17.xml"
TEST_PREDS_PATH = ROOT / "data" / "pan2012" / "pan12-sexual-predator-identification-test-corpus-2012-05-21" / "pan12-sexual-predator-identification-test-corpus-2012-05-21" / "pan12-sexual-predator-identification-groundtruth-problem1.txt"
TEST_LINES_PATH = ROOT / "data" / "pan2012" / "pan12-sexual-predator-identification-test-corpus-2012-05-21" / "pan12-sexual-predator-identification-test-corpus-2012-05-21" / "pan12-sexual-predator-identification-groundtruth-problem2.txt"
OUT_CSV = ROOT / "data" / "raw" / "grooming_dataset.csv"

def load_predators(path):
    with open(path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def load_suspicious_lines(path):
    susp_lines = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("\t")
                if len(parts) == 2:
                    susp_lines.add((parts[0].strip(), parts[1].strip()))
    return susp_lines

def parse_and_create_dataset():
    print("Loading test predators...")
    predators = load_predators(TEST_PREDS_PATH)
    print("Loaded", len(predators), "predator IDs.")
    
    print("Loading suspicious lines...")
    suspicious_lines = load_suspicious_lines(TEST_LINES_PATH)
    print("Loaded", len(suspicious_lines), "suspicious lines (label=1).")
    
    positives = []
    negatives = []
    
    print("Parsing XML corpus...")
    context = ET.iterparse(TEST_XML, events=('end',))
    
    convo_count = 0
    for event, elem in context:
        if elem.tag == 'conversation':
            convo_id = elem.get('id')
            convo_msgs = elem.findall('message')
            
            # Check if this conversation has any predator
            has_predator = False
            for msg in convo_msgs:
                author = msg.find('author').text
                if author in predators:
                    has_predator = True
                    break
            
            for msg in convo_msgs:
                line = msg.get('line')
                text_elem = msg.find('text')
                text = text_elem.text if (text_elem is not None and text_elem.text is not None) else ""
                text = text.strip()
                if not text:
                    continue
                
                # If this message is in the suspicious lines list, it's a positive (grooming) message
                if (convo_id, line) in suspicious_lines:
                    positives.append((text, 1))
                elif not has_predator:
                    # If conversation has no predators at all, it's a clean negative example
                    negatives.append((text, 0))
            
            convo_count += 1
            if convo_count % 10000 == 0:
                print(f"Processed {convo_count} conversations. Positives so far: {len(positives)}")
            elem.clear()
            
    print(f"Extraction finished. Positives: {len(positives)}, Negatives available: {len(negatives)}")
    
    # We want a high quality sample. Let's take all positives and sample negatives to prevent extreme imbalance
    # Let's take 20000 negatives randomly
    random.seed(42)
    selected_negatives = random.sample(negatives, min(len(negatives), 20000))
    
    all_samples = positives + selected_negatives
    random.shuffle(all_samples)
    
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        for text, label in all_samples:
            writer.writerow([text, label])
            
    print(f"Successfully wrote {len(all_samples)} samples to {OUT_CSV}")

if __name__ == '__main__':
    parse_and_create_dataset()
