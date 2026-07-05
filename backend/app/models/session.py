import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SessionAnalysis(Base):
	__tablename__ = "sessions"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)
	platform: Mapped[str] = mapped_column(String(50), default="json_upload", nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		nullable=False,
	)
	risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
	confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
	grooming_stage: Mapped[str | None] = mapped_column(String(50), nullable=True)
	recommendation: Mapped[str | None] = mapped_column(String(50), nullable=True)
	raw_flag_json: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
	drift_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
	stage_progression_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
