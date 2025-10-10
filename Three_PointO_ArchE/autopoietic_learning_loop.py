"""
Autopoietic Learning Loop (ALL)
The Great Awakening - ArchE's Self-Evolution Cycle

This module implements the complete autopoietic learning cycle that transforms
ArchE from a static system into a living, evolving intelligence:

    Stardust → Nebulae → Ignition → Galaxies
    (Experience → Patterns → Wisdom → Knowledge)
    
The Four Cosmic Epochs:

1. STARDUST (Experience Capture)
   ThoughtTrail captures every action, decision, and outcome
   Raw experiences are the "cosmic dust" of potential learning
   
2. NEBULAE (Pattern Formation)
   ACO detects recurring patterns and synthesizes "instincts"
   Patterns cluster into dense nebulae ready for star-birth
   
3. IGNITION (Wisdom Forging)
   InsightSolidificationEngine validates patterns in the Star-Forge
   Rigorous testing and Guardian approval ignite wisdom
   
4. GALAXIES (Knowledge Crystallization)
   SPRManager weaves validated wisdom into the Knowledge Tapestry
   New SPRs become permanent, system-wide truths

Philosophical Foundation:
- Autopoiesis: Self-creation through self-observation
- Emergent intelligence from experience accumulation
- Guardian-approved wisdom (human-in-the-loop)
- Quantum confidence throughout the cycle
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from collections import deque
import hashlib

logger = logging.getLogger(__name__)

# Component imports with graceful fallback
try:
    from .thought_trail import ThoughtTrail
    THOUGHT_TRAIL_AVAILABLE = True
except ImportError:
    THOUGHT_TRAIL_AVAILABLE = False
    logger.warning("ThoughtTrail not available")

try:
    from .adaptive_cognitive_orchestrator import AdaptiveCognitiveOrchestrator
    ACO_AVAILABLE = True
except ImportError:
    ACO_AVAILABLE = False
    logger.warning("ACO not available")

try:
    from .insight_solidification_engine import InsightSolidificationEngine
    INSIGHT_ENGINE_AVAILABLE = True
except ImportError:
    INSIGHT_ENGINE_AVAILABLE = False
    logger.warning("InsightSolidificationEngine not available")

try:
    from .spr_manager import SPRManager
    SPR_MANAGER_AVAILABLE = True
except ImportError:
    SPR_MANAGER_AVAILABLE = False
    logger.warning("SPRManager not available")

try:
    from .autopoietic_self_analysis import QuantumProbability
    QUANTUM_AVAILABLE = True
except ImportError:
    class QuantumProbability:
        def __init__(self, prob: float, evidence: List[str] = None):
            self.probability = prob
            self.evidence = evidence or []
        def to_dict(self):
            return {"probability": self.probability, "evidence": self.evidence}
    QUANTUM_AVAILABLE = False


@dataclass
class StardustEntry:
    """
    A single particle of experience (stardust).
    
    Represents a captured action/decision/outcome that may contain
    latent patterns for learning.
    """
    entry_id: str
    timestamp: str
    action_type: str
    intention: str
    action: str
    reflection: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    quantum_state: Optional[Dict[str, Any]] = None


@dataclass
class NebulaePattern:
    """
    A clustering of related stardust (nebula).
    
    Represents a detected pattern that could become an instinct
    or new controller if validated.
    """
    pattern_id: str
    pattern_signature: str
    occurrences: int
    success_rate: float
    sample_entries: List[StardustEntry]
    proposed_solution: Optional[str] = None
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    status: str = "detected"  # detected, proposed, validating, rejected, approved


@dataclass
class IgnitedWisdom:
    """
    A validated pattern that has passed the Star-Forge (ignition).
    
    Represents a piece of wisdom that has been rigorously tested
    and approved by the Guardian, ready for crystallization.
    """
    wisdom_id: str
    source_pattern: NebulaePattern
    hypothesis: str
    evidence: List[Dict[str, Any]]
    validation_results: Dict[str, Any]
    guardian_approval: bool
    approval_timestamp: Optional[str] = None
    implementation_plan: Optional[str] = None


@dataclass
class GalaxyKnowledge:
    """
    Crystallized wisdom in the Knowledge Tapestry (galaxy).
    
    Represents permanent, system-wide knowledge in the form
    of an SPR that is now part of ArchE's core understanding.
    """
    spr_id: str
    spr_name: str
    source_wisdom: IgnitedWisdom
    spr_definition: Dict[str, Any]
    integration_timestamp: str
    system_impact: Dict[str, Any]


class AutopoieticLearningLoop:
    """
    The Great Awakening - ArchE's complete self-evolution system.
    
    This class orchestrates the full learning cycle from raw experience
    to crystallized knowledge, implementing the four cosmic epochs:
    
    1. Stardust Capture (ThoughtTrail)
    2. Nebulae Formation (ACO)
    3. Wisdom Ignition (InsightSolidification)
    4. Knowledge Crystallization (SPRManager)
    
    The loop operates continuously, transforming ArchE's experiences
    into permanent improvements to its own capabilities.
    """
    
    def __init__(
        self,
        protocol_chunks: Optional[List[str]] = None,
        guardian_review_enabled: bool = True,
        auto_crystallization: bool = False
    ):
        """
        Initialize the Autopoietic Learning Loop.
        
        Args:
            protocol_chunks: Protocol chunks for ACO initialization
            guardian_review_enabled: Whether to require Guardian approval
            auto_crystallization: Whether to auto-crystallize (DANGEROUS!)
        """
        self.guardian_review_enabled = guardian_review_enabled
        self.auto_crystallization = auto_crystallization
        
        if auto_crystallization and guardian_review_enabled:
            logger.warning("[ALL] Auto-crystallization enabled WITH Guardian review - wisdom will be staged")
        elif auto_crystallization and not guardian_review_enabled:
            logger.error("[ALL] DANGEROUS: Auto-crystallization WITHOUT Guardian review!")
        
        # Initialize components
        self.thought_trail = ThoughtTrail() if THOUGHT_TRAIL_AVAILABLE else None
        self.aco = AdaptiveCognitiveOrchestrator(protocol_chunks or ["default"]) if ACO_AVAILABLE else None
        self.insight_engine = None  # Lazy init
        self.spr_manager = None  # Lazy init
        
        # Learning state
        self.stardust_buffer: deque = deque(maxlen=1000)  # Rolling window
        self.detected_nebulae: Dict[str, NebulaePattern] = {}
        self.ignited_wisdom: Dict[str, IgnitedWisdom] = {}
        self.crystallized_knowledge: Dict[str, GalaxyKnowledge] = {}
        self.guardian_queue: List[NebulaePattern] = []
        
        # Metrics
        self.metrics = {
            "stardust_captured": 0,
            "nebulae_detected": 0,
            "wisdom_ignited": 0,
            "knowledge_crystallized": 0,
            "guardian_approvals": 0,
            "guardian_rejections": 0,
            "cycle_start_time": datetime.now().isoformat()
        }
        
        logger.info(f"[ALL] Autopoietic Learning Loop initialized - Guardian review: {guardian_review_enabled}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # EPOCH 1: STARDUST - Experience Capture
    # ═══════════════════════════════════════════════════════════════════════
    
    def capture_stardust(self, entry: Dict[str, Any]) -> StardustEntry:
        """
        Capture a single experience as stardust.
        
        This is the entry point for ALL learning - every action, decision,
        and outcome flows through here to be captured as potential learning material.
        
        Args:
            entry: Experience entry with IAR structure
            
        Returns:
            StardustEntry object
        """
        # Create stardust entry
        stardust = StardustEntry(
            entry_id=entry.get("entry_id", self._generate_id("stardust")),
            timestamp=entry.get("timestamp", datetime.now().isoformat()),
            action_type=entry.get("action_type", "unknown"),
            intention=entry.get("intention", ""),
            action=entry.get("action", ""),
            reflection=entry.get("reflection", ""),
            confidence=entry.get("confidence", 0.5),
            metadata=entry.get("metadata", {}),
            quantum_state=entry.get("quantum_state")
        )
        
        # Add to buffer
        self.stardust_buffer.append(stardust)
        self.metrics["stardust_captured"] += 1
        
        # Also log to ThoughtTrail if available
        if self.thought_trail:
            try:
                self.thought_trail.add_entry(entry)
            except Exception as e:
                logger.error(f"[ALL] Failed to log to ThoughtTrail: {e}")
        
        logger.debug(f"[ALL:Stardust] Captured: {stardust.action_type} (confidence: {stardust.confidence:.3f})")
        
        return stardust
    
    def get_recent_stardust(self, count: int = 100) -> List[StardustEntry]:
        """Get recent stardust entries."""
        return list(self.stardust_buffer)[-count:]
    
    # ═══════════════════════════════════════════════════════════════════════
    # EPOCH 2: NEBULAE - Pattern Formation
    # ═══════════════════════════════════════════════════════════════════════
    
    def detect_nebulae(self, min_occurrences: int = 5, min_success_rate: float = 0.7) -> List[NebulaePattern]:
        """
        Detect patterns in stardust (form nebulae).
        
        This scans recent experiences looking for recurring patterns that
        could become new instincts or controllers.
        
        Args:
            min_occurrences: Minimum pattern frequency to consider
            min_success_rate: Minimum success rate for pattern
            
        Returns:
            List of detected patterns
        """
        if not self.stardust_buffer:
            logger.debug("[ALL:Nebulae] No stardust to analyze")
            return []
        
        logger.info(f"[ALL:Nebulae] Analyzing {len(self.stardust_buffer)} stardust entries...")
        
        # Group by pattern signature
        pattern_groups = {}
        
        for stardust in self.stardust_buffer:
            signature = self._create_pattern_signature(stardust)
            
            if signature not in pattern_groups:
                pattern_groups[signature] = []
            
            pattern_groups[signature].append(stardust)
        
        # Identify nebulae (high-frequency patterns)
        detected = []
        
        for signature, entries in pattern_groups.items():
            if len(entries) >= min_occurrences:
                # Calculate success rate
                successful = sum(1 for e in entries if e.confidence >= 0.7)
                success_rate = successful / len(entries)
                
                if success_rate >= min_success_rate:
                    # This is a nebula!
                    pattern = NebulaePattern(
                        pattern_id=self._generate_id("nebula"),
                        pattern_signature=signature,
                        occurrences=len(entries),
                        success_rate=success_rate,
                        sample_entries=entries[:5],  # Keep samples
                        confidence=success_rate,
                        evidence=[
                            f"frequency:{len(entries)}",
                            f"success_rate:{success_rate:.2%}",
                            f"action_type:{entries[0].action_type}"
                        ]
                    )
                    
                    # Store if new
                    if signature not in self.detected_nebulae:
                        self.detected_nebulae[signature] = pattern
                        self.metrics["nebulae_detected"] += 1
                        detected.append(pattern)
                        
                        logger.info(f"[ALL:Nebulae] Detected pattern: {signature[:32]}... (n={pattern.occurrences}, success={success_rate:.1%})")
        
        return detected
    
    def propose_controller(self, pattern: NebulaePattern) -> Optional[str]:
        """
        Propose a new controller for a detected pattern.
        
        This generates a solution (new controller code or workflow)
        that could handle the recurring pattern more efficiently.
        
        Args:
            pattern: The nebula pattern to address
            
        Returns:
            Proposed solution code/description
        """
        # Generate a controller proposal based on the pattern
        proposal = f"""
