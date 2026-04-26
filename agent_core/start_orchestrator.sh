#!/usr/bin/env bash
# agent_core/start_orchestrator.sh — Launch the Agentic Orchestrator
# Usage: ./agent_core/start_orchestrator.sh [--wait]
set -e

VENV=/tmp/stem_venv
ORCH_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8205
HEALTH_URL="http://127.0.0.1:${PORT}/health"
LOG=/tmp/stem_orchestrator.log

if [ ! -f "$VENV/bin/python3" ]; then
  echo "❌  /tmp/stem_venv not found. Run rebuild_venv.sh first."
  exit 1
fi

if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
  echo "✅  Orchestrator already running on port $PORT."
  exit 0
fi

echo "🤖  Starting Agentic Orchestrator on port $PORT …"
echo "    Log: $LOG"

cd "$ORCH_DIR"
"$VENV/bin/python3" orchestrator.py >> "$LOG" 2>&1 &
echo "    PID: $!"

if [[ "${1:-}" == "--wait" ]]; then
  echo -n "    Waiting for orchestrator "
  for i in $(seq 1 30); do
    sleep 1
    echo -n "."
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
      echo " ready! (${i}s)"
      exit 0
    fi
  done
  echo ""
  echo "❌  Orchestrator did not become ready. Check $LOG"
  exit 1
fi
