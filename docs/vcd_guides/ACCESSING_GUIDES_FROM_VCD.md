# Accessing VCD Guides from the VCD System

**Created**: 2025-11-19  
**Last Updated**: 2025-11-19 06:42:00 EST

## Overview

VCD Guides can be accessed from the VCD system through multiple methods:
1. **WebSocket via VCD Bridge** (Real-time access)
2. **Python API** (Programmatic access)
3. **Health Dashboard API** (Monitoring integration)
4. **Direct File Access** (File system)

## Method 1: WebSocket Access via VCD Bridge ⭐ (Recommended)

The VCD Bridge now supports guide requests via WebSocket messages.

### Connect to VCD Bridge

```javascript
// JavaScript/TypeScript (Frontend)
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
    console.log('Connected to VCD Bridge');
};
```

### Request a Specific Guide

```javascript
// Request a guide by component name
ws.send(JSON.stringify({
    type: "get_guide",
    guide_id: "vcd_bridge"  // or component name
}));

// Handle response
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "guide_response") {
        if (data.guide) {
            console.log("Guide Title:", data.guide.metadata.title);
            console.log("Guide Content:", data.guide.content);
        } else {
            console.error("Error:", data.error);
        }
    }
};
```

### List All Guides

```javascript
// Request list of all guides
ws.send(JSON.stringify({
    type: "list_guides"
}));

// Handle response
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "guides_list_response") {
        console.log(`Found ${data.total} guides:`);
        data.guides.forEach(guide => {
            console.log(`  - ${guide.title} (${guide.component})`);
        });
    }
};
```

### Search Guides

```javascript
// Search guides by keyword
ws.send(JSON.stringify({
    type: "search_guides",
    query: "backup"
}));

// Handle response
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "guides_search_response") {
        console.log(`Found ${data.count} guides for "${data.query}":`);
        data.results.forEach(guide => {
            console.log(`  - ${guide.title}`);
        });
    }
};
```

### Python WebSocket Client Example

```python
import asyncio
import websockets
import json

async def get_guide_from_vcd(guide_id: str):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Request guide
        await websocket.send(json.dumps({
            "type": "get_guide",
            "guide_id": guide_id
        }))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "guide_response" and "guide" in data:
            return data["guide"]
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
            return None

# Usage
guide = asyncio.run(get_guide_from_vcd("vcd_bridge"))
if guide:
    print(guide["metadata"]["title"])
    print(guide["content"][:500])  # First 500 chars
```

## Method 2: Python API Access

### Direct Guide Accessor

```python
from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor

# Initialize
ga = VCDGuideAccessor()

# Get a specific guide
guide = ga.get_guide("vcd_bridge")
if guide:
    print(guide["metadata"]["title"])
    print(guide["content"])

# List all guides
guides = ga.list_guides()
for guide in guides:
    print(f"- {guide['title']}")

# Search guides
results = ga.search_guides("backup")
for result in results:
    print(f"- {result['title']}")

# Get guide summary (metadata only)
summary = ga.get_guide_summary("vcd_health_dashboard")
print(summary)

# Get specific section
section = ga.get_guide_section("vcd_bridge", "API Reference")
print(section)
```

## Method 3: Health Dashboard Integration

### Via Health Dashboard API

```python
from Three_PointO_ArchE.vcd_health_dashboard import VCDHealthDashboardAPI, VCDHealthCollector

# Initialize
collector = VCDHealthCollector()
api = VCDHealthDashboardAPI(collector)

# Get guide access information
guide_info = api.get_guide_access()

if guide_info["guides_available"]:
    print(f"✅ Guides available: {guide_info['total_guides']} guides")
    print(f"Usage: {guide_info['usage']}")
    
    # Access guide accessor directly
    from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor
    ga = VCDGuideAccessor()
    guide = ga.get_guide("vcd_health_dashboard")
else:
    print(f"❌ Guides not available: {guide_info.get('error')}")
```

## Method 4: Direct File Access

### Reading Guide Files Directly

```python
from pathlib import Path

# Access guide files directly
guides_dir = Path("docs/vcd_guides")

# Read a specific guide
bridge_guide = guides_dir / "01_VCD_Bridge_Guide.md"
with open(bridge_guide, 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)

# List all guides
for guide_file in sorted(guides_dir.glob("0[1-8]_*.md")):
    print(f"- {guide_file.name}")
```

## Complete Example: Interactive Guide Browser

```python
import asyncio
import websockets
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

async def guide_browser():
    """Interactive guide browser via VCD Bridge"""
    uri = "ws://localhost:8765"
    
    async with websockets.connect(uri) as websocket:
        console.print("[green]✅ Connected to VCD Bridge[/green]")
        
        # List all guides
        await websocket.send(json.dumps({"type": "list_guides"}))
        response = await websocket.recv()
        data = json.loads(response)
        
        if data["type"] == "guides_list_response":
            console.print(f"\n[bold]Available Guides ({data['total']}):[/bold]")
            for i, guide in enumerate(data["guides"], 1):
                console.print(f"  {i}. {guide['title']}")
                console.print(f"     Component: {guide['component']}")
            
            # Get a specific guide
            guide_id = input("\nEnter guide ID to view (or 'q' to quit): ")
            if guide_id.lower() != 'q':
                await websocket.send(json.dumps({
                    "type": "get_guide",
                    "guide_id": guide_id
                }))
                
                response = await websocket.recv()
                guide_data = json.loads(response)
                
                if guide_data.get("type") == "guide_response" and "guide" in guide_data:
                    guide = guide_data["guide"]
                    console.print(Panel(
                        Markdown(guide["content"]),
                        title=guide["metadata"]["title"],
                        border_style="blue"
                    ))
                else:
                    console.print(f"[red]Error: {guide_data.get('error')}[/red]")

asyncio.run(guide_browser())
```

