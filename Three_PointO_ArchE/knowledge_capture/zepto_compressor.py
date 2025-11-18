"""
Zepto SPR Compressor - Compresses extracted patterns to Zepto format
Integrates with existing ZeptoSPRProcessor and PatternCrystallizationEngine
"""

from typing import Dict, Any, Optional
from .knowledge_extractor import ExtractedPattern
from ..zepto_spr_processor import ZeptoSPRProcessorAdapter, ZeptoSPRResult
import logging

logger = logging.getLogger(__name__)

class PatternZeptoCompressor:
    """
    Compresses extracted patterns to Zepto SPR format.
    
    Strategy:
    1. Take ExtractedPattern (already signal-filtered)
    2. Compress to Zepto SPR using ZeptoSPRProcessorAdapter
    3. Generate symbol codex for decompression
    4. Return compressed form + metadata
    
    This leverages the existing Zepto compression infrastructure
    to achieve 100:1 to 1000:1 compression ratios.
    """
    
    def __init__(self, zepto_processor: ZeptoSPRProcessorAdapter = None):
        """
        Initialize Pattern Zepto Compressor.
        
        Args:
            zepto_processor: Optional ZeptoSPRProcessorAdapter instance
        """
        self.zepto_processor = zepto_processor or ZeptoSPRProcessorAdapter()
        self.compression_history = []
    
    def compress_pattern(self, pattern: ExtractedPattern) -> Dict[str, Any]:
        """
        Compress extracted pattern to Zepto SPR.
        
        Args:
            pattern: ExtractedPattern to compress
            
        Returns:
            Dictionary with zepto_spr, codex, compression_ratio, etc.
        """
        # Build narrative from pattern
        narrative = self._build_narrative(pattern)
        
        if not narrative or len(narrative.strip()) < 10:
            logger.warning(f"Pattern {pattern.pattern_id} has insufficient narrative for compression")
            return {"error": "insufficient_narrative"}
        
        # Compress to Zepto
        try:
            result: ZeptoSPRResult = self.zepto_processor.compress_to_zepto(
                narrative=narrative,
                target_stage="Zepto",
                context={
                    "pattern_id": pattern.pattern_id,
                    "confidence": pattern.confidence,
                    "relationships": pattern.relationships
                }
            )
            
            if result.error:
                logger.error(f"Zepto compression failed: {result.error}")
                return {"error": result.error}
            
            compression_data = {
                "zepto_spr": result.zepto_spr,
                "symbol_codex": result.new_codex_entries,
                "compression_ratio": result.compression_ratio,
                "compression_stages": result.compression_stages,
                "original_length": result.original_length,
                "zepto_length": result.zepto_length,
                "pattern_id": pattern.pattern_id,
                "processing_time_sec": result.processing_time_sec
            }
            
            self.compression_history.append(compression_data)
            logger.info(f"Compressed pattern {pattern.pattern_id}: {result.compression_ratio:.1f}:1")
            
            return compression_data
            
        except Exception as e:
            logger.error(f"Exception during Zepto compression: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _build_narrative(self, pattern: ExtractedPattern) -> str:
        """Build narrative text from extracted pattern for compression"""
        narrative_parts = [
            f"Pattern: {pattern.core_principle}",
        ]
        
        if pattern.context:
            narrative_parts.append(f"Context: {pattern.context}")
        
        if pattern.implementation_hints:
            narrative_parts.append(f"Implementation: {pattern.implementation_hints}")
        
        if pattern.relationships:
            narrative_parts.append(f"Related to: {', '.join(pattern.relationships)}")
        
        return "\n".join(narrative_parts)

