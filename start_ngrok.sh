#!/bin/bash
# Start ngrok tunnel for FaceCheck service with authentication

echo "🚀 Starting ngrok tunnel for FaceCheck..."
echo "=========================================="

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not installed. Run ./setup_ngrok.sh first"
    exit 1
fi

# Check if config exists
if [ ! -f ~/.ngrok2/ngrok.yml ]; then
    echo "⚠️  ngrok not configured. Running setup..."
    ./setup_ngrok.sh
    if [ $? -ne 0 ]; then
        exit 1
    fi
fi

# Check if FaceCheck app is running
PORT=3033
if ! lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  FaceCheck app not running on port $PORT"
    echo "Starting FaceCheck app in background..."
    
    # Start app in background
    ./face.sh web > /tmp/facecheck.log 2>&1 &
    APP_PID=$!
    echo "✅ FaceCheck app started (PID: $APP_PID)"
    sleep 3
fi

# Start ngrok
echo ""
echo "🌐 Starting ngrok tunnel..."
echo "📊 Web interface: http://127.0.0.1:4040"
echo ""

# Check if config has facecheck tunnel
if grep -q "facecheck:" ~/.ngrok2/ngrok.yml; then
    echo "Using configured 'facecheck' tunnel..."
    ngrok start facecheck
else
    echo "Using default tunnel (port $PORT)..."
    ngrok http $PORT
fi



