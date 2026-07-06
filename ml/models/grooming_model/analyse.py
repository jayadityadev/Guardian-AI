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

# Strict enum sets from the API contract
_VALID_FLAG_TYPES = {
    "isolation_tactic",
    "gift_offering",
    "trust_building",
    "secrecy_request",
    "platform_hop",
    "age_probing",
    "request_escalation",
}

_VALID_SEVERITIES = {"high", "medium", "low"}

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

Allowed flag type values (use ONLY these exact strings):
isolation_tactic, gift_offering, trust_building, secrecy_request, platform_hop, age_probing, request_escalation

Allowed severity values: high, medium, low

Respond ONLY with valid JSON. No preamble. No markdown. Exactly this schema:
{
  "grooming_detected": true,
  "intent_score": 0.85,
  "flags": [
    {"type": "isolation_tactic", "snippet": "exact quote from chat", "severity": "high", "message_index": 0}
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
    # Order matters: more specific patterns first. A message only matches the
    # first pattern whose keyword fires (one flag per message per scan pass).
    patterns = [
        ("request_escalation", ["send photo", "send a photo", "pictures", "pic", "video call", "meet in private"], "high"),
        ("secrecy_request", ["delete this", "delete these", "no one else", "dont tell anyone", "don't tell anyone", "kisi ko mat batana", "sirf hamare beech", "apni mummy ko mat bata"], "high"),
        ("platform_hop", ["snapchat", "whatsapp", "signal", "telegram"], "medium"),
        ("isolation_tactic", ["dont tell", "don't tell", "keep this between us", "secret", "private", "mat batana", "beech mein rahe"], "high"),
        ("gift_offering", ["robux", "free coins", "money", "gift", "buy you", "send you"], "medium"),
        ("trust_building", ["you\'re so mature", "so mature", "special", "understand you", "trust me", "beautiful", "handsome", "samajhdar", "bahut mature"], "medium"),
        ("age_probing", ["how old", "your age", "home alone", "alone right now", "are you alone"], "medium"),
    ]

    flags: list[dict[str, Any]] = []
    for index, message in enumerate(messages):
        text = _safe_message_text(message).lower()
        if not text:
            continue
        matched = False
        for flag_type, keywords, severity in patterns:
            if matched:
                break
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
                    matched = True
                    break

    return flags


def _heuristic_fallback(messages: list[dict[str, Any]], reason: str) -> dict[str, Any]:
    """Return a keyword-heuristic result when no LLM is available."""
    flags = _keyword_flags(messages)
    base_intent = min(0.20 + len(messages) * 0.03, 0.60)
    return {
        "grooming_detected": bool(flags) or len(messages) > 10,
        "intent_score": base_intent if not flags else min(0.55 + 0.1 * len(flags), 0.95),
        "flags": flags,
        "dominant_pattern": classify_stage(flags, {"trust_building": False, "isolation": False, "secrecy": False, "escalation": False}),
        "reasoning": reason,
    }


def _validate_llm_flags(raw_flags: list) -> list[dict[str, Any]]:
    """Validate and normalise LLM-returned flags to strict contract enums."""
    validated: list[dict[str, Any]] = []
    for flag in raw_flags:
        if not isinstance(flag, dict):
            continue
        ftype = str(flag.get("type", "")).lower().strip().replace(" ", "_")
        if ftype not in _VALID_FLAG_TYPES:
            continue
        severity = str(flag.get("severity", "medium")).lower().strip()
        if severity not in _VALID_SEVERITIES:
            severity = "medium"
        validated.append({
            "type": ftype,
            "snippet": str(flag.get("snippet", "")),
            "severity": severity,
            "message_index": int(flag.get("message_index", 0)),
        })
    return validated


# Ordered list of models to try.  LiteLLM routes based on prefix.
# Env vars consumed:  GROQ_API_KEY, NVIDIA_NIM_API_KEY / NVIDIA_API_KEY
_LLM_MODELS = [
    "groq/llama-3.3-70b-versatile",
    "nvidia_nim/meta/llama-3.1-70b-instruct",
    "groq/llama-3.1-8b-instant",
]


def groq_analyse(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """LLM intent analysis with automatic provider fallback via LiteLLM.

    Tries each model in _LLM_MODELS in order.  Falls back to keyword
    heuristics if every LLM call fails or no API keys are configured.
    """
    # Quick check: is *any* key configured?
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    has_nvidia = bool(os.getenv("NVIDIA_NIM_API_KEY") or os.getenv("NVIDIA_API_KEY"))
    if not has_groq and not has_nvidia:
        return _heuristic_fallback(messages, "No LLM API keys configured; heuristic fallback used.")

    # Map NVIDIA_API_KEY → NVIDIA_NIM_API_KEY if only the former is set
    if not os.getenv("NVIDIA_NIM_API_KEY") and os.getenv("NVIDIA_API_KEY"):
        os.environ["NVIDIA_NIM_API_KEY"] = os.environ["NVIDIA_API_KEY"]

    try:
        import litellm
        litellm.drop_params = True           # silently ignore unsupported params
        litellm.set_verbose = False
    except ImportError:
        # Fall back to direct Groq SDK if litellm not installed
        return _groq_sdk_fallback(messages)

    convo_text = "\n".join([
        f"{m.get('sender', 'unknown')}: {m.get('text', '')}"
        for m in messages[-10:]
    ])

    llm_messages = [
        {"role": "system", "content": GROQ_SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyse this conversation:\n\n{convo_text}"},
    ]

    last_error = None
    for model in _LLM_MODELS:
        # Skip models whose provider key is missing
        if model.startswith("groq/") and not has_groq:
            continue
        if model.startswith("nvidia_nim/") and not has_nvidia:
            continue

        try:
            response = litellm.completion(
                model=model,
                messages=llm_messages,
                temperature=0.1,
                max_tokens=500,
                timeout=15,
            )
            raw_content = response.choices[0].message.content or ""
            # Strip markdown fences
            raw_content = re.sub(r"^```(?:json)?\s*", "", raw_content.strip())
            raw_content = re.sub(r"\s*```$", "", raw_content.strip())
            parsed = json.loads(raw_content)

            parsed.setdefault("flags", [])
            parsed.setdefault("intent_score", 0.5)
            parsed.setdefault("dominant_pattern",
                              classify_stage(parsed["flags"],
                                             {"trust_building": False, "isolation": False, "secrecy": False, "escalation": False}))
            parsed.setdefault("reasoning", f"LLM analysis completed via {model}.")
            parsed["flags"] = _validate_llm_flags(parsed["flags"])
            return parsed

        except json.JSONDecodeError:
            last_error = f"{model} returned invalid JSON"
        except Exception as exc:
            last_error = f"{model}: {exc}"

    return _heuristic_fallback(messages, f"All LLM calls failed ({last_error}); heuristic fallback used.")


def _groq_sdk_fallback(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Direct Groq SDK call when LiteLLM is not installed."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _heuristic_fallback(messages, "GROQ_API_KEY not set and litellm unavailable.")

    try:
        from groq import Groq
    except ImportError:
        return _heuristic_fallback(messages, "Neither litellm nor groq SDK available.")

    convo_text = "\n".join([
        f"{m.get('sender', 'unknown')}: {m.get('text', '')}"
        for m in messages[-10:]
    ])

    try:
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
        raw_content = response.choices[0].message.content or ""
        raw_content = re.sub(r"^```(?:json)?\s*", "", raw_content.strip())
        raw_content = re.sub(r"\s*```$", "", raw_content.strip())
        parsed = json.loads(raw_content)

        parsed.setdefault("flags", [])
        parsed.setdefault("intent_score", 0.5)
        parsed.setdefault("dominant_pattern",
                          classify_stage(parsed["flags"],
                                         {"trust_building": False, "isolation": False, "secrecy": False, "escalation": False}))
        parsed.setdefault("reasoning", "Groq SDK analysis completed.")
        parsed["flags"] = _validate_llm_flags(parsed["flags"])
        return parsed
    except Exception:
        return _heuristic_fallback(messages, "Groq SDK call failed; heuristic fallback used.")


def bert_score(messages: list[dict[str, Any]]) -> float:
    """Return the current BERT probability for grooming-like text."""
    full_text = _combined_text(messages)
    if not full_text:
        return 0.0

    # 1. Try BERT only if the model files exist
    model_dir = os.path.join(os.path.dirname(__file__), 'saved_model_bert')
    if os.path.isdir(model_dir):
        try:
            from .predict_grooming_bert import predict_grooming_with_confidence as bert_predict
            result = bert_predict(full_text)
            return float(result.get("probability", 0.0))
        except Exception:
            pass

    # 2. Fall back to TF-IDF classifier
    try:
        from .predict_grooming import predict_grooming as tfidf_predict
        return float(tfidf_predict(full_text))
    except Exception:
        # Keep risk scoring useful for demos when model artifacts are unavailable.
        flags = _keyword_flags(messages)
        if not flags:
            return min(0.30 + len(messages) * 0.02, 0.50)
        return min(0.25 + 0.15 * len(flags), 0.9)


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
