# Telegram Bot Setup Guide - Complete Walkthrough

This guide will help you create a Telegram bot and get your bot token.

## 📱 Step 1: Open Telegram Desktop

1. **Locate Telegram Desktop** in your Downloads folder
2. **Double-click** to open/install it
3. **Sign in** with your phone number (you'll receive a code via SMS or Telegram app)

## 🤖 Step 2: Create Your Bot

1. **Open Telegram Desktop**
2. **Search for @BotFather** in the search bar (top of the app)
3. **Click on @BotFather** (it should have a blue checkmark ✓)
4. **Click "Start"** or send `/start`

## 🎯 Step 3: Create New Bot

1. **Send this command** to @BotFather:
   ```
   /newbot
   ```

2. **BotFather will ask for a name**:
   - Enter a display name (e.g., "My FaceCheck Bot")
   - This is what users see

3. **BotFather will ask for a username**:
   - Must end with `bot` (e.g., `myfacecheck_bot`)
   - Must be unique (if taken, try another)
   - This is the @username people use to find your bot

4. **BotFather will give you a token** that looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
   **⚠️ SAVE THIS TOKEN - You'll need it!**

## 🔑 Step 4: Save Your Bot Token

1. **Copy the token** BotFather gave you
2. **Create/edit `.env` file** in your project:
   ```bash
   cp .env.example .env
   nano .env  # or use your favorite editor
   ```

3. **Add your token**:
   ```
   FACECHECK_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   FACECHECK_MODE=both
   ```

4. **Save the file**

## ✅ Step 5: Test Your Bot

1. **Find your bot** on Telegram:
   - Search for the username you created (e.g., `@myfacecheck_bot`)
   - Click on it
   - Click "Start"

2. **Start your FaceCheck service**:
   ```bash
   ./face.sh both
   ```

3. **Send a test message** to your bot:
   - Send `/start`
   - You should get a welcome message!

## 🎨 Step 6: Customize Your Bot (Optional)

You can customize your bot with @BotFather:

### Set Bot Description:
```
/setdescription
```
Then enter a description (e.g., "Search faces using FaceCheck.ID")

### Set Bot About Text:
```
/setabouttext
```
Then enter about text (e.g., "Send me a FaceCheck.ID URL to search for faces")

### Set Bot Commands:
```
/setcommands
```
Then send:
```
start - Get started with the bot
help - Get help and instructions
search - Search by FaceCheck ID
url - Search by FaceCheck URL
```

### Set Bot Photo:
```
/setuserpic
```
Then send a photo

## 🔒 Step 7: Security Tips

1. **Never share your bot token** publicly
2. **Don't commit `.env` to git** (it's already in `.gitignore`)
3. **If token is compromised**, revoke it:
   - Message @BotFather
   - Send `/revoke`
   - Select your bot
   - Get a new token

## 🧪 Step 8: Test Complete Flow

1. **Start your service**:
   ```bash
   ./face.sh both
   ```

2. **In Telegram**, send your bot a FaceCheck.ID URL:
   ```
   https://facecheck.id/#some-search-id
   ```

3. **Bot should respond** with results!

## 🐛 Troubleshooting

### Bot not responding?
- ✅ Check `FACECHECK_BOT_TOKEN` is set in `.env`
- ✅ Check service is running (`./face.sh both`)
- ✅ Check bot is started (send `/start` in Telegram)
- ✅ Check logs for errors

### "Unauthorized" error?
- ✅ Token might be wrong - get a new one from @BotFather
- ✅ Make sure token is in `.env` file
- ✅ Restart the service after changing `.env`

### Bot doesn't see messages?
- ✅ Make sure you clicked "Start" on the bot
- ✅ Check the bot is online (green dot)
- ✅ Try sending `/start` first

## 📋 Quick Reference

**BotFather Commands:**
- `/newbot` - Create new bot
- `/token` - Get your bot's token
- `/revoke` - Revoke current token (get new one)
- `/setdescription` - Set bot description
- `/setabouttext` - Set about text
- `/setcommands` - Set command list
- `/setuserpic` - Set bot profile picture
- `/deletebot` - Delete your bot

**Your Bot Commands:**
- `/start` - Welcome message
- `/help` - Help and instructions
- `/search <id>` - Search by FaceCheck ID
- `/url <url>` - Search by FaceCheck URL

## 🎉 You're Done!

Your bot is now ready to use! Users can:
1. Find your bot on Telegram
2. Send FaceCheck.ID URLs
3. Get search results back

---

**Next Steps:**
- Set up ngrok to expose your localhost (see `setup_ngrok.sh`)
- Deploy to cloud hosting (see `DEPLOYMENT_GUIDE.md`)
- Customize bot responses in `facecheck_bot.py`



