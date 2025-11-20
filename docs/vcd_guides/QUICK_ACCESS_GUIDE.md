# Quick Access Guide - VCD Guides from VCD System

**Created**: 2025-11-19  
**Last Updated**: 2025-11-19 06:52:14 EST

## 🚀 Quick Start

### Method 1: WebSocket (Real-Time) ⭐ Easiest

```javascript
// Connect to VCD Bridge
const ws = new WebSocket('ws://localhost:8765');

// Get a guide
ws.send(JSON.stringify({
    type: "get_guide",
    guide_id: "vcd_bridge"
}));

// List all guides
ws.send(JSON.stringify({ type: "list_guides" }));

// Search guides
ws.send(JSON.stringify({
    type: "search_guides",
    query: "backup"
}));
```

### Method 2: Python API

```python
from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor

ga = VCDGuideAccessor()
guide = ga.get_guide("vcd_bridge")
print(guide["content"])
```

### Method 3: Health Dashboard

```python
from Three_PointO_ArchE.vcd_health_dashboard import VCDHealthDashboardAPI, VCDHealthCollector

api = VCDHealthDashboardAPI(VCDHealthCollector())
guide_info = api.get_guide_access()
print(f"Guides: {guide_info['total_guides']}")
```

## 📋 Available Guides

1. `vcd_bridge` - VCD Bridge Guide
2. `vcd_analysis_agent` - Analysis Agent Guide
3. `vcd_health_dashboard` - Health Dashboard Guide
4. `vcd_backup_recovery` - Backup & Recovery Guide
5. `vcd_configuration_management` - Configuration Guide
6. `vcd_testing_suite` - Testing Suite Guide
7. `vcd_ui` - UI Component Guide
8. `free_model_options` - Model Options Guide

## 🔧 Integration Status

✅ **VCD Bridge**: Guide handlers added  
✅ **Guide Accessor**: Module created and tested  
✅ **Health Dashboard**: Integration method added  
✅ **All Guides**: 8 guides created and accessible

---

**Full Documentation**: [ACCESSING_GUIDES_FROM_VCD.md](ACCESSING_GUIDES_FROM_VCD.md)

