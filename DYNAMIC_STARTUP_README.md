# ArchE Dynamic Startup System

## 🎯 **Overview**

The ArchE system now features **fully dynamic port detection and startup** that automatically adapts to your system's available ports, activates the virtual environment, and cleans up existing processes. No more hardcoded port numbers, manual configuration, or process conflicts!

## 🚀 **Quick Start**

### **One-Command Startup (Recommended)**
```bash
python start_arche_dynamic.py
```

That's it! The system will:
1. 🔍 **Automatically detect available ports**
2. 🐍 **Activate virtual environment** (.venv, venv, or env)
3. 🧹 **Clean up existing processes** (kill any running ArchE/Node.js processes)
4. 🗑️ **Free up ports** (kill processes on ports we need)
5. 🧠 **Start ArchE backend** on an available port
6. 🌐 **Start Next.js frontend** on an available port
7. 🔌 **Configure all connections** automatically
8. 📊 **Display real-time status** of all components

### **Alternative Startup Methods**

#### **Bash Script (with port detection, venv activation, and cleanup)**
```bash
./simple-startup.sh
```

#### **Manual Port Detection**
```bash
python port_detector.py
```

## 🔧 **How It Works**

### **1. Virtual Environment Detection**
The system automatically finds and activates virtual environments:
- **`.venv`** (preferred)
- **`venv`** (alternative)
- **`env`** (alternative)
- **System Python** (fallback)

### **2. Dynamic Port Detection**
The system automatically scans for available ports in these ranges:
- **Next.js Frontend**: 3000-3010
- **ArchE Backend**: 3005-3015  
- **WebSocket Server**: 3004-3014

### **3. Process Cleanup**
The system automatically cleans up before starting:
- **Kills existing ArchE processes** (Python processes running `arche_persistent_server.py`)
- **Kills existing Node.js processes** (Next.js development servers)
- **Frees up ports** by killing processes on ports we need
- **Ensures clean startup** with no conflicts

### **4. Intelligent Fallbacks**
If preferred ports are busy, the system:
- Finds the next available port in the range
- Falls back to ports 8000-9000 if needed
- Updates all configuration automatically

### **5. Automatic Configuration**
- Updates `.env` file with detected ports
- Sets environment variables for all components
- Generates connection URLs automatically
- Saves configuration to `.port_config.json`

## 📁 **New Files**

### **`port_detector.py`**
- **Purpose**: Detects available ports and generates configuration
- **Usage**: `python port_detector.py`
- **Features**: 
  - Automatic process cleanup on ports
  - Port availability checking
  - Configuration generation
- **Output**: Updates `.env` and creates `.port_config.json`

### **`start_arche_dynamic.py`**
- **Purpose**: Complete startup manager with port detection, venv activation, and process cleanup
- **Usage**: `python start_arche_dynamic.py`
- **Features**: 
  - Automatic virtual environment activation
  - Automatic port detection
  - Process cleanup and port freeing
  - Component startup and monitoring
  - Graceful shutdown
  - Real-time status display

### **Updated Files**
- **`simple-startup.sh`**: Now uses dynamic port detection, venv activation, and process cleanup
- **`arche_persistent_server.py`**: Enhanced port finding capabilities
- **`env.template`**: Removed hardcoded ports

## 🎛️ **Configuration**

### **Automatic Configuration**
The system automatically creates/updates these files:

#### **`.env`** (Auto-generated)
```bash
# Auto-detected ports
NEXTJS_PORT=3001
ARCHE_PORT=3006
WEBSOCKET_PORT=3005
WEBSOCKET_URL=ws://localhost:3006
```

#### **`.port_config.json`** (Auto-generated)
```json
{
  "ports": {
    "nextjs": 3001,
    "arche": 3006,
    "websocket": 3005
  },
  "urls": {
    "frontend": "http://localhost:3001",
    "backend": "ws://localhost:3006",
    "websocket": "ws://localhost:3005"
  }
}
```

### **Virtual Environment Setup**
The system automatically detects and activates virtual environments:

```bash
# Create virtual environment (if not exists)
python -m venv .venv

# The startup script will automatically activate it
python start_arche_dynamic.py
```

### **Manual Override (Optional)**
If you want to specify ports manually:

```bash
# Set environment variables before starting
export ARCHE_PORT=3005
export NEXTJS_PORT=3000
python start_arche_dynamic.py
```

## 🔍 **Port Detection Logic**

### **Priority Order**
1. **Environment variables** (if set)
2. **Preferred ranges** (3000-3010, 3005-3015, etc.)
3. **Fallback ranges** (8000-9000)
4. **Any available port** (last resort)

### **Virtual Environment Priority**
1. **`.venv`** (most common)
2. **`venv`** (alternative)
3. **`env`** (alternative)
4. **System Python** (fallback)

### **Process Cleanup Strategy**
1. **Kill existing ArchE processes** - Find and kill Python processes running `arche_persistent_server.py`
2. **Kill existing Node.js processes** - Find and kill Node.js processes running development servers
3. **Free up specific ports** - Kill any processes on the ports we need
4. **Wait for cleanup** - Allow time for processes to terminate
5. **Verify availability** - Check that ports are actually free

### **Conflict Resolution**
- **Port already in use**: Automatically kills process and uses the port
- **Range exhausted**: Falls back to higher port ranges
- **No ports available**: Reports error with suggestions
- **No virtual environment**: Uses system Python with warning
- **Process won't die**: Force kills with `kill -9` (Unix) or `taskkill /F` (Windows)

