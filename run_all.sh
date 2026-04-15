#!/usr/bin/env bash
# run_all.sh — Start the STEM Video Factory (Manim + Piper TTS)
# Does NOT start a TTS microservice — execution is handled directly in the API route.

set -e
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
WEBAPP="$PROJECT_ROOT/web_app"

echo "======================================"
echo "  STEM Video Factory - Local Server"
echo "======================================"

# Check for manim
if ! command -v manim &>/dev/null && ! python3 -m manim --version &>/dev/null 2>&1; then
  echo ""
  echo "⚠  Manim not found. Run setup first:"
  echo "   pip3 install --break-system-packages manim"
  echo ""
fi

# Install web app node deps if needed
if [ ! -d "$WEBAPP/node_modules" ]; then
  echo "Installing Next.js dependencies..."
  cd "$WEBAPP" && npm install && cd "$PROJECT_ROOT"
fi

echo "Starting Next.js development server on http://localhost:3011..."
cd "$WEBAPP"
exec node ./node_modules/next/dist/bin/next dev -p 3011
