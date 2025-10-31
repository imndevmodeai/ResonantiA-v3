# Integrated Development Setup

## Overview

This project now includes an integrated development environment that starts both the Next.js frontend and ArchE backend server together. The setup provides a seamless development experience with automatic port management, health checks, and graceful shutdown.

## Quick Start

### Option 1: Full Integrated Development (Recommended)
```bash
# Start both Next.js and ArchE servers together
npm run dev:full
```

### Option 2: Individual Servers
```bash
# Start only Next.js frontend
npm run dev

# Start only ArchE backend
npm run dev:arche
```

### Option 3: Health Check
```bash
# Check if all services are running properly
npm run health
```

## What Gets Started

When you run `npm run dev:full`, the following services are started:

1. **Next.js Frontend** (Port 3000)
   - React application with ResonantiA Protocol integration
   - WebSocket client for real-time communication
   - Protocol-enhanced UI components

2. **ArchE Backend Server** (Port 3005)
   - Python-based cognitive orchestration server
   - ResonantiA Maestro for advanced query processing
   - Knowledge Scaffolding and workflow execution
   - IAR (Integrated Action Reflection) compliance

3. **WebSocket Server** (Port 3004)
   - Protocol-specific WebSocket server
   - Enhanced message processing with IAR, SPR, and temporal analysis
   - Real-time communication bridge

## Configuration

### Environment Variables

The following environment variables can be set to customize the behavior:

```bash
# WebSocket URLs
export WEBSOCKET_URL=ws://localhost:3005
export PROTOCOL_VERSION=ResonantiA v3.1-CA
export KEYHOLDER_OVERRIDE_ACTIVE=true

# Python environment
export PYTHONPATH=/path/to/your/project
export GOOGLE_API_KEY=your_google_api_key
```

### Configuration File

Edit `dev-config.json` to customize server settings:

```json
{
  "development": {
    "nextPort": 3000,
    "archePort": 3005,
    "websocketPort": 3004,
    "pythonPath": "./.venv/bin/python3"
  }
}
```

## Development Workflow

### 1. Initial Setup
```bash
# Install dependencies
npm install

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Development
```bash
# Start integrated development environment
npm run dev:full
```

### 3. Development Process
- Frontend changes are automatically hot-reloaded
- Backend changes require server restart (Ctrl+C, then `npm run dev:full`)
- All logs are displayed in the integrated console
- Health checks run automatically

### 4. Testing
```bash
# Test the connection
source .venv/bin/activate
python3 test_connection.py

# Test with browser
open test_browser_connection.html
```

## Features

### ✅ Automatic Port Management
- Checks for port conflicts before starting
- Automatically kills conflicting processes
- Ensures clean startup every time

### ✅ Health Monitoring
- Real-time health checks for all services
- Automatic detection of service failures
- Detailed status reporting

### ✅ Graceful Shutdown
- Proper cleanup of all processes
- Signal handling (Ctrl+C)
- Timeout-based force kill if needed

### ✅ Integrated Logging
- Color-coded output for different services
- Timestamped log entries
- Real-time log streaming

### ✅ Error Recovery
- Automatic retry mechanisms
- Detailed error reporting
- Fallback options for failed services

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Manual port cleanup
lsof -ti:3000 | xargs kill -9
lsof -ti:3005 | xargs kill -9
lsof -ti:3004 | xargs kill -9
```

#### 2. Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. Python Path Issues
```bash
# Check Python path
which python3
ls -la .venv/bin/python3

# Update configuration if needed
# Edit dev-config.json and update pythonPath
```

#### 4. Dependencies Missing
```bash
# Install missing dependencies
source .venv/bin/activate
pip install websockets google-generativeai
```

### Debug Mode

Enable debug logging by setting the environment variable:
```bash
export DEBUG=true
npm run dev:full
```

## Production Deployment

For production deployment, use the production configuration:

```bash
# Set production environment
export NODE_ENV=production

# Start with production settings
npm run dev:full
```

The production configuration includes:
- Longer timeouts for stability
- Reduced retry attempts
- Optimized health check intervals

## Monitoring and Logs

### Log Locations
- **Console**: Real-time integrated output
- **Files**: `logs/dev-server.log` (if enabled)
- **ArchE**: `logs/arche_persistent_server.log`
- **Next.js**: Built-in Next.js logging

### Health Check Endpoints
- Frontend: `http://localhost:3000`
- ArchE Backend: `ws://localhost:3005`
- WebSocket Server: `ws://localhost:3004`

## Advanced Configuration

### Custom Python Environment
If you're using a different Python setup:

1. Update `dev-config.json`:
```json
{
  "development": {
    "pythonPath": "/path/to/your/python"
  }
}
```

2. Or set environment variable:
```bash
export PYTHON_PATH=/path/to/your/python
```

### Custom Ports
To use different ports:

1. Update `dev-config.json`:
```json
{
  "development": {
    "nextPort": 3001,
    "archePort": 3006,
    "websocketPort": 3007
  }
}
```

2. Update environment variables:
```bash
export NEXT_PORT=3001
export ARCHE_PORT=3006
export WEBSOCKET_PORT=3007
```

## Scripts Reference

| Script | Description |
|--------|-------------|
| `npm run dev` | Start Next.js only |
| `npm run dev:full` | Start integrated environment |
| `npm run dev:arche` | Start ArchE server only |
| `npm run health` | Run health checks |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run linting |

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs in the console output
3. Verify all dependencies are installed
4. Ensure virtual environment is activated
5. Check port availability

The integrated development environment provides a seamless experience for developing with the ArchE cognitive system and ResonantiA Protocol v3.1-CA. 