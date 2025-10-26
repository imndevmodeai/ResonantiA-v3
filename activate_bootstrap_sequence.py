#!/usr/bin/env python3
"""
Bootstrap Sequence Activation
ResonantiA Protocol v3.5-GP

This script activates the foundational components needed for ArchE to assist
in its own repair and evolution:
1. VettingAgent - Quality assurance system
2. Autopoietic Genesis Protocol - Self-building capability

Once activated, ArchE can validate its own work and generate missing components.
"""

import sys
import json
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
print("BOOTSTRAP SEQUENCE ACTIVATION")
print("ResonantiA Protocol v3.5-GP")
print("=" * 80)
print()

# ============================================================================
# PHASE 1: VALIDATE CRITICAL COMPONENTS EXIST
# ============================================================================

print("[PHASE 1] Validating Critical Components...")
print("-" * 80)

critical_components = {
    "VettingAgent": "Three_PointO_ArchE/vetting_agent.py",
    "Autopoietic Mandate System": "Three_PointO_ArchE/autopoietic_mandate_system.py",
    "Genesis Workflow": "workflows/autopoietic_genesis_protocol.json",
    "Temporal Core": "Three_PointO_ArchE/temporal_core.py",
    "IAR Components": "Three_PointO_ArchE/iar_components.py",
    "Action Context": "Three_PointO_ArchE/action_context.py"
}

validation_results = {}
all_present = True

for component_name, component_path in critical_components.items():
    exists = Path(component_path).exists()
    validation_results[component_name] = exists
    status = "✓" if exists else "✗"
    print(f"{status} {component_name}: {component_path}")
    if not exists:
        all_present = False

print()
if all_present:
    print("✓ All critical components present")
else:
    print("✗ Missing critical components - Genesis Protocol can regenerate them")

print()

# ============================================================================
# PHASE 2: TEST VETTING AGENT
# ============================================================================

print("[PHASE 2] Testing VettingAgent...")
print("-" * 80)

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from Three_PointO_ArchE.vetting_agent import (
        VettingAgent,
        VettingStatus,
        AxiomaticKnowledgeBase
    )
    from Three_PointO_ArchE.action_context import ActionContext
    
    print("✓ VettingAgent imported successfully")
    
    # Create vetting agent
    agent = VettingAgent()
    print("✓ VettingAgent instantiated")
    
    # Test vetting on a safe action
    context = ActionContext(
        task_key="bootstrap_test",
        workflow_id="bootstrap_sequence",
        objective="Test vetting system during bootstrap"
    )
    
    result = agent.perform_vetting(
        "read_file",
        {"path": "test.txt"},
        context
    )
    
    print(f"✓ Vetting test complete")
    print(f"  Status: {result.status.value}")
    print(f"  Cognitive Resonance: {result.cognitive_resonance:.2f}")
    print(f"  Reasoning: {result.reasoning}")
    
    vetting_agent_operational = True
    
except Exception as e:
    print(f"✗ VettingAgent test failed: {e}")
    vetting_agent_operational = False

print()

# ============================================================================
# PHASE 3: TEST AUTOPOIETIC MANDATE SYSTEM
# ============================================================================

print("[PHASE 3] Testing Autopoietic Mandate System...")
print("-" * 80)

try:
    from Three_PointO_ArchE.autopoietic_mandate_system import (
        AutopoieticMandateSystem,
        activate_autopoietic_mandate
    )
    
    print("✓ Autopoietic Mandate System imported successfully")
    
    # Create mandate system
    mandate_system = AutopoieticMandateSystem()
    print("✓ Mandate System instantiated")
    
    # Check current status
    status = mandate_system.get_mandate_report()
    print(f"✓ Mandate Status: {status['status']}")
    print(f"  Genesis Count: {status['genesis_count']}")
    print(f"  Mandate Active: {status['mandate_active']}")
    
    mandate_system_operational = True
    
except Exception as e:
    print(f"✗ Mandate System test failed: {e}")
    mandate_system_operational = False

