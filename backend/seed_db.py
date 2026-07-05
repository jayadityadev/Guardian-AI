"""Seed the database with demo sessions so the dashboard is pre-populated."""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

import argparse

from app.core.database import SessionLocal, engine
from app.models.session import Base, SessionAnalysis


def seed(force: bool = False):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if we already have demo data
        existing = db.query(SessionAnalysis).count()
        if existing > 0 and not force:
            print(f"DB already has {existing} sessions — skipping seed.")
            return

        if existing > 0 and force:
            print(f"Force flag set — deleting existing {existing} sessions...")
            db.query(SessionAnalysis).delete()
            db.commit()

        sessions = [
            SessionAnalysis(
                platform="json_upload",
                risk_score=82,
                confidence=0.91,
                grooming_stage="isolation",
                recommendation="escalate_platform",
                raw_flag_json=[
                    {"type": "trust_building", "snippet": "you're so mature for your age", "severity": "medium", "message_index": 3},
                    {"type": "isolation_tactic", "snippet": "don't tell your parents about this", "severity": "high", "message_index": 14},
                    {"type": "gift_offering", "snippet": "I'll buy you Robux if you keep this between us", "severity": "high", "message_index": 21},
                ],
                drift_json={
                    "late_night_messages": True,
                    "message_frequency_spike": False,
                    "new_unknown_contact": True,
                },
                stage_progression_json={
                    "trust_building": True,
                    "isolation": True,
                    "secrecy": True,
                    "escalation": False,
                },
            ),
            SessionAnalysis(
                platform="json_upload",
                risk_score=24,
                confidence=0.85,
                grooming_stage="trust_building",
                recommendation="monitor",
                raw_flag_json=[],
                drift_json={
                    "late_night_messages": False,
                    "message_frequency_spike": False,
                    "new_unknown_contact": False,
                },
                stage_progression_json={
                    "trust_building": False,
                    "isolation": False,
                    "secrecy": False,
                    "escalation": False,
                },
            ),
            SessionAnalysis(
                platform="json_upload",
                risk_score=67,
                confidence=0.78,
                grooming_stage="secrecy",
                recommendation="alert_parent",
                raw_flag_json=[
                    {"type": "secrecy_request", "snippet": "yaar kisi ko mat batana", "severity": "high", "message_index": 5},
                    {"type": "gift_offering", "snippet": "free coins dunga bhai", "severity": "medium", "message_index": 9},
                    {"type": "trust_building", "snippet": "tu bahut samajhdar hai", "severity": "medium", "message_index": 2},
                ],
                drift_json={
                    "late_night_messages": True,
                    "message_frequency_spike": True,
                    "new_unknown_contact": True,
                },
                stage_progression_json={
                    "trust_building": True,
                    "isolation": False,
                    "secrecy": True,
                    "escalation": False,
                },
            ),
        ]

        for s in sessions:
            db.add(s)

        db.commit()
        print(f"Seeded {len(sessions)} demo sessions.")

        # Print IDs for reference
        for s in sessions:
            db.refresh(s)
            print(f"  {s.id}  score={s.risk_score}  rec={s.recommendation}")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the DB with demo sessions")
    parser.add_argument("--force", action="store_true", help="Delete existing sessions before seeding")
    args = parser.parse_args()
    seed(force=args.force)
