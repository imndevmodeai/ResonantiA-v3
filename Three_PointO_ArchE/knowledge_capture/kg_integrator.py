"""
Knowledge Graph Integrator - Stores compressed patterns in Knowledge Graph
Integrates with SPRManager and KnowledgeGraphManager
"""

from typing import Dict, Any, Optional, List
from .knowledge_extractor import ExtractedPattern
from .zepto_compressor import PatternZeptoCompressor
from ..spr_manager import SPRManager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Optional import for KnowledgeGraphManager
try:
    from ..knowledge_graph_manager import KnowledgeGraphManager
    KG_MANAGER_AVAILABLE = True
except ImportError:
    KG_MANAGER_AVAILABLE = False
    KnowledgeGraphManager = None
    logger.debug("KnowledgeGraphManager not available, relationship updates will be skipped")


class KnowledgeGraphIntegrator:
    """
    Integrates extracted and compressed patterns into Knowledge Graph.
    
    Strategy:
    1. Take ExtractedPattern + Zepto compression
    2. Create SPR definition
    3. Add to SPRManager
    4. Update Knowledge Graph relationships (if available)
    5. Track learning metrics
    
    This is the final stage where captured knowledge becomes permanent.
    """
    
    def __init__(
        self,
        spr_manager: SPRManager,
        kg_manager: Optional[Any] = None,
        zepto_compressor: PatternZeptoCompressor = None
    ):
        """
        Initialize Knowledge Graph Integrator.
        
        Args:
            spr_manager: SPRManager instance for storing SPRs
            kg_manager: Optional KnowledgeGraphManager for relationship updates
            zepto_compressor: Optional PatternZeptoCompressor instance
        """
        self.spr_manager = spr_manager
        self.kg_manager = kg_manager if KG_MANAGER_AVAILABLE and kg_manager else None
        self.zepto_compressor = zepto_compressor or PatternZeptoCompressor()
        self.integration_history = []
        self.learning_metrics = {
            "patterns_extracted": 0,
            "patterns_stored": 0,
            "llm_calls_saved": 0,
            "knowledge_growth_rate": 0.0,
            "average_compression_ratio": 0.0,
            "average_confidence": 0.0
        }
    
    def integrate_pattern(
        self,
        pattern: ExtractedPattern,
        llm_metadata: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Integrate extracted pattern into Knowledge Graph.
        
        Args:
            pattern: ExtractedPattern to integrate
            llm_metadata: Metadata about the LLM call that generated this pattern
            
        Returns:
            SPR definition if successful, None otherwise
        """
        # Step 1: Compress to Zepto
        compression_data = self.zepto_compressor.compress_pattern(pattern)
        
        if "error" in compression_data:
            logger.error(f"Failed to compress pattern {pattern.pattern_id}: {compression_data.get('error')}")
            return None
        
        # Step 2: Create SPR definition
        spr_definition = self._create_spr_definition(pattern, compression_data, llm_metadata)
        
        # Step 3: Add to SPRManager
        try:
            success = self.spr_manager.add_spr(spr_definition, save_to_file=True)
            if not success:
                logger.error(f"Failed to add SPR {spr_definition['spr_id']} to SPRManager")
                return None
            
            logger.info(f"Added SPR to Knowledge Graph: {spr_definition['spr_id']}")
        except Exception as e:
            logger.error(f"Exception adding SPR to SPRManager: {e}", exc_info=True)
            return None
        
        # Step 4: Update Knowledge Graph relationships (if KG manager available)
        if self.kg_manager:
            self._update_kg_relationships(spr_definition, pattern.relationships)
        
        # Step 5: Update metrics
        self.learning_metrics["patterns_extracted"] += 1
        self.learning_metrics["patterns_stored"] += 1
        
        # Update running averages
        compression_ratio = compression_data.get("compression_ratio", 0)
        total_stored = self.learning_metrics["patterns_stored"]
        current_avg_ratio = self.learning_metrics["average_compression_ratio"]
        self.learning_metrics["average_compression_ratio"] = (
            (current_avg_ratio * (total_stored - 1) + compression_ratio) / total_stored
        )
        
        current_avg_conf = self.learning_metrics["average_confidence"]
        self.learning_metrics["average_confidence"] = (
            (current_avg_conf * (total_stored - 1) + pattern.confidence) / total_stored
        )
        
        self.integration_history.append({
            "spr_id": spr_definition["spr_id"],
            "pattern_id": pattern.pattern_id,
            "timestamp": datetime.now().isoformat(),
            "compression_ratio": compression_ratio,
            "confidence": pattern.confidence
        })
        
        return spr_definition
    
    def _create_spr_definition(
        self,
        pattern: ExtractedPattern,
        compression_data: Dict[str, Any],
        llm_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create SPR definition from pattern and compression data"""
        spr_id = pattern.pattern_id
        
        spr_definition = {
            "spr_id": spr_id,
            "term": pattern.pattern_id.replace("_", " ").title(),
            "definition": pattern.core_principle,
            "description": f"Extracted from LLM response: {pattern.context}",
            "category": "LearnedPattern",
            "zepto_spr": compression_data.get("zepto_spr", ""),
            "symbol_codex": compression_data.get("symbol_codex", {}),
            "compression_stages": compression_data.get("compression_stages", []),
            "compression_ratio": compression_data.get("compression_ratio", 0),
            "confidence": pattern.confidence,
            "relationships": {
                "type": "LearnedPattern",
                "related_to": pattern.relationships,
                "source": "llm_knowledge_capture"
            },
            "blueprint_details": pattern.implementation_hints or "",
            "example_application": pattern.context,
            "source": "llm_knowledge_capture",
            "llm_metadata": llm_metadata or {},
            "created_at": datetime.now().isoformat(),
            "noise_removed": pattern.noise_removed  # For transparency
        }
        
        return spr_definition
    
    def _update_kg_relationships(self, spr_definition: Dict[str, Any], relationships: List[str]):
        """Update Knowledge Graph with new relationships"""
        if not self.kg_manager:
            return
        
        spr_id = spr_definition["spr_id"]
        
        # Add relationships to existing SPRs
        for related_spr_id in relationships:
            try:
                self.kg_manager.add_relationship(
                    source_node=spr_id,
                    target_node=related_spr_id,
                    relationship_type="learned_from",
                    metadata={"source": "llm_knowledge_capture"}
                )
            except Exception as e:
                logger.warning(f"Failed to add relationship {spr_id} -> {related_spr_id}: {e}")
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get current learning metrics"""
        return self.learning_metrics.copy()
    
    def get_autonomy_report(self) -> Dict[str, Any]:
        """Generate autonomy report"""
        return {
            "patterns_stored": self.learning_metrics["patterns_stored"],
            "average_compression_ratio": self.learning_metrics["average_compression_ratio"],
            "average_confidence": self.learning_metrics["average_confidence"],
            "knowledge_growth_rate": self.learning_metrics["knowledge_growth_rate"],
            "total_integrations": len(self.integration_history)
        }

