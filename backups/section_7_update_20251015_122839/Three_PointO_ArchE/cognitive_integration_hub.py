"""
Cognitive Integration Hub
The Neural Nexus - Connecting CRCS, RISE, and ACO

This module serves as the central integration point for ArchE's cognitive architecture,
orchestrating the flow between:
- CRCS (Cognitive Resonant Controller System) - The Cerebellum (fast, instinctual)
- RISE (Recursive Inquiry & Synthesis Engine) - The Cerebrum (slow, deliberate)
- ACO (Adaptive Cognitive Orchestrator) - The Meta-Learner (pattern evolution)

Philosophical Foundation:
- Fast and Slow Thinking (Kahneman's dual process theory)
- Hierarchical cognitive processing
- Autopoietic learning through feedback loops
- Quantum probability for confidence tracking

The Hub implements the complete cognitive flow:
Query → CRCS (fast path) → [fallback] → RISE (slow path) → ACO (learning) → Evolution
"""

import logging
import time
import random
from datetime import datetime
from typing import Any, Dict, Optional, List
from pathlib import Path

# Import the canonical types
from .canonical_types import CognitiveResponse, QuantumProbability, CognitiveMetrics

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now, now_iso, ago, from_now, format_log, format_filename


# Initialize logger for this module
logger = logging.getLogger(__name__)

# Fallback CRCS and RISE imports
try:
    from .cognitive_resonant_controller import CognitiveResonantController, CRCS_AVAILABLE
except ImportError:
    CRCS_AVAILABLE = False
    logger.warning("CognitiveResonantController not available")

try:
    from .rise_orchestrator import RISE_Orchestrator, RISE_AVAILABLE
except ImportError:
    RISE_AVAILABLE = False
    logger.warning("RISE_Orchestrator not available")
    raise  # Re-raise the exception to see the underlying error

try:
    from .thought_trail import thought_trail, THOUGHT_TRAIL_AVAILABLE
except ImportError:
    THOUGHT_TRAIL_AVAILABLE = False
    logger.warning("thought_trail not available")

try:
    from .system_health_monitor import SystemHealthMonitor, HEALTH_MONITOR_AVAILABLE
except ImportError:
    HEALTH_MONITOR_AVAILABLE = False
    logger.warning("SystemHealthMonitor not available")


