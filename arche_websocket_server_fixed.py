#!/usr/bin/env python3
"""
ArchE WebSocket Server - Cognitive Bus (Fixed)
Provides real-time communication between the UI and ArchE system with proper input validation
"""

import asyncio
import websockets
import json
import logging
import time
from typing import Dict, Set, Any, Optional
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

class ArcheWebSocketServerFixed:
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
        
    def validate_query_input(self, query: Any) -> tuple[bool, str, Optional[str]]:
        """
        Validate query input to prevent null/empty values from reaching the RISE engine
        
        Args:
            query: The query input to validate
            
        Returns:
            Tuple of (is_valid, error_message, cleaned_query)
        """
        # Check if query is None
        if query is None:
            return False, "Query cannot be null", None
            
        # Convert to string if it's not already
        if not isinstance(query, str):
            try:
                query = str(query)
            except Exception as e:
                return False, f"Failed to convert query to string: {e}", None
        
        # Check if query is empty or only whitespace
        if not query.strip():
            return False, "Query cannot be empty or only whitespace", None
            
        # Check minimum length
        if len(query.strip()) < 10:
            return False, "Query must be at least 10 characters long", None
            
        # Check maximum length
        if len(query) > 10000:
            return False, "Query cannot exceed 10,000 characters", None
            
        # Clean the query
        cleaned_query = query.strip()
        
        return True, "", cleaned_query
        
    async def register_client(self, websocket):
        """Register a new client connection"""
        self.clients.add(websocket)
        logger.info(f"🔗 Client connected. Total clients: {len(self.clients)}")
        
        # Send welcome message
        welcome_message = {
            "type": "system",
            "content": "Connected to ArchE Cognitive Bus (Fixed)",
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
        """Handle incoming messages from clients with enhanced validation"""
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
                
                logger.info(f"📨 Received message type: {message_type}, content length: {len(str(content))}")
                
                if message_type == "query":
                    await self.handle_query(websocket, content, data.get("metadata", {}))
                elif message_type == "workflow":
                    await self.handle_workflow(websocket, content, data.get("metadata", {}))
                else:
                    await self.handle_unknown_message(websocket, message)
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
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
            
    async def handle_query(self, websocket, query: Any, metadata: Dict[str, Any]):
        """Handle a query from the client with proper validation"""
        logger.info(f"📝 Received query input type: {type(query)}, value: {str(query)[:100]}...")
        
        # Validate the query input
        is_valid, error_message, cleaned_query = self.validate_query_input(query)
        
        if not is_valid:
            logger.error(f"❌ Query validation failed: {error_message}")
            error_response = {
                "type": "system",
                "content": f"Query validation failed: {error_message}",
                "metadata": {
                    "timestamp": str(time.time()),
                    "status": "validation_error",
                    "error": error_message
                }
            }
            await websocket.send(json.dumps(error_response))
            return
        
        logger.info(f"✅ Query validated successfully: {cleaned_query[:50]}...")
        
        # Send acknowledgment
        ack_message = {
            "type": "system",
            "content": "Query received and validated, processing...",
            "metadata": {
                "timestamp": time.time(),
                "status": "processing",
                "query_length": len(cleaned_query)
            }
        }
        await websocket.send(json.dumps(ack_message))
        
        # Process with RISE engine if available
        if self.rise_orchestrator:
            try:
                # Create a session for this query
                if self.session_manager:
                    session_id = self.session_manager.get_or_create_session(cleaned_query)
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
                logger.info(f"🧠 Calling RISE engine for validated query: {cleaned_query[:50]}...")
                
                # Call the RISE orchestrator to process the query
                try:
                    # Use the RISE orchestrator to process the query
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        self.rise_orchestrator.run_rise_workflow, 
                        cleaned_query  # Use the cleaned query
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
                    # Send detailed error response
                    response_message = {
                        "type": "response",
                        "content": f"RISE engine encountered an error: {str(rise_error)}",
                        "metadata": {
                            "timestamp": str(time.time()),
                            "session_id": session_id,
                            "status": "completed_with_errors",
                            "engine": "RISE",
                            "error": str(rise_error)
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
                        "status": "error",
                        "error": str(e)
                    }
                }
                await websocket.send(json.dumps(error_message))
        else:
            # Fallback response when RISE engine is not available
            response_message = {
                "type": "response",
                "content": f"Query received: {cleaned_query}. RISE engine not available, using fallback processing.",
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
            "content": f"Text message received: {message}",
            "metadata": {
                "timestamp": str(time.time()),
                "status": "echo"
            }
        }
        await websocket.send(json.dumps(response))
        
    async def handle_unknown_message(self, websocket, message: str):
        """Handle unknown message types"""
        logger.warning(f"❓ Unknown message type: {message[:50]}...")
        
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
        logger.info(f"🚀 Starting ArchE WebSocket Server (Fixed) on {self.host}:{self.port}")
        
        async def handler_wrapper(websocket, path):
            await self.handler(websocket, path)
            
        async with websockets.serve(handler_wrapper, self.host, self.port):
            logger.info(f"✅ WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever

def main():
    """Main function to run the WebSocket server"""
    server = ArcheWebSocketServerFixed()
    asyncio.run(server.start_server())

if __name__ == "__main__":
    main() 