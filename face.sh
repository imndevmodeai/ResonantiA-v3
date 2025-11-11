#!/bin/bash
# FaceCheck Flask App + Telegram Bot Startup Script
# Runs the Flask application with FaceCheck.ID integration and optional Telegram bot

echo "🎭 Starting FaceCheck Service..."
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check for required files
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory"
    echo "Please run this script from the directory containing app.py"
    exit 1
fi

# Determine mode from environment or argument
MODE="${1:-both}"
if [ "$1" = "bot" ] || [ "$1" = "web" ] || [ "$1" = "both" ]; then
    MODE="$1"
fi

# Check if .env file exists
if [ -f ".env" ]; then
    echo "📝 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Install dependencies if needed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Installing dependencies..."
    pip3 install -r facecheck_requirements.txt 2>/dev/null || pip3 install flask requests python-telegram-bot python-dotenv
fi

# Set environment variables
export FLASK_APP=app.py
export FACECHECK_MODE="$MODE"

# Development vs Production
if [ "$MODE" = "production" ] || [ -n "$PORT" ]; then
    export FLASK_ENV=production
    export FLASK_DEBUG=0
else
    export FLASK_ENV=development
    export FLASK_DEBUG=1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check Telegram bot token
if [ -z "$FACECHECK_BOT_TOKEN" ]; then
    echo "⚠️  Warning: FACECHECK_BOT_TOKEN not set. Bot functionality will be disabled."
    if [ "$MODE" = "bot" ]; then
        echo "❌ Cannot run in bot-only mode without token"
        exit 1
    fi
    MODE="web"
fi

# Display startup information
echo ""
echo "🚀 Starting FaceCheck Service..."
echo "📋 Mode: $MODE"
echo ""

if [ "$MODE" = "bot" ] || [ "$MODE" = "both" ]; then
    if [ -n "$FACECHECK_BOT_TOKEN" ]; then
        echo "🤖 Telegram Bot: ENABLED"
    else
        echo "🤖 Telegram Bot: DISABLED (no token)"
    fi
fi

