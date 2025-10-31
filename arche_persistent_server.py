#!/usr/bin/env python3
import asyncio
import websockets
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import os
import asyncio
import json
import logging
import websockets
import socket
from datetime import datetime

# Ensure the package root is in the Python path
# This is crucial for running the script directly
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root.parent))

from Three_PointO_ArchE.mastermind import Mastermind

# --- Logging Setup ---
LOG_DIR = project_root / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / "arche_persistent_server.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PersistentServer")

# --- CORRECTED INITIALIZATION ---
# Instantiate Mastermind at the global scope so it's ready for all connections.
# This resolves the "AttributeError: 'NoneType' object has no attribute 'interact'".
try:
    mastermind = Mastermind()
    logger.info("Mastermind object instantiated successfully at global scope.")
except Exception as e:
    logger.critical(f"Failed to instantiate Mastermind: {e}", exc_info=True)
    mastermind = None # Set to None if initialization fails

from concurrent.futures import ThreadPoolExecutor

# Create a thread pool executor
executor = ThreadPoolExecutor()

# ... (previous code remains the same) ...

async def websocket_handler(websocket):
    """Handles incoming WebSocket connections and messages."""
    logger.info(f"Client connected from {websocket.remote_address}")
    if mastermind is None:
        # ... (error handling remains the same) ...
        await websocket.close()
        return

    try:
        async for message in websocket:
            # ... (heartbeat logic remains the same) ...

            query = str(message)
            logger.info(f"Received query: {query}")
            
            try:
                # Run the synchronous mastermind.interact in a separate thread
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    executor, mastermind.interact_sync, query
                )
                
                logger.info(f"Sending response: {str(response)[:200]}...")
                
                # ... (JSON serialization and sending logic remains the same) ...
                
            except Exception as e:
                # ... (error handling remains the same) ...
                await websocket.send(json.dumps(error_response))
                
    except websockets.exceptions.ConnectionClosed:
        pass
        # ... (connection closed logic remains the same) ...
    finally:
        logger.info("WebSocket handler cleanup complete")

async def main():
    """Main function to start the WebSocket server."""
    # Get port from the ARCHE_PORT environment variable.
    # The unified startup script is responsible for ensuring this port is available.
    port_str = os.environ.get('ARCHE_PORT')
    if not port_str or not port_str.isdigit():
        logger.critical(f"FATAL: ARCHE_PORT environment variable is not set or invalid. Got: '{port_str}'. Cannot start server.")
        return  # Exit if port is not configured

    websocket_port = int(port_str)
    host = "0.0.0.0"

    logger.info(f"Attempting to start ArchE Persistent WebSocket server on {host}:{websocket_port}")

    try:
        # Create the server with the correct handler - bind to all interfaces
        async with websockets.serve(websocket_handler, host, websocket_port) as server:
            logger.info(f"ArchE Persistent Server running on ws://{host}:{websocket_port}")
            # Keep the server running
            await server.wait_closed()
    except OSError as e:
        logger.critical(f"FATAL: Failed to bind to port {websocket_port}. Error: {e}. The port might be in use by another process or require privileges.")
    except Exception as e:
        logger.critical(f"FATAL: An unexpected error occurred while starting the server: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutting down.")
    except Exception as e:
        logger.critical(f"Server failed to start: {e}", exc_info=True)