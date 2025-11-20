# VCD Guides - Quick Access

**Created**: 2025-11-19  
**Last Updated**: 2025-11-19 06:40:39 EST

## Quick Access from Python

```python
from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor

# Initialize
ga = VCDGuideAccessor()

# List all guides
guides = ga.list_guides()

# Get specific guide
guide = ga.get_guide("vcd_bridge")

# Search guides
results = ga.search_guides("backup")
```

## Access from VCD Health Dashboard

```python
from Three_PointO_ArchE.vcd_health_dashboard import VCDHealthDashboardAPI, VCDHealthCollector

api = VCDHealthDashboardAPI(VCDHealthCollector())
guide_info = api.get_guide_access()
```

## All Available Guides

1. [VCD Bridge Guide](01_VCD_Bridge_Guide.md)
2. [VCD Analysis Agent Guide](02_VCD_Analysis_Agent_Guide.md)
3. [VCD Health Dashboard Guide](03_VCD_Health_Dashboard_Guide.md)
4. [VCD Backup & Recovery Guide](04_VCD_Backup_Recovery_Guide.md)
5. [VCD Configuration Management Guide](05_VCD_Configuration_Management_Guide.md)
6. [VCD Testing Suite Guide](06_VCD_Testing_Suite_Guide.md)
7. [VCD UI Component Guide](07_VCD_UI_Component_Guide.md)
8. [Free Model Options Guide](08_Free_Model_Options_Guide.md)

See [HOW_TO_ACCESS_GUIDES_FROM_VCD.md](HOW_TO_ACCESS_GUIDES_FROM_VCD.md) for detailed integration instructions.

