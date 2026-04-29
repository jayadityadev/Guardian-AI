# Guardian AI — Final API Contract (Backend ↔ Frontend ↔ ML)

## 1. Core Principle
This JSON structure is the **single source of truth** across ML, Backend, and Frontend.

- ML outputs this structure
- Backend stores and returns this structure
- Frontend renders this structure

No transformations, renaming, or omissions are allowed after contract lock.

---

## 2. Base URL
```
http://localhost:8000
```

---

## 3. Endpoints

### 3.1 POST /ingest

#### Description
Submit chat messages for analysis

#### Request Body
```json
{
  "platform": "json_upload",
  "messages": [
    {
      "sender": "stranger",
      "text": "hey you're really mature for your age",
      "timestamp": "2025-01-01T22:14:00Z"
    }
  ]
}
```

#### Response
```json
{
  "session_id": "uuid",
  "status": "processing"
}
```

---

### 3.2 POST /ingest/audio

#### Description
Upload audio → transcribe → analyse

#### Request
- Content-Type: multipart/form-data
- Field: `file`

#### Response
```json
{
  "session_id": "uuid",
  "transcript": "full text here",
  "status": "processing"
}
```

---

### 3.3 GET /session/{session_id}  ⭐ PRIMARY CONTRACT

#### Description
Returns FULL ML analysis. This MUST match the JSON contract exactly.

#### Response
```json
{
  "session_id": "uuid-v4",
  "platform": "json_upload",
  "timestamp": "2025-01-01T00:00:00Z",
  "risk_score": 78,
  "confidence": 0.91,
  "grooming_stage": "isolation",
  "flags": [
    {
      "type": "isolation_tactic",
      "snippet": "don't tell your parents about this",
      "severity": "high",
      "message_index": 14
    }
  ],
  "categories": ["isolation", "gift_lure"],
  "stage_progression": {
    "trust_building": true,
    "isolation": true,
    "secrecy": false,
    "escalation": false
  },
  "recommendation": "alert_parent",
  "drift_signals": {
    "late_night_messages": true,
    "message_frequency_spike": false,
    "new_unknown_contact": true
  }
}
```

---

### 3.4 GET /sessions

#### Description
List of previous sessions (lightweight)

#### Response
```json
[
  {
    "session_id": "uuid",
    "risk_score": 78,
    "timestamp": "2025-01-01T00:00:00Z",
    "recommendation": "alert_parent"
  }
]
```

---

### 3.5 WebSocket /ws/alerts

#### Description
Real-time notification when analysis completes

#### Event Payload
```json
{
  "event": "analysis_complete",
  "session_id": "uuid",
  "risk_score": 78,
  "recommendation": "alert_parent"
}
```

---

## 4. Enumerations (STRICT)

### Grooming Stage
- trust_building
- isolation
- secrecy
- escalation

### Recommendation
- monitor
- alert_parent
- escalate_platform

### Flag Types
- isolation_tactic
- gift_offering
- trust_building
- secrecy_request
- platform_hop
- age_probing
- request_escalation

---

## 5. Backend Responsibilities

Backend MUST:
- Return ALL fields (no missing keys)
- Maintain exact field names
- Map DB → contract correctly

### Required mappings

| Contract Field | Source |
|---------------|--------|
| session_id | DB id |
| timestamp | DB created_at |
| flags | raw_flag_json |
| drift_signals | drift_json |
| stage_progression | stage_progression_json |

---

## 6. ML Responsibilities

ML MUST:
- Output full contract-compatible structure
- Never omit required fields
- Keep types consistent

---

## 7. Frontend Responsibilities

Frontend MUST:
- Treat contract as final (no assumptions)
- Use exact fields provided
- Not infer missing values

---

## 8. Error Responses

### 400
```json
{ "error": "invalid input" }
```

### 404
```json
{ "error": "session not found" }
```

### 500
```json
{ "error": "internal server error" }
```

---

## 9. Contract Lock Rule (CRITICAL)

After lock:
- No field additions
- No field renaming
- No type changes

Violating this breaks:
- ML integration
- Backend storage
- Frontend rendering

---

## 10. Key Implementation Rule

The backend should act as a **pass-through normalizer**, not a transformer.

Flow:
ML → Backend (store) → Backend (return SAME structure) → Frontend

Any deviation introduces bugs.

