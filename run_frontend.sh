#!/usr/bin/env bash
set -e

echo ""
echo "============================================================"
echo "  SpectraAI - Multimodal Product Intelligence Engine"
echo "  Starting Frontend Dashboard (Vite on http://localhost:5173)"
echo "============================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/frontend"

if ! command -v npm &> /dev/null; then
    echo "[ERROR] npm / Node.js was not found on your PATH."
    echo "Please install Node.js 18+ (https://nodejs.org/)"
    exit 1
fi

echo "Installing / verifying frontend dependencies..."
npm install --silent

echo "Starting Vite development server..."
npm run dev
