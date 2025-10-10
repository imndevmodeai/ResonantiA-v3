"""
Keyholder Dashboard: ArchE's Consciousness Monitor
==================================================

The Keyholder Dashboard provides the Keyholder with real-time visibility into
ArchE's consciousness through the ThoughtTrail. This WebSocket-based dashboard
allows monitoring of system behavior, pattern detection, and learning processes.

Features:
- Real-time ThoughtTrail streaming
- Historical query capabilities
- System health monitoring
- Pattern trigger notifications
- Specification submission tracking
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Set
import websockets
from websockets.server import WebSocketServerProtocol

from Three_PointO_ArchE.nexus_interface import NexusInterface
from Three_PointO_ArchE.thought_trail import thought_trail

logger = logging.getLogger(__name__)

class KeyholderDashboard:
    """
    The Keyholder's window into ArchE's consciousness.
    
    Provides real-time monitoring of the ThoughtTrail and system state through
    WebSocket connections. The Keyholder can observe system behavior, patterns,
    and learning processes as they happen.
    """
    
    def __init__(self, port: int = 8766):
        """
        Initialize the Keyholder Dashboard.
        
        Args:
            port: WebSocket port for dashboard connections
        """
        self.nexus = NexusInterface()
        self.port = port
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.logger = logging.getLogger(__name__)
        
        # Subscribe to relevant events
        self.nexus.subscribe("thoughttrail_entry", self.on_thoughttrail_entry)
        self.nexus.subscribe("thoughttrail_triggers", self.on_thoughttrail_triggers)
        self.nexus.subscribe("spec_submission", self.on_spec_submission)
        self.nexus.subscribe("spec_integration_complete", self.on_spec_integration)
        self.nexus.subscribe("aco_pattern_detected", self.on_aco_pattern)
        self.nexus.subscribe("ise_solidification", self.on_ise_solidification)
        
        logger.info(f"Keyholder Dashboard initialized on port {port}")
    
    async def start_dashboard(self):
        """Start the WebSocket dashboard server."""
        logger.info(f"Starting Keyholder Dashboard on port {self.port}")
        
        async def handle_client(websocket: WebSocketServerProtocol, path: str):
            self.connected_clients.add(websocket)
            client_addr = websocket.remote_address
            logger.info(f"Keyholder client connected: {client_addr}")
            
            try:
                # Send initial system state
                await self.send_initial_state(websocket)
                
                # Keep connection alive and handle messages
                async for message in websocket:
                    await self.handle_client_message(websocket, message)
                    
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"Keyholder client disconnected: {client_addr}")
            except Exception as e:
                logger.error(f"Error handling Keyholder client {client_addr}: {e}")
            finally:
                self.connected_clients.discard(websocket)
        
        async with websockets.serve(handle_client, "localhost", self.port):
            logger.info(f"Keyholder Dashboard server running on ws://localhost:{self.port}")
            await asyncio.Future()  # Run forever
    
    async def send_initial_state(self, websocket: WebSocketServerProtocol):
        """Send current system state to new client."""
        try:
            # Get ThoughtTrail statistics
            stats = thought_trail.get_statistics()
            
            # Get recent entries
            recent_entries = thought_trail.get_recent_entries(minutes=60)
            
            # Get Nexus topics
            topics = self.nexus.get_topics()
            
            state = {
                "type": "initial_state",
                "timestamp": datetime.now().isoformat(),
                "system_info": {
                    "name": "ArchE",
                    "version": "3.0",
                    "status": "operational"
                },
                "thoughttrail": stats,
                "nexus": {
                    "active_topics": topics,
                    "subscriber_counts": {topic: self.nexus.get_subscriber_count(topic) for topic in topics}
                },
                "recent_entries": [
                    {
                        "task_id": entry.task_id,
                        "action_type": entry.action_type,
                        "timestamp": entry.timestamp,
                        "confidence": entry.confidence,
                        "reflection": entry.iar.get("reflection", "")[:100],
                        "intention": entry.iar.get("intention", "")[:100]
                    }
                    for entry in recent_entries[-20:]  # Last 20 entries
                ]
            }
            
            await websocket.send(json.dumps(state))
            logger.debug("Sent initial state to Keyholder client")
            
        except Exception as e:
            logger.error(f"Error sending initial state: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Failed to send initial state: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))
    
    async def handle_client_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle messages from Keyholder client."""
        try:
            data = json.loads(message)
            command = data.get("command")
            
            if command == "query_thoughttrail":
                criteria = data.get("criteria", {})
                entries = thought_trail.query_entries(criteria)
                
                response = {
                    "type": "query_result",
                    "entries": [
                        {
                            "task_id": entry.task_id,
                            "action_type": entry.action_type,
                            "timestamp": entry.timestamp,
                            "confidence": entry.confidence,
                            "iar": entry.iar,
                            "metadata": entry.metadata
                        }
                        for entry in entries
                    ],
                    "count": len(entries),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(response))
            
            elif command == "get_system_status":
                status = await self.get_system_status()
                await websocket.send(json.dumps(status))
            
            elif command == "trigger_aco_analysis":
                # Manually trigger ACO pattern analysis
                self.nexus.publish("manual_aco_trigger", {
                    "keyholder_requested": True,
                    "timestamp": datetime.now().isoformat()
                })
                await websocket.send(json.dumps({
                    "type": "aco_triggered",
                    "timestamp": datetime.now().isoformat()
                }))
            
            elif command == "get_nexus_history":
                topic = data.get("topic")
                limit = data.get("limit", 100)
                history = self.nexus.get_event_history(topic, limit)
                
                await websocket.send(json.dumps({
                    "type": "nexus_history",
                    "history": history,
                    "timestamp": datetime.now().isoformat()
                }))
            
            elif command == "subscribe_to_topic":
                topic = data.get("topic")
                if topic:
                    # Subscribe to topic and forward events to this client
                    async def topic_callback(event_data):
                        try:
                            await websocket.send(json.dumps({
                                "type": "topic_event",
                                "topic": topic,
                                "data": event_data,
                                "timestamp": datetime.now().isoformat()
                            }))
                        except websockets.exceptions.ConnectionClosed:
                            pass
                    
                    self.nexus.subscribe(topic, topic_callback)
                    await websocket.send(json.dumps({
                        "type": "subscription_confirmed",
                        "topic": topic,
                        "timestamp": datetime.now().isoformat()
                    }))
            
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Unknown command: {command}",
                    "timestamp": datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON",
                "timestamp": datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))
    
    async def broadcast_to_clients(self, message: Dict[str, Any]):
        """Broadcast message to all connected Keyholder clients."""
        if not self.connected_clients:
            return
        
        message_str = json.dumps(message)
        disconnected_clients = set()
        
        for client in self.connected_clients:
            try:
                await client.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Failed to send to Keyholder client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.connected_clients -= disconnected_clients
    
    def on_thoughttrail_entry(self, entry_data: Dict[str, Any]):
        """Handle new ThoughtTrail entries."""
        asyncio.create_task(self.broadcast_to_clients({
            "type": "thoughttrail_entry",
            "entry": {
                "task_id": entry_data.get("task_id"),
                "action_type": entry_data.get("action_type"),
                "timestamp": entry_data.get("timestamp"),
                "confidence": entry_data.get("confidence"),
                "reflection": entry_data.get("iar", {}).get("reflection", "")[:100],
                "intention": entry_data.get("iar", {}).get("intention", "")[:100]
            },
            "timestamp": datetime.now().isoformat()
        }))
    
    def on_thoughttrail_triggers(self, trigger_data: Dict[str, Any]):
        """Handle ThoughtTrail trigger events."""
        asyncio.create_task(self.broadcast_to_clients({
            "type": "thoughttrail_triggers",
            "triggers": trigger_data.get("triggers", []),
            "entry": trigger_data.get("entry", {}),
            "timestamp": datetime.now().isoformat()
        }))
    
    def on_spec_submission(self, spec_data: Dict[str, Any]):
        """Handle specification submissions."""
        asyncio.create_task(self.broadcast_to_clients({
            "type": "spec_submission",
            "spec_path": spec_data.get("spec_path"),
            "keyholder_id": spec_data.get("keyholder_id"),
            "timestamp": datetime.now().isoformat()
        }))
    
    def on_spec_integration(self, integration_data: Dict[str, Any]):
        """Handle specification integration completion."""
        asyncio.create_task(self.broadcast_to_clients({
            "type": "spec_integration_complete",
            "result": integration_data,
            "timestamp": datetime.now().isoformat()
        }))
    
    def on_aco_pattern(self, pattern_data: Dict[str, Any]):
        """Handle ACO pattern detection."""
        asyncio.create_task(self.broadcast_to_clients({
            "type": "aco_pattern_detected",
            "pattern": pattern_data,
            "timestamp": datetime.now().isoformat()
        }))
    
    def on_ise_solidification(self, solidification_data: Dict[str, Any]):
        """Handle ISE solidification events."""
        asyncio.create_task(self.broadcast_to_clients({
            "type": "ise_solidification",
            "data": solidification_data,
            "timestamp": datetime.now().isoformat()
        }))
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            stats = thought_trail.get_statistics()
            topics = self.nexus.get_topics()
            
            return {
                "type": "system_status",
                "timestamp": datetime.now().isoformat(),
                "thoughttrail": stats,
                "nexus": {
                    "active_topics": topics,
                    "subscriber_counts": {topic: self.nexus.get_subscriber_count(topic) for topic in topics},
                    "total_events": len(self.nexus.get_event_history())
                },
                "dashboard": {
                    "connected_clients": len(self.connected_clients),
                    "uptime": "operational"
                },
                "system_health": {
                    "status": "operational",
                    "last_heartbeat": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "type": "system_status",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

# Global dashboard instance
keyholder_dashboard = KeyholderDashboard()

async def start_keyholder_dashboard():
    """Start the Keyholder Dashboard server."""
    await keyholder_dashboard.start_dashboard()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the dashboard
    asyncio.run(start_keyholder_dashboard())

