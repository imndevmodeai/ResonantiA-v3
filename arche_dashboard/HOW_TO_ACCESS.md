# How to Access and Interact with ArchE Dashboard

**Quick Start Guide**

---

## 🚀 Method 1: Direct File Access (Easiest)

### Step 1: Open the Frontend File

Simply open this file in your browser:
```
file:///mnt/3626C55326C514B1/Happier/arche_dashboard/frontend/index.html
```

**How to do it:**
1. Open your file manager
2. Navigate to: `/mnt/3626C55326C514B1/Happier/arche_dashboard/frontend/`
3. Right-click on `index.html`
4. Select "Open with" → Your web browser (Chrome, Firefox, etc.)

**OR** in terminal:
```bash
xdg-open /mnt/3626C55326C514B1/Happier/arche_dashboard/frontend/index.html
# Or
firefox /mnt/3626C55326C514B1/Happier/arche_dashboard/frontend/index.html
```

---

## 🌐 Method 2: HTTP Server (Recommended)

### Step 1: Start HTTP Server

```bash
cd /mnt/3626C55326C514B1/Happier/arche_dashboard/frontend
python3 -m http.server 8080
```

### Step 2: Open in Browser

Open your browser and go to:
```
http://localhost:8080
```

**Note:** If port 8080 is busy, use a different port:
```bash
python3 -m http.server 8081
# Then open: http://localhost:8081
```

---

## ✅ Verify Backend is Running

Before using the dashboard, make sure the backend is running:

```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status":"healthy","service":"ArchE Dashboard API","version":"3.5-GP"}
```

If not running, start it:
```bash
cd /mnt/3626C55326C514B1/Happier
./arche_dashboard/start_dashboard.sh
```

---

## 🎯 Dashboard Features You Can Use

Once the dashboard is open, you'll see:

### 1. **Query Interface** (Default View)
- Type your question in the text area
- Select provider (Groq/Google/Cursor)
- Toggle RISE methodology
- Click "🚀 Submit Query"
- Watch terminal output and response

### 2. **Thought Trail**
- Click "🧠 Thought Trail" in sidebar
- View all past queries and responses
- Search and filter entries
- See confidence scores

### 3. **SPR Knowledge**
- Click "🔑 SPR Knowledge" in sidebar
- Browse all 3,589 SPR definitions
- Search for specific SPRs

### 4. **Statistics**
- Click "📊 Statistics" in sidebar
- View system performance metrics
- See query statistics

### 5. **Conversation Mode**
- Click "💬 Conversation Mode" in sidebar
- Chat with ArchE in real-time
- Multi-turn conversations with context

---

## 🔧 Troubleshooting

### Dashboard shows "Disconnected"
- Check backend is running: `curl http://localhost:8000/health`
- Check port matches: Look at URL or localStorage
- Refresh the page

### Can't connect to backend
- Verify backend is on port 8000: `lsof -i :8000`
- Check firewall settings
- Try: `http://localhost:8000/api/status`

### Frontend not loading
- Make sure you're opening the HTML file or using HTTP server
- Check browser console (F12) for errors
- Verify file path is correct

---

## 📍 Quick Access URLs

**Backend:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

**Frontend:**
- Direct: `file:///mnt/3626C55326C514B1/Happier/arche_dashboard/frontend/index.html`
- HTTP: `http://localhost:8080` (after starting server)

---

**Status:** ✅ Dashboard ready to use!

