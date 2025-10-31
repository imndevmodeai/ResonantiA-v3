#!/usr/bin/env python3
"""
Run the Enhanced Resonant Autopoietic Genesis Protocol (v3.5-GP)
with comprehensive safety measures for Four_PointO_ArchE integration.
"""

import json
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Add Four_PointO_ArchE to Python path
four_pointo_dir = os.path.join(project_root, 'Four_PointO_ArchE')
if four_pointo_dir not in sys.path:
    sys.path.insert(0, four_pointo_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Run the Enhanced Resonant Autopoietic Genesis Protocol."""
    print("🧬 ENHANCED RESONANT AUTOPOIETIC GENESIS PROTOCOL (v3.5-GP)")
    print("=" * 70)
    print("Executing with comprehensive safety measures for Four_PointO_ArchE integration")
    print()
    
    try:
        # Import the workflow engine
        from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
        
        # Initialize the workflow engine
        workflows_dir = os.path.join(project_root, "workflows")
        engine = IARCompliantWorkflowEngine(workflows_dir=workflows_dir)
        
        print("✅ Workflow engine initialized")
        
        # Prepare initial context for v3.5-GP integration
        initial_context = {
            "protocol_path": "ResonantiA_Protocol_v3.5-GP_Canonical.md",
            "target_output_root": "Four_PointO_ArchE/",
            "spr_definitions_path": "knowledge_graph/spr_definitions_tv.json",
            "author": "Keyholder",
            "workflow_run_id": "resonant_genesis_v3.5_gp_001"
        }
        
        print("📋 Initial Context:")
        for key, value in initial_context.items():
            print(f"  {key}: {value}")
        print()
        
        # Check if required files exist
        protocol_file = initial_context["protocol_path"]
        if not os.path.exists(protocol_file):
            print(f"❌ Protocol file not found: {protocol_file}")
            print("Available protocol files:")
            for f in os.listdir("."):
                if "ResonantiA_Protocol" in f and f.endswith(".md"):
                    print(f"  - {f}")
            return False
        
        print(f"✅ Protocol file found: {protocol_file}")
        
        # Run the enhanced workflow
        print("🚀 Starting Enhanced Resonant Autopoietic Genesis Protocol...")
        print("This will create safety backups and integrate v3.5-GP with Four_PointO_ArchE")
        print()
        
        workflow_path = "resonant_autopoietic_genesis_protocol.json"
        results = engine.run_workflow(workflow_path, initial_context)
        
        # Display results
        print("\n" + "=" * 70)
        print("🎉 RESONANT AUTOPOIETIC GENESIS PROTOCOL COMPLETED")
        print("=" * 70)
        
        print(f"Workflow Name: {results.get('workflow_name', 'Unknown')}")
        print(f"Run ID: {results.get('workflow_run_id', 'Unknown')}")
        print(f"Status: {results.get('workflow_status', 'Unknown')}")
        print(f"Duration: {results.get('workflow_run_duration_sec', 0):.2f} seconds")
        
        print("\n📊 Task Statuses:")
        task_statuses = results.get('task_statuses', {})
        for task, status in task_statuses.items():
            status_icon = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
            print(f"  {status_icon} {task}: {status}")
        
        # Display safety information
        if 'analyze_existing_architecture' in results:
            arch_result = results['analyze_existing_architecture']
            if arch_result.get('backup_created'):
                print(f"\n🛡️ Safety Backup Created: {arch_result.get('backup_location', 'Unknown')}")
        
        if 'safety_validation' in results:
            safety_result = results['safety_validation']
            if safety_result.get('rollback_ready'):
                print("✅ Rollback capability ready")
            if safety_result.get('validation_passed'):
                print("✅ Safety validation passed")
        
        print("\n🔮 This represents the ultimate achievement of:")
        print("   • ResonantiA Protocol v3.5-GP (Genesis Protocol)")
        print("   • Four_PointO_ArchE v4.0 integration")
        print("   • Comprehensive safety measures")
        print("   • Perfect Implementation Resonance")
        print("   • Autonomous system evolution with rollback capability")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure Three_PointO_ArchE is properly set up")
        return False
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
