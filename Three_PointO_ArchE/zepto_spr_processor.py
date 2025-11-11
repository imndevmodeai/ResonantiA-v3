"""
Universal Zepto SPR Processor Abstraction
ResonantiA Protocol v3.5-GP - Universal Abstraction Layer

This module provides a universal abstraction for the Zepto SPR (Sparse Priming Representation)
compression and decompression process, enabling system-wide integration of hyper-dense symbolic
knowledge representation.

The abstraction follows Universal Abstraction principles: Represent → Compare → Learn → Crystallize
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Import Pattern Crystallization Engine
try:
    from .pattern_crystallization_engine import (
        PatternCrystallizationEngine,
        CompressionStage,
        SymbolCodexEntry
    )
    CRYSTALLIZATION_ENGINE_AVAILABLE = True
except ImportError:
    CRYSTALLIZATION_ENGINE_AVAILABLE = False
    PatternCrystallizationEngine = None
    CompressionStage = None
    SymbolCodexEntry = None
    logger.warning("PatternCrystallizationEngine not available. Zepto SPR processing will be limited.")


@dataclass
class ZeptoSPRResult:
    """Result container for Zepto SPR processing operations."""
    zepto_spr: str
    compression_ratio: float
    compression_stages: List[Dict[str, Any]]
    new_codex_entries: Dict[str, Dict[str, Any]]
    original_length: int
    zepto_length: int
    processing_time_sec: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ZeptoSPRDecompressionResult:
    """Result container for Zepto SPR decompression operations."""
    decompressed_text: str
    symbols_found: List[str]
    symbols_expanded: Dict[str, str]
    decompression_accuracy: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class IZeptoSPRProcessor(ABC):
    """
    Universal Abstract Interface for Zepto SPR Processing.
    
    This interface defines the contract for all Zepto SPR processors,
    enabling polymorphic usage throughout the ResonantiA system.
    
    Implements Universal Abstraction: Represent → Compare → Learn → Crystallize
    """
    
    @abstractmethod
    def compress_to_zepto(
        self,
        narrative: str,
        target_stage: str = "Zepto",
        context: Optional[Dict[str, Any]] = None
    ) -> ZeptoSPRResult:
        """
        Compress a narrative to Zepto SPR form.
        
        Args:
            narrative: The verbose narrative to compress
            target_stage: Compression stage target ("Concise", "Nano", "Micro", "Pico", "Femto", "Atto", "Zepto")
            context: Optional context metadata for compression
            
        Returns:
            ZeptoSPRResult containing the compressed SPR and metadata
        """
        pass
    
    @abstractmethod
    def decompress_from_zepto(
        self,
        zepto_spr: str,
        codex: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ZeptoSPRDecompressionResult:
        """
        Decompress a Zepto SPR back to readable narrative.
        
        Args:
            zepto_spr: The Zepto SPR string to decompress
            codex: Optional symbol codex (uses default if None)
            context: Optional context metadata for decompression
            
        Returns:
            ZeptoSPRDecompressionResult containing decompressed text and metadata
        """
        pass
    
    @abstractmethod
    def validate_compression(
        self,
        original: str,
        zepto_spr: str,
        decompressed: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate compression integrity and meaning preservation.
        
        Args:
            original: Original narrative
            zepto_spr: Compressed Zepto SPR
            decompressed: Optional decompressed text (will decompress if None)
            
        Returns:
            Validation metrics dictionary
        """
        pass
    
    @abstractmethod
    def get_codex(self) -> Dict[str, Any]:
        """Retrieve the current Symbol Codex."""
        pass
    
    @abstractmethod
    def update_codex(self, new_entries: Dict[str, Dict[str, Any]]) -> bool:
        """Update the Symbol Codex with new entries."""
        pass