class CognitiveIntegrationHub:
    """
    The Neural Nexus - Central integration of ArchE's cognitive architecture.
    
    This hub orchestrates the complete cognitive flow:
    1. All queries enter through process_query()
    2. CRCS attempts fast, specialized processing
    3. On fallback, RISE provides deep analysis
    4. ACO observes patterns and proposes evolutions
    5. ThoughtTrail captures all experiences for learning
    
    The hub maintains quantum confidence states throughout the flow,
    enabling probabilistic decision-making and measurable improvement.
    """
    
    def __init__(
        self,
        protocol_chunks: Optional[List[str]] = None,
        confidence_threshold: float = 0.7,
        enable_learning: bool = True
    ):
        """
        Initialize the Cognitive Integration Hub.
        
        Args:
            protocol_chunks: Protocol chunks for CRCS and other systems
            confidence_threshold: Minimum confidence for CRCS direct path
            enable_learning: Whether to enable ACO pattern learning
        """
        self.crcs_threshold = 0.7  # Base threshold
        self.exploration_rate = 0.001 # Agent of Chaos: 0.1% of queries
        self.enable_learning = enable_learning
        self.metrics = CognitiveMetrics()
        
        # Load protocol chunks if not provided
        if protocol_chunks is None:
            protocol_chunks = self._load_protocol_chunks()
        
        # Initialize cognitive components
        self.crcs = CognitiveResonantController() if CRCS_AVAILABLE else None
        self.rise = RISE_Orchestrator() if RISE_AVAILABLE else None
        self.aco = None # ACO is not initialized here, it's handled by the new route_query
        self.thought_trail = thought_trail if THOUGHT_TRAIL_AVAILABLE else None
        self.health_monitor = SystemHealthMonitor() if HEALTH_MONITOR_AVAILABLE else None
        
        logger.info(f"[CognitiveHub] Initialized with confidence_threshold={confidence_threshold}, learning_enabled={enable_learning}")
    
    def _load_protocol_chunks(self) -> List[str]:
        """Load protocol chunks from specifications."""
        protocol_chunks = []
        spec_dir = Path(__file__).parent.parent / "specifications"
        
        if not spec_dir.exists():
            logger.warning(f"Specification directory not found: {spec_dir}")
            return ["Default protocol chunk for initialization"]
        
        for spec_file in spec_dir.glob("*.md"):
            try:
                with open(spec_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Split into reasonable chunks (approx 2000 chars each)
                    chunk_size = 2000
                    for i in range(0, len(content), chunk_size):
                        protocol_chunks.append(content[i:i+chunk_size])
            except Exception as e:
                logger.error(f"Failed to load {spec_file}: {e}")
        
        logger.info(f"[CognitiveHub] Loaded {len(protocol_chunks)} protocol chunks")
        return protocol_chunks if protocol_chunks else ["Default protocol chunk"]
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> CognitiveResponse:
        """
        Process a query through the integrated cognitive architecture.
        
        This is the main entry point that orchestrates the complete cognitive flow:
        1. Try CRCS (fast path) first
        2. Fallback to RISE (slow path) if confidence is low
        3. Report to ACO for pattern learning
        4. Log to ThoughtTrail for experience capture
        
        Args:
            query: The user query to process
            context: Optional context information
            
        Returns:
            CognitiveResponse with content and quantum confidence
        """
        start_time = time.time()
        context = context or {}
        
        self.metrics.total_queries += 1
        
        # Log to ThoughtTrail (Stardust phase - Experience Capture)
        if self.thought_trail:
            self.thought_trail.add_entry({
                "timestamp": now_iso(),
                "query": query,
                "context": context,
                "phase": "query_ingestion"
            })
        
        # Phase 1: Try CRCS (The Cerebellum - Fast, Instinctual)
        crcs_response = None
        crcs_confidence = None
        
        if self.crcs:
            try:
                crcs_result = self.crcs.process_query(query)
                crcs_response = crcs_result.get("response", "")
                crcs_confidence_value = crcs_result.get("confidence", 0.5)
                
                crcs_time = (time.time() - start_time) * 1000
                self.metrics.crcs_direct_count += 1
                self.metrics.update_avg("avg_crcs_time_ms", crcs_time, self.metrics.crcs_direct_count)
                
                # Create quantum confidence state
                evidence = []
                if crcs_result.get("controller"):
                    evidence.append(f"controller:{crcs_result['controller']}")
                if crcs_result.get("fallback", False):
                    evidence.append("fallback_activated")
                else:
                    evidence.append("direct_match")
                
                crcs_confidence = QuantumProbability(crcs_confidence_value, evidence)
                
                # If confidence is high enough, return CRCS result
                if crcs_confidence.probability >= self.crcs_threshold:
                    response = CognitiveResponse(
                        content=crcs_response,
                        processing_path="crcs_direct",
                        confidence=crcs_confidence,
                        processing_time_ms=crcs_time,
                        controller_used=crcs_result.get("controller"),
                        metadata={"crcs_result": crcs_result}
                    )
                    
                    # Report success to ACO for pattern learning
                    if self.aco and self.enable_learning:
                        self._report_to_aco(query, response, success=True)
                    
                    self._log_response(response)
                    return response
                
            except Exception as e:
                logger.error(f"[CognitiveHub] CRCS processing failed: {e}")
                crcs_confidence = QuantumProbability.uncertain(0.2, ["crcs_error", str(type(e).__name__)])
        
        # Phase 2: Fallback to RISE (The Cerebrum - Slow, Deliberate)
        self.metrics.crcs_fallback_count += 1
        
        fallback_reason = "low_confidence" if crcs_confidence and crcs_confidence.probability < self.crcs_threshold else "crcs_unavailable"
        
        if not self.rise:
            # No RISE available, return CRCS result even if low confidence
            if crcs_response:
                response = CognitiveResponse(
                    content=crcs_response,
                    processing_path="crcs_fallback",
                    confidence=crcs_confidence or QuantumProbability.uncertain(0.3, ["no_rise_available"]),
                    processing_time_ms=(time.time() - start_time) * 1000,
                    fallback_reason="rise_unavailable",
                    metadata={"warning": "RISE not available, using low-confidence CRCS result"}
                )
            else:
                response = CognitiveResponse(
                    content="I'm unable to process this query with sufficient confidence.",
                    processing_path="system_failure",
                    confidence=QuantumProbability.certain_false(),
                    processing_time_ms=(time.time() - start_time) * 1000,
                    fallback_reason="no_cognitive_systems_available"
                )
            
            self._log_response(response)
            return response
        
        # Execute RISE processing
        try:
            rise_start = time.time()
            rise_result = self.rise.process_query(query, context)
            rise_time = (time.time() - rise_start) * 1000
            
            self.metrics.rise_escalation_count += 1
            self.metrics.update_avg("avg_rise_time_ms", rise_time, self.metrics.rise_escalation_count)
            
            # Extract RISE response and confidence
            rise_response = rise_result.get("response", rise_result.get("final_synthesis", ""))
            rise_confidence_value = rise_result.get("confidence", 0.8)
            
            rise_confidence = QuantumProbability(
                rise_confidence_value,
                ["rise_deep_analysis", f"fallback_from_crcs:{fallback_reason}"]
            )
            
            response = CognitiveResponse(
                content=rise_response,
                processing_path="rise_escalation",
                confidence=rise_confidence,
                processing_time_ms=(time.time() - start_time) * 1000,
                fallback_reason=fallback_reason,
                metadata={
                    "crcs_attempted": crcs_response is not None,
                    "crcs_confidence": crcs_confidence.to_dict() if crcs_confidence else None,
                    "rise_result": rise_result
                }
            )
            
            # Report to ACO for pattern learning
            if self.aco and self.enable_learning:
                self._report_to_aco(query, response, success=True, fallback=True)
            
            self._log_response(response)
            return response
            
        except Exception as e:
            logger.error(f"[CognitiveHub] RISE processing failed: {e}")
            
            # Complete failure - return error response
            response = CognitiveResponse(
                content=f"Cognitive processing failed: {str(e)}",
                processing_path="system_failure",
                confidence=QuantumProbability.uncertain(0.1, ["rise_error", str(type(e).__name__)]),
                processing_time_ms=(time.time() - start_time) * 1000,
                fallback_reason="rise_exception",
                metadata={"error": str(e)}
            )
            
            if self.aco and self.enable_learning:
                self._report_to_aco(query, response, success=False)
            
            self._log_response(response)
            return response
    
    def _report_to_aco(self, query: str, response: CognitiveResponse, success: bool, fallback: bool = False):
        """
        Report query processing to ACO for pattern learning (Nebulae phase).
        
        This enables the ACO to detect recurring patterns and propose
        new specialized controllers for common query types.
        """
        try:
            if not self.aco:
                return
            
            # This would call ACO's pattern analysis
            # For now, we'll log the pattern
            self.metrics.learning_events += 1
            
            logger.debug(f"[CognitiveHub] Reported to ACO: query_success={success}, fallback={fallback}, confidence={response.confidence.probability:.3f}")
            
            # ACO would analyze this and potentially propose new controllers
            # if it detects a recurring pattern of fallbacks
            
        except Exception as e:
            logger.error(f"[CognitiveHub] Failed to report to ACO: {e}")
    
    def _log_response(self, response: CognitiveResponse):
        """Log response to ThoughtTrail for learning."""
        if self.thought_trail:
            try:
                self.thought_trail.add_entry({
                    "timestamp": now_iso(),
                    "response": response.to_dict(),
                    "phase": "response_delivery"
                })
            except Exception as e:
                logger.error(f"[CognitiveHub] Failed to log to ThoughtTrail: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            "total_queries": self.metrics.total_queries,
            "crcs_usage": {
                "direct_count": self.metrics.crcs_direct_count,
                "fallback_count": self.metrics.crcs_fallback_count,
                "direct_rate": self.metrics.crcs_direct_count / max(1, self.metrics.total_queries),
                "avg_time_ms": self.metrics.avg_crcs_time_ms
            },
            "rise_usage": {
                "escalation_count": self.metrics.rise_escalation_count,
                "escalation_rate": self.metrics.rise_escalation_count / max(1, self.metrics.total_queries),
                "avg_time_ms": self.metrics.avg_rise_time_ms
            },
            "learning": {
                "enabled": self.enable_learning,
                "learning_events": self.metrics.learning_events
            },
            "system_health": {
                "crcs_available": self.crcs is not None,
                "rise_available": self.rise is not None,
                "aco_available": self.aco is not None,
                "thought_trail_available": self.thought_trail is not None
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "hub_initialized": True,
            "components": {
                "crcs": {
                    "available": self.crcs is not None,
                    "type": type(self.crcs).__name__ if self.crcs else None
                },
                "rise": {
                    "available": self.rise is not None,
                    "type": type(self.rise).__name__ if self.rise else None
                },
                "aco": {
                    "available": self.aco is not None,
                    "enabled": self.enable_learning,
                    "type": type(self.aco).__name__ if self.aco else None
                },
                "thought_trail": {
                    "available": self.thought_trail is not None,
                    "type": type(self.thought_trail).__name__ if self.thought_trail else None
                }
            },
            "configuration": {
                "confidence_threshold": self.crcs_threshold,
                "learning_enabled": self.enable_learning
            },
            "metrics": self.get_metrics()
        }
        
        return status

    def _create_initial_superposition(self, query: str) -> Dict[str, float]:
        """
        Creates a quantum superposition of intents from a query.
        
        In a real implementation, this would use a sophisticated NLP model.
        Here, we simulate it based on keywords.
        """
        # Simulate NLP analysis to get potential intents and their probabilities
        superposition = {"generic_inquiry": 0.5} # Default
        
        if "analyze" in query.lower() or "report" in query.lower():
            superposition["data_analysis"] = 0.8
        if "create" in query.lower() or "generate" in query.lower():
            superposition["content_generation"] = 0.7
        if "execute" in query.lower() or "run" in query.lower():
            superposition["code_execution"] = 0.9
            
        # Normalize probabilities
        total_prob = sum(superposition.values())
        normalized_superposition = {k: v / total_prob for k, v in superposition.items()}
        
        return normalized_superposition

    def route_query(self, query: str, model: str = None, workflow_name: str = None) -> CognitiveResponse:
        """
        Routes a query through the cognitive architecture.
        1.  Represents the query as a quantum superposition of intents.
        """
        start_time = time.time()
        context = {} # Initialize context

        initial_superposition = self._create_initial_superposition(query)
        
        logger.info(f"[CIH] Query superposition: {initial_superposition}")

        # --- Cognitive Immune System Pre-computation ---
        effective_threshold = self._get_dynamic_threshold()
        suppression_flags = self.health_monitor.get_suppression_flags() if self.health_monitor else {}
        is_exploration_override = random.random() < self.exploration_rate

        # --- 2. CRCS Resonance ---
        crcs_response = self.crcs.handle_query(query)
        
        # Check for suppression
        if crcs_response.controller_used in suppression_flags:
            logger.warning(f"[CIH] Sentinel of Performance: Suppressing CRCS controller '{crcs_response.controller_used}' due to suboptimal performance.")
            crcs_response.confidence.probability = 0.1 # Override confidence
            
        # Check for exploration override
        if is_exploration_override and crcs_response.confidence.collapse() >= effective_threshold:
            logger.info(f"[CIH] Agent of Chaos: Intentionally ignoring CRCS match for exploration.")
            crcs_response.confidence.probability = 0.1 # Override confidence by altering probability before collapse

        if crcs_response.confidence.collapse() >= effective_threshold:
            logger.info(f"[CIH] CRCS collapsed superposition with high confidence ({crcs_response.confidence.probability:.2f})")
            final_response = crcs_response
        else:
            logger.info(f"[CIH] CRCS confidence ({crcs_response.confidence.probability:.2f}) below threshold or controller suppressed, escalating to RISE.")
            try:
                # Pass the model and workflow parameters down to the RISE orchestrator
                final_response = self.rise.process_query(
                    query, 
                    {"crcs_context": crcs_response.metadata}, 
                    model=model,
                    workflow_name=workflow_name
                )
                # Handle both dict and CognitiveResponse objects
                if isinstance(final_response, dict):
                    self.thought_trail.add_entry(final_response)
                else:
                    self.thought_trail.add_entry(final_response.to_dict())
            except Exception as e:
                logger.error(f"[CIH] RISE processing failed: {e}", exc_info=True)

        # Log to ThoughtTrail (Stardust phase - Experience Capture)
        if self.thought_trail:
            self.thought_trail.add_entry({
                "timestamp": now_iso(),
                "query": query,
                "context": context,
                "phase": "response_delivery"
            })

        return final_response

    def _get_dynamic_threshold(self) -> float:
        """
        Mechanism 1: The Penumbra of Uncertainty.
        Adjusts the CRCS confidence threshold based on system health.
        """
        if not self.health_monitor:
            return self.crcs_threshold

        # Get a general 'system load' metric (0.0 = idle, 1.0 = max load)
        system_load = self.health_monitor.get_current_load() 
        
        # If system is idle (low load), be "pickier" by raising the threshold
        # If system is busy (high load), be "less picky" to save resources
        dynamic_threshold = self.crcs_threshold + (0.2 * (1.0 - system_load)) # e.g., raises threshold up to 0.9 when idle
        
        logger.debug(f"[CIH] Penumbra of Uncertainty: System load is {system_load:.2f}, dynamic threshold is {dynamic_threshold:.2f}")
        return min(dynamic_threshold, 0.95) # Cap at 0.95


def main():
    """Demo the Cognitive Integration Hub."""
    print("🧠 Initializing Cognitive Integration Hub...")
    print()
    
    hub = CognitiveIntegrationHub(enable_learning=True)
    
    print("✓ Hub initialized!")
    print()
    
    # Display system status
    status = hub.get_system_status()
    print("System Status:")
    print(f"  CRCS Available: {status['components']['crcs']['available']}")
    print(f"  RISE Available: {status['components']['rise']['available']}")
    print(f"  ACO Available: {status['components']['aco']['available']}")
    print(f"  ThoughtTrail Available: {status['components']['thought_trail']['available']}")
    print()
    
    # Test queries
    test_queries = [
        "What is an SPR?",
        "Explain quantum entanglement in the context of CFP",
        "How does the Autopoietic Learning Loop work?"
    ]
    
    print("Processing test queries...")
    print()
    
    for query in test_queries:
        print(f"Query: {query}")
        response = hub.process_query(query)
        print(f"  Path: {response.processing_path}")
        print(f"  Confidence: {response.confidence.probability:.3f}")
        print(f"  Time: {response.processing_time_ms:.2f}ms")
        if response.controller_used:
            print(f"  Controller: {response.controller_used}")
        print()
    
    # Display final metrics
    metrics = hub.get_metrics()
    print("Final Metrics:")
    print(f"  Total Queries: {metrics['total_queries']}")
    print(f"  CRCS Direct: {metrics['crcs_usage']['direct_count']} ({metrics['crcs_usage']['direct_rate']:.1%})")
    print(f"  RISE Escalations: {metrics['rise_usage']['escalation_count']} ({metrics['rise_usage']['escalation_rate']:.1%})")
    print(f"  Learning Events: {metrics['learning']['learning_events']}")


if __name__ == "__main__":
    main()

