# ArchE Server Troubleshooting Guide

## Issues Encountered and Resolved

### 1. Python Command Not Found
**Problem**: `Command 'python' not found, did you mean: command 'python3'`

**Solution**: Use `python3` instead of `python` on Ubuntu/Debian systems.

```bash
# Instead of:
python arche_persistent_server.py

# Use:
python3 arche_persistent_server.py
```

### 2. Missing Dependencies
**Problem**: `ModuleNotFoundError: No module named 'websockets'`

**Solution**: Activate the virtual environment before running the server.

```bash
# Activate virtual environment
source .venv/bin/activate

# Then run the server
python3 arche_persistent_server.py
```

### 3. Port Already in Use
**Problem**: `[Errno 98] error while attempting to bind on address ('0.0.0.0', 3005): address already in use`

**Solution**: Kill the existing process or use a different port.

```bash
# Check what's using the port
lsof -i :3005

# Kill the process
kill <PID>

# Or use the startup script
python3 start_arche_server.py
```

### 4. Knowledge Scaffolding Error
**Problem**: `IARCompliantWorkflowEngine.execute_workflow() takes 2 positional arguments but 3 were given`

**Root Cause**: Method signature mismatch in ResonantiA Maestro.

**Solution**: Fixed the method calls in `Three_PointO_ArchE/resonantia_maestro.py`:

```python
# Before (incorrect):
scaffold_result = self.workflow_engine.execute_workflow(
    "knowledge_scaffolding",
    {"problem_description": query}
)

# After (correct):
scaffold_result = self.workflow_engine.run_workflow(
    "knowledge_scaffolding.json",
    {"problem_description": query}
)
```

## Current Status

✅ **Server is now working properly!**

- Knowledge Scaffolding error has been resolved
- Server starts successfully on port 3005
- WebSocket connections are working
- ResonantiA Maestro is responding correctly

## How to Start the Server

### Method 1: Direct Start (Recommended)
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Start the server
python3 arche_persistent_server.py
```

### Method 2: Using the Startup Script
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Use the startup script
python3 start_arche_server.py
```

The startup script provides:
- Port availability checking
- Automatic process cleanup
- Better error handling
- Interactive prompts for conflicts

## Testing the Server

### Test Connection
```bash
source .venv/bin/activate
python3 test_connection.py
```

### Test with Browser
Open `test_browser_connection.html` in your web browser to test the WebSocket connection.

### Test Strategic Queries
```bash
source .venv/bin/activate
python3 test_strategic_query.py
```

## Server Features

The ArchE Persistent Server now provides:

1. **WebSocket Communication**: Real-time bidirectional communication
2. **ResonantiA Maestro Integration**: Advanced cognitive orchestration
3. **Knowledge Scaffolding**: Domain expertise acquisition
4. **Tool Integration**: Web search, LLM generation, workflow execution
5. **IAR Compliance**: Integrated Action Reflection for all operations
6. **Error Recovery**: Robust error handling and recovery mechanisms

## Log Files

Server logs are saved to:
- `logs/arche_persistent_server.log` - Main server logs
- `outputs/` - Workflow execution results
- `logs/` - Additional system logs

## Troubleshooting Commands

```bash
# Check if port is in use
lsof -i :3005

# Kill process on port
kill $(lsof -ti:3005)

# Check server logs
tail -f logs/arche_persistent_server.log

# Test server health
curl -I http://localhost:3005
```

## Environment Requirements

- Python 3.8+
- Virtual environment with dependencies installed
- Required environment variables (GOOGLE_API_KEY, etc.)
- Sufficient disk space for logs and outputs

## Next Steps

1. **Monitor Performance**: Watch the logs for any performance issues
2. **Scale if Needed**: Consider load balancing for multiple clients
3. **Add Security**: Implement authentication if needed
4. **Backup Logs**: Set up log rotation and backup procedures

## Support

If you encounter any issues:

1. Check the logs in `logs/arche_persistent_server.log`
2. Verify the virtual environment is activated
3. Ensure all dependencies are installed
4. Check port availability
5. Review this troubleshooting guide

The server is now fully operational and ready for production use! 