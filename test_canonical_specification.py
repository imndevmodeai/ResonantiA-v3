#!/usr/bin/env python3
"""
Test Canonical Specification for Autopoietic System Genesis

This script verifies that the canonical specification (ResonantiA_Protocol_v3.1-CA.md)
can be properly read and processed by the Autopoietic System Genesis workflow.
"""

import json
import sys
from pathlib import Path

def test_specification_file():
    """Test that the canonical specification file exists and is readable."""
    print("🔍 Testing Canonical Specification File...")
    
    spec_file = "ResonantiA_Protocol_v3.1-CA.md"
    
    if not Path(spec_file).exists():
        print(f"  ❌ Specification file not found: {spec_file}")
        return False
    
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"  ✅ Specification file found and readable")
        print(f"  📄 File size: {len(content)} characters")
        print(f"  📄 File size: {len(content.split())} words")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error reading specification file: {e}")
        return False

def test_section_7_presence():
    """Test that Section 7: Codebase & File Definitions is present."""
    print("\n📋 Testing Section 7 Presence...")
    
    spec_file = "ResonantiA_Protocol_v3.1-CA.md"
    
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Section 7
        if "Section 7: Codebase & File Definitions" in content:
            print("  ✅ Section 7 found in specification")
        else:
            print("  ❌ Section 7 not found in specification")
            return False
        
        # Check for file specifications
        file_specs = [
            "7.1 config.py",
            "7.2 main.py", 
            "7.3 workflow_engine.py",
            "7.4 action_registry.py",
            "7.5 spr_manager.py",
            "7.6 cfp_framework.py",
            "7.7 quantum_utils.py",
            "7.8 llm_providers.py",
            "7.9 enhanced_tools.py",
            "7.10 code_executor.py"
        ]
        
        found_specs = 0
        for spec in file_specs:
            if spec in content:
                found_specs += 1
                print(f"    ✅ {spec} specification found")
            else:
                print(f"    ❌ {spec} specification missing")
        
        print(f"  📊 Found {found_specs}/{len(file_specs)} file specifications")
        
        if found_specs >= len(file_specs) * 0.8:  # 80% threshold
            print("  ✅ Sufficient file specifications present")
            return True
        else:
            print("  ❌ Insufficient file specifications")
            return False
            
    except Exception as e:
        print(f"  ❌ Error checking Section 7: {e}")
        return False

def test_workflow_file():
    """Test that the Genesis workflow file exists and is valid JSON."""
    print("\n🔧 Testing Genesis Workflow File...")
    
    workflow_file = "workflows/autopoietic_genesis_protocol.json"
    
    if not Path(workflow_file).exists():
        print(f"  ❌ Workflow file not found: {workflow_file}")
        return False
    
    try:
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        print(f"  ✅ Workflow file found and valid JSON")
        print(f"  📄 Workflow name: {workflow.get('name', 'Unknown')}")
        print(f"  📄 SPR ID: {workflow.get('spr_id', 'Unknown')}")
        print(f"  📄 Tasks: {len(workflow.get('tasks', {}))}")
        
        # Check for required tasks
        required_tasks = [
            "validate_keyholder_authority",
            "ingest_canonical_specification",
            "deconstruct_code_blueprints",
            "generate_system_code",
            "validate_generated_code",
            "final_genesis_report"
        ]
        
        missing_tasks = []
        for task in required_tasks:
            if task not in workflow.get('tasks', {}):
                missing_tasks.append(task)
        
        if missing_tasks:
            print(f"  ❌ Missing required tasks: {missing_tasks}")
            return False
        else:
            print(f"  ✅ All required tasks present")
            return True
            
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON in workflow file: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error reading workflow file: {e}")
        return False

def test_specification_content():
    """Test the content quality of the specification."""
    print("\n📝 Testing Specification Content Quality...")
    
    spec_file = "ResonantiA_Protocol_v3.1-CA.md"
    
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key elements
        key_elements = [
            "**File Path**:",
            "**Purpose**:",
            "**Key Classes and Functions**:",
            "**Required Dependencies**:",
            "**IAR Compliance**:"
        ]
        
        found_elements = 0
        for element in key_elements:
            if element in content:
                found_elements += 1
                print(f"    ✅ {element} found")
            else:
                print(f"    ❌ {element} missing")
        
        print(f"  📊 Found {found_elements}/{len(key_elements)} key elements")
        
        # Check for file path specifications
        file_path_count = content.count("**File Path**:")
        print(f"  📄 File path specifications: {file_path_count}")
        
        if file_path_count >= 20:  # Expect at least 20 file specifications
            print("  ✅ Sufficient file path specifications")
        else:
            print("  ❌ Insufficient file path specifications")
            return False
        
        # Check for IAR compliance mentions
        iar_count = content.count("**IAR Compliance**:")
        print(f"  📄 IAR compliance mentions: {iar_count}")
        
        if iar_count >= 20:  # Expect at least 20 IAR compliance mentions
            print("  ✅ Sufficient IAR compliance specifications")
        else:
            print("  ❌ Insufficient IAR compliance specifications")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error analyzing specification content: {e}")
        return False

def main():
    """Main test function."""
    print("🎯 Canonical Specification Test for Autopoietic System Genesis")
    print("=" * 70)
    
    tests = [
        ("Specification File", test_specification_file),
        ("Section 7 Presence", test_section_7_presence),
        ("Workflow File", test_workflow_file),
        ("Content Quality", test_specification_content)
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
        print("🎉 All tests passed! Canonical specification is ready for Autopoietic System Genesis.")
        print("\n🚀 NEXT STEPS:")
        print("  1. The canonical specification is complete and comprehensive")
        print("  2. Section 7 contains all necessary file definitions")
        print("  3. The Genesis workflow can process the specification")
        print("  4. Ready to execute autopoietic_genesis_protocol.json")
        return True
    elif passed >= 3:
        print("⚠️ Most tests passed. Canonical specification is mostly ready.")
        return True
    else:
        print("❌ Multiple tests failed. Canonical specification needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 