#!/bin/bash

# ArchE System Shutdown Script
# Stops all three servers gracefully

echo "🛑 Stopping ArchE System - All Three Servers"
echo "============================================="

echo "🧹 Stopping Python Mastermind Server..."
pkill -f "mastermind_server.py" || true

echo "🧹 Stopping WebSocket Bridge Server..."
pkill -f "webSocketServer" || true

echo "🧹 Stopping Next.js VCD Frontend..."
pkill -f "next dev" || true

sleep 2

echo ""
echo "✅ All servers stopped successfully!"
echo ""
echo "📊 Server Status:"
echo "   🐍 Python Mastermind Server: STOPPED"
echo "   🌐 WebSocket Bridge Server:  STOPPED"
echo "   🎨 VCD Frontend:             STOPPED"
