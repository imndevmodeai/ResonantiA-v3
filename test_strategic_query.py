#!/usr/bin/env python3
import asyncio
import websockets
import json
import os

async def test_strategic_query():
    # Get WebSocket URL from environment or use default
    uri = os.environ.get('WEBSOCKET_URL', f"ws://localhost:{os.environ.get('ARCHE_PORT', 3005)}")
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            # Send a strategic query
            query = "Analyze the current geopolitical landscape and provide strategic insights."
            await websocket.send(query)
            print(f"Sent query: {query}")
            
            # Receive response
            response = await websocket.recv()
            print(f"Received response: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_strategic_query()) 