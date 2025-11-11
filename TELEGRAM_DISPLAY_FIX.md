# Fixing Telegram Desktop Display Errors

## The Problem
You're seeing Qt/GUI errors like:
```
QPainter::begin: Paint device returned engine == 0
QWidget::render: Cannot render with an inactive painter
```

This means Telegram Desktop can't access your display.

## Quick Diagnosis

Run this to check your display setup:
```bash
echo "DISPLAY=$DISPLAY"
echo "XDG_SESSION_TYPE=$XDG_SESSION_TYPE"
```

## Solutions

### Solution 1: Set DISPLAY Variable (Most Common)

If you're using X11:
```bash
export DISPLAY=:0
~/Downloads/Telegram/Telegram
```

Or if you're on a remote server:
```bash
export DISPLAY=:0.0
~/Downloads/Telegram/Telegram
```

### Solution 2: Use X11 Forwarding (SSH)

If you're connecting via SSH:
```bash
# Connect with X11 forwarding
ssh -X username@hostname

# Or with trusted X11 forwarding
ssh -Y username@hostname

# Then run Telegram
~/Downloads/Telegram/Telegram
```

### Solution 3: Use Virtual Display (Headless Server)

If you don't have a physical display:

```bash
# Install Xvfb (virtual framebuffer)
sudo apt install xvfb

# Run Telegram in virtual display
xvfb-run -a ~/Downloads/Telegram/Telegram
```

**Note:** This won't show a GUI, but Telegram might work in headless mode.

### Solution 4: Use Telegram CLI Instead (Recommended for Servers)

If you're on a headless server, use Telegram CLI instead:

```bash
# Install telegram-cli
sudo apt install telegram-cli

# Or use Python library
pip install python-telegram-bot
```

Then use the bot via command line or Python scripts (which you already have set up!).

### Solution 5: Check Your Desktop Environment

If you're on a desktop Linux:

```bash
# Check if you have a desktop session
echo $XDG_SESSION_TYPE

# If it says "tty" or empty, you might need to:
# 1. Log in via GUI (not SSH)
# 2. Or use a different terminal emulator
```

### Solution 6: Fix Qt Library Issues

```bash
# Install Qt dependencies
sudo apt install qt5-default libqt5gui5 libqt5core5a libqt5dbus5

# Or for Qt6
sudo apt install qt6-base-dev
```

## Best Solution for Your Use Case

Since you're setting up a **Telegram bot** (not using Telegram Desktop for chatting), you have two options:

### Option A: Use Telegram Desktop on a Different Machine
- Install Telegram Desktop on a machine with a GUI (Windows, Mac, or Linux desktop)
- Create your bot there
- Copy the token to your server

### Option B: Use Telegram Web (Easiest!)
1. Go to https://web.telegram.org in your browser
2. Log in with your phone number
3. Search for @BotFather
4. Create your bot
5. Copy the token

### Option C: Use Your Bot Code Directly
Your `facecheck_bot.py` uses **polling mode**, which doesn't need a GUI. You can:
1. Get your bot token from Telegram Web
2. Add it to `.env`
3. Run `./face.sh both`
4. The bot will work without Telegram Desktop!

## Recommended Workflow

1. **Get Bot Token**: Use Telegram Web (https://web.telegram.org)
2. **Configure Token**: Add to `.env` file
3. **Run Bot**: `./face.sh both`
4. **Test**: Send messages to your bot on Telegram (mobile app or web)

You don't actually need Telegram Desktop to run your bot!

## Quick Fix Script

Create this script to try different display options:

```bash
#!/bin/bash
# try_telegram.sh - Try different display configurations

echo "Trying DISPLAY=:0..."
export DISPLAY=:0
~/Downloads/Telegram/Telegram 2>&1 | head -5

# If that doesn't work, try :0.0
if [ $? -ne 0 ]; then
    echo "Trying DISPLAY=:0.0..."
    export DISPLAY=:0.0
    ~/Downloads/Telegram/Telegram 2>&1 | head -5
fi
```

## Summary

**For creating the bot**: Use Telegram Web (easiest)
**For running the bot**: You don't need Telegram Desktop - your Python bot works independently!



