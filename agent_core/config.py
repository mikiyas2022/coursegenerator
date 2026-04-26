"""
config.py — Shared LLM + Manim configuration for all agents.

Cloud LLM endpoint: OpenRouter (free-tier models).
Override any model via environment variable.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# ── Local LLM endpoint (Ollama) ──────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")

# ── Role-based Model Routing (Local Inference) ───────────────────────────────
#
# RESEARCHER    → gemma3:1b
# SCRIPTWRITER  → gemma3:1b
# MANIM_CODER   → gemma3:1b
# CRITIC / VL   → gemma3:1b
#
RESEARCHER_MODEL   = os.getenv("RESEARCHER_MODEL",   "llama3.1:latest")
SCRIPTWRITER_MODEL = os.getenv("SCRIPTWRITER_MODEL", "llama3.1:latest")
MANIM_CODER_MODEL  = os.getenv("MANIM_CODER_MODEL",  "qwen3-coder:30b")
CRITIC_MODEL       = os.getenv("CRITIC_MODEL",       "qwen3:8b")
VL_MODEL_NAME      = os.getenv("VL_MODEL_NAME",      "qwen3-vl:8b")

# ── TTS Server ────────────────────────────────────────────────────────────────
TTS_SERVER_URL    = os.getenv("TTS_SERVER_URL", "http://127.0.0.1:8102")
ORCHESTRATOR_PORT = int(os.getenv("ORCHESTRATOR_PORT", "8205"))

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

def get_llm(model_name: str, temperature: float = 0.2, max_tokens: int = 4096) -> ChatOpenAI:
    """
    Returns a unified ChatOpenAI instance pointed at local Ollama.
    """
    return ChatOpenAI(
        base_url=OLLAMA_BASE_URL,
        model=model_name,
        api_key="ollama-local",
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=1200,  # 20 minutes for local CPU inference
        max_retries=1,
    )

def get_vl_llm(max_tokens: int = 600) -> ChatOpenAI:
    """
    Returns a ChatOpenAI instance for the vision-language model.
    Used by the visual critic to inspect rendered Manim frames locally.
    """
    return ChatOpenAI(
        base_url=OLLAMA_BASE_URL,
        model=VL_MODEL_NAME,
        api_key="ollama-local",
        temperature=0.1,
        max_tokens=max_tokens,
        timeout=120,
        max_retries=1,
    )