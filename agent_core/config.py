"""
config.py — Shared LLM + Manim configuration for all agents.
v3: LOCAL paths are now discovered at runtime. No more hardcoded /opt/homebrew.
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# ── Project root ──────────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).parent.parent

# ── Automation flags ──────────────────────────────────────────────────────────
# Set AUTO_APPROVE=False to pause at storyboard review step
AUTO_APPROVE = os.getenv("AUTO_APPROVE", "true").lower() in ("true", "1", "yes")

# ── Local LLM endpoint (Ollama) ───────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")

# ── Role-based Model Routing (Local Inference) ────────────────────────────────
RESEARCHER_MODEL       = os.getenv("RESEARCHER_MODEL",       "llama3.1:latest")
SCRIPTWRITER_MODEL     = os.getenv("SCRIPTWRITER_MODEL",     "llama3.1:latest")
VISUAL_DESIGNER_MODEL  = os.getenv("VISUAL_DESIGNER_MODEL",  "llama3.1:latest")
MATH_VERIFIER_MODEL    = os.getenv("MATH_VERIFIER_MODEL",    "llama3.1:latest")
MANIM_CODER_MODEL      = os.getenv("MANIM_CODER_MODEL",      "qwen3-coder:30b")
CRITIC_MODEL           = os.getenv("CRITIC_MODEL",           "qwen3:8b")
VL_MODEL_NAME          = os.getenv("VL_MODEL_NAME",          "qwen3-vl:8b")

# ── TTS Server ────────────────────────────────────────────────────────────────
TTS_SERVER_URL    = os.getenv("TTS_SERVER_URL", "http://127.0.0.1:8102")
ORCHESTRATOR_PORT = int(os.getenv("ORCHESTRATOR_PORT", "8205"))

# ── Retry limits ──────────────────────────────────────────────────────────────
MAX_CRITIC_RETRIES = int(os.getenv("MAX_CRITIC_RETRIES", "3"))
MAX_VISUAL_RETRIES = int(os.getenv("MAX_VISUAL_RETRIES", "2"))


# ── Dynamic Manim / Python path discovery ────────────────────────────────────

def _find_manim_python() -> tuple[str, str]:
    """
    Discover the venv python + manim binary at runtime.
    Priority:
      1. VENV_PYTHON / VENV_MANIM env vars
      2. /tmp/stem_venv (standard build location)
      3. System PATH (conda / pipx installs)
    Returns (python_path, manim_path).
    """
    # Explicit override
    env_py    = os.getenv("VENV_PYTHON")
    env_manim = os.getenv("VENV_MANIM")
    if env_py and env_manim:
        return env_py, env_manim

    # Check standard venv
    venv_py    = "/tmp/stem_venv/bin/python3"
    venv_manim = "/tmp/stem_venv/bin/manim"
    if os.path.exists(venv_py) and os.path.exists(venv_manim):
        return venv_py, venv_manim

    # Fall back to system PATH
    sys_manim = shutil.which("manim")
    sys_py    = shutil.which("python3")
    if sys_manim and sys_py:
        return sys_py, sys_manim

    # Last resort — return the venv paths even if missing (let critic report missing)
    return venv_py, venv_manim


VENV_PYTHON, VENV_MANIM = _find_manim_python()


def _build_tex_env() -> dict[str, str]:
    """Discover TeX distribution path at runtime (no hardcoded version string)."""
    candidates = [
        "/Library/TeX/texbin",
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
    ]
    # Try to locate kpsewhich which implies a working TeX dist
    tex_bin = ""
    for c in candidates:
        if os.path.exists(os.path.join(c, "kpsewhich")):
            tex_bin = c
            break

    # Discover texmf-dist
    texmf_dist = os.getenv("TEXMFDIST", "")
    if not texmf_dist:
        # Try common brew paths
        import glob
        patterns = [
            "/opt/homebrew/Cellar/texlive/*/share/texmf-dist",
            "/usr/local/Cellar/texlive/*/share/texmf-dist",
            "/usr/share/texmf",
        ]
        for pat in patterns:
            matches = glob.glob(pat)
            if matches:
                texmf_dist = sorted(matches)[-1]  # latest version
                break

    path_parts = ["/tmp/stem_venv/bin"]
    if tex_bin:
        path_parts.append(tex_bin)
    path_parts += ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/bin"]

    env = {
        "PATH": ":".join(path_parts),
        "HF_HOME": os.getenv("HF_HOME", "/tmp/huggingface_cache"),
    }

    # libgs (Ghostscript) — find dynamically
    gs_candidates = [
        "/opt/homebrew/lib/libgs.dylib",
        "/usr/local/lib/libgs.dylib",
        "/usr/lib/libgs.so",
    ]
    for gs in gs_candidates:
        if os.path.exists(gs):
            env["LIBGS"] = gs
            break

    if texmf_dist and os.path.exists(texmf_dist):
        env["TEXMFCNF"]  = texmf_dist + "/web2c"
        env["TEXMFDIST"] = texmf_dist
        env["TEXMFMAIN"] = texmf_dist

    return env


MANIM_ENV_PATCH = _build_tex_env()

# ── Logs directory ────────────────────────────────────────────────────────────
LOGS_DIR = _PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)


# ── LLM factory ───────────────────────────────────────────────────────────────

def get_llm(model_name: str, temperature: float = 0.2, max_tokens: int = 4096) -> ChatOpenAI:
    """Unified ChatOpenAI instance pointing at local Ollama."""
    return ChatOpenAI(
        base_url=OLLAMA_BASE_URL,
        model=model_name,
        api_key="ollama-local",
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=1200,
        max_retries=1,
    )


def get_vl_llm(max_tokens: int = 600) -> ChatOpenAI:
    """VL (vision-language) model for visual critic."""
    return ChatOpenAI(
        base_url=OLLAMA_BASE_URL,
        model=VL_MODEL_NAME,
        api_key="ollama-local",
        temperature=0.1,
        max_tokens=max_tokens,
        timeout=120,
        max_retries=1,
    )