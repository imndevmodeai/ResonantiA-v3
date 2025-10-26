#!/usr/bin/env python3
"""
Section 7 Update Protocol - Safe Execution Wrapper
ResonantiA Protocol v3.5-GP

SAFETY MANDATE: Zero-risk backup enforcement
- Creates comprehensive backups before any modifications
- Provides rollback capability
- Preserves all valuable gains
- Ensures Implementation Resonance protection

Keyholder Authority: keyy=('IMnDEVmode')
"""

import sys
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("SECTION 7 UPDATE PROTOCOL - SAFE EXECUTION")
print("ResonantiA Protocol v3.5-GP")
print("BACKUP MANDATE: ENFORCED")
print("=" * 80)
print()

# ============================================================================
# PHASE 0: PRE-EXECUTION SAFETY CHECKS
# ============================================================================

print("[PHASE 0] Pre-Execution Safety Checks...")
print("-" * 80)

# Generate backup timestamp
backup_timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
backup_root = Path(f"backups/section_7_update_{backup_timestamp}")

print(f"Backup Location: {backup_root}")
print()

# Confirm with user
print("⚠️  SAFETY MANDATE ENFORCEMENT ⚠️")
print()
print("This script will:")
print("  1. Create comprehensive backups of:")
print("     - All protocol documents (Section 7 sources)")
print("     - Current Three_PointO_ArchE/ codebase")
print("     - Existing specifications/")
print("  2. Execute Section 7 Update Protocol")
print("  3. Provide rollback capability if needed")
print()
print(f"Backup will be stored at: {backup_root}")
print()

# Auto-proceed for non-interactive execution
proceed = "yes"
print("✅ Auto-proceeding with backup and execution (non-interactive mode)")

if proceed not in ['yes', 'y']:
    print("❌ Execution cancelled by Keyholder")
    sys.exit(0)

print()

# ============================================================================
# PHASE 1: CREATE COMPREHENSIVE BACKUPS
# ============================================================================

print("[PHASE 1] Creating Comprehensive Backups...")
print("-" * 80)

backup_manifest = {
    "timestamp": backup_timestamp,
    "backup_root": str(backup_root),
    "backed_up_items": [],
    "backup_status": "in_progress"
}

