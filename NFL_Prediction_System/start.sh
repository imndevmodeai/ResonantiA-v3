#!/bin/bash
# NFL Prediction System Startup Script
# World-class NFL prediction system launcher

echo "🏈 NFL PREDICTION SYSTEM - WORLD-CLASS STARTUP"
echo "=============================================="

# Check if Python 3.8+ is installed
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3.8+ is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/cache
mkdir -p static
mkdir -p templates

# Set environment variables
export NFL_API_KEY="your_nfl_api_key_here"
export WEATHER_API_KEY="your_weather_api_key_here"
export REDIS_URL="redis://localhost:6379"

# Start the system
echo "🚀 Starting NFL Prediction System..."
echo "🌐 Web Interface: http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

# Start FastAPI server
python3 api/nfl_prediction_api.py
