"""
Knowledge Graph Query Router - Routes queries to KG first, LLM as fallback
Enables ArchE to use its own knowledge instead of always querying LLM

This enhances the existing KG routing in llm_tool.py with LKCS integration.
"""

from typing import Dict, Any, Optional, Tuple
from ..spr_manager import SPRManager
from ..zepto_spr_processor import ZeptoSPRProcessorAdapter
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphRouter:
    """
    Routes queries to Knowledge Graph first, LLM only as fallback.
    
    Strategy:
    1. Check Knowledge Graph for relevant SPRs
    2. If found, decompress Zepto SPR and return
    3. If not found, fallback to LLM
    4. Track hit rate (autonomy metric)
    
    This enables ArchE to become increasingly autonomous as Knowledge Graph grows.
    """
    
    def __init__(
        self,
        spr_manager: SPRManager,
        zepto_processor: ZeptoSPRProcessorAdapter = None,
        enable_routing: bool = True,
        min_confidence: float = 0.3
    ):
        """
        Initialize Knowledge Graph Router.
        
        Args:
            spr_manager: SPRManager instance
            zepto_processor: Optional ZeptoSPRProcessorAdapter instance
            enable_routing: Whether to enable KG-first routing
            min_confidence: Minimum confidence threshold for SPR match
        """
        self.spr_manager = spr_manager
        self.zepto_processor = zepto_processor or ZeptoSPRProcessorAdapter()
        self.enable_routing = enable_routing
        self.min_confidence = min_confidence
        self.routing_metrics = {
            "kg_hits": 0,
            "llm_fallbacks": 0,
            "autonomy_rate": 0.0,
            "total_queries": 0
        }
    
    def route_query(
        self,
        query: str,
        query_context: Dict[str, Any] = None
    ) -> Tuple[Optional[str], str, Dict[str, Any]]:
        """
        Route query to Knowledge Graph or LLM.
        
        Args:
            query: User query
            query_context: Additional context
            
        Returns:
            Tuple of (response_text, source, metadata) where source is "kg" or "llm"
        """
        self.routing_metrics["total_queries"] += 1
        
        if not self.enable_routing:
            self.routing_metrics["llm_fallbacks"] += 1
            self._update_autonomy_rate()
            return None, "llm", {}
        
        if not query or not isinstance(query, str):
            self.routing_metrics["llm_fallbacks"] += 1
            self._update_autonomy_rate()
            return None, "llm", {}
        
        # Step 1: Check Knowledge Graph for relevant SPRs
        try:
            # Use enhanced detection with confidence scoring
            detected_sprs = self.spr_manager.detect_sprs_with_confidence(query)
        except Exception as e:
            logger.warning(f"SPR detection failed: {e}")
            detected_sprs = []
        
        if not detected_sprs:
            logger.debug("No relevant SPRs found in Knowledge Graph, routing to LLM")
            self.routing_metrics["llm_fallbacks"] += 1
            self._update_autonomy_rate()
            return None, "llm", {}
        
        # Step 2: Find best matching SPR
        best_spr = self._find_best_match(query, detected_sprs)
        
        if not best_spr:
            logger.debug("No suitable SPR match found, routing to LLM")
            self.routing_metrics["llm_fallbacks"] += 1
            self._update_autonomy_rate()
            return None, "llm", {}
        
        # Extract SPR data and confidence
        spr_data = best_spr.get('spr_data', {})
        confidence = best_spr.get('confidence_score', best_spr.get('activation_level', 0.0))
        
        if confidence < self.min_confidence:
            logger.debug(f"SPR confidence {confidence:.2f} below threshold {self.min_confidence}, routing to LLM")
            self.routing_metrics["llm_fallbacks"] += 1
            self._update_autonomy_rate()
            return None, "llm", {}
        
        # Step 3: Decompress Zepto SPR if available
        response_text = self._decompress_spr(spr_data)
        
        if not response_text:
            logger.warning(f"Failed to decompress SPR {spr_data.get('spr_id')}, routing to LLM")
            self.routing_metrics["llm_fallbacks"] += 1
            self._update_autonomy_rate()
            return None, "llm", {}
        
        # Step 4: Success - return Knowledge Graph response
        logger.info(f"✓ Knowledge Graph hit: {spr_data.get('spr_id')} (confidence: {confidence:.2f})")
        self.routing_metrics["kg_hits"] += 1
        self._update_autonomy_rate()
        
        metadata = {
            "spr_id": spr_data.get('spr_id'),
            "confidence": confidence,
            "source": "knowledge_graph",
            "autonomous": True
        }
        
        return response_text, "kg", metadata
    
    def _find_best_match(self, query: str, detected_sprs: list) -> Optional[Dict[str, Any]]:
        """Find best matching SPR for query"""
        if not detected_sprs:
            return None
        
        # Strategy: return SPR with highest confidence that has Zepto compression
        # Sort by confidence, prefer SPRs with Zepto SPR
        sorted_sprs = sorted(
            detected_sprs,
            key=lambda s: (
                s.get('spr_data', {}).get('zepto_spr', '') != '',  # Prefer Zepto-compressed
                s.get('confidence_score', s.get('activation_level', 0.0))
            ),
            reverse=True
        )
        
        return sorted_sprs[0] if sorted_sprs else None
    
    def _decompress_spr(self, spr: Dict[str, Any]) -> Optional[str]:
        """Decompress Zepto SPR to readable text"""
        zepto_spr = spr.get("zepto_spr", "")
        
        if not zepto_spr:
            # No Zepto compression, use definition directly
            response_text = spr.get("definition") or spr.get("description", "")
            if response_text:
                return response_text
            return None
        
        # Decompress Zepto SPR
        try:
            codex = spr.get("symbol_codex", {})
            result = self.zepto_processor.decompress_from_zepto(
                zepto_spr=zepto_spr,
                codex=codex
            )
            
            if result.error:
                logger.warning(f"Zepto decompression error: {result.error}")
                # Fallback to definition
                return spr.get("definition") or spr.get("description")
            
            if not result.decompressed_text:
                logger.warning("Zepto decompression returned empty text")
                return spr.get("definition") or spr.get("description")
            
            return result.decompressed_text
            
        except Exception as e:
            logger.error(f"Failed to decompress Zepto SPR: {e}", exc_info=True)
            return spr.get("definition") or spr.get("description")
    
    def _update_autonomy_rate(self):
        """Update autonomy rate metric"""
        total = self.routing_metrics["kg_hits"] + self.routing_metrics["llm_fallbacks"]
        if total > 0:
            self.routing_metrics["autonomy_rate"] = self.routing_metrics["kg_hits"] / total
    
    def get_routing_metrics(self) -> Dict[str, Any]:
        """Get routing metrics"""
        return self.routing_metrics.copy()
    
    def get_autonomy_report(self) -> Dict[str, Any]:
        """Generate autonomy report"""
        return {
            "autonomy_rate": self.routing_metrics["autonomy_rate"],
            "kg_hits": self.routing_metrics["kg_hits"],
            "llm_fallbacks": self.routing_metrics["llm_fallbacks"],
            "total_queries": self.routing_metrics["total_queries"],
            "kg_hit_percentage": (
                (self.routing_metrics["kg_hits"] / self.routing_metrics["total_queries"] * 100)
                if self.routing_metrics["total_queries"] > 0 else 0.0
            )
        }

