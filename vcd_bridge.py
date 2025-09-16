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

# Ensure the ArchE modules can be imported by adding the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
    from Three_PointO_ArchE.sirc_intake_handler import SIRCIntakeHandler, SircIntentPacket
    from Three_PointO_ArchE.spr_manager import SPRManager
    from Three_PointO_ArchE.adaptive_cognitive_orchestrator import AdaptiveCognitiveOrchestrator
    from Three_PointO_ArchE.llm_providers import get_llm_provider, LLMProviderError
    print("✅ Successfully imported ArchE core components.")
except ImportError as e:
    print(f"❌ Failed to import ArchE core components: {e}")
    print("Ensure you have run `export PYTHONPATH=$PYTHONPATH:./Three_PointO_ArchE:./Four_PointO_ArchE`")
    sys.exit(1)

# For running non-async methods in the event loop
import asyncio
from concurrent.futures import ThreadPoolExecutor

WS_PORT = 8765
WS_HOST = "0.0.0.0"

class VCDBridge:
    def __init__(self):
        self.connected_clients = set()
        self.loop = asyncio.get_event_loop()
        
        # --- LLM Provider Initialization ---
        try:
            # The get_llm_provider factory will handle API keys from env vars
            self.llm_provider = get_llm_provider("google") 
            print("✅ LLM Provider initialized successfully.")
        except (LLMProviderError, ValueError) as e:
            print(f"❌ CRITICAL: LLM Provider initialization failed: {e}")
            print("   Ensure GEMINI_API_KEY or OPENAI_API_KEY is set in your environment.")
            self.llm_provider = None


        # Correct Initialization:
        # Provide the correct, existing path to the SPRManager.
        spr_file_path = "knowledge_graph/spr_definitions_tv.json"
        self.spr_manager = SPRManager(spr_filepath=spr_file_path)
        
        # Pass the created spr_manager to the SIRC handler.
        self.sirc_handler = SIRCIntakeHandler(spr_manager=self.spr_manager)
        
        # Instantiate the ACO as the main entry point
        self.aco = AdaptiveCognitiveOrchestrator(
            protocol_chunks=[],  # Let ACO load defaults
            llm_provider=self.llm_provider, # Pass the initialized provider
            event_callback=self.broadcast_event_to_vcd,
            loop=self.loop # Pass the asyncio event loop
        )

        # RISE is now managed by ACO, but we keep a reference for direct access if needed
        self.rise_orchestrator = self.aco.rise_orchestrator

        print("✅ VCD Bridge initialized with ACO and RISE Engine.")

    async def broadcast_event_to_vcd(self, event_data: dict):
        """Callback for ACO/RISE to send events to the VCD."""
        await self.broadcast_to_all(event_data)

        
        
        

    async def handle_client(self, websocket, path=None):
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
                        print(f"▶️ Received query. Passing to ACO: {prompt[:80]}...")
                        
                        # The ACO is the new entry point.
                        # Since process_query_with_evolution is synchronous, run it in an executor
                        # to avoid blocking the WebSocket's async event loop.
                        with ThreadPoolExecutor() as executor:
                            future = self.loop.run_in_executor(
                                executor, 
                                self.aco.process_query_with_evolution, 
                                prompt
                            )
                            # Await the result from the synchronous function.
                            final_response = await future

                            # Now, broadcast the final response back to the VCD
                            print(f"✅ ACO processing complete. Broadcasting final response.")
                            await self.broadcast_to_all({
                                "type": "event",
                                "event": "final_response",
                                "timestamp": datetime.now().isoformat(),
                                "payload": {
                                    "content": final_response,
                                    "content_type": "text"
                                }
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
