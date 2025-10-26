#!/bin/bash

# ArchE System Log Viewer
# Shows logs from all three servers

echo "📋 ArchE System Logs"
echo "===================="

echo ""
echo "🐍 Python Mastermind Server Logs:"
echo "---------------------------------"
if [ -f "Three_PointO_ArchE/logs/arche_v3_default.log" ]; then
    tail -n 20 Three_PointO_ArchE/logs/arche_v3_default.log
else
    echo "   No log file found"
fi

echo ""
echo "🌐 WebSocket Bridge Server Logs:"
echo "--------------------------------"
if [ -f "logs/websocket_*.log" ]; then
    tail -n 20 logs/websocket_*.log
else
    echo "   No log file found"
fi

echo ""
echo "🎨 Next.js VCD Frontend Logs:"
echo "-----------------------------"
echo "   Check terminal where Next.js is running for logs"