## WebSocket Message Formats

### Request: Get Guide

```json
{
  "type": "get_guide",
  "guide_id": "vcd_bridge"
}
```

### Response: Guide Data

```json
{
  "type": "guide_response",
  "guide": {
    "metadata": {
      "guide_id": "vcd_bridge",
      "title": "VCD Bridge - Complete How-To Guide",
      "component": "vcd_bridge",
      "version": "1.0",
      "created": "2025-11-19",
      "last_updated": "2025-11-19 06:27:10 EST"
    },
    "content": "# VCD Bridge - Complete How-To Guide\n\n...",
    "guide_id": "vcd_bridge",
    "component": "vcd_bridge"
  },
  "timestamp": "2025-11-19T11:42:00.123456"
}
```

### Request: List Guides

```json
{
  "type": "list_guides"
}
```

### Response: Guides List

```json
{
  "type": "guides_list_response",
  "guides": [
    {
      "guide_id": "vcd_bridge",
      "title": "VCD Bridge - Complete How-To Guide",
      "component": "vcd_bridge",
      ...
    }
  ],
  "total": 8,
  "timestamp": "2025-11-19T11:42:00.123456"
}
```

### Request: Search Guides

```json
{
  "type": "search_guides",
  "query": "backup"
}
```

### Response: Search Results

```json
{
  "type": "guides_search_response",
  "query": "backup",
  "results": [
    {
      "guide_id": "vcd_backup_recovery",
      "title": "VCD Backup & Recovery - Complete How-To Guide",
      ...
    }
  ],
  "count": 1,
  "timestamp": "2025-11-19T11:42:00.123456"
}
```

## Integration Examples

### Example 1: Add Help Menu to VCD UI

```python
# In your VCD UI component
async def show_help_menu():
    # Connect to bridge
    ws = await websockets.connect("ws://localhost:8765")
    
    # Request guide list
    await ws.send(json.dumps({"type": "list_guides"}))
    response = await ws.recv()
    data = json.loads(response)
    
    # Display menu
    print("VCD Help Menu:")
    for guide in data["guides"]:
        print(f"  {guide['component']}: {guide['title']}")
    
    # User selects guide
    selection = input("Select guide: ")
    await ws.send(json.dumps({
        "type": "get_guide",
        "guide_id": selection
    }))
    
    # Display guide
    response = await ws.recv()
    guide_data = json.loads(response)
    display_guide(guide_data["guide"])
```

### Example 2: Contextual Help in VCD

```python
# Show relevant guide based on current component
async def show_contextual_help(component_name: str):
    ws = await websockets.connect("ws://localhost:8765")
    
    # Get guide for current component
    await ws.send(json.dumps({
        "type": "get_guide",
        "guide_id": component_name
    }))
    
    response = await ws.recv()
    guide_data = json.loads(response)
    
    if "guide" in guide_data:
        # Show quick reference section
        guide = guide_data["guide"]
        quick_ref = guide["content"].split("## Quick Start")[1].split("##")[0]
        show_popup(quick_ref)
```

## Troubleshooting

### Guide Accessor Not Available

**Problem**: `guide_accessor` is None in VCD Bridge

**Solutions**:
1. Check guide accessor module exists: `ls Three_PointO_ArchE/vcd_guide_accessor.py`
2. Verify guides directory exists: `ls docs/vcd_guides/`
3. Check import errors in bridge logs
4. Verify PYTHONPATH includes project root

### WebSocket Connection Failed

**Problem**: Cannot connect to VCD Bridge

**Solutions**:
1. Verify bridge is running: `ps aux | grep vcd_bridge`
2. Check port 8765 is open: `netstat -an | grep 8765`
3. Verify firewall settings
4. Check bridge logs for errors

### Guide Not Found

**Problem**: Requested guide returns error

**Solutions**:
1. List available guides first
2. Verify component name is correct
3. Check guide file exists: `ls docs/vcd_guides/0*_*_Guide.md`
4. Review guide accessor logs

## Best Practices

1. **Cache Guide Metadata**: Cache guide list for performance
2. **Error Handling**: Always check for errors in responses
3. **Progressive Loading**: Load guide content on demand
4. **Search First**: Use search before direct access
5. **User Feedback**: Show loading states during requests

## Quick Reference

```python
# Quick access function
def get_vcd_guide(guide_id: str):
    from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor
    ga = VCDGuideAccessor()
    return ga.get_guide(guide_id)

# Usage
guide = get_vcd_guide("vcd_bridge")
print(guide["content"] if guide else "Guide not found")
```

---

**See Also**:
- [VCD Guides Index](00_VCD_GUIDES_INDEX.md)
- [VCD Bridge Guide](01_VCD_Bridge_Guide.md)
- [VCD Health Dashboard Guide](03_VCD_Health_Dashboard_Guide.md)

