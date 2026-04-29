"""
Contract-compatible grooming analysis wrapper.

This module keeps the existing model logic intact and adds the exact JSON
contract expected by the backend and frontend.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from .predict_grooming_bert import predict_grooming_with_confidence as bert_predict


GROQ_SYSTEM_PROMPT = """
You are a child safety AI. Analyse the following chat conversation for grooming behaviour patterns.

Grooming patterns to detect:
- Trust building: excessive compliments, claims of special understanding, "you're so mature"
- Isolation tactics: asking child to keep secret, move to private platform, not tell parents
- Gift offering: offering money, game credits, gifts in exchange for anything
- Secrecy requests: "delete this", "don't tell anyone", "this is between us"
- Age probing: asking how old the child is, whether they're home alone
- Platform hopping: asking to move to Snapchat, WhatsApp, Signal
- Request escalation: any inappropriate asks

Respond ONLY with valid JSON. No preamble. No markdown. Exactly this schema:
{
  "grooming_detected": true,
  "intent_score": 0.85,
  "flags": [
    {"type": "isolation_tactic", "snippet": "exact quote from chat", "severity": "high"}
  ],
  "dominant_pattern": "isolation",
  "reasoning": "one sentence"
}
""".strip()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_message_text(message: dict[str, Any]) -> str:
    return str(message.get("text", "")).strip()


def _combined_text(messages: list[dict[str, Any]]) -> str:
    return " ".join(_safe_message_text(message) for message in messages if _safe_message_text(message))


def _keyword_flags(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Heuristic flags used when Groq is unavailable or returns invalid JSON."""
    patterns = [
        ("trust_building", ["you\'re so mature", "so mature", "special", "understand you", "trust me", "beautiful", "handsome"], "medium"),
        ("isolation_tactic", ["dont tell", "don't tell", "keep this between us", "secret", "private", "snapchat", "whatsapp", "signal", "telegram"], "high"),
        ("gift_offering", ["robux", "free coins", "money", "gift", "buy you", "send you"], "medium"),
        ("secrecy_request", ["delete this", "delete these", "between us", "no one else", "dont tell anyone", "don't tell anyone"], "high"),
        ("age_probing", ["how old", "your age", "home alone", "alone right now", "are you alone"], "medium"),
        ("platform_hop", ["snapchat", "whatsapp", "signal", "telegram"], "medium"),
        ("request_escalation", ["send photo", "send a photo", "pictures", "pic", "video call", "meet in private"], "high"),
    ]

    flags: list[dict[str, Any]] = []
    for index, message in enumerate(messages):
        text = _safe_message_text(message).lower()
        if not text:
            continue
        for flag_type, keywords, severity in patterns:
            for keyword in keywords:
                if keyword in text:
                    flags.append(
                        {
                            "type": flag_type,
                            "snippet": _safe_message_text(message),
                            "severity": severity,
                            "message_index": index,
                        }
                    )
                    break

    return flags


def groq_analyse(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Optional Groq call with deterministic fallback when unavailable."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        flags = _keyword_flags(messages)
        return {
            "grooming_detected": bool(flags),
            "intent_score": 0.1 if not flags else min(0.55 + 0.1 * len(flags), 0.95),
            "flags": flags,
            "dominant_pattern": classify_stage(flags, {"trust_building": False, "isolation": False, "secrecy": False, "escalation": False}),
            "reasoning": "Heuristic fallback used because GROQ_API_KEY is not configured.",
        }

    try:
        from groq import Groq
    except Exception:
        flags = _keyword_flags(messages)
        return {
            "grooming_detected": bool(flags),
            "intent_score": 0.1 if not flags else min(0.55 + 0.1 * len(flags), 0.95),
            "flags": flags,
            "dominant_pattern": classify_stage(flags, {"trust_building": False, "isolation": False, "secrecy": False, "escalation": False}),
            "reasoning": "Groq SDK not available; heuristic fallback used.",
        }

    convo_text = "\n".join([f"{message.get('sender', 'unknown')}: {message.get('text', '')}" for message in messages[-10:]])
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": GROQ_SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyse this conversation:\n\n{convo_text}"},
        ],
        temperature=0.1,
        max_tokens=500,
    )

    try:
        parsed = json.loads(response.choices[0].message.content)
        if "flags" not in parsed:
            parsed["flags"] = []
        if "intent_score" not in parsed:
            parsed["intent_score"] = 0.5
        if "dominant_pattern" not in parsed:
            parsed["dominant_pattern"] = classify_stage(parsed["flags"], {"trust_building": False, "isolation": False, "secrecy": False, "escalation": False})
        if "reasoning" not in parsed:
            parsed["reasoning"] = "Groq analysis completed."
        return parsed
    except Exception:
        flags = _keyword_flags(messages)
        return {
            "grooming_detected": bool(flags),
            "intent_score": 0.1 if not flags else min(0.55 + 0.1 * len(flags), 0.95),
            "flags": flags,
            "dominant_pattern": classify_stage(flags, {"trust_building": False, "isolation": False, "secrecy": False, "escalation": False}),
            "reasoning": "Groq returned invalid JSON; heuristic fallback used.",
        }


