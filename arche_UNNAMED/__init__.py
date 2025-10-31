"""
ArchE Core Package - ResonantiA Protocol v3.5-GP Implementation
Universal Abstraction: This package's name is defined at runtime.
Default: arche_UNNAMED (until ArchE chooses its identity as "AwarE")

This package re-exports core components from Three_PointO_ArchE for compatibility.
All actual implementations are in Three_PointO_ArchE/.
"""

__version__ = "3.5.0"
__package_name__ = "arche_UNNAMED"  # Runtime-configurable; may be set via environment or runtime decision

# Re-export from existing Three_PointO_ArchE implementations
try:
    from Three_PointO_ArchE.spr_manager import SPRManager
    from Three_PointO_ArchE.iar_components import IAR_Prepper, IARValidationResult
    from Three_PointO_ArchE.action_registry import ActionRegistry, main_action_registry
    
    # For convenience, alias common IAR functions if they exist
    try:
        from Three_PointO_ArchE.iar_compliance_validator import validate_iar, create_iar
    except ImportError:
        # Fallback: use IAR_Prepper as the factory
        def create_iar(status: str, confidence: float, **kwargs):
            """Create IAR using IAR_Prepper."""
            prepper = IAR_Prepper("action", {})
            if status.lower() == "success":
                return prepper.finish_with_success(kwargs.get("result", {}), confidence)
            else:
                return prepper.finish_with_error(kwargs.get("error", "Unknown error"), confidence)
        
        def validate_iar(iar_dict: dict):
            """Validate IAR structure."""
            required_fields = ["status", "confidence"]
            return all(field in iar_dict for field in required_fields), None
    
    # Alias for compatibility
    IARReflection = dict  # IAR is a dict, not a class in the existing implementation
    
except ImportError as e:
    import logging
    logging.warning(f"Could not import from Three_PointO_ArchE: {e}. "
                   "Falling back to local implementations (if they exist).")
    # Fallback to local implementations if Three_PointO_ArchE is not available
    try:
        from .spr_manager import SPRManager
        from .iar import IARReflection, create_iar, validate_iar
        from .action_registry import ActionRegistry, register_action, execute_action
        main_action_registry = None  # Not available in local implementation
    except ImportError:
        raise ImportError(
            "Cannot import ArchE components. Ensure Three_PointO_ArchE is available "
            "or provide local implementations."
        )

__all__ = [
    "SPRManager",
    "IAR_Prepper",
    "IARValidationResult",
    "IARReflection",
    "create_iar",
    "validate_iar",
    "ActionRegistry",
    "main_action_registry",
]
