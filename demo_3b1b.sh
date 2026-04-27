#!/usr/bin/env bash
# demo_3b1b.sh — One-command 3B1B-style demo video
# 
# Usage:
#   ./demo_3b1b.sh
#   ./demo_3b1b.sh "The Pythagorean Theorem"
#   ./demo_3b1b.sh "Why does gravity feel like acceleration?" landscape 2
#
# Args: [topic] [orientation=landscape] [persona_id=1]

set -euo pipefail

TOPIC="${1:-Why does gravity feel like acceleration?}"
ORIENTATION="${2:-landscape}"
PERSONA_ID="${3:-1}"
ORCH_URL="http://localhost:8205"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          STEM AI Studio — 3B1B Mode Demo                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  Topic       : $TOPIC"
echo "  Orientation : $ORIENTATION"
echo "  Persona     : $PERSONA_ID"
echo ""

# Check orchestrator is running
if ! curl -sf "$ORCH_URL/health" > /dev/null 2>&1; then
  echo "❌ Orchestrator not running at $ORCH_URL"
  echo "   Start it with: ./run_all.sh  or  cd agent_core && python orchestrator.py"
  exit 1
fi

echo "✅ Orchestrator online"
echo "🚀 Starting full automated 3B1B pipeline..."
echo ""

# Stream the full pipeline
curl -sN -X POST "$ORCH_URL/generate_full" \
  -H "Content-Type: application/json" \
  -d "{
    \"topic\": \"$TOPIC\",
    \"audience\": \"High School (Grade 7–12)\",
    \"style\": \"World-Class 3b1b (Deep Visual Insight)\",
    \"persona_id\": $PERSONA_ID,
    \"orientation\": \"$ORIENTATION\",
    \"run_postprod\": true
  }" | while IFS= read -r line; do
    if [[ "$line" == data:* ]]; then
      payload="${line#data: }"
      msg=$(echo "$payload" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    t = d.get('type','')
    p = d.get('payload', {})
    m = p.get('message', t)
    if t not in ('ping',):
        print(f'[{t:20s}] {m}')
except:
    pass
" 2>/dev/null || true)
      if [[ -n "$msg" ]]; then
        echo "$msg"
      fi
    fi
  done

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Check Local_Video_Output/ for your 3B1B masterpiece!      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
