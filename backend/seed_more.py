"""Insert ~20 realistic demo SessionAnalysis rows for the dashboard.

Run from the backend folder with the backend venv activated:

  . .venv/bin/activate && python seed_more.py

"""
from pathlib import Path
import sys
from random import randint, choice, random
from datetime import datetime, timedelta

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.session import SessionAnalysis


def make_demo(i: int) -> SessionAnalysis:
    score = int(max(0, min(100, randint(5, 95) + (5 if i % 7 == 0 else 0))))
    conf = round(0.6 + random() * 0.35, 2)
    stages = ["trust_building", "isolation", "secrecy", "escalation"]
    stage = choice(stages)
    rec = "monitor"
    if score > 80:
        rec = "escalate_platform"
    elif score > 60:
        rec = "alert_parent"

    flags = []
    if score > 50:
        flags = [
            {"type": "trust_building", "snippet": "you're so mature for your age", "severity": "medium", "message_index": 1},
            {"type": "gift_offering", "snippet": "I'll send you coins if you help me", "severity": "high", "message_index": 4},
        ]

    drift = {
        "late_night_messages": bool(i % 5 == 0),
        "message_frequency_spike": bool(i % 6 == 0),
        "new_unknown_contact": bool(i % 8 == 0),
    }

    stage_prog = {
        "trust_building": score > 30,
        "isolation": score > 50,
        "secrecy": score > 60,
        "escalation": score > 80,
    }

    created = datetime.utcnow() - timedelta(hours=(i * 3))

    return SessionAnalysis(
        platform="json_upload",
        created_at=created,
        risk_score=score,
        confidence=conf,
        grooming_stage=stage,
        recommendation=rec,
        raw_flag_json=flags,
        drift_json=drift,
        stage_progression_json=stage_prog,
    )


def main(n: int = 20, force: bool = False):
    db = SessionLocal()
    try:
        if force:
            print("Deleting existing sessions...")
            db.query(SessionAnalysis).delete()
            db.commit()

        demos = [make_demo(i) for i in range(n)]
        for d in demos:
            db.add(d)
        db.commit()
        for d in demos:
            db.refresh(d)
            print(f"inserted {d.id} score={d.risk_score} rec={d.recommendation}")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=20)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    main(n=args.n, force=args.force)
