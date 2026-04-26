#!/usr/bin/env bash
# run_all.sh — Start the complete STEM AI Studio stack
#
#  Service stack:
#    1. Meta MMS TTS Server       → http://127.0.0.1:8100
#    2. Agentic Orchestrator      → http://127.0.0.1:8200
#    3. Next.js Frontend          → http://localhost:3011
#
set -e
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
WEBAPP="$PROJECT_ROOT/web_app"
VENV=/tmp/stem_venv

echo "============================================"
echo "  STEM AI Studio — Full Stack Startup"
echo "============================================"

# ── Venv check ────────────────────────────────────────────────────────────
if [ ! -f "$VENV/bin/python3" ]; then
  echo "❌  /tmp/stem_venv not found."
  echo "    Run: ./rebuild_venv.sh"
  exit 1
fi

# ── 1. Start TTS Server ───────────────────────────────────────────────────
echo ""
bash "$PROJECT_ROOT/video_compiler/start_tts.sh" --wait

# ── 2. Start Orchestrator ─────────────────────────────────────────────────
echo ""
bash "$PROJECT_ROOT/agent_core/start_orchestrator.sh" --wait

# ── 3. Install web app node deps if needed ────────────────────────────────
if [ ! -d "$WEBAPP/node_modules" ]; then
  echo ""
  echo "Installing Next.js dependencies…"
  cd "$WEBAPP" && npm install && cd "$PROJECT_ROOT"
fi

# ── 4. Start Next.js ──────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "  🚀 Starting Next.js on http://localhost:3011"
echo "  🎙  TTS Server:      http://localhost:8102"
echo "  🤖  Orchestrator:    http://localhost:8205"
echo "============================================"
echo ""
cd "$WEBAPP"
exec node ./node_modules/next/dist/bin/next dev -p 3012
