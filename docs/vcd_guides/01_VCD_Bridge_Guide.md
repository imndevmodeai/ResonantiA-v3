# VCD Bridge - Complete How-To Guide

**Component**: Visual Cognitive Debugger Bridge  
**Version**: 1.0  
**Created**: 2025-11-19  
**Last Updated**: 2025-11-19 06:27:10 EST  
**File**: `vcd_bridge.py`

## Overview

The VCD Bridge is the WebSocket server that connects ArchE's cognitive core to the Visual Cognitive Debugger frontend. It provides real-time event broadcasting, rich media support, and interactive capabilities for research-grade cognitive analysis.

## Prerequisites

- Python 3.8+
- `websockets` library: `pip install websockets`
- ArchE core components installed
- Access to `Three_PointO_ArchE` module directory

## Installation

### Step 1: Install Dependencies

```bash
pip install websockets asyncio
```

### Step 2: Verify ArchE Core Access

```bash
# Ensure PYTHONPATH includes ArchE modules
export PYTHONPATH=$PYTHONPATH:./Three_PointO_ArchE:./Four_PointO_ArchE
```

### Step 3: Test Import

```python
python3 -c "from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator; print('✅ Imports successful')"
```

## Basic Usage

### Starting the VCD Bridge Server

```bash
# Start the bridge server
python3 vcd_bridge.py
```

The server will:
- Start on WebSocket port **8765**
- Listen on `0.0.0.0` (all interfaces)
- Display connection status and event logs

### Connecting from a Client

```python
import asyncio
import websockets

async def connect_to_vcd():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Send handshake
        await websocket.send(json.dumps({
            "type": "handshake",
            "client_id": "my_client"
        }))
        
        # Receive messages
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data['type']}")

asyncio.run(connect_to_vcd())
```

## Advanced Usage

### Custom Event Broadcasting

```python
from vcd_bridge import VCDBridge, VCDEventType, VCDRichEvent

# Create custom event
event = VCDRichEvent(
    event_id=str(uuid.uuid4()),
    event_type=VCDEventType.THOUGHT_PROCESS,
    timestamp=datetime.now().isoformat(),
    phase="analysis",
    title="Custom Analysis",
    description="Performing custom cognitive analysis",
    links=[{"url": "https://example.com", "title": "Reference"}],
    code_blocks=[{"language": "python", "code": "print('Hello')"}]
)

# Broadcast event
await bridge.broadcast_event(event)
```

### Integration with RISE Engine

```python
from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator

# Initialize RISE orchestrator
rise = RISE_Orchestrator()

# Perform analysis with VCD integration
result = await rise.execute_rise_workflow(
    query="Analyze system performance",
    vcd_bridge=bridge  # Pass bridge for real-time updates
)
```

## API Reference

### VCDBridge Class

#### `__init__(host: str = "0.0.0.0", port: int = 8765)`
Initialize the VCD Bridge server.

**Parameters:**
- `host`: Server host address (default: "0.0.0.0")
- `port`: WebSocket port (default: 8765)

#### `async def start()`
Start the WebSocket server and begin accepting connections.

#### `async def broadcast_event(event: VCDRichEvent)`
Broadcast an event to all connected clients.

**Parameters:**
- `event`: VCDRichEvent object to broadcast

#### `async def send_to_client(client_id: str, message: dict)`
Send a message to a specific client.

**Parameters:**
- `client_id`: Target client identifier
- `message`: Message dictionary to send

### VCDEventType Enum

Available event types:
- `ANALYSIS_START`: Analysis session started
- `PHASE_START`: New analysis phase began
- `WEB_SEARCH`: Web search performed
- `CODE_EXECUTION`: Code executed
- `THOUGHT_PROCESS`: Cognitive thought process
- `ANALYSIS_COMPLETE`: Analysis finished

## Configuration

### Environment Variables

```bash
# WebSocket port (default: 8765)
export VCD_BRIDGE_PORT=8765

# Server host (default: 0.0.0.0)
export VCD_BRIDGE_HOST=0.0.0.0

# Enable debug logging
export VCD_DEBUG=true
```

### Configuration File

Create `config/vcd_bridge.yaml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8765
  timeout: 30
  max_connections: 100

websocket:
  ping_interval: 20
  ping_timeout: 10
  max_size: 1048576  # 1MB

logging:
  level: "INFO"
  file: "logs/vcd_bridge.log"
```

## Troubleshooting

### Connection Refused

**Problem**: Cannot connect to WebSocket server

**Solutions**:
1. Verify server is running: `ps aux | grep vcd_bridge`
2. Check port availability: `netstat -an | grep 8765`
3. Verify firewall settings
4. Check server logs: `tail -f logs/vcd_bridge.log`

### Import Errors

**Problem**: `ImportError: cannot import name 'RISE_Orchestrator'`

**Solutions**:
1. Set PYTHONPATH: `export PYTHONPATH=$PYTHONPATH:./Three_PointO_ArchE`
2. Verify module exists: `ls Three_PointO_ArchE/rise_orchestrator.py`
3. Install dependencies: `pip install -r Three_PointO_ArchE/requirements.txt`

### High Memory Usage

**Problem**: Server using excessive memory

**Solutions**:
1. Reduce `max_connections` in configuration
2. Implement message queue limits
3. Enable connection timeouts
4. Monitor with: `python3 -m vcd_health_dashboard`

## Best Practices

1. **Connection Management**
   - Always use connection timeouts
   - Implement reconnection logic in clients
   - Monitor connection count

2. **Event Broadcasting**
   - Use appropriate event types
   - Include timestamps in all events
   - Limit event frequency for performance

3. **Error Handling**
   - Wrap WebSocket operations in try/except
   - Log all errors with context
   - Implement graceful degradation

4. **Security**
   - Use authentication for production
   - Validate all incoming messages
   - Limit message size

## Examples

### Example 1: Basic Server

```python
#!/usr/bin/env python3
import asyncio
from vcd_bridge import VCDBridge

async def main():
    bridge = VCDBridge(host="0.0.0.0", port=8765)
    await bridge.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Event Broadcasting

```python
async def broadcast_analysis_progress(bridge, phase, progress):
    event = VCDRichEvent(
        event_id=str(uuid.uuid4()),
        event_type=VCDEventType.PHASE_START,
        timestamp=datetime.now().isoformat(),
        phase=phase,
        title=f"Analysis Phase: {phase}",
        description=f"Progress: {progress}%"
    )
    await bridge.broadcast_event(event)
```

### Example 3: Client Connection Handler

```python
async def handle_client(websocket, path):
    client_id = str(uuid.uuid4())
    print(f"Client connected: {client_id}")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            # Process message
            response = {"status": "ok", "data": data}
            await websocket.send(json.dumps(response))
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {client_id}")
```

## Related Components

- **VCD Analysis Agent**: Uses bridge for real-time analysis updates
- **VCD Health Dashboard**: Monitors bridge performance
- **VCD UI Component**: Frontend visualization using bridge

## Support

For issues or questions:
1. Check logs: `logs/vcd_bridge.log`
2. Review health dashboard: `python3 -m Three_PointO_ArchE.vcd_health_dashboard`
3. Run diagnostics: `python3 -m Three_PointO_ArchE.vcd_testing_suite`

---

**Next Guide**: [VCD Analysis Agent Guide](02_VCD_Analysis_Agent_Guide.md)

