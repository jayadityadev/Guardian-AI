import logging
import os
import tempfile
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.alerts import broadcast_analysis_complete
from app.core.database import SessionLocal, get_db
from app.models.session import SessionAnalysis
from app.services.ml_bridge import analyse
from app.services.stt import WhisperTranscriber

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingest"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class IngestMessage(BaseModel):
	sender: str = Field(min_length=1)
	text: str = Field(min_length=1)
	timestamp: str = ""  # accept any string; empty strings from audio pipeline are valid


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


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

def _run_ml_and_update(session_id: UUID, messages: list[dict]) -> None:
	"""Run ML analysis in a background thread and persist results to the DB."""
	db = SessionLocal()
	try:
		analysis_result = analyse(messages)

		session_row = db.query(SessionAnalysis).filter(SessionAnalysis.id == session_id).first()
		if session_row is None:
			logger.error("Session %s disappeared before ML could update it", session_id)
			return

		session_row.risk_score = analysis_result.get("risk_score", 0)
		session_row.confidence = analysis_result.get("confidence", 0.0)
		session_row.grooming_stage = analysis_result.get("grooming_stage", "trust_building")
		session_row.recommendation = analysis_result.get("recommendation", "monitor")
		session_row.raw_flag_json = analysis_result.get("flags", [])
		session_row.drift_json = analysis_result.get("drift_signals", {
			"late_night_messages": False,
			"message_frequency_spike": False,
			"new_unknown_contact": False,
		})
		session_row.stage_progression_json = analysis_result.get("stage_progression", {
			"trust_building": False,
			"isolation": False,
			"secrecy": False,
			"escalation": False,
		})

		db.commit()

		# Fire WebSocket alert.
		import asyncio

		coro = broadcast_analysis_complete(
			session_id=session_row.id,
			risk_score=session_row.risk_score or 0,
			recommendation=session_row.recommendation or "monitor",
		)

		try:
			loop = asyncio.get_running_loop()
			loop.create_task(coro)
		except RuntimeError:
			asyncio.run(coro)

	except Exception:
		logger.exception("Background ML analysis failed for session %s", session_id)
	finally:
		db.close()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest(
	payload: IngestRequest,
	background_tasks: BackgroundTasks,
	db: Session = Depends(get_db),
) -> IngestResponse:
	"""
	Ingest chat messages for grooming pattern analysis.

	Creates a session record immediately and returns its ID.
	ML analysis runs in the background; results are pushed via WebSocket.
	"""
	messages = [m.model_dump() for m in payload.messages]
	if not messages:
		raise HTTPException(status_code=400, detail="invalid input")

	# Create a preliminary DB row so the session_id exists immediately.
	session_row = SessionAnalysis(platform=payload.platform)
	db.add(session_row)
	db.commit()
	db.refresh(session_row)

	# Kick off heavy ML work in the background.
	background_tasks.add_task(_run_ml_and_update, session_row.id, messages)

	return IngestResponse(session_id=session_row.id, status="processing")


@router.post("/ingest/audio", response_model=AudioIngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_audio(
	background_tasks: BackgroundTasks,
	file: UploadFile = File(...),
	db: Session = Depends(get_db),
) -> AudioIngestResponse:
	"""
	Ingest audio file for grooming pattern analysis.

	Transcribes audio synchronously (returned in response), then kicks off
	ML analysis in the background identically to the JSON ingest path.
	"""
	audio_bytes = await file.read()
	if not audio_bytes:
		raise HTTPException(status_code=400, detail="invalid input")

	with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
		tmp.write(audio_bytes)
		tmp_path = tmp.name

	try:
		# Transcribe — synchronous but fast enough with Whisper base model.
		transcript = WhisperTranscriber.transcribe(tmp_path)
	finally:
		os.unlink(tmp_path)

	messages = WhisperTranscriber.audio_to_messages(transcript)

	# Persist preliminary session row.
	session_row = SessionAnalysis(platform="audio_upload")
	db.add(session_row)
	db.commit()
	db.refresh(session_row)

	# Background ML analysis.
	background_tasks.add_task(_run_ml_and_update, session_row.id, messages)

	return AudioIngestResponse(session_id=session_row.id, transcript=transcript, status="processing")
