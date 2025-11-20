# How to Access VCD Guides from the VCD System

**Created**: 2025-11-19  
**Last Updated**: 2025-11-19 06:38:29 EST

## Quick Access Methods

### Method 1: Using VCD Guide Accessor (Recommended)

```python
from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor

# Initialize accessor
guide_accessor = VCDGuideAccessor()

# Get a specific guide
guide = guide_accessor.get_guide("vcd_bridge")
print(guide["content"])

# List all guides
all_guides = guide_accessor.list_guides()
for guide in all_guides:
    print(f"- {guide['title']}")

# Search guides
results = guide_accessor.search_guides("backup")
for result in results:
    print(f"- {result['title']}")
```

### Method 2: Through VCD Health Dashboard

```python
from Three_PointO_ArchE.vcd_health_dashboard import VCDHealthDashboardAPI, VCDHealthCollector

collector = VCDHealthCollector()
api = VCDHealthDashboardAPI(collector)

# Get guide access information
guide_info = api.get_guide_access()
print(f"Guides available: {guide_info['guides_available']}")
print(f"Total guides: {guide_info['total_guides']}")
```

### Method 3: Direct File Access

```python
from pathlib import Path

# Access guide files directly
guides_dir = Path("docs/vcd_guides")
bridge_guide = guides_dir / "01_VCD_Bridge_Guide.md"

with open(bridge_guide, 'r') as f:
    content = f.read()
    print(content)
```

## Integration Examples

### Example 1: Add Guide Access to VCD Bridge

```python
# In vcd_bridge.py
from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor

class VCDBridge:
    def __init__(self):
        self.guide_accessor = VCDGuideAccessor()
    
    async def handle_guide_request(self, websocket, message):
        """Handle guide request from client"""
        guide_id = message.get("guide_id")
        guide = self.guide_accessor.get_guide(guide_id)
        
        await websocket.send(json.dumps({
            "type": "guide_response",
            "guide": guide
        }))
```

### Example 2: Add Help Command to VCD UI

```python
# In visual_cognitive_debugger_ui.py
from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor

class VisualCognitiveDebugger:
    def __init__(self):
        self.guide_accessor = VCDGuideAccessor()
    
    async def handle_help_command(self, command):
        """Handle help command"""
        if command == "list":
            guides = self.guide_accessor.list_guides()
            return {"guides": guides}
        elif command.startswith("guide "):
            guide_id = command.split(" ", 1)[1]
            guide = self.guide_accessor.get_guide(guide_id)
            return {"guide": guide}
        else:
            return {"error": "Unknown help command"}
```

## WebSocket Integration

### Client Request Format

```json
{
  "type": "get_guide",
  "guide_id": "vcd_bridge"
}
```

### Server Response Format

```json
{
  "type": "guide_response",
  "guide": {
    "metadata": {
      "guide_id": "vcd_bridge",
      "title": "VCD Bridge - Complete How-To Guide",
      "component": "vcd_bridge",
      "version": "1.0"
    },
    "content": "# VCD Bridge - Complete How-To Guide\n\n..."
  }
}
```

## REST API Integration (Future)

```python
# Example Flask endpoint
from flask import Flask, jsonify
from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor

app = Flask(__name__)
guide_accessor = VCDGuideAccessor()

@app.route('/api/vcd/guides')
def list_guides():
    return jsonify(guide_accessor.list_guides())

@app.route('/api/vcd/guides/<guide_id>')
def get_guide(guide_id):
    guide = guide_accessor.get_guide(guide_id)
    if guide:
        return jsonify(guide)
    return jsonify({"error": "Guide not found"}), 404

@app.route('/api/vcd/guides/search/<query>')
def search_guides(query):
    return jsonify(guide_accessor.search_guides(query))
```

## Command Line Access

```bash
# List all guides
python3 -m Three_PointO_ArchE.vcd_guide_accessor

# Get specific guide (via Python)
python3 -c "
from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor
ga = VCDGuideAccessor()
guide = ga.get_guide('vcd_bridge')
print(guide['content'])
"
```

## Best Practices

1. **Use Guide Accessor**: Always use `VCDGuideAccessor` for programmatic access
2. **Cache Results**: Cache guide metadata for performance
3. **Error Handling**: Always check if guide exists before accessing
4. **Search First**: Use search before direct access for better UX
5. **Update Regularly**: Keep guides synchronized with code changes

## Troubleshooting

### Guides Not Found

**Problem**: `get_guide()` returns None

**Solutions**:
1. Verify guides directory exists: `ls docs/vcd_guides/`
2. Check guide file names match expected format
3. Verify file permissions
4. Check guide accessor initialization

### Import Errors

**Problem**: Cannot import `VCDGuideAccessor`

**Solutions**:
1. Verify file exists: `ls Three_PointO_ArchE/vcd_guide_accessor.py`
2. Check PYTHONPATH
3. Verify dependencies installed

---

**See Also**: [VCD Guides Index](00_VCD_GUIDES_INDEX.md)

