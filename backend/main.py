from fastapi import FastAPI

from app.api.alerts import router as alerts_router
from app.api.ingest import router as ingest_router
from app.api.session import router as session_router
from app.core.config import settings
from app.services.stt import WhisperTranscriber


app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
	WhisperTranscriber.load_model()


app.include_router(ingest_router)
app.include_router(session_router)
app.include_router(alerts_router)
app.include_router(session_router)


@app.get("/")
def main():
    return {"message": "Guardian AI backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
