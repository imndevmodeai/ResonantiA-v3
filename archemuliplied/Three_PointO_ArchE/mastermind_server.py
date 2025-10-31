#!/usr/bin/env python3
"""
ArchE Mastermind Server - Unified Cognitive Core
ResonantiA Protocol v3.1-CA

This script merges the advanced cognitive core from mastermind/interact.py
with a robust WebSocket server architecture. It serves as the single,
authoritative entry point for the ArchE backend.
"""

import sys
import os
import logging
import json
from pathlib import Path
import asyncio
import websockets
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

# Add the project root to the path to allow direct imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.proactive_truth_system import ProactiveTruthSystem
from Three_PointO_ArchE.tools.enhanced_search_tool import EnhancedSearchTool
from Three_PointO_ArchE.spr_manager import SPRManager
from Three_PointO_ArchE.adaptive_cognitive_orchestrator import AdaptiveCognitiveOrchestrator
from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
from Three_PointO_ArchE.llm_providers import GoogleProvider

# --- Logging Setup ---
from Three_PointO_ArchE.logging_config import setup_logging, get_session_logger, get_performance_logger

# Initialize timestamped logging system
setup_logging()
logger = logging.getLogger("ArchE_Mastermind_Server")
perf_logger = get_performance_logger()

class MastermindServer:
    """
    The unified ArchE server, integrating the full cognitive core with a WebSocket interface.
    """
    
    def __init__(self):
        """Initializes all cognitive components of the ArchE system."""
        logger.info("🧠 Initializing ArchE Mastermind Server...")
        self.engine = IARCompliantWorkflowEngine()
        self._initialize_ptrf()
        self._initialize_aco()
        self._initialize_rise()
        self.executor = ThreadPoolExecutor()
        logger.info("✅ ArchE Mastermind Server Initialized Successfully.")

    def _initialize_ptrf(self):
        """Initializes the Proactive Truth Resonance Framework."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set.")
            
            llm_provider = GoogleProvider(api_key=api_key)
            web_search_tool = EnhancedSearchTool()
            spr_definitions_path = str(project_root / "knowledge_graph" / "spr_definitions_tv.json")
            spr_manager = SPRManager(spr_filepath=spr_definitions_path)
            
            self.truth_seeker = ProactiveTruthSystem(
                workflow_engine=self.engine,
                llm_provider=llm_provider,
                web_search_tool=web_search_tool,
                spr_manager=spr_manager
            )
            self.ptrf_enabled = True
            logger.info("✅ Proactive Truth Resonance Framework is ONLINE.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize PTRF: {e}", exc_info=True)
            self.ptrf_enabled = False
            self.truth_seeker = None

    def _initialize_aco(self):
        """Initializes the Adaptive Cognitive Orchestrator."""
        try:
            protocol_chunks = [
                'Implementation Resonance refers to the alignment between conceptual understanding and operational implementation.',
                'The ProportionalResonantControlPatterN eliminates oscillatory errors through resonant gain amplification.',
                'Adaptive Cognitive Orchestrator enables meta-learning and pattern evolution in cognitive architectures.'
            ]
            self.aco = AdaptiveCognitiveOrchestrator(protocol_chunks)
            self.autonomous_evolution_enabled = True
            logger.info("✅ Adaptive Cognitive Orchestrator is ONLINE.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ACO: {e}", exc_info=True)
            self.autonomous_evolution_enabled = False
            self.aco = None
            
    def _initialize_rise(self):
        """Initializes the RISE Orchestrator."""
        try:
            workflows_dir = project_root / "workflows"
            self.rise_orchestrator = RISE_Orchestrator(workflows_dir=str(workflows_dir))
            self.rise_v2_enabled = True
            logger.info("✅ RISE v2.0 Genesis Protocol is ONLINE.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RISE v2.0: {e}", exc_info=True)
            self.rise_v2_enabled = False
            self.rise_orchestrator = None

    def _handle_cognitive_query_sync(self, query: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for handling queries through the ACO/RISE cognitive core.
        This is the method that will be run in a separate thread.
        """
        # This is a simplified version of the logic from mastermind/interact.py
        # It determines the cognitive path and executes it.
        try:
            query_lower = query.lower()
            
            strategic_indicators = [
                "crisis", "conflicting", "ground truth", "predictive forecast", "geopolitical",
                "strategic", "complex", "high-stakes", "Execution paradoX"
            ]
            
            is_strategic_query = any(indicator in query_lower for indicator in strategic_indicators)
            
            if is_strategic_query and self.rise_v2_enabled:
                logger.info(f"🎯 Strategic query detected. Routing to RISE engine.")
                return self.rise_orchestrator.run_rise_workflow(query)
            elif self.ptrf_enabled and any(k in query_lower for k in ["truth", "fact", "verify"]):
                 logger.info(f"🎯 Truth-seeking query detected. Routing to PTRF engine.")
                 return self.truth_seeker.seek_truth(query)
            elif self.autonomous_evolution_enabled:
                logger.info(f"🎯 Standard query. Routing to ACO for enhancement.")
                context, _ = self.aco.process_query_with_evolution(query)
                return {"response": context}
            else:
                logger.warning("No cognitive core available for query.")
                return {"error": "No cognitive core available."}

        except Exception as e:
            logger.error(f"Error in cognitive query handler: {e}", exc_info=True)
            return {"error": str(e)}

    async def websocket_handler(self, websocket):
        """Handles incoming WebSocket connections and messages."""
        logger.info(f"🔗 Client connected from {websocket.remote_address}")
        try:
            async for message in websocket:
                if message == "ping":
                    await websocket.send("pong")
                    continue

                query = str(message)
                logger.info(f"📥 Received query: {query[:150]}...")
                
                try:
                    loop = asyncio.get_running_loop()
                    response = await loop.run_in_executor(
                        self.executor, self._handle_cognitive_query_sync, query
                    )
                    
                    response_json = json.dumps(response, default=str)
                    logger.info(f"📤 Sending response: {response_json[:200]}...")
                    await websocket.send(response_json)
                    
                except Exception as e:
                    logger.error(f"Error processing query: {e}", exc_info=True)
                    error_response = {"error": "An error occurred while processing your request."}
                    await websocket.send(json.dumps(error_response))
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for client {websocket.remote_address}")
        finally:
            logger.info("WebSocket handler cleanup complete.")

async def main():
    """Main function to start the Mastermind WebSocket server."""
    port_str = os.environ.get('ARCHE_PORT')
    if not port_str or not port_str.isdigit():
        logger.critical(f"FATAL: ARCHE_PORT environment variable is not set or invalid. Got: '{port_str}'.")
        return

    websocket_port = int(port_str)
    host = "0.0.0.0"

    server_instance = MastermindServer()
    
    logger.info(f"🚀 Attempting to start ArchE Mastermind Server on {host}:{websocket_port}")
    
    try:
        async with websockets.serve(server_instance.websocket_handler, host, websocket_port) as server:
            logger.info(f"✅ ArchE Mastermind Server is running on ws://{host}:{websocket_port}")
            await server.wait_closed()
    except OSError as e:
        logger.critical(f"FATAL: Failed to bind to port {websocket_port}. Error: {e}")
    except Exception as e:
        logger.critical(f"FATAL: An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Server shutting down.")
    except Exception as e:
        logger.critical(f"💥 Server failed to start: {e}", exc_info=True)
