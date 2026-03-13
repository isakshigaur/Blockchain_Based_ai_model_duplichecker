#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# start.sh — One-command launcher for the Blockchain AI Model
#             Ownership Portal (local development)
# ─────────────────────────────────────────────────────────────
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "  AI Model Ownership Portal — Local Launcher"
echo "  ─────────────────────────────────────────────"
echo ""

# 1. Start Ganache in background
echo "  [1/3] Starting Ganache CLI ..."
npx ganache-cli --chainId 1337 --port 8545 --deterministic > /dev/null 2>&1 &
GANACHE_PID=$!
sleep 3

# Check if ganache started
if ! kill -0 $GANACHE_PID 2>/dev/null; then
    echo "  ERROR: Ganache failed to start."
    exit 1
fi
echo "        Ganache running on port 8545 (PID $GANACHE_PID)"

# 2. Deploy contract
echo "  [2/3] Deploying smart contract ..."
python3 scripts/deploy.py 2>&1 | while IFS= read -r line; do
    echo "        $line"
done

# 3. Reset local index
echo '{}' > data/model_index.json

# 4. Launch Streamlit
echo "  [3/3] Launching Streamlit ..."
echo ""
echo "  ─────────────────────────────────────────────"
echo "  Portal will open at: http://localhost:8501"
echo "  Press Ctrl+C to stop everything"
echo "  ─────────────────────────────────────────────"
echo ""

# Trap exit to kill ganache
trap "echo ''; echo '  Shutting down...'; kill $GANACHE_PID 2>/dev/null; exit 0" INT TERM

streamlit run streamlit_app.py --server.headless true 2>&1 &
STREAMLIT_PID=$!

wait $STREAMLIT_PID
kill $GANACHE_PID 2>/dev/null
