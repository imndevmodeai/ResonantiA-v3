# Visual Cognitive Debugger (VCD) - Quick Start Guide

## 🎯 What is the VCD?

The Visual Cognitive Debugger (VCD) is ArchE's real-time cognitive monitoring and visualization system. It provides:

- **Real-time cognitive state visualization**
- **SPR activation patterns**
- **Thought network graphs**
- **Temporal flow analysis**
- **Workflow execution monitoring**
- **IAR reflection visualization**
- **System health metrics**

## 🚀 Quick Start

### Option 1: Start VCD Bridge (Backend)

```bash
# Start the VCD Bridge WebSocket server
python3 vcd_bridge.py
```

The server will start on **WebSocket port 8765** (`ws://localhost:8765`)

### Option 2: Use the Demo Script

```bash
# Show VCD structure and capabilities
python3 demo_vcd.py --structure

# Start VCD server
python3 demo_vcd.py --server

# Connect as client (in another terminal)
python3 demo_vcd.py --client
```

### Option 3: Use Enhanced Ask_Arche Scripts

The updated `ask_arche_enhanced_v2.py` and `ask_arche_enhanced_with_tools.py` automatically:
- Connect to VCD Bridge
- Send real-time cognitive data
- Perform comprehensive VCD analysis
- Display VCD status and metrics

```bash
# Run with VCD integration
python3 ask_arche_enhanced_v2.py "Your query here"
```

## 📡 VCD Architecture

### Components

1. **VCD Bridge** (`vcd_bridge.py`)
   - WebSocket server on port 8765
   - Connects ArchE core to frontend
   - Handles real-time event broadcasting

2. **VCD Analysis Agent** (`vcd_analysis_agent.py`)
   - Comprehensive VCD system analysis
   - RISE engine integration
   - Performance metrics collection

3. **Visual Cognitive Debugger UI** (`Three_PointO_ArchE/visual_cognitive_debugger_ui.py`)
   - Main VCD server class
   - Cognitive visualization generation
   - Multiple visualization modes

4. **Frontend** (Next.js - `nextjs-chat/`)
   - Web-based UI at `http://localhost:3000`
   - Real-time WebSocket connection
   - Interactive visualizations

## 🎨 Visualization Modes

The VCD supports multiple visualization modes:

- **thought_network**: Network graph of cognitive thoughts and connections
- **spr_activation**: Visualization of SPR activation patterns
- **temporal_flow**: Time-based flow of cognitive processes
- **workflow_execution**: Real-time workflow execution visualization
- **iar_reflection**: IAR reflection data visualization
- **system_health**: System health and performance metrics

## 🔌 WebSocket Protocol

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8765');
```

### Message Types

1. **Handshake**
```json
{
  "type": "handshake",
  "client": "your_client_name",
  "timestamp": "2025-11-11T16:00:00Z"
}
```

2. **Get Cognitive State**
```json
{
  "type": "get_cognitive_state",
  "timestamp": 1699718400
}
```

3. **Get Visualization**
```json
{
  "type": "get_visualization",
  "mode": "thought_network",
  "timestamp": 1699718400
}
```

4. **Thought Process**
```json
{
  "type": "thought_process",
  "message": "Processing query...",
  "context": {},
  "timestamp": "2025-11-11T16:00:00Z"
}
```

## 📊 Integration with Ask_Arche Scripts

The enhanced `ask_arche_enhanced*` scripts now include:

✅ **Automatic VCD Connection**
- Connects to VCD Bridge on startup
- Sends handshake with feature information

✅ **Real-time Cognitive Data**
- Emits thought processes
- Sends phase transitions
- Broadcasts SPR priming events

✅ **VCD Analysis Integration**
- Performs comprehensive VCD analysis
- Sends analysis results to VCD Bridge
- Displays VCD status in reports

✅ **Zepto Compression Visualization**
- Shows Zepto compression ratios
- Displays compression metadata
- Real-time compression stats

## 🛠️ Troubleshooting

### VCD Bridge Not Starting

```bash
# Check if port 8765 is in use
lsof -i :8765

# Kill existing process if needed
kill -9 $(lsof -t -i :8765)

# Start VCD Bridge
python3 vcd_bridge.py
```

### Import Errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=$PYTHONPATH:./Three_PointO_ArchE:./Four_PointO_ArchE

# Install missing dependencies
pip install websockets
```

### Connection Refused

- Ensure VCD Bridge is running: `python3 vcd_bridge.py`
- Check WebSocket URL: `ws://localhost:8765`
- Verify firewall settings

## 📝 Example Usage

### Start VCD Bridge
```bash
python3 vcd_bridge.py
```

### In Another Terminal - Run Query with VCD
```bash
python3 ask_arche_enhanced_v2.py "Analyze the current state of AI development"
```

The VCD will automatically:
1. Connect to the bridge
2. Send real-time cognitive data
3. Perform comprehensive analysis
4. Display results in the VCD interface

## 🎯 Next Steps

1. **Start VCD Bridge**: `python3 vcd_bridge.py`
2. **Run Enhanced Query**: `python3 ask_arche_enhanced_v2.py "your query"`
3. **View Real-time Data**: Connect WebSocket client to `ws://localhost:8765`
4. **Access Frontend**: Navigate to `http://localhost:3000` (if Next.js frontend is running)

## 📚 Related Files

- `vcd_bridge.py` - Main VCD Bridge server
- `vcd_analysis_agent.py` - VCD analysis capabilities
- `demo_vcd.py` - VCD demo script
- `ask_arche_enhanced_v2.py` - Enhanced query interface with VCD
- `Three_PointO_ArchE/visual_cognitive_debugger_ui.py` - VCD UI implementation