def bert_score(messages: list[dict[str, Any]]) -> float:
    """Return the current BERT probability for grooming-like text."""
    full_text = _combined_text(messages)
    if not full_text:
        return 0.0

    try:
        result = bert_predict(full_text)
        return float(result.get("probability", 0.0))
    except Exception:
        return 0.0


def calculate_risk_score(bert_score_value: float, groq_score: float, flag_count: int) -> int:
    """Risk score formula from the project guide."""
    base = (bert_score_value * 0.4) + (groq_score * 0.4) + (min(flag_count, 5) / 5 * 0.2)
    return min(int(base * 100), 100)


def classify_stage(flags: list[dict[str, Any]], stage_progression: dict[str, bool]) -> str:
    """Stage classifier from the project guide, with contract-safe fallback."""
    types = {flag.get("type") for flag in flags}

    if "request_escalation" in types:
        return "escalation"
    if "secrecy_request" in types or "platform_hop" in types:
        return "secrecy"
    if "isolation_tactic" in types:
        return "isolation"
    if "trust_building" in types or "gift_offering" in types:
        return "trust_building"
    return "trust_building"


def detect_drift(messages: list[dict[str, Any]]) -> dict[str, bool]:
    """Detect simple time and sender drift signals."""
    late_night_messages = False
    message_frequency_spike = False
    new_unknown_contact = False

    parsed_times = []
    senders = set()

    for message in messages:
        sender = str(message.get("sender", "unknown")).lower()
        senders.add(sender)
        if sender in {"stranger", "unknown", "new", "new_contact"}:
            new_unknown_contact = True

        timestamp = str(message.get("timestamp", "")).strip()
        if timestamp:
            timestamp = timestamp.replace("Z", "+00:00")
            try:
                parsed_times.append(datetime.fromisoformat(timestamp))
            except ValueError:
                pass

        text = _safe_message_text(message).lower()
        if any(token in text for token in ["home alone", "alone right now", "are you alone"]):
            new_unknown_contact = True

    for parsed_time in parsed_times:
        if parsed_time.hour >= 22 or parsed_time.hour < 6:
            late_night_messages = True
            break

    if len(parsed_times) >= 4:
        parsed_times.sort()
        for index in range(len(parsed_times) - 3):
            window = parsed_times[index + 3] - parsed_times[index]
            if window.total_seconds() <= 10 * 60:
                message_frequency_spike = True
                break

    if len(senders) >= 3:
        new_unknown_contact = True

    return {
        "late_night_messages": late_night_messages,
        "message_frequency_spike": message_frequency_spike,
        "new_unknown_contact": new_unknown_contact,
    }


def analyse(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the contract-compatible JSON structure required by the backend."""
    messages = messages or []
    if not messages:
        messages = [{"sender": "unknown", "text": "", "timestamp": ""}]

    bert_conf = bert_score(messages)
    groq_result = groq_analyse(messages)

    flags = list(groq_result.get("flags", []))
    stage_progression = {
        "trust_building": any(flag.get("type") in ["trust_building", "gift_offering"] for flag in flags),
        "isolation": any(flag.get("type") == "isolation_tactic" for flag in flags),
        "secrecy": any(flag.get("type") in ["secrecy_request", "platform_hop"] for flag in flags),
        "escalation": any(flag.get("type") == "request_escalation" for flag in flags),
    }

    risk_score = calculate_risk_score(bert_conf, float(groq_result.get("intent_score", 0.5)), len(flags))
    recommendation = (
        "escalate_platform" if risk_score >= 80
        else "alert_parent" if risk_score >= 50
        else "monitor"
    )

    return {
        "session_id": str(uuid.uuid4()),
        "platform": "json_upload",
        "timestamp": _utc_now_iso(),
        "risk_score": risk_score,
        "confidence": round(float(groq_result.get("intent_score", bert_conf)), 2),
        "grooming_stage": classify_stage(flags, stage_progression),
        "flags": flags,
        "categories": sorted({flag.get("type") for flag in flags if flag.get("type")}),
        "stage_progression": stage_progression,
        "recommendation": recommendation,
        "drift_signals": detect_drift(messages),
    }
