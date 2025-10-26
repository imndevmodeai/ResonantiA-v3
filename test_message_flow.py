#!/usr/bin/env python3
import asyncio
import websockets
import json
import os

async def test_message_flow():
    # Get WebSocket URL from environment or use default
    uri = os.environ.get('WEBSOCKET_URL', f"ws://localhost:{os.environ.get('ARCHE_PORT', 3005)}")
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            # Send a test message
            message = "Hello ArchE, this is a test message."
            await websocket.send(message)
            print(f"Sent message: {message}")
            
            # Receive response
            response = await websocket.recv()
            print(f"Received response: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_message_flow()) 