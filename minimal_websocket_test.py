#!/usr/bin/env python3
import asyncio
import websockets

async def minimal_test():
    try:
        print("🔗 Attempting connection...")
        websocket = await websockets.connect('ws://localhost:3005')
        print("✅ Connected successfully!")
        
        print("📤 Sending heartbeat...")
        await websocket.send("heartbeat")
        print("📤 Heartbeat sent")
        
        print("📥 Waiting for response...")
        response = await websocket.recv()
        print(f"📨 Response: {response}")
        
        await websocket.close()
        print("🔌 Connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(minimal_test()) 