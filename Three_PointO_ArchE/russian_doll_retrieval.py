"""
Russian Doll Layer Retrieval Utilities
ResonantiA Protocol v3.5-GP - Adaptive SPR Retrieval

Provides utilities for intelligently selecting appropriate Russian Doll layers
based on context needs, enabling efficient adaptive retrieval.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# Layer hierarchy (innermost to outermost)
LAYER_HIERARCHY = ["Zepto", "Atto", "Femto", "Pico", "Micro", "Nano", "Concise", "Narrative"]

# Layer characteristics for adaptive selection
LAYER_CHARACTERISTICS = {
    "Zepto": {
        "size_range": (1, 15),
        "use_case": "quick_lookup",
        "detail_level": "minimal",
        "speed": "instant",
        "context": "symbol_only"
    },
    "Atto": {
        "size_range": (15, 50),
        "use_case": "key_points",
        "detail_level": "high_compression",
        "speed": "very_fast",
        "context": "symbols_and_keywords"
    },
    "Femto": {
        "size_range": (50, 100),
        "use_case": "key_points",
        "detail_level": "high_compression",
        "speed": "very_fast",
        "context": "symbols_and_keywords"
    },
    "Pico": {
        "size_range": (100, 300),
        "use_case": "balanced_detail",
        "detail_level": "moderate_compression",
        "speed": "fast",
        "context": "relationships"
    },
    "Micro": {
        "size_range": (300, 800),
        "use_case": "balanced_detail",
        "detail_level": "moderate_compression",
        "speed": "fast",
        "context": "relationships"
    },
    "Nano": {
        "size_range": (800, 2000),
        "use_case": "summary",
        "detail_level": "light_compression",
        "speed": "medium",
        "context": "patterns"
    },
    "Concise": {
        "size_range": (2000, 5000),
        "use_case": "summary",
        "detail_level": "light_compression",
        "speed": "medium",
        "context": "patterns"
    },
    "Narrative": {
        "size_range": (5000, 100000),
        "use_case": "full_context",
        "detail_level": "none",
        "speed": "slower",
        "context": "complete"
    }
}


def select_adaptive_layer(
    use_case: str = "balanced_detail",
    max_size: Optional[int] = None,
    min_detail: str = "moderate",
    require_code: bool = False,
    require_specs: bool = False
) -> str:
    """
    Intelligently select appropriate Russian Doll layer based on requirements.
    
    Args:
        use_case: Desired use case ("quick_lookup", "key_points", "balanced_detail", 
                 "summary", "full_context")
        max_size: Maximum content size in characters (None = no limit)
        min_detail: Minimum detail level ("minimal", "high_compression", "moderate", 
                   "light_compression", "none")
        require_code: Whether full code implementation is required
        require_specs: Whether full specifications are required
        
    Returns:
        Recommended layer name
    """
    # If code or specs required, must use Narrative (only layer with full content)
    if require_code or require_specs:
        return "Narrative"
    
    # Map use_case to layer
    use_case_to_layer = {
        "quick_lookup": "Zepto",
        "key_points": "Femto",
        "balanced_detail": "Micro",
        "summary": "Concise",
        "full_context": "Narrative"
    }
    
    # Start with use_case recommendation
    recommended = use_case_to_layer.get(use_case, "Micro")
    
    # Adjust based on max_size
    if max_size:
        for layer in LAYER_HIERARCHY:
            char_range = LAYER_CHARACTERISTICS[layer]["size_range"]
            if char_range[1] <= max_size:
                recommended = layer
                break
    
    # Adjust based on min_detail
    detail_levels = {
        "minimal": ["Zepto"],
        "high_compression": ["Zepto", "Atto", "Femto"],
        "moderate": ["Zepto", "Atto", "Femto", "Pico", "Micro"],
        "light_compression": ["Zepto", "Atto", "Femto", "Pico", "Micro", "Nano", "Concise"],
        "none": LAYER_HIERARCHY
    }
    
    allowed_layers = detail_levels.get(min_detail, LAYER_HIERARCHY)
    if recommended not in allowed_layers:
        # Find highest allowed layer
        for layer in reversed(LAYER_HIERARCHY):
            if layer in allowed_layers:
                recommended = layer
                break
    
    return recommended


def get_layer_info(layer: str) -> Dict[str, Any]:
    """
    Get information about a specific layer.
    
    Args:
        layer: Layer name
        
    Returns:
        Dictionary with layer characteristics
    """
    return LAYER_CHARACTERISTICS.get(layer, {})


def suggest_layers_for_context(
    context_type: str,
    estimated_tokens: Optional[int] = None
) -> List[str]:
    """
    Suggest appropriate layers for a given context type.
    
    Args:
        context_type: Type of context ("prompt_priming", "quick_reference", 
                     "detailed_analysis", "code_generation", "specification_review")
        estimated_tokens: Estimated token budget (None = no limit)
        
    Returns:
        List of recommended layers (most appropriate first)
    """
    suggestions = {
        "prompt_priming": ["Concise", "Nano", "Micro"],
        "quick_reference": ["Zepto", "Atto", "Femto"],
        "detailed_analysis": ["Narrative", "Concise"],
        "code_generation": ["Narrative"],  # Always need full code
        "specification_review": ["Narrative"],  # Always need full specs
        "workflow_execution": ["Micro", "Pico"],  # Balanced detail for execution
        "error_diagnosis": ["Narrative", "Concise"],  # Need full context for debugging
    }
    
    recommended = suggestions.get(context_type, ["Micro"])
    
    # Adjust based on token budget
    if estimated_tokens:
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = estimated_tokens * 4
        
        filtered = []
        for layer in recommended:
            char_range = LAYER_CHARACTERISTICS[layer]["size_range"]
            if char_range[1] <= max_chars:
                filtered.append(layer)
        
        if filtered:
            recommended = filtered
    
    return recommended


def compare_layers(
    spr_id: str,
    spr_manager,
    layers: List[str] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Compare content across multiple layers for a single SPR.
    
    Useful for understanding compression trade-offs.
    
    Args:
        spr_id: SPR ID to compare
        spr_manager: SPRManager instance
        layers: List of layers to compare (None = all layers)
        
    Returns:
        Dictionary mapping layer names to content info
    """
    if layers is None:
        layers = LAYER_HIERARCHY
    
    comparison = {}
    
    for layer in layers:
        content = spr_manager.get_spr_content_at_layer(spr_id, layer)
        if content:
            comparison[layer] = {
                "size": len(content.get("content", "")),
                "compression_ratio": content.get("compression_ratio", 1.0),
                "symbol_count": content.get("symbol_count", 0),
                "source": content.get("source", "unknown")
            }
    
    return comparison


