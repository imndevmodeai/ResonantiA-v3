#!/bin/bash
#
# stop_vcd.sh
# A robust script to find and terminate all running VCD processes.
#

echo "Shutting down ArchE Visual Cognitive Debugger services..."

# Find and kill processes by port first (more reliable)
echo "--> Searching for processes using port 8765 (WebSocket server)..."
PID_8765=$(lsof -ti :8765)
if [ ! -z "$PID_8765" ]; then
    echo "    Terminating process $PID_8765 on port 8765..."
    kill $PID_8765
    echo "    Process $PID_8765 terminated."
else
    echo "    No process found on port 8765."
fi

echo "--> Searching for processes using port 3000 (Next.js)..."
PID_3000=$(lsof -ti :3000)
if [ ! -z "$PID_3000" ]; then
    echo "    Terminating process $PID_3000 on port 3000..."
    kill $PID_3000
    echo "    Process $PID_3000 terminated."
else
    echo "    No process found on port 3000."
fi

echo "--> Searching for processes using port 3001 (Next.js fallback)..."
PID_3001=$(lsof -ti :3001)
if [ ! -z "$PID_3001" ]; then
    echo "    Terminating process $PID_3001 on port 3001..."
    kill $PID_3001
    echo "    Process $PID_3001 terminated."
else
    echo "    No process found on port 3001."
fi

# Also kill by process name as backup
echo "--> Searching for WebSocket server processes..."
pkill -f "arche_nexus_bridge.py"
if [ $? -eq 0 ]; then
    echo "    ArchE-Nexus Bridge process terminated."
else
    pkill -f "nexus_websocket_server.py"
    if [ $? -eq 0 ]; then
        echo "    WebSocket server process terminated."
    else
        echo "    No running WebSocket server found."
    fi
fi

echo "--> Searching for Next.js processes..."
pkill -f "next dev"
if [ $? -eq 0 ]; then
    echo "    Next.js frontend process terminated."
else
    echo "    No running Next.js frontend found."
fi

echo "ArchE VCD shutdown complete."
