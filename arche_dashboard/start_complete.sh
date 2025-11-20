#!/bin/bash
#
# Complete ArchE Dashboard Startup Script
# ========================================
# Kills existing instances, starts backend and frontend, opens browser
#
# ResonantiA Protocol v3.5-GP
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                      ║${NC}"
echo -e "${BLUE}║            ⚡ ArchE DASHBOARD - COMPLETE STARTUP ⚡                 ║${NC}"
echo -e "${BLUE}║            ResonantiA Protocol v3.5-GP                              ║${NC}"
echo -e "${BLUE}║                                                                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo -e "${GREEN}📂 Project Root:${NC} $PROJECT_ROOT"
echo -e "${GREEN}📂 Dashboard Root:${NC} $SCRIPT_DIR"
echo ""

# ============================================================================
# STEP 1: KILL EXISTING INSTANCES
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🛑 Step 1: Cleaning up existing instances...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Kill backend processes (api.py runs uvicorn internally)
echo -e "${BLUE}   Killing backend processes...${NC}"
pkill -f "python3.*api.py" 2>/dev/null && echo -e "${GREEN}   ✅ Backend processes killed${NC}" || echo -e "${YELLOW}   ⚠️  No backend processes found${NC}"
# Note: uvicorn runs inside python3 api.py, not as separate process
pkill -f "uvicorn.*api" 2>/dev/null && echo -e "${GREEN}   ✅ Additional uvicorn processes killed${NC}" || true

# Kill frontend HTTP servers (python3 -m http.server on common ports)
echo -e "${BLUE}   Killing frontend HTTP servers...${NC}"
for port in 3000 8080 8081 8000 5000; do
    pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$pid" ]; then
        kill -9 $pid 2>/dev/null && echo -e "${GREEN}   ✅ Killed process on port $port${NC}" || true
    fi
done

# Wait a moment for processes to fully terminate
sleep 2

echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

# ============================================================================
# STEP 2: CHECK PREREQUISITES
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔍 Step 2: Checking prerequisites...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check virtual environment
if [ ! -d "$PROJECT_ROOT/arche_env" ]; then
    echo -e "${RED}❌ Error: arche_env virtual environment not found!${NC}"
    echo "   Expected location: $PROJECT_ROOT/arche_env"
    echo ""
    echo "   Please create it first:"
    echo "   cd $PROJECT_ROOT"
    echo "   python3 -m venv arche_env"
    echo "   source arche_env/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi
echo -e "${GREEN}✅ Virtual environment found${NC}"

