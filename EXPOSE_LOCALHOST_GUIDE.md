# Exposing Localhost to the Internet - Complete Guide

This guide shows you how to expose your local Flask app to the internet for testing, webhooks, or sharing.

## 🚀 Quick Options (Ranked by Ease)

### Option 1: ngrok (Most Popular - Recommended)

**Why**: Easiest, most reliable, free tier available, great for Telegram webhooks

**Installation**:
```bash
# Linux/Mac
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Or download from https://ngrok.com/download
# Or use snap: sudo snap install ngrok
```

**Usage**:
```bash
# 1. Sign up at https://ngrok.com (free)
# 2. Get your authtoken from dashboard
ngrok config add-authtoken YOUR_AUTH_TOKEN

# 3. Expose your Flask app (port 5000)
ngrok http 5000

# Or for your FaceCheck app (port 3033)
ngrok http 3033
```

**What you get**:
- Public URL like: `https://abc123.ngrok.io`
- HTTPS automatically enabled
- Web interface at `http://127.0.0.1:4040` to see requests
- Free tier: 1 tunnel, random URLs
- Paid: Custom domains, reserved URLs

**For Telegram Webhooks**:
```bash
# Expose your webhook endpoint
ngrok http 5000

# Then set webhook (if using webhooks instead of polling)
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://abc123.ngrok.io/webhook"
```

---

### Option 2: Cloudflare Tunnel (cloudflared) - Free & Fast

**Why**: Free, fast, no signup required, unlimited tunnels

**Installation**:
```bash
# Linux
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Or use package manager
# Ubuntu/Debian
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

**Usage**:
```bash
# Simple one-liner (no signup needed!)
cloudflared tunnel --url http://localhost:5000

# For your FaceCheck app
cloudflared tunnel --url http://localhost:3033
```

**What you get**:
- Public URL like: `https://random-words-1234.trycloudflare.com`
- HTTPS automatically
- No account needed for basic use
- Free forever

---

### Option 3: localtunnel - Simple & Free

**Why**: Very simple, no installation needed (npm), good for quick tests

**Installation**:
```bash
# Requires Node.js
npm install -g localtunnel

# Or use npx (no install needed)
npx localtunnel --port 5000
```

**Usage**:
```bash
# Basic usage
lt --port 5000

# With custom subdomain (requires free account)
lt --port 5000 --subdomain myfacecheck
```

**What you get**:
- Public URL like: `https://random-name.loca.lt`
- Free, simple
- Can be unstable on free tier

---

### Option 4: localhost.run - SSH-Based (No Install)

**Why**: No installation, uses SSH you already have

**Usage**:
```bash
# Simple - just SSH!
ssh -R 80:localhost:5000 serveo.net

# Or with custom subdomain
ssh -R myfacecheck:80:localhost:5000 serveo.net
```

**What you get**:
- Public URL like: `https://myfacecheck.serveo.net`
- No installation needed
- Uses your existing SSH

---

### Option 5: serveo.net - SSH Alternative

**Usage**:
```bash
ssh -R 80:localhost:5000 serveo.net
```

---

## 🎯 For Your FaceCheck App Specifically

### Quick Start with ngrok:

```bash
# 1. Install ngrok (see above)

# 2. Start your FaceCheck app
./face.sh web
# Or if running on different port
python3 app.py  # Runs on port 3033

# 3. In another terminal, expose it
ngrok http 3033  # or 5000 if you changed the port

# 4. You'll get a URL like:
# Forwarding: https://abc123.ngrok.io -> http://localhost:3033
```

### Quick Start with Cloudflare Tunnel:

```bash
# 1. Start your app
./face.sh web

# 2. Expose it (in another terminal)
cloudflared tunnel --url http://localhost:3033

# 3. You'll get a URL immediately
```

---

## 🔧 Advanced: Persistent Tunnel with ngrok

For production-like testing, you can configure ngrok to always use the same URL:

```yaml
# ~/.ngrok2/ngrok.yml
version: "2"
authtoken: YOUR_TOKEN
tunnels:
  facecheck:
    addr: 3033
    proto: http
    subdomain: myfacecheck  # Requires paid plan
```