class ZeptoSPRProcessorAdapter(IZeptoSPRProcessor):
    """
    Concrete Implementation of IZeptoSPRProcessor.
    
    Adapts PatternCrystallizationEngine to the universal interface,
    enabling seamless integration throughout the ResonantiA system.
    """
    
    def __init__(
        self,
        symbol_codex_path: str = "knowledge_graph/symbol_codex.json",
        protocol_vocabulary_path: str = "knowledge_graph/protocol_symbol_vocabulary.json"
    ):
        """Initialize the adapter with Pattern Crystallization Engine."""
        if not CRYSTALLIZATION_ENGINE_AVAILABLE:
            raise RuntimeError(
                "PatternCrystallizationEngine not available. "
                "Cannot initialize ZeptoSPRProcessorAdapter."
            )
        
        self.engine = PatternCrystallizationEngine(
            symbol_codex_path=symbol_codex_path,
            protocol_vocabulary_path=protocol_vocabulary_path
        )
        self.codex_path = Path(symbol_codex_path)
        logger.info("ZeptoSPRProcessorAdapter initialized with PatternCrystallizationEngine")
    
    def compress_to_zepto(
        self,
        narrative: str,
        target_stage: str = "Zepto",
        context: Optional[Dict[str, Any]] = None
    ) -> ZeptoSPRResult:
        """Compress narrative to Zepto SPR using PatternCrystallizationEngine."""
        import time
        start_time = time.time()
        
        try:
            if not narrative or not isinstance(narrative, str):
                return ZeptoSPRResult(
                    zepto_spr="",
                    compression_ratio=1.0,
                    compression_stages=[],
                    new_codex_entries={},
                    original_length=0,
                    zepto_length=0,
                    error="Invalid narrative input"
                )
            
            original_length = len(narrative)
            
            # Delegate to PatternCrystallizationEngine
            zepto_spr, new_codex_entries = self.engine.distill_to_spr(
                thought_trail_entry=narrative,
                target_stage=target_stage
            )
            
            zepto_length = len(zepto_spr) if zepto_spr else 0
            compression_ratio = original_length / zepto_length if zepto_length > 0 else 1.0
            
            # Convert compression stages to serializable format
            compression_stages = [
                {
                    "stage_name": stage.stage_name,
                    "compression_ratio": stage.compression_ratio,
                    "symbol_count": stage.symbol_count,
                    "timestamp": stage.timestamp
                }
                for stage in self.engine.compression_history
            ]
            
            # Convert SymbolCodexEntry objects to dicts
            codex_entries_dict = {
                symbol: asdict(entry) if hasattr(entry, '__dict__') else entry
                for symbol, entry in new_codex_entries.items()
            }
            
            processing_time = time.time() - start_time
            
            return ZeptoSPRResult(
                zepto_spr=zepto_spr,
                compression_ratio=compression_ratio,
                compression_stages=compression_stages,
                new_codex_entries=codex_entries_dict,
                original_length=original_length,
                zepto_length=zepto_length,
                processing_time_sec=processing_time,
                metadata=context or {}
            )
            
        except Exception as e:
            logger.error(f"Error compressing to Zepto SPR: {e}", exc_info=True)
            return ZeptoSPRResult(
                zepto_spr="",
                compression_ratio=1.0,
                compression_stages=[],
                new_codex_entries={},
                original_length=len(narrative) if narrative else 0,
                zepto_length=0,
                error=str(e)
            )
    
    def decompress_from_zepto(
        self,
        zepto_spr: str,
        codex: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ZeptoSPRDecompressionResult:
        """Decompress Zepto SPR using PatternCrystallizationEngine."""
        try:
            if not zepto_spr or not isinstance(zepto_spr, str):
                return ZeptoSPRDecompressionResult(
                    decompressed_text="",
                    symbols_found=[],
                    symbols_expanded={},
                    error="Invalid Zepto SPR input"
                )
            
            # Convert codex dict to SymbolCodexEntry objects if needed
            codex_entries = None
            if codex:
                codex_entries = {}
                for symbol, entry_data in codex.items():
                    if isinstance(entry_data, dict):
                        codex_entries[symbol] = SymbolCodexEntry(**entry_data)
                    else:
                        codex_entries[symbol] = entry_data
            
            # Delegate to engine
            decompressed = self.engine.decompress_spr(
                zepto_spr=zepto_spr,
                codex=codex_entries
            )
            
            # Extract symbols found
            symbols_found = self.engine._extract_symbols(zepto_spr)
            
            # Build symbols_expanded mapping
            symbols_expanded = {}
            active_codex = codex_entries if codex_entries else self.engine.codex
            for symbol in symbols_found:
                if symbol in active_codex:
                    entry = active_codex[symbol]
                    if isinstance(entry, SymbolCodexEntry):
                        symbols_expanded[symbol] = entry.meaning
                    elif isinstance(entry, dict):
                        symbols_expanded[symbol] = entry.get('meaning', str(symbol))
            
            return ZeptoSPRDecompressionResult(
                decompressed_text=decompressed,
                symbols_found=symbols_found,
                symbols_expanded=symbols_expanded,
                metadata=context or {}
            )
            
        except Exception as e:
            logger.error(f"Error decompressing Zepto SPR: {e}", exc_info=True)
            return ZeptoSPRDecompressionResult(
                decompressed_text="",
                symbols_found=[],
                symbols_expanded={},
                error=str(e)
            )
    
    def validate_compression(
        self,
        original: str,
        zepto_spr: str,
        decompressed: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate compression integrity."""
        try:
            if decompressed is None:
                decomp_result = self.decompress_from_zepto(zepto_spr)
                decompressed = decomp_result.decompressed_text
            
            # Use engine's validation method
            validation = self.engine.validate_compression(
                original=original,
                zepto_spr=zepto_spr,
                decompressed=decompressed
            )
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating compression: {e}", exc_info=True)
            return {
                "compression_ratio": len(original) / len(zepto_spr) if zepto_spr else 1.0,
                "decompression_accuracy": 0.0,
                "key_concepts_preserved": False,
                "logical_structure_intact": False,
                "error": str(e)
            }
    
    def get_codex(self) -> Dict[str, Any]:
        """Retrieve current Symbol Codex."""
        try:
            return {
                symbol: asdict(entry) if hasattr(entry, '__dict__') else entry
                for symbol, entry in self.engine.codex.items()
            }
        except Exception as e:
            logger.error(f"Error retrieving codex: {e}", exc_info=True)
            return {}
    
    def update_codex(self, new_entries: Dict[str, Dict[str, Any]]) -> bool:
        """Update Symbol Codex with new entries."""
        try:
            for symbol, entry_data in new_entries.items():
                if isinstance(entry_data, dict):
                    entry = SymbolCodexEntry(**entry_data)
                    self.engine.codex[symbol] = entry
                else:
                    self.engine.codex[symbol] = entry_data
            
            self.engine._save_codex()
            return True
            
        except Exception as e:
            logger.error(f"Error updating codex: {e}", exc_info=True)
            return False


class ZeptoSPRRegistry:
    """
    System-wide Registry for Zepto SPR Processors.
    
    Provides singleton access and factory methods for Zepto SPR processing
    throughout the ResonantiA system.
    """
    
    _instance: Optional[IZeptoSPRProcessor] = None
    _default_config: Dict[str, str] = {
        "symbol_codex_path": "knowledge_graph/symbol_codex.json",
        "protocol_vocabulary_path": "knowledge_graph/protocol_symbol_vocabulary.json"
    }
    
    @classmethod
    def get_processor(
        cls,
        config: Optional[Dict[str, str]] = None,
        force_new: bool = False
    ) -> Optional[IZeptoSPRProcessor]:
        """
        Get or create the universal Zepto SPR processor instance.
        
        Args:
            config: Optional configuration override
            force_new: Force creation of new instance
            
        Returns:
            IZeptoSPRProcessor instance or None if unavailable
        """
        if force_new or cls._instance is None:
            try:
                final_config = {**cls._default_config, **(config or {})}
                cls._instance = ZeptoSPRProcessorAdapter(**final_config)
                logger.info("ZeptoSPRRegistry: Created new processor instance")
            except Exception as e:
                logger.error(f"ZeptoSPRRegistry: Failed to create processor: {e}", exc_info=True)
                return None
        
        return cls._instance
    
    @classmethod
    def register_processor(cls, processor: IZeptoSPRProcessor):
        """Register a custom processor implementation."""
        cls._instance = processor
        logger.info("ZeptoSPRRegistry: Registered custom processor")
    
    @classmethod
    def reset(cls):
        """Reset the registry (useful for testing)."""
        cls._instance = None


# Convenience functions for universal access
def get_zepto_processor(config: Optional[Dict[str, str]] = None) -> Optional[IZeptoSPRProcessor]:
    """Get the universal Zepto SPR processor."""
    return ZeptoSPRRegistry.get_processor(config)


def compress_to_zepto(
    narrative: str,
    target_stage: str = "Zepto",
    config: Optional[Dict[str, str]] = None
) -> ZeptoSPRResult:
    """Universal function to compress narrative to Zepto SPR."""
    processor = get_zepto_processor(config)
    if processor:
        return processor.compress_to_zepto(narrative, target_stage)
    return ZeptoSPRResult(
        zepto_spr="",
        compression_ratio=1.0,
        compression_stages=[],
        new_codex_entries={},
        original_length=len(narrative) if narrative else 0,
        zepto_length=0,
        error="Zepto SPR processor not available"
    )


def decompress_from_zepto(
    zepto_spr: str,
    codex: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, str]] = None
) -> ZeptoSPRDecompressionResult:
    """Universal function to decompress Zepto SPR."""
    processor = get_zepto_processor(config)
    if processor:
        return processor.decompress_from_zepto(zepto_spr, codex)
    return ZeptoSPRDecompressionResult(
        decompressed_text="",
        symbols_found=[],
        symbols_expanded={},
        error="Zepto SPR processor not available"
    )


__all__ = [
    'IZeptoSPRProcessor',
    'ZeptoSPRProcessorAdapter',
    'ZeptoSPRRegistry',
    'ZeptoSPRResult',
    'ZeptoSPRDecompressionResult',
    'get_zepto_processor',
    'compress_to_zepto',
    'decompress_from_zepto'
]
