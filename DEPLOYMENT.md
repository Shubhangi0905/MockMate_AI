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

Optionally, you can allow a regex (useful for Vercel preview deployments):

```env
CORS_ORIGIN_REGEX=https://.*\.vercel\.app
```

## Deploy (Render + Vercel)

### 1) Deploy backend on Render

1. Render → New → **Web Service** → connect your GitHub repo.
2. Settings:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3. Add environment variables in Render:
   - `LLM_PROVIDER=gemini` (or `openai`)
   - `GOOGLE_API_KEY=...` and `GEMINI_MODEL=gemini-2.5-flash` (or OpenAI equivalents)
   - `LLM_TEMPERATURE=0.2`
   - `CORS_ORIGINS=https://<your-vercel-domain>`
   - (Optional) `CORS_ORIGIN_REGEX=https://.*\.vercel\.app`
4. Deploy. Copy the Render service URL (example `https://your-service.onrender.com`).

### 2) Deploy frontend on Vercel

1. Vercel → New Project → import your GitHub repo.
2. In project settings:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Add environment variable in Vercel:
   - `VITE_API_BASE=https://<your-render-service>.onrender.com`
4. Deploy.

Notes:
- `frontend/vercel.json` includes a rewrite rule so page refresh works with Vue Router routes.
- Update `CORS_ORIGINS` in Render if your Vercel production domain changes.

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
