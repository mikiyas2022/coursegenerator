"""
config.py — Shared LLM configuration for all agents.

Supports both Ollama (default) and LM Studio via environment variable:
  export STEM_LLM_BACKEND=lmstudio   (default: ollama)
  export STEM_LLM_MODEL=qwen2.5-coder:32b
"""

import os
from langchain_openai import ChatOpenAI


# ── Ollama (default) ─────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_API_KEY  = "ollama"
OLLAMA_MODEL    = os.getenv("STEM_LLM_MODEL", "qwen2.5-coder:32b")

# ── LM Studio ────────────────────────────────────────────────────────────────
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY  = "lm-studio"
LM_STUDIO_MODEL    = os.getenv("STEM_LLM_MODEL", "qwen2.5-coder-32b-instruct")

# ── Backend selection ─────────────────────────────────────────────────────────
BACKEND = os.getenv("STEM_LLM_BACKEND", "ollama").lower()  # "ollama" | "lmstudio"

# ── TTS Server ────────────────────────────────────────────────────────────────
TTS_SERVER_URL       = os.getenv("TTS_SERVER_URL", "http://127.0.0.1:8100")
ORCHESTRATOR_PORT    = int(os.getenv("ORCHESTRATOR_PORT", "8200"))

# ── Manim environment ─────────────────────────────────────────────────────────
VENV_PYTHON = "/tmp/stem_venv/bin/python3"
VENV_MANIM  = "/tmp/stem_venv/bin/manim"
MANIM_ENV_PATCH = {
    "PATH":     "/tmp/stem_venv/bin:/Library/TeX/texbin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
    "HF_HOME":  "/tmp/huggingface_cache",
    "LIBGS":    "/opt/homebrew/lib/libgs.dylib",
    "TEXMFCNF": "/opt/homebrew/Cellar/texlive/20260301/share/texmf-dist/web2c",
}

MAX_CRITIC_RETRIES = 3


def get_llm(temperature: float = 0.15, max_tokens: int = 4096) -> ChatOpenAI:
    """Return a ChatOpenAI instance pointed at the configured local LLM backend."""
    if BACKEND == "lmstudio":
        return ChatOpenAI(
            model=LM_STUDIO_MODEL,
            openai_api_base=LM_STUDIO_BASE_URL,
            openai_api_key=LM_STUDIO_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    # default: Ollama
    return ChatOpenAI(
        model=OLLAMA_MODEL,
        openai_api_base=OLLAMA_BASE_URL,
        openai_api_key=OLLAMA_API_KEY,
        temperature=temperature,
        max_tokens=max_tokens,
    )
