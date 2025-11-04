# ⚡ ArchE Dashboard - Quick Start Card

## 🚀 Start in 3 Commands

```bash
# 1. Navigate to project
cd /mnt/3626C55326C514B1/Happier

# 2. Start dashboard backend
./arche_dashboard/start_dashboard.sh

# 3. Open frontend in browser
# Then open: file:///mnt/3626C55326C514B1/Happier/arche_dashboard/frontend/index.html
```

## 📍 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard UI** | `file:///.../arche_dashboard/frontend/index.html` | Main interface |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive docs |
| **WebSocket** | ws://localhost:8000/ws/live | Real-time updates |

## 🎯 First Steps

### 1. Check Connection
- Look for green dot in header
- Status should say "Connected"

### 2. Submit Test Query
- Go to "Query Interface" (default view)
- Type: `"Explain quantum computing"`
- Click "🚀 Submit Query"

### 3. View Thought Trail
- Click "🧠 Thought Trail" in sidebar
- See your query in timeline

### 4. Try Conversation
- Click "💬 Conversation Mode"
- Chat naturally with ArchE

## 🔧 If Something Goes Wrong

### Backend won't start?
```bash
source arche_env/bin/activate
pip install fastapi uvicorn websockets
```

### WebSocket not connecting?
```bash
# Check backend is running
curl http://localhost:8000/health
```

### Thought trail empty?
```bash
# Run a query first
python3 ask_arche_enhanced_v2.py "test"
```

## 📚 Full Documentation

See `arche_dashboard/README.md` for complete guide!

---

**Status:** ✅ ALL SYSTEMS OPERATIONAL  
**Your dashboard is ready!** 🎉

