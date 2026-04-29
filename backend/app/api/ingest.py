from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.session import SessionAnalysis
from app.services.ml_bridge import analyse
from app.services.stt import WhisperTranscriber
import tempfile
import json


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


class AudioIngestResponse(BaseModel):
	session_id: UUID
	transcript: str
	status: str


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest(payload: IngestRequest, db: Session = Depends(get_db)) -> IngestResponse:
	"""
	Ingest chat messages for grooming pattern analysis.
	
	Accepts JSON array of messages, runs ML analysis, stores results in DB.
	Returns session ID for later retrieval of full risk assessment.
	"""
	# Convert Pydantic models to dicts for ML pipeline
	messages = [m.model_dump() for m in payload.messages]
	
	# Run ML analysis
	analysis_result = analyse(messages)
	
	# Create DB session record
	session_row = SessionAnalysis(
		platform=payload.platform,
		risk_score=analysis_result.get("risk_score"),
		confidence=analysis_result.get("confidence"),
		grooming_stage=analysis_result.get("grooming_stage"),
		recommendation=analysis_result.get("recommendation"),
		raw_flag_json=analysis_result.get("flags"),
		drift_json=analysis_result.get("drift_signals"),
		stage_progression_json=analysis_result.get("stage_progression"),
	)
	db.add(session_row)
	db.commit()
	db.refresh(session_row)
	
	return IngestResponse(session_id=session_row.id, status="processing")


@router.post("/ingest/audio", response_model=AudioIngestResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_audio(file: UploadFile = File(...), db: Session = Depends(get_db)) -> AudioIngestResponse:
	"""
	Ingest audio file for grooming pattern analysis.
	
	Transcribes audio to text using Whisper STT, converts to message array,
	runs same ML analysis pipeline as JSON ingest, stores results in DB.
	"""
	# Save uploaded file to temp location
	with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
		tmp.write(file.file.read())
		tmp_path = tmp.name
	
	try:
		# Transcribe audio
		transcript = WhisperTranscriber.transcribe(tmp_path)
		
		# Convert transcript to messages
		messages = WhisperTranscriber.audio_to_messages(transcript)
		
		# Run ML analysis
		analysis_result = analyse(messages)
		
		# Create DB session record
		session_row = SessionAnalysis(
			platform="audio_upload",
			risk_score=analysis_result.get("risk_score"),
			confidence=analysis_result.get("confidence"),
			grooming_stage=analysis_result.get("grooming_stage"),
			recommendation=analysis_result.get("recommendation"),
			raw_flag_json=analysis_result.get("flags"),
			drift_json=analysis_result.get("drift_signals"),
			stage_progression_json=analysis_result.get("stage_progression"),
		)
		db.add(session_row)
		db.commit()
		db.refresh(session_row)
		
		return AudioIngestResponse(session_id=session_row.id, transcript=transcript, status="processing")
	finally:
		import os
		os.unlink(tmp_path)