# Function to set up external access using cloudflared or ngrok
setup_external_access() {
    local flask_port=$1
    local tunnel_type="${TUNNEL_TYPE:-cloudflared}"
    
    echo ""
    echo "🌍 Setting up external access..."
    
    if [ "$tunnel_type" = "cloudflared" ]; then
        # Use cloudflared (free, no signup)
        CLOUDFLARED_CMD=""
        if command -v cloudflared &> /dev/null; then
            CLOUDFLARED_CMD="cloudflared"
        elif [ -f "/tmp/cloudflared" ] && [ -x "/tmp/cloudflared" ]; then
            CLOUDFLARED_CMD="/tmp/cloudflared"
        else
            echo "📥 Downloading cloudflared..."
            curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared 2>/dev/null
            chmod +x /tmp/cloudflared
            CLOUDFLARED_CMD="/tmp/cloudflared"
        fi
        
        if [ -n "$CLOUDFLARED_CMD" ]; then
            echo "🚇 Starting Cloudflare Tunnel..."
            echo "   This will create a public URL accessible from anywhere"
            
            # Start cloudflared in background and capture the URL
            $CLOUDFLARED_CMD tunnel --url http://localhost:$flask_port > /tmp/cloudflared.log 2>&1 &
            CLOUDFLARED_PID=$!
            sleep 3
            
            # Extract the public URL from logs (multiple patterns)
            PUBLIC_URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log 2>/dev/null | head -1)
            if [ -z "$PUBLIC_URL" ]; then
                # Try alternative pattern from cloudflared output
                PUBLIC_URL=$(grep -oP 'https://[a-z0-9-]+-[a-z0-9-]+-[a-z0-9-]+-[a-z0-9-]+-[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log 2>/dev/null | head -1)
            fi
            if [ -z "$PUBLIC_URL" ]; then
                # Try to extract from the formatted output
                PUBLIC_URL=$(grep -A 2 "Your quick Tunnel" /tmp/cloudflared.log | grep -oP 'https://[^\s]+' | head -1)
            fi
            
            if [ -n "$PUBLIC_URL" ]; then
                echo "✅ External access enabled!"
                echo "🌐 Public URL: $PUBLIC_URL"
                echo "   (This URL is accessible from anywhere on the internet)"
                echo "   PID: $CLOUDFLARED_PID"
                echo "$PUBLIC_URL" > /tmp/facecheck_public_url.txt
            else
                echo "⚠️  Could not extract public URL. Check /tmp/cloudflared.log"
                cat /tmp/cloudflared.log | tail -5
            fi
        else
            echo "❌ Could not set up cloudflared"
        fi
        
    elif [ "$tunnel_type" = "ngrok" ]; then
        # Use ngrok (requires signup and authtoken)
        if ! command -v ngrok &> /dev/null; then
            echo "❌ ngrok not found. Install it or use cloudflared (TUNNEL_TYPE=cloudflared)"
            return 1
        fi
        
        echo "🚇 Starting ngrok tunnel..."
        ngrok http $flask_port > /tmp/ngrok.log 2>&1 &
        NGROK_PID=$!
        sleep 3
        
        # Try to get URL from ngrok API
        NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -oP '"public_url":"https://[^"]+"' | head -1 | cut -d'"' -f4)
        
        if [ -n "$NGROK_URL" ]; then
            echo "✅ External access enabled!"
            echo "🌐 Public URL: $NGROK_URL"
            echo "   (This URL is accessible from anywhere on the internet)"
            echo "   Dashboard: http://localhost:4040"
            echo "$NGROK_URL" > /tmp/facecheck_public_url.txt
        else
            echo "⚠️  Could not get ngrok URL. Check http://localhost:4040"
        fi
    else
        echo "❌ Unknown tunnel type: $tunnel_type (use 'cloudflared' or 'ngrok')"
        return 1
    fi
}

