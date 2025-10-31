#!/usr/bin/env python3
"""
Function-based WebSocket Server Test
"""

import asyncio
import websockets
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global client set
clients = set()

async def websocket_handler(websocket, path):
    """WebSocket handler function"""
    logger.info(f"🔗 New connection from {websocket.remote_address}")
    clients.add(websocket)
    
    try:
        async for message in websocket:
            logger.info(f"📝 Received: {message}")
            response = f"Echo: {message}"
            await websocket.send(response)
    except websockets.exceptions.ConnectionClosed:
        logger.info("🔌 Connection closed")
    finally:
        clients.remove(websocket)

async def start_server():
    """Start the WebSocket server"""
    host = 'localhost'
    port = 3005
    
    logger.info(f"🚀 Starting function-based WebSocket server on {host}:{port}")
    
    async with websockets.serve(websocket_handler, host, port):
        logger.info(f"✅ Server running on ws://{host}:{port}")
        await asyncio.Future()  # Run forever

def main():
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped")

if __name__ == "__main__":
    main() 