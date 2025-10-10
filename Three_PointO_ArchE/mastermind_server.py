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
from typing import Dict, Any, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Add the project root to the path to allow direct imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from .workflow_engine import IARCompliantWorkflowEngine
    from .proactive_truth_system import ProactiveTruthSystem
    from .tools.enhanced_search_tool import EnhancedSearchTool
    from .spr_manager import SPRManager
    from .adaptive_cognitive_orchestrator import AdaptiveCognitiveOrchestrator
    from .rise_orchestrator import RISE_Orchestrator
    from .autopoietic_governor import AutopoieticGovernor
    from .thought_trail import ThoughtTrail # Assuming thought_trail is a singleton or class
    from .nexus_interface import nexus_interface
except ImportError:
    # Fallback to absolute imports if relative imports fail
    from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
    from Three_PointO_ArchE.proactive_truth_system import ProactiveTruthSystem
    from Three_PointO_ArchE.tools.enhanced_search_tool import EnhancedSearchTool
    from Three_PointO_ArchE.spr_manager import SPRManager
    from Three_PointO_ArchE.adaptive_cognitive_orchestrator import AdaptiveCognitiveOrchestrator
    from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
    from Three_PointO_ArchE.autopoietic_governor import AutopoieticGovernor
    from Three_PointO_ArchE.thought_trail import ThoughtTrail
    from Three_PointO_ArchE.nexus_interface import nexus_interface
from .llm_providers.google import GoogleProvider

# --- Logging Setup ---
try:
    from .logging_config import setup_logging
except ImportError:
    from Three_PointO_ArchE.logging_config import setup_logging

# Initialize timestamped logging system
setup_logging()
logger = logging.getLogger("ArchE_Mastermind_Server")
perf_logger = logging.getLogger("ArchE_Performance")
# session_logger = logging.getLogger("ArchE_Session") # Example for a session-specific logger

