# MockMate AI

Python + FastAPI + LangGraph backend that:

- Analyzes resume (and optional JD)
- Generates an adaptive mock interview (1 question at a time)
- Evaluates each answer and adapts difficulty
- Produces a final report

## Setup

1) Create and activate a venv (Python 3.10+)
2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Configure environment:

- Copy `.env.example` → `.env`
- Set `LLM_PROVIDER` and the relevant API key(s)

## Run

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend (Vue)

The repo includes a Vue 3 + Vite UI in `frontend/` that connects to the FastAPI backend.

Features:
- Multi-page dashboard (Dashboard / Resume & JD / Interview / Report)
- Upload Resume + JD via PDF/TXT (or paste text)
- Structured report view + PDF download

1) Configure API base (optional):

- Copy `frontend/.env.example` → `frontend/.env`
- Edit `VITE_API_BASE` if your backend URL differs

2) Run:

```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://127.0.0.1:5173`.

Note: CORS is enabled in the backend for `http://localhost:5173` and `http://127.0.0.1:5173`.

## Project PDFs

Auto-generate project documentation PDFs:

```bash
python scripts/generate_project_pdfs.py
```

Output folder: `docs/pdfs/`

## Deployment notes (no Docker)

See `DEPLOYMENT.md`.

## API (MVP)

- `POST /upload` → creates a session from `resume_text` (+ optional `jd_text`)
- `POST /analyze` → runs analysis and returns skills/gaps (+ match score if JD)
- `POST /start-interview` → returns first question
- `POST /next-question` → returns current/next question (if not waiting for answer)
- `POST /submit-answer` → evaluates answer, adapts difficulty, returns next question (or ends)
- `GET /report?session_id=...` → returns final report when ready

Open Swagger UI at `http://127.0.0.1:8000/docs`.
