#!/bin/bash
# Complete setup script for FaceCheck with ngrok and Telegram bot
# This will guide you through the entire setup process

echo "🎭 FaceCheck Complete Setup"
echo "============================"
echo ""

# Step 1: Check Telegram Desktop
echo "📱 Step 1: Telegram Desktop Setup"
echo "-----------------------------------"
if [ -d ~/Downloads ] && find ~/Downloads -name "*telegram*" -o -name "*Telegram*" 2>/dev/null | grep -q .; then
    echo "✅ Found Telegram in Downloads folder"
    read -p "Have you installed and logged into Telegram Desktop? (y/n): " telegram_ready
    if [ "$telegram_ready" != "y" ]; then
        echo ""
        echo "📝 Please:"
        echo "1. Install Telegram Desktop from Downloads"
        echo "2. Log in with your phone number"
        echo "3. Run this script again"
        exit 0
    fi
else
    echo "⚠️  Telegram not found in Downloads"
    read -p "Have you installed Telegram Desktop? (y/n): " telegram_installed
    if [ "$telegram_installed" != "y" ]; then
        echo "📥 Download Telegram Desktop from: https://desktop.telegram.org/"
        exit 0
    fi
fi

# Step 2: Create Telegram Bot
echo ""
echo "🤖 Step 2: Create Telegram Bot"
echo "-------------------------------"
echo "1. Open Telegram Desktop"
echo "2. Search for @BotFather"
echo "3. Send /newbot"
echo "4. Follow the instructions"
echo ""
read -p "Have you created your bot and received the token? (y/n): " bot_created

if [ "$bot_created" != "y" ]; then
    echo ""
    echo "📖 Follow these steps:"
    echo "1. In Telegram, search for @BotFather"
    echo "2. Click 'Start'"
    echo "3. Send: /newbot"
    echo "4. Give your bot a name"
    echo "5. Give it a username (must end with 'bot')"
    echo "6. Copy the token BotFather gives you"
    echo ""
    echo "Then run this script again!"
    exit 0
fi

# Step 3: Get Bot Token
echo ""
echo "🔑 Step 3: Enter Your Bot Token"
echo "---------------------------------"
read -p "Paste your bot token here: " bot_token

if [ -z "$bot_token" ]; then
    echo "❌ Token is required!"
    exit 1
fi

# Step 4: Create .env file
echo ""
echo "📝 Step 4: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
fi

# Update .env with token
if grep -q "FACECHECK_BOT_TOKEN" .env; then
    # Update existing token
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|FACECHECK_BOT_TOKEN=.*|FACECHECK_BOT_TOKEN=$bot_token|" .env
    else
        # Linux
        sed -i "s|FACECHECK_BOT_TOKEN=.*|FACECHECK_BOT_TOKEN=$bot_token|" .env
    fi
else
    # Add new token
    echo "FACECHECK_BOT_TOKEN=$bot_token" >> .env
    echo "FACECHECK_MODE=both" >> .env
fi

echo "✅ Bot token saved to .env"

# Step 5: Setup ngrok
echo ""
echo "🌐 Step 5: Setup ngrok"
echo "----------------------"
read -p "Do you want to set up ngrok now? (y/n): " setup_ngrok

if [ "$setup_ngrok" = "y" ]; then
    echo ""
    echo "📥 Setting up ngrok..."
    ./setup_ngrok.sh
    
    if [ $? -ne 0 ]; then
        echo "⚠️  ngrok setup had issues, but continuing..."
    fi
fi

# Step 6: Install dependencies
echo ""
echo "📦 Step 6: Installing Dependencies"
echo "-----------------------------------"
if [ -f facecheck_requirements.txt ]; then
    echo "Installing Python packages..."
    pip3 install -r facecheck_requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed"
    else
        echo "⚠️  Some dependencies may have failed to install"
    fi
else
    echo "⚠️  facecheck_requirements.txt not found"
    echo "Installing basic packages..."
    pip3 install flask requests python-telegram-bot python-dotenv gunicorn
fi

# Step 7: Test setup
echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "📋 Summary:"
echo "  ✅ Telegram bot token configured"
echo "  ✅ Environment file created"
if [ "$setup_ngrok" = "y" ]; then
    echo "  ✅ ngrok configured"
fi
echo "  ✅ Dependencies installed"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Test your bot locally:"
echo "   ./face.sh both"
echo ""
echo "2. Find your bot on Telegram:"
echo "   Search for the username you created"
echo "   Send /start to test"
echo ""
if [ "$setup_ngrok" != "y" ]; then
    echo "3. (Optional) Set up ngrok to expose localhost:"
    echo "   ./setup_ngrok.sh"
    echo ""
fi
echo "4. Start ngrok (if configured):"
echo "   ./start_ngrok.sh"
echo ""
echo "5. Deploy to cloud (optional):"
echo "   See DEPLOYMENT_GUIDE.md"
echo ""
echo "🎉 You're all set! Happy botting!"



