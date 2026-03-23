from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class MappedError:
    status_code: int
    detail: Any
    headers: dict[str, str] | None = None


_RETRY_RE = re.compile(r"retry in\s+(\d+(?:\.\d+)?)s", re.IGNORECASE)


def _extract_retry_after_seconds(message: str) -> int | None:
    m = _RETRY_RE.search(message or "")
    if not m:
        return None
    try:
        return max(0, int(float(m.group(1))))
    except ValueError:
        return None


def map_llm_exception(exc: Exception) -> MappedError | None:
    """
    Best-effort mapping of provider errors to HTTP-friendly errors.
    Returns None if the exception is not recognized.
    """
    msg = str(exc)

    # Gemini (langchain-google-genai) wraps google.genai 429 into ChatGoogleGenerativeAIError.
    if "RESOURCE_EXHAUSTED" in msg or "Quota exceeded" in msg or "generate_content_free_tier_requests" in msg:
        retry_after = _extract_retry_after_seconds(msg)
        headers = {"Retry-After": str(retry_after)} if retry_after else None
        detail: dict[str, Any] = {
            "message": "Rate limit / quota exceeded for the current LLM. Please wait and retry.",
            "provider": "gemini",
        }
        if retry_after is not None:
            detail["retry_after_seconds"] = retry_after
        return MappedError(status_code=429, detail=detail, headers=headers)

    # OpenAI-like rate limit phrasing (covers many wrappers)
    if "rate limit" in msg.lower() or "429" in msg:
        retry_after = _extract_retry_after_seconds(msg)
        headers = {"Retry-After": str(retry_after)} if retry_after else None
        detail = {"message": "Rate limit hit for the current LLM. Please wait and retry."}
        if retry_after is not None:
            detail["retry_after_seconds"] = retry_after
        return MappedError(status_code=429, detail=detail, headers=headers)

    return None

