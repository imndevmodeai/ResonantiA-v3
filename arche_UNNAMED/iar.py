"""
Integrated Action Reflection (IAR) - ResonantiA Protocol v3.5-GP
Every action must return an IAR dictionary for system self-awareness.
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class IARStatus(Enum):
    """Status values for IAR reflection."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    SKIPPED = "skipped"
    ERROR = "error"


class IARAlignment(Enum):
    """Alignment check values."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MISALIGNED = "misaligned"


class IARReflection:
    """
    Integrated Action Reflection - standardized self-assessment returned by every action.
    
    This is the nervous system of ArchE's self-awareness, enabling meta-cognition,
    error detection, and continuous learning through operational feedback.
    """
    
    REQUIRED_FIELDS = ["status", "confidence"]
    OPTIONAL_FIELDS = [
        "alignment_check",
        "potential_issues",
        "tactical_resonance",
        "crystallization_potential",
        "metadata",
        "error",
        "warnings",
        "notes",
        "execution_time_ms",
        "resource_usage",
        "related_sprs",
    ]
    
    @staticmethod
    def create(
        status: Union[str, IARStatus],
        confidence: float,
        alignment_check: Optional[Union[str, IARAlignment]] = None,
        potential_issues: Optional[List[str]] = None,
        tactical_resonance: Optional[float] = None,
        crystallization_potential: Optional[float] = None,
        error: Optional[str] = None,
        warnings: Optional[List[str]] = None,
        notes: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        resource_usage: Optional[Dict[str, Any]] = None,
        related_sprs: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Factory method to create a valid IAR reflection dictionary.
        
        Args:
            status: Action execution status (IARStatus enum or string).
            confidence: Confidence score (0.0 to 1.0).
            alignment_check: Alignment with task goals (IARAlignment or string).
            potential_issues: List of potential issues or concerns.
            tactical_resonance: Resonance with tactical objectives (0.0 to 1.0).
            crystallization_potential: Potential for insight solidification (0.0 to 1.0).
            error: Error message if status indicates failure.
            warnings: List of warning messages.
            notes: Additional notes or observations.
            execution_time_ms: Execution time in milliseconds.
            resource_usage: Dictionary of resource usage metrics.
            related_sprs: List of SPR IDs activated during this action.
            metadata: Additional metadata dictionary.
        
        Returns:
            Validated IAR reflection dictionary.
        """
        # Normalize status
        if isinstance(status, IARStatus):
            status_str = status.value
        else:
            status_str = str(status).lower()
            # Validate string status
            valid_statuses = [s.value for s in IARStatus]
            if status_str not in valid_statuses:
                logger.warning(f"Invalid status '{status_str}', defaulting to 'error'")
                status_str = IARStatus.ERROR.value
        
        # Validate confidence
        if not isinstance(confidence, (int, float)):
            logger.warning(f"Invalid confidence type {type(confidence)}, defaulting to 0.0")
            confidence = 0.0
        confidence = float(max(0.0, min(1.0, confidence)))
        
        # Normalize alignment
        if alignment_check is not None:
            if isinstance(alignment_check, IARAlignment):
                alignment_str = alignment_check.value
            else:
                alignment_str = str(alignment_check).lower()
        else:
            alignment_str = None
        
        # Build IAR dictionary
        iar_dict = {
            "status": status_str,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        # Add optional fields if provided
        if alignment_str is not None:
            iar_dict["alignment_check"] = alignment_str
        
        if potential_issues is not None:
            if isinstance(potential_issues, list):
                iar_dict["potential_issues"] = potential_issues
            else:
                iar_dict["potential_issues"] = [str(potential_issues)]
        
        if tactical_resonance is not None:
            iar_dict["tactical_resonance"] = float(max(0.0, min(1.0, tactical_resonance)))
        
        if crystallization_potential is not None:
            iar_dict["crystallization_potential"] = float(max(0.0, min(1.0, crystallization_potential)))
        
        if error is not None:
            iar_dict["error"] = str(error)
        
        if warnings is not None:
            if isinstance(warnings, list):
                iar_dict["warnings"] = warnings
            else:
                iar_dict["warnings"] = [str(warnings)]
        
        if notes is not None:
            iar_dict["notes"] = str(notes)
        
        if execution_time_ms is not None:
            iar_dict["execution_time_ms"] = float(execution_time_ms)
        
        if resource_usage is not None and isinstance(resource_usage, dict):
            iar_dict["resource_usage"] = resource_usage
        
        if related_sprs is not None:
            if isinstance(related_sprs, list):
                iar_dict["related_sprs"] = [str(spr) for spr in related_sprs]
            else:
                iar_dict["related_sprs"] = [str(related_sprs)]
        
        if metadata is not None and isinstance(metadata, dict):
            iar_dict["metadata"] = metadata
        
        return iar_dict
    
    @staticmethod
    def validate(iar_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate an IAR reflection dictionary.
        
        Args:
            iar_dict: Dictionary to validate.
        
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        if not isinstance(iar_dict, dict):
            return False, "IAR reflection must be a dictionary"
        
        # Check required fields
        for field in IARReflection.REQUIRED_FIELDS:
            if field not in iar_dict:
                return False, f"Missing required IAR field: {field}"
        
        # Validate status
        status = iar_dict.get("status")
        valid_statuses = [s.value for s in IARStatus]
        if status not in valid_statuses:
            return False, f"Invalid status '{status}'. Must be one of {valid_statuses}"
        
        # Validate confidence
        confidence = iar_dict.get("confidence")
        if not isinstance(confidence, (int, float)):
            return False, f"Invalid confidence type {type(confidence)}. Must be numeric."
        confidence_float = float(confidence)
        if not (0.0 <= confidence_float <= 1.0):
            return False, f"Confidence {confidence_float} out of range [0.0, 1.0]"
        
        # Validate optional fields if present
        if "alignment_check" in iar_dict:
            alignment = iar_dict["alignment_check"]
            valid_alignments = [a.value for a in IARAlignment]
            if alignment not in valid_alignments:
                logger.warning(f"Invalid alignment_check '{alignment}', but not blocking validation")
        
        if "potential_issues" in iar_dict:
            if not isinstance(iar_dict["potential_issues"], list):
                return False, "potential_issues must be a list"
        
        if "warnings" in iar_dict:
            if not isinstance(iar_dict["warnings"], list):
                return False, "warnings must be a list"
        
        if "tactical_resonance" in iar_dict:
            tr = iar_dict["tactical_resonance"]
            if not isinstance(tr, (int, float)):
                return False, "tactical_resonance must be numeric"
            if not (0.0 <= float(tr) <= 1.0):
                return False, f"tactical_resonance {tr} out of range [0.0, 1.0]"
        
        if "crystallization_potential" in iar_dict:
            cp = iar_dict["crystallization_potential"]
            if not isinstance(cp, (int, float)):
                return False, "crystallization_potential must be numeric"
            if not (0.0 <= float(cp) <= 1.0):
                return False, f"crystallization_potential {cp} out of range [0.0, 1.0]"
        
        return True, None
    
    @staticmethod
    def extract_confidence(iar_dict: Dict[str, Any]) -> float:
        """Extract confidence score from IAR, defaulting to 0.0 if missing."""
        return float(iar_dict.get("confidence", 0.0))
    
    @staticmethod
    def extract_status(iar_dict: Dict[str, Any]) -> str:
        """Extract status from IAR, defaulting to 'error' if missing."""
        return str(iar_dict.get("status", IARStatus.ERROR.value))
    
    @staticmethod
    def has_error(iar_dict: Dict[str, Any]) -> bool:
        """Check if IAR indicates an error condition."""
        status = IARReflection.extract_status(iar_dict)
        return status in [IARStatus.FAILURE.value, IARStatus.ERROR.value] or "error" in iar_dict
    
    @staticmethod
    def has_low_confidence(iar_dict: Dict[str, Any], threshold: float = 0.5) -> bool:
        """Check if IAR confidence is below threshold."""
        confidence = IARReflection.extract_confidence(iar_dict)
        return confidence < threshold
    
    @staticmethod
    def has_potential_issues(iar_dict: Dict[str, Any]) -> bool:
        """Check if IAR flags potential issues."""
        issues = iar_dict.get("potential_issues", [])
        return bool(issues and len(issues) > 0)


# Convenience factory functions for common IAR patterns
def create_iar(
    status: Union[str, IARStatus],
    confidence: float,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to create IAR reflection."""
    return IARReflection.create(status, confidence, **kwargs)


def validate_iar(iar_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Convenience function to validate IAR reflection."""
    return IARReflection.validate(iar_dict)


def create_success_iar(
    confidence: float = 0.9,
    notes: Optional[str] = None,
    related_sprs: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create IAR for successful action."""
    return IARReflection.create(
        status=IARStatus.SUCCESS,
        confidence=confidence,
        notes=notes,
        related_sprs=related_sprs,
        **kwargs
    )


def create_error_iar(
    error: str,
    confidence: float = 0.1,
    potential_issues: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create IAR for failed action."""
    if potential_issues is None:
        potential_issues = []
    potential_issues.append(error)
    
    return IARReflection.create(
        status=IARStatus.ERROR,
        confidence=confidence,
        error=error,
        potential_issues=potential_issues,
        **kwargs
    )
