from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.alerts import router as alerts_router
from app.api.ingest import router as ingest_router
from app.api.session import router as session_router
from app.core.config import settings
from app.services.stt import WhisperTranscriber


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, __: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "invalid input"})


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    detail = str(exc.detail).lower() if exc.detail else "internal server error"
    return JSONResponse(status_code=exc.status_code, content={"error": detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, __: Exception):
    return JSONResponse(status_code=500, content={"error": "internal server error"})


@app.on_event("startup")
def on_startup() -> None:
	WhisperTranscriber.load_model()


app.include_router(ingest_router)
app.include_router(session_router)
app.include_router(alerts_router)


@app.get("/")
def main():
    return {"message": "Guardian AI backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
