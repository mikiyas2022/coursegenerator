"""
config.py — Shared LLM + Manim configuration for all agents.

LLM endpoint points to your local Ollama instance running qwen3:30b.
Override via environment variables if needed:
  export LOCAL_BASE_URL=http://localhost:11434/v1
  export LLM_MODEL_NAME=qwen3-coder:30b
  export VL_MODEL_NAME=qwen2.5-vl:7b    (vision model for visual critic)
"""

import os
from langchain_openai import ChatOpenAI


# ── Local LLM endpoint (Ollama) ───────────────────────────────────────────────
LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL", "http://localhost:11434/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen3:8b")
VL_MODEL_NAME  = os.getenv("VL_MODEL_NAME",  "qwen3-vl:8b")   # vision critic

# ── TTS Server ────────────────────────────────────────────────────────────────
TTS_SERVER_URL    = os.getenv("TTS_SERVER_URL", "http://127.0.0.1:8100")
ORCHESTRATOR_PORT = int(os.getenv("ORCHESTRATOR_PORT", "8200"))

# ── Manim environment ─────────────────────────────────────────────────────────
VENV_PYTHON = "/tmp/stem_venv/bin/python3"
VENV_MANIM  = "/tmp/stem_venv/bin/manim"
MANIM_ENV_PATCH = {
    "PATH":     "/tmp/stem_venv/bin:/Library/TeX/texbin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
    "HF_HOME":  "/tmp/huggingface_cache",
    "LIBGS":    "/opt/homebrew/lib/libgs.dylib",
    "TEXMFCNF": "/opt/homebrew/Cellar/texlive/20260301/share/texmf-dist/web2c",
}

# ── Retry limits ──────────────────────────────────────────────────────────────
MAX_CRITIC_RETRIES = 3
MAX_VISUAL_RETRIES = 2


def get_llm(temperature: float = 0.2, max_tokens: int = 4096) -> ChatOpenAI:
    """
    Returns a ChatOpenAI instance pointed at the local Ollama endpoint.
    ChatOpenAI works flawlessly with Ollama's /v1 OpenAI-compatible API.
    """
    return ChatOpenAI(
        base_url=LOCAL_BASE_URL,
        model=LLM_MODEL_NAME,
        api_key="local-execution-does-not-need-a-key",
        temperature=temperature,
        max_tokens=max_tokens,
        request_timeout=900,
        max_retries=0,
    )


def get_vl_llm(max_tokens: int = 600) -> ChatOpenAI:
    """
    Returns a ChatOpenAI instance for the vision-language model.
    Used by the visual critic to inspect rendered Manim frames.
    """
    return ChatOpenAI(
        base_url=LOCAL_BASE_URL,
        model=VL_MODEL_NAME,
        api_key="local-execution-does-not-need-a-key",
        temperature=0.1,
        max_tokens=max_tokens,
    )