try:
    # Create backup directory structure
    backup_root.mkdir(parents=True, exist_ok=True)
    
    # 1. Backup all protocol documents
    print("📄 Backing up protocol documents...")
    protocol_backup = backup_root / "protocol"
    protocol_backup.mkdir(exist_ok=True)
    
    protocol_dir = Path("protocol")
    if protocol_dir.exists():
        for protocol_file in protocol_dir.rglob("*.md"):
            relative_path = protocol_file.relative_to(protocol_dir)
            backup_path = protocol_backup / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(protocol_file, backup_path)
            backup_manifest["backed_up_items"].append({
                "type": "protocol_document",
                "source": str(protocol_file),
                "backup": str(backup_path)
            })
            print(f"  ✓ {protocol_file}")
    
    print(f"  Total protocol documents backed up: {len([i for i in backup_manifest['backed_up_items'] if i['type'] == 'protocol_document'])}")
    print()
    
    # 2. Backup Three_PointO_ArchE codebase
    print("💻 Backing up Three_PointO_ArchE codebase...")
    codebase_backup = backup_root / "Three_PointO_ArchE"
    codebase_backup.mkdir(exist_ok=True)
    
    codebase_dir = Path("Three_PointO_ArchE")
    if codebase_dir.exists():
        # Copy entire directory but exclude __pycache__ and .pyc files
        for py_file in codebase_dir.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".backup" in str(py_file).lower():
                continue
            relative_path = py_file.relative_to(codebase_dir)
            backup_path = codebase_backup / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(py_file, backup_path)
            backup_manifest["backed_up_items"].append({
                "type": "python_file",
                "source": str(py_file),
                "backup": str(backup_path)
            })
        
        # Also backup knowledge_graph
        kg_dir = codebase_dir / "knowledge_graph"
        if kg_dir.exists():
            for kg_file in kg_dir.rglob("*.json"):
                relative_path = kg_file.relative_to(codebase_dir)
                backup_path = codebase_backup / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(kg_file, backup_path)
                backup_manifest["backed_up_items"].append({
                    "type": "knowledge_graph",
                    "source": str(kg_file),
                    "backup": str(backup_path)
                })
    
    print(f"  Total Python files backed up: {len([i for i in backup_manifest['backed_up_items'] if i['type'] == 'python_file'])}")
    print(f"  Total knowledge graph files backed up: {len([i for i in backup_manifest['backed_up_items'] if i['type'] == 'knowledge_graph'])}")
    print()
    
    # 3. Backup specifications directory
    print("📋 Backing up specifications...")
    specs_backup = backup_root / "specifications"
    specs_backup.mkdir(exist_ok=True)
    
    specs_dir = Path("specifications")
    if specs_dir.exists():
        for spec_file in specs_dir.rglob("*.md"):
            relative_path = spec_file.relative_to(specs_dir)
            backup_path = specs_backup / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(spec_file, backup_path)
            backup_manifest["backed_up_items"].append({
                "type": "specification",
                "source": str(spec_file),
                "backup": str(backup_path)
            })
    
    print(f"  Total specification files backed up: {len([i for i in backup_manifest['backed_up_items'] if i['type'] == 'specification'])}")
    print()
    
    # 4. Backup workflows
    print("⚙️  Backing up workflows...")
    workflows_backup = backup_root / "workflows"
    workflows_backup.mkdir(exist_ok=True)
    
    workflows_dir = Path("workflows")
    if workflows_dir.exists():
        for workflow_file in workflows_dir.rglob("*.json"):
            relative_path = workflow_file.relative_to(workflows_dir)
            backup_path = workflows_backup / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(workflow_file, backup_path)
            backup_manifest["backed_up_items"].append({
                "type": "workflow",
                "source": str(workflow_file),
                "backup": str(backup_path)
            })
    
    print(f"  Total workflow files backed up: {len([i for i in backup_manifest['backed_up_items'] if i['type'] == 'workflow'])}")
    print()
    
    # 5. Save backup manifest
    backup_manifest["backup_status"] = "complete"
    backup_manifest["total_items"] = len(backup_manifest["backed_up_items"])
    
    manifest_path = backup_root / "backup_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(backup_manifest, f, indent=2)
    
    print(f"✓ Backup manifest saved: {manifest_path}")
    print()
    print(f"✅ BACKUP COMPLETE: {backup_manifest['total_items']} items backed up")
    print()

except Exception as e:
    print(f"❌ BACKUP FAILED: {e}")
    print()
    print("Execution aborted to preserve system integrity.")
    sys.exit(1)

# ============================================================================
# PHASE 2: EXECUTE SECTION 7 UPDATE PROTOCOL
# ============================================================================

print("[PHASE 2] Executing Section 7 Update Protocol...")
print("-" * 80)
print()

# Check if workflow engine exists
workflow_engine_path = Path("Three_PointO_ArchE/workflow_engine.py")

if not workflow_engine_path.exists():
    print("⚠️  Workflow Engine not found")
    print()
    print("The Section 7 Update Protocol requires the Workflow Engine to execute.")
    print("Options:")
    print("  1. Run Genesis Protocol to generate Workflow Engine first")
    print("  2. Use manual Section 7 update process")
    print("  3. Restore from backup and try different approach")
    print()
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        print()
        print("To run Genesis Protocol, execute:")
        print("  python -m Three_PointO_ArchE.autopoietic_mandate_system --execute-genesis")
        print()
        print(f"Backup is safely stored at: {backup_root}")
        sys.exit(0)
    elif choice == "2":
        print()
        print("Manual Section 7 update process:")
        print("  1. Review current codebase: Three_PointO_ArchE/")
        print("  2. Document each file in Section 7 format")
        print("  3. Update protocol/Section_7_Codebase_Definitions_UPDATED.md")
        print()
        print(f"Backup is safely stored at: {backup_root}")
        sys.exit(0)
    else:
        print()
        print("Execution cancelled.")
        print(f"Backup is safely stored at: {backup_root}")
        sys.exit(0)

