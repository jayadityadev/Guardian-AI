import zipfile
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]
PAN_DIR = ROOT / "data" / "pan2012"

def main():
    zips = list(PAN_DIR.glob("*.zip"))
    for z in zips:
        print(f"Extracting nested zip: {z.name} ...")
        dest_dir = PAN_DIR / z.stem
        dest_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(z, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
        print(f"Extracted to {dest_dir}")
        
        # Remove the nested zip to save space
        os.remove(z)
        print(f"Removed nested zip: {z.name}")

    # List files under PAN_DIR
    print("Files structure:")
    for root, dirs, files in os.walk(PAN_DIR):
        level = root.replace(str(PAN_DIR), '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        for f in files[:10]:
            print(f"{indent}    {f}")
        if len(files) > 10:
            print(f"{indent}    ... and {len(files) - 10} more files")

if __name__ == '__main__':
    main()
