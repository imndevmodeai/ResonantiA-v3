#!/bin/bash
# Setup script for Telegram Thread Saver Bot

set -e  # Exit on error

echo "🚀 Setting up Telegram Thread Saver Bot..."
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v14+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js found: $NODE_VERSION"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

NPM_VERSION=$(npm --version)
echo "✅ npm found: $NPM_VERSION"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env file not found. Creating template..."
    echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env
    echo "✅ Created .env file. Please edit it with your Telegram bot token!"
else
    echo "✅ .env file exists"
fi

# Create saves directory
if [ ! -d saves ]; then
    mkdir -p saves
    echo "✅ Created saves directory"
else
    echo "✅ saves directory exists"
fi

# Check for Chrome/Chromium
echo ""
echo "🔍 Checking for Chrome/Chromium..."

CHROME_FOUND=false
if command -v google-chrome &> /dev/null; then
    CHROME_PATH=$(which google-chrome)
    echo "✅ Found Google Chrome: $CHROME_PATH"
    CHROME_FOUND=true
elif command -v chromium-browser &> /dev/null; then
    CHROME_PATH=$(which chromium-browser)
    echo "✅ Found Chromium: $CHROME_PATH"
    CHROME_FOUND=true
elif command -v chromium &> /dev/null; then
    CHROME_PATH=$(which chromium)
    echo "✅ Found Chromium: $CHROME_PATH"
    CHROME_FOUND=true
fi

if [ "$CHROME_FOUND" = false ]; then
    echo "⚠️  Chrome/Chromium not found in PATH"
    echo ""
    echo "Please install Chrome or Chromium:"
    echo "  Ubuntu/Debian: sudo apt-get install chromium-browser"
    echo "  Or: sudo apt-get install google-chrome-stable"
    echo ""
    echo "Alternatively, install via Puppeteer:"
    echo "  npx puppeteer browsers install chrome"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and add your TELEGRAM_BOT_TOKEN"
echo "2. Run: node app.js"
echo "3. Send a Hugging Face URL to your bot on Telegram"
echo ""
echo "For more information, see README.md"
