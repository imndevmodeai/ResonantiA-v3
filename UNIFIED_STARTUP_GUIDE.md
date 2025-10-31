# 🚀 ArchE Unified Startup System

## 🎯 Problem Solved

**No more port conflicts!** This unified system eliminates the recurring issue of multiple startup scripts using different ports and creating connection problems.

## 🔧 How It Works

### 1. Centralized Port Configuration
- **Single source of truth**: `config/ports.json`
- **Automatic conflict resolution**: Port manager detects conflicts and reassigns ports
- **Environment synchronization**: All services use the same port configuration

### 2. Port Management System
- **Port availability checking**: Automatically detects which ports are in use
- **Dynamic reassignment**: Finds the next available port if conflicts exist
- **Environment file generation**: Creates `.env.local` with correct URLs

### 3. Unified Startup Process
- **Single command**: `node start-unified.js`
- **Sequential startup**: Services start in the correct order
- **Health monitoring**: Ensures each service is ready before starting the next

## 📋 Port Configuration

### Default Ports
```json
{
  "websocket": 3004,    // WebSocket Server
  "nextjs": 3000,       // Next.js UI
  "arche_python": 5000, // ArchE Python Interface
  "arche_interface": 5001
}
```

### Automatic Reassignment
If ports are in use, the system automatically reassigns:
- 3004 → 3005 (if 3004 is busy)
- 3000 → 3001 (if 3000 is busy)
- etc.

## 🚀 Quick Start

### Option 1: Unified Startup (Recommended)
```bash
# Start everything with one command
node start-unified.js
```

### Option 2: Manual Port Management
```bash
# Check and resolve port conflicts
node scripts/port-manager.js check

# Generate environment file
node scripts/port-manager.js env

# Start individual services
node scripts/port-manager.js start websocket
node scripts/port-manager.js start nextjs
```

### Option 3: Traditional Python Startup
```bash
# Still works, but now uses unified port management
python start-arche.py
```

## 🔍 Port Status Commands

```bash
# Check current port configuration
node scripts/port-manager.js

# Check port availability
node scripts/port-manager.js check

# View current configuration
cat config/ports.json

# View environment variables
cat .env.local
```

## 🛠️ Troubleshooting

### Port Conflicts
```bash
# The system automatically handles this, but you can manually check:
node scripts/port-manager.js check
```

### Service Not Starting
```bash
# Check if ports are available
ss -tlnp | grep -E "(3000|3001|3004|3005)"

# Restart with fresh port assignment
rm config/ports.json
node scripts/port-manager.js check
```

### Connection Issues
1. **Check the generated `.env.local` file**
2. **Verify the WebSocket URL matches your UI configuration**
3. **Restart the Next.js server after port changes**

## 📁 File Structure

```
config/
├── ports.json              # Centralized port configuration
scripts/
├── port-manager.js         # Port conflict resolution
├── unified-startup.js      # Unified service startup
.env.local                  # Generated environment variables
start-unified.js           # Simple startup script
```

## 🔄 Migration from Old System

### Before (Multiple Configurations)
- `next.config.js`: `ws://localhost:3001`
- `Chat.tsx`: `ws://localhost:3005`
- `webSocketServer.js`: Port 3004
- **Result**: Connection failures

### After (Unified System)
- `config/ports.json`: Single source of truth
- All services read from centralized config
- **Result**: Consistent connections

## 🎉 Benefits

1. **No More Port Conflicts**: Automatic detection and resolution
2. **Single Command Startup**: `node start-unified.js`
3. **Consistent Configuration**: All services use the same ports
4. **Easy Troubleshooting**: Clear port status and configuration
5. **Future-Proof**: New services automatically get assigned ports

## 🚨 Important Notes

- **Always use the unified startup system** for new deployments
- **Don't manually edit port numbers** in individual files
- **The system automatically handles port conflicts**
- **Environment variables are generated automatically**

## 🔧 Advanced Usage

### Custom Port Configuration
```bash
# Edit the default ports (not recommended)
nano config/ports.json

# Regenerate environment after changes
node scripts/port-manager.js env
```

### Service-Specific Startup
```bash
# Start only WebSocket server
node scripts/port-manager.js start websocket

# Start only Next.js UI
node scripts/port-manager.js start nextjs
```

### Development Mode
```bash
# Check ports without starting services
node scripts/port-manager.js check

# Generate environment for manual startup
node scripts/port-manager.js env
```

---

**🎯 This system eliminates port conflicts once and for all!** 