## 📊 **Status Monitoring**

The dynamic startup system provides real-time monitoring:

```
🎯 ArchE System Status
============================================================
🌐 Frontend: http://localhost:3001
🧠 Backend: ws://localhost:3006
🔌 WebSocket: ws://localhost:3005
🐍 Virtual Environment: /path/to/.venv
============================================================
ArchE Backend: 🟢 Running (PID: 12345)
Next.js Frontend: 🟢 Running (PID: 12346)
============================================================
Press Ctrl+C to stop all components
============================================================
```

## 🛠️ **Troubleshooting**

### **Process Cleanup Issues**
```bash
# Check what processes are running
ps aux | grep -E "(arche|node)" | grep -v grep

# Manually kill processes if needed
pkill -f "arche_persistent_server.py"
pkill -f "node.*dev"

# Check what's using ports
lsof -i :3000-3020

# Force kill processes on ports
kill -9 $(lsof -ti:3000-3020)
```

### **Virtual Environment Issues**
```bash
# Check if virtual environment exists
ls -la .venv/

# Create virtual environment if missing
python -m venv .venv

# Install dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

### **Port Detection Fails**
```bash
# Check what's using ports
lsof -i :3000-3020

# Kill processes if needed
kill -9 $(lsof -ti:3000-3020)

# Run with verbose output
python port_detector.py --verbose
```

### **Component Won't Start**
```bash
# Check prerequisites
ls arche_persistent_server.py
ls package.json

# Check Python environment
python --version
pip list | grep websockets

# Check Node.js environment
node --version
npm --version
```

### **Connection Issues**
```bash
# Test backend connection
python test_connection.py

# Check generated configuration
cat .port_config.json

# Verify environment variables
env | grep -E "(ARCHE|NEXT|WEBSOCKET|VIRTUAL_ENV)"
```

## 🎉 **Benefits**

### **For Developers**
- **Zero configuration** - Just run and go
- **Automatic venv activation** - No manual activation needed
- **No process conflicts** - Automatic cleanup of existing processes
- **No port conflicts** - Automatic resolution and port freeing
- **Multiple instances** - Can run several ArchE systems simultaneously
- **Easy testing** - Different ports for different test scenarios

### **For Deployment**
- **Environment agnostic** - Works on any system
- **Production ready** - Proper port, environment, and process management
- **Scalable** - Can handle multiple deployments
- **Reliable** - Graceful fallbacks and error handling
- **Clean restarts** - No leftover processes or port conflicts

### **For Testing**
- **Isolated environments** - Each test gets unique ports
- **Parallel execution** - No port conflicts between tests
- **Reproducible** - Consistent behavior across environments
- **Virtual environment isolation** - Proper dependency management
- **Clean state** - No interference from previous test runs

## 🔄 **Migration from Old System**

### **Old Way (Manual)**
```bash
# Had to manually activate venv, check ports, and kill processes
source .venv/bin/activate
pkill -f "arche_persistent_server.py"
pkill -f "node.*dev"
export ARCHE_PORT=3005
export NEXTJS_PORT=3000
python arche_persistent_server.py &
npm run dev &
```

### **New Way (Dynamic)**
```bash
# Just run one command
python start_arche_dynamic.py
```

## 🚀 **Advanced Usage**

### **Custom Port Ranges**
Edit `port_detector.py` to change port ranges:

```python
self.port_ranges = {
    'nextjs': (4000, 4010),      # Custom Next.js range
    'arche': (4005, 4015),       # Custom ArchE range
    'websocket': (4004, 4014),   # Custom WebSocket range
}
```

### **Custom Process Cleanup**
The system automatically cleans up these processes:
- Python processes running `arche_persistent_server.py`
- Node.js processes running development servers
- Any process on the ports we need

### **Custom Virtual Environment Path**
The system automatically detects common venv paths, but you can specify custom ones:

```bash
# Set custom venv path
export VIRTUAL_ENV=/custom/path/to/venv
python start_arche_dynamic.py
```

### **Integration with CI/CD**
```yaml
# Example GitHub Actions
- name: Setup Python
  uses: actions/setup-python@v3
  with:
    python-version: '3.9'

- name: Create virtual environment
  run: python -m venv .venv

- name: Install dependencies
  run: |
    source .venv/bin/activate
    pip install -r requirements.txt

- name: Start ArchE System
  run: python start_arche_dynamic.py
```

### **Docker Integration**
```dockerfile
# Example Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY start_arche_dynamic.py /app/
COPY port_detector.py /app/
COPY arche_persistent_server.py /app/

CMD ["python", "start_arche_dynamic.py"]
```

## 📝 **API Reference**

### **PortDetector Class**
```python
detector = PortDetector()
detector.kill_process_on_port(3005)    # Kill process on specific port
ports = detector.detect_ports()        # Detect available ports
config = detector.generate_startup_config(ports)
```

### **ArchEDynamicStartup Class**
```python
startup = ArchEDynamicStartup()
startup.find_venv()                    # Find virtual environment
startup.activate_venv_environment()    # Activate virtual environment
startup.kill_arche_processes()         # Kill existing ArchE processes
startup.kill_processes_on_ports([3005, 3000])  # Kill processes on ports
startup.detect_ports()                 # Detect available ports
startup.start_arche_backend()          # Start ArchE backend
startup.start_nextjs_frontend()        # Start Next.js frontend
```

Your ArchE system is now **truly dynamic and adaptive** with automatic virtual environment management and process cleanup! 🎉 