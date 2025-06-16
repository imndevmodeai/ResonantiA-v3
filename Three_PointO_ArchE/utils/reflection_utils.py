from typing import Any, Dict, List, Optional
import time

def _create_reflection(status: str, summary: str, confidence: Optional[float], alignment: Optional[str], issues: Optional[List[str]], preview: Any) -> Dict[str, Any]:
    """Helper to create a standardized IAR reflection dictionary."""
    return {
        "status": status,
        "summary": summary,
        "confidence": confidence if confidence is not None else 0.0, # Ensure confidence is always a float
        "alignment_check": alignment if alignment is not None else "N/A",
        "potential_issues": issues if issues is not None else [],
        "raw_output_preview": str(preview)[:200] if preview is not None else None, # Truncate preview
        "timestamp": time.time() # Add a timestamp for when the reflection was created
    } 