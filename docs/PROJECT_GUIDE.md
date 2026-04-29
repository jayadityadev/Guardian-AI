# Guardian AI — Ultimate Project Guide
> **Hackathon target: 1500hrs today → 0400hrs tomorrow (13 hours)**
> Child Online Predator Behaviour Pattern Detector

---

## Table of Contents
1. [What We Are Building](#what-we-are-building)
2. [The JSON Contract](#the-json-contract)
3. [System Architecture](#system-architecture)
4. [Jay — Backend](#jay--backend)
5. [Jaggu — ML Pipeline](#jaggu--ml-pipeline)
6. [Arun — Frontend](#arun--frontend)
7. [Aniket — Data & DevOps](#aniket--data--devops)
8. [Phase Timeline](#phase-timeline)
9. [Sync Checkpoints](#sync-checkpoints)
10. [Demo Script](#demo-script)
11. [Presentation Talking Points](#presentation-talking-points)

---

## What We Are Building

### One-line pitch
> Guardian AI is an ML-powered grooming behaviour detector that analyses chat patterns — timing, tone shifts, isolation tactics, gift-offering language — and generates real-time risk alerts for parents. It understands Hindi and Hinglish. No existing platform does this.

### The product (exactly three things)
1. **ML inference engine** — the actual deliverable. BERT + Groq LLaMA analyses conversation patterns and outputs a structured risk JSON.
2. **Input interface** — a minimal web UI to upload a JSON chat log or an audio file. That's it. No chat app. No real-time interception.
3. **Parent alert dashboard** — displays risk score (0–100), flagged snippets, detected grooming stage, and recommended action.

### What we are NOT building
- A chat app (dropped — was a legal workaround, not the product)
- Real-time message interception
- Mobile app
- Browser extension
- User authentication

The demo chat app exists only as **pre-prepared JSON files** that we upload during the demo. The product is the pipeline that processes them.

### X-factors that make this winnable
| Feature | Why it matters |
|---------|----------------|
| Hindi + Hinglish NLP | No competitor does this. 500M+ untouched market |
| Behavioural sequence detection | Detects grooming *arc*, not keywords |
| Behavioural drift over time | First-mover — no existing platform does this |
| DPDP Act 2023 compliant architecture | Raw messages never stored |
| Audio input with STT | Voice grooming detection — jaw-drop demo moment |

---

## The JSON Contract

**Locked at 1700hrs. Never changes. Everyone builds around this.**

This is the single output that Jaggu's ML produces, Jay's backend stores, and Arun's frontend displays.

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
    },
    {
      "type": "gift_offering",
      "snippet": "I'll buy you Robux if you keep this between us",
      "severity": "high",
      "message_index": 21
    },
    {
      "type": "trust_building",
      "snippet": "you're so mature for your age",
      "severity": "medium",
      "message_index": 3
    }
  ],
  "categories": ["isolation", "gift_lure", "trust_building"],
  "stage_progression": {
    "trust_building": true,
    "isolation": true,
    "secrecy": true,
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

**Recommendation values:** `monitor` | `alert_parent` | `escalate_platform`

**Grooming stage values:** `trust_building` | `isolation` | `secrecy` | `escalation`

**Flag type values:** `isolation_tactic` | `gift_offering` | `trust_building` | `secrecy_request` | `platform_hop` | `age_probing` | `request_escalation`

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│  INPUT LAYER                                    │
│  Web UI — upload JSON chat log OR audio file    │
└────────────────────┬────────────────────────────┘
                     │ HTTP POST
                     ▼
┌─────────────────────────────────────────────────┐
│  INGESTION SERVICE  (FastAPI)                   │
│  POST /ingest       — JSON chat log             │
│  POST /ingest/audio — audio file → STT          │
│  Normalises to standard message schema          │
└────────────────────┬────────────────────────────┘
                     │ normalised messages
                     ▼
┌─────────────────────────────────────────────────┐
│  ML INFERENCE CORE  ← THE DELIVERABLE           │
│                                                 │
│  Hinglish Tokeniser                             │
│       ↓                    ↓                    │
│  BERT classifier      Groq LLaMA 70B            │
│  (sequence patterns)  (intent analysis)         │
│       ↓                    ↓                    │
│       └──── Weighted Risk Scorer ───┘           │
│                     ↓                           │
│         Grooming Stage Classifier               │
│         Behavioural Drift Engine                │
│                     ↓                           │
│              Risk JSON output                   │
└────────────────────┬────────────────────────────┘
                     │ stores score + snippets only
                     ▼
┌─────────────────────────────────────────────────┐
│  PostgreSQL                                     │
│  sessions · scores · flags  (no raw messages)   │
└────────────────────┬────────────────────────────┘
                     │ WebSocket push
                     ▼
┌─────────────────────────────────────────────────┐
│  PARENT DASHBOARD  (React)                      │
│  Risk score · Flagged snippets · Stage arc      │
│  Drift signals · Recommended action             │
└─────────────────────────────────────────────────┘
```

### Tech stack
| Layer | Tech |
|-------|------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| ML | HuggingFace Transformers (BERT), Groq SDK |
| STT | OpenAI Whisper (local, `whisper` pip package) |
| Database | PostgreSQL |
| Frontend | React, Vite, TailwindCSS |
| Real-time | WebSockets (FastAPI native) |
| DevOps | Docker, Docker Compose |
| Repo | GitHub, MIT licence |

---

## Jay — Backend

### Your role
You own everything between the frontend and the ML model. FastAPI, PostgreSQL, WebSocket, scoring logic, and the audio STT pipeline.

### Deliverables checklist

#### Phase 0 (1500–1700) — Setup
- [x] Init FastAPI project with `uv` — `uv init guardian-backend`
- [x] Install deps: `fastapi uvicorn sqlalchemy psycopg2 python-multipart websockets openai-whisper groq`
- [x] Connect to PostgreSQL — verify connection works
- [x] Create DB schema (see below)
- [x] Stub all three endpoints (return dummy 200)
- [x] Share JSON contract with team — **lock it at 1700**

#### Phase 1 (1700–2100) — Core build
- [x] `POST /ingest` — accepts JSON body (array of messages), returns `session_id`
- [x] `POST /ingest/audio` — accepts multipart audio file, runs Whisper STT, converts transcript to message array, passes to same pipeline as `/ingest`
- [x] `GET /session/{session_id}` — returns full risk JSON for a session
- [x] `GET /sessions` — returns list of past sessions (id, score, timestamp, recommendation)
- [x] `WebSocket /ws/alerts` — broadcasts when a session analysis completes
- [x] Scoring engine: takes Jaggu's raw output, applies weighting, writes to DB
- [x] Whisper integration: `whisper.load_model("base")`, transcribe audio, chunk into messages by pause detection

#### Phase 2 (2100–0100) — Integration
- [x] Wire Jaggu's ML module into `/ingest` endpoint
- [ ] Test full flow: upload JSON → ML runs → score in DB → WebSocket fires
- [ ] Test audio flow: upload MP3 → Whisper → ML → score
- [x] CORS configured for React frontend
- [x] Error handling: bad JSON, empty audio, ML timeout fallback

#### Phase 3 (0100–0400) — Polish
- [x] Health check endpoint `GET /health`
- [ ] Seed DB with demo session results (so dashboard looks populated on first open)
- [ ] Confirm WebSocket works in demo environment

---

### PostgreSQL schema

```sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  platform VARCHAR(50) DEFAULT 'json_upload',
  created_at TIMESTAMP DEFAULT NOW(),
  risk_score INTEGER,
  confidence FLOAT,
  grooming_stage VARCHAR(50),
  recommendation VARCHAR(50),
  raw_flag_json JSONB,
  drift_json JSONB,
  stage_progression_json JSONB
);

-- raw messages are NEVER stored
-- only scores and flag snippets go in raw_flag_json
```

---

### API spec

#### POST /ingest
```
Request body:
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

Response:
{
  "session_id": "uuid",
  "status": "processing"
}
```

#### POST /ingest/audio
```
Request: multipart/form-data
  file: <audio file — mp3, wav, m4a>

Response:
{
  "session_id": "uuid",
  "transcript": "full text here",
  "status": "processing"
}
```

#### GET /session/{session_id}
```
Response: full risk JSON (the contract above)
```

#### WebSocket /ws/alerts
```
On session complete, broadcast:
{
  "event": "analysis_complete",
  "session_id": "uuid",
  "risk_score": 78,
  "recommendation": "alert_parent"
}
```

---

### Whisper STT integration

```python
import whisper

model = whisper.load_model("base")  # ~140MB, loads once at startup

def transcribe_audio(file_path: str) -> str:
    result = model.transcribe(file_path)
    return result["text"]

def audio_to_messages(transcript: str) -> list[dict]:
    # Split on natural pauses / punctuation into message chunks
    # Tag all as sender="unknown" for demo
    sentences = transcript.split(". ")
    return [
        {"sender": "unknown", "text": s.strip(), "timestamp": ""}
        for s in sentences if s.strip()
    ]
```

---

## Jaggu — ML Pipeline

### Your role
You own the intelligence of the product. BERT sequence classifier + Groq intent analysis + risk scorer. Your output is the JSON contract. Everything else depends on it.

### Deliverables checklist

#### Phase 0 (1500–1700) — Setup
- [x] Test Groq API key — run a hello world call with `llama-3.3-70b-versatile`
- [x] Install: `transformers torch groq sentence-transformers`
- [x] Confirm HuggingFace model download works: `bert-base-multilingual-cased`
- [ ] Jupyter notebook environment ready
- [x] Read and agree JSON contract

#### Phase 1 (1700–2100) — Core build
- [ ] **Hinglish tokeniser** — use `bert-base-multilingual-cased` which handles Hindi + English natively. Test with: *"yaar kisi ko mat batana"* and *"free coins dunga bhai"*
- [x] **BERT classifier** — fine-tune or use zero-shot on PAN 2012 labels. Classify each message as: `grooming` / `normal`. Use `pipeline("text-classification")`.
- [x] **Groq prompt** — send sliding window of last 10 messages to Groq. Get back structured intent analysis. See prompt below.
- [x] **Risk scorer** — combine BERT confidence + Groq score into weighted 0–100. See formula below.
- [x] **Stage classifier** — rule-based from flag types. See logic below.
- [x] **Drift engine** — check timestamps for late-night patterns, frequency spikes.
- [x] Wrap everything into single function: `analyse(messages: list[dict]) -> dict` that returns the JSON contract.

#### Phase 2 (2100–0100) — Integration with Jay
- [x] Expose `analyse()` as importable module (not a script)
- [x] Jay calls your function from FastAPI endpoint
- [ ] Test with real PAN 2012 samples — verify output matches contract schema exactly
- [x] Fallback: if Groq API fails/times out, return BERT-only result with `confidence: 0.7`

#### Phase 3 (0100–0400) — Polish
- [ ] Test Hinglish demo conversation — verify flags fire correctly
- [ ] Tune weights if demo score feels off
- [ ] Confirm model loads in under 10 seconds at startup

---

### Groq prompt (copy this exactly, tune if needed)

```python
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
"""

def groq_analyse(messages: list[dict]) -> dict:
    from groq import Groq
    client = Groq()
    
    convo_text = "\n".join([
        f"{m['sender']}: {m['text']}" for m in messages[-10:]
    ])
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": GROQ_SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyse this conversation:\n\n{convo_text}"}
        ],
        temperature=0.1,
        max_tokens=500
    )
    
    import json
    return json.loads(response.choices[0].message.content)
```

---

### Risk scoring formula

```python
def calculate_risk_score(bert_score: float, groq_score: float, flag_count: int) -> int:
    # bert_score: 0.0–1.0 (BERT confidence that conversation is grooming)
    # groq_score: 0.0–1.0 (Groq intent_score)
    # flag_count: number of distinct flags detected
    
    base = (bert_score * 0.4) + (groq_score * 0.4) + (min(flag_count, 5) / 5 * 0.2)
    return min(int(base * 100), 100)
```

---

### Grooming stage classification logic

```python
def classify_stage(flags: list[dict], stage_progression: dict) -> str:
    types = {f["type"] for f in flags}
    
    if "request_escalation" in types:
        return "escalation"
    if "secrecy_request" in types or "platform_hop" in types:
        return "secrecy"
    if "isolation_tactic" in types:
        return "isolation"
    if "trust_building" in types or "gift_offering" in types:
        return "trust_building"
    return "none"
```

---

### BERT setup (fast path for hackathon)

```python
from transformers import pipeline

# Multilingual BERT — handles Hindi, English, Hinglish
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"  # fallback if multilingual BERT too slow
)

GROOMING_LABELS = [
    "grooming and predatory behaviour",
    "normal friendly conversation"
]

def bert_score(messages: list[dict]) -> float:
    full_text = " ".join([m["text"] for m in messages])
    result = classifier(full_text, GROOMING_LABELS)
    grooming_idx = result["labels"].index("grooming and predatory behaviour")
    return result["scores"][grooming_idx]
```

> **If BERT model download is too slow:** use `distilbert-base-uncased` as fallback. Smaller, faster, English-only. Still works for demo.

---

### Master analyse() function

```python
def analyse(messages: list[dict]) -> dict:
    import uuid
    
    bert_conf = bert_score(messages)
    groq_result = groq_analyse(messages)
    
    flags = groq_result.get("flags", [])
    risk = calculate_risk_score(bert_conf, groq_result.get("intent_score", 0.5), len(flags))
    
    stage_prog = {
        "trust_building": any(f["type"] in ["trust_building", "gift_offering"] for f in flags),
        "isolation": any(f["type"] == "isolation_tactic" for f in flags),
        "secrecy": any(f["type"] in ["secrecy_request", "platform_hop"] for f in flags),
        "escalation": any(f["type"] == "request_escalation" for f in flags),
    }
    
    recommendation = (
        "escalate_platform" if risk >= 80
        else "alert_parent" if risk >= 50
        else "monitor"
    )
    
    return {
        "session_id": str(uuid.uuid4()),
        "platform": "json_upload",
        "risk_score": risk,
        "confidence": round(groq_result.get("intent_score", bert_conf), 2),
        "grooming_stage": classify_stage(flags, stage_prog),
        "flags": flags,
        "categories": list({f["type"] for f in flags}),
        "stage_progression": stage_prog,
        "recommendation": recommendation,
        "drift_signals": detect_drift(messages),
    }
```

---

## Arun — Frontend

### Your role
You own both the input interface and the parent dashboard. Two React views. You build on mock data first, then connect to real backend in Phase 2.

### Deliverables checklist

#### Phase 0 (1500–1700) — Setup
- [ ] `npm create vite@latest guardian-frontend -- --template react`
- [ ] Install: `npm install tailwindcss axios react-router-dom recharts`
- [ ] Setup Tailwind
- [ ] Create two routes: `/upload` and `/dashboard/:sessionId`
- [ ] Create mock JSON matching the contract (copy from this doc) — use it for all Phase 1 UI work

#### Phase 1 (1700–2100) — Build UI on mock data
**Upload page (`/upload`):**
- [ ] Clean centered layout — Guardian AI logo/title at top
- [ ] Two upload options side by side:
  - **JSON chat log** — file picker, accepts `.json` only, shows filename on select
  - **Audio file** — file picker, accepts `.mp3 .wav .m4a`, shows filename on select
- [ ] Single "Analyse" button — disabled until a file is selected
- [ ] On click: show loading spinner with message "Analysing conversation patterns..."
- [ ] On complete: redirect to `/dashboard/:sessionId`
- [ ] Below upload: small text — "Files are never stored. Only risk scores are retained."

**Dashboard page (`/dashboard/:sessionId`):**
- [ ] **Risk score panel** — large number (0–100), colour coded:
  - 0–40: green background, "Low risk — monitor"
  - 41–70: amber background, "Medium risk — review"
  - 71–100: red background, "High risk — act now"
- [ ] **Grooming stage arc** — four stages as horizontal pills: Trust building → Isolation → Secrecy → Escalation. Completed stages filled, current stage highlighted, future stages grey.
- [ ] **Flagged snippets panel** — list of flags, each showing:
  - Badge with flag type (colour coded by severity)
  - The snippet text in quotes
  - Severity tag: HIGH / MEDIUM / LOW
- [ ] **Drift signals panel** — three signal cards: Late-night messages / New unknown contact / Message frequency spike. Green tick or red cross per signal.
- [ ] **Recommended action banner** — full width, three states:
  - Monitor: blue — "Continue monitoring. No immediate action needed."
  - Alert parent: amber — "Unusual patterns detected. Recommended: speak with your child."
  - Escalate: red — "High-risk behaviour detected. Report to platform and authorities."
- [ ] **Past sessions sidebar** — list of previous analyses, clickable, shows score + timestamp

#### Phase 2 (2100–0100) — Connect to real backend
- [ ] Replace mock data with real `axios.post('/ingest', formData)`
- [ ] Connect WebSocket to `ws://localhost:8000/ws/alerts`
- [ ] On WebSocket message `analysis_complete` → fetch session and update dashboard
- [ ] `GET /sessions` to populate sidebar
- [ ] Handle loading state and error state gracefully

#### Phase 3 (0100–0400) — Polish
- [ ] Mobile-responsive layout (judges may view on phone)
- [ ] Smooth loading animation between upload and results
- [ ] Confirm demo flow works: upload JSON → dashboard populates with real data
- [ ] Test with Hinglish demo file — confirm flags display correctly

---

### UI colour reference
```
Risk low:     bg-green-100  text-green-800  border-green-300
Risk medium:  bg-amber-100  text-amber-800  border-amber-300
Risk high:    bg-red-100    text-red-800    border-red-300

Flag high:    bg-red-500    text-white
Flag medium:  bg-amber-500  text-white
Flag low:     bg-blue-500   text-white

Stage done:   bg-purple-600 text-white
Stage active: bg-purple-200 text-purple-900 ring-2 ring-purple-600
Stage future: bg-gray-100   text-gray-400
```

---

### Mock data file (use this for Phase 1 development)

Create `/src/mock/demoSession.json` — paste the full JSON contract from the top of this doc with `risk_score: 78` and two or three flags filled in.

---

## Aniket — Data & DevOps

### Your role
You own the dataset, the demo data files, Docker Compose, and the README. The demo lives or dies on the quality of your prepared chat files. This is not a support role — it is mission critical.

### Deliverables checklist

#### Phase 0 (1500–1700) — Setup
- [ ] Create GitHub repo: `guardian-ai` — public, MIT licence
- [ ] Folder structure:
  ```
  /guardian-ai
  ├── backend/
  ├── frontend/
  ├── ml/
  ├── data/
  │   ├── pan2012/
  │   ├── synthetic/
  │   └── demo/
  ├── docker-compose.yml
  └── README.md
  ```
- [ ] Invite all team members as collaborators
- [ ] Create `.env.example` with all required keys

#### Phase 1 (1700–2100) — Dataset + demo data
**PAN 2012 dataset:**
- [ ] Download from: https://pan.webis.de/clef12/pan12-web/sexual-predator-identification.html
- [ ] Extract and place in `data/pan2012/`
- [ ] Write `ml/data_loader.py` — loads PAN 2012 into list of `{sender, text, timestamp, label}` dicts
- [ ] Verify at least 500 grooming + 500 normal samples load correctly

**Synthetic demo files (most important job):**

Create these exact files in `data/demo/`:

**`demo_high_risk.json`** — full grooming arc, score should hit 80+
```
Conversation of ~25 messages showing:
- Messages 1–8:   trust building ("you're so mature", "I totally get you")
- Messages 9–15:  isolation ("don't tell your parents", "this is our thing")
- Messages 16–20: gift offering ("I'll buy you Robux", "I can send you money")
- Messages 21–25: secrecy escalation ("delete these messages", "move to Snapchat")
```

**`demo_hinglish.json`** — Hindi/Hinglish version of above. Key phrases to include:
- `"yaar kisi ko mat batana"` (don't tell anyone)
- `"free coins dunga bhai"` (I'll give you free coins)
- `"tu bahut samajhdar hai"` (you're very smart/mature)
- `"apni mummy ko mat bata"` (don't tell your mum)
- `"sirf hamare beech mein rahe"` (keep this between us)

**`demo_low_risk.json`** — normal gaming chat, score should stay below 30
```
Normal conversation about game strategy, scores, favourite characters.
No grooming patterns. Casual friendly chat between two players.
```

**`demo_audio_script.txt`** — script for recording the audio demo
```
Write a 30-second script with grooming language in English.
Record it as an MP3. Save as data/demo/demo_audio.mp3
This is the jaw-drop moment of the demo.
```

#### Phase 2 (2100–0100) — Docker + deployment
- [ ] `docker-compose.yml`:
  ```yaml
  services:
    db:
      image: postgres:15
      environment:
        POSTGRES_DB: guardianai
        POSTGRES_USER: guardian
        POSTGRES_PASSWORD: guardian123
    backend:
      build: ./backend
      depends_on: [db]
      ports: ["8000:8000"]
      env_file: .env
    frontend:
      build: ./frontend
      ports: ["3000:3000"]
  ```
- [ ] `backend/Dockerfile` and `frontend/Dockerfile`
- [ ] Test: `docker compose up` spins entire stack
- [ ] `.env.example` with `GROQ_API_KEY`, `DATABASE_URL`

#### Phase 3 (0100–0400) — README + final polish
- [ ] `README.md` must include:
  - [ ] One-line pitch
  - [ ] Architecture diagram (link to the one in this doc)
  - [ ] Setup instructions: `cp .env.example .env` → `docker compose up`
  - [ ] Demo instructions: which files to upload and in what order
  - [ ] Tech stack table
  - [ ] X-factors section (from the features doc)
  - [ ] Team members
  - [ ] MIT licence badge
- [ ] Verify repo is public
- [ ] Tag release `v1.0.0-hackathon`

---

## Phase Timeline

| Time | Phase | Status |
|------|-------|--------|
| 1500–1700 | Phase 0 — Foundation | All setup, JSON contract locked |
| 1700–2100 | Phase 1 — Core build | Fully parallel, no dependencies |
| 2100–0100 | Phase 2 — Integration | Pair: Jay+Jaggu, Arun+Jay, Aniket solo |
| 0100–0400 | Phase 3 — Polish + demo | All hands, fix bugs, prep presentation |

---

## Sync Checkpoints

### Checkpoint 1 — 1700hrs (mandatory)
Everyone stops and verifies:
- [ ] JSON contract printed/shared — everyone has a copy
- [ ] All repos cloned and running locally
- [ ] Groq API key works — Jaggu confirms
- [ ] FastAPI returns 200 on all stub endpoints — Jay confirms
- [ ] React app loads at localhost:3000 — Arun confirms
- [ ] Git repo is public with MIT licence — Aniket confirms

**Do not proceed to Phase 1 until all six boxes are checked.**

### Checkpoint 2 — 2100hrs (go/no-go for integration)
- [ ] Jaggu: `analyse(messages)` returns valid JSON matching contract on test input
- [ ] Jay: all three endpoints return real responses (even if ML is stubbed)
- [ ] Arun: both pages render correctly with mock data
- [ ] Aniket: demo JSON files ready and validated

**If Jaggu's ML is not ready:** Jay uses a stub that returns hardcoded risk JSON. Integration continues. Jaggu finishes ML separately.

### Checkpoint 3 — 0100hrs (full flow must work)
- [ ] Upload `demo_high_risk.json` → dashboard shows score 75+, flags visible
- [ ] Upload `demo_low_risk.json` → dashboard shows score below 35
- [ ] Upload audio file → transcript visible, score generated
- [ ] WebSocket updates dashboard without page refresh

**If audio is broken at 0100:** drop it from demo. Do not spend more than 30 minutes debugging.

---

## Demo Script

### Setup (before judges arrive)
1. Open two browser tabs: Tab 1 = `localhost:3000/upload`, Tab 2 = `localhost:3000/dashboard` (pre-seeded with a session)
2. Have `demo_high_risk.json`, `demo_hinglish.json`, `demo_low_risk.json` on desktop
3. Have `demo_audio.mp3` ready

### Demo flow (5 minutes)

**Step 1 — Open with the problem (30 seconds)**
> "Existing content moderation catches explicit words. It completely misses this —"
> *[show demo_high_risk.json contents briefly — looks like a normal conversation]*

**Step 2 — Upload and analyse (60 seconds)**
> "We upload this chat log. Guardian AI's ML pipeline analyses the behavioural sequence."
> *[upload demo_high_risk.json, click Analyse, show loading]*

**Step 3 — Show the result (90 seconds)**
> "Risk score 82. The model detected isolation tactics, gift offering, and secrecy escalation. Four stages of a classic grooming arc — across 25 messages. No single message would have triggered a keyword filter."
> *[walk through dashboard — score, stage arc, flagged snippets, recommended action]*

**Step 4 — Hinglish moment (60 seconds)**
> "We're building for India. No existing platform detects grooming in Hindi."
> *[upload demo_hinglish.json — show same flags firing on Hindi phrases]*

**Step 5 — Audio input (30 seconds)**
> "Voice messages too."
> *[upload demo_audio.mp3 — show transcript, show score]*

**Step 6 — Close (30 seconds)**
> "Guardian AI. Behavioural pattern detection. Hindi and Hinglish. DPDP Act compliant. No platform does all four."

---

## Presentation Talking Points

### Lead with the gap
> "Content moderation catches explicit words. Real grooming never uses explicit words in the early stages. It looks like a friendly conversation. That's why parents find out too late."

### The ML angle (for technical judges)
> "We're not doing keyword matching. BERT analyses multi-turn conversation sequences — the arc from trust building to isolation to secrecy. A single message scores low. The pattern across 20 messages scores 82."

### The India angle (market judges)
> "Bark, Qustodio, mSpy — all English-only. India has 500 million Hindi speakers. No product exists for this market. Guardian AI understands Hinglish natively using multilingual BERT."

### The privacy angle (ethics judges)
> "We never store raw messages. PostgreSQL only holds risk scores and flagged snippets. This is DPDP Act 2023 compliant by architecture, not by policy."

### If asked "what about real platforms?"
> "Our ingestion service accepts a normalised message schema. Any adapter — a browser extension reading WhatsApp Web's DOM, an Android Accessibility Service, a platform API — can POST to it. Today we demonstrate with uploaded chat logs. The ML pipeline is the product."

### If asked "why not just use ChatGPT?"
> "Groq gives us sub-second inference at zero cost. We use LLaMA 70B for intent analysis but pair it with a fine-tuned BERT classifier for sequence patterns — something a general-purpose LLM isn't optimised for. The combination gives us both speed and accuracy."

---

## Environment Variables

```env
# .env (copy from .env.example, never commit)
GROQ_API_KEY=your_key_here
DATABASE_URL=postgresql://guardian:guardian123@localhost:5432/guardianai
WHISPER_MODEL=base
FRONTEND_URL=http://localhost:3000
```

---

## Git Conventions (Aniket enforces)

```
main          — working code only, tagged for demo
dev           — integration branch
feat/jay-*    — Jay's feature branches
feat/jaggu-*  — Jaggu's feature branches
feat/arun-*   — Arun's feature branches
```

Commit format: `type: short description`
Examples: `feat: add /ingest endpoint`, `fix: groq json parse error`, `chore: docker compose setup`

**Never push broken code to main. PR to dev, merge to main only at checkpoints.**

---

*Guardian AI — PS-01 Hackathon*
*Built in 13 hours. MIT Licence.*
