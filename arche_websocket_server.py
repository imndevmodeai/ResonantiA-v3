#!/usr/bin/env python3
"""
ArchE WebSocket Server - Cognitive Bus
Provides real-time communication between the UI and ArchE system
"""

import asyncio
import websockets
import json
import logging
import time
from typing import Dict, Set, Any
from pathlib import Path
import sys

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from Three_PointO_ArchE.session_manager import session_manager
    from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    SESSION_MANAGER_AVAILABLE = False
    print("Warning: Session manager not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ArcheWebSocketServer:
    def __init__(self, host='localhost', port=3006):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.rise_orchestrator = None
        self.session_manager = None
        
        # Initialize ArchE components if available
        if SESSION_MANAGER_AVAILABLE:
            try:
                self.session_manager = session_manager
                self.rise_orchestrator = RISE_Orchestrator()
                logger.info("✅ ArchE components initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize ArchE components: {e}")
        
    async def register_client(self, websocket):
        """Register a new client connection"""
        self.clients.add(websocket)
        logger.info(f"🔗 Client connected. Total clients: {len(self.clients)}")
        
        # Send welcome message
        welcome_message = {
            "type": "system",
            "content": "Connected to ArchE Cognitive Bus",
            "metadata": {
                "timestamp": str(time.time()),
                "session_id": "welcome_session",
                "status": "connected"
            }
        }
        await websocket.send(json.dumps(welcome_message))
        
    async def unregister_client(self, websocket):
        """Unregister a client connection"""
        self.clients.remove(websocket)
        logger.info(f"🔌 Client disconnected. Total clients: {len(self.clients)}")
        
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        if not self.clients:
            return
            
        message_json = json.dumps(message)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected_clients.add(client)
                
        # Remove disconnected clients
        for client in disconnected_clients:
            await self.unregister_client(client)
            
    async def handle_message(self, websocket, message: str):
        """Handle incoming messages from clients"""
        try:
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
                "timestamp": time.time(),
                "status": "processing"
            }
        }
        await websocket.send(json.dumps(ack_message))
        
        # Process with RISE engine if available
        if self.rise_orchestrator:
            try:
                # Create a session for this query
                if self.session_manager:
                    session_id = self.session_manager.get_or_create_session(query)
                else:
                    session_id = f"session_{int(time.time())}"
                    
                # Send thought trail message
                thought_message = {
                    "type": "thought",
                    "content": f"Processing query with RISE engine (Session: {session_id})",
                    "metadata": {
                        "timestamp": str(time.time()),
                        "session_id": session_id,
                        "status": "thinking"
                    }
                }
                await websocket.send(json.dumps(thought_message))
                
                # Send progress message
                progress_message = {
                    "type": "system",
                    "content": "RISE Engine: Executing Phase A - Knowledge Scaffolding & Dynamic Specialization...",
                    "metadata": {
                        "timestamp": str(time.time()),
                        "session_id": session_id,
                        "status": "phase_a"
                    }
                }
                await websocket.send(json.dumps(progress_message))
                
                # Actually call the RISE engine to process the query
                logger.info(f"🧠 Calling RISE engine for query: {query[:50]}...")
                
                # Call the RISE orchestrator to process the query
                try:
                    # Use the RISE orchestrator to process the query
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        self.rise_orchestrator.run_rise_workflow, 
                        query
                    )
                    
                    # Process the RISE engine result
                    if result and isinstance(result, dict):
                        # Extract the final strategy from the RISE result
                        final_strategy = result.get('final_strategy', {})
                        if isinstance(final_strategy, dict):
                            strategy_content = final_strategy.get('strategy_text', final_strategy.get('content', 'Strategy generated successfully'))
                        else:
                            strategy_content = str(final_strategy)
                        
                        # Get session ID from result
                        result_session_id = result.get('session_id', session_id)
                        
                        response_message = {
                            "type": "response",
                            "content": f"RISE Engine Analysis Complete\n\n{strategy_content}",
                            "metadata": {
                                "timestamp": str(time.time()),
                                "session_id": result_session_id,
                                "status": "completed",
                                "engine": "RISE",
                                "execution_duration": result.get('total_duration', 0),
                                "phases_completed": list(result.get('phase_results', {}).keys())
                            }
                        }
                    else:
                        response_message = {
                            "type": "response",
                            "content": "Query processed by RISE engine successfully.",
                            "metadata": {
                                "timestamp": str(time.time()),
                                "session_id": session_id,
                                "status": "completed",
                                "engine": "RISE"
                            }
                        }
                except Exception as rise_error:
                    logger.error(f"RISE engine error: {rise_error}")
                    # Fallback to simulated response if RISE fails
                    await asyncio.sleep(1)  # Brief delay
                    response_message = {
                        "type": "response",
                        "content": f"Query processed with RISE engine. Session ID: {session_id}. RISE engine encountered an error: {str(rise_error)}",
                        "metadata": {
                            "timestamp": str(time.time()),
                            "session_id": session_id,
                            "status": "completed_with_errors",
                            "engine": "RISE"
                        }
                    }
                
                # Send SPR activation message
                spr_message = {
                    "type": "spr",
                    "content": "Activating relevant SPRs for query processing",
                    "metadata": {
                        "timestamp": str(time.time()),
                        "session_id": session_id,
                        "status": "spr_activation"
                    }
                }
                await websocket.send(json.dumps(spr_message))
                
                # Send the final response from RISE engine
                await websocket.send(json.dumps(response_message))
                
            except Exception as e:
                logger.error(f"Error processing query with RISE: {e}")
                error_message = {
                    "type": "system",
                    "content": f"Error processing query: {str(e)}",
                    "metadata": {
                        "timestamp": str(time.time()),
                        "status": "error"
                    }
                }
                await websocket.send(json.dumps(error_message))
        else:
            # Fallback response when RISE engine is not available
            response_message = {
                "type": "response",
                "content": f"Query received: {query}. RISE engine not available, using fallback processing.",
                "metadata": {
                    "timestamp": str(time.time()),
                    "status": "fallback"
                }
            }
            await websocket.send(json.dumps(response_message))
            
    async def handle_workflow(self, websocket, workflow_name: str, metadata: Dict[str, Any]):
        """Handle a workflow execution request"""
        logger.info(f"🔄 Received workflow request: {workflow_name}")
        
        # Send acknowledgment
        ack_message = {
            "type": "system",
            "content": f"Workflow '{workflow_name}' received, executing...",
            "metadata": {
                "timestamp": str(time.time()),
                "workflow": workflow_name,
                "status": "executing"
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
        logger.info(f"🚀 Starting ArchE WebSocket Server on {self.host}:{self.port}")
        
        # Create a proper wrapper function that handles method binding
        async def handler_wrapper(websocket, path):
            await self.handler(websocket, path)
        
        # Start the server
        async with websockets.serve(handler_wrapper, self.host, self.port):
            logger.info(f"✅ ArchE Cognitive Bus running on ws://{self.host}:{self.port}")
            logger.info("🔗 Ready to accept client connections")
            
            # Keep the server running
            await asyncio.Future()  # Run forever

def main():
    """Main entry point"""
    server = ArcheWebSocketServer()
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")

if __name__ == "__main__":
    main() 