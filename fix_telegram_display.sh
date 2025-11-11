#!/bin/bash
# Fix Telegram Desktop display issues

echo "🔧 Fixing Telegram Desktop Display Issues"
echo "=========================================="

# Check if Telegram is running
if pgrep -f "Telegram" > /dev/null; then
    echo "⚠️  Telegram is already running"
    read -p "Kill existing Telegram process and restart? (y/n): " restart
    if [ "$restart" = "y" ]; then
        pkill -f Telegram
        sleep 2
    else
        echo "Keeping existing process. Try accessing it in your GUI."
        exit 0
    fi
fi

# Set display
export DISPLAY=:0
export XDG_SESSION_TYPE=x11

# Install Qt dependencies if missing
echo "📦 Checking Qt dependencies..."
if ! dpkg -l | grep -q libqt5gui5; then
    echo "Installing Qt5 GUI libraries..."
    sudo apt install -y libqt5gui5 libqt5core5a libqt5dbus5 libqt5widgets5
fi

# Try to launch with proper environment
echo "🚀 Launching Telegram Desktop..."
echo "DISPLAY=$DISPLAY"
echo ""

# Launch in background
~/Downloads/Telegram/Telegram > /tmp/telegram.log 2>&1 &

sleep 3

# Check if it started
if pgrep -f Telegram > /dev/null; then
    echo "✅ Telegram Desktop started!"
    echo "Check your desktop/window manager for the Telegram window"
    echo ""
    echo "If you don't see it, check logs:"
    echo "  tail -f /tmp/telegram.log"
else
    echo "❌ Failed to start. Check logs:"
    echo "  cat /tmp/telegram.log"
    echo ""
    echo "💡 Alternative: Use Telegram Web instead!"
    echo "   Run: ./get_bot_token_web.sh"
fi