if [ "$MODE" = "web" ] || [ "$MODE" = "both" ]; then
    # Initialize port forwarding status
    PORT_FORWARDED=1
    
    # Function to set up custom domain (face.local)
    setup_custom_domain() {
        local domain="${FACECHECK_DOMAIN:-face.local}"
        local hosts_file="/etc/hosts"
        
        # Check if domain already exists in /etc/hosts
        if grep -q "$domain" "$hosts_file" 2>/dev/null; then
            echo "✅ Domain $domain already configured in /etc/hosts"
            return 0
        fi
        
        # Try to add domain to /etc/hosts (requires sudo)
        echo "🔧 Setting up custom domain: $domain"
        echo "   This requires sudo access to modify /etc/hosts"
        
        # Check if we can write to /etc/hosts
        if [ -w "$hosts_file" ]; then
            echo "127.0.0.1    $domain" >> "$hosts_file"
            echo "✅ Added $domain to /etc/hosts"
        else
            # Try with sudo
            if sudo sh -c "echo '127.0.0.1    $domain' >> $hosts_file" 2>/dev/null; then
                echo "✅ Added $domain to /etc/hosts (with sudo)"
            else
                echo "⚠️  Could not add $domain to /etc/hosts (may need manual setup)"
                echo "   Please run: sudo sh -c \"echo '127.0.0.1    $domain' >> /etc/hosts\""
                return 1
            fi
        fi
    }
    
    # Function to set up port forwarding from port 80 to Flask port
    setup_port_forwarding() {
        local flask_port=$1
        
        # Check if port 80 is available
        if ! check_port_available 80; then
            echo "⚠️  Port 80 is already in use, skipping port forwarding"
            return 1
        fi
        
        # Check if iptables is available
        if ! command -v iptables &> /dev/null; then
            echo "ℹ️  iptables not found, skipping port forwarding"
            return 1
        fi
        
        # Check if we have sudo access
        if ! sudo -n true 2>/dev/null; then
            echo "ℹ️  Port forwarding requires sudo (skipping)"
            echo "   You can access the app at http://face.local:$flask_port"
            return 1
        fi
        
        # Set up iptables port forwarding (requires sudo)
        echo "🔧 Setting up port forwarding: 80 -> $flask_port"
        
        # Add PREROUTING rule (for external access)
        if sudo iptables -t nat -C PREROUTING -p tcp --dport 80 -j REDIRECT --to-port $flask_port 2>/dev/null; then
            echo "✅ Port forwarding rule already exists"
        else
            if sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port $flask_port 2>/dev/null; then
                echo "✅ Port forwarding configured: 80 -> $flask_port"
            else
                echo "⚠️  Failed to set up port forwarding (may need manual setup)"
                return 1
            fi
        fi
        
        # Also set up OUTPUT rule (for localhost access)
        if sudo iptables -t nat -C OUTPUT -p tcp -d 127.0.0.1 --dport 80 -j REDIRECT --to-port $flask_port 2>/dev/null; then
            echo "✅ Localhost forwarding rule already exists"
        else
            sudo iptables -t nat -A OUTPUT -p tcp -d 127.0.0.1 --dport 80 -j REDIRECT --to-port $flask_port 2>/dev/null
        fi
        
        return 0
    }
    
    # Function to check if a port is available
    check_port_available() {
        local port=$1
        if command -v netstat &> /dev/null; then
            ! netstat -tuln 2>/dev/null | grep -q ":$port "
        elif command -v ss &> /dev/null; then
            ! ss -tuln 2>/dev/null | grep -q ":$port "
        elif command -v lsof &> /dev/null; then
            ! lsof -i :$port &> /dev/null
        else
            # Fallback: try to bind to the port
            timeout 1 bash -c "echo > /dev/tcp/localhost/$port" 2>/dev/null
            [ $? -ne 0 ]
        fi
    }
    
    # Function to find an available port starting from a given port
    find_available_port() {
        local start_port=$1
        local port=$start_port
        local max_attempts=100
        
        while [ $max_attempts -gt 0 ]; do
            if check_port_available $port; then
                echo $port
                return 0
            fi
            port=$((port + 1))
            max_attempts=$((max_attempts - 1))
        done
        
        echo ""
        return 1
    }
    
    # Function to open port with ufw
    open_port_ufw() {
        local port=$1
        if command -v ufw &> /dev/null; then
            # Check if ufw is active
            if ufw status | grep -q "Status: active"; then
                # Check if port is already allowed
                if ! ufw status | grep -q ":$port"; then
                    echo "🔓 Opening port $port with ufw..."
                    echo "y" | ufw allow $port/tcp > /dev/null 2>&1
                    if [ $? -eq 0 ]; then
                        echo "✅ Port $port opened successfully"
                    else
                        echo "⚠️  Failed to open port $port (may need sudo)"
                    fi
                else
                    echo "✅ Port $port is already open"
                fi
            else
                echo "ℹ️  UFW is not active, skipping port opening"
            fi
        else
            echo "ℹ️  UFW not found, skipping port opening"
        fi
    }
    
    # Determine default port (check app.py for hardcoded port or use 5000)
    DEFAULT_PORT=3033
    if [ -f "app.py" ]; then
        # Try to extract port from app.py
        APP_PORT=$(grep -oP "port=\K\d+" app.py 2>/dev/null | head -1)
        if [ -n "$APP_PORT" ]; then
            DEFAULT_PORT=$APP_PORT
        fi
    fi
    
    # Use PORT env var if set, otherwise use default
    REQUESTED_PORT="${PORT:-$DEFAULT_PORT}"
    
    # Check if requested port is available
    if check_port_available $REQUESTED_PORT; then
        PORT=$REQUESTED_PORT
        echo "✅ Port $PORT is available"
    else
        echo "⚠️  Port $REQUESTED_PORT is already in use"
        echo "🔍 Searching for available port..."
        AVAILABLE_PORT=$(find_available_port $REQUESTED_PORT)
        
        if [ -n "$AVAILABLE_PORT" ]; then
            PORT=$AVAILABLE_PORT
            echo "✅ Found available port: $PORT"
        else
            echo "❌ Could not find an available port"
            exit 1
        fi
    fi
    
    # Open the port with ufw
    open_port_ufw $PORT
    
    # Set up custom domain (face.local)
    setup_custom_domain
    
    # Try to set up port forwarding from 80 to Flask port (optional)
    USE_PORT_80="${USE_PORT_80:-true}"
    if [ "$USE_PORT_80" = "true" ]; then
        setup_port_forwarding $PORT
        PORT_FORWARDED=$?
    else
        PORT_FORWARDED=1
    fi
    
    # Export PORT so the app uses it
    export PORT
    
    # Display access URLs
    echo ""
    echo "🌐 Web Interface URLs:"
    if [ $PORT_FORWARDED -eq 0 ]; then
        echo "   ✅ http://face.local (port 80 -> $PORT)"
    else
        echo "   ✅ http://face.local:$PORT"
    fi
    echo "   ✅ http://localhost:$PORT"
    echo "🔍 FaceCheck.ID integration: Active"
    
    # Set up external access if requested
    if [ "${EXPOSE_EXTERNAL:-false}" = "true" ] || [ -n "$EXTERNAL_ACCESS" ]; then
        setup_external_access $PORT
    fi
