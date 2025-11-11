# Telegram Desktop Setup Guide - Step by Step

## What You Have
- File: `tsetup.6.2.4.tar.xz` in your Downloads folder
- This is the official Telegram Desktop for Linux

## Step-by-Step Installation

### Step 1: Extract the Archive

Open a terminal and run:

```bash
# Navigate to Downloads
cd ~/Downloads

# Extract the archive
tar -xf tsetup.6.2.4.tar.xz

# This will create a folder called "Telegram" with the application
```

### Step 2: Move to a Permanent Location (Optional but Recommended)

```bash
# Create a directory for Telegram (optional)
sudo mkdir -p /opt/telegram

# Move the extracted folder
sudo mv ~/Downloads/Telegram /opt/telegram/

# Make the executable... executable
sudo chmod +x /opt/telegram/Telegram/Telegram
```

### Step 3: Create a Desktop Shortcut (Optional)

```bash
# Create desktop entry
cat > ~/.local/share/applications/telegram.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Name=Telegram Desktop
Comment=Official Telegram Desktop client
Exec=/opt/telegram/Telegram/Telegram
Icon=/opt/telegram/Telegram/Telegram
Terminal=false
Type=Application
Categories=Network;InstantMessaging;
EOF

# Make it executable
chmod +x ~/.local/share/applications/telegram.desktop
```

### Step 4: Launch Telegram Desktop

**Option A: Run directly**
```bash
# If you kept it in Downloads
~/Downloads/Telegram/Telegram

# If you moved it to /opt
/opt/telegram/Telegram/Telegram
```

**Option B: Use the desktop shortcut**
- Look for "Telegram Desktop" in your applications menu
- Or double-click the desktop icon if you created one

### Step 5: Sign In to Telegram

1. **Telegram Desktop will open**
2. **Enter your phone number** (with country code, e.g., +1 for US)
3. **Click "Next"**
4. **You'll receive a code** via:
   - SMS to your phone, OR
   - Telegram app if you're already logged in elsewhere
5. **Enter the code** when prompted
6. **You're in!**

## Quick Launch Script

Create a simple script to launch Telegram easily:

```bash
# Create launch script
cat > ~/launch_telegram.sh << 'EOF'
#!/bin/bash
/opt/telegram/Telegram/Telegram &
EOF

chmod +x ~/launch_telegram.sh

# Now you can run: ~/launch_telegram.sh
```

## Next Steps: Create Your Bot

Once Telegram Desktop is running:

1. **Search for @BotFather** in Telegram
2. **Click "Start"**
3. **Send**: `/newbot`
4. **Follow the prompts** to create your bot
5. **Copy the token** BotFather gives you
6. **Save it** in your `.env` file (see TELEGRAM_BOT_SETUP.md)

## Troubleshooting

### "Permission denied" error?
```bash
chmod +x ~/Downloads/Telegram/Telegram
```

### Can't find the executable?
```bash
# List contents of extracted folder
ls -la ~/Downloads/Telegram/
```

### Want to update later?
1. Download new version from https://desktop.telegram.org/
2. Extract and replace the old folder
3. Your settings and chats are saved separately, so they'll remain

### Alternative: Install via Package Manager

If you prefer, you can also install via your package manager:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install telegram-desktop
```

**Fedora:**
```bash
sudo dnf install telegram-desktop
```

**Arch Linux:**
```bash
sudo pacman -S telegram-desktop
```

## You're Ready!

Once Telegram Desktop is running and you're logged in, you can proceed to create your bot by following the instructions in `TELEGRAM_BOT_SETUP.md`.



