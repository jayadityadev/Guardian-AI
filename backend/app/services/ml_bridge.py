"""
ML Bridge: Interface to Jaggu's ML pipeline.

This module prefers calling a remote inference API when `ML_API_URL` is set.
If the remote call fails, it falls back to the local mock implementation so
the backend remains functional for development and testing.
"""

import logging
import os
from datetime import datetime
from uuid import uuid4

import requests


def _mock_analyse(messages: list[dict]) -> dict:
    """
    Local mock analysis (original Phase 1 behaviour).
    """
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
    """
    Analyse a conversation for grooming patterns.

    Behavior:
    - If `ML_API_URL` env var is set, POST the messages to that URL and return
      the JSON response (expects contract-shaped JSON).
    - On any network/error, fall back to the local mock implementation.
    """
    ml_url = os.getenv("ML_API_URL")
    ml_key = os.getenv("ML_API_KEY")

    if ml_url:
        try:
            headers = {"Content-Type": "application/json"}
            if ml_key:
                headers["Authorization"] = f"Bearer {ml_key}"
            resp = requests.post(ml_url, json={"messages": messages}, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # fallback to local mock
            logging.exception("Remote ML inference failed, falling back to local mock: %s", exc)

    return _mock_analyse(messages)
