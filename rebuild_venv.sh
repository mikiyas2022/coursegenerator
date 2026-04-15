#!/usr/bin/env bash
set -e

VENV=/tmp/stem_venv

echo "=== Rebuilding /tmp/stem_venv from scratch ==="

# Remove corrupted venv entirely
rm -rf "$VENV"

# Create fresh venv with Homebrew Python 3.13
/opt/homebrew/bin/python3.13 -m venv "$VENV"

echo "=== Installing core packages ==="
"$VENV/bin/pip" install --upgrade pip --quiet
"$VENV/bin/pip" install manim manim-voiceover edge-tts pydub torch transformers scipy soundfile uroman --quiet

echo ""
echo "=== Validating install ==="
"$VENV/bin/python3" -c "from manim import *; from manim_voiceover import VoiceoverScene; print('ALL OK')"
echo "=== DONE ==="
