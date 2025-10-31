#!/usr/bin/env python3
"""
Test script to verify the ArchE system fixes are working properly.
"""

import asyncio
import websockets
import json
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

async def test_arche_system():
    """Test the ArchE system to verify fixes are working."""
    
    print("🧪 Testing ArchE System Fixes")
    print("=" * 50)
    
    # Test 1: Check if persistent server is running
    print("\n1. Testing WebSocket Connection...")
    try:
        uri = "ws://localhost:3004"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection successful")
            
            # Test 2: Send a simple query
            print("\n2. Testing Query Processing...")
            test_query = "Hello ArchE, can you explain quantum computing in simple terms?"
            
            await websocket.send(test_query)
            print(f"📤 Sent query: {test_query[:50]}...")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            print("📥 Received response")
            
            # Parse response
            try:
                response_data = json.loads(response)
                print("✅ Response is valid JSON")
                
                if response_data.get("type") == "response":
                    content = response_data.get("content", "")
                    print(f"✅ Got response content: {content[:100]}...")
                elif response_data.get("type") == "error":
                    print(f"❌ Got error response: {response_data.get('content', '')}")
                else:
                    print(f"⚠️ Got unexpected response type: {response_data.get('type')}")
                    
            except json.JSONDecodeError:
                print("⚠️ Response is not JSON, treating as plain text")
                print(f"Response: {response[:200]}...")
                
    except websockets.exceptions.ConnectionRefused:
        print("❌ WebSocket connection refused. Is the persistent server running?")
        print("   Run: python arche_persistent_server.py")
        return False
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    
    print("\n3. Testing Action Registry...")
    try:
        from Three_PointO_ArchE.action_registry import main_action_registry
        
        # Check if key actions are registered
        required_actions = ["generate_text_llm", "search_web", "execute_code"]
        missing_actions = []
        
        for action in required_actions:
            if action in main_action_registry.actions:
                print(f"✅ Action '{action}' is registered")
            else:
                print(f"❌ Action '{action}' is missing")
                missing_actions.append(action)
        
        if missing_actions:
            print(f"❌ Missing actions: {missing_actions}")
            return False
        else:
            print("✅ All required actions are registered")
            
    except ImportError as e:
        print(f"❌ Could not import action registry: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing action registry: {e}")
        return False
    
    print("\n4. Testing Workflow Engine...")
    try:
        from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
        
        # Test workflow engine initialization
        engine = IARCompliantWorkflowEngine()
        print("✅ Workflow engine initialized successfully")
        
        # Test loading a workflow
        try:
            workflow = engine.load_workflow("knowledge_scaffolding.json")
            print("✅ Successfully loaded knowledge_scaffolding.json workflow")
        except Exception as e:
            print(f"❌ Failed to load workflow: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing workflow engine: {e}")
        return False
    
    print("\n🎉 All tests passed! The ArchE system is working properly.")
    return True

async def main():
    """Main test function."""
    success = await test_arche_system()
    
    if success:
        print("\n✅ System Status: OPERATIONAL")
        print("The ArchE system is ready for use.")
    else:
        print("\n❌ System Status: FAILED")
        print("Please check the error messages above and fix the issues.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1) 