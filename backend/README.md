# backend

A project created with FastAPI CLI.

## Quick Start

### Start the development server

```bash
uv run fastapi dev
```

Visit http://localhost:8000

### Deploy to FastAPI Cloud

> FastAPI Cloud is currently in private beta. Join the waitlist at https://fastapicloud.com

```bash
uv run fastapi deploy
```

## Project Structure

- `main.py` - Your FastAPI application
- `pyproject.toml` - Project dependencies

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [FastAPI Cloud](https://fastapicloud.com)

## Using Jaggu's hosted ML inference (recommended for slow uploads)

If the trained model is large and you cannot upload it, Jaggu can host the model
behind a simple HTTP API (e.g. FastAPI) on a machine that has the model files.
Set the following environment variables for the backend to call that service:

- `ML_API_URL` — URL for POST inference requests (expects JSON `{ "messages": [...] }`).
- `ML_API_KEY` — optional bearer token if the inference service is protected.

Example environment (in `.env` or deployment settings):

```
ML_API_URL=https://jaggu.example.internal/api/infer
ML_API_KEY=sk_live_...
```

The backend will attempt a remote call and automatically fall back to the
local mock analyser if the remote request fails. For local testing you can run
the helper script:

```bash
./scripts/call_remote_infer.sh http://localhost:8080/infer
```

If you prefer artifact storage (S3/Hugging Face), use that workflow instead; the
backend supports downloading model artifacts at startup (ask me to implement
that path if you want it).
