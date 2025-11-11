#!/bin/bash
# Quick script to expose localhost to the internet
# Usage: ./expose_localhost.sh [port] [method]

PORT="${1:-3033}"
METHOD="${2:-cloudflare}"

echo "🌐 Exposing localhost:$PORT to the internet..."
echo "Method: $METHOD"
echo ""

case $METHOD in
    ngrok)
        if ! command -v ngrok &> /dev/null; then
            echo "❌ ngrok not installed"
            echo "Install: https://ngrok.com/download"
            exit 1
        fi
        echo "🚀 Starting ngrok on port $PORT..."
        echo "📊 Web interface: http://127.0.0.1:4040"
        ngrok http $PORT
        ;;
    
    cloudflare|cloudflared)
        if ! command -v cloudflared &> /dev/null; then
            echo "⚠️  cloudflared not installed, trying to download..."
            curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
            chmod +x /tmp/cloudflared
            /tmp/cloudflared tunnel --url http://localhost:$PORT
        else
            echo "🚀 Starting Cloudflare Tunnel on port $PORT..."
            cloudflared tunnel --url http://localhost:$PORT
        fi
        ;;
    
    localtunnel|lt)
        if ! command -v lt &> /dev/null && ! command -v npx &> /dev/null; then
            echo "❌ localtunnel not installed and npx not available"
            echo "Install Node.js or run: npm install -g localtunnel"
            exit 1
        fi
        echo "🚀 Starting localtunnel on port $PORT..."
        if command -v lt &> /dev/null; then
            lt --port $PORT
        else
            npx localtunnel --port $PORT
        fi
        ;;
    
    serveo|ssh)
        echo "🚀 Starting serveo tunnel on port $PORT..."
        echo "⚠️  Make sure you have SSH access"
        ssh -R 80:localhost:$PORT serveo.net
        ;;
    
    *)
        echo "❌ Unknown method: $METHOD"
        echo ""
        echo "Available methods:"
        echo "  - cloudflare (default, no install needed)"
        echo "  - ngrok (most popular)"
        echo "  - localtunnel (simple)"
        echo "  - serveo (SSH-based)"
        echo ""
        echo "Usage: $0 [port] [method]"
        echo "Example: $0 3033 ngrok"
        exit 1
        ;;
esac