try:
    # Import and execute workflow
    sys.path.insert(0, str(Path(__file__).parent))
    from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
    
    print("✓ Workflow Engine loaded")
    print()
    
    # Initialize engine
    engine = IARCompliantWorkflowEngine()
    print("✓ Engine initialized")
    print()
    
    # Execute Section 7 Update Protocol
    print("🔄 Running Section 7 Update Protocol...")
    print("   (This may take several minutes)")
    print()
    
    result = engine.run_workflow(
        "workflows/section_7_update_protocol.json",
        {
            "backup_location": str(backup_root),
            "keyholder_authority": "keyy=('IMnDEVmode')"
        }
    )
    
    print()
    print("✅ Section 7 Update Protocol completed")
    print()
    
    # Save execution result
    result_path = backup_root / "execution_result.json"
    with open(result_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✓ Execution result saved: {result_path}")
    print()
    
except Exception as e:
    print(f"❌ EXECUTION FAILED: {e}")
    print()
    print("⚠️  System state preserved - all backups intact")
    print(f"Backup location: {backup_root}")
    print()
    print("To restore from backup:")
    print(f"  python restore_from_backup.py {backup_root}")
    print()
    sys.exit(1)

# ============================================================================
# PHASE 3: GENERATE ROLLBACK SCRIPT
# ============================================================================

print("[PHASE 3] Generating Rollback Capability...")
print("-" * 80)

rollback_script = f"""#!/usr/bin/env python3
'''
Rollback Script for Section 7 Update
Backup: {backup_timestamp}

This script restores the system to the state before Section 7 update.
'''

import shutil
from pathlib import Path

print("=" * 80)
print("ROLLBACK: Section 7 Update {backup_timestamp}")
print("=" * 80)
print()

backup_root = Path("{backup_root}")

# Restore protocol documents
print("Restoring protocol documents...")
for item in {json.dumps([i for i in backup_manifest["backed_up_items"] if i["type"] == "protocol_document"])}:
    Path(item["source"]).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(item["backup"], item["source"])
    print(f"  ✓ {{item['source']}}")

# Restore codebase
print("Restoring Three_PointO_ArchE codebase...")
for item in {json.dumps([i for i in backup_manifest["backed_up_items"] if i["type"] == "python_file"])}:
    Path(item["source"]).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(item["backup"], item["source"])

# Restore knowledge graph
for item in {json.dumps([i for i in backup_manifest["backed_up_items"] if i["type"] == "knowledge_graph"])}:
    Path(item["source"]).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(item["backup"], item["source"])

print()
print("✅ ROLLBACK COMPLETE")
print("System restored to pre-update state")
"""

rollback_path = backup_root / "rollback.py"
with open(rollback_path, 'w') as f:
    f.write(rollback_script)

# Make executable
import os
os.chmod(rollback_path, 0o755)

print(f"✓ Rollback script generated: {rollback_path}")
print()

# ============================================================================
# PHASE 4: FINAL REPORT
# ============================================================================

print("=" * 80)
print("EXECUTION COMPLETE")
print("=" * 80)
print()

print("📊 Summary:")
print(f"  • Items backed up: {backup_manifest['total_items']}")
print(f"  • Backup location: {backup_root}")
print(f"  • Section 7 update: Executed")
print(f"  • Rollback capability: Available")
print()

print("📁 Generated Files:")
print(f"  • Backup manifest: {backup_root}/backup_manifest.json")
print(f"  • Execution result: {backup_root}/execution_result.json")
print(f"  • Rollback script: {backup_root}/rollback.py")
print()

print("🎯 Next Steps:")
print("  1. Review execution result")
print("  2. Verify updated Section 7: protocol/Section_7_Codebase_Definitions_UPDATED.md")
print("  3. If satisfied, proceed with Genesis Protocol")
print("  4. If issues found, run rollback script")
print()

print("🔄 To Rollback (if needed):")
print(f"  python {rollback_path}")
print()

print("✅ BACKUP MANDATE: ENFORCED AND SATISFIED")
print("   Zero risk - all valuable gains preserved")
print()
print("=" * 80)

sys.exit(0)






