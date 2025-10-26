from typing import Dict, Any

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