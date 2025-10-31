#!/usr/bin/env python3
"""
Test script for RISE v2.0 Genesis Protocol - RISE_Orchestrator
Verifies that the orchestrator can be imported and initialized correctly.
"""

import sys
import os

# Add the Three_PointO_ArchE directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Three_PointO_ArchE'))

def test_rise_orchestrator_import():
    """Test that the RISE_Orchestrator can be imported successfully"""
    try:
        # Try direct import first
        import rise_orchestrator
        from rise_orchestrator import RISE_Orchestrator, RISEState
        print("✅ Successfully imported RISE_Orchestrator and RISEState")
        return True
    except ImportError as e:
        print(f"❌ Failed to import RISE_Orchestrator: {e}")
        # Try alternative import method
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "rise_orchestrator", 
                os.path.join("Three_PointO_ArchE", "rise_orchestrator.py")
            )
            rise_orchestrator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(rise_orchestrator)
            RISE_Orchestrator = rise_orchestrator.RISE_Orchestrator
            RISEState = rise_orchestrator.RISEState
            print("✅ Successfully imported RISE_Orchestrator using alternative method")
            return True
        except Exception as e2:
            print(f"❌ Alternative import also failed: {e2}")
            return False

def test_rise_orchestrator_initialization():
    """Test that the RISE_Orchestrator can be initialized"""
    try:
        # Get the RISE_Orchestrator class
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "rise_orchestrator", 
            os.path.join("Three_PointO_ArchE", "rise_orchestrator.py")
        )
        rise_orchestrator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rise_orchestrator)
        RISE_Orchestrator = rise_orchestrator.RISE_Orchestrator
        
        # Initialize the orchestrator
        orchestrator = RISE_Orchestrator()
        print("✅ Successfully initialized RISE_Orchestrator")
        
        # Check that required attributes exist
        assert hasattr(orchestrator, 'workflows_dir'), "Missing workflows_dir attribute"
        assert hasattr(orchestrator, 'spr_manager'), "Missing spr_manager attribute"
        assert hasattr(orchestrator, 'workflow_engine'), "Missing workflow_engine attribute"
        assert hasattr(orchestrator, 'thought_trail'), "Missing thought_trail attribute"
        assert hasattr(orchestrator, 'phases'), "Missing phases attribute"
        assert hasattr(orchestrator, 'active_sessions'), "Missing active_sessions attribute"
        assert hasattr(orchestrator, 'execution_history'), "Missing execution_history attribute"
        
        print("✅ All required attributes present")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize RISE_Orchestrator: {e}")
        return False

def test_rise_state_creation():
    """Test that RISEState can be created"""
    try:
        # Get the RISEState class
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "rise_orchestrator", 
            os.path.join("Three_PointO_ArchE", "rise_orchestrator.py")
        )
        rise_orchestrator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rise_orchestrator)
        RISEState = rise_orchestrator.RISEState
        from datetime import datetime
        
        # Create a test state
        state = RISEState(
            problem_description="Test problem",
            session_id="test_session",
            current_phase="A",
            phase_start_time=datetime.utcnow(),
            session_knowledge_base={},
            specialized_agent=None,
            advanced_insights=[],
            specialist_consultation=None,
            fused_strategic_dossier=None,
            vetting_dossier=None,
            final_strategy=None,
            spr_definition=None,
            execution_metrics={}
        )
        
        print("✅ Successfully created RISEState")
        
        # Test to_dict method
        state_dict = state.to_dict()
        assert isinstance(state_dict, dict), "to_dict() should return a dictionary"
        print("✅ RISEState.to_dict() works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create RISEState: {e}")
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

def test_rise_orchestrator_structure():
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
            'def _execute_phase_c'
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

def main():
    """Run all tests"""
    print("🧪 Testing RISE v2.0 Genesis Protocol - RISE_Orchestrator")
    print("=" * 60)
    
    tests = [
        ("File Structure Test", test_rise_orchestrator_structure),
        ("Import Test", test_rise_orchestrator_import),
        ("Initialization Test", test_rise_orchestrator_initialization),
        ("State Creation Test", test_rise_state_creation),
        ("Workflow Files Test", test_workflow_files_exist)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RISE_Orchestrator is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 