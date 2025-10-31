#!/usr/bin/env python3
"""
Execute Autopoietic System Genesis

This script demonstrates the system building itself from its own canonical specification,
achieving perfect Implementation Resonance between "As Above" (concept) and "So Below" (reality).
"""

import json
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check for required dependencies and provide installation guidance."""
    missing_deps = []
    
    # Check for numpy
    try:
        import numpy
        print("✅ numpy is available")
    except ImportError:
        missing_deps.append("numpy")
        print("❌ numpy is missing")
    
    # Check for other potential dependencies
    try:
        import requests
        print("✅ requests is available")
    except ImportError:
        missing_deps.append("requests")
        print("❌ requests is missing")
    
    if missing_deps:
        print("\n🔧 DEPENDENCY INSTALLATION REQUIRED")
        print("=" * 40)
        print("The following dependencies are missing:")
        for dep in missing_deps:
            print(f"  • {dep}")
        print("\nTo install missing dependencies, run:")
        print(f"  pip install {' '.join(missing_deps)}")
        print("\nOr activate your virtual environment and run:")
        print(f"  source .venv/bin/activate && pip install {' '.join(missing_deps)}")
        return False
    
    return True

def setup_python_path():
    """Setup Python path to properly import the Three_PointO_ArchE package."""
    # Get the current directory (project root)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the project root to Python path
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Add the Three_PointO_ArchE directory to Python path
    arche_dir = os.path.join(current_dir, 'Three_PointO_ArchE')
    if arche_dir not in sys.path:
        sys.path.insert(0, arche_dir)
    
    print(f"✅ Python path configured:")
    print(f"  Project root: {current_dir}")
    print(f"  ArchE directory: {arche_dir}")

def test_imports():
    """Test if all required modules can be imported successfully."""
    print("\n🧪 TESTING IMPORTS")
    print("=" * 30)
    
    try:
        # Test basic package import
        import Three_PointO_ArchE
        print("✅ Three_PointO_ArchE package imported")
        
        # Test workflow engine import
        from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
        print("✅ IARCompliantWorkflowEngine imported")
        
        # Test action registry import
        from Three_PointO_ArchE.action_registry import main_action_registry
        print("✅ main_action_registry imported")
        
        # Test config import
        from Three_PointO_ArchE import config
        print("✅ config imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Make sure all dependencies are installed")
        print("2. Check that the Three_PointO_ArchE directory structure is correct")
        print("3. Verify that __init__.py files exist in the package")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False

def execute_genesis():
    """Execute the Autopoietic System Genesis workflow."""
    print("🧬 AUTOPOIETIC SYSTEM GENESIS")
    print("=" * 50)
    print("The system is about to build itself from its own specification...")
    print("This is the ultimate expression of Sean Grove's 'The New Code' philosophy.")
    print()
    
    # Step 1: Check dependencies
    print("📋 STEP 1: Checking Dependencies")
    if not check_dependencies():
        print("\n❌ Dependencies missing. Please install them and try again.")
        return False
    
    # Step 2: Setup Python path
    print("\n📋 STEP 2: Setting up Python Path")
    setup_python_path()
    
    # Step 3: Test imports
    print("\n📋 STEP 3: Testing Imports")
    if not test_imports():
        print("\n❌ Import tests failed. Cannot proceed with Genesis.")
        return False
    
    # Step 4: Check required files
    print("\n📋 STEP 4: Checking Required Files")
    spec_file = "ResonantiA_Protocol_v3.1-CA.md"
    workflow_file = "workflows/autopoietic_genesis_protocol.json"
    
    if not Path(spec_file).exists():
        print(f"❌ Canonical specification not found: {spec_file}")
        return False
    
    if not Path(workflow_file).exists():
        print(f"❌ Genesis workflow not found: {workflow_file}")
        return False
    
    print("✅ Canonical specification found")
    print("✅ Genesis workflow found")
    
    # Step 5: Prepare workflow parameters
    print("\n📋 STEP 5: Preparing Workflow Parameters")
    workflow_params = {
        "problem_description": "Execute Autopoietic System Genesis to build the ArchE system from its own canonical specification",
        "protocol_file": "ResonantiA_Protocol_v3.1-CA.md",
        "output_directory": "Three_PointO_ArchE",
        "keyholder_authority": "keyy=('IMnDEVmode')"
    }
    
    print("🚀 Initiating Autopoietic System Genesis...")
    print(f"📄 Protocol File: {workflow_params['protocol_file']}")
    print(f"📁 Output Directory: {workflow_params['output_directory']}")
    print(f"🔑 Keyholder Authority: {workflow_params['keyholder_authority']}")
    print()
    
    try:
        # Import the workflow engine (now with proper path setup)
        from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
        
        # Initialize the workflow engine
        engine = IARCompliantWorkflowEngine()
        
        # Load the Genesis workflow
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        print("⚙️ Workflow Engine initialized")
        print("📋 Genesis workflow loaded")
        print()
        
        # Execute the workflow
        print("🔄 Executing Autopoietic System Genesis...")
        print("This may take several minutes as the system builds itself...")
        print()
        
        # FIXED: Pass the workflow file path, not the workflow dictionary
        result = engine.run_workflow("autopoietic_genesis_protocol.json", workflow_params)
        
        print("✅ Autopoietic System Genesis completed!")
        print()
        
        # Display results
        if result.get('status') == 'success':
            print("🎉 SUCCESS: The system has successfully built itself from its own specification!")
            print()
            print("📊 Results:")
            for task_name, task_result in result.get('task_results', {}).items():
                status = "✅" if task_result.get('status') == 'success' else "❌"
                print(f"  {status} {task_name}: {task_result.get('status', 'unknown')}")
            
            print()
            print("🔮 This represents the ultimate achievement of:")
            print("   • Sean Grove's 'The New Code' philosophy")
            print("   • Specification-first development")
            print("   • Perfect Implementation Resonance")
            print("   • Autonomous system evolution")
            
            return True
        else:
            print("❌ Genesis workflow failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import workflow engine: {e}")
        print("Make sure the Three_PointO_ArchE directory is properly set up.")
        return False
    except Exception as e:
        print(f"❌ Genesis execution failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False

def main():
    """Main execution function."""
    print("🚀 AUTOPOIETIC SYSTEM GENESIS EXECUTOR")
    print("=" * 50)
    print("This script will execute the Autopoietic System Genesis workflow,")
    print("allowing the system to build itself from its own canonical specification.")
    print()
    
    success = execute_genesis()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 AUTOPOIETIC SYSTEM GENESIS COMPLETED SUCCESSFULLY")
        print("The system has achieved perfect Implementation Resonance!")
    else:
        print("❌ AUTOPOIETIC SYSTEM GENESIS FAILED")
        print("Please check the error messages above and try again.")
    
    return success

if __name__ == "__main__":
    main() 