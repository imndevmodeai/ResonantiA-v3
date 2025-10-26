#!/bin/bash

# --- Quick Start Script for ResonantiA Protocol v3.5-GP Dashboard ---
# Simple script to quickly start the web dashboard

echo "🚀 Quick Start: ResonantiA Protocol v3.5-GP Dashboard"

# Navigate to sandbox directory
cd "$(dirname "$0")"
SANDBOX_DIR=$(pwd)

# Check for virtual environment
PARENT_DIR=$(dirname "$SANDBOX_DIR")
VENV_PATH="$PARENT_DIR/arche_env"

if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at: $VENV_PATH"
    echo "Please run the main setup_and_run.sh first"
    exit 1
fi

# Activate environment
echo "🔧 Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$SANDBOX_DIR:$PARENT_DIR/Three_PointO_ArchE:$PARENT_DIR/Four_PointO_ArchE

# Start web dashboard
echo "🌐 Starting Web Dashboard..."
echo "   - Dashboard will be available at: http://localhost:5000"
echo "   - Press Ctrl+C to stop"
echo ""

python3 dashboard/web_dashboard.py