def select_layer_from_query(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Automatically select appropriate Russian Doll layer based on user query.
    
    This is the PRIMARY function ArchE uses to intelligently select layers.
    
    Args:
        query: User query text
        context: Optional context (task_type, token_budget, etc.)
        
    Returns:
        Recommended layer name
    """
    if not query or not isinstance(query, str):
        return "Micro"  # Default balanced layer
    
    query_lower = query.lower().strip()
    
    # Extract context hints
    task_type = context.get("task_type") if context else None
    token_budget = context.get("token_budget") if context else None
    require_code = context.get("require_code", False) if context else False
    require_specs = context.get("require_specs", False) if context else False
    
    # Priority 1: Code/Spec requirements (always Narrative)
    if require_code or require_specs:
        return "Narrative"
    
    # Priority 2: Task type mapping
    if task_type:
        task_layer_map = {
            "code_generation": "Narrative",
            "specification_review": "Narrative",
            "error_diagnosis": "Narrative",
            "quick_reference": "Zepto",
            "workflow_execution": "Micro",
            "prompt_priming": "Concise",
            "detailed_analysis": "Narrative"
        }
        if task_type in task_layer_map:
            return task_layer_map[task_type]
    
    # Priority 3: Query intent detection
    # Code/implementation requests
    code_keywords = ["code", "implementation", "show me the", "how is it implemented", 
                     "source code", "full code", "complete code", "implementation of"]
    if any(keyword in query_lower for keyword in code_keywords):
        return "Narrative"
    
    # Specification requests
    spec_keywords = ["specification", "spec", "full spec", "complete spec", "blueprint"]
    if any(keyword in query_lower for keyword in spec_keywords):
        return "Narrative"
    
    # Quick questions
    quick_keywords = ["what is", "define", "briefly", "quick", "remind me", 
                      "tell me about", "explain briefly"]
    if any(keyword in query_lower for keyword in quick_keywords):
        # Check if it's asking for code (override)
        if not any(c in query_lower for c in ["code", "implementation", "how"]):
            return "Zepto"
    
    # Detailed analysis
    detail_keywords = ["analyze", "detailed", "full context", "complete context", 
                       "everything about", "all about", "deep dive"]
    if any(keyword in query_lower for keyword in detail_keywords):
        return "Narrative"
    
    # Summary requests
    summary_keywords = ["summary", "summarize", "overview", "brief overview"]
    if any(keyword in query_lower for keyword in summary_keywords):
        return "Concise"
    
    # Workflow/usage requests
    usage_keywords = ["use", "workflow", "how to use", "how do i", "usage", "example"]
    if any(keyword in query_lower for keyword in usage_keywords):
        return "Micro"
    
    # Priority 4: Token budget constraints
    if token_budget:
        max_chars = token_budget * 4  # Rough: 1 token ≈ 4 chars
        if max_chars < 50:
            return "Zepto"
        elif max_chars < 300:
            return "Micro"
        elif max_chars < 2000:
            return "Concise"
        else:
            return "Narrative"
    
    # Default: Balanced detail (Micro)
    return "Micro"

