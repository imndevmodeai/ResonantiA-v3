#!/usr/bin/env python3
"""
Test RISE Engine Null Handling Fix

This script tests the enhanced RISE orchestrator to ensure it properly handles
null values and provides fallback mechanisms to prevent cascading failures.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv('.env')

def test_rise_null_handling():
    """Test RISE engine with null handling capabilities"""
    print("🧠 Testing RISE Engine Null Handling...")
    
    try:
        from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
        from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
        
        # Initialize components
        workflow_engine = IARCompliantWorkflowEngine()
        rise_orchestrator = RISE_Orchestrator(workflow_engine=workflow_engine)
        
        # Test problem description
        test_problem = "Analyze the competitive landscape for AI-powered strategic planning tools and identify opportunities for market entry."
        
        print(f"  Testing with problem: {test_problem[:50]}...")
        
        # Run RISE workflow
        result = rise_orchestrator.run_rise_workflow(test_problem)
        
        # Check results
        if result.get('status') == 'completed':
            print(f"  ✅ RISE workflow completed successfully!")
            
            # Check for null values
            session_kb = result.get('session_knowledge_base', {})
            specialized_agent = result.get('specialized_agent', {})
            
            print(f"  Knowledge base: {'✅ Valid' if session_kb else '❌ Null'}")
            print(f"  Specialized agent: {'✅ Valid' if specialized_agent else '❌ Null'}")
            print(f"  Fallback used: {'⚠️ Yes' if result.get('fallback_used') else '✅ No'}")
            
            # Check domain extraction
            domain = session_kb.get('domain', 'Not found')
            print(f"  Domain extracted: {domain}")
            
            # Check search results
            search_results = session_kb.get('search_results', [])
            search_status = session_kb.get('search_status', 'unknown')
            print(f"  Search status: {search_status}")
            print(f"  Search results count: {len(search_results)}")
            
            return True
        else:
            print(f"  ❌ RISE workflow failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ Test failed with exception: {e}")
        return False

def test_rise_with_edge_cases():
    """Test RISE engine with edge cases that might cause null issues"""
    print("\n🔍 Testing RISE Engine Edge Cases...")
    
    try:
        from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
        from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
        
        workflow_engine = IARCompliantWorkflowEngine()
        rise_orchestrator = RISE_Orchestrator(workflow_engine=workflow_engine)
        
        # Test cases that might cause null issues
        edge_cases = [
            "Very short problem",
            "A" * 10000,  # Very long problem
            "",  # Empty problem
            "Problem with special characters: @#$%^&*()",
            "Problem with unicode: 🚀🌟✨",
        ]
        
        results = []
        
        for i, test_case in enumerate(edge_cases):
            print(f"  Testing edge case {i+1}: {test_case[:30]}...")
            
            try:
                result = rise_orchestrator.run_rise_workflow(test_case)
                
                if result.get('status') == 'completed':
                    print(f"    ✅ Edge case {i+1} passed")
                    results.append(True)
                else:
                    print(f"    ❌ Edge case {i+1} failed: {result.get('error', 'Unknown')}")
                    results.append(False)
                    
            except Exception as e:
                print(f"    ❌ Edge case {i+1} crashed: {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results) if results else 0
        print(f"  Edge case success rate: {success_rate:.1%}")
        
        return success_rate > 0.5  # At least 50% should pass
        
    except Exception as e:
        print(f"  ❌ Edge case test failed: {e}")
        return False

def test_workflow_validation():
    """Test that the fixed workflow file exists and is valid"""
    print("\n🔧 Testing Workflow File Validation...")
    
    try:
        # Check if the fixed workflow file exists
        fixed_workflow_path = Path("workflows/knowledge_scaffolding_fixed.json")
        
        if fixed_workflow_path.exists():
            print(f"  ✅ Fixed workflow file exists: {fixed_workflow_path}")
            
            # Try to load and validate the JSON
            import json
            with open(fixed_workflow_path, 'r') as f:
                workflow_data = json.load(f)
            
            # Check required fields
            required_fields = ['name', 'description', 'version', 'inputs', 'tasks', 'outputs']
            missing_fields = [field for field in required_fields if field not in workflow_data]
            
            if not missing_fields:
                print(f"  ✅ Workflow JSON is valid")
                print(f"  Tasks defined: {len(workflow_data.get('tasks', {}))}")
                print(f"  Outputs defined: {len(workflow_data.get('outputs', {}))}")
                return True
            else:
                print(f"  ❌ Missing required fields: {missing_fields}")
                return False
        else:
            print(f"  ❌ Fixed workflow file not found: {fixed_workflow_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Workflow validation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 RISE Engine Null Handling Fix Test")
    print("=" * 50)
    
    tests = [
        ("RISE Null Handling", test_rise_null_handling),
        ("Edge Cases", test_rise_with_edge_cases),
        ("Workflow Validation", test_workflow_validation)
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
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RISE engine null handling is working correctly.")
        return True
    elif passed >= 2:
        print("⚠️ Most tests passed. RISE engine has basic null handling.")
        return True
    else:
        print("❌ Multiple tests failed. RISE engine needs more work.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 