from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.session import SessionAnalysis


router = APIRouter(tags=["session"])


# ---------------------------------------------------------------------------
# Contract-strict response schemas
# ---------------------------------------------------------------------------

# Default empty structures matching the API contract
_DEFAULT_STAGE_PROGRESSION = {
	"trust_building": False,
	"isolation": False,
	"secrecy": False,
	"escalation": False,
}

_DEFAULT_DRIFT_SIGNALS = {
	"late_night_messages": False,
	"message_frequency_spike": False,
	"new_unknown_contact": False,
}


class SessionListItem(BaseModel):
	"""Lightweight session entry for GET /sessions (contract §3.4)."""
	session_id: UUID
	risk_score: int
	timestamp: datetime
	recommendation: str

	class Config:
		from_attributes = True


class FlagItem(BaseModel):
	"""Single flag entry inside the risk JSON (contract §3.3)."""
	type: str
	snippet: str
	severity: str
	message_index: int = 0


class StageProgression(BaseModel):
	trust_building: bool = False
	isolation: bool = False
	secrecy: bool = False
	escalation: bool = False


class DriftSignals(BaseModel):
	late_night_messages: bool = False
	message_frequency_spike: bool = False
	new_unknown_contact: bool = False


class RiskJSON(BaseModel):
	"""Full risk assessment response (contract §3.3 — PRIMARY CONTRACT)."""
	session_id: UUID
	platform: str
	timestamp: datetime
	risk_score: int
	confidence: float
	grooming_stage: str
	flags: list[FlagItem]
	categories: list[str]
	stage_progression: StageProgression
	recommendation: str
	drift_signals: DriftSignals

	class Config:
		from_attributes = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/session/{session_id}", response_model=RiskJSON, status_code=status.HTTP_200_OK)
def get_session(session_id: UUID, db: Session = Depends(get_db)) -> RiskJSON:
	"""
	Get full risk assessment for a session.

	Returns the complete risk JSON including scores, flags, drift signals, and recommendations.
	All fields are guaranteed present per the API contract — no nulls.
	"""
	session = db.query(SessionAnalysis).filter(SessionAnalysis.id == session_id).first()

	if not session:
		raise HTTPException(status_code=404, detail="session not found")

	# --- Map DB columns → contract fields with safe defaults ---

	raw_flags = session.raw_flag_json if isinstance(session.raw_flag_json, list) else []
	flags = []
	for f in raw_flags:
		if isinstance(f, dict) and "type" in f and "snippet" in f and "severity" in f:
			flags.append(FlagItem(
				type=f["type"],
				snippet=f["snippet"],
				severity=f["severity"],
				message_index=f.get("message_index", 0),
			))

	# Categories are the unique flag types (contract example shows this)
	categories = sorted({f.type for f in flags}) if flags else []

	# Stage progression: stored in stage_progression_json
	sp_raw = session.stage_progression_json if isinstance(session.stage_progression_json, dict) else {}
	stage_progression = StageProgression(
		trust_building=sp_raw.get("trust_building", False),
		isolation=sp_raw.get("isolation", False),
		secrecy=sp_raw.get("secrecy", False),
		escalation=sp_raw.get("escalation", False),
	)

	# Drift signals: stored in drift_json
	ds_raw = session.drift_json if isinstance(session.drift_json, dict) else {}
	drift_signals = DriftSignals(
		late_night_messages=ds_raw.get("late_night_messages", False),
		message_frequency_spike=ds_raw.get("message_frequency_spike", False),
		new_unknown_contact=ds_raw.get("new_unknown_contact", False),
	)

	return RiskJSON(
		session_id=session.id,
		platform=session.platform or "json_upload",
		timestamp=session.created_at,
		risk_score=session.risk_score if session.risk_score is not None else 0,
		confidence=session.confidence if session.confidence is not None else 0.0,
		grooming_stage=session.grooming_stage or "trust_building",
		flags=flags,
		categories=categories,
		stage_progression=stage_progression,
		recommendation=session.recommendation or "monitor",
		drift_signals=drift_signals,
	)


@router.get("/sessions", response_model=list[SessionListItem], status_code=status.HTTP_200_OK)
def get_sessions(
	limit: int = 50,
	offset: int = 0,
	db: Session = Depends(get_db),
) -> list[SessionListItem]:
	"""
	Get list of all past sessions.

	Returns session IDs, timestamps, risk scores, and recommendations.
	Supports pagination via limit and offset.
	"""
	sessions = (
		db.query(SessionAnalysis)
		.order_by(SessionAnalysis.created_at.desc())
		.limit(limit)
		.offset(offset)
		.all()
	)

	return [
		SessionListItem(
			session_id=s.id,
			risk_score=s.risk_score if s.risk_score is not None else 0,
			timestamp=s.created_at,
			recommendation=s.recommendation or "monitor",
		)
		for s in sessions
	]