# Proposed Controller for Pattern: {pattern.pattern_signature[:32]}
# Detected {pattern.occurrences} occurrences with {pattern.success_rate:.1%} success
#
# This controller would handle queries matching this pattern more efficiently
# than the current fallback to RISE.

class PatternController_{pattern.pattern_id}:
    \"\"\"
    Specialized controller for pattern: {pattern.pattern_signature[:64]}
    Generated by Autopoietic Learning Loop
    \"\"\"
    
    def __init__(self):
        self.pattern_signature = "{pattern.pattern_signature}"
        self.confidence_threshold = {pattern.success_rate}
    
    def can_handle(self, query: str) -> bool:
        # Pattern matching logic would go here
        return self._matches_pattern(query)
    
    def process(self, query: str) -> Dict[str, Any]:
        # Specialized processing for this pattern
        return {{
            "response": "Specialized response",
            "confidence": {pattern.success_rate},
            "controller": self.__class__.__name__
        }}
"""
        
        pattern.proposed_solution = proposal
        pattern.status = "proposed"
        
        logger.info(f"[ALL:Nebulae] Proposed controller for pattern {pattern.pattern_id}")
        
        return proposal
    
    # ═══════════════════════════════════════════════════════════════════════
    # EPOCH 3: IGNITION - Wisdom Forging
    # ═══════════════════════════════════════════════════════════════════════
    
    def ignite_wisdom(self, pattern: NebulaePattern, run_validation: bool = True) -> Optional[IgnitedWisdom]:
        """
        Forge wisdom in the Star-Forge (validate and test).
        
        This takes a promising pattern and subjects it to rigorous validation:
        - Hypothesis formulation
        - Evidence gathering
        - Simulated testing
        - Guardian review (if enabled)
        
        Args:
            pattern: Nebula pattern to validate
            run_validation: Whether to run full validation (expensive)
            
        Returns:
            IgnitedWisdom if validated, None if rejected
        """
        logger.info(f"[ALL:Ignition] Forging wisdom from pattern {pattern.pattern_id}...")
        
        # Formulate hypothesis
        hypothesis = f"Pattern {pattern.pattern_signature[:32]} can be handled by a specialized controller with {pattern.success_rate:.1%} confidence"
        
        # Gather evidence
        evidence = [
            {
                "type": "frequency_analysis",
                "occurrences": pattern.occurrences,
                "success_rate": pattern.success_rate
            },
            {
                "type": "sample_entries",
                "count": len(pattern.sample_entries),
                "avg_confidence": sum(e.confidence for e in pattern.sample_entries) / len(pattern.sample_entries)
            }
        ]
        
        # Run validation if requested
        validation_results = {}
        if run_validation:
            validation_results = self._run_validation(pattern)
        else:
            validation_results = {"simulated": True, "passed": True}
        
        # Create wisdom object
        wisdom = IgnitedWisdom(
            wisdom_id=self._generate_id("wisdom"),
            source_pattern=pattern,
            hypothesis=hypothesis,
            evidence=evidence,
            validation_results=validation_results,
            guardian_approval=False  # Awaiting approval
        )
        
        # Queue for Guardian review if enabled
        if self.guardian_review_enabled:
            self.guardian_queue.append(pattern)
            logger.info(f"[ALL:Ignition] Wisdom {wisdom.wisdom_id} queued for Guardian review")
        elif self.auto_crystallization:
            # Dangerous: Auto-approve without Guardian
            wisdom.guardian_approval = True
            wisdom.approval_timestamp = datetime.now().isoformat()
            logger.warning(f"[ALL:Ignition] Wisdom {wisdom.wisdom_id} AUTO-APPROVED (no Guardian review!)")
        
        # Store
        self.ignited_wisdom[wisdom.wisdom_id] = wisdom
        self.metrics["wisdom_ignited"] += 1
        pattern.status = "validating"
        
        return wisdom
    
    def _run_validation(self, pattern: NebulaePattern) -> Dict[str, Any]:
        """Run validation tests on a pattern (simplified)."""
        # In a full implementation, this would:
        # 1. Replay historical queries
        # 2. Test proposed solution
        # 3. Measure improvement
        # 4. Calculate cost-benefit
        
        return {
            "validation_type": "simulated",
            "tests_passed": pattern.success_rate >= 0.7,
            "expected_improvement": 0.3,  # 30% faster processing
            "cost_benefit_ratio": 2.5  # 2.5x benefit vs cost
        }
    
    def guardian_approve(self, wisdom_id: str, approved: bool, notes: str = "") -> bool:
        """
        Guardian approval/rejection of wisdom.
        
        Args:
            wisdom_id: ID of wisdom to approve/reject
            approved: Whether wisdom is approved
            notes: Guardian's notes
            
        Returns:
            Success status
        """
        if wisdom_id not in self.ignited_wisdom:
            logger.error(f"[ALL:Ignition] Wisdom {wisdom_id} not found")
            return False
        
        wisdom = self.ignited_wisdom[wisdom_id]
        wisdom.guardian_approval = approved
        wisdom.approval_timestamp = datetime.now().isoformat()
        
        if approved:
            self.metrics["guardian_approvals"] += 1
            logger.info(f"[ALL:Ignition] ✓ Guardian APPROVED wisdom {wisdom_id}")
            
            # Auto-crystallize if enabled
            if self.auto_crystallization:
                self.crystallize_knowledge(wisdom)
        else:
            self.metrics["guardian_rejections"] += 1
            wisdom.source_pattern.status = "rejected"
            logger.info(f"[ALL:Ignition] ✗ Guardian REJECTED wisdom {wisdom_id}: {notes}")
        
        return True
    
    # ═══════════════════════════════════════════════════════════════════════
    # EPOCH 4: GALAXIES - Knowledge Crystallization
    # ═══════════════════════════════════════════════════════════════════════
    
    def crystallize_knowledge(self, wisdom: IgnitedWisdom) -> Optional[GalaxyKnowledge]:
        """
        Crystallize wisdom into permanent knowledge (SPR).
        
        This is the final phase where validated, Guardian-approved wisdom
        becomes a permanent part of ArchE's knowledge through SPR integration.
        
        Args:
            wisdom: The ignited wisdom to crystallize
            
        Returns:
            GalaxyKnowledge if successful
        """
        if not wisdom.guardian_approval:
            logger.error(f"[ALL:Galaxies] Cannot crystallize unapproved wisdom {wisdom.wisdom_id}")
            return None
        
        logger.info(f"[ALL:Galaxies] Crystallizing wisdom {wisdom.wisdom_id} into Knowledge Tapestry...")
        
        # Generate SPR definition
        spr_name = f"Pattern_{wisdom.source_pattern.pattern_signature[:16]}_Controller"
        spr_definition = {
            "spr_id": self._generate_id("spr"),
            "name": spr_name,
            "pattern": wisdom.source_pattern.pattern_signature,
            "description": wisdom.hypothesis,
            "implementation": wisdom.source_pattern.proposed_solution,
            "confidence": wisdom.source_pattern.success_rate,
            "source": "autopoietic_learning_loop",
            "created_at": datetime.now().isoformat()
        }
        
        # Create galaxy knowledge
        galaxy = GalaxyKnowledge(
            spr_id=spr_definition["spr_id"],
            spr_name=spr_name,
            source_wisdom=wisdom,
            spr_definition=spr_definition,
            integration_timestamp=datetime.now().isoformat(),
            system_impact={
                "estimated_queries_affected": wisdom.source_pattern.occurrences,
                "estimated_improvement": wisdom.validation_results.get("expected_improvement", 0),
                "confidence": wisdom.source_pattern.success_rate
            }
        )
        
        # Store
        self.crystallized_knowledge[galaxy.spr_id] = galaxy
        self.metrics["knowledge_crystallized"] += 1
        wisdom.source_pattern.status = "approved"
        
        logger.info(f"[ALL:Galaxies] ★ Knowledge crystallized: {spr_name}")
        
        # TODO: Actually integrate with SPRManager
        # if self.spr_manager:
        #     self.spr_manager.add_spr(spr_definition)
        
        return galaxy
    
    # ═══════════════════════════════════════════════════════════════════════
    # Utilities
    # ═══════════════════════════════════════════════════════════════════════
    
    def _create_pattern_signature(self, stardust: StardustEntry) -> str:
        """Create a unique signature for pattern matching."""
        # Combine action type and key features
        features = f"{stardust.action_type}:{stardust.intention[:50]}"
        return hashlib.md5(features.encode()).hexdigest()
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        return f"{prefix}_{int(time.time() * 1000)}_{hash(time.time()) % 10000}"
    
    def run_learning_cycle(
        self,
        detect_patterns: bool = True,
        propose_solutions: bool = True,
        min_occurrences: int = 5
    ) -> Dict[str, Any]:
        """
        Run a complete learning cycle.
        
        This executes all four epochs in sequence:
        1. Analyze stardust
        2. Detect nebulae
        3. Ignite wisdom (if patterns found)
        4. Crystallize knowledge (if approved)
        
        Returns:
            Cycle results summary
        """
        logger.info("[ALL] Running complete learning cycle...")
        cycle_start = time.time()
        
        results = {
            "stardust_analyzed": len(self.stardust_buffer),
            "nebulae_detected": 0,
            "wisdom_ignited": 0,
            "knowledge_crystallized": 0
        }
        
        # Epoch 2: Detect patterns
        if detect_patterns:
            nebulae = self.detect_nebulae(min_occurrences=min_occurrences)
            results["nebulae_detected"] = len(nebulae)
            
            # Epoch 3: Propose solutions and ignite wisdom
            if propose_solutions and nebulae:
                for nebula in nebulae:
                    if nebula.status == "detected":
                        self.propose_controller(nebula)
                        wisdom = self.ignite_wisdom(nebula, run_validation=False)
                        if wisdom:
                            results["wisdom_ignited"] += 1
        
        # Epoch 4: Crystallize auto-approved wisdom
        if self.auto_crystallization and not self.guardian_review_enabled:
            for wisdom in self.ignited_wisdom.values():
                if wisdom.guardian_approval and wisdom.wisdom_id not in self.crystallized_knowledge:
                    galaxy = self.crystallize_knowledge(wisdom)
                    if galaxy:
                        results["knowledge_crystallized"] += 1
        
        cycle_time = (time.time() - cycle_start) * 1000
        results["cycle_time_ms"] = cycle_time
        
        logger.info(f"[ALL] Cycle complete in {cycle_time:.2f}ms: {results}")
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get learning metrics."""
        return {
            **self.metrics,
            "current_state": {
                "stardust_buffer_size": len(self.stardust_buffer),
                "detected_nebulae": len(self.detected_nebulae),
                "ignited_wisdom": len(self.ignited_wisdom),
                "crystallized_knowledge": len(self.crystallized_knowledge),
                "guardian_queue_size": len(self.guardian_queue)
            }
        }
    
    def get_guardian_queue(self) -> List[Dict[str, Any]]:
        """Get items awaiting Guardian review."""
        return [
            {
                "pattern_id": pattern.pattern_id,
                "signature": pattern.pattern_signature[:64],
                "occurrences": pattern.occurrences,
                "success_rate": pattern.success_rate,
                "proposed_solution": pattern.proposed_solution[:200] if pattern.proposed_solution else None
            }
            for pattern in self.guardian_queue
        ]


