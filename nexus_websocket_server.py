import asyncio
import json
import websockets
from datetime import datetime
import logging
from collections import defaultdict
from typing import Dict, List, Any, Callable, Optional, Set
import threading
import time
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed

# Use the same robust implementation as the main Nexus interface
logger = logging.getLogger(__name__)

class NexusStandaloneServer:
    def __init__(self, port: int = 8765):
        self.port = port
        self.subscribers = defaultdict(list)
        self.websocket_clients: Set[WebSocketServerProtocol] = set()
        self._running = False
        self._lock = threading.Lock()
        self._server_thread = None
        self._loop = None

    def start_server(self):
        self._server_thread = threading.Thread(target=self._run_server, daemon=True)
        self._server_thread.start()
        logger.info(f"Standalone Nexus server thread started on port {self.port}")

    def _run_server(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._websocket_server())

    async def _websocket_server(self):
        self._running = True
        async with websockets.serve(
            self.handler,
            "0.0.0.0",
            self.port,
            ping_interval=30,
            ping_timeout=30,
            max_queue=64,
        ):
            async def heartbeat():
                while self._running:
                    await asyncio.sleep(10)
                    await self.broadcast(json.dumps({
                        "id": str(datetime.now().timestamp()),
                        "content": "[heartbeat] Nexus alive",
                        "timestamp": datetime.now().isoformat(),
                        "sender": "arche",
                        "message_type": "system",
                        "protocol_compliance": True
                    }))
            asyncio.create_task(heartbeat())
            await asyncio.Future()  # run forever

    async def handler(self, websocket: WebSocketServerProtocol):
        self.websocket_clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.websocket_clients)}")
        try:
            await websocket.send(json.dumps({
                "type": "connection_established",
                "timestamp": datetime.now().isoformat(),
                "message": "Connected to Standalone Nexus"
            }))
            # Broadcast a normal message immediately so UI shows activity
            await self.broadcast(json.dumps({
                "id": str(datetime.now().timestamp()),
                "content": "Welcome to ArchE Nexus.",
                "timestamp": datetime.now().isoformat(),
                "sender": "arche",
                "message_type": "system",
                "protocol_compliance": True
            }))

            async for message in websocket:
                print(f"[Nexus] Raw message received: {repr(message)}")
                print(f"[Nexus] Message type: {type(message)}")
                try:
                    data = json.loads(message)
                    print(f"[Nexus] Parsed JSON: {data}")
                except json.JSONDecodeError as e:
                    print(f"[Nexus] JSON decode error: {e}")
                    continue
                except Exception as e:
                    print(f"[Nexus] Unexpected error parsing message: {e}")
                    continue

                response = {
                    "id": str(datetime.now().timestamp()),
                    "content": f"ArchE received: {data.get('content')}",
                    "timestamp": datetime.now().isoformat(),
                    "sender": "arche",
                    "message_type": "chat",
                    "protocol_compliance": True,
                    "iar": {
                        "status": "ok",
                        "confidence": 0.98
                    }
                }
                print(f"[Nexus] Broadcasting response: {response}")
                await self.broadcast(json.dumps(response))

                await asyncio.sleep(0.2)
                thought_trail_event = {
                    "type": "nexus_event",
                    "event": {
                        "topic": "thoughttrail_entry",
                        "data": {
                           "task_id": f"sim_task_{int(datetime.now().timestamp())}",
                            "action_type": "process_user_input",
                            "iar": {"reflection": f"Processed user input: {data.get('content', 'unknown')}"},
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                }
                print(f"[Nexus] Broadcasting thought trail event: {thought_trail_event}")
                await self.broadcast(json.dumps(thought_trail_event))

        except ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            if websocket in self.websocket_clients:
                self.websocket_clients.remove(websocket)
            print(f"Client disconnected. Total clients: {len(self.websocket_clients)}")

    async def broadcast(self, message: str):
        if not self.websocket_clients:
            return
        stale = []
        tasks = []
        for client in self.websocket_clients:
            try:
                if client.closed:
                    stale.append(client)
                    continue
                tasks.append(client.send(message))
            except Exception:
                stale.append(client)
        for s in stale:
            if s in self.websocket_clients:
                self.websocket_clients.remove(s)
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                logger.warning(f"Broadcast encountered errors: {e}")

    def stop(self):
        if not self._running:
            return
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._server_thread:
            self._server_thread.join(timeout=5)
        logger.info("Standalone Nexus server stopped")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = NexusStandaloneServer()
    server.start_server()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.stop()
        print("Server shut down.")
