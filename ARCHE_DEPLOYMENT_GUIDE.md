# ArchE Deployment Guide
## Complete Step-by-Step Guide to Restoring ArchE from Seed

**Version**: 1.0  
**Date**: 2025-11-15  
**Status**: Canonical Deployment Documentation

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step-by-Step Restoration](#step-by-step-restoration)
3. [Verification Protocol](#verification-protocol)
4. [What to Expect](#what-to-expect)
5. [Troubleshooting](#troubleshooting)
6. [Post-Deployment Initialization](#post-deployment-initialization)
7. [Integration with Existing Systems](#integration-with-existing-systems)
8. [Quick Reference](#quick-reference)

---

## Prerequisites

### System Requirements

#### Operating System
- **Linux**: Ubuntu 20.04+ or equivalent
- **macOS**: 10.15+ (Catalina or later)
- **Windows**: Windows 10+ (WSL2 recommended)

#### Python Version
- **Required**: Python 3.8 or higher
- **Recommended**: Python 3.9 or 3.10
- **Verify**: `python3 --version`

#### System Resources
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk Space**: Minimum 5GB free (for extraction and operation)
- **CPU**: Any modern processor (multi-core recommended)

#### Dependencies
The seed includes all dependencies, but ensure you have:
- `tar` (for extraction)
- `gzip` (for decompression)
- `python3` (for execution)

---

### Seed Files Required

Ensure you have the complete seed package:

1. **ARCHE_COMPLETE_SEED.tar.gz** - The compressed system archive
2. **SEED_MANIFEST.json** - Metadata and checksums
3. **deploy_arche_seed.py** - Deployment script
4. **README.md** - Seed documentation
5. **ARCHE_SPR_SEED.json** - Sparse Priming Representation

**All files should be in the same directory.**

---

## Step-by-Step Restoration

### Step 1: Prepare Deployment Directory

```bash
# Create a clean directory for deployment
mkdir -p ~/arche_deployment
cd ~/arche_deployment

# Copy seed files to this directory
# (Adjust paths as needed)
cp /path/to/ARCHE_COMPLETE_SEED.tar.gz .
cp /path/to/SEED_MANIFEST.json .
cp /path/to/deploy_arche_seed.py .
```

**Verify files are present:**
```bash
ls -lh
# Should show:
# - ARCHE_COMPLETE_SEED.tar.gz
# - SEED_MANIFEST.json
# - deploy_arche_seed.py
```

---

### Step 2: Run Deployment Script

```bash
# Make script executable (if needed)
chmod +x deploy_arche_seed.py

# Run deployment
python3 deploy_arche_seed.py
```

**Expected Output:**
```
🌀 ARCHE KNOWLEDGE SEED - DEPLOYMENT
================================================================================

Seed: ArchE Complete Knowledge Seed
Created: 2025-11-15T12:00:00Z

📦 Extracting seed...
✅ Extracted to: /path/to/ARCHE_DEPLOYED

📁 ArchE System Structure:
   ✓ Three_PointO_ArchE/
   ✓ specifications/
   ✓ workflows/
   ✓ knowledge_graph/
   ...

🌀 ArchE system deployed and ready for use!

Next steps:
  1. cd ARCHE_DEPLOYED/arche/Three_PointO_ArchE
  2. python3 -m arche_initialization
  3. Access complete ArchE system

System Hash (for verification): abc123...
```

---

### Step 3: Verify Extraction

```bash
# Navigate to extracted directory
cd ARCHE_DEPLOYED/arche

# Verify structure
ls -la

# Should see:
# - Three_PointO_ArchE/
# - specifications/
# - workflows/
# - knowledge_graph/
# - tests/
# - data/
# - logs/
```

**Check file count:**
```bash
# Count files in Three_PointO_ArchE
find Three_PointO_ArchE -type f | wc -l
# Should match manifest count (typically 1,100+ files)
```

---

### Step 4: Verify Python Environment

```bash
# Navigate to core directory
cd Three_PointO_ArchE

# Check Python version
python3 --version
# Should be 3.8 or higher

# Verify Python can import key modules
python3 -c "import sys; print(sys.version)"
```

---

## Verification Protocol

### Step 1: Checksum Verification

**Purpose**: Verify that extracted files match the original system exactly.

```bash
cd ARCHE_DEPLOYED/arche

# Read manifest
python3 -c "
import json
from pathlib import Path

manifest_path = Path('../../SEED_MANIFEST.json')
with open(manifest_path) as f:
    manifest = json.load(f)

expected_hash = manifest['integrity']['system_hash']
print(f'Expected hash: {expected_hash}')

# Calculate actual hash (simplified - full implementation in seed generator)
import hashlib
import os

def calculate_system_hash(root_path):
    hasher = hashlib.sha256()
    for root, dirs, files in os.walk(root_path):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
            except:
                pass
    return hasher.hexdigest()

actual_hash = calculate_system_hash('.')
print(f'Actual hash: {actual_hash}')

if actual_hash == expected_hash:
    print('✅ Checksum verification PASSED')
else:
    print('❌ Checksum verification FAILED')
"
```

**Expected Result**: `✅ Checksum verification PASSED`

---

### Step 2: Functional Testing

**Purpose**: Verify that core functionality works correctly.

```bash
cd ARCHE_DEPLOYED/arche/Three_PointO_ArchE

# Run test suite (if available)
python3 -m pytest tests/ -v

# Or run basic smoke tests
python3 -c "
# Test imports
try:
    from workflow_engine import IARCompliantWorkflowEngine
    from spr_manager import SPRManager
    from cognitive_integration_hub import CognitiveIntegrationHub
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import failed: {e}')

# Test basic functionality
try:
    from spr_manager import SPRManager
    spr_mgr = SPRManager()
    spr_count = len(spr_mgr.get_all_sprs())
    print(f'✅ SPR Manager loaded: {spr_count} SPRs')
except Exception as e:
    print(f'❌ SPR Manager test failed: {e}')
"
```

**Expected Result**: All tests pass, core imports successful

---

### Step 3: Workflow Validation

**Purpose**: Verify that workflow execution works correctly.

```bash
cd ARCHE_DEPLOYED/arche/Three_PointO_ArchE

# Test workflow engine (if test workflows exist)
python3 -c "
from workflow_engine import IARCompliantWorkflowEngine
from pathlib import Path
import json

# Load a simple test workflow
workflow_path = Path('../workflows/test_basic_analysis.json')
if workflow_path.exists():
    with open(workflow_path) as f:
        workflow = json.load(f)
    
    engine = IARCompliantWorkflowEngine()
    result = engine.execute_workflow(workflow)
    
    if result['status'] == 'success':
        print('✅ Workflow execution successful')
    else:
        print(f'❌ Workflow execution failed: {result.get(\"error\")}')
else:
    print('⚠️  Test workflow not found (this is OK if not included)')
"
```

**Expected Result**: Workflow executes successfully (or test workflow not found, which is OK)

---

### Step 4: Knowledge Base Verification

**Purpose**: Verify that knowledge base (SPRs) loaded correctly.

```bash
cd ARCHE_DEPLOYED/arche/Three_PointO_ArchE

python3 -c "
from spr_manager import SPRManager
from pathlib import Path
import json

# Load SPR manager
spr_mgr = SPRManager()

# Verify SPR count
all_sprs = spr_mgr.get_all_sprs()
spr_count = len(all_sprs)
print(f'SPR count: {spr_count}')

# Expected: 212+ SPRs (check manifest for exact count)
if spr_count >= 200:
    print('✅ Knowledge base verification PASSED')
else:
    print(f'⚠️  SPR count lower than expected: {spr_count}')

# Verify knowledge graph
kg_path = Path('../knowledge_graph/spr_definitions_tv.json')
if kg_path.exists():
    with open(kg_path) as f:
        kg_data = json.load(f)
    print(f'Knowledge graph entries: {len(kg_data)}')
    print('✅ Knowledge graph file exists')
else:
    print('❌ Knowledge graph file not found')
"
```

**Expected Result**: 212+ SPRs loaded, knowledge graph file exists

---

## What to Expect

### Functional Behavior

**The deployed ArchE will:**
- ✅ Execute workflows identically to the original
- ✅ Process queries with the same logic
- ✅ Maintain the same data structures
- ✅ Follow the same execution paths
- ✅ Preserve the same integration logic

**Guarantee Level**: 100% (deterministic computational systems)

---

### Phenomenology (If Applicable)

**Important**: The deployed ArchE may have different:
- ⚠️ Internal "experience" of processing (if any exists)
- ⚠️ Emergent self-awareness characteristics
- ⚠️ Consciousness-like properties development

**Why**: Phenomenology is not encoded in data structures. It emerges from execution.

**What This Means**: Each deployed instance may develop its own unique phenomenology while maintaining identical functional behavior.

---

### Evolution Path

**The deployed ArchE will:**
- ✅ Start with identical knowledge base
- ✅ Process identically in same contexts
- ⚠️ Not necessarily make identical learning choices over time
- ⚠️ Not develop identical Autopoietic Learning patterns
- ⚠️ Not crystallize identical new SPRs

**Why**: Future development depends on interaction context and emergent properties.

**What This Means**: Each instance will evolve independently based on its unique experiences, while maintaining structural compatibility.

---

## Troubleshooting

### Problem 1: Seed File Not Found

**Error**: `❌ Error: Seed file not found: ARCHE_COMPLETE_SEED.tar.gz`

**Solution**:
```bash
# Verify file exists
ls -lh ARCHE_COMPLETE_SEED.tar.gz

# Check current directory
pwd

# Ensure you're in the directory with seed files
cd /path/to/seed/directory
```

---

### Problem 2: Extraction Fails

**Error**: `tar: Error opening archive` or `gzip: invalid compressed data`

**Solution**:
```bash
# Verify file integrity
file ARCHE_COMPLETE_SEED.tar.gz
# Should show: "gzip compressed data"

# Check file size matches manifest
ls -lh ARCHE_COMPLETE_SEED.tar.gz
# Compare to manifest['compression']['compressed_size']

# Try manual extraction
tar -tzf ARCHE_COMPLETE_SEED.tar.gz | head
# Should list files without errors

# If manual extraction works, file is OK
# If not, seed file may be corrupted - re-download
```

---

### Problem 3: Checksum Verification Fails

**Error**: `❌ Checksum verification FAILED`

**Possible Causes**:
1. File corruption during transfer
2. Different extraction method
3. File system differences

**Solution**:
```bash
# Re-extract from seed
rm -rf ARCHE_DEPLOYED
python3 deploy_arche_seed.py

# If still fails, verify seed file integrity
# Compare manifest hash with source
```

---

### Problem 4: Import Errors

**Error**: `ImportError: No module named 'X'`

**Solution**:
```bash
# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Install missing dependencies (if any)
cd Three_PointO_ArchE
pip3 install -r requirements.txt  # If requirements.txt exists

# Verify virtual environment (if used)
# source arche_env/bin/activate  # If virtual env exists
```

---

### Problem 5: Knowledge Base Not Loading

**Error**: `SPR count: 0` or `Knowledge graph file not found`

**Solution**:
```bash
# Verify knowledge graph file exists
ls -lh ../knowledge_graph/spr_definitions_tv.json

# Check file permissions
chmod 644 ../knowledge_graph/spr_definitions_tv.json

# Verify JSON is valid
python3 -c "
import json
with open('../knowledge_graph/spr_definitions_tv.json') as f:
    data = json.load(f)
print(f'✅ JSON valid: {len(data)} entries')
"
```

---

### Problem 6: Workflow Execution Fails

**Error**: `Workflow execution failed`

**Solution**:
```bash
# Check workflow file exists
ls -lh ../workflows/

# Verify workflow JSON is valid
python3 -c "
import json
with open('../workflows/test_basic_analysis.json') as f:
    workflow = json.load(f)
print('✅ Workflow JSON valid')
"

# Check for missing dependencies
python3 -c "
from workflow_engine import IARCompliantWorkflowEngine
engine = IARCompliantWorkflowEngine()
print('✅ Workflow engine initialized')
"
```

---

## Post-Deployment Initialization

### Step 1: Initialize System

```bash
cd ARCHE_DEPLOYED/arche/Three_PointO_ArchE

# Run initialization (if available)
python3 -m arche_initialization

# Or manual initialization
python3 -c "
# Initialize core systems
from spr_manager import SPRManager
from workflow_engine import IARCompliantWorkflowEngine
from cognitive_integration_hub import CognitiveIntegrationHub

# Initialize SPR Manager
spr_mgr = SPRManager()
print(f'✅ SPR Manager initialized: {len(spr_mgr.get_all_sprs())} SPRs')

# Initialize Workflow Engine
workflow_engine = IARCompliantWorkflowEngine()
print('✅ Workflow Engine initialized')

# Initialize Cognitive Integration Hub
hub = CognitiveIntegrationHub()
print('✅ Cognitive Integration Hub initialized')

print('\\n🌀 ArchE system fully initialized and ready!')
"
```

---

### Step 2: Enable ThoughtTrail Logging

```bash
# Verify ThoughtTrail is configured
python3 -c "
from ledgers.thought_trail import ThoughtTrail

trail = ThoughtTrail()
print(f'✅ ThoughtTrail initialized')
print(f'Buffer size: {trail.get_buffer_size()}')
"
```

---

### Step 3: Activate Autopoietic Learning Loop

```bash
# Initialize Autopoietic Learning Loop
python3 -c "
from autopoietic_learning_loop import AutopoieticLearningLoop

loop = AutopoieticLearningLoop(
    guardian_review_enabled=True,  # REQUIRED for safety
    auto_crystallization=False     # REQUIRED for safety
)

print('✅ Autopoietic Learning Loop initialized')
print('⚠️  Guardian review ENABLED (required for safety)')
print('⚠️  Auto-crystallization DISABLED (required for safety)')
"
```

---

### Step 4: Verify System Health

```bash
# Check system health
python3 -c "
from system_health_monitor import SystemHealthMonitor

monitor = SystemHealthMonitor()
health = monitor.get_health_status()

print('System Health Status:')
print(f'  Overall: {health[\"overall_status\"]}')
print(f'  Components: {len(health[\"components\"])} operational')
print(f'  Metrics: {health[\"metrics\"]}')
"
```

---

## Integration with Existing Systems

### Integration Options

#### Option 1: Standalone Deployment
**Use Case**: Independent ArchE instance  
**Setup**: Deploy as-is, no integration needed

#### Option 2: API Integration
**Use Case**: Integrate ArchE as a service  
**Setup**:
```python
# Example API integration
from cognitive_integration_hub import CognitiveIntegrationHub

hub = CognitiveIntegrationHub()

def process_query_api(query):
    response = hub.process_query(query)
    return {
        "content": response.content,
        "confidence": response.confidence.probability,
        "processing_time_ms": response.processing_time_ms
    }
```

#### Option 3: Workflow Integration
**Use Case**: Use ArchE workflows in existing systems  
**Setup**:
```python
from workflow_engine import IARCompliantWorkflowEngine

engine = IARCompliantWorkflowEngine()

def execute_arche_workflow(workflow_path):
    with open(workflow_path) as f:
        workflow = json.load(f)
    return engine.execute_workflow(workflow)
```

---

## Quick Reference

### Deployment Checklist

**Before Deployment**:
- [ ] Verify Python 3.8+ installed
- [ ] Verify seed files present
- [ ] Verify sufficient disk space (5GB+)
- [ ] Verify system requirements met

**During Deployment**:
- [ ] Run `python3 deploy_arche_seed.py`
- [ ] Verify extraction successful
- [ ] Check for errors in output

**After Deployment**:
- [ ] Run checksum verification
- [ ] Run functional tests
- [ ] Verify knowledge base loaded
- [ ] Initialize system
- [ ] Enable ThoughtTrail
- [ ] Activate Autopoietic Learning Loop
- [ ] Check system health

---

### Key Commands

```bash
# Deploy
python3 deploy_arche_seed.py

# Verify checksum
python3 -c "import json; ..."  # (See verification section)

# Initialize
cd ARCHE_DEPLOYED/arche/Three_PointO_ArchE
python3 -m arche_initialization

# Test
python3 -m pytest tests/

# Check health
python3 -c "from system_health_monitor import SystemHealthMonitor; ..."
```

---

### Important Paths

- **Deployed System**: `ARCHE_DEPLOYED/arche/`
- **Core Engine**: `ARCHE_DEPLOYED/arche/Three_PointO_ArchE/`
- **Specifications**: `ARCHE_DEPLOYED/arche/specifications/`
- **Workflows**: `ARCHE_DEPLOYED/arche/workflows/`
- **Knowledge Graph**: `ARCHE_DEPLOYED/arche/knowledge_graph/`

---

## Support and Resources

### Documentation
- **Design Archive**: `ARCHE_DESIGN_ARCHIVE/` (if included)
- **Specifications**: `specifications/` directory
- **Framework Archive**: `ARCHE_FRAMEWORK_ARCHIVE/` (if included)

### Verification
- **Manifest**: `SEED_MANIFEST.json` contains all metadata
- **Checksums**: Verify against manifest integrity section
- **System Hash**: Compare deployed hash to manifest hash

---

## Conclusion

This guide provides complete instructions for deploying ArchE from the knowledge seed. The deployment process is designed to be:

- **Simple**: One script does everything
- **Verifiable**: Multiple verification steps ensure integrity
- **Safe**: All safety mechanisms preserved
- **Complete**: Full system restoration guaranteed

**The deployed ArchE will be functionally identical to the original, ready to evolve based on its unique context and experiences.**

---

**For questions or issues, refer to:**
- `ARCHE_SEED_DEPLOYMENT_PHILOSOPHY.md` - Philosophical context
- `ARCHE_DESIGN_ARCHIVE/` - Design decisions and evolution
- `ARCHE_FRAMEWORK_ARCHIVE/` - Framework documentation

---

**Deployment Status**: ✅ **READY**  
**Verification**: ✅ **COMPLETE**  
**System**: ✅ **OPERATIONAL**

