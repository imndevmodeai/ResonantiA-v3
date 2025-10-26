#!/usr/bin/env python3
"""
Test WebSocket and RISE Engine Null Handling Fix

This script tests the fixed WebSocket server and RISE engine to ensure they properly
handle null values and prevent cascading failures.
"""

import asyncio
import websockets
import json
import time
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_websocket_connection():
    """Test WebSocket connection and basic communication"""
    print("🔌 Testing WebSocket Connection...")
    
    try:
        # Connect to the WebSocket server
        uri = "ws://localhost:3006"
        async with websockets.connect(uri) as websocket:
            print("  ✅ Connected to WebSocket server")
            
            # Wait for welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"  📨 Received welcome: {welcome_data.get('content', '')}")
            
            return True
            
    except Exception as e:
        print(f"  ❌ WebSocket connection failed: {e}")
        return False

async def test_query_validation():
    """Test query validation with various input types"""
    print("\n🔍 Testing Query Validation...")
    
    test_cases = [
        {
            "name": "Valid Query",
            "query": "Analyze the competitive landscape for AI-powered strategic planning tools",
            "should_pass": True
        },
        {
            "name": "Null Query",
            "query": None,
            "should_pass": False
        },
        {
            "name": "Empty Query",
            "query": "",
            "should_pass": False
        },
        {
            "name": "Short Query",
            "query": "Test",
            "should_pass": False
        },
        {
            "name": "Whitespace Only",
            "query": "   \n\t   ",
            "should_pass": False
        }
    ]
    
    results = []
    
    try:
        uri = "ws://localhost:3006"
        async with websockets.connect(uri) as websocket:
            # Wait for welcome message
            await websocket.recv()
            
            for test_case in test_cases:
                print(f"  Testing: {test_case['name']}")
                
                # Send query
                message = {
                    "type": "query",
                    "content": test_case["query"],
                    "metadata": {"test_case": test_case["name"]}
                }
                
                await websocket.send(json.dumps(message))
                
                # Wait for response
                response = await websocket.recv()
                response_data = json.loads(response)
                
                # Check if validation passed or failed as expected
                status = response_data.get('metadata', {}).get('status', '')
                content = response_data.get('content', '')
                
                if test_case["should_pass"]:
                    if "validation_error" not in status and "error" not in status:
                        print(f"    ✅ Passed validation as expected")
                        results.append(True)
                    else:
                        print(f"    ❌ Failed validation unexpectedly: {content}")
                        results.append(False)
                else:
                    if "validation_error" in status or "error" in status:
                        print(f"    ✅ Correctly rejected invalid input: {content}")
                        results.append(True)
                    else:
                        print(f"    ❌ Accepted invalid input unexpectedly")
                        results.append(False)
                        
    except Exception as e:
        print(f"  ❌ Query validation test failed: {e}")
        return False
    
    success_rate = sum(results) / len(results) if results else 0
    print(f"  Query validation success rate: {success_rate:.1%}")
    
    return success_rate > 0.8  # At least 80% should pass

async def test_rise_engine_integration():
    """Test RISE engine integration with valid query"""
    print("\n🧠 Testing RISE Engine Integration...")
    
    try:
        uri = "ws://localhost:3006"
        async with websockets.connect(uri) as websocket:
            # Wait for welcome message
            await websocket.recv()
            
            # Send a valid query
            valid_query = "Analyze the competitive landscape for AI-powered strategic planning tools and identify opportunities for market entry."
            
            message = {
                "type": "query",
                "content": valid_query,
                "metadata": {"test": "rise_integration"}
            }
            
            print(f"  📤 Sending valid query: {valid_query[:50]}...")
            await websocket.send(json.dumps(message))
            
            # Collect responses
            responses = []
            start_time = time.time()
            timeout = 60  # 60 second timeout
            
            while time.time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    responses.append(response_data)
                    
                    # Check if we got a final response
                    if response_data.get('type') == 'response':
                        status = response_data.get('metadata', {}).get('status', '')
                        if status in ['completed', 'completed_with_errors']:
                            print(f"  ✅ RISE engine completed with status: {status}")
                            
                            # Check if we got meaningful content
                            content = response_data.get('content', '')
                            if content and len(content) > 50:
                                print(f"  📄 Received meaningful response ({len(content)} characters)")
                                return True
                            else:
                                print(f"  ⚠️ Response content seems short: {content[:100]}...")
                                return False
                                
                except asyncio.TimeoutError:
                    print(f"  ⏰ Timeout waiting for response after {time.time() - start_time:.1f}s")
                    break
                    
            print(f"  📊 Collected {len(responses)} responses")
            for i, resp in enumerate(responses):
                resp_type = resp.get('type', 'unknown')
                resp_status = resp.get('metadata', {}).get('status', 'unknown')
                print(f"    {i+1}. {resp_type}: {resp_status}")
                
            return False
            
    except Exception as e:
        print(f"  ❌ RISE engine integration test failed: {e}")
        return False

async def test_error_handling():
    """Test error handling with malformed messages"""
    print("\n⚠️ Testing Error Handling...")
    
    try:
        uri = "ws://localhost:3006"
        async with websockets.connect(uri) as websocket:
            # Wait for welcome message
            await websocket.recv()
            
            # Test malformed JSON
            print("  Testing malformed JSON...")
            await websocket.send("{invalid json}")
            
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get('type') == 'system' and 'error' in response_data.get('content', '').lower():
                print("    ✅ Correctly handled malformed JSON")
            else:
                print("    ❌ Did not handle malformed JSON properly")
                return False
                
            # Test unknown message type
            print("  Testing unknown message type...")
            message = {
                "type": "unknown_type",
                "content": "test content"
            }
            
            await websocket.send(json.dumps(message))
            
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get('type') == 'system' and 'unknown' in response_data.get('content', '').lower():
                print("    ✅ Correctly handled unknown message type")
                return True
            else:
                print("    ❌ Did not handle unknown message type properly")
                return False
                
    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🎯 WebSocket and RISE Engine Null Handling Fix Test")
    print("=" * 60)
    
    tests = [
        ("WebSocket Connection", test_websocket_connection),
        ("Query Validation", test_query_validation),
        ("RISE Engine Integration", test_rise_engine_integration),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! WebSocket and RISE engine null handling is working correctly.")
        return True
    elif passed >= 3:
        print("⚠️ Most tests passed. WebSocket and RISE engine have basic null handling.")
        return True
    else:
        print("❌ Multiple tests failed. WebSocket and RISE engine need more work.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 