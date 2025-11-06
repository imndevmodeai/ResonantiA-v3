#!/bin/bash
# FaceCheck Flask App + Telegram Bot Startup Script
# Runs the Flask application with FaceCheck.ID integration and optional Telegram bot

echo "🎭 Starting FaceCheck Service..."
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check for required files
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory"
    echo "Please run this script from the directory containing app.py"
    exit 1
fi

# Determine mode from environment or argument
MODE="${1:-both}"
if [ "$1" = "bot" ] || [ "$1" = "web" ] || [ "$1" = "both" ]; then
    MODE="$1"
fi

# Check if .env file exists
if [ -f ".env" ]; then
    echo "📝 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Install dependencies if needed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Installing dependencies..."
    pip3 install -r facecheck_requirements.txt 2>/dev/null || pip3 install flask requests python-telegram-bot python-dotenv
fi

# Set environment variables
export FLASK_APP=app.py
export FACECHECK_MODE="$MODE"

# Development vs Production
if [ "$MODE" = "production" ] || [ -n "$PORT" ]; then
    export FLASK_ENV=production
    export FLASK_DEBUG=0
else
    export FLASK_ENV=development
    export FLASK_DEBUG=1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check Telegram bot token
if [ -z "$FACECHECK_BOT_TOKEN" ]; then
    echo "⚠️  Warning: FACECHECK_BOT_TOKEN not set. Bot functionality will be disabled."
    if [ "$MODE" = "bot" ]; then
        echo "❌ Cannot run in bot-only mode without token"
        exit 1
    fi
    MODE="web"
fi

# Display startup information
echo ""
echo "🚀 Starting FaceCheck Service..."
echo "📋 Mode: $MODE"
echo ""

if [ "$MODE" = "bot" ] || [ "$MODE" = "both" ]; then
    if [ -n "$FACECHECK_BOT_TOKEN" ]; then
        echo "🤖 Telegram Bot: ENABLED"
    else
        echo "🤖 Telegram Bot: DISABLED (no token)"
    fi
fi

if [ "$MODE" = "web" ] || [ "$MODE" = "both" ]; then
    PORT="${PORT:-5000}"
    echo "🌐 Web Interface: http://localhost:$PORT"
    echo "🔍 FaceCheck.ID integration: Active"
fi

echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Run the appropriate service
if [ "$MODE" = "bot" ]; then
    # Bot-only mode
    python3 facecheck_bot.py
elif [ "$MODE" = "web" ]; then
    # Web-only mode (original Flask app)
    python3 app.py
else
    # Both bot and web (using facecheck_bot.py which handles both)
    python3 facecheck_bot.py
fi





