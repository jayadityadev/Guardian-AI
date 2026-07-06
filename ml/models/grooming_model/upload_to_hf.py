import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo

def upload_model():
    print("Hugging Face Model Uploader")
    print("===========================")
    
    token = os.getenv("HF_TOKEN")
    if not token:
        token = input("Please enter your Hugging Face Access Token (write permission): ").strip()
        if not token:
            print("Error: Hugging Face Token is required.")
            return

    repo_id = "jayadityadev/guardian-ai-grooming"
    
    # 1. Create repo if it doesn't exist
    try:
        print(f"Creating repository '{repo_id}' on Hugging Face Hub (if it doesn't exist)...")
        create_repo(repo_id=repo_id, token=token, repo_type="model", exist_ok=True)
    except Exception as e:
        print(f"Note/Error creating repo: {e}")

    # 2. Upload folder
    model_path = Path(__file__).parent / "saved_model_bert"
    if not model_path.exists():
        print(f"Error: Local model folder not found at {model_path}")
        print("Please extract your saved_model_bert.zip to that folder first.")
        return

    print(f"Uploading files from '{model_path}' to HF Hub '{repo_id}'...")
    api = HfApi()
    try:
        api.upload_folder(
            folder_path=str(model_path),
            repo_id=repo_id,
            repo_type="model",
            token=token
        )
        print("\n[SUCCESS] Model successfully uploaded to Hugging Face Hub!")
        print(f"View it here: https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"\n[FAIL] Failed to upload model folder: {e}")

if __name__ == '__main__':
    upload_model()
