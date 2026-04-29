#!/usr/bin/env bash
# rebuild_venv.sh — Rebuild /tmp/stem_venv with all pipeline dependencies
set -e

VENV=/tmp/stem_venv
PYTHON=/opt/homebrew/bin/python3.13

echo "=========================================="
echo "  STEM AI Studio — venv rebuild"
echo "  Target: $VENV"
echo "=========================================="

if [ -d "$VENV" ]; then
  echo "Removing existing venv…"
  rm -rf "$VENV"
fi

echo "Creating venv with $PYTHON…"
"$PYTHON" -m venv "$VENV"

echo "Upgrading pip…"
"$VENV/bin/pip" install --upgrade pip --quiet

echo "Installing packages (this may take a few minutes)…"
"$VENV/bin/pip" install \
  manim \
  manim-voiceover \
  pydub \
  fastapi \
  "uvicorn[standard]" \
  transformers \
  torch \
  scipy \
  soundfile \
  uroman \
  langgraph \
  langchain-openai \
  langchain-core \
  langchain-community \
  langchain-huggingface \
  faiss-cpu \
  edge-tts \
  kokoro-manim-voiceover \
  sympy \
  python-dotenv \
  requests \
  --quiet

echo ""
echo "=========================================="
echo "  Validating…"
echo "=========================================="

"$VENV/bin/python3" -c "
import manim, pydub, fastapi, uvicorn
import transformers, torch, scipy, soundfile, uroman
import langgraph, langchain_openai, langchain_core, requests
from manim_voiceover import VoiceoverScene
print('  All packages OK ✓')
"

echo ""
echo "=========================================="
echo "  DONE ✓"
echo ""
echo "  Start everything:  ./run_all.sh"
echo "  TTS only:          ./video_compiler/start_tts.sh --wait"
echo "  Orchestrator only: ./agent_core/start_orchestrator.sh --wait"
echo "=========================================="
