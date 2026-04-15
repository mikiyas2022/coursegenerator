#!/usr/bin/env bash
# start_tts.sh — Launch the Amharic MMS TTS server
# Usage: ./video_compiler/start_tts.sh [--wait]
#   --wait  Block until the server passes its health check (useful in run_all.sh)
set -e

VENV=/tmp/stem_venv
SERVER_DIR="$(cd "$(dirname "$0")" && pwd)"
TTS_PORT=8100
HEALTH_URL="http://127.0.0.1:${TTS_PORT}/health"
LOG_FILE="/tmp/stem_tts.log"

# ── Check that the venv exists ────────────────────────────────────────────────
if [ ! -f "$VENV/bin/python3" ]; then
  echo "❌  /tmp/stem_venv not found. Run rebuild_venv.sh first."
  exit 1
fi

# ── Check if already running ──────────────────────────────────────────────────
if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
  echo "✅  TTS server already running on port $TTS_PORT."
  exit 0
fi

echo "🚀  Starting Amharic MMS TTS server on port $TTS_PORT …"
echo "    Log: $LOG_FILE"

# Launch in background, cd into video_compiler so relative imports work
cd "$SERVER_DIR"
"$VENV/bin/python3" tts_server.py >> "$LOG_FILE" 2>&1 &
TTS_PID=$!
echo "    PID: $TTS_PID"

# ── Optionally wait for readiness ─────────────────────────────────────────────
if [[ "${1:-}" == "--wait" ]]; then
  echo -n "    Waiting for model to load "
  MAX_WAIT=120   # MMS model may take a while on first run (download)
  ELAPSED=0
  while ! curl -sf "$HEALTH_URL" | grep -q '"engine_ready": true' 2>/dev/null; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    echo -n "."
    if [ $ELAPSED -ge $MAX_WAIT ]; then
      echo ""
      echo "❌  TTS server did not become ready within ${MAX_WAIT}s."
      echo "    Check $LOG_FILE for errors."
      exit 1
    fi
  done
  echo ""
  echo "✅  TTS server ready! (${ELAPSED}s)"
fi
