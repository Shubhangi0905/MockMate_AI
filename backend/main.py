import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router as api_router


# Let project-local `.env` override any globally-set environment variables
# (common on Windows where variables may be set in the user/system profile).
load_dotenv(override=True)

app = FastAPI(title="AI Mock Interview Agent", version="0.1.0")

def _cors_origins() -> list[str]:
    raw = (os.getenv("CORS_ORIGINS") or "").strip()
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://mock-mate-ai-phi.vercel.app/",
    ]

def _cors_origin_regex() -> str | None:
    # Useful for Vercel preview deployments (optional).
    # Example: https://.*\.vercel\.app
    raw = (os.getenv("CORS_ORIGIN_REGEX") or "").strip()
    return raw or None


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_origin_regex=_cors_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = _env_int("PORT", 8000)
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
