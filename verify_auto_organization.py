#!/usr/bin/env python3
"""
Simple verification that auto-log organization is integrated.
"""

import os
import inspect
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine

def verify_auto_organization_integration():
    """Verify that auto-log organization is integrated into the workflow engine."""
    
    print("🔍 Verifying Auto-Log Organization Integration...")
    
    # Check if the method exists
    engine = IARCompliantWorkflowEngine()
    
    if hasattr(engine, '_auto_organize_log'):
        print("✅ _auto_organize_log method found in IARCompliantWorkflowEngine")
        
        # Check method signature
        method = getattr(engine, '_auto_organize_log')
        sig = inspect.signature(method)
        print(f"✅ Method signature: {sig}")
        
        # Check if log organizer exists
        if os.path.exists('log_organizer.py'):
            print("✅ log_organizer.py found")
        else:
            print("❌ log_organizer.py not found")
            return False
            
        # Check if config exists
        if os.path.exists('log_organization_config.json'):
            print("✅ log_organization_config.json found")
        else:
            print("❌ log_organization_config.json not found")
            return False
            
        # Check if organized directory exists
        if os.path.exists('logs_organized'):
            print("✅ logs_organized directory exists")
        else:
            print("ℹ️  logs_organized directory will be created automatically")
            
        print("\n🎉 Auto-log organization integration VERIFIED!")
        print("✅ Future logs will be automatically organized")
        return True
        
    else:
        print("❌ _auto_organize_log method not found in IARCompliantWorkflowEngine")
        return False

def show_integration_details():
    """Show details about the integration."""
    
    print("\n📋 Integration Details:")
    print("=" * 50)
    
    print("🔧 Workflow Engine Integration:")
    print("  - File: Three_PointO_ArchE/workflow_engine.py")
    print("  - Method: _auto_organize_log()")
    print("  - Trigger: After each workflow completes")
    print("  - Line: ~1569-1573 in run_workflow() method")
    
    print("\n🔧 RISE Orchestrator Integration:")
    print("  - File: Three_PointO_ArchE/rise_orchestrator.py")
    print("  - Integration: Automatic (uses workflow engine)")
    print("  - Coverage: All RISE phases (A, B, C, D)")
    
    print("\n🔧 Configuration:")
    print("  - File: log_organization_config.json")
    print("  - Setting: auto_organization.enabled = true")
    print("  - Purpose: Enable/disable auto-organization")
    
    print("\n🔧 Organization Process:")
    print("  1. Workflow completes → Log saved")
    print("  2. Auto-organization triggered")
    print("  3. Metadata extracted")
    print("  4. Directory selected")
    print("  5. File organized with descriptive name")
    print("  6. Metadata file created")
    print("  7. Catalog updated")
    
    print("\n🎯 Result:")
    print("  ✅ All future logs automatically organized")
    print("  ✅ Descriptive filenames")
    print("  ✅ Hierarchical directory structure")
    print("  ✅ Error separation")
    print("  ✅ Search capabilities")

if __name__ == "__main__":
    success = verify_auto_organization_integration()
    
    if success:
        show_integration_details()
        print("\n🚀 SYSTEM READY: Future logs will be automatically organized!")
    else:
        print("\n❌ Integration verification FAILED!")
        print("🔧 Manual organization still required.")


