# ResonantiA Protocol v3.5-GP Dashboard System

## 🎯 Overview

The ResonantiA Protocol v3.5-GP Dashboard System provides comprehensive monitoring and control for your sandbox environment. It displays all available tools, their status, system metrics, and provides safe controls for validation and deployment.

## 🚀 Quick Start

### Option 1: Quick Start (Recommended)
```bash
cd Sandbox_v35
./quick_start_dashboard.sh
```
Then open your browser to: **http://localhost:5000**

### Option 2: Full Setup
```bash
cd Sandbox_v35
./setup_and_run_dashboard.sh
```

### Option 3: Manual Start
```bash
cd Sandbox_v35
source ../arche_env/bin/activate
python3 dashboard/web_dashboard.py
```

## 📊 Dashboard Features

### 🌐 Web Dashboard (Flask)
- **Real-time monitoring** with auto-refresh every 5 seconds
- **Beautiful responsive UI** with modern styling
- **Interactive controls** for validation and deployment
- **Export functionality** for detailed reports
- **API endpoints** for programmatic access

### 🖥️ GUI Dashboard (Tkinter)
- **Real-time charts** for system metrics
- **Interactive tabs** for different views
- **Performance monitoring** for v3.5-GP metrics
- **Control panel** for operations

## 🔧 Available Tools Categories

### Core Components
- ✅ Enhanced Workflow Engine
- ✅ Enhanced IAR Validator
- ✅ Enhanced Resonance Tracker
- ✅ Genesis Protocol
- ✅ Resonant Corrective Loop
- ✅ Autonomous Orchestration

### Analysis Tools
- ✅ Causal Inference Tool (DoWhy)
- ✅ Agent-Based Modeling (Mesa)
- ✅ Predictive Modeling
- ✅ TSP Solver
- ✅ Combat ABM

### Web & Search
- ✅ Web Search Tool
- ✅ Enhanced Perception Engine
- ✅ Google Maps Integration
- ✅ Selenium WebDriver
- ✅ WebSocket Bridge

### AI & ML
- ✅ Enhanced LLM Provider
- ✅ Prompt Manager
- ✅ Knowledge Graph Manager
- ✅ Insight Solidification Engine
- ✅ Temporal Reasoning Engine

### System Tools
- ✅ Code Executor
- ✅ Visual Cognitive Debugger
- ✅ Token Cache Manager
- ✅ Scalable Framework
- ✅ Mastermind
- ✅ Vetting Agent

## 📈 Real-time Monitoring

### System Metrics
- **CPU Usage**: Real-time CPU utilization
- **Memory Usage**: Current memory consumption
- **Disk Usage**: Storage utilization
- **Process Information**: Running processes and threads

### v3.5-GP Performance Metrics
- **Tactical Resonance**: Pattern recognition effectiveness
- **Crystallization Potential**: Knowledge solidification rate
- **Genesis Protocol Compliance**: Objective clarity and implementation resonance
- **Autonomous Orchestration Score**: Decision autonomy and context adaptation

## 🎮 Control Panel Features

### Validation
- **Run Comprehensive Validation**: Test all sandbox components
- **View Validation Results**: Detailed test results and scores
- **Deployment Readiness**: Check if ready for production deployment

### Deployment
- **Safe Deployment**: Staged deployment with automatic rollback
- **Backup Creation**: Automatic production system backup
- **Rollback Capability**: Safe rollback on deployment failure

### Export & Reporting
- **Export Reports**: Generate detailed JSON reports
- **Performance Analytics**: Historical performance data
- **Tool Status Reports**: Comprehensive tool availability reports

## 🌐 Web Dashboard Interface

### Main Dashboard
- **Tool Status Grid**: Visual status indicators for all tools
- **System Metrics**: Real-time system performance
- **Validation Score**: Overall system health score
- **Control Buttons**: Quick access to all operations

### API Endpoints
- `GET /api/data` - Get current dashboard data
- `POST /api/validate` - Run validation
- `GET /api/export` - Export report
- `POST /api/deploy` - Deploy to production

## 🛠️ Setup Scripts

### `setup_and_run_dashboard.sh`
Comprehensive setup script that:
1. Stops any running dashboard services
2. Activates the virtual environment
3. Installs missing dependencies
4. Sets up environment variables
5. Starts both GUI and Web dashboards
6. Provides status and access information

### `quick_start_dashboard.sh`
Simple script for quick testing:
1. Activates virtual environment
2. Sets up environment variables
3. Starts web dashboard only

## 📋 Usage Examples

### Start Web Dashboard
```bash
./quick_start_dashboard.sh
# Open browser to: http://localhost:5000
```

### Run Full Setup
```bash
./setup_and_run_dashboard.sh
# Access both dashboards
```

### Manual Validation
```bash
source ../arche_env/bin/activate
python3 run_sandbox.py validate
```

### Manual Deployment
```bash
source ../arche_env/bin/activate
python3 run_sandbox.py deploy
```

## 🔍 Troubleshooting

### Common Issues

#### Dashboard Won't Start
- Ensure virtual environment is activated: `source ../arche_env/bin/activate`
- Check if port 5000 is available: `netstat -tlnp | grep :5000`
- Verify Python path: `which python3`

#### Missing Dependencies
```bash
source ../arche_env/bin/activate
pip install flask matplotlib networkx psutil
```

#### Permission Issues
```bash
chmod +x setup_and_run_dashboard.sh
chmod +x quick_start_dashboard.sh
```

### Log Files
- `web_dashboard.log` - Web dashboard logs
- `gui_dashboard.log` - GUI dashboard logs
- `sandbox.log` - General sandbox logs

### Process Management
```bash
# Check running processes
ps aux | grep dashboard

# Stop all dashboards
pkill -F gui_dashboard.pid && pkill -F web_dashboard.pid

# View logs
tail -f web_dashboard.log
```

## 🎯 Key Benefits

1. **Complete Visibility**: See all tools and their status at a glance
2. **Real-time Monitoring**: Live system metrics and performance data
3. **Safe Operations**: All operations go through validation and safety checks
4. **Beautiful Interface**: Modern, responsive UI with animations
5. **Comprehensive Reporting**: Detailed reports and analytics
6. **Easy Access**: Simple scripts for quick setup and operation

## 🔗 Integration

The dashboard integrates with:
- **Sandbox Environment**: Real-time sandbox monitoring
- **Validation System**: Comprehensive validation testing
- **Deployment System**: Safe production deployment
- **Monitoring System**: System health and performance tracking

## 📞 Support

For issues or questions:
1. Check the log files for error messages
2. Verify all dependencies are installed
3. Ensure the virtual environment is properly activated
4. Check that all required tools are available

---

**🎉 Your ResonantiA Protocol v3.5-GP Dashboard is ready!**

Access the web dashboard at: **http://localhost:5000**
