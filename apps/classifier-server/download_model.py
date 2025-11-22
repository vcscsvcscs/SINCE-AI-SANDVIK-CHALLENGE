"""
Download the spare parts model from Hugging Face Hub
"""
import os
from huggingface_hub import snapshot_download
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
HF_REPO_ID = "juskuu/sandvik_classifier"
LOCAL_MODEL_PATH = "./spare_parts_model"
HF_TOKEN = os.getenv("HF_TOKEN")  # Optional: only needed for private repos

def download_model():
    """Download model from Hugging Face Hub"""

    print(f"\nDownloading model from {HF_REPO_ID}...")

    try:
        # Download all model files directly without loading into memory
        snapshot_download(
            repo_id=HF_REPO_ID,
            local_dir=LOCAL_MODEL_PATH,
            token=HF_TOKEN  # Uses token if provided, otherwise public access
        )

        print(f"\n✓ Model downloaded successfully to {LOCAL_MODEL_PATH}")
        print(f"\nYou can now use it with:")
        print(f'  classifier = pipeline("text-classification", model="{LOCAL_MODEL_PATH}")')
        return True

    except Exception as e:
        print(f"\n❌ Error downloading model: {e}")
        print(f"\nMake sure:")
        print(f"  1. You have internet connection")
        print(f"  2. The repository exists: https://huggingface.co/{HF_REPO_ID}")
        print(f"  3. If it's private, run: huggingface-cli login")
        return False

if __name__ == "__main__":
    download_model()
