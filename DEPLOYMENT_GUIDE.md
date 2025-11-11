# FaceCheck Service Deployment Guide

This guide explains how to deploy the FaceCheck Flask app with Telegram bot to cloud hosting services.

## 🚀 Quick Deployment Options

### Option 1: Render.com (Recommended - Free Tier Available)

**Steps:**

1. **Create a Render account** at https://render.com
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Build Command**: `pip install -r facecheck_requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT facecheck_bot:app`
   - **Environment Variables**:
     - `FACECHECK_BOT_TOKEN`: Your Telegram bot token
     - `FACECHECK_MODE`: `both` (or `web` for web-only)
     - `PORT`: Automatically set by Render

5. **Deploy!**

Render provides:
- ✅ Free tier (with limitations)
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Automatic deployments from Git
- ✅ 24/7 uptime

**Note**: For the Telegram bot to work 24/7, you may need to run it as a separate Worker service, or use the web service with `FACECHECK_MODE=both`.

---

### Option 2: Railway.app (Great for Python Apps)

**Steps:**

1. **Create a Railway account** at https://railway.app
2. **Create a new project**
3. **Add a new service** → "Deploy from GitHub repo"
4. **Configure environment variables:**
   - `FACECHECK_BOT_TOKEN`: Your Telegram bot token
   - `FACECHECK_MODE`: `both`

5. **Railway will auto-detect Python and deploy**

Railway provides:
- ✅ $5 free credit monthly
- ✅ Automatic HTTPS
- ✅ Simple deployment
- ✅ Webhooks support

---

### Option 3: Fly.io (Good for Long-Running Services)

**Steps:**

1. **Install Fly CLI**: `curl -L https://fly.io/install.sh | sh`
2. **Login**: `fly auth login`
3. **Create app**: `fly launch`
4. **Set secrets**:
   ```bash
   fly secrets set FACECHECK_BOT_TOKEN=your_token
   fly secrets set FACECHECK_MODE=both
   ```
5. **Deploy**: `fly deploy`

Fly.io provides:
- ✅ Generous free tier
- ✅ Global edge deployment
- ✅ Automatic HTTPS
- ✅ Great for bots

---

### Option 4: Heroku (Classic Choice)

**Steps:**

1. **Install Heroku CLI**
2. **Login**: `heroku login`
3. **Create app**: `heroku create facecheck-service`
4. **Set config vars**:
   ```bash
   heroku config:set FACECHECK_BOT_TOKEN=your_token
   heroku config:set FACECHECK_MODE=both
   ```
5. **Deploy**: `git push heroku main`

**Note**: Heroku free tier was discontinued, but they have an Eco plan.

---

## 🤖 Setting Up Telegram Bot

1. **Create a bot**:
   - Message @BotFather on Telegram
   - Send `/newbot`
   - Follow instructions to name your bot
   - Copy the token provided

2. **Set the token**:
   - In your hosting service's environment variables
   - Set `FACECHECK_BOT_TOKEN` to your token

3. **Test the bot**:
   - Find your bot on Telegram
   - Send `/start`
   - Try sending a FaceCheck.ID URL

---

## 📁 File Structure

```
.
├── app.py                    # Original Flask app
├── facecheck_bot.py          # Bot + Flask integration
├── facecheck_requirements.txt # Dependencies
├── face.sh                   # Startup script (local use)
├── Procfile                  # For Heroku/Render
├── render.yaml              # Render.com config
├── runtime.txt              # Python version
└── .env.example             # Environment template
```

---

## 🔧 Local Development

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** and add your bot token:
   ```
   FACECHECK_BOT_TOKEN=your_token_here
   FACECHECK_MODE=both
   ```

3. **Install dependencies**:
   ```bash
   pip install -r facecheck_requirements.txt
   ```

4. **Run the service**:
   ```bash
   # Run both bot and web
   ./face.sh both
   
   # Or run just bot
   ./face.sh bot
   
   # Or run just web
   ./face.sh web
   ```

---

## 🌐 Using the Service

### Web Interface
- Visit `http://localhost:5000` (or your deployed URL)
- Upload JSON or use `/from-url?url=...` endpoint

### Telegram Bot
- Find your bot on Telegram
- Send a FaceCheck.ID URL: `https://facecheck.id/#search-id`
- Or use commands:
  - `/start` - Get started
  - `/help` - See help
  - `/search <search_id>` - Search by ID
  - `/url <facecheck_url>` - Search by URL

---

## 🐛 Troubleshooting

### Bot not responding?
- Check `FACECHECK_BOT_TOKEN` is set correctly
- Verify bot is running (check logs)
- Try restarting the service

### Web interface not working?
- Check `PORT` environment variable
- Verify Flask app is running
- Check firewall/security settings

### Deployment issues?
- Ensure `facecheck_requirements.txt` is in repo
- Check Python version in `runtime.txt`
- Review build logs for errors

---

## 💡 Tips

1. **Separate Workers**: For 24/7 bot operation, consider running bot as a separate worker service
2. **Monitoring**: Set up health checks on `/` endpoint
3. **Logging**: Check service logs regularly for errors
4. **Backup**: Keep your `.env` file secure and backed up

---

## 📞 Support

For issues or questions:
- Check the logs in your hosting service dashboard
- Review the code in `facecheck_bot.py` and `app.py`
- Test locally first before deploying




