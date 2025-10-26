from typing import Dict, Any

def create_iar(confidence: float, tactical_resonance: float, potential_issues: list = None, metadata: dict = None) -> Dict[str, Any]:
    """Creates a standardized Intelligent Agent Report (IAR)."""
    return {
        "confidence": confidence,
        "tactical_resonance": tactical_resonance,
        "potential_issues": potential_issues if potential_issues is not None else [],
        "metadata": metadata if metadata is not None else {},
    }
