#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_websocket():
    try:
        uri = "ws://localhost:3005"
        print(f"Attempting to connect to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established successfully!")
            
            # Send a test message
            test_message = "Hello ArchE!"
            print(f"Sending test message: {test_message}")
            await websocket.send(test_message)
            
            # Wait for response
            response = await websocket.recv()
            print(f"✅ Received response: {response}")
            
            # Send heartbeat
            print("Sending heartbeat...")
            await websocket.send("heartbeat")
            
            heartbeat_response = await websocket.recv()
            print(f"✅ Heartbeat response: {heartbeat_response}")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    if result:
        print("🎉 WebSocket server is working correctly!")
    else:
        print("💥 WebSocket server has issues!") 