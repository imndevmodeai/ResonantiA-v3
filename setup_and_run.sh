#!/bin/bash

# --- Comprehensive Setup and Run Script for VCD Environment ---
# This script ensures a clean, consistent environment for running ArchE and the VCD.
# It will:
# 1. Stop any running services.
# 2. Delete the old Python virtual environment to prevent stale package issues.
# 3. Recreate the Python virtual environment.
# 4. Install all required Python packages.
# 5. Set the necessary PYTHONPATH.
# 6. Start the backend and frontend services.

echo "🚀 Starting Comprehensive VCD Environment Setup..."

# Step 1: Stop any lingering services from previous runs
echo "[1/6] Stopping any lingering services..."
pkill -f "vcd_bridge.py"
pkill -f "next dev"
sleep 2 # Give processes time to shut down

# Step 2: Clean the Python environment
echo "[2/6] Cleaning up old Python virtual environment..."
if [ -d "arche_env" ]; then
    rm -rf arche_env
    echo "  - Removed old 'arche_env' directory."
fi

# Step 3: Recreate the virtual environment
echo "[3/6] Creating new Python virtual environment..."
python3 -m venv arche_env
echo "  - New 'arche_env' created."

# Step 4: Activate and install dependencies
echo "[4/6] Activating environment and installing dependencies..."
source arche_env/bin/activate
pip install --upgrade pip
if [ -f "requirements_core.txt" ]; then
    pip install -r requirements_core.txt
    echo "  - Python packages installed from requirements_core.txt."
else
    echo "  - WARNING: requirements_core.txt not found. Trying full requirements.txt."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo "  - Python packages installed from requirements.txt."
    else
        echo "  - WARNING: No requirements file found. Skipping package installation."
    fi
fi
deactivate

# Step 5: Set up environment and start Backend
echo "[5/6] Starting VCD Bridge (Backend)..."
export PYTHONPATH=$PYTHONPATH:$(pwd)/Three_PointO_ArchE:$(pwd)/Four_PointO_ArchE
(
  source arche_env/bin/activate
  nohup python3 vcd_bridge.py > vcd_bridge.log 2>&1 &
  echo $! > vcd_bridge.pid
)
sleep 5 # Give the backend a moment to initialize
if ps -p $(cat vcd_bridge.pid) > /dev/null; then
   echo "  - ✅ VCD Bridge started successfully (PID: $(cat vcd_bridge.pid))."
   echo "  - Logs are being written to: vcd_bridge.log"
else
   echo "  - ❌ VCD Bridge FAILED to start. Check vcd_bridge.log for details."
   exit 1
fi

# Step 6: Start Frontend
echo "[6/6] Starting VCD Frontend (Next.js)..."
(
  cd nextjs-chat
  nohup npm run dev > ../nextjs_chat.log 2>&1 &
  echo $! > ../nextjs_chat.pid
)
sleep 10 # Give Next.js time to compile and start
if ps -p $(cat nextjs_chat.pid) > /dev/null; then
    echo "  - ✅ VCD Frontend started successfully (PID: $(cat nextjs_chat.pid))."
    echo "  - Logs are being written to: nextjs_chat.log"
else
    echo "  - ❌ VCD Frontend FAILED to start. Check nextjs_chat.log for details."
    exit 1
fi


echo "🎉 All services are running."
echo "   - VCD Frontend available at: http://localhost:3000"
echo "   - VCD Bridge WebSocket listening on: ws://localhost:8765"
echo "To stop all services, run: pkill -F vcd_bridge.pid && pkill -F nextjs_chat.pid"
