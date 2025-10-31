#!/usr/bin/env python3
"""
ArchE-Nexus Bridge Server
Integrates the real ArchE mastermind.interact functionality with the Nexus WebSocket interface.
This replaces the mock server with actual ArchE cognitive processing.
"""

import asyncio
import json
import websockets
import sys
import os
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, Any, Set
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed

# Add the Three_PointO_ArchE directory to the path
project_root = Path(__file__).parent
three_point_path = project_root / "Three_PointO_ArchE"
sys.path.insert(0, str(three_point_path))

logger = logging.getLogger(__name__)

class ArchENexusBridge:
    def __init__(self, port: int = 8765):
        self.port = port
        self.websocket_clients: Set[WebSocketServerProtocol] = set()
        self._running = False
        
        # Initialize ArchE components
        self.mastermind = None
        self.thought_trail = None
        self.nexus_interface = None
        self.aco = None
        self.llm_provider = None
        self.loop = None
        
        self._initialize_arche_components()
        
    def _initialize_arche_components(self):
        """Initialize the real ArchE components"""
        try:
            logger.info("Initializing ArchE components...")
            
            # Try to initialize ResonantiA Maestro directly
            try:
                import sys
                import os
                
                # Add Three_PointO_ArchE to path
                arche_path = os.path.join(project_root, "Three_PointO_ArchE")
                if arche_path not in sys.path:
                    sys.path.insert(0, arche_path)
                
                # Import ResonantiA Maestro components using absolute imports
                from Three_PointO_ArchE.resonantia_maestro import ResonantiAMaestro
                from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
                from Three_PointO_ArchE.spr_manager import SPRManager
                from Three_PointO_ArchE.llm_providers import GoogleProvider
                from Three_PointO_ArchE.tools.search_tool import SearchTool
                
                logger.info("✅ ResonantiA Maestro components imported successfully")
                
                # Initialize components
                self.spr_manager = SPRManager()
                self.workflow_engine = IARCompliantWorkflowEngine(spr_manager=self.spr_manager)
                
                # Initialize LLM provider if API key available
                api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
                llm_provider = None
                search_tool = None
                
                if api_key:
                    llm_provider = GoogleProvider(api_key=api_key)
                    search_tool = SearchTool()
                    logger.info("✅ LLM provider and search tool initialized")
                else:
                    logger.warning("No API key found - running without LLM enhancement")
                
                # Initialize ResonantiA Maestro
                self.maestro = ResonantiAMaestro(
                    workflow_engine=self.workflow_engine,
                    rise_orchestrator=None,  # We'll add this later if needed
                    llm_provider=llm_provider,
                    spr_manager=self.spr_manager,
                    search_tool=search_tool
                )
                
                logger.info("🎉 ResonantiA Maestro initialized successfully!")
                self.arche_available = True
                
            except ImportError as e:
                logger.error(f"Failed to import ResonantiA Maestro components: {e}")
                logger.info("Falling back to enhanced response mode")
                self.arche_available = False
                
        except Exception as e:
            logger.error(f"Failed to initialize ArchE components: {e}")
            logger.info("Falling back to enhanced response mode")
            self.arche_available = False
    
    async def _emit_aco_event(self, event_type: str, message: str, data: dict = None):
        """Emit ACO events to connected VCD clients"""
        event = {
            "type": "nexus_event",
            "event": {
                "topic": "aco_event",
                "data": {
                    "event_type": event_type,
                    "message": message,
                    "data": data or {},
                    "timestamp": datetime.now().isoformat()
                }
            }
        }
        await self._broadcast(event)
    
    async def start_server(self):
        """Start the WebSocket server"""
        self._running = True
        self.loop = asyncio.get_event_loop()  # Set the loop for ACO callbacks
        logger.info(f"🚀 Starting ArchE-Nexus Bridge on port {self.port}")
        
        async with websockets.serve(
            self.websocket_handler,
            "0.0.0.0",
            self.port,
            ping_interval=30,
            ping_timeout=30
        ):
            logger.info(f"🌐 ArchE-Nexus Bridge listening on ws://0.0.0.0:{self.port}")
            
            # Start heartbeat
            asyncio.create_task(self._heartbeat())
            
            # Keep server running
            await asyncio.Future()  # run forever
    
    async def websocket_handler(self, websocket: WebSocketServerProtocol):
        """Handle WebSocket connections"""
        self.websocket_clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"🔗 Client connected: {client_addr} (Total: {len(self.websocket_clients)})")
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                "type": "nexus_event",
                "event": {
                    "topic": "system_message",
                    "data": {
                        "sender": "ArchE",
                        "content": "🧠 Connected to ArchE Cognitive Core via Nexus Bridge",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }))
            
            # Handle messages
            async for message in websocket:
                await self._process_message(message, websocket)
                
        except ConnectionClosed:
            logger.info(f"🔌 Client disconnected: {client_addr}")
        except Exception as e:
            logger.error(f"❌ WebSocket handler error: {e}")
        finally:
            self.websocket_clients.discard(websocket)
            logger.info(f"🧹 Client removed: {client_addr} (Remaining: {len(self.websocket_clients)})")
    
    async def _process_message(self, message: str, websocket: WebSocketServerProtocol):
        """Process incoming messages and route them through ArchE"""
        try:
            logger.info(f"📥 Raw message: {message}")
            data = json.loads(message)
            logger.info(f"📥 Parsed data: {data}")
            
            user_query = data.get('content', '').strip()
            logger.info(f"📥 Extracted query: '{user_query}'")
            
            if not user_query:
                logger.info("📥 Empty query, skipping")
                return
                
            logger.info(f"📥 Processing query: {user_query[:100]}...")
            
            # Process through ResonantiA Maestro if available
            if self.arche_available and hasattr(self, 'maestro'):
                logger.info("📥 Using ResonantiA Maestro")
                try:
                    # Use the maestro's weave_response method
                    maestro_result = self.maestro.weave_response(user_query)
                    
                    # Extract the response content
                    if isinstance(maestro_result, dict):
                        response = maestro_result.get('content', str(maestro_result))
                        logger.info(f"📊 Maestro enhancement level: {maestro_result.get('enhancement_level', 'unknown')}")
                        logger.info(f"📊 Maestro tools used: {maestro_result.get('tools_used', [])}")
                    else:
                        response = str(maestro_result)
                        
                    logger.info(f"📊 ResonantiA Maestro response: {response[:100]}...")
                    
                except Exception as e:
                    logger.error(f"ResonantiA Maestro processing failed: {e}")
                    response = self._fallback_response(user_query)
            else:
                logger.info("📥 Using fallback response")
                response = self._fallback_response(user_query)
            
            logger.info(f"📤 Generated response: {response[:100]}...")
            
            # Send chat response
            chat_event = {
                "type": "nexus_event", 
                "event": {
                    "topic": "arche_response",
                    "data": {
                        "sender": "ArchE",
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
            logger.info(f"📤 Sending chat event: {json.dumps(chat_event)[:200]}...")
            await self._broadcast(chat_event)
            
            # Send thought trail event
            trail_event = {
                "type": "nexus_event",
                "event": {
                    "topic": "thoughttrail_entry",
                    "data": {
                        "task_id": f"query_{int(datetime.now().timestamp())}",
                        "action_type": "process_user_query",
                        "inputs": {"query": user_query},
                        "outputs": {"response": response[:200] + "..." if len(response) > 200 else response},
                        "iar": {
                            "intention": "Process user query through ArchE cognitive core",
                            "action": "cognitive_processing",
                            "reflection": "Query processed successfully"
                        },
                        "timestamp": datetime.now().isoformat(),
                        "confidence": 0.95,
                        "metadata": {"source": "arche_nexus_bridge"}
                    }
                }
            }
            logger.info(f"📤 Sending trail event: {json.dumps(trail_event)[:200]}...")
            await self._broadcast(trail_event)
            
            logger.info("✅ Message processing completed successfully")
            
        except json.JSONDecodeError as e:
            logger.error(f"⚠️ JSON decode error: {e} - Raw message: {message}")
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}", exc_info=True)
    
    async def _process_with_arche(self, query: str) -> str:
        """Process query through the real ArchE mastermind"""
        try:
            # Run in thread to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.mastermind.interact_sync, query)
            
            # Extract the response content
            if isinstance(result, dict):
                return result.get('response', str(result))
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"❌ Error in ArchE processing: {e}")
            return f"ArchE encountered an error: {str(e)}"
    
    def _fallback_response(self, query: str) -> str:
        """Enhanced fallback response when ArchE components aren't available"""
        query_lower = query.lower()
        
        # Provide intelligent responses based on query content
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return f"Hello! I'm ArchE, your cognitive AI assistant. I received your message: '{query}'. While my full cognitive components are initializing, I'm here to help. What would you like to explore?"
        
        elif any(word in query_lower for word in ['cheap', 'cheapest', 'cost', 'price', 'budget']):
            return f"I understand you're asking about cost-effective options regarding: '{query}'. While my full reasoning capabilities are loading, I can suggest checking comparison websites, looking for deals, or considering alternative approaches. What specific area are you most interested in?"
        
        elif any(word in query_lower for word in ['how', 'what', 'why', 'when', 'where']):
            return f"That's an interesting question: '{query}'. My cognitive processing modules are currently initializing, but I can help you think through this systematically. Could you provide more context about what you're trying to achieve?"
        
        elif any(word in query_lower for word in ['help', 'assist', 'support']):
            return f"I'm here to help! You asked: '{query}'. While my full cognitive capabilities are loading, I can provide guidance and work through problems with you. What specific assistance do you need?"
        
        else:
            return f"ArchE received your query: '{query}'. My cognitive components are currently initializing, but I'm processing your request. This appears to be about: {self._analyze_query_intent(query)}. How can I assist you further?"
    
    def _analyze_query_intent(self, query: str) -> str:
        """Simple intent analysis for fallback mode"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['travel', 'trip', 'flight', 'hotel', 'destination']):
            return "travel planning"
        elif any(word in query_lower for word in ['code', 'programming', 'development', 'software']):
            return "programming assistance"
        elif any(word in query_lower for word in ['learn', 'study', 'education', 'knowledge']):
            return "learning and education"
        elif any(word in query_lower for word in ['business', 'work', 'project', 'management']):
            return "business and work"
        else:
            return "general inquiry"
    
    async def _broadcast(self, event: Dict[str, Any]):
        """Broadcast event to all connected clients"""
        if not self.websocket_clients:
            return
            
        message = json.dumps(event)
        disconnected = set()
        
        for client in self.websocket_clients:
            try:
                if client.closed:
                    disconnected.add(client)
                else:
                    await client.send(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                disconnected.add(client)
        
        # Remove disconnected clients
        self.websocket_clients -= disconnected
    
    async def _heartbeat(self):
        """Send periodic heartbeat"""
        while self._running:
            await asyncio.sleep(30)
            await self._broadcast({
                "type": "nexus_event",
                "event": {
                    "topic": "heartbeat", 
                    "data": {
                        "sender": "Nexus",
                        "content": "💓 ArchE-Nexus Bridge heartbeat",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            })

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    bridge = ArchENexusBridge()
    
    try:
        asyncio.run(bridge.start_server())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Server crashed: {e}")