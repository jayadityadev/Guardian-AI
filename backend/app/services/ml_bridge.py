"""
ML Bridge: Interface to Jaggu's ML pipeline.

For Phase 1, this is a mock that returns realistic data.
When Jaggu's analyse() is ready, swap the implementation.
"""

from datetime import datetime
from uuid import uuid4


def analyse(messages: list[dict]) -> dict:
    """
    Analyse a conversation for grooming patterns.
    
    Args:
        messages: List of message dicts with sender, text, timestamp
        
    Returns:
        Risk analysis JSON matching the project contract schema
    """
    # MOCK IMPLEMENTATION — Replace with Jaggu's real ML when ready
    
    # Simulate scoring based on message count and keywords
    risk_score = min(100, len(messages) * 5 + 30)  # Dummy calculation
    confidence = 0.72 + (len(messages) * 0.01)
    
    # Mock grooming stage detection
    all_text = " ".join([m.get("text", "").lower() for m in messages])
    if "mature" in all_text or "special" in all_text:
        grooming_stage = "trust_building"
    elif "secret" in all_text or "tell parents" in all_text:
        grooming_stage = "isolation"
    elif "money" in all_text or "gift" in all_text:
        grooming_stage = "gift_lure"
    else:
        grooming_stage = "trust_building"
    
    # Mock flags
    mock_flags = [
        {
            "type": "trust_building",
            "snippet": "you're so mature for your age",
            "severity": "medium",
            "message_index": 0,
        }
    ]
    
    # Recommendation based on risk score
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
