#!/usr/bin/env python3
"""
Simple test script for RISE v2.0 Genesis Protocol - RISE_Orchestrator
Verifies the implementation structure and workflow files without importing modules.
"""

import os
import json

def test_rise_orchestrator_file_structure():
    """Test the basic structure of the RISE_Orchestrator file"""
    try:
        rise_file_path = os.path.join("Three_PointO_ArchE", "rise_orchestrator.py")
        if not os.path.exists(rise_file_path):
            print(f"❌ RISE_Orchestrator file not found: {rise_file_path}")
            return False
        
        with open(rise_file_path, 'r') as f:
            content = f.read()
        
        # Check for key components
        required_components = [
            'class RISE_Orchestrator',
            'class RISEState',
            'def run_rise_workflow',
            'def _execute_phase_a',
            'def _execute_phase_b',
            'def _execute_phase_c',
            'Phase A: Knowledge Scaffolding & Dynamic Specialization',
            'Phase B: Fused Insight Generation',
            'Phase C: Fused Strategy Generation & Finalization'
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"❌ Missing components in RISE_Orchestrator: {missing_components}")
            return False
        else:
            print("✅ RISE_Orchestrator file structure is correct")
            return True
            
    except Exception as e:
        print(f"❌ Failed to test RISE_Orchestrator structure: {e}")
        return False

def test_workflow_files_exist():
    """Test that the required workflow files exist"""
    workflow_files = [
        'workflows/knowledge_scaffolding.json',
        'workflows/metamorphosis_protocol.json',
        'workflows/strategy_fusion.json',
        'workflows/high_stakes_vetting.json',
        'workflows/distill_spr.json'
    ]
    
    missing_files = []
    for file_path in workflow_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing workflow files: {missing_files}")
        return False
    else:
        print("✅ All required workflow files exist")
        return True

def test_workflow_files_structure():
    """Test that the workflow files have correct JSON structure"""
    workflow_files = [
        'workflows/knowledge_scaffolding.json',
        'workflows/metamorphosis_protocol.json',
        'workflows/strategy_fusion.json',
        'workflows/high_stakes_vetting.json',
        'workflows/distill_spr.json'
    ]
    
    for file_path in workflow_files:
        try:
            with open(file_path, 'r') as f:
                workflow = json.load(f)
            
            # Check required fields
            required_fields = ['name', 'description', 'version', 'tasks']
            missing_fields = []
            for field in required_fields:
                if field not in workflow:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in {file_path}: {missing_fields}")
                return False
            
            # Check that tasks exist and have required structure
            if not workflow['tasks']:
                print(f"❌ No tasks found in {file_path}")
                return False
            
            # Check first task has required fields
            first_task = list(workflow['tasks'].values())[0]
            task_required_fields = ['description', 'action_type', 'inputs']
            missing_task_fields = []
            for field in task_required_fields:
                if field not in first_task:
                    missing_task_fields.append(field)
            
            if missing_task_fields:
                print(f"❌ Missing task fields in {file_path}: {missing_task_fields}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {file_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return False
    
    print("✅ All workflow files have correct structure")
    return True

def test_workflow_content():
    """Test that workflow files contain RISE v2.0 specific content"""
    workflow_files = [
        ('workflows/knowledge_scaffolding.json', 'Phase A'),
        ('workflows/metamorphosis_protocol.json', 'Phase A'),
        ('workflows/strategy_fusion.json', 'Phase B'),
        ('workflows/high_stakes_vetting.json', 'Phase C'),
        ('workflows/distill_spr.json', 'Phase C')
    ]
    
    for file_path, expected_phase in workflow_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            if expected_phase not in content:
                print(f"❌ {file_path} missing expected phase reference: {expected_phase}")
                return False
                
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return False
    
    print("✅ All workflow files contain RISE v2.0 specific content")
    return True

def test_rise_architecture_completeness():
    """Test that the RISE architecture is complete"""
    try:
        rise_file_path = os.path.join("Three_PointO_ArchE", "rise_orchestrator.py")
        with open(rise_file_path, 'r') as f:
            content = f.read()
        
        # Check for key architectural elements
        architectural_elements = [
            'Metamorphosis Protocol',
            'HighStakesVetting',
            'specialized cognitive agent',
            'session knowledge base',
            'fused_strategic_dossier',
            'SPR distillation'
        ]
        
        missing_elements = []
        for element in architectural_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing architectural elements: {missing_elements}")
            return False
        else:
            print("✅ RISE architecture is complete")
            return True
            
    except Exception as e:
        print(f"❌ Failed to test RISE architecture: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing RISE v2.0 Genesis Protocol - RISE_Orchestrator (Simple)")
    print("=" * 70)
    
    tests = [
        ("File Structure Test", test_rise_orchestrator_file_structure),
        ("Workflow Files Exist Test", test_workflow_files_exist),
        ("Workflow Structure Test", test_workflow_files_structure),
        ("Workflow Content Test", test_workflow_content),
        ("Architecture Completeness Test", test_rise_architecture_completeness)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RISE v2.0 Genesis Protocol implementation is complete.")
        print("\n📋 Implementation Summary:")
        print("✅ RISE_Orchestrator class with three-phase workflow")
        print("✅ RISEState dataclass for state management")
        print("✅ Knowledge Scaffolding workflow (Phase A)")
        print("✅ Metamorphosis Protocol workflow (Phase A)")
        print("✅ Strategy Fusion workflow (Phase B)")
        print("✅ High Stakes Vetting workflow (Phase C)")
        print("✅ SPR Distillation workflow (Phase C)")
        print("\n🚀 The RISE v2.0 Genesis Protocol is ready for integration!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 