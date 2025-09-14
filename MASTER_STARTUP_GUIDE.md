# 🚀 Master Startup Guide - ArchE Cognitive System

## Overview

The Master Startup Script (`master-startup.js`) is a comprehensive solution that handles all services in your ArchE Cognitive System with detailed logging and port management. It provides the same level of detailed output you see in your UI.

## Quick Start

### 🎯 **Primary Command for UI Testing**
```bash
# Start everything with detailed logging
npm run test-ui

# OR directly
npm run startup

# OR with the master script
node master-startup.js
```

### 🔧 **Alternative Commands**
```bash
# Start with integrated development server
npm run dev:full

# Start only ArchE backend
npm run dev:arche

# Check system status
npm run status

# Health check
npm run health
```

## What Gets Started

When you run the master startup, it automatically starts:

### 🖥️ **Frontend Services**
- **Next.js Application** (Port 3000) - Your React UI
- **WebSocket Server** (Port 3004) - Protocol server

### 🧠 **Backend Services**
- **ArchE Cognitive Server** (Port 3005) - Python cognitive engine

## Detailed Output You'll See

The master startup provides comprehensive logging similar to your UI output:

### 🔍 **System Initialization**
```
🚀 ArchE Cognitive System Master Startup
ResonantiA Protocol v3.1-CA Enhanced

🔍 Checking system prerequisites...
✅ Node.js
✅ npm
✅ Python3
✅ Virtual Environment
✅ ArchE Server
✅ Package.json
Prerequisites check: 6 passed, 0 failed
```

### 🧠 **ArchE Cognitive Backend Logs**
```
🧠 Starting ArchE Cognitive Backend...
[2025-07-24 06:10:56] ARCHE: quantum_utils.py loaded successfully for CFP.
[2025-07-24 06:10:57] ARCHE: Actual causal inference libraries loaded: DoWhy, statsmodels
[2025-07-24 06:10:58] ARCHE: Mesa library loaded successfully for ABM.
[2025-07-24 06:10:59] ARCHE: OpenAI library found.
[2025-07-24 06:10:59] ARCHE: Google Generative AI library found.
[2025-07-24 06:10:59] ARCHE: ActionRegistry initialized.
[2025-07-24 06:10:59] ARCHE: Action registry populated. Total actions: 17.
[2025-07-24 06:10:59] ARCHE: IARCompliantWorkflowEngine initialized with full vetting capabilities
[2025-07-24 06:10:59] ARCHE: ArchE Workflow CLI initialized. Found 72 workflows.
[2025-07-24 06:10:59] ARCHE: Initializing Proactive Truth Resonance Framework engine...
[2025-07-24 06:10:59] ARCHE: Google Generative AI client configured successfully with advanced capabilities.
[2025-07-24 06:10:59] ARCHE: GoogleProvider initialized successfully.
[2025-07-24 06:10:59] ARCHE: Successfully loaded 64 SPR definitions from /media/newbu/3626C55326C514B1/Happier/knowledge_graph/spr_definitions_tv.json
[2025-07-24 06:10:59] ARCHE: Proactive Truth Resonance Framework engine is ONLINE.
[2025-07-24 06:10:59] ARCHE: Initializing Adaptive Cognitive Orchestrator with Autonomous Evolution...
[2025-07-24 06:10:59] ARCHE: Initialized 3 domain controllers
[2025-07-24 06:10:59] ARCHE: Cognitive Resonant Controller System initialized
[2025-07-24 06:10:59] ARCHE: [PatternEngine] Initialized with learning capabilities
[2025-07-24 06:10:59] ARCHE: [EmergentDomainDetector] Initialized with autonomous evolution capabilities
[2025-07-24 06:10:59] ARCHE: [ACO] Adaptive Cognitive Orchestrator initialized with autonomous evolution
[2025-07-24 06:10:59] ARCHE: [ACO] Base CRCS has 3 domain controllers
[2025-07-24 06:10:59] ARCHE: [ACO] Meta-learning active: True
[2025-07-24 06:10:59] ARCHE: [ACO] Emergent Domain Detector active: threshold=0.8
[2025-07-24 06:10:59] ARCHE: Adaptive Cognitive Orchestrator with Autonomous Evolution is ONLINE.
[2025-07-24 06:10:59] ARCHE: Universal Query Enhancement System ACTIVATED - All queries will be processed through autonomous evolution.
[2025-07-24 06:10:59] ARCHE: Initializing RISE v2.0 Genesis Protocol with Utopian Upgrade...
[2025-07-24 06:10:59] ARCHE: Successfully loaded 64 SPR definitions from /media/newbu/3626C55326C514B1/Happier/knowledge_graph/spr_definitions_tv.json
[2025-07-24 06:10:59] ARCHE: Loaded chronicle from /media/newbu/3626C55326C514B1/Happier/chronicles/genesis_chronicle.json
[2025-07-24 06:10:59] ARCHE: Genesis Chronicle initialized with 5 entries and 1 cases
[2025-07-24 06:10:59] ARCHE: Utopian Solution Synthesizer initialized
[2025-07-24 06:10:59] ARCHE: IARCompliantWorkflowEngine initialized with full vetting capabilities
[2025-07-24 06:10:59] ARCHE: RISE_Orchestrator initialized with Synergistic Fusion Protocol
[2025-07-24 06:10:59] ARCHE: RISE v2.0 Genesis Protocol is ONLINE.
[2025-07-24 06:10:59] ARCHE: 🔮 Synergistic Fusion Protocol: ENABLED
[2025-07-24 06:10:59] ARCHE: 🌟 Utopian Solution Synthesizer: ENABLED
[2025-07-24 06:10:59] ARCHE: Autonomous Orchestrator initialized and ready for CEO-level operation
[2025-07-24 06:10:59] ARCHE: 🤖 Autonomous Orchestration System: ENABLED
[2025-07-24 06:10:59] ARCHE: CEO Mode: ACTIVE - Keyholder elevated to strategic oversight
```

