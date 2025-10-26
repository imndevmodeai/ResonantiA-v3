#!/bin/bash
#
# Master Startup Script for the Visual Cognitive Debugger (VCD)
#
# This script automates the setup and launch of all components required
# for the live ArchE VCD environment.

echo "🚀 Starting Visual Cognitive Debugger Environment..."

# --- Configuration ---
PROJECT_ROOT=$(pwd)
VENV_PATH="$PROJECT_ROOT/arche_env"
BRIDGE_LOG="vcd_bridge.log"
FRONTEND_LOG="nextjs_chat.log"

# --- Functions ---

# Function to kill processes on a given port
kill_on_port() {
    PORT=$1
    PID=$(lsof -t -i:$PORT)
    if [ -n "$PID" ]; then
        echo "🔪 Killing process on port $PORT (PID: $PID)..."
        kill -9 $PID
    fi
}

# --- Main Execution ---

# 1. Stop any previously running services
echo "[1/4] Stopping any lingering services..."
kill_on_port 8765 # VCD Bridge WebSocket
kill_on_port 3000 # Next.js Frontend
pkill -f "vcd_bridge.py"
pkill -f "next dev"
sleep 1

# 2. Set up Python environment
echo "[2/4] Setting up Python environment..."
export PYTHONPATH="$PROJECT_ROOT/Three_PointO_ArchE:$PROJECT_ROOT/Four_PointO_ArchE"
echo "  - PYTHONPATH set."

if [ ! -d "$VENV_PATH" ]; then
    echo "  - Virtual environment not found. Please run 'python3 -m venv arche_env' and 'source arche_env/bin/activate && pip install -r requirements.txt' first."
    exit 1
fi

source "$VENV_PATH/bin/activate"
echo "  - Virtual environment activated."

# 3. Start the VCD Bridge (Backend)
echo "[3/4] Starting VCD Bridge (Backend)..."
nohup python3 vcd_bridge.py > "$BRIDGE_LOG" 2>&1 &
BRIDGE_PID=$!
sleep 3 # Give the server a moment to start

if ps -p $BRIDGE_PID > /dev/null; then
    echo "  - ✅ VCD Bridge started successfully (PID: $BRIDGE_PID)."
    echo "  - Logs are being written to: $BRIDGE_LOG"
else
    echo "  - ❌ VCD Bridge failed to start. Check logs for details:"
    cat "$BRIDGE_LOG"
    exit 1
fi

# 4. Start the VCD Frontend
echo "[4/4] Starting VCD Frontend (Next.js)..."
cd "$PROJECT_ROOT/nextjs-chat"
nohup npm run dev > "$PROJECT_ROOT/$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"
sleep 5 # Give Next.js time to compile

if ps -p $FRONTEND_PID > /dev/null; then
    echo "  - ✅ VCD Frontend started successfully (PID: $FRONTEND_PID)."
    echo "  - Logs are being written to: $FRONTEND_LOG"
else
    echo "  - ❌ VCD Frontend failed to start. Check logs for details:"
    cat "$FRONTEND_LOG"
    exit 1
fi

echo ""
echo "🎉 All services are running."
echo "   - VCD Frontend available at: http://localhost:3000"
echo "   - VCD Bridge WebSocket listening on: ws://localhost:8765"
echo ""
echo "To stop all services, run: ./stop_vcd.sh (or pkill -f vcd_bridge.py && pkill -f 'next dev')"
