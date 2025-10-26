#!/usr/bin/env python3
"""
Simple WebSocket Server for ArchE
Basic communication without complex dependencies
"""

import asyncio
import json
import time
import logging
import websockets
from typing import Set, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SimpleWebSocket")

class SimpleWebSocketServer:
    def __init__(self, host='localhost', port=3005):
        self.host = host
        self.port = port
        self.clients: Set = set()
        
    async def register_client(self, websocket):
        """Register a new client connection"""
        self.clients.add(websocket)
        logger.info(f"🔗 Client connected. Total clients: {len(self.clients)}")
        
        # Send welcome message
        welcome_message = {
            "type": "system",
            "content": "Connected to ArchE Cognitive Bus (Simple Mode)",
            "metadata": {
                "timestamp": str(time.time()),
                "session_id": "simple_session",
                "status": "connected"
            }
        }
        await websocket.send(json.dumps(welcome_message))
        
    async def unregister_client(self, websocket):
        """Unregister a client connection"""
        self.clients.remove(websocket)
        logger.info(f"🔌 Client disconnected. Total clients: {len(self.clients)}")
        
    async def handle_message(self, websocket, message: str):
        """Handle incoming messages from clients"""
        try:
            logger.info(f"📝 Received message: {message[:50]}...")
            
            # Handle heartbeat
            if message == "heartbeat":
                response = {
                    "type": "system",
                    "content": "Heartbeat received",
                                    "metadata": {
                    "timestamp": str(time.time()),
                    "status": "alive"
                }
                }
                await websocket.send(json.dumps(response))
                return
                
            # Try to parse as JSON
            try:
                data = json.loads(message)
                message_type = data.get("type", "unknown")
                content = data.get("content", "")
                
                if message_type == "query":
                    await self.handle_query(websocket, content, data.get("metadata", {}))
                elif message_type == "workflow":
                    await self.handle_workflow(websocket, content, data.get("metadata", {}))
                else:
                    await self.handle_unknown_message(websocket, message)
                    
            except json.JSONDecodeError:
                # Handle plain text messages
                await self.handle_text_message(websocket, message)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            error_response = {
                "type": "system",
                "content": f"Error processing message: {str(e)}",
                "metadata": {
                    "timestamp": str(time.time()),
                    "status": "error"
                }
            }
            await websocket.send(json.dumps(error_response))
            
    async def handle_query(self, websocket, query: str, metadata: Dict[str, Any]):
        """Handle a query from the client"""
        logger.info(f"📝 Received query: {query[:50]}...")
        
        # Send acknowledgment
        ack_message = {
            "type": "system",
            "content": "Query received, processing...",
            "metadata": {
                "timestamp": str(time.time()),
                "status": "processing"
            }
        }
        await websocket.send(json.dumps(ack_message))
        
        # Simulate processing
        await asyncio.sleep(1)
        
        # Send response
        response_message = {
            "type": "response",
            "content": f"Query processed successfully: {query}",
            "metadata": {
                "timestamp": str(time.time()),
                "status": "completed"
            }
        }
        await websocket.send(json.dumps(response_message))
        
    async def handle_workflow(self, websocket, workflow_name: str, metadata: Dict[str, Any]):
        """Handle a workflow execution request"""
        logger.info(f"🔄 Received workflow request: {workflow_name}")
        
        # Send acknowledgment
        ack_message = {
            "type": "system",
            "content": f"Workflow '{workflow_name}' received",
            "metadata": {
                "timestamp": str(time.time()),
                "workflow": workflow_name,
                "status": "received"
            }
        }
        await websocket.send(json.dumps(ack_message))
        
        # Simulate workflow execution
        await asyncio.sleep(1)
        
        # Send workflow progress
        progress_message = {
            "type": "system",
            "content": f"Workflow '{workflow_name}' in progress...",
            "metadata": {
                "timestamp": str(time.time()),
                "workflow": workflow_name,
                "status": "in_progress"
            }
        }
        await websocket.send(json.dumps(progress_message))
        
        await asyncio.sleep(2)
        
        # Send completion message
        completion_message = {
            "type": "response",
            "content": f"Workflow '{workflow_name}' completed successfully",
            "metadata": {
                "timestamp": str(time.time()),
                "workflow": workflow_name,
                "status": "completed"
            }
        }
        await websocket.send(json.dumps(completion_message))
        
    async def handle_text_message(self, websocket, message: str):
        """Handle plain text messages"""
        logger.info(f"📝 Received text message: {message[:50]}...")
        
        # Echo the message back
        response = {
            "type": "response",
            "content": f"Received: {message}",
            "metadata": {
                "timestamp": str(time.time()),
                "status": "echo"
            }
        }
        await websocket.send(json.dumps(response))
        
    async def handle_unknown_message(self, websocket, message: str):
        """Handle unknown message types"""
        logger.info(f"❓ Received unknown message type: {message[:50]}...")
        
        response = {
            "type": "system",
            "content": "Unknown message type received",
            "metadata": {
                "timestamp": str(time.time()),
                "status": "unknown"
            }
        }
        await websocket.send(json.dumps(response))
        
    async def handler(self, websocket, path):
        """Main WebSocket handler"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        except Exception as e:
            logger.error(f"Error in WebSocket handler: {e}")
        finally:
            await self.unregister_client(websocket)
            
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"🚀 Starting Simple ArchE WebSocket Server on {self.host}:{self.port}")
        
        # Create a proper wrapper function that handles method binding
        async def handler_wrapper(websocket, path):
            await self.handler(websocket, path)
        
        # Start the server
        async with websockets.serve(handler_wrapper, self.host, self.port):
            logger.info(f"✅ Simple ArchE Cognitive Bus running on ws://{self.host}:{self.port}")
            logger.info("🔗 Ready to accept client connections")
            
            # Keep the server running
            await asyncio.Future()  # Run forever

def main():
    """Main entry point"""
    server = SimpleWebSocketServer()
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")

if __name__ == "__main__":
    main() 