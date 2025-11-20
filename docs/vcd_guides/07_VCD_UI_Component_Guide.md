# VCD UI Component - Complete How-To Guide

**Component**: Visual Cognitive Debugger UI Component  
**Version**: 1.0  
**Created**: 2025-11-19  
**Last Updated**: 2025-11-19 06:42:00 EST  
**File**: `Three_PointO_ArchE/visual_cognitive_debugger_ui.py`

## Overview

The VCD UI Component provides visualization and user interface capabilities for the Visual Cognitive Debugger, including multiple visualization modes, real-time cognitive state display, and interactive cognitive process monitoring.

## Prerequisites

- Python 3.8+
- WebSocket support
- ArchE core components
- Optional: Frontend framework (Next.js)

## Installation

```bash
# No additional installation required
python3 -c "from Three_PointO_ArchE.visual_cognitive_debugger_ui import VisualCognitiveDebugger; print('✅ Available')"
```

## Basic Usage

### Starting the VCD UI Server

```python
from Three_PointO_ArchE.visual_cognitive_debugger_ui import VisualCognitiveDebugger
import asyncio

async def start_vcd():
    vcd = VisualCognitiveDebugger()
    await vcd.start_server()

asyncio.run(start_vcd())
```

### Visualization Modes

The VCD UI supports multiple visualization modes:

1. **REAL_TIME_MONITORING** - Live cognitive state
2. **COGNITIVE_RESONANCE_MAP** - Resonance visualization
3. **TEMPORAL_DYNAMICS_VIEW** - Time-based analysis
4. **IMPLEMENTATION_RESONANCE_TRACE** - Code-concept alignment
5. **PATTERN_CRYSTALLIZATION_DISPLAY** - Pattern evolution
6. **MANDATE_COMPLIANCE_DASHBOARD** - Compliance tracking
7. **RISK_ASSESSMENT_VISUALIZATION** - Risk analysis
8. **COLLECTIVE_INTELLIGENCE_NETWORK** - Network visualization
9. **THOUGHT_TRAIL_VISUALIZATION** - Thought history
10. **SPR_ACTIVATION_MONITORING** - SPR activation patterns

### Generating Visualizations

```python
from Three_PointO_ArchE.visual_cognitive_debugger_ui import (
    VisualCognitiveDebugger,
    CognitiveVisualizationMode
)

vcd = VisualCognitiveDebugger()

# Generate cognitive resonance map
visualization = vcd.generate_visualization(
    mode=CognitiveVisualizationMode.COGNITIVE_RESONANCE_MAP
)
```

## Advanced Usage

### Custom Visualization Data

```python
from Three_PointO_ArchE.visual_cognitive_debugger_ui import CognitiveVisualizationData

data = CognitiveVisualizationData(
    timestamp=now_iso(),
    cognitive_resonance=0.85,
    temporal_resonance={"coherence": 0.90},
    implementation_resonance={"strategic": 0.88},
    mandate_compliance={"mandate_1": True, "mandate_2": True},
    risk_assessment={"overall_risk": "low"},
    pattern_crystallization={"patterns": 5},
    collective_intelligence_status={"nodes": 3},
    thought_trail_status={"entries": 100},
    spr_activation_status={"active": 12}
)

visualization = vcd.generate_visualization_from_data(data)
```

## API Reference

### VisualCognitiveDebugger Class

#### `__init__()`
Initialize VCD UI component.

#### `async def start_server(host="0.0.0.0", port=8765)`
Start WebSocket server for UI connections.

#### `generate_visualization(mode) -> Dict[str, Any]`
Generate visualization for specified mode.

#### `generate_visualization_from_data(data) -> Dict[str, Any]`
Generate visualization from data object.

### CognitiveVisualizationMode Enum

All available visualization modes as enum values.

## Integration

### With VCD Bridge

```python
from vcd_bridge import VCDBridge
from Three_PointO_ArchE.visual_cognitive_debugger_ui import VisualCognitiveDebugger

# Start bridge
bridge = VCDBridge()
await bridge.start()

# Start UI
vcd = VisualCognitiveDebugger()
vcd.bridge = bridge
await vcd.start_server()
```

### With Frontend (Next.js)

The VCD UI integrates with the Next.js frontend in `nextjs-chat/`:

```bash
cd nextjs-chat
npm run dev
# Open http://localhost:3000
```

## Troubleshooting

### Server Won't Start

**Problem**: WebSocket server fails to start

**Solutions**:
1. Check port availability: `netstat -an | grep 8765`
2. Verify permissions
3. Check firewall settings
4. Review server logs

### No Visualizations Generated

**Problem**: Visualizations are empty

**Solutions**:
1. Verify cognitive data is available
2. Check visualization mode is valid
3. Review data structure
4. Check component initialization

## Best Practices

1. **Mode Selection**: Choose appropriate visualization mode
2. **Data Quality**: Ensure accurate cognitive data
3. **Performance**: Limit visualization frequency
4. **Caching**: Cache visualization data when possible

## Examples

### Example 1: Real-Time Monitoring

```python
async def real_time_monitoring():
    vcd = VisualCognitiveDebugger()
    await vcd.start_server()
    
    # Generate real-time visualizations
    while True:
        viz = vcd.generate_visualization(
            CognitiveVisualizationMode.REAL_TIME_MONITORING
        )
        # Send to clients
        await asyncio.sleep(1)  # Update every second
```

## Related Components

- **VCD Bridge**: Provides WebSocket communication
- **VCD Health Dashboard**: Monitors UI performance
- **VCD Analysis Agent**: Provides analysis data

## Support

For issues:
1. Check UI logs
2. Verify WebSocket connections
3. Review visualization data
4. Test with different modes

---

**Previous Guide**: [VCD Testing Suite Guide](06_VCD_Testing_Suite_Guide.md)  
**Next Guide**: [Free Model Options Guide](08_Free_Model_Options_Guide.md)
