"""
LLM Response Interceptor - Intercepts LLM responses and triggers knowledge capture
Integrates with existing llm_tool.py and generate_text_llm
"""

from typing import Dict, Any, Optional
from .knowledge_extractor import KnowledgeExtractor, ExtractedPattern
from .kg_integrator import KnowledgeGraphIntegrator
import logging

logger = logging.getLogger(__name__)


class LLMResponseInterceptor:
    """
    Intercepts LLM responses and triggers knowledge capture.
    
    Strategy:
    1. Wrap generate_text_llm() calls (or intercept at provider level)
    2. After LLM response, extract patterns
    3. Compress and store in Knowledge Graph
    4. Track learning progress
    
    This enables ArchE to learn from every LLM interaction.
    """
    
    def __init__(
        self,
        knowledge_extractor: KnowledgeExtractor,
        kg_integrator: KnowledgeGraphIntegrator,
        enable_capture: bool = True,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize LLM Response Interceptor.
        
        Args:
            knowledge_extractor: KnowledgeExtractor instance
            kg_integrator: KnowledgeGraphIntegrator instance
            enable_capture: Whether to enable knowledge capture
            confidence_threshold: Minimum confidence to store patterns
        """
        self.extractor = knowledge_extractor
        self.integrator = kg_integrator
        self.enable_capture = enable_capture
        self.confidence_threshold = confidence_threshold
        self.interception_history = []
    
    def intercept_llm_response(
        self,
        llm_response: str,
        query_context: Dict[str, Any],
        llm_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Intercept LLM response and capture knowledge.
        
        Args:
            llm_response: The LLM response text
            query_context: Original query and context
            llm_metadata: LLM provider, model, tokens, etc.
            
        Returns:
            Dictionary with interception results and captured knowledge
        """
        if not self.enable_capture:
            return {"captured": False, "reason": "capture_disabled"}
        
        if not llm_response or not isinstance(llm_response, str):
            return {"captured": False, "reason": "invalid_response"}
        
        # Extract pattern
        try:
            pattern: Optional[ExtractedPattern] = self.extractor.extract_from_llm_response(
                llm_response=llm_response,
                query_context=query_context,
                llm_metadata=llm_metadata
            )
        except Exception as e:
            logger.error(f"Pattern extraction failed: {e}", exc_info=True)
            return {"captured": False, "reason": "extraction_failed", "error": str(e)}
        
        if not pattern:
            return {"captured": False, "reason": "no_extractable_pattern"}
        
        # Check confidence threshold
        if pattern.confidence < self.confidence_threshold:
            logger.debug(f"Pattern confidence {pattern.confidence:.2f} below threshold {self.confidence_threshold}")
            return {
                "captured": False,
                "reason": "low_confidence",
                "confidence": pattern.confidence
            }
        
        # Integrate into Knowledge Graph
        try:
            spr_definition = self.integrator.integrate_pattern(pattern, llm_metadata)
        except Exception as e:
            logger.error(f"Pattern integration failed: {e}", exc_info=True)
            return {"captured": False, "reason": "integration_failed", "error": str(e)}
        
        if not spr_definition:
            return {"captured": False, "reason": "integration_failed"}
        
        # Track interception
        self.interception_history.append({
            "pattern_id": pattern.pattern_id,
            "spr_id": spr_definition.get("spr_id"),
            "confidence": pattern.confidence,
            "compression_ratio": spr_definition.get("compression_ratio", 0),
            "timestamp": llm_metadata.get("timestamp") if llm_metadata else None
        })
        
        logger.info(f"✓ Captured knowledge: {pattern.pattern_id} → {spr_definition.get('spr_id')}")
        
        return {
            "captured": True,
            "pattern_id": pattern.pattern_id,
            "spr_id": spr_definition.get("spr_id"),
            "confidence": pattern.confidence,
            "compression_ratio": spr_definition.get("compression_ratio", 0)
        }
    
    def get_interception_stats(self) -> Dict[str, Any]:
        """Get interception statistics"""
        total = len(self.interception_history)
        captured = sum(1 for entry in self.interception_history if entry.get("spr_id"))
        
        return {
            "total_interceptions": total,
            "successfully_captured": captured,
            "capture_rate": captured / total if total > 0 else 0.0,
            "average_confidence": (
                sum(e.get("confidence", 0) for e in self.interception_history) / total
                if total > 0 else 0.0
            ),
            "average_compression_ratio": (
                sum(e.get("compression_ratio", 0) for e in self.interception_history) / total
                if total > 0 else 0.0
            )
        }

