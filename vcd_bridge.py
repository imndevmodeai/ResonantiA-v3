#!/usr/bin/env python3
"""
VCD Bridge - Visual Cognitive Debugger Backend (LIVE INTEGRATION)
Connects the actual ArchE cognitive core to the VCD frontend via WebSocket.
"""
import asyncio
import json
import websockets
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Ensure the ArchE modules can be imported
sys.path.insert(0, str(Path(__file__).parent / 'Three_PointO_ArchE'))
sys.path.insert(0, str(Path(__file__).parent / 'Four_PointO_ArchE'))

try:
    from rise_orchestrator import RISE_Orchestrator
    from sirc_intake_handler import SircIntakeHandler, SircIntentPacket
    print("✅ Successfully imported ArchE core components.")
except ImportError as e:
    print(f"❌ Failed to import ArchE core components: {e}")
    print("Ensure you have run `export PYTHONPATH=$PYTHONPATH:./Three_PointO_ArchE:./Four_PointO_ArchE`")
    sys.exit(1)

WS_PORT = 8765
WS_HOST = "0.0.0.0"

class VCDBridge:
    def __init__(self):
        self.connected_clients = set()
        self.rise_orchestrator = self._initialize_rise()
        self.sirc_handler = SircIntakeHandler()

    def _initialize_rise(self):
        """Initializes the RISE Orchestrator and attaches the event callback."""
        try:
            workflows_dir = Path(__file__).parent / "workflows"
            orchestrator = RISE_Orchestrator(workflows_dir=str(workflows_dir))
            
            # This is the crucial link: hook our broadcast function into the orchestrator's event system
            orchestrator.event_callback = self.handle_rise_event
            print("✅ RISE v2.0 Genesis Protocol is ONLINE and hooked into VCD Bridge.")
            return orchestrator
        except Exception as e:
            print(f"❌ Failed to initialize RISE v2.0: {e}", file=sys.stderr)
            return None
            
    async def handle_rise_event(self, event_obj: Dict[str, Any]):
        """Callback function to receive events from the RISE orchestrator."""
        print(f"📨 RISE Event Received: {event_obj.get('message_type')}")
        await self.broadcast_to_all(event_obj)

    async def handle_client(self, websocket, path):
        """Register client and handle incoming messages."""
        self.connected_clients.add(websocket)
        print(f"VCD client connected from {websocket.remote_address}. Total clients: {len(self.connected_clients)}")
        
        await self.send_to_client(websocket, {
            "type": "system",
            "message_type": "system",
            "content": "VCD Bridge connected to LIVE ArchE Core. Ready for directives.",
            "timestamp": datetime.now().isoformat(),
        })
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get("type") == "query" and "payload" in data:
                        prompt = data["payload"]
                        print(f"▶️ Received query. Passing to SIRC Intake: {prompt[:80]}...")
                        
                        # Use the actual SIRC handler to process the intent
                        intent_packet = await self.sirc_handler.process_request(prompt)
                        
                        # Start the actual RISE workflow execution in the background
                        if self.rise_orchestrator:
                            asyncio.create_task(self.rise_orchestrator.handle_intent(intent_packet))
                        else:
                            await self.broadcast_to_all({
                                "type": "error", "message_type": "error", "content": "RISE Orchestrator is not initialized."
                            })
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {message}")

        finally:
            self.connected_clients.discard(websocket)
            print(f"VCD client disconnected. Total clients: {len(self.connected_clients)}")

    async def send_to_client(self, websocket, message):
        """Send message to a specific client."""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            self.connected_clients.discard(websocket)
    
    async def broadcast_to_all(self, message):
        """Broadcast message to all connected clients."""
        if self.connected_clients:
            await asyncio.gather(
                *[self.send_to_client(client, message) for client in self.connected_clients],
                return_exceptions=True
            )

async def main():
    bridge = VCDBridge()
    
    if not bridge.rise_orchestrator:
        print("❌ Halting server start due to RISE initialization failure.", file=sys.stderr)
        return
        
    print(f"🚀 Starting LIVE VCD Bridge on {WS_HOST}:{WS_PORT}")
    print("Waiting for VCD frontend to connect...")
    
    async with websockets.serve(bridge.handle_client, WS_HOST, WS_PORT):
        await asyncio.Future()

if __name__ == "__main__":
    # Note: For this to work, you may need to run this from the root of the Happier project
    # and ensure the PYTHONPATH is set correctly.
    # export PYTHONPATH=$PYTHONPATH:./Three_PointO_ArchE:./Four_PointO_ArchE
    asyncio.run(main())
