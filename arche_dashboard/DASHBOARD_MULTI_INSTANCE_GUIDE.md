# ArchE Dashboard Multi-Instance & Port Management Guide

**Version:** 3.5-GP  
**Date:** 2025-11-20  
**Status:** ✅ PRODUCTION READY

---

## 🎯 Overview

The ArchE Dashboard now supports **multiple simultaneous instances** without port conflicts or resource interference. This guide explains how the system handles:

1. **Automatic Port Selection** - Finds available ports automatically
2. **Resource Isolation** - Each instance manages its own resources
3. **Connection Management** - Proper WebSocket connection tracking
4. **Cleanup & Cleanup** - Automatic resource cleanup on disconnect

---

## 🔧 Port Management

### Automatic Port Selection

The dashboard automatically detects and uses available ports:

1. **Checks Environment Variable** - Uses `DASHBOARD_PORT` if set and available
2. **Finds Available Port** - Searches for free ports starting from 8000
3. **Tracks Used Ports** - Maintains a registry to prevent conflicts
4. **Releases on Exit** - Automatically releases ports when dashboard stops

### Port Configuration

**Environment Variable:**
```bash
export DASHBOARD_PORT=8000  # Use specific port
```

**Port Range:**
- Default: 8000
- Range: 8000-8999 (automatically finds next available)

**Port Registry:**
- Stored in: `arche_dashboard/port_config.json`
- Tracks all used ports across instances
- Automatically updated on start/stop

---

## 🚀 Starting Multiple Instances

### Instance 1 (Default Port)
```bash
cd /mnt/3626C55326C514B1/Happier
./arche_dashboard/start_dashboard.sh
# Uses port 8000 (or next available)
```

### Instance 2 (Automatic Port Selection)
```bash
# In a new terminal
cd /mnt/3626C55326C514B1/Happier
export DASHBOARD_PORT=8001  # Or let it auto-select
./arche_dashboard/start_dashboard.sh
# Automatically uses port 8001 (or next available)
```

### Instance 3+ (Continues Auto-Selection)
Each new instance automatically finds the next available port.

---

## 🔌 Frontend Connection

### Dynamic Port Detection

The frontend automatically detects the backend port:

1. **URL Parameter** - `?port=8000`
2. **LocalStorage** - Remembers last used port
3. **Default** - Falls back to 8000

### Opening Dashboard with Specific Port

```bash
# Open in browser with port parameter
file:///mnt/3626C55326C514B1/Happier/arche_dashboard/frontend/index.html?port=8000

# Or via HTTP server
cd arche_dashboard/frontend
python3 -m http.server 3000
# Then open: http://localhost:3000?port=8000
```

---

## 🛡️ Resource Isolation

### Connection Isolation

Each dashboard instance maintains:
- **Separate WebSocket connections** - No cross-instance interference
- **Independent query queues** - Queries don't mix between instances
- **Isolated processors** - Each query has its own processor instance
- **Cleanup tracking** - Resources cleaned up per connection

### Query Processing Isolation

When multiple chats/queries run simultaneously:

1. **Separate Processors** - Each query gets its own `EnhancedRealArchEProcessor`
2. **Independent Browser Instances** - Each query manages its own browser
3. **Isolated Resources** - No shared state between queries
4. **Automatic Cleanup** - Resources released when query completes

### Browser Process Management

The system ensures:
- ✅ **Automatic Cleanup** - Browser processes closed after each query
- ✅ **Orphan Prevention** - Safety net for any missed cleanup
- ✅ **Resource Tracking** - All processors tracked and cleaned up
- ✅ **Signal Handling** - Proper cleanup on SIGINT/SIGTERM

---

## 📊 Connection Management

### WebSocket Connection Tracking

The `ConnectionManager` tracks:
- **Active Connections** - List of all WebSocket connections
- **Query Mapping** - Which queries belong to which connection
- **Processor Registry** - Active processors per query
- **Resource Queues** - Output queues per query

### Connection Lifecycle

