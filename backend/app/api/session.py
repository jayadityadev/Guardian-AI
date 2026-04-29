from uuid import UUID

from fastapi import APIRouter, status


router = APIRouter(tags=["session"])


@router.get("/session/{session_id}", status_code=status.HTTP_200_OK)
def get_session(session_id: UUID) -> dict[str, str]:
	return {
		"session_id": str(session_id),
		"status": "stub",
		"message": "Session lookup endpoint is stubbed for Phase 0",
	}
