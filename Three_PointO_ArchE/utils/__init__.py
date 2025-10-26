from typing import Dict, Any

def create_iar(confidence: float = 0.5, tactical_resonance: float = 0.5, potential_issues: list = None, metadata: dict = None, **kwargs) -> Dict[str, Any]:
    """
    Creates a standardized IAR (Integrated Action Reflection) object.
    Accepts additional keyword arguments for flexibility.
    """
    return {
        "status": kwargs.get('status', 'Success'),
        "summary": kwargs.get('summary', 'Action completed successfully'),
        "confidence": kwargs.get('confidence', confidence),
        "alignment_check": {"objective_alignment": 1.0, "protocol_alignment": 1.0},
        "potential_issues": kwargs.get('potential_issues', potential_issues if potential_issues is not None else []),
        "raw_output_preview": kwargs.get('raw_output_preview', f"{{'confidence': {kwargs.get('confidence', confidence)}, 'tactical_resonance': {kwargs.get('tactical_resonance', tactical_resonance)}}}")
    }

def _create_reflection(
    status: str,
    summary: str,
    confidence: float = 0.0,
    alignment_check: str = "Not checked",
    potential_issues: str = "None",
    raw_output_preview: str = ""
) -> Dict[str, Any]:
    """
    Creates a standardized reflection object for IAR compliance.
    """
    return {
        "status": status,
        "summary": summary,
        "confidence": confidence,
        "alignment_check": alignment_check,
        "potential_issues": potential_issues,
        "raw_output_preview": raw_output_preview[:500]  # Truncate for brevity
    }

__all__ = ['create_iar', '_create_reflection']
