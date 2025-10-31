#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_websocket_detailed():
    try:
        uri = "ws://localhost:3005"
        print(f"Attempting to connect to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established successfully!")
            
            # Send a test message
            test_message = "Hello ArchE!"
            print(f"Sending test message: {test_message}")
            await websocket.send(test_message)
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"✅ Received response: {response}")
                
                # Try to parse as JSON
                try:
                    parsed = json.loads(response)
                    print(f"✅ Parsed JSON: {json.dumps(parsed, indent=2)}")
                except json.JSONDecodeError:
                    print(f"⚠️ Response is not valid JSON: {response}")
                    
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for response")
                return False
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_websocket_detailed())
    if result:
        print("🎉 WebSocket server is working correctly!")
    else:
        print("💥 WebSocket server has issues!") 