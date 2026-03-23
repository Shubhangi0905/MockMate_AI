# Deployment / Personal Use Notes

This project is intended for personal use and resume demos. No Docker required.

## Backend (FastAPI)

### Local (dev)

```powershell
cd "C:\Users\Hema Ranjan\Desktop\SHUBHANGI\MockMate AI"
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Alternative (npm script from repo root):

```powershell
npm.cmd run run_backend
```

### Local (production-like)

```powershell
cd "C:\Users\Hema Ranjan\Desktop\SHUBHANGI\MockMate AI"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Alternative (npm script from repo root):

```powershell
npm.cmd run run_backend_prod
```

### CORS for hosted frontend

Set `CORS_ORIGINS` as a comma-separated list in `.env`, for example:

```env
CORS_ORIGINS=https://your-frontend-domain.com
```

## Frontend (Vue)

### Local (dev)

```powershell
cd "C:\Users\Hema Ranjan\Desktop\SHUBHANGI\MockMate AI\frontend"
npm.cmd install
npm.cmd run dev
```

### Build (production)

Set API base URL at build time:

- Create `frontend/.env` with:
  - `VITE_API_BASE=https://your-backend-domain.com`

Then:

```powershell
cd "C:\Users\Hema Ranjan\Desktop\SHUBHANGI\MockMate AI\frontend"
npm.cmd run build
```

This generates `frontend/dist/`.

To preview locally:

```powershell
cd "C:\Users\Hema Ranjan\Desktop\SHUBHANGI\MockMate AI\frontend"
npm.cmd run preview
```

## Notes

- Backend session state is in-memory. Restarting the backend invalidates active sessions.
- If using Gemini free tier, you may hit request quotas (HTTP 429). Wait and retry or switch provider/model.