class MastermindServer:
    """
    The unified ArchE server, integrating the full cognitive core with a WebSocket interface.
    """
    
    def __init__(self):
        """Initializes all cognitive components of the ArchE system."""
        logger.info("🧠 Initializing ArchE Mastermind Server...")
        self.config = self._load_config()
        self.engine = IARCompliantWorkflowEngine()
        self._initialize_ptrf()
        self._initialize_aco()
        self._initialize_rise()
        self._initialize_autopoiesis()
        self.executor = ThreadPoolExecutor()
        logger.info("✅ ArchE Mastermind Server Initialized Successfully.")

    def _load_config(self) -> Dict[str, Any]:
        """Loads the enhanced mastermind configuration."""
        try:
            config_path = project_root / "mastermind" / "enhanced_mastermind_config.json"
            with open(config_path, 'r') as f:
                logger.info("Loading enhanced mastermind configuration...")
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"FATAL: Could not load or parse configuration file: {e}. Using empty config.", exc_info=True)
            return {}

    def _initialize_ptrf(self):
        """Initializes the Proactive Truth Resonance Framework."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set.")
            
            self.llm_provider = GoogleProvider(api_key=api_key) # Store provider as instance variable
            web_search_tool = EnhancedSearchTool()
            spr_definitions_path = str(project_root / "knowledge_graph" / "spr_definitions_tv.json")
            self.spr_manager = SPRManager(spr_filepath=spr_definitions_path)
            
            self.truth_seeker = ProactiveTruthSystem(
                workflow_engine=self.engine,
                llm_provider=self.llm_provider,
                web_search_tool=web_search_tool,
                spr_manager=self.spr_manager
            )
            self.ptrf_enabled = True
            logger.info("✅ Proactive Truth Resonance Framework is ONLINE.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize PTRF: {e}", exc_info=True)
            self.ptrf_enabled = False
            self.truth_seeker = None
            self.spr_manager = None

    def _initialize_aco(self):
        """Initializes the Adaptive Cognitive Orchestrator."""
        try:
            protocol_chunks = [
                'Implementation Resonance refers to the alignment between conceptual understanding and operational implementation.',
                'The ProportionalResonantControlPatterN eliminates oscillatory errors through resonant gain amplification.',
                'Adaptive Cognitive Orchestrator enables meta-learning and pattern evolution in cognitive architectures.'
            ]
            self.aco = AdaptiveCognitiveOrchestrator(
                protocol_chunks=protocol_chunks,
                llm_provider=getattr(self, 'llm_provider', None) # Pass the stored LLM provider
            )
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

            # Attach event callback to forward SIRC events to websockets clients
            def _event_sink(event_obj: Dict[str, Any]):
                try:
                    # Buffer events on the server instance for retrieval by websocket handler
                    if not hasattr(self, '_event_queue'):
                        self._event_queue = []
                    self._event_queue.append(event_obj)
                except Exception:
                    pass

            try:
                self.rise_orchestrator.event_callback = _event_sink  # type: ignore
            except Exception:
                pass
            self.rise_v2_enabled = True
            logger.info("✅ RISE v2.0 Genesis Protocol is ONLINE.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RISE v2.0: {e}", exc_info=True)
            self.rise_v2_enabled = False
            self.rise_orchestrator = None

    def _initialize_autopoiesis(self):
        """Initializes the Autopoietic Governor and its dependencies."""
        try:
            # Connect the global thought_trail instance to the global nexus_interface
            self.thought_trail = ThoughtTrail() 
            nexus_interface.inject_thoughttrail(self.thought_trail)

            # The insight engine needs to be defined/initialized, mocking for now
            class MockInsightEngine: pass
            self.insight_engine = MockInsightEngine()

            self.governor = AutopoieticGovernor(
                config=self.config, # Pass the loaded server config
                thought_trail=self.thought_trail,
                insight_engine=self.insight_engine,
                spr_manager=self.spr_manager
            )
            
            # Schedule the governor's self-audit
            self.scheduler = AsyncIOScheduler()
            audit_interval = self.governor.config.get("AUDIT_INTERVAL_MINUTES", 60)
            self.scheduler.add_job(
                self.governor.perform_self_audit, 
                'interval', 
                minutes=audit_interval
            )
            self.scheduler.start()
            
            self.autopoiesis_enabled = self.governor.config.get("AUTOPOIESIS_ENABLED", False)
            if self.autopoiesis_enabled:
                logger.info(f"✅ Autopoietic Governor is ONLINE and scheduled for audit every {audit_interval} minutes.")
            else:
                logger.warning("Autopoiesis is DISABLED by configuration. The Governor is idle.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Autopoietic Governor: {e}", exc_info=True)
            self.autopoiesis_enabled = False
            self.governor = None


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
                rise_result = self.rise_orchestrator.run_rise_workflow(query)
                return self._wrap_response_with_iar(rise_result, "RISE", query)
            elif self.ptrf_enabled and any(k in query_lower for k in ["truth", "fact", "verify"]):
                 logger.info(f"🎯 Truth-seeking query detected. Routing to PTRF engine.")
                 ptrf_result = self.truth_seeker.seek_truth(query)
                 return self._wrap_response_with_iar(ptrf_result, "PTRF", query)
            elif self.autonomous_evolution_enabled:
                logger.info(f"🎯 Standard query. Routing to ACO for enhancement.")
                context, _ = self.aco.process_query_with_evolution(query)
                return self._wrap_response_with_iar({"response": context}, "ACO", query)
            else:
                logger.warning("No cognitive core available for query.")
                return self._wrap_response_with_iar({"error": "No cognitive core available."}, "ERROR", query)

        except Exception as e:
            logger.error(f"Error in cognitive query handler: {e}", exc_info=True)
            return self._wrap_response_with_iar({"error": str(e)}, "ERROR", query)
    
    def _wrap_response_with_iar(self, response: Dict[str, Any], engine: str, query: str) -> Dict[str, Any]:
        """
        Wrap the response with enhanced IAR (Integrated Action Reflection) data for VCD display.
        Incorporates frontend's sophisticated cognitive assessment structure.
        """
        import time
        from datetime import datetime
        
        # Determine confidence based on response content
        confidence = 0.9
        status = "Success"
        potential_issues = []
        
        if "error" in response:
            confidence = 0.1
            status = "Failure"
            potential_issues.append(f"Engine {engine} returned error")
        elif "execution_status" in response and response["execution_status"] == "failed":
            confidence = 0.3
            status = "Warning"
            potential_issues.append("Workflow execution failed")
        
        # Enhanced cognitive resonance analysis
        cognitive_resonance = self._analyze_cognitive_resonance(query, response)
        temporal_resonance = self._analyze_temporal_resonance(query, response)
        
        # SPR detection using enhanced backend capabilities
        spr_activations = self._detect_sprs_in_content(query, response)
        
        # Create enhanced IAR data with frontend sophistication
        iar_data = {
            "status": status,
            "confidence": confidence,
            "summary": f"Query processed by {engine} engine",
            "potential_issues": potential_issues,
            "alignment_check": {
                "query_relevance": 0.9,
                "engine_selection": 0.8,
                "response_quality": confidence
            },
            "engine_used": engine,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            # Enhanced cognitive assessment
            "cognitive_resonance": cognitive_resonance,
            "temporal_resonance": temporal_resonance,
            "recommendations": self._generate_iar_recommendations(cognitive_resonance, temporal_resonance),
            "confidence_boost": max(0, 0.9 - confidence),
            "resonance_enhancement": max(0, 0.8 - ((cognitive_resonance["clarity"] + temporal_resonance["causal_understanding"]) / 2))
        }
        
        # Create enhanced message structure
        enhanced_response = {
            "id": f"arche_{int(time.time() * 1000)}",
            "content": self._format_response_content(response),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sender": "arche",
            "message_type": "chat",
            "protocol_compliance": True,
            "protocol_version": "ResonantiA v3.1-CA",
            "iar": iar_data,
            "spr_activations": spr_activations,  # Include SPR detection results
            "raw_response": response  # Include original response for debugging
        }
        
        return enhanced_response
    
    def _analyze_cognitive_resonance(self, query: str, response: Dict[str, Any]) -> Dict[str, float]:
        """Analyze cognitive resonance using frontend's sophisticated approach."""
        content = self._format_response_content(response)
        
        # Analyze clarity indicators
        clarity_indicators = ['clear', 'specific', 'example', 'detail', 'explain']
        clarity_score = self._calculate_indicator_score(content, clarity_indicators)
        
        # Analyze coherence indicators
        coherence_indicators = ['logical', 'structure', 'flow', 'organized', 'systematic']
        coherence_score = self._calculate_indicator_score(content, coherence_indicators)
        
        # Analyze completeness indicators
        completeness_indicators = ['complete', 'comprehensive', 'thorough', 'detailed', 'full']
        completeness_score = self._calculate_indicator_score(content, completeness_indicators)
        
        # Analyze contextual relevance
        contextual_relevance = 0.9 if len(content) > 100 else 0.6
        
        return {
            "clarity": min(0.9, 0.3 + clarity_score),
            "coherence": min(0.9, 0.3 + coherence_score),
            "completeness": min(0.9, 0.3 + completeness_score),
            "contextual_relevance": contextual_relevance
        }
    
    def _analyze_temporal_resonance(self, query: str, response: Dict[str, Any]) -> Dict[str, float]:
        """Analyze temporal resonance using frontend's 4D approach."""
        content = self._format_response_content(response)
        
        # Past context analysis
        past_indicators = ['history', 'past', 'previous', 'before', 'earlier', 'tradition']
        past_score = self._calculate_indicator_score(content, past_indicators)
        
        # Present accuracy analysis
        present_indicators = ['current', 'now', 'present', 'today', 'contemporary', 'modern']
        present_score = self._calculate_indicator_score(content, present_indicators)
        
        # Future projection analysis
        future_indicators = ['future', 'will', 'shall', 'project', 'predict', 'forecast']
        future_score = self._calculate_indicator_score(content, future_indicators)
        
        # Causal understanding analysis
        causal_indicators = ['cause', 'effect', 'because', 'therefore', 'result', 'consequence']
        causal_score = self._calculate_indicator_score(content, causal_indicators)
        
        return {
            "past_context": min(0.9, 0.2 + past_score),
            "present_accuracy": min(0.9, 0.3 + present_score),
            "future_projection": min(0.9, 0.2 + future_score),
            "causal_understanding": min(0.9, 0.3 + causal_score)
        }
    
    def _calculate_indicator_score(self, content: str, indicators: List[str]) -> float:
        """Calculate score based on indicator presence in content."""
        if not content:
            return 0.0
        
        lower_content = content.lower()
        matches = sum(1 for indicator in indicators if indicator in lower_content)
        return min(0.6, matches * 0.1)
    
    def _generate_iar_recommendations(self, cognitive_resonance: Dict[str, float], temporal_resonance: Dict[str, float]) -> List[str]:
        """Generate recommendations based on IAR analysis."""
        recommendations = []
        
        if cognitive_resonance["clarity"] < 0.7:
            recommendations.append("Enhance clarity by providing more specific examples")
        if cognitive_resonance["coherence"] < 0.7:
            recommendations.append("Improve logical flow and structure")
        if temporal_resonance["causal_understanding"] < 0.6:
            recommendations.append("Strengthen causal relationships and temporal context")
        if cognitive_resonance["completeness"] < 0.7:
            recommendations.append("Provide more comprehensive coverage of the topic")
        
        return recommendations
    
    def _detect_sprs_in_content(self, query: str, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect SPRs in query and response content using enhanced backend capabilities."""
        try:
            # Combine query and response content for SPR detection
            content = f"{query} {self._format_response_content(response)}"
            
            # Use the enhanced SPR manager if available
            if hasattr(self, 'spr_manager') and self.spr_manager:
                return self.spr_manager.detect_sprs_with_confidence(content)
            else:
                # Fallback to basic detection
                return self._basic_spr_detection(content)
        except Exception as e:
            logger.warning(f"SPR detection failed: {e}")
            return []
    
    def _basic_spr_detection(self, content: str) -> List[Dict[str, Any]]:
        """Basic SPR detection fallback."""
        # Simple keyword-based detection
        spr_keywords = {
            'IntegratedActionReflection': ['IAR', 'action reflection', 'integrated reflection'],
            'SparsePrimingRepresentations': ['SPR', 'sparse priming', 'priming representations'],
            'VisualCognitiveDebugger': ['VCD', 'visual debugger', 'cognitive debugger'],
            'ResonantInsightStrategyEngine': ['RISE', 'resonant insight', 'strategy engine'],
            'SynergisticIntentResonanceCycle': ['SIRC', 'synergistic intent', 'resonance cycle']
        }
        
        detected_sprs = []
        lower_content = content.lower()
        
        for spr_id, keywords in spr_keywords.items():
            for keyword in keywords:
                if keyword.lower() in lower_content:
                    detected_sprs.append({
                        'spr_id': spr_id,
                        'activation_level': 0.8,
                        'confidence_score': 0.7,
                        'guardian_point': spr_id,
                        'matched_keyword': keyword
                    })
                    break  # Only add once per SPR
        
        return detected_sprs
    
    def _format_response_content(self, response: Dict[str, Any]) -> str:
        """
        Format the response content for display in the VCD.
        """
        if "error" in response:
            return f"Error: {response['error']}"
        elif "final_strategy" in response:
            return f"RISE Strategy Generated:\n\n{response.get('final_strategy', 'No strategy available')}"
        elif "response" in response:
            return str(response["response"])
        else:
            return json.dumps(response, indent=2, default=str)

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
                    
                    # First stream any buffered SIRC events
                    try:
                        if hasattr(self, '_event_queue') and self._event_queue:
                            for evt in self._event_queue:
                                await websocket.send(json.dumps(evt))
                            self._event_queue.clear()
                    except Exception:
                        pass
                    
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
    
    # Start the Nexus WebSocket server in a background thread
    nexus_interface.start_server_in_thread()
    
    logger.info(f"🚀 Attempting to start ArchE Mastermind Server on {host}:{websocket_port}")
    
    try:
        # We are not running a websocket server from here anymore, just the cognitive loop.
        # This part of the code could be adapted to run a main cognitive loop
        # or other primary server task. For now, we will just wait.
        logger.info("✅ ArchE Mastermind Server core is running.")
        logger.info("Nexus WebSocket bridge is running in a background thread.")
        await asyncio.Future() # Keep the main thread alive
    except OSError as e:
        logger.critical(f"FATAL: Failed to start server components. Error: {e}")
    except Exception as e:
        logger.critical(f"FATAL: An unexpected error occurred: {e}", exc_info=True)
    finally:
        logger.info("Shutting down Nexus server...")
        nexus_interface.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Server shutting down.")
    except Exception as e:
        logger.critical(f"💥 Server failed to start: {e}", exc_info=True)
