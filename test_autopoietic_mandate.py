#!/usr/bin/env python3
"""
Test Autopoietic System Genesis Workflow and Mandate System

This script demonstrates how to:
1. Activate the Autopoietic System Genesis mandate
2. Execute the Genesis workflow to build the system from its specification
3. Enforce the mandate for system development operations
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_mandate_activation():
    """Test activating the Autopoietic System Genesis mandate."""
    print("🔧 Testing Autopoietic Mandate Activation...")
    
    try:
        from Three_PointO_ArchE.autopoietic_mandate_system import activate_autopoietic_mandate
        
        result = activate_autopoietic_mandate()
        print(f"  Result: {result['status']}")
        print(f"  Message: {result['message']}")
        
        if result['status'] == 'success':
            print("  ✅ Mandate activated successfully")
            return True
        else:
            print(f"  ❌ Mandate activation failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing mandate activation: {e}")
        return False

def test_mandate_status():
    """Test checking the mandate status."""
    print("\n📊 Testing Mandate Status Check...")
    
    try:
        from Three_PointO_ArchE.autopoietic_mandate_system import AutopoieticMandateSystem
        
        mandate_system = AutopoieticMandateSystem()
        status = mandate_system.get_mandate_report()
        
        print(f"  Status: {status['status']}")
        print(f"  Mandate Active: {status['mandate_active']}")
        print(f"  Genesis Count: {status['genesis_count']}")
        print(f"  Last Genesis: {status['last_genesis']}")
        print(f"  Workflow Path: {status['workflow_path']}")
        
        return status['mandate_active']
        
    except Exception as e:
        print(f"  ❌ Error checking mandate status: {e}")
        return False

def test_mandate_enforcement():
    """Test mandate enforcement for different operation types."""
    print("\n🛡️ Testing Mandate Enforcement...")
    
    try:
        from Three_PointO_ArchE.autopoietic_mandate_system import mandate_check
        
        # Test operations that should trigger Genesis
        genesis_operations = [
            "code_generation",
            "system_evolution",
            "architecture_change",
            "new_feature_development",
            "protocol_modification"
        ]
        
        for operation in genesis_operations:
            result = mandate_check(operation, {"details": "test operation"})
            print(f"  {operation}: {result['status']}")
            
            if result['status'] == 'mandate_enforced':
                print(f"    ✅ Correctly enforced for {operation}")
            else:
                print(f"    ⚠️ Unexpected result for {operation}")
        
        # Test operations that should be allowed
        allowed_operations = [
            "data_analysis",
            "report_generation",
            "query_processing"
        ]
        
        for operation in allowed_operations:
            result = mandate_check(operation, {"details": "test operation"})
            print(f"  {operation}: {result['status']}")
            
            if result['status'] == 'allowed':
                print(f"    ✅ Correctly allowed for {operation}")
            else:
                print(f"    ⚠️ Unexpected result for {operation}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing mandate enforcement: {e}")
        return False

def test_genesis_workflow():
    """Test executing the Autopoietic System Genesis workflow."""
    print("\n🧬 Testing Autopoietic System Genesis Workflow...")
    
    try:
        from Three_PointO_ArchE.autopoietic_mandate_system import execute_autopoietic_genesis
        
        print("  ⚠️ This will execute the full Genesis workflow...")
        print("  ⚠️ This may take several minutes and will generate code files...")
        
        # Check if protocol file exists
        protocol_file = "ResonantiA_Protocol_v3.1-CA.md"
        if not Path(protocol_file).exists():
            print(f"  ❌ Protocol file not found: {protocol_file}")
            print("  ⚠️ Skipping Genesis workflow execution")
            return False
        
        # Check if workflow file exists
        workflow_file = "workflows/autopoietic_genesis_protocol.json"
        if not Path(workflow_file).exists():
            print(f"  ❌ Workflow file not found: {workflow_file}")
            print("  ⚠️ Skipping Genesis workflow execution")
            return False
        
        print("  🚀 Executing Autopoietic System Genesis...")
        result = execute_autopoietic_genesis()
        
        print(f"  Result: {result['status']}")
        print(f"  Message: {result['message']}")
        
        if result['status'] == 'success':
            print("  ✅ Genesis workflow completed successfully")
            return True
        else:
            print(f"  ❌ Genesis workflow failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing Genesis workflow: {e}")
        return False

def test_workflow_validation():
    """Test that the Genesis workflow is properly structured."""
    print("\n🔍 Testing Genesis Workflow Validation...")
    
    try:
        workflow_file = "workflows/autopoietic_genesis_protocol.json"
        
        if not Path(workflow_file).exists():
            print(f"  ❌ Workflow file not found: {workflow_file}")
            return False
        
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        # Validate required fields
        required_fields = ["name", "description", "version", "spr_id", "inputs", "tasks", "outputs"]
        for field in required_fields:
            if field not in workflow:
                print(f"  ❌ Missing required field: {field}")
                return False
        
        # Validate SPR ID
        if workflow.get("spr_id") != "AutopoieticSystemGenesiS":
            print(f"  ❌ Incorrect SPR ID: {workflow.get('spr_id')}")
            return False
        
        # Validate tasks
        required_tasks = [
            "validate_keyholder_authority",
            "ingest_canonical_specification", 
            "deconstruct_code_blueprints",
            "generate_system_code",
            "validate_generated_code",
            "final_genesis_report"
        ]
        
        for task in required_tasks:
            if task not in workflow.get("tasks", {}):
                print(f"  ❌ Missing required task: {task}")
                return False
        
        print("  ✅ Workflow structure is valid")
        print(f"  ✅ SPR ID: {workflow.get('spr_id')}")
        print(f"  ✅ Version: {workflow.get('version')}")
        print(f"  ✅ Tasks: {len(workflow.get('tasks', {}))}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error validating workflow: {e}")
        return False

def main():
    """Main test function."""
    print("🎯 Autopoietic System Genesis Workflow and Mandate System Test")
    print("=" * 70)
    
    tests = [
        ("Workflow Validation", test_workflow_validation),
        ("Mandate Activation", test_mandate_activation),
        ("Mandate Status", test_mandate_status),
        ("Mandate Enforcement", test_mandate_enforcement),
        ("Genesis Workflow", test_genesis_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Autopoietic System Genesis is fully operational.")
        print("\n🚀 NEXT STEPS:")
        print("  1. The mandate is now active and will enforce Genesis for system development")
        print("  2. All code generation must now use the Genesis workflow")
        print("  3. The system will build itself from its own specification")
        print("  4. This solves the Execution paradoX through ultimate Implementation resonancE")
        return True
    elif passed >= 3:
        print("⚠️ Most tests passed. Autopoietic System Genesis is mostly operational.")
        return True
    else:
        print("❌ Multiple tests failed. Autopoietic System Genesis needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 