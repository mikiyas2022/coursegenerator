#!/usr/bin/env bash
# run_all.sh — Start the STEM Video Factory (MMS TTS server + Next.js frontend)
set -e
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
WEBAPP="$PROJECT_ROOT/web_app"
VENV=/tmp/stem_venv

echo "======================================"
echo "  STEM Video Factory - Local Stack"
echo "======================================"

# ── Check venv ────────────────────────────────────────────────────────────────
if [ ! -f "$VENV/bin/python3" ]; then
  echo ""
  echo "⚠  /tmp/stem_venv not found. Run rebuild_venv.sh first:"
  echo "   ./rebuild_venv.sh"
  echo ""
  exit 1
fi

# ── Check Manim ───────────────────────────────────────────────────────────────
if ! "$VENV/bin/manim" --version > /dev/null 2>&1; then
  echo ""
  echo "⚠  Manim not found in venv. Run rebuild_venv.sh."
  echo ""
fi

# ── Start MMS TTS server (background, wait for readiness) ─────────────────────
echo ""
echo "Starting Amharic MMS TTS server …"
bash "$PROJECT_ROOT/video_compiler/start_tts.sh" --wait

# ── Install web app node deps if needed ───────────────────────────────────────
if [ ! -d "$WEBAPP/node_modules" ]; then
  echo "Installing Next.js dependencies …"
  cd "$WEBAPP" && npm install && cd "$PROJECT_ROOT"
fi

# ── Start Next.js dev server ──────────────────────────────────────────────────
echo ""
echo "Starting Next.js frontend on http://localhost:3011 …"
echo "TTS server running on  http://localhost:8100"
echo ""
cd "$WEBAPP"
exec node ./node_modules/next/dist/bin/next dev -p 3011
