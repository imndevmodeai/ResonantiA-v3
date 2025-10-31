#!/usr/bin/env python3
"""
Minimal WebSocket Server Test
"""

import asyncio
import websockets
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalWebSocketServer:
    def __init__(self, host='localhost', port=3005):
        self.host = host
        self.port = port
        self.clients = set()
    
    async def handler(self, websocket, path):
        """Main WebSocket handler"""
        logger.info(f"🔗 New connection from {websocket.remote_address}")
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                logger.info(f"📝 Received: {message}")
                response = f"Echo: {message}"
                await websocket.send(response)
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Connection closed")
        finally:
            self.clients.remove(websocket)
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"🚀 Starting minimal WebSocket server on {self.host}:{self.port}")
        
        # Create wrapper function
        async def handler_wrapper(websocket, path):
            await self.handler(websocket, path)
        
        # Start server
        async with websockets.serve(handler_wrapper, self.host, self.port):
            logger.info(f"✅ Server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

def main():
    server = MinimalWebSocketServer()
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped")

if __name__ == "__main__":
    main() 