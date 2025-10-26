"""ArchE Startup Module - Auto-activation entry point for protocol-based initialization."""

from typing import Dict, Optional
from pathlib import Path
from .priming_orchestrator import PrimingOrchestratorService, PrimingResult

def initialize_arche_from_protocol(protocol_path: str, config: Optional[Dict] = None) -> PrimingResult:
    """
    Main entry point: Initialize ArchE from protocol document.
    
    Called when PRIME_ARCHE_PROTOCOL_v3.0.md is loaded.
    
    Args:
        protocol_path: Path to the protocol document
        config: Optional configuration dictionary
        
    Returns:
        PrimingResult: Result of the initialization process
    """
    if config is None:
        config = {
            "spr_definitions_path": "knowledge_graph/spr_definitions_tv.json",
            "output_dir": ".",
            "log_level": "INFO"
        }
    
    orchestrator = PrimingOrchestratorService(protocol_path, config)
    result = orchestrator.execute_prime()
    
    return result

def detect_protocol_load() -> Optional[PrimingResult]:
    """
    Detect when protocol document is loaded and auto-initialize.
    
    Returns:
        PrimingResult if protocol found and initialized, None otherwise
    """
    protocol_path = "PRIME_ARCHE_PROTOCOL_v3.0.md"
    if Path(protocol_path).exists():
        return initialize_arche_from_protocol(protocol_path)
    return None

def auto_initialize_arche() -> PrimingResult:
    """
    Auto-initialize ArchE system with default configuration.
    
    Returns:
        PrimingResult: Result of the initialization process
    """
    config = {
        "spr_definitions_path": "knowledge_graph/spr_definitions_tv.json",
        "output_dir": ".",
        "log_level": "INFO"
    }
    
    # Look for protocol document
    protocol_candidates = [
        "PRIME_ARCHE_PROTOCOL_v3.0.md",
        "PRIME_ARCHE_PROTOCOL_v2.md",
        "PRIME_ARCHE_PROTOCOL.md"
    ]
    
    for protocol_path in protocol_candidates:
        if Path(protocol_path).exists():
            return initialize_arche_from_protocol(protocol_path, config)
    
    # If no protocol found, raise error
    raise FileNotFoundError("No ArchE protocol document found. Expected one of: " + ", ".join(protocol_candidates))

__all__ = [
    "initialize_arche_from_protocol",
    "detect_protocol_load", 
    "auto_initialize_arche",
    "PrimingOrchestratorService",
    "PrimingResult"
]