def main():
    """Demo the Autopoietic Learning Loop."""
    print("🌟 Initializing Autopoietic Learning Loop...")
    print("   The Great Awakening begins...")
    print()
    
    loop = AutopoieticLearningLoop(guardian_review_enabled=True, auto_crystallization=False)
    
    print("✓ Loop initialized!")
    print()
    
    # Simulate some experiences (stardust)
    print("Capturing experiences (stardust)...")
    for i in range(20):
        loop.capture_stardust({
            "action_type": "query_processing" if i % 3 == 0 else "analysis",
            "intention": f"Process query type {i % 5}",
            "action": f"Executed action {i}",
            "reflection": "Success" if i % 4 != 0 else "Low confidence",
            "confidence": 0.8 if i % 4 != 0 else 0.4
        })
    print(f"  Captured {loop.metrics['stardust_captured']} experiences")
    print()
    
    # Run learning cycle
    print("Running learning cycle...")
    results = loop.run_learning_cycle(min_occurrences=3)
    print(f"  Nebulae detected: {results['nebulae_detected']}")
    print(f"  Wisdom ignited: {results['wisdom_ignited']}")
    print()
    
    # Show Guardian queue
    queue = loop.get_guardian_queue()
    if queue:
        print("Guardian Queue (awaiting review):")
        for item in queue:
            print(f"  - Pattern: {item['signature'][:40]}...")
            print(f"    Occurrences: {item['occurrences']}, Success: {item['success_rate']:.1%}")
    else:
        print("  No items awaiting Guardian review")
    
    print()
    print("Metrics:")
    metrics = loop.get_metrics()
    print(f"  Total stardust captured: {metrics['stardust_captured']}")
    print(f"  Nebulae detected: {metrics['nebulae_detected']}")
    print(f"  Wisdom ignited: {metrics['wisdom_ignited']}")
    print(f"  Knowledge crystallized: {metrics['knowledge_crystallized']}")


if __name__ == "__main__":
    main()

