#!/usr/bin/env bash
# rebuild_venv.sh — Create /tmp/stem_venv with all pipeline dependencies
# Replaces the old Edge-TTS stack with local Meta MMS TTS via FastAPI.
set -e

VENV=/tmp/stem_venv
PYTHON=/opt/homebrew/bin/python3.13

echo "========================================="
echo "  STEM Pipeline — venv rebuild"
echo "  Target: $VENV"
echo "========================================="

# ── Remove any existing (possibly corrupt) venv ───────────────────────────────
if [ -d "$VENV" ]; then
  echo "Removing existing venv …"
  rm -rf "$VENV"
fi

# ── Create fresh venv ─────────────────────────────────────────────────────────
echo "Creating venv with $PYTHON …"
"$PYTHON" -m venv "$VENV"

# ── Upgrade pip ───────────────────────────────────────────────────────────────
echo "Upgrading pip …"
"$VENV/bin/pip" install --upgrade pip --quiet

# ── Core packages ─────────────────────────────────────────────────────────────
echo "Installing core pipeline packages …"
"$VENV/bin/pip" install \
  manim \
  pydub \
  fastapi \
  "uvicorn[standard]" \
  transformers \
  torch \
  scipy \
  soundfile \
  uroman \
  --quiet

echo ""
echo "========================================="
echo "  Validating installation …"
echo "========================================="

"$VENV/bin/python3" -c "
from manim import *
import pydub, fastapi, uvicorn, transformers, torch, scipy, soundfile, uroman
print('  manim          ✓')
print('  pydub          ✓')
print('  fastapi        ✓')
print('  uvicorn        ✓')
print('  transformers   ✓')
print('  torch          ✓')
print('  scipy          ✓')
print('  soundfile      ✓')
print('  uroman         ✓')
"

echo ""
echo "========================================="
echo "  ALL DONE ✓"
echo ""
echo "  Next steps:"
echo "  1. Run the full stack:   ./run_all.sh"
echo "  2. Or start TTS only:    ./video_compiler/start_tts.sh --wait"
echo "========================================="
