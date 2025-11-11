# 🚀 FaceCheck Quick Start Guide

## Step-by-Step Setup (5 Minutes)

### 1️⃣ Run the Complete Setup Script

```bash
./complete_setup.sh
```

This will guide you through:
- ✅ Telegram bot creation
- ✅ Token configuration
- ✅ ngrok setup with authentication
- ✅ Dependency installation

---

### 2️⃣ Manual Setup (If You Prefer)

#### A. Create Telegram Bot

1. **Open Telegram Desktop** (from Downloads folder)
2. **Search for @BotFather**
3. **Send**: `/newbot`
4. **Follow instructions** and **copy your token**

#### B. Configure Bot Token

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your token
nano .env
# Add: FACECHECK_BOT_TOKEN=your_token_here
```

#### C. Setup ngrok with Auth

```bash
# Run setup script
./setup_ngrok.sh

# It will ask for:
# - ngrok authtoken (from https://dashboard.ngrok.com)
# - Username for basic auth
# - Password for basic auth
```

#### D. Install Dependencies

```bash
pip3 install -r facecheck_requirements.txt
```

---

### 3️⃣ Start Everything

#### Option A: Start with ngrok (Recommended)

```bash
# Terminal 1: Start FaceCheck service
./face.sh both

# Terminal 2: Start ngrok tunnel
./start_ngrok.sh
```

#### Option B: Start without ngrok (Local only)

```bash
./face.sh both
```

---

### 4️⃣ Test Your Bot

1. **Open Telegram Desktop**
2. **Search for your bot** (the username you created)
3. **Click "Start"**
4. **Send**: `/start`
5. **Send a FaceCheck.ID URL** to test!

---

## 🔐 Authentication

### ngrok Basic Auth
- Configured in `setup_ngrok.sh`
- Protects the tunnel endpoint
- Username/password set during setup

### Flask App Auth (Optional)
- Enable in `.env`: `FACECHECK_ENABLE_AUTH=true`
- Set credentials: `FACECHECK_AUTH_USER` and `FACECHECK_AUTH_PASS`
- Protects the web interface

---

## 📱 Using Your Bot

### Commands:
- `/start` - Welcome message
- `/help` - Get help
- `/search <id>` - Search by FaceCheck ID
- `/url <url>` - Search by FaceCheck URL

### Just Send URLs:
- Send any FaceCheck.ID URL
- Bot will automatically process it!

---

## 🌐 Accessing Your Service

### Local:
- Web: `http://localhost:3033`
- Bot: Find on Telegram

### Via ngrok:
- Web: `https://your-ngrok-url.ngrok.io`
- Bot: Same as local (uses polling)

---

## 🐛 Troubleshooting

### Bot not responding?
```bash
# Check service is running
./face.sh both

# Check token in .env
cat .env | grep FACECHECK_BOT_TOKEN
```

### ngrok not working?
```bash
# Re-run setup
./setup_ngrok.sh

# Or start manually
ngrok http 3033
```

### Port already in use?
```bash
# Find what's using port 3033
sudo lsof -i :3033

# Kill it or change port in app.py
```

---

## 📚 Next Steps

- **Deploy to cloud**: See `DEPLOYMENT_GUIDE.md`
- **Customize bot**: Edit `facecheck_bot.py`
- **Add features**: Extend `app.py`

---

## 🎉 You're All Set!

Your FaceCheck service is now running with:
- ✅ Telegram bot integration
- ✅ Web interface
- ✅ ngrok tunnel with authentication
- ✅ Secure access

Happy botting! 🚀



