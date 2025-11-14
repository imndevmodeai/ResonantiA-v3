# 🎨 Visual Cognitive Debugger (VCD) - Visual Access Guide

## 🚀 Quick Access

### VCD Bridge Status
- **WebSocket Server**: `ws://localhost:8765`
- **Status**: ✅ Running (PID shown in process list)
- **Purpose**: Backend that connects ArchE core to frontend

### Frontend Access Options

#### Option 1: Next.js Web Interface (Recommended)
```bash
cd nextjs-chat
npm run dev
```
Then open: **http://localhost:3000**

#### Option 2: WebSocket Client (Terminal)
```bash
python3 vcd_websocket_client.py --duration 60
```

#### Option 3: Integrated Query Interface
```bash
python3 ask_arche_enhanced_v2.py "Your query here"
```
This automatically connects to VCD and shows real-time data.

## 📊 VCD Components Visualization

### 1. **VCD Bridge** (Backend)
```
┌─────────────────────────────────────────┐
│         VCD Bridge Server              │
│         ws://localhost:8765              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  WebSocket Handler               │  │
│  │  - Client connections            │  │
│  │  - Message routing               │  │
│  │  - Event broadcasting            │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  ArchE Core Integration          │  │
│  │  - RISE Orchestrator             │  │
│  │  - ACO (Adaptive Cognitive)      │  │
│  │  - SPR Manager                   │  │
│  │  - ThoughtTrail                  │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### 2. **Visual Cognitive Debugger UI** (Core)
```
┌─────────────────────────────────────────┐
│   VisualCognitiveDebugger              │
│                                         │
│  Visualization Modes:                  │
│  ├─ Real-time Monitoring              │
│  ├─ Cognitive Resonance Map           │
│  ├─ Temporal Dynamics View           │
│  ├─ Implementation Resonance Trace   │
│  ├─ Pattern Crystallization Display   │
│  ├─ Mandate Compliance Dashboard      │
│  ├─ Risk Assessment Visualization    │
│  ├─ Collective Intelligence Network   │
│  ├─ Thought Trail Visualization      │
│  └─ SPR Activation Monitoring        │
└─────────────────────────────────────────┘
```

### 3. **Next.js Frontend** (Web UI)
```
┌─────────────────────────────────────────┐
│   http://localhost:3000                 │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Chat Interface                  │  │
│  │  - Message list                  │  │
│  │  - Real-time updates             │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Canvas Visualization            │  │
│  │  - Thought network graph         │  │
│  │  - SPR activation patterns       │  │
│  │  - Temporal flow                 │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Protocol Flow                   │  │
│  │  - Workflow execution            │  │
│  │  - Phase transitions             │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 🎯 What You'll See in the VCD

### Real-Time Cognitive Data
- **Thought Processes**: Live stream of ArchE's thinking
- **SPR Activations**: Which SPRs are being used
- **Cognitive Resonance**: Alignment scores
- **Temporal Dynamics**: Time-based analysis
- **Mandate Compliance**: 13 mandates status

### Visualizations
- **Thought Network Graph**: Nodes and edges showing cognitive connections
- **SPR Activation Heatmap**: Which patterns are active
- **Temporal Timeline**: Cognitive events over time
- **Resonance Maps**: Visual representation of cognitive alignment
- **Workflow Execution**: Real-time workflow visualization

### Interactive Features
- **Drill-down**: Click nodes to see details
- **Filter**: Filter by SPR, time, or type
- **Search**: Search through thought history
- **Export**: Export visualizations as images

## 🔌 Connection Flow

```
User Query
    ↓
ask_arche_enhanced_v2.py
    ↓
VCD Integration
    ├─→ Connects to VCD Bridge (ws://localhost:8765)
    ├─→ Sends handshake
    ├─→ Emits thought processes
    ├─→ Sends phase transitions
    └─→ Broadcasts cognitive state
    ↓
VCD Bridge
    ├─→ Receives from ArchE core
    ├─→ Processes events
    └─→ Broadcasts to all clients
    ↓
Frontend (Next.js)
    ├─→ Receives WebSocket messages
    ├─→ Updates UI in real-time
    └─→ Renders visualizations
```

## 📱 Access Methods

### Method 1: Web Browser (Best Visual Experience)
1. Start VCD Bridge: `python3 vcd_bridge.py &`
2. Start Next.js: `cd nextjs-chat && npm run dev`
3. Open browser: `http://localhost:3000`
4. You'll see:
   - Chat interface
   - Real-time cognitive stream
   - Interactive visualizations
   - Thought network graphs

### Method 2: Terminal WebSocket Client
1. Start VCD Bridge: `python3 vcd_bridge.py &`
2. Run client: `python3 vcd_websocket_client.py --duration 60`
3. You'll see:
   - Rich formatted terminal output
   - Real-time cognitive data
   - Thought processes
   - Events and visualizations

### Method 3: Integrated Query (Automatic)
1. Run: `python3 ask_arche_enhanced_v2.py "Your query"`
2. VCD automatically:
   - Connects to bridge
   - Sends cognitive data
   - Displays VCD status
   - Shows real-time updates

## 🎨 Visual Features

### Cognitive Resonance Map
```
    [High Resonance]
         │
    ┌────┴────┐
    │  SPR A  │───[Strong Connection]
    └────┬────┘
         │
    ┌────┴────┐
    │  SPR B  │───[Medium Connection]
    └────┬────┘
         │
    [Low Resonance]
```

### Temporal Dynamics View
```
Time ──────────────────────────────────────>
     │
     ├─ Phase 1: Query Analysis
     │
     ├─ Phase 2: SPR Priming (228 SPRs)
     │
     ├─ Phase 3: Cognitive Synthesis
     │
     └─ Phase 4: Response Generation
```

### SPR Activation Monitoring
```
Active SPRs: 228
├─ CognitiveresonancE: ⚡ ACTIVE
├─ TemporalDynamiX: ⚡ ACTIVE
├─ ImplementationresonancE: ⚡ ACTIVE
├─ ZeptoSPR: ⚡ ACTIVE
└─ ... (224 more)
```

## 🚀 Quick Start Commands

```bash
# Terminal 1: Start VCD Bridge
python3 vcd_bridge.py

# Terminal 2: Start Next.js Frontend
cd nextjs-chat && npm run dev

# Terminal 3: Run Query with VCD
python3 ask_arche_enhanced_v2.py "Show me the VCD in action"

# Or use WebSocket client
python3 vcd_websocket_client.py --duration 60
```

## 📊 Current Status

✅ **VCD Bridge**: Running on port 8765
✅ **WebSocket Protocol**: Active
✅ **ArchE Integration**: Connected
✅ **Real-time Monitoring**: Enabled
✅ **Visualization Modes**: 10 modes available

## 🎯 Next Steps

1. **Open Browser**: Navigate to `http://localhost:3000` (if Next.js is running)
2. **Run Query**: Use `ask_arche_enhanced_v2.py` to see VCD in action
3. **Watch Terminal**: Use `vcd_websocket_client.py` for terminal visualization
4. **Explore**: Try different queries to see various VCD visualizations

The VCD is ready to show you ArchE's cognitive processes in real-time! 🎉

