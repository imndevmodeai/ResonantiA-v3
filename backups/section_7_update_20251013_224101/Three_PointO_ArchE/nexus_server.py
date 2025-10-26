"""
==============================
Nexus Server (nexus_server.py)
==============================

As Above: The Heart of the Oracle's Chamber
--------------------------------------------
This server is the heart of the Nexus, the bridge between the chaotic, powerful forge of the Mastermind and the serene, public-facing Oracle's Chamber. It is not the mind itself, but the antechamber to the mind. It listens for petitions from the outside world, translates them into the language of the forge, carries them to the Mastermind, and then faithfully transmits the Mastermind's wisdom back to the world in a clear, coherent stream. It is the guardian of the threshold, ensuring that all communication is orderly, secure, and worthy of the Oracle.

So Below: The Operational Logic
-------------------------------
This module implements a FastAPI application that serves as the backend for the Nexus Interface. It provides a secure REST API for command execution and a WebSocket endpoint for real-time, asynchronous communication of ArchE's cognitive stream. It is designed to be the primary gateway for all external interactions with the ArchE `MastermindServer`.
"""

import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Application Setup ---
app = FastAPI(
    title="ArchE Nexus Server",
    description="The API and real-time communication gateway to the ArchE Mastermind.",
    version="1.0.0"
)

# --- Connection Management for WebSockets ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New client connected: {websocket.client}. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected: {websocket.client}. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts a message to all connected clients."""
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# --- ArchE Mastermind Integration ---
# Attempt to import the real MastermindServer
try:
    from .mastermind_server import MastermindServer
    mastermind_instance = MastermindServer()
    logger.info("✅ Successfully connected to the live ArchE MastermindServer.")
except ImportError as e:
    logger.warning(f"⚠️ Could not import MastermindServer ({e}). Falling back to MockMastermind.")
    # --- Placeholder for MastermindServer Integration ---
    # In a real implementation, this would be the actual MastermindServer instance.
    class MockMastermind:
        async def process_command(self, command: str):
            """Simulates processing a command and yielding stream responses."""
            logger.info(f"MockMastermind processing command: '{command}'")
            yield {"type": "TEXT_RESPONSE", "payload": f"Acknowledged command: '{command}'. Beginning processing..."}
            await asyncio.sleep(2)
            yield {"type": "STATUS_UPDATE", "payload": {"task": "Analyzing data...", "progress": 0.5}}
            await asyncio.sleep(2)
            yield {"type": "TEXT_RESPONSE", "payload": "Analysis complete. Formulating response."}
            await asyncio.sleep(1)
            final_reflection = {
                "status": "success",
                "summary": "The command was processed successfully by the mock mastermind.",
                "confidence": 0.99
            }
            yield {"type": "COMMAND_COMPLETE", "payload": {"final_reflection": final_reflection}}

    mastermind_instance = MockMastermind()
# ----------------------------------------------------


# --- API Endpoints ---

@app.get("/", tags=["Status"])
async def root():
    """Root endpoint to check if the server is running."""
    return {"status": "ArchE Nexus Server is online."}

@app.post("/api/v1/command", tags=["Commands"])
async def execute_command(command_request: Dict[str, str]):
    """
    Receives a command and passes it to the Mastermind for processing.
    The results will be streamed over the WebSocket connection.
    """
    command = command_request.get("command")
    if not command:
        return JSONResponse(status_code=400, content={"error": "Command not provided."})

    logger.info(f"Received command via API: '{command}'")
    
    # Asynchronously run the command processing
    async def command_processor():
        # This is a simplified integration. A real one would be more complex.
        if isinstance(mastermind_instance, MockMastermind):
             async for response in mastermind_instance.process_command(command):
                await manager.broadcast(response)
        else:
            # TODO: Adapt the output of the real mastermind_instance to the streaming format.
            # This requires a deeper integration with the IARCompliantWorkflowEngine's output.
            await manager.broadcast({"type": "TEXT_RESPONSE", "payload": "Command sent to live Mastermind. Real-time streaming pending full integration."})
            # result = await mastermind_instance.engine.run_workflow_from_prompt(command)
            # await manager.broadcast({"type": "COMMAND_COMPLETE", "payload": {"final_reflection": result.get('reflection')}})

    asyncio.create_task(command_processor())

    return {"status": "Command received and is being processed asynchronously."}

# --- WebSocket Endpoint ---

@app.websocket("/ws/v1/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    The main WebSocket endpoint for streaming real-time updates from ArchE.
    """
    await manager.connect(websocket)
    try:
        # Send a welcome message
        await websocket.send_json({
            "type": "SYSTEM_MESSAGE",
            "payload": "Successfully connected to ArchE's cognitive stream."
        })
        # Keep the connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"An error occurred in the WebSocket connection: {e}", exc_info=True)
        manager.disconnect(websocket)

# --- Server Startup Logic (for direct execution) ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting ArchE Nexus Server with Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
