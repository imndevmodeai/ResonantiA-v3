"""
NexusInterface: ArchE's Central Nervous System
==============================================

The NexusInterface serves as ArchE's central communication bus, implementing
a publisher-subscriber pattern for asynchronous, decoupled communication
between all system components.

This implementation provides:
- Event publishing and subscription
- Real-time message routing
- ThoughtTrail integration
- WebSocket support for external clients
- Event filtering and routing
"""

import asyncio
import json
import logging
import threading
import time
from collections import defaultdict
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
from typing import Dict, List, Any, Callable, Optional, Set
import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)

class NexusInterface:
    """
    Central communication hub for ArchE.
    
    Implements a publisher-subscriber pattern where components can:
    - Publish events to specific topics
    - Subscribe to events from specific topics
    - Filter events based on criteria
    - Connect external clients via WebSocket
    """
    
    def __init__(self, websocket_port: int = 8765):
        """
        Initialize the NexusInterface.
        
        Args:
            websocket_port: Port for WebSocket server
        """
        self.subscribers = defaultdict(list)  # topic -> list of callbacks
        self.event_history = []  # Store recent events for debugging
        self.max_history = 1000
        self.websocket_port = websocket_port
        self.websocket_clients: Set[WebSocketServerProtocol] = set()
        self._thoughttrail = None
        self._running = False
        self._lock = threading.Lock()
        self._server_thread = None
        self._loop = None
        
        logger.info(f"NexusInterface initialized with WebSocket port {websocket_port}")
    
    def publish(self, topic: str, data: Dict[str, Any]) -> None:
        """
        Publish an event to a specific topic.
        
        Args:
            topic: The topic/channel name
            data: The event data to publish
        """
        event = {
            "topic": topic,
            "data": data,
            "timestamp": now_iso(),
            "event_id": f"{topic}_{int(time.time() * 1000)}"
        }
        
        with self._lock:
            # Store in history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
            
            # Notify subscribers
            if topic in self.subscribers:
                for callback in self.subscribers[topic]:
                    try:
                        callback(data)
                    except Exception as e:
                        logger.error(f"Subscriber callback failed for topic {topic}: {e}")
        
        # Broadcast to WebSocket clients
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._broadcast_to_websockets(event), self._loop)
        
        logger.debug(f"Published event to topic '{topic}': {event['event_id']}")
    
    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to events from a specific topic.
        
        Args:
            topic: The topic to subscribe to
            callback: Function to call when events are published
        """
        with self._lock:
            self.subscribers[topic].append(callback)
        
        logger.info(f"Subscribed to topic '{topic}'")
    
    def unsubscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Unsubscribe from a specific topic.
        
        Args:
            topic: The topic to unsubscribe from
            callback: The callback function to remove
        """
        with self._lock:
            if topic in self.subscribers:
                try:
                    self.subscribers[topic].remove(callback)
                except ValueError:
                    logger.warning(f"Callback not found in subscribers for topic '{topic}'")
        
        logger.info(f"Unsubscribed from topic '{topic}'")
    
    def inject_thoughttrail(self, thoughttrail_instance) -> None:
        """
        Inject ThoughtTrail instance for bidirectional communication.
        
        Args:
            thoughttrail_instance: The ThoughtTrail instance
        """
        self._thoughttrail = thoughttrail_instance
        thoughttrail_instance.inject_nexus(self)
        logger.info("ThoughtTrail injected into NexusInterface")
    
    def get_event_history(self, topic: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent event history.
        
        Args:
            topic: Filter by topic (None for all topics)
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        with self._lock:
            events = self.event_history[-limit:] if limit else self.event_history
            
            if topic:
                events = [e for e in events if e["topic"] == topic]
            
            return events
    
    def get_subscriber_count(self, topic: str) -> int:
        """
        Get the number of subscribers for a topic.
        
        Args:
            topic: The topic to check
            
        Returns:
            Number of subscribers
        """
        with self._lock:
            return len(self.subscribers.get(topic, []))
    
    def get_topics(self) -> List[str]:
        """
        Get all active topics.
        
        Returns:
            List of topic names
        """
        with self._lock:
            return list(self.subscribers.keys())
    
    def start_server_in_thread(self):
        """Starts the WebSocket server in a separate thread."""
        if self._running:
            logger.warning("WebSocket server is already running.")
            return

        self._server_thread = threading.Thread(target=self._run_server, daemon=True)
        self._server_thread.start()
        logger.info("WebSocket server thread started.")

    def _run_server(self):
        """The target function for the server thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self.start_websocket_server())

    async def start_websocket_server(self) -> None:
        """Start the WebSocket server for external clients."""
        self._running = True
        
        async def handle_client(websocket: WebSocketServerProtocol, path: str):
            self.websocket_clients.add(websocket)
            logger.info(f"WebSocket client connected: {websocket.remote_address}")
            
            try:
                # Send initial connection message
                await websocket.send(json.dumps({
                    "type": "connection_established",
                    "timestamp": now_iso(),
                    "message": "Connected to ArchE Nexus"
                }))
                
                # Keep connection alive
                async for message in websocket:
                    await self._handle_websocket_message(websocket, message)
                    
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.websocket_clients.discard(websocket)
                logger.info(f"WebSocket client disconnected: {websocket.remote_address}")
        
        async with websockets.serve(handle_client, "localhost", self.websocket_port) as server:
            logger.info(f"WebSocket server started on port {self.websocket_port}")
            self.server_instance = server
            await asyncio.Future()  # Run forever
    
    async def _broadcast_to_websockets(self, event: Dict[str, Any]) -> None:
        """Broadcast event to all connected WebSocket clients."""
        if not self.websocket_clients:
            return
        
        message = json.dumps({
            "type": "nexus_event",
            "event": event
        })
        
        # Send to all clients concurrently
        disconnected_clients = set()
        for client in self.websocket_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Failed to send to WebSocket client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        with self._lock:
            self.websocket_clients -= disconnected_clients
    
    async def _handle_websocket_message(self, websocket: WebSocketServerProtocol, message: str) -> None:
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                # Client wants to subscribe to a topic
                topic = data.get("topic")
                if topic:
                    # Create a callback that sends to this specific client
                    async def client_callback(event_data):
                        try:
                            await websocket.send(json.dumps({
                                "type": "topic_event",
                                "topic": topic,
                                "data": event_data,
                                "timestamp": now_iso()
                            }))
                        except websockets.exceptions.ConnectionClosed:
                            pass
                    
                    self.subscribe(topic, client_callback)
                    
                    await websocket.send(json.dumps({
                        "type": "subscription_confirmed",
                        "topic": topic,
                        "timestamp": now_iso()
                    }))
            
            elif message_type == "query_history":
                # Client wants event history
                topic = data.get("topic")
                limit = data.get("limit", 100)
                history = self.get_event_history(topic, limit)
                
                await websocket.send(json.dumps({
                    "type": "history_response",
                    "history": history,
                    "timestamp": now_iso()
                }))
            
            elif message_type == "get_topics":
                # Client wants list of active topics
                topics = self.get_topics()
                await websocket.send(json.dumps({
                    "type": "topics_response",
                    "topics": topics,
                    "timestamp": now_iso()
                }))
            
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": now_iso()
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON",
                "timestamp": now_iso()
            }))
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e),
                "timestamp": now_iso()
            }))
    
    def stop(self) -> None:
        """Stop the NexusInterface and its WebSocket server."""
        if not self._running:
            return
            
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        
        if self._server_thread:
            self._server_thread.join(timeout=5)

        logger.info("NexusInterface and WebSocket server stopped")

# Global instance
nexus_interface = NexusInterface()

# Convenience functions
def publish_event(topic: str, data: Dict[str, Any]) -> None:
    """Publish an event to the global NexusInterface."""
    nexus_interface.publish(topic, data)

def subscribe_to_topic(topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
    """Subscribe to a topic on the global NexusInterface."""
    nexus_interface.subscribe(topic, callback)

def get_nexus() -> NexusInterface:
    """Get the global NexusInterface instance."""
    return nexus_interface

__all__ = [
    'NexusInterface',
    'nexus_interface',
    'publish_event',
    'subscribe_to_topic',
    'get_nexus'
]

