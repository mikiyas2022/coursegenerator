#!/usr/bin/env bash
# run_all.sh — Start the complete STEM AI Studio 3B1B stack
#
#  Services:
#    1. Meta MMS TTS Server    → http://127.0.0.1:8102
#    2. Agentic Orchestrator   → http://127.0.0.1:8205  (v3.0.0)
#    3. Next.js Web UI         → http://localhost:3000
#
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
WEBAPP="$PROJECT_ROOT/web_app"
VENV=/tmp/stem_venv
LOGDIR="$PROJECT_ROOT/logs"
mkdir -p "$LOGDIR"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        STEM AI Studio 3B1B — Full Stack Startup             ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# ── Venv check ────────────────────────────────────────────────────────────────
if [ ! -f "$VENV/bin/python3" ]; then
  echo "❌  /tmp/stem_venv not found. Run: ./rebuild_venv.sh"
  exit 1
fi

# ── Kill any stale instances ──────────────────────────────────────────────────
echo ""
echo "🧹 Cleaning up stale processes..."
pkill -f "orchestrator.py" 2>/dev/null && echo "  Killed stale orchestrators" || true
pkill -f "next dev"        2>/dev/null && echo "  Killed stale Next.js"        || true
sleep 1

# ── 1. TTS Server ─────────────────────────────────────────────────────────────
echo ""
echo "🎙  Starting TTS Server..."
if curl -sf http://127.0.0.1:8102/health >/dev/null 2>&1; then
  echo "  TTS already running ✓"
else
  bash "$PROJECT_ROOT/video_compiler/start_tts.sh" --wait
fi

# ── 2. Orchestrator ───────────────────────────────────────────────────────────
echo ""
echo "🤖 Starting Orchestrator v3.0.0..."
cd "$PROJECT_ROOT/agent_core"
nohup "$VENV/bin/python3" orchestrator.py > "$LOGDIR/orchestrator.log" 2>&1 &
ORCH_PID=$!
echo "  PID $ORCH_PID — waiting for startup..."
for i in $(seq 1 15); do
  sleep 1
  if curl -sf http://127.0.0.1:8205/health >/dev/null 2>&1; then
    echo "  Orchestrator UP ✓"
    break
  fi
  echo "  Waiting... ($i)"
done
cd "$PROJECT_ROOT"

# ── 3. Next.js Web App ────────────────────────────────────────────────────────
echo ""
echo "🌐 Starting Next.js on http://localhost:3000..."
if [ ! -d "$WEBAPP/node_modules" ]; then
  echo "  Installing npm deps..."
  cd "$WEBAPP" && npm install && cd "$PROJECT_ROOT"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ⚡ 3B1B Mode Ready!                                        ║"
echo "║  🌐  Web UI:        http://localhost:3000                   ║"
echo "║  🤖  Orchestrator:  http://localhost:8205                   ║"
echo "║  🎙   TTS Server:   http://localhost:8102                   ║"
echo "║  📝  Log:           logs/pipeline.log                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd "$WEBAPP"
exec node ./node_modules/next/dist/bin/next dev -p 3000
