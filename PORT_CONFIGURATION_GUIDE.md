# ArchE System Port Configuration Guide

## Overview

This guide explains how to configure ports for the ArchE system and the changes made to eliminate hardcoded port numbers.

## 🎯 **Problem Solved**

Previously, the ArchE system had hardcoded port numbers throughout the codebase, which caused connection failures when ports were already in use. The system would try to start on ports like 3000, 3004, 3005, but if those were occupied, it would fail to connect properly.

## ✅ **Changes Made**

### 1. **Environment Variable Configuration**

All port numbers are now configurable through environment variables:

```bash
# ArchE Backend Server
ARCHE_PORT=3005

# Next.js Frontend
NEXTJS_PORT=3000

# WebSocket Server
WEBSOCKET_PORT=3004

# WebSocket URL (auto-generated from ARCHE_PORT)
WEBSOCKET_URL=ws://localhost:3005
```

### 2. **Files Updated**

#### **Backend Files:**
- `arche_persistent_server.py` - Now uses `ARCHE_PORT` environment variable
- `start_arche_server.py` - Now uses `ARCHE_PORT` environment variable

#### **Frontend Files:**
- `next.config.js` - Uses `WEBSOCKET_URL` and `ARCHE_PORT` environment variables
- `nextjs-chat/src/hooks/useWebSocket.ts` - Uses `NEXT_PUBLIC_WEBSOCKET_URL` and `NEXT_PUBLIC_ARCHE_PORT`
- `nextjs-chat/src/components/Chat.tsx` - Uses environment variables for WebSocket connection

#### **Test Files:**
- `test_strategic_query.py` - Uses `WEBSOCKET_URL` and `ARCHE_PORT` environment variables
- `test_message_flow.py` - Uses `WEBSOCKET_URL` and `ARCHE_PORT` environment variables
- `test_connection.py` - Uses `WEBSOCKET_URL` and `ARCHE_PORT` environment variables
- `test_frontend_connection.html` - Uses configurable WebSocket URL
- `test_browser_connection.html` - Uses configurable WebSocket URL

#### **Configuration Files:**
- `env.template` - Added `ARCHE_PORT` and `ARCHE_HOST` configuration
- `simple-startup.sh` - Now loads environment variables and uses configurable ports

## 🚀 **How to Use**

### **Option 1: Environment File (Recommended)**

1. Copy the environment template:
   ```bash
   cp env.template .env
   ```

2. Edit `.env` and set your desired ports:
   ```bash
   # ArchE Backend Server Configuration
   ARCHE_PORT=3005
   ARCHE_HOST=localhost

   # WebSocket Server Configuration
   WEBSOCKET_PORT=3004
   WEBSOCKET_HOST=localhost

   # Next.js Frontend Configuration
   NEXTJS_PORT=3000
   NEXTJS_HOST=localhost
   ```

3. Start the system:
   ```bash
   ./simple-startup.sh
   ```

### **Option 2: Environment Variables**

Set environment variables directly:

```bash
export ARCHE_PORT=3005
export NEXTJS_PORT=3000
export WEBSOCKET_PORT=3004
export WEBSOCKET_URL=ws://localhost:3005

# Then start your components
python arche_persistent_server.py
npm run dev
```

### **Option 3: Command Line Override**

Override ports when starting individual components:

```bash
# Start ArchE backend on custom port
ARCHE_PORT=3006 python arche_persistent_server.py

# Start Next.js on custom port
NEXTJS_PORT=3001 npm run dev
```

## 🔧 **Configuration Options**

### **Default Ports**
- **ArchE Backend**: 3005
- **Next.js Frontend**: 3000
- **WebSocket Server**: 3004

### **Environment Variables**
- `ARCHE_PORT` - ArchE backend server port
- `ARCHE_HOST` - ArchE backend server host
- `NEXTJS_PORT` - Next.js frontend port
- `NEXTJS_HOST` - Next.js frontend host
- `WEBSOCKET_PORT` - WebSocket server port
- `WEBSOCKET_HOST` - WebSocket server host
- `WEBSOCKET_URL` - Full WebSocket URL (auto-generated if not set)

### **Frontend Environment Variables**
- `NEXT_PUBLIC_WEBSOCKET_URL` - WebSocket URL for client-side
- `NEXT_PUBLIC_ARCHE_PORT` - ArchE port for client-side

## 🛠️ **Troubleshooting**

### **Port Already in Use**
If you get "port already in use" errors:

1. **Check what's using the port:**
   ```bash
   lsof -i :3005
   ```

2. **Kill the process:**
   ```bash
   kill -9 $(lsof -ti:3005)
   ```

3. **Or use a different port:**
   ```bash
   export ARCHE_PORT=3006
   python arche_persistent_server.py
   ```

### **Connection Issues**
If frontend can't connect to backend:

1. **Check environment variables:**
   ```bash
   echo $ARCHE_PORT
   echo $WEBSOCKET_URL
   ```

2. **Verify backend is running:**
   ```bash
   curl http://localhost:3005
   ```

3. **Check WebSocket connection:**
   ```bash
   python test_connection.py
   ```

### **Frontend Can't Connect**
If the frontend shows connection errors:

1. **Check Next.js environment:**
   ```bash
   # In your .env file
   NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:3005
   NEXT_PUBLIC_ARCHE_PORT=3005
   ```

2. **Restart Next.js:**
   ```bash
   npm run dev
   ```

## 📋 **Best Practices**

### **1. Use Environment Files**
Always use `.env` files for configuration rather than hardcoding values.

### **2. Consistent Port Ranges**
Use consistent port ranges for different environments:
- **Development**: 3000-3010
- **Staging**: 4000-4010
- **Production**: 5000-5010

### **3. Port Validation**
The startup script now validates ports before starting services.

### **4. Graceful Fallbacks**
All components have sensible defaults if environment variables aren't set.

## 🔄 **Migration from Hardcoded Ports**

If you have existing scripts or documentation with hardcoded ports:

1. **Replace hardcoded URLs:**
   ```bash
   # Old
   ws://localhost:3005
   
   # New
   ws://localhost:${ARCHE_PORT:-3005}
   ```

2. **Update documentation:**
   ```bash
   # Old
   http://localhost:3000
   
   # New
   http://localhost:${NEXTJS_PORT:-3000}
   ```

3. **Update test scripts:**
   ```bash
   # Old
   python test_connection.py
   
   # New
   ARCHE_PORT=3005 python test_connection.py
   ```

## ✅ **Verification**

To verify your configuration is working:

1. **Start the system:**
   ```bash
   ./simple-startup.sh
   ```

2. **Check all services are running:**
   ```bash
   lsof -i :3000  # Next.js
   lsof -i :3005  # ArchE
   lsof -i :3004  # WebSocket
   ```

3. **Test connections:**
   ```bash
   python test_connection.py
   python test_strategic_query.py
   ```

4. **Access the frontend:**
   - Open `http://localhost:3000` (or your configured port)
   - Check that WebSocket connection is established

## 🎉 **Benefits**

- **No more port conflicts** - System automatically uses available ports
- **Flexible deployment** - Easy to deploy on different environments
- **Better testing** - Can run multiple instances with different ports
- **Production ready** - Proper configuration management
- **Developer friendly** - Clear configuration options

Your ArchE system is now fully configurable and resilient to port conflicts! 🚀 