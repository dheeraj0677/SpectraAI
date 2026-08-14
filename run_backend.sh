#!/usr/bin/env bash
set -e

echo ""
echo "============================================================"
echo "  SpectraAI - Multimodal Product Intelligence Engine"
echo "  Starting Backend Server (FastAPI on http://localhost:8000)"
echo "============================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Auto-activate .venv if present
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment (.venv)..."
    source .venv/bin/activate
fi

if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python was not found on your PATH."
    echo "Please install Python 3.12+ (https://www.python.org/downloads/)"
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

if command -v uv &> /dev/null; then
    echo "Installing / verifying backend dependencies via uv..."
    uv pip install -r backend/requirements.txt --quiet
else
    echo "Installing / verifying backend dependencies via pip..."
    $PYTHON_CMD -m pip install -r backend/requirements.txt --quiet
fi

cd "$SCRIPT_DIR/backend"
echo "Starting FastAPI server..."
$PYTHON_CMD main.py
