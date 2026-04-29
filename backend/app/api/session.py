from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.session import SessionAnalysis


router = APIRouter(tags=["session"])


class SessionListItem(BaseModel):
	session_id: UUID
	platform: str
	timestamp: datetime
	risk_score: int | None
	recommendation: str | None
	
	class Config:
		from_attributes = True


class RiskJSON(BaseModel):
	session_id: UUID
	platform: str
	timestamp: datetime
	risk_score: int | None
	confidence: float | None
	grooming_stage: str | None
	flags: list | dict | None = None
	categories: list | None = None
	stage_progression: dict | None = None
	recommendation: str | None = None
	drift_signals: dict | None = None
	
	class Config:
		from_attributes = True


@router.get("/session/{session_id}", response_model=RiskJSON, status_code=status.HTTP_200_OK)
def get_session(session_id: UUID, db: Session = Depends(get_db)) -> RiskJSON:
	"""
	Get full risk assessment for a session.
	
	Returns the complete risk JSON including scores, flags, drift signals, and recommendations.
	"""
	session = db.query(SessionAnalysis).filter(SessionAnalysis.id == session_id).first()
	
	if not session:
		raise HTTPException(status_code=404, detail="Session not found")
	
	# Extract categories from flags if available
	categories = []
	if isinstance(session.raw_flag_json, list):
		categories = list({flag.get("type") for flag in session.raw_flag_json if "type" in flag})
	elif session.grooming_stage:
		categories = [session.grooming_stage]
	
	return RiskJSON(
		session_id=session.id,
		platform=session.platform,
		timestamp=session.created_at,
		risk_score=session.risk_score,
		confidence=session.confidence,
		grooming_stage=session.grooming_stage,
		flags=session.raw_flag_json,
		categories=categories,
		stage_progression=session.stage_progression_json,
		recommendation=session.recommendation,
		drift_signals=session.drift_json,
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
			platform=s.platform,
			timestamp=s.created_at,
			risk_score=s.risk_score,
			recommendation=s.recommendation,
		)
		for s in sessions
	]
