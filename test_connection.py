#!/usr/bin/env python3
import asyncio
import websockets
import os

async def test_connection():
    # Get WebSocket URL from environment or use default
    uri = os.environ.get('WEBSOCKET_URL', f"ws://localhost:{os.environ.get('ARCHE_PORT', 3005)}")
    
    print(f"Testing connection to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connection successful!")
            
            # Send a simple ping
            await websocket.send("heartbeat")
            print("📤 Sent heartbeat")
            
            # Wait for pong response
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection()) 