Then run:
```bash
ngrok start facecheck
```

---

## 📱 For Telegram Bot Webhooks

If you want to use webhooks instead of polling (better for production):

### 1. Expose your localhost:
```bash
ngrok http 5000
```

### 2. Set webhook URL:
```bash
# Get your ngrok URL (e.g., https://abc123.ngrok.io)
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://abc123.ngrok.io/webhook"
```

### 3. Update your bot code to handle webhooks:
```python
# In facecheck_bot.py, instead of polling:
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    application.process_update(update)
    return 'OK'
```

---

## 🛡️ Security Considerations

1. **Temporary URLs**: These are for testing only. Don't use in production.
2. **HTTPS**: All these tools provide HTTPS automatically.
3. **Rate Limiting**: Free tiers have rate limits.
4. **Access Control**: Consider adding basic auth for sensitive apps.

### Add Basic Auth (Optional):
```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == "admin" and password == "secret"

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')
```

---

## 🎯 Recommended Setup for FaceCheck

**For Development/Testing**:
```bash
# Use Cloudflare Tunnel (easiest, no signup)
cloudflared tunnel --url http://localhost:3033
```

**For Production/Stable Testing**:
```bash
# Use ngrok with authtoken (more stable)
ngrok http 3033
```

**For Telegram Webhooks**:
```bash
# Use ngrok (best webhook support)
ngrok http 5000
# Then set webhook URL in Telegram
```

---

## 📊 Comparison Table

| Tool | Free | Setup | Stability | Best For |
|------|------|-------|-----------|----------|
| **ngrok** | ✅ | Easy | ⭐⭐⭐⭐⭐ | Production testing, webhooks |
| **cloudflared** | ✅ | Very Easy | ⭐⭐⭐⭐ | Quick testing, no signup |
| **localtunnel** | ✅ | Easy | ⭐⭐⭐ | Quick demos |
| **localhost.run** | ✅ | Very Easy | ⭐⭐⭐ | SSH users, simple needs |
| **serveo** | ✅ | Very Easy | ⭐⭐ | SSH users |

---

## 🚀 Quick Commands Cheat Sheet

```bash
# ngrok
ngrok http 3033

# Cloudflare Tunnel
cloudflared tunnel --url http://localhost:3033

# localtunnel
npx localtunnel --port 3033

# localhost.run
ssh -R 80:localhost:3033 serveo.net

# serveo
ssh -R myapp:80:localhost:3033 serveo.net
```

---

## 💡 Pro Tips

1. **Keep ngrok running**: Use `screen` or `tmux` to keep tunnel alive
   ```bash
   screen -S ngrok
   ngrok http 3033
   # Press Ctrl+A then D to detach
   ```

2. **Auto-restart on disconnect**: Use a simple script
   ```bash
   # restart_ngrok.sh
   #!/bin/bash
   while true; do
       ngrok http 3033
       sleep 5
   done
   ```

3. **Multiple ports**: Expose multiple services
   ```bash
   # Terminal 1
   ngrok http 3033
   
   # Terminal 2  
   ngrok http 5000 --region eu
   ```

4. **Inspect traffic**: ngrok web UI at `http://127.0.0.1:4040`

---

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Find what's using the port
sudo lsof -i :3033
# Kill it
kill -9 <PID>
```

**Connection refused?**
- Make sure your Flask app is running
- Check the port matches (3033 or 5000)
- Verify firewall isn't blocking

**ngrok not working?**
```bash
# Check authtoken
ngrok config check

# Reset config
rm ~/.ngrok2/ngrok.yml
ngrok config add-authtoken YOUR_TOKEN
```

---

## 📚 Resources

- **ngrok**: https://ngrok.com/docs
- **Cloudflare Tunnel**: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **localtunnel**: https://github.com/localtunnel/localtunnel

---

**Recommendation**: Start with **Cloudflare Tunnel** for quick testing, then use **ngrok** for more stable/production-like testing.



