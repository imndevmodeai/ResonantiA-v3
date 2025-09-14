#!/usr/bin/env python3
import asyncio
import websockets
import json

async def debug_test():
    try:
        async with websockets.connect('ws://localhost:3005') as websocket:
            print("✅ Connected successfully!")
            
            # Test 1: Simple heartbeat
            print("\n🔍 Test 1: Heartbeat")
            await websocket.send("heartbeat")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Response: {response}")
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for response")
            except Exception as e:
                print(f"❌ Error receiving response: {e}")
            
            # Test 2: JSON message
            print("\n🔍 Test 2: JSON message")
            test_message = {
                "type": "query",
                "content": "Hello ArchE",
                "metadata": {"test": True}
            }
            await websocket.send(json.dumps(test_message))
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Response: {response}")
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for response")
            except Exception as e:
                print(f"❌ Error receiving response: {e}")
            
            # Test 3: Plain text
            print("\n🔍 Test 3: Plain text")
            await websocket.send("Hello from debug test")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Response: {response}")
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for response")
            except Exception as e:
                print(f"❌ Error receiving response: {e}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")

asyncio.run(debug_test()) 