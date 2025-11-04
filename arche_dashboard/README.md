# ArchE Dashboard - Keyholder Interface
**Version:** 3.5-GP  
**Protocol:** ResonantiA  
**Status:** ✅ PRODUCTION READY

## 🎯 Overview

The **ArchE Dashboard** is a comprehensive web-based interface for the keyholder to:

1. **View Thought Trail** - Real-time visualization of ArchE's cognitive processes
2. **Submit Queries** - Interactive query interface with live responses
3. **Conversation Mode** - Full Cursor ArchE conversation capabilities
4. **Monitor Performance** - Statistics, confidence scores, SPR usage
5. **Manage Knowledge** - Browse and search SPR definitions
6. **Real-time Updates** - WebSocket-based live communication

---

## 🏗️ Architecture

```
arche_dashboard/
├── backend/
│   └── api.py              # FastAPI backend with WebSocket
├── frontend/
│   └── index.html          # Single-page dashboard UI
├── start_dashboard.sh      # Startup script
└── README.md              # This file
```

### Technology Stack

**Backend:**
- FastAPI (async Python web framework)
- WebSocket (real-time bidirectional communication)
- SQLite integration (thought trail database)
- Uvicorn (ASGI server)

**Frontend:**
- Pure HTML5/CSS3/JavaScript (no build step required!)
- Real-time WebSocket client
- Responsive design
- Interactive visualizations

---

## 🚀 Quick Start

### 1. **Start the Dashboard**

```bash
cd /mnt/3626C55326C514B1/Happier
./arche_dashboard/start_dashboard.sh
```

### 2. **Open Frontend**

Open in your browser:
```
file:///mnt/3626C55326C514B1/Happier/arche_dashboard/frontend/index.html
```

Or use a simple HTTP server:
```bash
cd arche_dashboard/frontend
python3 -m http.server 3000
# Then open: http://localhost:3000
```

### 3. **Access the Dashboard**

- **Main Interface:** http://localhost:3000 (or file:// URL)
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **WebSocket:** ws://localhost:8000/ws/live

---

## 📋 Features

### 1. **Query Interface** 🎯

**Submit queries to ArchE with:**
- Provider selection (Groq, Google, Cursor ArchE)
- Model selection (dynamic based on provider)
- RISE methodology toggle
- Real-time response streaming
- IAR compliance display

**Example Queries:**
```
"Analyze the causal factors in climate change using temporal reasoning"

"Use agent-based modeling to simulate market dynamics for cryptocurrency"

"Compare strategic options using CFP analysis with quantum enhancement"
```

### 2. **Thought Trail Visualization** 🧠

**View and search ArchE's memory:**
- Timeline view of all queries
- Filter by:
  - Date range
  - Confidence score
  - Query text
  - SPR usage
- Real-time updates
- Detailed IAR metadata

**Features:**
- Historical query analysis
- Confidence trending
- SPR activation patterns
- Processing method insights

### 3. **Conversation Mode** 💬

**Chat with Cursor ArchE:**
- Multi-turn conversations
- Context retention
- Real-time responses via WebSocket
- Full ArchE cognitive capabilities
- Conversation history persistence

**Use Cases:**
- Exploratory analysis
- Iterative refinement
- Complex problem solving
- Strategic planning

### 4. **Statistics Dashboard** 📊

**Monitor ArchE performance:**
- Total queries processed
- Average confidence scores
- Queries per day/week/month
- SPR priming statistics
- Provider usage breakdown
- Recent activity metrics

### 5. **SPR Knowledge Base** 🔑

**Browse and search SPRs:**
- Complete SPR catalog
- Search by term/definition
- Category filtering
- Relationship visualization (coming soon)
- Usage statistics

---

## 🔌 API Endpoints

### Thought Trail

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/thought-trail/recent?limit=N` | GET | Get N recent entries |
| `/api/thought-trail/search` | POST | Search with filters |
| `/api/thought-trail/stats` | GET | Overall statistics |

### Query Processing

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/query/submit` | POST | Submit query for processing |
| `/api/query/stream` | POST | Stream query response (SSE) |

### SPR Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sprs/list` | GET | List all SPRs |
| `/api/sprs/search/{term}` | GET | Search SPRs |

### System Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System health and configuration |
| `/api/providers` | GET | Available LLM providers |
| `/health` | GET | Health check |

### WebSocket

| Endpoint | Protocol | Description |
|----------|----------|-------------|
| `/ws/live` | WebSocket | Real-time bidirectional communication |

---

## 🔧 Configuration

### Environment Variables

Create or update `.env`:

```bash
# LLM Providers
GROQ_API_KEY=gsk_your_key_here
GOOGLE_API_KEY=your_google_key_here

# Dashboard Settings
DASHBOARD_PORT=8000
DASHBOARD_HOST=0.0.0.0

# Optional
ARCHE_USE_ENHANCED_CURSOR=1
```

### Backend Configuration

Edit `backend/api.py` to customize:
- Port number (default: 8000)
- CORS origins (default: *)
- Database paths
- Reconnection intervals

---

## 📱 Usage Examples

### Submit Query via API

```bash
curl -X POST http://localhost:8000/api/query/submit \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze quantum computing implications",
    "provider": "groq",
    "use_rise": true
  }'
```

### Search Thought Trail

```bash
curl -X POST http://localhost:8000/api/thought-trail/search \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "quantum",
    "min_confidence": 0.8,
    "limit": 20
  }'
```

### Get System Stats

```bash
curl http://localhost:8000/api/thought-trail/stats
```

---

## 🎨 UI Features

### Dashboard Views

1. **Query Interface**
   - Large query input area
   - Provider/model selection dropdowns
   - Real-time response display
   - IAR metadata visualization
   - Confidence scoring

