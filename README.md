# ArchE - ResonantiA Protocol v3.1-CA

**ArchE** is an advanced AI system implementing the **ResonantiA Protocol v3.1-CA**, designed to provide intelligent assistance through a sophisticated cognitive architecture with real-time visual debugging capabilities.

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **Google Gemini API Key** (Get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ArchE
   ```

2. **Run the setup script:**
   ```bash
   python3 setup_arche.py
   ```
   This will:
   - Check your Python version
   - Create a `.env` file from template
   - Validate all critical files
   - Check Python dependencies
   - Test system initialization

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API key:**
   ```bash
   # Edit the .env file and add your Gemini API key
   nano .env
   ```
   Replace `your_gemini_api_key_here` with your actual API key.

5. **Install Node.js dependencies:**
   ```bash
   cd nextjs-chat
   npm install
   ```

### Running the System

1. **Start the WebSocket server** (from project root):
   ```bash
   node webSocketServer.js
   ```

2. **Start the Next.js frontend** (in a new terminal):
   ```bash
   cd nextjs-chat
   npm run dev
   ```

3. **Open your browser:**
   Navigate to the URL shown by the Next.js server (typically `http://localhost:3003`)

## 🏗️ System Architecture

### Core Components

- **ResonantiA Protocol v3.1-CA**: The operational framework governing ArchE's behavior
- **IARCompliantWorkflowEngine**: Executes workflows with Integrated Action Reflection compliance
- **Proactive Truth Resonance Framework (PTRF)**: Validates information through multiple sources
- **RISE v2.0 Genesis Protocol**: Deep analysis engine for complex problem-solving
- **Adaptive Cognitive Orchestrator (ACO)**: Autonomous evolution and decision-making
- **Visual Cognitive Debugger**: Real-time interface showing ArchE's cognitive processes

### Key Features

- **Real-time Cognitive Visualization**: Watch ArchE's thoughts and SPR activations in real-time
- **WebSocket Integration**: Seamless communication between frontend and backend
- **Workflow Execution**: Execute complex workflows with IAR compliance
- **Truth Seeking**: Validate information through the PTRF
- **Autonomous Evolution**: System learns and evolves through ACO
- **Strategic Pattern Recognition**: SPR-based reasoning and knowledge management

## 📁 Project Structure

```
ArchE/
├── Three_PointO_ArchE/          # Core Python modules
│   ├── workflow_engine.py       # IAR-compliant workflow engine
│   ├── proactive_truth_system.py # PTRF implementation
│   ├── rise_orchestrator.py     # RISE v2.0 Genesis Protocol
│   ├── adaptive_cognitive_orchestrator.py # ACO system
│   └── ...
├── mastermind/
│   └── interact.py              # Main CLI interface
├── workflows/                   # Workflow definitions
│   ├── temporal_forecasting_workflow.json
│   └── creative_synthesis.json
├── knowledge_graph/             # Knowledge base
│   ├── spr_definitions_tv.json # SPR definitions
│   └── axiomatic_knowledge.json
├── chronicles/                  # System history
│   └── genesis_chronicle.json
├── nextjs-chat/                 # Visual Cognitive Debugger
│   ├── src/
│   │   ├── components/          # React components
│   │   └── hooks/               # Custom React hooks
│   └── package.json
├── webSocketServer.js           # WebSocket server
├── setup_arche.py              # Setup and validation script
├── requirements.txt            # Python dependencies
└── env.template                # Environment template
```

## 🎯 Usage Examples

### Command Line Interface

```bash
# Interactive mode
python3 mastermind/interact.py

# Direct query
python3 mastermind/interact.py "What is artificial intelligence?"

# Truth seeking mode
python3 mastermind/interact.py --truth-seek "Is the Earth round?"

# RISE analysis
python3 mastermind/interact.py --rise-execute "How to optimize supply chain logistics?"
```

### Visual Interface

1. Open the Visual Cognitive Debugger in your browser
2. Type your query in the chat interface
3. Watch real-time cognitive process visualization
4. View Thought Trail and SPR Activation nodes
5. Receive comprehensive analysis and recommendations

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.template`:

```bash
# Required
GEMINI_API_KEY=your_actual_api_key_here

# Optional
ARCHE_ENVIRONMENT=development
ARCHE_LOG_LEVEL=INFO
WEBSOCKET_PORT=3004
NEXTJS_PORT=3003
```

### Port Configuration

- **Next.js Frontend**: Port 3003 (auto-assigned if busy)
- **WebSocket Server**: Port 3004
- **ArchE Backend**: Via mastermind.interact

## 🧪 Testing

### System Validation

Run the setup script to validate your installation:

```bash
python3 setup_arche.py
```

### Live Test

Use Benchmark Query 2 (Fog of War) to test the complete system:

```
There is a rapidly developing geopolitical crisis in the South China Sea. 
Initial reports are conflicting... I need the ground truth. 
Initiate your Proactive Truth Resonance Framework... and then use your RISE engine 
to generate a predictive forecast...
```

## 🐛 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not set"**
   - Ensure your `.env` file contains a valid API key
   - Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **"Port already in use"**
   - The system will automatically try the next available port
   - Check terminal output for actual ports being used

3. **"SPR file not found"**
   - Run `python3 setup_arche.py` to validate file structure
   - Ensure `knowledge_graph/spr_definitions_tv.json` exists

4. **"Python dependencies missing"**
   - Run `pip install -r requirements.txt`
   - Check Python version (requires 3.8+)

### Debug Mode

Enable debug logging by setting in `.env`:
```
ARCHE_DEBUG_MODE=true
ARCHE_LOG_LEVEL=DEBUG
```

## 📚 Documentation

- **ResonantiA Protocol**: See `protocol/` directory
- **Critical Mandates**: See `protocol/CRITICAL_MANDATES.md`
- **Workflow Documentation**: See `docs/workflows/`
- **API Reference**: See individual module docstrings
- **Latest (v3.5‑GP Canonical)**:
  - Chronicle: `protocol/ResonantiA_Protocol_v3.5-GP_Canonical.md`
  - Specs: `protocol/specs/`
    - `contracts_and_schemas.md`
    - `protocol_events.md`
    - `execution_tiers_and_orchestrator.md`
    - `distributed_registry.md`
    - `visual_debug_bridges.md`
    - `executable_spec_parser.md`
    - `acceptance_tests.md`
    - `compliance_and_error_codes.md`

## 🤝 Contributing

1. Follow the ResonantiA Protocol guidelines
2. Ensure IAR compliance in all new features
3. Add tests for new functionality
4. Update documentation for changes
5. Follow the CRDSP (Codebase Reference and Documentation Synchronization Protocol)

## 📄 License

This project is part of the ResonantiA Protocol ecosystem and follows the same licensing terms.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Run `python3 setup_arche.py` for system validation
3. Review the logs for detailed error information
4. Check the documentation in the `protocol/` directory

---

**Status**: Active Development  
**Version**: 3.1-CA  
**ArchE Integration**: Complete  
**Live Test Ready**: Yes