print()

# ============================================================================
# PHASE 4: ACTIVATE MANDATE (OPTIONAL)
# ============================================================================

print("[PHASE 4] Mandate Activation (Optional)...")
print("-" * 80)
print("The Autopoietic Mandate can be activated to enforce Genesis Protocol")
print("for all system development. This is optional during bootstrap.")
print()

activate_mandate = input("Activate Autopoietic Mandate? (y/N): ").strip().lower()

if activate_mandate == 'y':
    try:
        result = activate_autopoietic_mandate()
        if result['status'] == 'success':
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Activation failed: {result['message']}")
    except Exception as e:
        print(f"✗ Activation error: {e}")
else:
    print("○ Mandate activation skipped")

print()

# ============================================================================
# PHASE 5: GENERATE BOOTSTRAP REPORT
# ============================================================================

print("[PHASE 5] Generating Bootstrap Report...")
print("-" * 80)

bootstrap_report = {
    "bootstrap_timestamp": datetime.utcnow().isoformat() + "Z",
    "protocol_version": "ResonantiA v3.5-GP",
    "validation": {
        "critical_components": validation_results,
        "all_components_present": all_present
    },
    "operational_status": {
        "vetting_agent": vetting_agent_operational,
        "mandate_system": mandate_system_operational,
        "mandate_activated": activate_mandate == 'y'
    },
    "capabilities": {
        "can_validate_work": vetting_agent_operational,
        "can_self_repair": mandate_system_operational and all_present,
        "can_assist_repair": vetting_agent_operational or mandate_system_operational
    },
    "next_steps": []
}

# Determine next steps
if not all_present:
    bootstrap_report["next_steps"].append(
        "Run Genesis Protocol to regenerate missing components"
    )

if not vetting_agent_operational:
    bootstrap_report["next_steps"].append(
        "Fix VettingAgent import/instantiation issues"
    )

if not mandate_system_operational:
    bootstrap_report["next_steps"].append(
        "Fix Autopoietic Mandate System issues"
    )

if vetting_agent_operational and mandate_system_operational and all_present:
    bootstrap_report["next_steps"].append(
        "Bootstrap complete - ArchE can now assist in self-repair"
    )

# Save report
report_path = Path("logs/bootstrap_report.json")
report_path.parent.mkdir(parents=True, exist_ok=True)

with open(report_path, 'w') as f:
    json.dump(bootstrap_report, f, indent=2)

print(f"✓ Report saved to: {report_path}")

print()

# ============================================================================
# PHASE 6: FINAL STATUS
# ============================================================================

print("=" * 80)
print("BOOTSTRAP SEQUENCE COMPLETE")
print("=" * 80)
print()

if bootstrap_report["capabilities"]["can_self_repair"]:
    print("✓ STATUS: FULLY OPERATIONAL")
    print()
    print("ArchE can now:")
    print("  • Validate its own work via VettingAgent")
    print("  • Generate missing components via Genesis Protocol")
    print("  • Assist in self-repair and evolution")
    print()
    print("Next: Use ArchE to identify and repair any system gaps")
    
elif bootstrap_report["capabilities"]["can_assist_repair"]:
    print("○ STATUS: PARTIALLY OPERATIONAL")
    print()
    print("Some components are functional. ArchE can assist in repair but")
    print("may need manual intervention for full capability restoration.")
    print()
    print("Next Steps:")
    for step in bootstrap_report["next_steps"]:
        print(f"  • {step}")
    
else:
    print("✗ STATUS: BOOTSTRAP FAILED")
    print()
    print("Critical components are not operational. Manual repair required.")
    print()
    print("Required Actions:")
    for step in bootstrap_report["next_steps"]:
        print(f"  • {step}")

print()
print("=" * 80)

# Exit with appropriate code
if bootstrap_report["capabilities"]["can_self_repair"]:
    sys.exit(0)
elif bootstrap_report["capabilities"]["can_assist_repair"]:
    sys.exit(1)
else:
    sys.exit(2)









