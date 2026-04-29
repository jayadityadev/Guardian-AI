from fastapi import FastAPI

from app.api.ingest import router as ingest_router
from app.api.session import router as session_router
from app.core.config import settings


app = FastAPI(title=settings.app_name)


app.include_router(ingest_router)
app.include_router(session_router)


@app.get("/")
def main():
    return {"message": "Guardian AI backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
