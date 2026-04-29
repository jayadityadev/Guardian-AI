from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.session import SessionAnalysis


router = APIRouter(tags=["ingest"])


class IngestMessage(BaseModel):
	sender: str = Field(min_length=1)
	text: str = Field(min_length=1)
	timestamp: datetime


class IngestRequest(BaseModel):
	platform: str = Field(default="json_upload", min_length=1)
	messages: list[IngestMessage] = Field(min_length=1)


class IngestResponse(BaseModel):
	session_id: UUID
	status: str


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest(payload: IngestRequest, db: Session = Depends(get_db)) -> IngestResponse:
	# Persist only session metadata; raw messages are intentionally not stored.
	session_row = SessionAnalysis(platform=payload.platform)
	db.add(session_row)
	db.commit()
	db.refresh(session_row)

	return IngestResponse(session_id=session_row.id, status="processing")


@router.post("/ingest/audio", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_audio(file: UploadFile = File(...), db: Session = Depends(get_db)) -> IngestResponse:
	session_row = SessionAnalysis(platform="audio_upload")
	db.add(session_row)
	db.commit()
	db.refresh(session_row)

	return IngestResponse(session_id=session_row.id, status="processing")
