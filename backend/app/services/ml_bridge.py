"""
ML Bridge: Interface to Jaggu's ML pipeline.

This module supports three inference modes in order:
1. Remote API if `ML_API_URL` is configured.
2. In-repo ML pipeline (under `ml/`) if present and model artifacts exist.
3. Local mock analyser as a safe fallback for development.
"""

import logging
import os
from datetime import datetime
from uuid import uuid4

import requests


def _mock_analyse(messages: list[dict]) -> dict:
    """Local mock analysis used as a fallback."""
    risk_score = min(100, len(messages) * 5 + 30)
    confidence = 0.72 + (len(messages) * 0.01)

    all_text = " ".join([m.get("text", "").lower() for m in messages])
    if "mature" in all_text or "special" in all_text:
        grooming_stage = "trust_building"
    elif "secret" in all_text or "tell parents" in all_text:
        grooming_stage = "isolation"
    elif "money" in all_text or "gift" in all_text:
        grooming_stage = "gift_lure"
    else:
        grooming_stage = "trust_building"

    mock_flags = [
        {
            "type": "trust_building",
            "snippet": "you're so mature for your age",
            "severity": "medium",
            "message_index": 0,
        }
    ]

    if risk_score > 80:
        recommendation = "escalate_platform"
    elif risk_score > 60:
        recommendation = "alert_parent"
    else:
        recommendation = "monitor"

    return {
        "session_id": str(uuid4()),
        "platform": "json_upload",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "risk_score": risk_score,
        "confidence": float(confidence),
        "grooming_stage": grooming_stage,
        "flags": mock_flags,
        "categories": [grooming_stage],
        "stage_progression": {
            "trust_building": grooming_stage == "trust_building",
            "isolation": grooming_stage == "isolation",
            "secrecy": grooming_stage == "secrecy",
            "escalation": grooming_stage == "escalation",
        },
        "recommendation": recommendation,
        "drift_signals": {
            "late_night_messages": len(messages) > 5,
            "message_frequency_spike": False,
            "new_unknown_contact": True,
        },
    }


def analyse(messages: list[dict]) -> dict:
    """Analyse a conversation for grooming patterns.

    Order of attempts:
    - Remote inference via ML_API_URL
    - In-repo `ml` pipeline (if present)
    - Local mock analyser
    """
    ml_url = os.getenv("ML_API_URL")
    ml_key = os.getenv("ML_API_KEY")

    # 1) Remote API
    if ml_url:
        try:
            headers = {"Content-Type": "application/json"}
            if ml_key:
                headers["Authorization"] = f"Bearer {ml_key}"
            resp = requests.post(ml_url, json={"messages": messages}, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logging.exception("Remote ML inference failed, falling back: %s", exc)

    # 2) In-repo ML pipeline
    try:
        import sys
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[3]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))

        # The grooming model wrapper provides an analyse() function
        from ml.models.grooming_model import analyse as jaggu_analyse

        try:
            return jaggu_analyse.analyse(messages)
        except Exception as exc:
            logging.exception("In-repo ML analyse() raised an exception, falling back: %s", exc)
    except Exception:
        logging.debug("In-repo ML pipeline not available; skipping import")

    # 3) Fallback
    return _mock_analyse(messages)

