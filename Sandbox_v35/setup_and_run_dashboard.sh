#!/bin/bash

# --- Comprehensive Setup and Run Script for ResonantiA Protocol v3.5-GP Dashboard ---
# This script ensures a clean, consistent environment for running the sandbox dashboard.
# It will:
# 1. Stop any running dashboard services.
# 2. Activate the existing Python virtual environment.
# 3. Install any missing Python packages.
# 4. Set the necessary PYTHONPATH.
# 5. Start the GUI and Web dashboard services.
# 6. Provide access URLs and control commands.

echo "🚀 Starting ResonantiA Protocol v3.5-GP Dashboard Setup..."

# Step 1: Stop any lingering dashboard services from previous runs
echo "[1/7] Stopping any lingering dashboard services..."
pkill -f "tools_dashboard.py"
pkill -f "web_dashboard.py"
pkill -f "flask"
sleep 2 # Give processes time to shut down

# Step 2: Navigate to sandbox directory
echo "[2/7] Navigating to sandbox directory..."
cd "$(dirname "$0")"
SANDBOX_DIR=$(pwd)
echo "  - Sandbox directory: $SANDBOX_DIR"

# Step 3: Check for virtual environment
echo "[3/7] Checking for virtual environment..."
PARENT_DIR=$(dirname "$SANDBOX_DIR")
VENV_PATH="$PARENT_DIR/arche_env"

if [ -d "$VENV_PATH" ]; then
    echo "  - ✅ Found virtual environment at: $VENV_PATH"
else
    echo "  - ❌ Virtual environment not found at: $VENV_PATH"
    echo "  - Please run the main setup_and_run.sh first to create the environment"
    exit 1
fi

# Step 4: Activate environment and install dashboard dependencies
echo "[4/7] Activating environment and installing dashboard dependencies..."
source "$VENV_PATH/bin/activate"

# Install dashboard-specific packages
echo "  - Installing dashboard dependencies..."
pip install --upgrade pip
pip install flask matplotlib networkx psutil

# Check if all required packages are available
echo "  - Verifying package availability..."
python3 -c "
import sys
required_packages = ['flask', 'matplotlib', 'networkx', 'psutil', 'dowhy', 'mesa', 'selenium', 'googlemaps']
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        print(f'  ✅ {package}')
    except ImportError:
        missing_packages.append(package)
        print(f'  ❌ {package}')

if missing_packages:
    print(f'  - Installing missing packages: {missing_packages}')
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages)
else:
    print('  - All required packages are available!')
"

# Step 5: Set up environment variables
echo "[5/7] Setting up environment variables..."
export PYTHONPATH=$PYTHONPATH:$SANDBOX_DIR:$PARENT_DIR/Three_PointO_ArchE:$PARENT_DIR/Four_PointO_ArchE
echo "  - PYTHONPATH set to: $PYTHONPATH"

# Step 6: Start GUI Dashboard (Background)
echo "[6/7] Starting GUI Dashboard..."
(
  cd "$SANDBOX_DIR"
  source "$VENV_PATH/bin/activate"
  export PYTHONPATH=$PYTHONPATH:$SANDBOX_DIR:$PARENT_DIR/Three_PointO_ArchE:$PARENT_DIR/Four_PointO_ArchE
  nohup python3 dashboard/tools_dashboard.py > gui_dashboard.log 2>&1 &
  echo $! > gui_dashboard.pid
)
sleep 3 # Give the GUI dashboard a moment to initialize
if ps -p $(cat gui_dashboard.pid) > /dev/null 2>&1; then
   echo "  - ✅ GUI Dashboard started successfully (PID: $(cat gui_dashboard.pid))."
   echo "  - Logs are being written to: gui_dashboard.log"
else
   echo "  - ⚠️  GUI Dashboard may have issues (check gui_dashboard.log)"
   echo "  - This is normal if running in headless environment"
fi

# Step 7: Start Web Dashboard
echo "[7/7] Starting Web Dashboard..."
(
  cd "$SANDBOX_DIR"
  source "$VENV_PATH/bin/activate"
  export PYTHONPATH=$PYTHONPATH:$SANDBOX_DIR:$PARENT_DIR/Three_PointO_ArchE:$PARENT_DIR/Four_PointO_ArchE
  nohup python3 dashboard/web_dashboard.py > web_dashboard.log 2>&1 &
  echo $! > web_dashboard.pid
)
sleep 5 # Give Flask time to start
if ps -p $(cat web_dashboard.pid) > /dev/null 2>&1; then
    echo "  - ✅ Web Dashboard started successfully (PID: $(cat web_dashboard.pid))."
    echo "  - Logs are being written to: web_dashboard.log"
else
    echo "  - ❌ Web Dashboard FAILED to start. Check web_dashboard.log for details."
    exit 1
fi

# Final status and instructions
echo ""
echo "🎉 Dashboard services are running!"
echo ""
echo "📊 Available Dashboards:"
echo "   - Web Dashboard: http://localhost:5000"
echo "   - GUI Dashboard: Running in background (check gui_dashboard.log)"
echo ""
echo "🔧 Dashboard Features:"
echo "   - Real-time tool status monitoring"
echo "   - System metrics (CPU, Memory, Disk)"
echo "   - v3.5-GP performance metrics"
echo "   - Validation and deployment controls"
echo "   - Export functionality"
echo ""
echo "📋 Control Commands:"
echo "   - Stop all dashboards: pkill -F gui_dashboard.pid && pkill -F web_dashboard.pid"
echo "   - View GUI logs: tail -f gui_dashboard.log"
echo "   - View Web logs: tail -f web_dashboard.log"
echo "   - Check status: ps aux | grep dashboard"
echo ""
echo "🌐 Access the Web Dashboard:"
echo "   - Open your browser to: http://localhost:5000"
echo "   - The dashboard will auto-refresh every 5 seconds"
echo "   - Use the control panel for validation and deployment"
echo ""
echo "📈 Dashboard Tabs:"
echo "   - Tools Status: View all available tools and their status"
echo "   - System Monitoring: Real-time system metrics and charts"
echo "   - Validation: Run comprehensive validation tests"
echo "   - Performance: v3.5-GP performance metrics"
echo ""
echo "🛠️  Available Tools Categories:"
echo "   - Core Components (Enhanced Workflow Engine, IAR Validator, etc.)"
echo "   - Analysis Tools (DoWhy, Mesa, Predictive Modeling, etc.)"
echo "   - Web & Search (Selenium, Google Maps, Web Search, etc.)"
echo "   - AI & ML (LLM Provider, Knowledge Graph, etc.)"
echo "   - System Tools (Code Executor, Debugger, etc.)"
echo ""
echo "✅ Setup complete! Your ResonantiA Protocol v3.5-GP dashboard is ready."