1. **Connect** - WebSocket accepted, added to active connections
2. **Query Registration** - Query ID linked to connection
3. **Processor Creation** - New processor instance created
4. **Processing** - Query executes with isolated resources
5. **Cleanup** - All resources cleaned up on completion
6. **Disconnect** - Connection removed, all queries cleaned up

---

## 🧹 Cleanup Mechanisms

### Automatic Cleanup

The system performs cleanup at multiple levels:

1. **Query Completion** - Resources cleaned up immediately
2. **Connection Disconnect** - All queries for connection cleaned up
3. **Process Exit** - Port released, all resources cleaned up
4. **Signal Handling** - Proper cleanup on termination

### Cleanup Includes

- ✅ Browser processes (Chrome/Chromium)
- ✅ Processor instances
- ✅ Output queues
- ✅ WebSocket connections
- ✅ Port reservations

---

## 🔍 Monitoring & Debugging

### Check Active Ports

```bash
# Check which ports are in use
lsof -i :8000
lsof -i :8001
lsof -i :8002

# Or use netstat
netstat -tulpn | grep :8000
```

### View Port Configuration

```bash
# Check port registry
cat arche_dashboard/port_config.json
```

### Check Active Connections

The dashboard API provides status:
```bash
curl http://localhost:8000/api/status
# Returns: connections count, active queries count
```

---

## ⚠️ Troubleshooting

### Port Already in Use

**Symptom:** Dashboard fails to start with "Address already in use"

**Solution:**
1. Check if another instance is running: `lsof -i :8000`
2. Kill the process: `kill -9 <PID>`
3. Or use a different port: `export DASHBOARD_PORT=8001`

### Multiple Instances Conflict

**Symptom:** Queries from different instances interfere

**Solution:**
- Each instance uses separate ports (automatic)
- Each instance has isolated resources (automatic)
- Ensure frontend connects to correct port

### Browser Processes Not Cleaning Up

**Symptom:** Chrome/Chromium processes accumulate

**Solution:**
- System automatically cleans up after each query
- Safety net runs on disconnect
- Manual cleanup: `pkill -f 'chrome.*--headless'`

### WebSocket Connection Issues

**Symptom:** Frontend can't connect to backend

**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify port matches: Check URL parameter or localStorage
3. Check firewall settings
4. Verify CORS is enabled (default: all origins)

---

## 📋 Best Practices

### Running Multiple Instances

1. **Use Different Ports** - Let system auto-select or set explicitly
2. **Separate Terminals** - Run each instance in its own terminal
3. **Monitor Resources** - Check CPU/memory usage
4. **Clean Shutdown** - Use Ctrl+C for graceful shutdown

### Frontend Access

1. **Bookmark with Port** - Save URL with port parameter
2. **Use localStorage** - System remembers last port
3. **Check Status** - Verify connection in dashboard header

### Resource Management

1. **Close Unused Instances** - Don't leave instances running
2. **Monitor Browser Processes** - Check for orphaned processes
3. **Regular Cleanup** - Restart instances periodically if needed

---

## 🎯 Summary

### ✅ What Works

- ✅ Multiple dashboard instances on different ports
- ✅ Automatic port conflict detection and resolution
- ✅ Isolated resources per instance and query
- ✅ Automatic cleanup of all resources
- ✅ Proper WebSocket connection management
- ✅ Browser process cleanup after each query

### 🔒 Safety Features

- ✅ Port registry prevents conflicts
- ✅ Resource tracking ensures cleanup
- ✅ Signal handling for graceful shutdown
- ✅ Safety net for orphaned processes
- ✅ Connection isolation prevents interference

---

## 📞 Support

**Issues?** Check:
1. Port configuration: `cat arche_dashboard/port_config.json`
2. Active ports: `lsof -i :8000-8999`
3. Backend logs: Console output from `start_dashboard.sh`
4. Frontend console: Browser developer tools (F12)

**Status:** 🟢 MULTI-INSTANCE SUPPORT READY

