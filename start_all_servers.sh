#!/bin/bash

# ArchE System Startup Script
# Starts all three servers in the correct order for full system operation

echo "🚀 Starting ArchE System - All Three Servers"
echo "=============================================="

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "mastermind_server.py" || true
pkill -f "webSocketServer" || true
pkill -f "next dev" || true
sleep 3

# Set environment variables
export ARCHE_PORT=3005
export WEBSOCKET_PORT=3006

echo ""
echo "1️⃣ Starting Python Mastermind Server (Port 3005)..."
cd Three_PointO_ArchE
python3 mastermind_server.py &
MASTERMIND_PID=$!
echo "   Mastermind Server PID: $MASTERMIND_PID"
sleep 5

echo ""
echo "2️⃣ Starting WebSocket Bridge Server (Port 3006)..."
cd ..
node webSocketServer.js &
WEBSOCKET_PID=$!
echo "   WebSocket Server PID: $WEBSOCKET_PID"
sleep 3

echo ""
echo "3️⃣ Starting Next.js VCD Frontend (Port 3000)..."
cd nextjs-chat
npm run dev &
NEXTJS_PID=$!
echo "   Next.js Server PID: $NEXTJS_PID"
sleep 5

echo ""
echo "✅ All servers started successfully!"
echo ""
echo "📊 Server Status:"
echo "   🐍 Python Mastermind Server: http://localhost:3005 (WebSocket)"
echo "   🌐 WebSocket Bridge Server:  ws://localhost:3006"
echo "   🎨 VCD Frontend:             http://localhost:3000"
echo ""
echo "🔗 Connection Flow:"
echo "   VCD (3000) → WebSocket Bridge (3006) → Python Backend (3005)"
echo ""
echo "📝 To stop all servers, run: ./stop_all_servers.sh"
echo "📝 To view logs, run: ./view_logs.sh"
echo ""
echo "🎯 Ready to use! Open http://localhost:3000 in your browser"
