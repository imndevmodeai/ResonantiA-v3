#!/usr/bin/env python3
"""
Test WebSocket Server on Port 3004
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_port_3004():
    """Test WebSocket server on port 3004"""
    uri = "ws://localhost:3004"
    
    try:
        logger.info(f"🔗 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected successfully to port 3004!")
            
            # Send a simple test message
            test_message = {
                "type": "test",
                "content": "Hello from test client",
                "metadata": {
                    "timestamp": int(asyncio.get_event_loop().time() * 1000),
                    "test_id": "port_3004_test"
                }
            }
            
            logger.info("📤 Sending test message...")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            logger.info("📥 Waiting for response...")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                logger.info(f"📨 Response received: {response}")
                logger.info("✅ Port 3004 WebSocket server is working correctly!")
            except asyncio.TimeoutError:
                logger.warning("⏰ No response received within 5 seconds")
                
    except Exception as e:
        logger.error(f"❌ Error connecting to {uri}: {e}")
        logger.info("💡 Make sure the WebSocket server is running on port 3004")

if __name__ == "__main__":
    asyncio.run(test_port_3004()) 