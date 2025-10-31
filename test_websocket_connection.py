#!/usr/bin/env python3
"""
Test WebSocket Connection
Simple test to verify the ArchE WebSocket server is working
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Test connection to the ArchE WebSocket server"""
    uri = "ws://localhost:3005"
    
    try:
        print(f"🔗 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to ArchE WebSocket server!")
            
            # Wait for welcome message
            try:
                welcome = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Welcome message: {welcome}")
            except asyncio.TimeoutError:
                print("⚠️ No welcome message received")
            
            # Send a test message
            test_message = {
                "type": "query",
                "content": "Hello ArchE! This is a test message.",
                "metadata": {
                    "test": True,
                    "timestamp": "test"
                }
            }
            
            print(f"📤 Sending test message: {json.dumps(test_message)}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📨 Response received: {response}")
                
                # Try to parse as JSON
                try:
                    response_data = json.loads(response)
                    print(f"✅ JSON response: {json.dumps(response_data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"📝 Text response: {response}")
                    
            except asyncio.TimeoutError:
                print("⚠️ No response received within timeout")
            
            # Send heartbeat
            print("💓 Sending heartbeat...")
            await websocket.send("heartbeat")
            
            try:
                heartbeat_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"💓 Heartbeat response: {heartbeat_response}")
            except asyncio.TimeoutError:
                print("⚠️ No heartbeat response received")
                
            print("✅ WebSocket test completed successfully!")
            
    except ConnectionRefusedError:
        print("❌ Connection refused. Is the WebSocket server running on port 3005?")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 