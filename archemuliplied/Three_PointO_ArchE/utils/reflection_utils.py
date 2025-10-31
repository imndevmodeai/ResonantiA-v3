from typing import Any, Dict, List, Optional
import time
from enum import Enum

class ExecutionStatus(str, Enum):
    """Enumeration for the status of an action's execution."""
    SUCCESS = "Success"
    FAILURE = "Failure"
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    WARNING = "Warning"
    CRITICAL_FAILURE = "Critical Failure"

def create_reflection(
    action_name: str,
    status: ExecutionStatus,
    message: str,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    confidence: Optional[float] = None,
    alignment_check: Optional[Dict[str, str]] = None,
    potential_issues: Optional[List[str]] = None,
    execution_time: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Creates a standardized Integrated Action Reflection (IAR) dictionary.

    This utility ensures all reflections across the ArchE system are consistent
    with the ResonantiA Protocol v3.1-CA.

    Args:
        action_name: The name of the action being reflected upon.
        status: The execution status of the action.
        message: A human-readable summary of the action's outcome.
        inputs: A dictionary of the inputs provided to the action.
        outputs: A dictionary of the primary outputs from the action.
        confidence: A float (0.0-1.0) representing confidence in the result.
        alignment_check: A dictionary checking alignment with principles.
        potential_issues: A list of any identified potential issues or warnings.
        execution_time: The duration of the action's execution in seconds.

    Returns:
        A dictionary representing the IAR reflection.
    """
    reflection = {
        "action_name": action_name,
        "timestamp_utc": time.time(),
        "status": status.value,
        "confidence": confidence if confidence is not None else 0.0,
        "summary_message": message,
        "inputs_preview": {k: str(v)[:100] + '...' if len(str(v)) > 100 else str(v) for k, v in (inputs or {}).items()},
        "outputs_preview": {k: str(v)[:100] + '...' if len(str(v)) > 100 else str(v) for k, v in (outputs or {}).items()},
        "alignment_check": alignment_check or {"resonatia_protocol": "Alignment not assessed."},
        "potential_issues": potential_issues or [],
        "execution_time_seconds": execution_time
    }
    return reflection 