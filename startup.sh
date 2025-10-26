#!/bin/bash
#
# startup.sh
# A graceful startup script for the ArchE Visual Cognitive Debugger (VCD).
# Ensures a clean state by first shutting down any existing VCD processes.
#

echo "Initiating ArchE Visual Cognitive Debugger startup sequence..."

# Step 1: Execute the shutdown script to ensure a clean slate.
echo "--> Running shutdown protocol to terminate old instances..."
./stop_vcd.sh
echo "--> Shutdown complete."

# Step 2: Start the real ArchE-Nexus Bridge server.
echo "--> Starting ArchE-Nexus Bridge server on port 8765..."
python3 arche_nexus_bridge.py > logs/arche_bridge.log 2>&1 &
WEBSOCKET_PID=$!
echo "    ArchE-Nexus Bridge started with PID: $WEBSOCKET_PID"

# Give the server a moment to initialize
sleep 2

# Step 3: Start the Next.js frontend server in the background.
echo "--> Starting ArchE VCD frontend on port 3000 (or 3001 if 3000 is in use)..."
cd nextjs-chat
npm run dev > ../logs/nextjs_dev.log 2>&1 &
FRONTEND_PID=$!
echo "    Next.js frontend started with PID: $FRONTEND_PID"
cd ..

echo ""
echo "Waiting for ArchE VCD services to initialize..."
sleep 5 # Add a 5-second delay to allow services to fully start

echo "ArchE VCD startup sequence complete."
echo "✅ The ArchE Visual Cognitive Debugger is now online at http://localhost:3000"
echo "   (or http://localhost:3001 if port 3000 was in use)"
echo ""
echo "WebSocket server is running on ws://localhost:8765"
echo ""
echo "To stop all services, run: ./stop_vcd.sh"
