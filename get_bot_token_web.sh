#!/bin/bash
# Guide to get bot token via Telegram Web (no GUI needed!)

echo "🤖 Getting Telegram Bot Token via Web"
echo "======================================"
echo ""
echo "Since Telegram Desktop needs a display, let's use Telegram Web instead!"
echo ""
echo "📝 Steps:"
echo ""
echo "1. Open your web browser"
echo "2. Go to: https://web.telegram.org"
echo "3. Log in with your phone number"
echo "4. Search for: @BotFather"
echo "5. Click 'Start'"
echo "6. Send: /newbot"
echo "7. Follow the prompts:"
echo "   - Give your bot a name"
echo "   - Give it a username (must end with 'bot')"
echo "8. Copy the token BotFather gives you"
echo ""
echo "Then run:"
echo "  ./complete_setup.sh"
echo ""
echo "Or manually add to .env:"
echo "  FACECHECK_BOT_TOKEN=your_token_here"
echo ""
echo "💡 Your bot will work perfectly without Telegram Desktop!"
echo "   The Python bot uses polling, so it doesn't need a GUI."



