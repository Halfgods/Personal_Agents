#!/usr/bin/env bash
set -e

echo "=== Personal AI Agent System Setup ==="
echo ""

# Use existing venv or create one
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing backend dependencies..."
pip install -e . fastapi uvicorn pydantic 2>/dev/null || python -m pip install -e . fastapi uvicorn pydantic

echo "Installing frontend dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    npm install
    cd ..
else
    echo "Frontend directory not found. Skipping frontend setup."
fi

echo ""
echo "=== Checking LLM backend ==="

# Check for Ollama
if command -v ollama &>/dev/null; then
    echo "[OK] Ollama is installed!"
    if ! ollama list 2>/dev/null | tail -n +2 | grep -q .; then
        echo "  No models found. Pulling a lightweight model..."
        echo "  (This downloads ~2GB, may take a while)"
        ollama pull llama3.2:3b || ollama pull phi:2.7b || ollama pull gemma:2b
    fi
else
    echo "[!] Ollama not found."
    echo "  Install it from: https://ollama.com"
    echo "  Then run: ollama pull llama3.2:3b"
    echo ""
    echo "  Alternatively, install Hugging Face support:"
    echo "  pip install transformers torch"
fi

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Start the interactive web app:"
echo "  ./run_web.sh"
echo ""
echo "Or run the CLI version:"
echo "  source .venv/bin/activate"
echo "  agents"
echo ""
echo "Or try demo mode (no LLM needed):"
echo "  python -m personal_agents.demo"