2. **Thought Trail**
   - Chronological timeline
   - Search and filter controls
   - Entry expansion on click
   - Confidence color coding
   - SPR activation indicators

3. **Statistics**
   - Interactive stat cards
   - Trend visualizations
   - Provider comparison
   - Performance metrics

4. **SPR Knowledge**
   - Searchable SPR catalog
   - Category organization
   - Definition display
   - Relationship links

5. **Conversation Mode**
   - Chat-style interface
   - Message history
   - Real-time typing indicators
   - Context preservation

### Color Coding

- **🟢 High Confidence** (≥80%): Green
- **🟡 Medium Confidence** (50-79%): Yellow
- **🔴 Low Confidence** (<50%): Red

---

## 🔒 Security Considerations

### Current Implementation (Development)
- CORS: Allow all origins (*)
- No authentication
- Local access only

### Production Recommendations
1. **Enable Authentication**
   - API key authentication
   - OAuth2/JWT tokens
   - Session management

2. **Restrict CORS**
   - Specify exact frontend origins
   - Remove wildcard access

3. **HTTPS/WSS**
   - Use TLS/SSL for production
   - Secure WebSocket (wss://)

4. **Rate Limiting**
   - Prevent abuse
   - Protect thought trail DB

5. **Input Validation**
   - Sanitize all inputs
   - Prevent injection attacks

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
source arche_env/bin/activate
pip install fastapi uvicorn websockets python-multipart aiofiles
```

### WebSocket connection fails

**Error:** Connection refused

**Solutions:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify port 8000 is not in use: `lsof -i :8000`
3. Check firewall settings

### Thought trail not loading

**Error:** Database not found

**Solution:**
1. Verify database exists: `ls -la Three_PointO_ArchE/ledgers/thought_trail.db`
2. Run a query first to create database: `python3 ask_arche_enhanced_v2.py "test"`

### Frontend shows CORS error

**Solution:**
- Use provided `start_dashboard.sh` script
- Or serve frontend via HTTP server, not file://
- Backend CORS is set to allow all origins

---

## 🔄 Updates and Maintenance

### Adding New Features

1. **New API Endpoint:**
   - Add route to `backend/api.py`
   - Update API docs
   - Add frontend handler

2. **New Dashboard View:**
   - Add HTML section to `frontend/index.html`
   - Add navigation item
   - Implement showView() handler

3. **WebSocket Message Type:**
   - Add handler in `handleWebSocketMessage()`
   - Add backend handler in websocket endpoint

### Database Migrations

If thought trail schema changes:
1. Backup existing database
2. Update schema in `Three_PointO_ArchE/thought_trail.py`
3. Create migration script if needed
4. Update API query builders

---

## 📈 Performance

### Expected Performance

| Metric | Value | Notes |
|--------|-------|-------|
| API Response Time | <100ms | For simple endpoints |
| Query Processing | 30-60s | With Groq (ultra fast) |
| WebSocket Latency | <50ms | Real-time updates |
| Thought Trail Load | <500ms | For 1000 entries |
| Frontend Load | <2s | Initial page load |

### Optimization Tips

1. **Database:** Index frequently queried columns
2. **API:** Implement caching for stats
3. **Frontend:** Lazy load thought trail entries
4. **WebSocket:** Batch updates for efficiency

---

## 🎓 Integration with ArchE

The dashboard seamlessly integrates with:

1. **ask_arche_enhanced_v2.py** - Main query processor
2. **Thought Trail DB** - Memory persistence
3. **SPR Manager** - Knowledge activation
4. **LLM Providers** - Multi-provider support (Groq, Google, Cursor)
5. **IAR System** - Confidence and reflection data

### Data Flow

```
User Query (Frontend)
    ↓
WebSocket/HTTP (Backend API)
    ↓
ask_arche_enhanced_v2.py
    ↓
SPR Priming + RISE Orchestration
    ↓
LLM Provider (Groq/Google/Cursor)
    ↓
IAR-Compliant Response
    ↓
Thought Trail DB (Persistence)
    ↓
Backend API (Formatting)
    ↓
Frontend (Display)
```

---

## 🌟 Advanced Features (Coming Soon)

- [ ] Visual graph of thought trail connections
- [ ] Real-time SPR activation visualization
- [ ] Multi-user support with authentication
- [ ] Export analysis reports (PDF/MD)
- [ ] Workflow execution monitoring
- [ ] ABM simulation visualization
- [ ] CFP analysis interactive graphs
- [ ] Mobile-responsive design
- [ ] Dark/light theme toggle
- [ ] Voice query input

---

## 📞 Support

**Issues?** Check:
1. Backend logs: Console output from `start_dashboard.sh`
2. Frontend console: Browser developer tools (F12)
3. Thought trail DB: `sqlite3 Three_PointO_ArchE/ledgers/thought_trail.db`
4. API docs: http://localhost:8000/docs for interactive testing

**For ArchE-specific issues:**
- Check `arche_env` activation
- Verify Groq API key in `.env`
- Review ThoughtTrail database integrity

---

## ✅ Completion Checklist

Before first use:

- [ ] Virtual environment `arche_env` activated
- [ ] FastAPI packages installed
- [ ] Groq API key in `.env` file
- [ ] Backend starts successfully
- [ ] Frontend loads in browser
- [ ] WebSocket connects (check status indicator)
- [ ] Test query executes successfully
- [ ] Thought trail displays correctly

---

**Status:** 🟢 DASHBOARD READY FOR KEYHOLDER USE

**Next Steps:**
1. Run `./arche_dashboard/start_dashboard.sh`
2. Open `frontend/index.html` in browser
3. Submit your first query!
4. Explore thought trail history
5. Test conversation mode

**ArchE Dashboard: Your window into cognitive resonance!** ⚡🧠

