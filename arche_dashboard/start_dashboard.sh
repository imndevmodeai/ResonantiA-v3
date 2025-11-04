#!/bin/bash
#
# ArchE Dashboard Startup Script
# ================================
# Starts both backend API and frontend server
#
# ResonantiA Protocol v3.5-GP
#

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║                  ⚡ ArchE DASHBOARD STARTUP ⚡                      ║"
echo "║                  ResonantiA Protocol v3.5-GP                         ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "📂 Project Root: $PROJECT_ROOT"
echo "📂 Dashboard Root: $SCRIPT_DIR"
echo ""

# Check if arche_env exists
if [ ! -d "$PROJECT_ROOT/arche_env" ]; then
    echo "❌ Error: arche_env virtual environment not found!"
    echo "   Expected location: $PROJECT_ROOT/arche_env"
    echo ""
    echo "   Please create it first:"
    echo "   cd $PROJECT_ROOT"
    echo "   python3 -m venv arche_env"
    echo "   source arche_env/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating arche_env..."
source "$PROJECT_ROOT/arche_env/bin/activate"

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"
echo ""

# Check if required packages are installed
echo "🔍 Checking required packages..."

REQUIRED_PACKAGES=("fastapi" "uvicorn" "websockets")
MISSING_PACKAGES=()

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "📦 Installing missing packages: ${MISSING_PACKAGES[*]}"
    pip install "${MISSING_PACKAGES[@]}"
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install required packages"
        echo "   Try manually: pip install fastapi uvicorn websockets python-multipart aiofiles"
        exit 1
    fi
    echo "✅ Packages installed successfully"
else
    echo "✅ All required packages found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Starting Backend API Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   📍 Backend API:  http://localhost:8000"
echo "   📚 API Docs:     http://localhost:8000/docs"
echo "   🔌 WebSocket:    ws://localhost:8000/ws/live"
echo "   🎯 Frontend:     $SCRIPT_DIR/frontend/index.html"
echo ""
echo "   💡 Open frontend/index.html in your browser to access the dashboard"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Change to backend directory
cd "$SCRIPT_DIR/backend"

# Start backend API
python3 api.py

# Cleanup on exit
echo ""
echo "🛑 Dashboard shutting down..."
echo "✅ Goodbye!"

