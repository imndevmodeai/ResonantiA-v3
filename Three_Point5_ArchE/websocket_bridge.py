import asyncio
import json
import logging
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed
from typing import Dict, Any, Set, Optional

logger = logging.getLogger(__name__)

class MessageDispatcher:
    """
    The Central Relay. Routes incoming messages to the appropriate handlers
    based on their declared type or intent. This is a simplified implementation;
    a more advanced version would integrate directly with the RISE or Autonomous Orchestrator.
    """
    async def dispatch(self, message: Dict[str, Any], websocket: WebSocketServerProtocol) -> Dict[str, Any]:
        """
        Processes an incoming message and returns a response.

        Args:
            message (Dict[str, Any]): The parsed JSON message from the client.
            websocket (WebSocketServerProtocol): The websocket connection instance.

        Returns:
            A dictionary representing the JSON response to be sent back.
        """
        message_type = message.get("type")
        payload = message.get("payload", {})
        
        logger.info(f"Dispatching message of type '{message_type}' from {websocket.remote_address}")

        # In a real system, these would call functions in other modules,
        # e.g., rise_orchestrator.run_rise_workflow(payload)
        if message_type == "run_workflow":
            # Simulate workflow execution
            response = {
                "status": "success",
                "message": f"Workflow '{payload.get('name', 'N/A')}' started.",
                "details": "Simulation complete. Result: 42."
            }
        elif message_type == "get_status":
            # Simulate status check
            response = {
                "status": "success",
                "message": "System status check.",
                "details": {"cpu_load": 0.42, "memory_usage": "2.5GB", "active_workflows": 1}
            }
        elif message_type == "ping":
            response = {"status": "success", "message": "pong"}
        else:
            response = {
                "status": "error",
                "message": f"Unknown message type: '{message_type}'",
                "details": None
            }
        
        return self._create_iar_compliant_response(message.get("request_id"), response)

    def _create_iar_compliant_response(self, request_id: Optional[str], response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Wraps the response in a standardized format."""
        return {
            "request_id": request_id,
            "response_type": "standard_response",
            "payload": {
                "result": response_data.get("details"),
                "reflection": {
                    "status": response_data["status"],
                    "confidence": 0.95, # Simulated confidence
                    "potential_issues": [response_data["message"]] if response_data["status"] == "error" else []
                }
            }
        }

class WebSocketBridge:
    """
    The Nervous System of ArchE. Establishes a real-time, bidirectional communication
    channel between the ArchE core and external clients. It listens for incoming
    commands, dispatches them for execution, and pushes results and status updates back.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initializes the WebSocketBridge.

        Args:
            host (str): The host to bind the websocket server to.
            port (int): The port to listen on.
        """
        self.host = host
        self.port = port
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.dispatcher = MessageDispatcher()
        self.server_task = None
        logger.info(f"[WebSocketBridge] Initialized. Ready to listen on ws://{self.host}:{self.port}")

    async def _register_client(self, websocket: WebSocketServerProtocol):
        """Adds a new client to the set of connected clients."""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}. Total clients: {len(self.connected_clients)}")

    async def _unregister_client(self, websocket: WebSocketServerProtocol):
        """Removes a client from the set of connected clients."""
        self.connected_clients.remove(websocket)
        logger.info(f"Client disconnected: {websocket.remote_address}. Total clients: {len(self.connected_clients)}")

    async def _handler(self, websocket: WebSocketServerProtocol, path: str):
        """
        The main handler for incoming websocket connections. Listens for messages,
        passes them to the dispatcher, and sends back the response.
        """
        await self._register_client(websocket)
        try:
            async for message_str in websocket:
                try:
                    message = json.loads(message_str)
                    if not isinstance(message, dict) or "type" not in message:
                        raise ValueError("Message must be a JSON object with a 'type' field.")
                    
                    response = await self.dispatcher.dispatch(message, websocket)
                    await websocket.send(json.dumps(response))

                except json.JSONDecodeError:
                    error_response = self.dispatcher._create_iar_compliant_response(None, {
                        "status": "error", "message": "Invalid JSON received."
                    })
                    await websocket.send(json.dumps(error_response))
                    logger.warning(f"Invalid JSON from {websocket.remote_address}: {message_str}")
                except ValueError as e:
                    error_response = self.dispatcher._create_iar_compliant_response(message.get("request_id"), {
                        "status": "error", "message": str(e)
                    })
                    await websocket.send(json.dumps(error_response))

        except ConnectionClosed as e:
            logger.info(f"Connection with {websocket.remote_address} closed gracefully: {e.code} {e.reason}")
        except Exception as e:
            logger.error(f"An unexpected error occurred with client {websocket.remote_address}: {e}", exc_info=True)
        finally:
            await self._unregister_client(websocket)

    async def start(self):
        """Starts the websocket server."""
        if self.server_task:
            logger.warning("Server is already running.")
            return
        
        try:
            server = await websockets.serve(self._handler, self.host, self.port)
            logger.info(f"WebSocketBridge is now listening on ws://{self.host}:{self.port}")
            # Keep the server running until it's cancelled
            self.server_task = asyncio.create_task(server.wait_closed())
            await self.server_task
        except asyncio.CancelledError:
            logger.info("Server start cancelled.")
        except OSError as e:
            logger.error(f"Failed to start server on {self.host}:{self.port}. Is the port already in use? Error: {e}")

    def stop(self):
        """Stops the websocket server."""
        if self.server_task and not self.server_task.done():
            self.server_task.cancel()
            logger.info("WebSocketBridge stopping...")
        else:
            logger.info("WebSocketBridge is not running.")

async def main():
    """Main function to run the server for testing."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    bridge = WebSocketBridge()
    
    try:
        await bridge.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        bridge.stop()
        print("Server stopped.")

if __name__ == "__main__":
    print("--- WebSocket Bridge Test Harness ---")
    print("Starting server on ws://localhost:8765")
    print("Use a websocket client (e.g., Postman, wscat) to connect and send messages.")
    print("Example message: {\"type\": \"run_workflow\", \"request_id\": \"123\", \"payload\": {\"name\": \"MyTestWorkflow\"}}")
    print("Press CTRL+C to stop the server.")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown initiated by user.")
