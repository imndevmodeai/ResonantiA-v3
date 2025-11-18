"""
Lossy Knowledge Capture System (LKCS)
ResonantiA Protocol v3.5-GP - Autonomous Learning Enhancement

This module implements the Lossy Knowledge Capture System that enables ArchE to:
1. Learn from LLM responses (the teacher)
2. Extract core patterns (signal vs noise)
3. Compress to Zepto SPRs (lossy but optimized)
4. Store in Knowledge Graph (permanent knowledge base)
5. Gradually reduce LLM dependency (become autonomous)

Components:
- KnowledgeExtractor: Extracts core patterns from LLM responses
- PatternZeptoCompressor: Compresses patterns to Zepto SPR format
- KnowledgeGraphIntegrator: Stores patterns in Knowledge Graph
- LLMResponseInterceptor: Intercepts LLM responses for capture
- KnowledgeGraphRouter: Routes queries to KG first, LLM as fallback
"""

from .knowledge_extractor import KnowledgeExtractor, ExtractedPattern
from .zepto_compressor import PatternZeptoCompressor
from .kg_integrator import KnowledgeGraphIntegrator
from .llm_interceptor import LLMResponseInterceptor
from .kg_router import KnowledgeGraphRouter

__all__ = [
    'KnowledgeExtractor',
    'ExtractedPattern',
    'PatternZeptoCompressor',
    'KnowledgeGraphIntegrator',
    'LLMResponseInterceptor',
    'KnowledgeGraphRouter'
]

