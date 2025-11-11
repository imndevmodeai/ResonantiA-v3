#!/bin/bash
# Setup ngrok with authentication for FaceCheck service
# This script will help you configure ngrok with basic auth

echo "🔐 Setting up ngrok with authentication..."
echo "=========================================="

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "📥 ngrok not found. Installing..."
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux installation
        curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
        echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
        sudo apt update && sudo apt install ngrok -y
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS installation
        if command -v brew &> /dev/null; then
            brew install ngrok/ngrok/ngrok
        else
            echo "❌ Please install Homebrew first: https://brew.sh"
            echo "Or download from: https://ngrok.com/download"
            exit 1
        fi
    else
        echo "❌ Please install ngrok manually from: https://ngrok.com/download"
        exit 1
    fi
fi

echo "✅ ngrok is installed"
echo ""

# Check if ngrok is already configured
if [ -f ~/.ngrok2/ngrok.yml ]; then
    echo "⚠️  ngrok config already exists"
    read -p "Do you want to reconfigure? (y/n): " reconfigure
    if [ "$reconfigure" != "y" ]; then
        echo "Keeping existing configuration"
        exit 0
    fi
fi

# Get ngrok authtoken
echo "📝 Setting up ngrok authentication..."
echo ""
echo "1. Go to https://dashboard.ngrok.com/signup (or login)"
echo "2. Copy your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
echo ""
read -p "Enter your ngrok authtoken: " authtoken

if [ -z "$authtoken" ]; then
    echo "❌ Authtoken is required"
    exit 1
fi

# Configure ngrok
ngrok config add-authtoken "$authtoken"

if [ $? -eq 0 ]; then
    echo "✅ ngrok authtoken configured successfully"
else
    echo "❌ Failed to configure authtoken"
    exit 1
fi

# Create ngrok config with basic auth
echo ""
echo "🔐 Setting up basic authentication..."
read -p "Enter username for basic auth: " username
read -sp "Enter password for basic auth: " password
echo ""

if [ -z "$username" ] || [ -z "$password" ]; then
    echo "⚠️  Skipping basic auth setup (username/password required)"
else
    # Create ngrok config directory if it doesn't exist
    mkdir -p ~/.ngrok2
    
    # Create ngrok config with basic auth
    cat > ~/.ngrok2/ngrok.yml <<EOF
version: "2"
authtoken: $authtoken
tunnels:
  facecheck:
    addr: 3033
    proto: http
    auth: "$username:$password"
    inspect: true
EOF

    echo "✅ ngrok configured with basic auth"
    echo "   Username: $username"
    echo "   Password: [hidden]"
fi

echo ""
echo "🎉 ngrok setup complete!"
echo ""
echo "To start ngrok with auth, run:"
echo "  ngrok start facecheck"
echo ""
echo "Or use the start_ngrok.sh script"



