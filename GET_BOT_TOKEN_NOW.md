# 🚀 GET YOUR TELEGRAM BOT TOKEN - STEP BY STEP

## ⚡ FASTEST METHOD: Telegram Web (Recommended)

### Step 1: Open Telegram Web
1. Open your web browser (Chrome, Firefox, etc.)
2. Go to: **https://web.telegram.org**
3. You'll see a QR code or login screen

### Step 2: Log In
1. Enter your **phone number** (with country code, e.g., +1 for US)
2. Click **"Next"**
3. You'll receive a **code** via:
   - SMS to your phone, OR
   - Telegram app if you're already logged in
4. Enter the **code** when prompted
5. You're logged in!

### Step 3: Find BotFather
1. In the search bar at the top, type: **@BotFather**
2. Click on **@BotFather** (it has a blue checkmark ✓)
3. Click **"Start"** button (or send `/start`)

### Step 4: Create Your Bot
1. Type this command: **`/newbot`**
2. Press **Enter**

### Step 5: Name Your Bot
1. BotFather will ask: **"Alright, a new bot. How are we going to call it? Please choose a name for your bot."**
2. Type a name (e.g., **"My FaceCheck Bot"**)
3. Press **Enter**

### Step 6: Choose Username
1. BotFather will ask: **"Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot."**
2. Type a username that:
   - Ends with `bot` (e.g., `myfacecheck_bot`)
   - Is unique (if taken, try another)
3. Press **Enter**

### Step 7: Get Your Token! 🎉
1. BotFather will give you a message like:
   ```
   Done! Congratulations on your new bot. You will find it at t.me/your_bot_username. 
   Use this token to access the HTTP API:
   
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
   
   Keep your token secure and store it safely, it can be used by anyone to control your bot.
   ```

2. **COPY THAT TOKEN!** It looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890`

### Step 8: Save Your Token
Run this command in your terminal:

```bash
# Create .env file if it doesn't exist
cp .env.example .env 2>/dev/null || touch .env

# Add your token (replace YOUR_TOKEN_HERE with the actual token)
echo "FACECHECK_BOT_TOKEN=YOUR_TOKEN_HERE" >> .env
echo "FACECHECK_MODE=both" >> .env
```

**OR** edit the file manually:
```bash
nano .env
```

Add these lines:
```
FACECHECK_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
FACECHECK_MODE=both
```

Save and exit (Ctrl+X, then Y, then Enter)

---

## 📱 ALTERNATIVE: Using Telegram Desktop

If Telegram Desktop is working on your screen:

1. **Open Telegram Desktop** (the window should be visible)
2. **Click the search bar** at the top
3. **Type**: `@BotFather`
4. **Click on @BotFather**
5. **Click "Start"**
6. **Follow Steps 4-8 above** (same process!)

---

## ✅ VERIFY YOUR TOKEN

After saving your token, test it:

```bash
# Check if token is saved
cat .env | grep FACECHECK_BOT_TOKEN

# Start your bot
./face.sh both
```

You should see:
```
🤖 Telegram Bot: ENABLED
🚀 Starting FaceCheck Service...
```

---

## 🎯 QUICK COPY-PASTE COMMANDS

After you get your token, run these:

```bash
# 1. Create .env file
cp .env.example .env 2>/dev/null || touch .env

# 2. Add your token (REPLACE YOUR_TOKEN with actual token!)
echo "FACECHECK_BOT_TOKEN=YOUR_TOKEN" > .env
echo "FACECHECK_MODE=both" >> .env

# 3. Verify it's saved
cat .env

# 4. Start your bot
./face.sh both
```

---

## 🆘 TROUBLESHOOTING

### "Token not found" error?
- Make sure you copied the ENTIRE token (it's long!)
- Check there are no spaces before/after the token
- Verify the `.env` file exists: `ls -la .env`

### Bot not responding?
- Make sure `./face.sh both` is running
- Check the token is correct in `.env`
- Try sending `/start` to your bot on Telegram

### Can't find @BotFather?
- Make sure you typed exactly: `@BotFather`
- Look for the blue checkmark ✓
- Try refreshing Telegram Web

---

## 🎉 YOU'RE DONE!

Once you have the token saved in `.env`, your bot is ready to use!

**Test it:**
1. Find your bot on Telegram (search for the username you created)
2. Click "Start"
3. Send `/start` - you should get a welcome message!



