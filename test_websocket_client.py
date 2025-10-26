#!/usr/bin/env python3
"""
Simple WebSocket test client to verify server communication.
This will help isolate whether the issue is in the server or the frontend.
"""

import asyncio
import json
import websockets
from datetime import datetime

async def test_websocket_communication():
    uri = "ws://localhost:8765"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Listen for initial messages
            print("Waiting for initial messages...")
            try:
                initial_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received initial: {initial_message}")
            except asyncio.TimeoutError:
                print("⚠️  No initial message received")
            
            # Send a test message
            test_message = {
                "content": "Hello from test client",
                "timestamp": datetime.now().isoformat()
            }
            print(f"📤 Sending: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for responses
            print("Waiting for responses...")
            response_count = 0
            while response_count < 3:  # Expect welcome, response, and thought trail
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    print(f"📥 Response {response_count + 1}: {response}")
                    
                    # Parse and analyze the response
                    try:
                        parsed = json.loads(response)
                        if parsed.get("type") == "nexus_event":
                            print(f"   🧠 Nexus event - topic: {parsed.get('event', {}).get('topic')}")
                        else:
                            print(f"   💬 Chat message - content: {parsed.get('content')}")
                    except json.JSONDecodeError:
                        print(f"   ⚠️  Non-JSON response: {response}")
                    
                    response_count += 1
                    
                except asyncio.TimeoutError:
                    print(f"⏰ Timeout waiting for response {response_count + 1}")
                    break
            
            print("✅ Test completed!")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    print("🧪 WebSocket Communication Test")
    print("=" * 40)
    asyncio.run(test_websocket_communication())

