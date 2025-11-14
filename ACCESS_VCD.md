# 🎨 Access the Visual Cognitive Debugger (VCD)

## ✅ VCD Bridge Status
- **Port**: 8765 (WebSocket)
- **Status**: ✅ RUNNING
- **URL**: `ws://localhost:8765`

## 🌐 Browser Access (Easiest Way!)

**I've created a browser client for you!**

### Open in Browser:
```bash
# Open this file in your browser:
file:///mnt/3626C55326C514B1/Happier/vcd_browser_client.html
```

Or if you have a web server:
```bash
# Python simple server
cd /mnt/3626C55326C514B1/Happier
python3 -m http.server 8080
# Then open: http://localhost:8080/vcd_browser_client.html
```

### What You'll See:
- ✅ Real-time connection status
- ✅ Live cognitive stream
- ✅ Thought processes
- ✅ Events and visualizations
- ✅ Message statistics
- ✅ Interactive controls

## 🔌 Other Access Methods

### 1. Terminal WebSocket Client
```bash
python3 vcd_websocket_client.py --duration 60
```

### 2. Query Interface (Automatic VCD)
```bash
python3 ask_arche_enhanced_v2.py "Your query here"
```

### 3. Next.js Frontend (Full UI)
```bash
cd nextjs-chat
npm run dev
# Open: http://localhost:3000
```

## 📊 What the VCD Shows

- **Thought Processes**: Live stream of ArchE's thinking
- **SPR Activations**: Which patterns are active
- **Cognitive Resonance**: Alignment scores
- **Temporal Dynamics**: Time-based analysis
- **Events**: Phase transitions, code execution, etc.
- **Visualizations**: Network graphs, resonance maps

## 🚀 Quick Start

1. **Open Browser Client**: 
   - Double-click `vcd_browser_client.html`
   - Or open via file:// URL
   - It will auto-connect to `ws://localhost:8765`

2. **Click "Connect"** if not auto-connected

3. **Click "Send Handshake"** to initialize

4. **Watch the cognitive stream** in real-time!

The VCD is ready to show you ArchE's cognitive processes! 🎉