fi

echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Cleanup function for iptables rules (called on exit)
cleanup_iptables() {
    if [ -n "$PORT" ] && [ -n "$PORT_FORWARDED" ] && [ "$PORT_FORWARDED" = "0" ]; then
        echo ""
        echo "🧹 Cleaning up port forwarding rules..."
        sudo iptables -t nat -D PREROUTING -p tcp --dport 80 -j REDIRECT --to-port $PORT 2>/dev/null
        sudo iptables -t nat -D OUTPUT -p tcp -d 127.0.0.1 --dport 80 -j REDIRECT --to-port $PORT 2>/dev/null
        echo "✅ Cleanup complete"
    fi
}

# Set up trap to cleanup on exit
trap cleanup_iptables EXIT INT TERM

# Activate virtual environment if it exists
if [ -d "arche_env" ]; then
    source arche_env/bin/activate
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python3"
fi

# Determine which app to use (with or without auth)
USE_AUTH="${USE_AUTH:-false}"
if [ "$USE_AUTH" = "true" ] && [ -f "app_with_auth.py" ]; then
    APP_FILE="app_with_auth.py"
    echo "🔐 Using authenticated version (app_with_auth.py)"
    if [ -z "$FACECHECK_AUTH_USER" ] || [ -z "$FACECHECK_AUTH_PASS" ]; then
        echo "⚠️  WARNING: FACECHECK_AUTH_USER and FACECHECK_AUTH_PASS not set!"
        echo "   Using default credentials (CHANGE THESE!)"
        echo "   Set them in .env or export before running"
    fi
else
    APP_FILE="app.py"
    if [ "${EXPOSE_EXTERNAL:-false}" = "true" ]; then
        echo "⚠️  WARNING: External access enabled WITHOUT authentication!"
        echo "   Anyone with the URL can access your app."
        echo "   Consider using: USE_AUTH=true EXPOSE_EXTERNAL=true ./face.sh"
    fi
fi

# Run the appropriate service
if [ "$MODE" = "bot" ]; then
    # Bot-only mode
    $PYTHON_CMD facecheck_bot.py
elif [ "$MODE" = "web" ]; then
    # Web-only mode (Flask app with optional auth)
    $PYTHON_CMD $APP_FILE
else
    # Both bot and web (using facecheck_bot.py which handles both)
    $PYTHON_CMD facecheck_bot.py
fi