### 🖥️ **Frontend Services**
```
🚀 Starting Next.js frontend...
✅ Next.js frontend started successfully

🔌 Starting WebSocket Server...
✅ WebSocket server started successfully
```

### 🏥 **Health Check Results**
```
🏥 Performing health check...
✅ Next.js health check passed
✅ ArchE health check passed
✅ WebSocket health check passed
```

### 📊 **Final Status Display**
```
================================================================================
📊 SYSTEM STATUS
================================================================================
NEXTJS        | RUNNING     | Uptime: 45s
ARCHE         | RUNNING     | Uptime: 42s
WEBSOCKET     | RUNNING     | Uptime: 40s
================================================================================
🌐 Frontend: http://localhost:3000
🧠 ArchE Backend: ws://localhost:3005
🔌 WebSocket: ws://localhost:3004
================================================================================
```

## Interactive Mode

Once started, the master startup provides an interactive mode:

```
🎮 Interactive Mode - Available commands:
  status    - Show system status
  health    - Perform health check
  logs      - Show recent logs
  restart   - Restart all services
  quit      - Shutdown gracefully
  help      - Show this help
```

### Interactive Commands

| Command | Description |
|---------|-------------|
| `status` | Display current system status |
| `health` | Perform health check on all services |
| `logs` | Show recent logs from all services |
| `restart` | Restart all services |
| `quit` | Gracefully shutdown all services |
| `help` | Show available commands |

## Port Management

The master startup automatically handles port conflicts:

- **Port 3000** - Next.js frontend
- **Port 3004** - WebSocket server
- **Port 3005** - ArchE cognitive backend

If any port is in use, the script will:
1. Detect the conflict
2. Kill existing processes
3. Wait for ports to be released
4. Start services cleanly

## Error Handling

The script provides comprehensive error handling:

- **Prerequisites Check**: Validates all required components
- **Port Conflicts**: Automatically resolves port issues
- **Service Failures**: Detailed error reporting
- **Graceful Shutdown**: Proper cleanup on exit
- **Health Monitoring**: Continuous service monitoring

## Testing Your UI

To test your UI with the detailed output you showed:

1. **Start the system**:
   ```bash
   npm run test-ui
   ```

2. **Wait for startup** (you'll see all the detailed logs)

3. **Open your browser** to `http://localhost:3000`

4. **Send a prompt** like the "Fog of War" query you showed

5. **Watch the detailed output** in both the terminal and your UI

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - The script automatically handles this
   - If manual intervention needed: `lsof -ti:3000,3004,3005 | xargs kill -9`

2. **Python Dependencies Missing**
   - Ensure virtual environment is activated: `source .venv/bin/activate`
   - Install missing packages: `pip install -r requirements.txt`

3. **Node.js Dependencies Missing**
   - Install dependencies: `npm install`

4. **Permission Issues**
   - Make script executable: `chmod +x master-startup.js`

### Log Levels

The script supports different log levels:

- **Detailed** (default): Full ArchE output + system logs
- **Normal**: System logs only
- **Minimal**: Status updates only

## Configuration

Edit `master-startup.js` to customize:

- Port numbers
- Timeout values
- Log levels
- Health check intervals

## Performance

The master startup is optimized for:

- **Fast Startup**: Parallel service initialization
- **Resource Efficiency**: Minimal overhead
- **Reliability**: Comprehensive error handling
- **Monitoring**: Continuous health checks

## Next Steps

1. **Test the system**: Run `npm run test-ui`
2. **Explore the UI**: Navigate to `http://localhost:3000`
3. **Send queries**: Test with various prompts
4. **Monitor logs**: Watch the detailed output
5. **Customize**: Modify configuration as needed

The master startup provides the exact level of detailed output you're seeing in your UI, making it perfect for testing and development! 