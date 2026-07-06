import os
from fastapi import FastAPI, HTTPException
import modal

# 1. Define the Modal App
app = modal.App("guardian-ai-ml")

# 2. Define the container environment
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "huggingface-hub",
        "groq",
        "litellm",
        "numpy",
        "scikit-learn",
        "requests",
        "fastapi",
        "pydantic"
    )
)

# Create FastAPI app
web_app = FastAPI()

# 3. Mount local ml directory
# This uploads your local ml/ folder code into the serverless container
ml_mount = modal.Mount.from_local_dir(
    "./ml",
    remote_path="/root/ml"
)

# 4. Define the inference endpoint
# Auto-packages local environment keys as container secrets during deploy
@app.function(
    image=image,
    mounts=[ml_mount],
    secrets=[
        modal.Secret.from_dict({
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
            "NVIDIA_API_KEY": os.getenv("NVIDIA_API_KEY", "")
        })
    ]
)
@modal.asgi_app()
def inference_endpoint():
    import sys
    sys.path.insert(0, "/root")
    
    from ml.models.grooming_model.analyse import analyse
    
    @web_app.post("/infer")
    def infer(payload: dict):
        messages = payload.get("messages")
        if not messages:
            raise HTTPException(status_code=400, detail="Missing 'messages' in payload")
            
        try:
            # Run the E2E analysis pipeline
            result = analyse(messages)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    @web_app.get("/health")
    def health():
        return {"status": "ok"}
            
    return web_app
