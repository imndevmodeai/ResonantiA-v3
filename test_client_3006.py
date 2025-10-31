#!/usr/bin/env python3
"""
Test client for port 3006
"""

import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection():
    """Test WebSocket connection"""
    uri = "ws://localhost:3004"
    
    try:
        logger.info(f"🔗 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected successfully!")
            
            # Send a test message
            test_message = "Hello from test client"
            logger.info(f"📤 Sending: {test_message}")
            await websocket.send(test_message)
            
            # Wait for response
            logger.info("📥 Waiting for response...")
            response = await websocket.recv()
            logger.info(f"📥 Received: {response}")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection()) 