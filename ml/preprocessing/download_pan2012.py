import os
import zipfile
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST_DIR = ROOT / "data" / "pan2012"
ZIP_PATH = ROOT / "data" / "pan12-sexual-predator-identification.zip"

def download_file(url, dest_path):
    print(f"Downloading {url} to {dest_path}...")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    
    total_size = int(r.headers.get('content-length', 0))
    downloaded = 0
    
    with open(dest_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
    print("\nDownload complete.")

def extract_zip(zip_path, dest_dir):
    print(f"Extracting {zip_path} to {dest_dir}...")
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)
    print("Extraction complete.")

def list_files(dest_dir):
    print("Files in extracted directory:")
    count = 0
    for root, dirs, files in os.walk(dest_dir):
        level = root.replace(str(dest_dir), '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files[:10]:
            print(f"{subindent}{f}")
        if len(files) > 10:
            print(f"{subindent}... and {len(files) - 10} more files")
        count += len(files)
    print(f"Total files: {count}")

def main():
    url = "https://zenodo.org/api/records/3713280/files/pan12-sexual-predator-identification-test-and-training.zip/content"
    if not ZIP_PATH.exists():
        download_file(url, ZIP_PATH)
    else:
        print(f"Zip file already exists at {ZIP_PATH}, skipping download.")
        
    extract_zip(ZIP_PATH, DEST_DIR)
    list_files(DEST_DIR)
    
    # Remove the zip file to save space
    if ZIP_PATH.exists():
        os.remove(ZIP_PATH)
        print("Removed downloaded zip file to save disk space.")

if __name__ == '__main__':
    main()
