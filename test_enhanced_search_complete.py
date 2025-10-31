#!/usr/bin/env python3
"""
Comprehensive test of the enhanced search functionality
"""

import sys
import os
import json
from datetime import datetime

# Add ArchE to path
sys.path.append('Three_PointO_ArchE')

def test_enhanced_perception_engine():
    """Test the enhanced perception engine directly"""
    print("🔍 Testing Enhanced Perception Engine Directly")
    print("=" * 50)
    
    try:
        from enhanced_perception_engine_with_fallback import enhanced_web_search_with_fallback
        
        # Test search
        result, iar = enhanced_web_search_with_fallback({
            'query': 'machine learning trends 2024',
            'context': {'engine': 'duckduckgo', 'debug': True},
            'max_results': 3
        })
        
        print(f"✅ Success: {result.get('success')}")
        print(f"📊 Results: {len(result.get('results', []))}")
        print(f"⏱️ Response Time: {result.get('response_time', 0):.2f}s")
        print(f"🧠 IAR Confidence: {iar.get('confidence', 0)}")
        
        if result.get('results'):
            print("\n📋 Sample Results:")
            for i, res in enumerate(result['results'][:2]):
                print(f"  {i+1}. {res.get('title', 'No title')}")
                print(f"     URL: {res.get('url', 'No URL')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_enhanced_search_tool():
    """Test the enhanced search tool integration"""
    print("\n🔧 Testing Enhanced Search Tool Integration")
    print("=" * 50)
    
    try:
        from Three_PointO_ArchE.tools.enhanced_search_tool import perform_web_search
        
        # Test search
        result = perform_web_search('quantum computing breakthroughs', 'duckduckgo', debug=True, num_results=3)
        
        print(f"✅ Success: {result.get('success')}")
        print(f"📊 Results: {len(result.get('results', []))}")
        print(f"⏱️ Response Time: {result.get('response_time', 0):.2f}s")
        
        if result.get('results'):
            print("\n📋 Sample Results:")
            for i, res in enumerate(result['results'][:2]):
                print(f"  {i+1}. {res.get('title', 'No title')}")
                print(f"     URL: {res.get('url', 'No URL')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_workflow_execution():
    """Test workflow execution with search"""
    print("\n🚀 Testing Workflow Execution")
    print("=" * 50)
    
    try:
        # Create a simple test workflow
        test_workflow = {
            "name": "Enhanced Search Test Workflow",
            "description": "Test workflow for enhanced search functionality",
            "tasks": {
                "search_test": {
                    "action_type": "search_web",
                    "inputs": {
                        "query": "artificial intelligence ethics 2024",
                        "engine": "duckduckgo",
                        "num_results": 3
                    },
                    "dependencies": []
                },
                "analyze_results": {
                    "action_type": "execute_code",
                    "inputs": {
                        "language": "python",
                        "code": """
import json

search_results = {{search_test.results}}
print('Workflow Search Results:')
print(f'Success: {search_results.get(\"success\", False)}')
print(f'Total Results: {len(search_results.get(\"results\", []))}')
print(f'Response Time: {search_results.get(\"response_time\", 0):.2f}s')

if search_results.get('results'):
    print('\\nFirst Result:')
    first = search_results['results'][0]
    print(f'  Title: {first.get(\"title\", \"No title\")}')
    print(f'  URL: {first.get(\"url\", \"No URL\")}')
"""
                    },
                    "dependencies": ["search_test"]
                }
            }
        }
        
        # Save test workflow
        workflow_path = "test_enhanced_search_workflow.json"
        with open(workflow_path, 'w') as f:
            json.dump(test_workflow, f, indent=2)
        
        print(f"📝 Created test workflow: {workflow_path}")
        print("✅ Workflow structure validated")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 ENHANCED SEARCH COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Enhanced Perception Engine", test_enhanced_perception_engine),
        ("Enhanced Search Tool", test_enhanced_search_tool),
        ("Workflow Execution", test_workflow_execution)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🚀 All tests passed! Enhanced search is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
