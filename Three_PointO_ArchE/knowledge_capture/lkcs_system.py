"""
Lossy Knowledge Capture System (LKCS) - System Initialization and Management
Main entry point for LKCS integration
"""

from typing import Dict, Any, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Lazy initialization pattern
_lkcs_system = None
_lkcs_interceptor = None
_lkcs_router = None

def get_lkcs_system(force_reinit: bool = False) -> Tuple[Optional[Any], Optional[Any]]:
    """
    Get or initialize LKCS system (singleton pattern).
    
    Args:
        force_reinit: Force reinitialization even if already initialized
        
    Returns:
        Tuple of (interceptor, router) or (None, None) if initialization fails
    """
    global _lkcs_system, _lkcs_interceptor, _lkcs_router
    
    if _lkcs_system is not None and not force_reinit:
        return _lkcs_interceptor, _lkcs_router
    
    try:
        from .knowledge_extractor import KnowledgeExtractor
        from .zepto_compressor import PatternZeptoCompressor
        from .kg_integrator import KnowledgeGraphIntegrator
        from .llm_interceptor import LLMResponseInterceptor
        from .kg_router import KnowledgeGraphRouter
        from ..spr_manager import SPRManager
        from ..zepto_spr_processor import ZeptoSPRProcessorAdapter
        
        # Initialize SPR Manager
        spr_file = Path(__file__).parent.parent.parent / "knowledge_graph" / "spr_definitions_tv.json"
        if not spr_file.exists():
            logger.warning(f"SPR file not found at {spr_file}, LKCS disabled")
            return None, None
        
        spr_manager = SPRManager(str(spr_file))
        logger.info(f"LKCS: Initialized SPRManager with {len(spr_manager.sprs)} SPRs")
        
        # Initialize components
        extractor = KnowledgeExtractor(spr_manager=spr_manager)
        zepto_compressor = PatternZeptoCompressor()
        integrator = KnowledgeGraphIntegrator(
            spr_manager=spr_manager,
            zepto_compressor=zepto_compressor
        )
        
        # Initialize interceptor
        interceptor = LLMResponseInterceptor(
            knowledge_extractor=extractor,
            kg_integrator=integrator,
            enable_capture=True,
            confidence_threshold=0.6
        )
        
        # Initialize router
        zepto_processor = ZeptoSPRProcessorAdapter()
        router = KnowledgeGraphRouter(
            spr_manager=spr_manager,
            zepto_processor=zepto_processor,
            enable_routing=True,
            min_confidence=0.3
        )
        
        _lkcs_interceptor = interceptor
        _lkcs_router = router
        _lkcs_system = {
            "interceptor": interceptor,
            "router": router,
            "integrator": integrator,
            "extractor": extractor
        }
        
        logger.info("✓ LKCS system initialized successfully")
        return interceptor, router
        
    except Exception as e:
        logger.error(f"Failed to initialize LKCS system: {e}", exc_info=True)
        return None, None


def intercept_llm_response(
    llm_response: str,
    query_context: Dict[str, Any],
    llm_metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Intercept LLM response and capture knowledge (convenience function).
    
    Args:
        llm_response: The LLM response text
        query_context: Original query and context
        llm_metadata: LLM provider, model, tokens, etc.
        
    Returns:
        Dictionary with interception results
    """
    interceptor, _ = get_lkcs_system()
    
    if not interceptor:
        return {"captured": False, "reason": "lkcs_not_available"}
    
    return interceptor.intercept_llm_response(llm_response, query_context, llm_metadata)


def route_query_to_kg(
    query: str,
    query_context: Dict[str, Any] = None
) -> Tuple[Optional[str], str, Dict[str, Any]]:
    """
    Route query to Knowledge Graph first (convenience function).
    
    Args:
        query: User query
        query_context: Additional context
        
    Returns:
        Tuple of (response_text, source, metadata)
    """
    _, router = get_lkcs_system()
    
    if not router:
        return None, "llm", {}
    
    return router.route_query(query, query_context)


def get_lkcs_metrics() -> Dict[str, Any]:
    """Get LKCS system metrics"""
    interceptor, router = get_lkcs_system()
    
    metrics = {
        "system_available": interceptor is not None and router is not None
    }
    
    if interceptor:
        metrics["interception_stats"] = interceptor.get_interception_stats()
    
    if router:
        metrics["routing_metrics"] = router.get_routing_metrics()
        metrics["autonomy_report"] = router.get_autonomy_report()
    
    if interceptor and hasattr(interceptor, 'integrator'):
        integrator = interceptor.integrator
        if hasattr(integrator, 'get_learning_metrics'):
            metrics["learning_metrics"] = integrator.get_learning_metrics()
            metrics["autonomy_report"] = integrator.get_autonomy_report()
    
    return metrics