# Activate virtual environment
echo -e "${BLUE}   Activating arche_env...${NC}"
source "$PROJECT_ROOT/arche_env/bin/activate" || {
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
}
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Check required packages
REQUIRED_PACKAGES=("fastapi" "uvicorn" "websockets")
MISSING_PACKAGES=()

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}📦 Installing missing packages: ${MISSING_PACKAGES[*]}${NC}"
    pip install "${MISSING_PACKAGES[@]}" || {
        echo -e "${RED}❌ Failed to install required packages${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ Packages installed${NC}"
else
    echo -e "${GREEN}✅ All required packages found${NC}"
fi

echo ""

# ============================================================================
# STEP 3: START BACKEND
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🚀 Step 3: Starting Backend API Server...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$BACKEND_DIR"

# Start backend in background
echo -e "${BLUE}   Starting backend on port 8000 (or next available)...${NC}"
nohup python3 api.py > "$SCRIPT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$SCRIPT_DIR/backend.pid"

# Wait for backend to start (with progress indicator)
echo -e "${BLUE}   Waiting for backend to initialize (this may take 10-30 seconds)...${NC}"
for i in {1..45}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is running (PID: $BACKEND_PID)${NC}"
        break
    fi
    # Show progress every 5 seconds
    if [ $((i % 5)) -eq 0 ]; then
        echo -e "${BLUE}   Still initializing... (${i}s elapsed)${NC}"
    fi
    if [ $i -eq 45 ]; then
        echo -e "${RED}❌ Backend failed to start after 45 seconds${NC}"
        echo "   Check logs: $SCRIPT_DIR/backend.log"
        echo "   Last 20 lines of log:"
        tail -20 "$SCRIPT_DIR/backend.log" 2>/dev/null || echo "   (log file not found)"
        exit 1
    fi
    sleep 1
done

# Get actual backend port (in case it's not 8000)
BACKEND_PORT=$(lsof -ti:8000 > /dev/null 2>&1 && echo "8000" || \
    (grep -oP 'port=\K[0-9]+' "$SCRIPT_DIR/backend.log" 2>/dev/null | head -1 || echo "8000"))

echo -e "${GREEN}   Backend API: http://localhost:$BACKEND_PORT${NC}"
echo -e "${GREEN}   API Docs: http://localhost:$BACKEND_PORT/docs${NC}"
echo ""

# ============================================================================
# STEP 4: START FRONTEND
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🌐 Step 4: Starting Frontend HTTP Server...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$FRONTEND_DIR"

# Find available port for frontend
FRONTEND_PORT=3000
for port in 3000 8080 8081 5000; do
    if ! lsof -ti:$port > /dev/null 2>&1; then
        FRONTEND_PORT=$port
        break
    fi
done

echo -e "${BLUE}   Starting frontend server on port $FRONTEND_PORT...${NC}"
nohup python3 -m http.server $FRONTEND_PORT > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$SCRIPT_DIR/frontend.pid"

# Wait a moment for server to start
sleep 2

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Frontend is running (PID: $FRONTEND_PID)${NC}"
    echo -e "${GREEN}   Frontend URL: http://localhost:$FRONTEND_PORT${NC}"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
    echo "   Check logs: $SCRIPT_DIR/frontend.log"
    exit 1
fi

echo ""

# ============================================================================
# STEP 5: OPEN BROWSER
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🌍 Step 5: Opening Dashboard in Browser...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Wait a moment for everything to be ready
sleep 2

# Try to open browser (works on Linux, macOS, and Windows with WSL)
if command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:$FRONTEND_PORT" 2>/dev/null && \
        echo -e "${GREEN}✅ Browser opened${NC}" || \
        echo -e "${YELLOW}⚠️  Could not auto-open browser. Please open: http://localhost:$FRONTEND_PORT${NC}"
elif command -v open > /dev/null; then
    open "http://localhost:$FRONTEND_PORT" 2>/dev/null && \
        echo -e "${GREEN}✅ Browser opened${NC}" || \
        echo -e "${YELLOW}⚠️  Could not auto-open browser. Please open: http://localhost:$FRONTEND_PORT${NC}"
else
    echo -e "${YELLOW}⚠️  Please manually open: http://localhost:$FRONTEND_PORT${NC}"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ DASHBOARD STARTED SUCCESSFULLY ✅              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Access Points:${NC}"
echo -e "   ${GREEN}Frontend:${NC} http://localhost:$FRONTEND_PORT"
echo -e "   ${GREEN}Backend API:${NC} http://localhost:$BACKEND_PORT"
echo -e "   ${GREEN}API Docs:${NC} http://localhost:$BACKEND_PORT/docs"
echo ""
echo -e "${BLUE}📊 Process IDs:${NC}"
echo -e "   ${GREEN}Backend:${NC} $BACKEND_PID (saved to: $SCRIPT_DIR/backend.pid)"
echo -e "   ${GREEN}Frontend:${NC} $FRONTEND_PID (saved to: $SCRIPT_DIR/frontend.pid)"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "   ${GREEN}Backend:${NC} $SCRIPT_DIR/backend.log"
echo -e "   ${GREEN}Frontend:${NC} $SCRIPT_DIR/frontend.log"
echo ""
echo -e "${YELLOW}💡 To stop the dashboard:${NC}"
echo -e "   ${BLUE}./stop_dashboard.sh${NC} (if available)"
echo -e "   ${BLUE}Or:${NC} kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎯 Dashboard is ready! Happy querying! 🎯${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Keep script running (optional - can be backgrounded)
# Uncomment the following to keep the script running and show logs:
# tail -f "$SCRIPT_DIR/backend.log" "$SCRIPT_DIR/frontend.log"

