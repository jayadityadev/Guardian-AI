# Guardian AI — Child Sexual Predator Identification & Grooming Detection Platform

Guardian AI is a real-time monitoring and threat assessment platform designed to identify online grooming behaviors and protect children. By integrating local speech-to-text translation (audio upload), asynchronous background pipelines, and a dual-path classification logic (combining local deep learning models with state-of-the-art LLMs), Guardian AI analyzes conversation dynamics and visualizes risk vectors on an interactive parent alerts dashboard.

---

## 1. Features
- **Dual-Path NLP Classification**:
  - **Path A (Deep Learning)**: Fine-tuned **DistilBERT** sequence classification model running locally via PyTorch to score text segment grooming probabilities.
  - **Path B (LLM Analysis)**: Semantic flag and snippet extraction using **LLaMA** via Groq SDK/LiteLLM.
- **Speech-to-Text Ingestion**: Converts audio stream log inputs (WAV, MP3, M4A) to chat logs using a locally hosted OpenAI **Whisper** STT model.
- **Asynchronous Processing**: Ingest requests are accepted immediately (`202 Accepted`) and handled in background tasks to prevent thread blocks.
- **Neon PostgreSQL Persistence**: Complete storage of flagged conversations, stage progressions, drift signals, and historical sessions.
- **Real-time Alerting**: Live notifications and dashboard updates broadcast via WebSockets (`/ws/alerts`).
- **Interactive Alerts Dashboard**: React-based parent control center highlighting grooming stages (Trust Building, Isolation, Secrecy, Escalation) and tactical text snippets.

---

## 2. System Architecture

```mermaid
flowchart TD
  User[Parent / Client] -->|View Alerts| Dashboard[React Dashboard - Port 3000]
  User -->|Upload Chat/Audio| API[FastAPI Ingest - Port 8000]
  
  API -->|Write Jobs| DB[(Neon PostgreSQL)]
  API -->|Enqueue Task| TaskQueue[Asynchronous Background Worker]
  
  TaskQueue -->|STT Conversion| Whisper[Whisper STT Model]
  TaskQueue -->|Dual-Path Analysis| MLBridge[ML Orchestration Bridge]
  
  MLBridge -->|Path 1: Sequence Prob| DistilBERT[Local PyTorch DistilBERT Classifier]
  MLBridge -->|Path 2: Flag Extraction| Groq[Groq LLaMA Cloud API]
  
  MLBridge -->|Publish Complete| WSManager[WebSocket Alert Manager]
  WSManager -->|Broadcast alert| Dashboard
```

---

## 3. Tech Stack

### Frontend (Dashboard)
- React 19 + Vite (Port 3000)
- TailwindCSS 4
- Lucide React (Icons)
- Radix UI primitives & GSAP animations

### Backend (Orchestration)
- Python 3.14+
- FastAPI
- SQLAlchemy ORM & Alembic Migrations
- Psycopg2 binary (Postgres connection)
- Uvicorn server (Port 8000)

### ML & AI Pipelines
- PyTorch & Hugging Face Transformers (`distilbert-base-uncased`)
- OpenAI Whisper (`base` size) for STT
- Groq / LiteLLM APIs for snippet extraction

---

## 4. Getting Started

### Prerequisites
- Python 3.11+ (Local ML virtual environment uses Python 3.11; Backend environment uses Python 3.14)
- Node.js (v22+)
- Neon PostgreSQL Database URL

---

### Step 1: Environment Configuration
1. Create a `.env` file in the `backend/` directory:
   ```env
   APP_NAME=Guardian AI Backend
   APP_ENV=dev
   DATABASE_URL=postgresql+psycopg2://user:pass@host/dbname?sslmode=require
   GROQ_API_KEY=your_groq_api_key
   NVIDIA_API_KEY=your_nvidia_api_key

   # Optional: Configure if you deploy the ML sequence classifier separately (e.g. Modal)
   # ML_API_URL=https://your-modal-app.modal.run/infer
   # ML_API_KEY=optional_bearer_token
   ```
2. Create a `.env` file in the `frontend/` directory:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   VITE_WS_URL=ws://127.0.0.1:8000/ws/alerts
   VITE_USE_MOCK=false
   ```

---

### Step 2: Set Up the ML Pipeline
Choose **one** of the following options to load the DistilBERT sequence grooming model:

#### Option A (Recommended) — Download Pretrained Model
Runs immediately. 
1. Open the Google Colab Notebook located at [ml/train_on_colab.ipynb](ml/train_on_colab.ipynb) on Colab's free T4 GPU.
2. Run the cells to download the PAN 2012 dataset from Zenodo, execute Hinglish data augmentation, and fine-tune `distilbert-base-uncased`.
3. Download the generated `saved_model_bert.zip` and unzip its contents directly into:
   `ml/models/grooming_model/saved_model_bert/`

#### Option B — Train from Scratch
Takes ~35 minutes on CPU.
1. Activate the local ML virtual environment:
   ```powershell
   & "ml\.venv\Scripts\Activate.ps1"
   ```
2. Run the local training script:
   ```bash
   python ml/models/grooming_model/train_bert_grooming.py
   ```
   *(Note: This requires local PyTorch compilation. To enable local CUDA training, run `uv pip install torch --python ml\.venv\Scripts\python.exe` first).*

---

### Step 3: Run the Application

#### 1. Start the Backend Server
From the `backend/` directory, run:
```bash
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

#### 2. Start the Frontend Server
From the `frontend/` directory, run:
```bash
npm install
npm run dev -- --port 3000 --host 127.0.0.1
```

Once running, navigate to `http://127.0.0.1:3000/` in your browser to interact with the Guardian AI Parent alerts dashboard.
