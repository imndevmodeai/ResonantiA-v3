#!/usr/bin/env python3
import asyncio
import websockets

async def test():
    try:
        async with websockets.connect('ws://localhost:3005') as websocket:
            print("✅ Connected successfully!")
            await websocket.send("heartbeat")
            response = await websocket.recv()
            print(f"📨 Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(test()) 