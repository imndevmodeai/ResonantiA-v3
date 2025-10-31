#!/bin/bash
# FaceCheck Flask App Startup Script
# Runs the Flask application with FaceCheck.ID integration

echo "🎭 Starting FaceCheck Flask Application..."
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not found. Installing Flask..."
    pip3 install flask requests
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory"
    echo "Please run this script from the directory containing app.py"
    exit 1
fi

# Set environment variables for Flask
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the Flask application
echo "🚀 Starting Flask application..."
echo "📱 FaceCheck API will be available at: http://localhost:5000"
echo "🔍 FaceCheck.ID integration: Active"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Run the Flask app
python3 app.py





