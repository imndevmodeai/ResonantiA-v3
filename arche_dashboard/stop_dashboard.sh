#!/bin/bash
#
# Stop ArchE Dashboard Script
# ===========================
# Stops all dashboard processes (backend and frontend)
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🛑 Stopping ArchE Dashboard..."

# Stop by PID files if they exist
if [ -f "$SCRIPT_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$SCRIPT_DIR/backend.pid")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null && echo "✅ Backend stopped (PID: $BACKEND_PID)"
    fi
    rm -f "$SCRIPT_DIR/backend.pid"
fi

if [ -f "$SCRIPT_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/frontend.pid")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null && echo "✅ Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm -f "$SCRIPT_DIR/frontend.pid"
fi

# Kill any remaining processes
pkill -f "python3.*api.py" 2>/dev/null && echo "✅ Additional backend processes killed"
pkill -f "uvicorn.*api" 2>/dev/null && echo "✅ Additional uvicorn processes killed"
pkill -f "python3 -m http.server" 2>/dev/null && echo "✅ Additional frontend servers killed"

echo "✅ Dashboard stopped"

