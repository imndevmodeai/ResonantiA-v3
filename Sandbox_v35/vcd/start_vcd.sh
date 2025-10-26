#!/bin/bash
# ResonantiA Protocol v3.5-GP - VCD Startup Script

echo "🐛 ResonantiA Protocol v3.5-GP - Interactive VCD Startup"
echo "============================================================"
set -x # Enable debugging

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Get the absolute path of the Happier directory (2 levels up from vcd)
HAPPIER_DIR=$(dirname "$(dirname "$SCRIPT_DIR")")
export PYTHONPATH=$PYTHONPATH:$HAPPIER_DIR

# Check if we're in the right directory
if [ ! -f "interactive_vcd.py" ]; then
    echo "❌ Error: Could not find interactive_vcd.py in the script's directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Activate virtual environment
if [ -f "../../arche_env/bin/activate" ]; then
    echo "🔧 Activating virtual environment..."
    source ../../arche_env/bin/activate
else
    echo "⚠️ Virtual environment not found at ../../arche_env/"
    echo "   Continuing without virtual environment..."
fi

# Get the PID of the current script
CURRENT_PID=$$

# Find and kill other VCD processes
pgrep -f "python3 interactive_vcd.py" | grep -v "$CURRENT_PID" | xargs --no-run-if-empty kill -9

# Wait a moment for cleanup
sleep 2

# Start the VCD
echo "🚀 Starting Interactive VCD..."
echo "============================================================"

python3 interactive_vcd.py
set +x # Disable debugging
