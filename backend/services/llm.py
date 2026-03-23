from __future__ import annotations

import os


def get_llm():
    provider = (os.getenv("LLM_PROVIDER") or "openai").strip().lower()
    temperature = float(os.getenv("LLM_TEMPERATURE") or "0.2")

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        model = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "LLM_PROVIDER is set to 'openai' but OPENAI_API_KEY is missing. "
                "Either set OPENAI_API_KEY, or set LLM_PROVIDER=gemini and provide GOOGLE_API_KEY."
            )
        return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = os.getenv("GEMINI_MODEL") or "gemini-1.5-flash"
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "LLM_PROVIDER is set to 'gemini' but GOOGLE_API_KEY is missing. "
                "Set GOOGLE_API_KEY in .env."
            )
        return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=api_key)

    raise RuntimeError("Unsupported LLM_PROVIDER. Use: openai | gemini")
