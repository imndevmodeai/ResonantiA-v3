"""
IAR Components - IAR validation and resonance tracking for workflow execution
"""
from typing import Dict, Any, Tuple, List
from datetime import datetime
import numpy as np
from dataclasses import dataclass
from typing import get_origin, get_args

@dataclass
class IARValidationResult:
    """Result of IAR validation."""
    is_valid: bool
    issues: List[str]
    confidence: float
    resonance_score: float

class IAR_Prepper:
    """A helper class to prepare standardized IAR dictionaries."""
    def __init__(self, action_name: str, action_inputs: Dict[str, Any]):
        """
        Initializes the IAR_Prepper.

        Args:
            action_name (str): The name of the action being performed.
            action_inputs (Dict[str, Any]): The inputs provided to the action.
        """
        self.action_name = action_name
        self.action_inputs = action_inputs
        self.start_time = datetime.now()

    def _get_common_fields(self) -> Dict[str, Any]:
        """Returns fields common to all IAR responses."""
        execution_duration = (datetime.now() - self.start_time).total_seconds()
        return {
            "action_name": self.action_name,
            "inputs": self.action_inputs,
            "timestamp": self.start_time.isoformat(),
            "execution_duration": round(execution_duration, 4),
            "alignment_check": {"objective_alignment": 1.0, "protocol_alignment": 1.0}, # Placeholder
        }

    def finish_with_success(
        self, 
        result: Dict[str, Any], 
        confidence: float = 0.9, 
        summary: str = "Action completed successfully."
    ) -> Dict[str, Any]:
        """Formats a successful IAR response."""
        if not (0.5 <= confidence <= 1.0):
            confidence = 0.9
            
        iar = self._get_common_fields()
        iar.update({
            "status": "Success",
            "confidence": confidence,
            "summary": summary,
            "potential_issues": [],
            "result": result,
            "error": None,
            "raw_output_preview": str(result)[:2000] + "..." if len(str(result)) > 2000 else str(result)
        })
        return iar

    def finish_with_error(
        self, 
        error_message: str, 
        confidence: float = 0.1
    ) -> Dict[str, Any]:
        """Formats a failed IAR response."""
        if not (0.0 <= confidence < 0.5):
            confidence = 0.1

        iar = self._get_common_fields()
        iar.update({
            "status": "Failure",
            "confidence": confidence,
            "summary": f"Action failed with error: {error_message}",
            "potential_issues": [error_message],
            "result": None,
            "error": error_message,
            "raw_output_preview": f"Error: {error_message}"
        })
        return iar

    def finish_with_skip(self, reason: str) -> Dict[str, Any]:
        """Formats a skipped IAR response."""
        iar = self._get_common_fields()
        iar.update({
            "status": "Skipped",
            "confidence": 0.5, # Skipped tasks have neutral confidence
            "summary": f"Action skipped: {reason}",
            "potential_issues": [],
            "result": {"status": "Skipped", "reason": reason},
            "error": None,
            "raw_output_preview": f"Skipped: {reason}"
        })
        return iar

class IARValidator:
    """Validates IAR (Integrated Action Reflection) data structure and content."""
    
    def __init__(self):
        self.required_fields = {
            'status': str,
            'confidence': float,
            'summary': str,
            'potential_issues': List[str],
            'alignment_check': Dict[str, Any]
        }
    
    def validate_structure(self, iar_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate the structure of IAR data.
        
        Args:
            iar_data: The IAR data to validate
            
        Returns:
            Tuple of (is_valid, issues)
        """
        issues = []
        
        # Check required fields
        for field, field_type in self.required_fields.items():
            if field not in iar_data:
                issues.append(f"Missing required field: {field}")
            else:
                origin = get_origin(field_type)
                if origin:
                    if not isinstance(iar_data[field], origin):
                        issues.append(f"Invalid type for field {field}: expected {field_type}, got {type(iar_data[field])}")
                elif not isinstance(iar_data[field], field_type):
                    issues.append(f"Invalid type for field {field}: expected {field_type}, got {type(iar_data[field])}")
        
        # Validate confidence range
        if 'confidence' in iar_data:
            confidence = iar_data['confidence']
            if not (0 <= confidence <= 1):
                issues.append(f"Confidence must be between 0 and 1, got {confidence}")
        
        # Validate status values
        if 'status' in iar_data:
            status = iar_data['status']
            valid_statuses = ['Success', 'Failure', 'Warning', 'Skipped']
            if status not in valid_statuses:
                issues.append(f"Invalid status: {status}. Must be one of {valid_statuses}")
        
        return len(issues) == 0, issues
    
    def validate_content(self, iar_data: Dict[str, Any], context: Dict[str, Any]) -> IARValidationResult:
        """
        Validate the content of IAR data in context.
        
        Args:
            iar_data: The IAR data to validate
            context: The execution context
            
        Returns:
            IARValidationResult containing validation details
        """
        is_valid, issues = self.validate_structure(iar_data)
        
        # Calculate confidence score
        confidence = iar_data.get('confidence', 0.0)
        
        # Calculate resonance score
        resonance_score = self._calculate_resonance(iar_data, context)
        
        return IARValidationResult(
            is_valid=is_valid,
            issues=issues,
            confidence=confidence,
            resonance_score=resonance_score
        )
    
    def _calculate_resonance(self, iar_data: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate the resonance score for IAR data."""
        # Base resonance on confidence
        resonance = iar_data.get('confidence', 0.0)
        
        # Adjust for alignment
        alignment = iar_data.get('alignment_check', {})
        if alignment:
            alignment_score = sum(alignment.values()) / len(alignment)
            resonance = (resonance + alignment_score) / 2
        
        # Adjust for issues
        issues = iar_data.get('potential_issues', [])
        if issues:
            issue_penalty = len(issues) * 0.1
            resonance = max(0.0, resonance - issue_penalty)
        
        return resonance

class ResonanceTracker:
    """Tracks resonance across workflow execution."""
    
    def __init__(self):
        self.execution_history = []
        self.resonance_threshold = 0.7
    
    def record_execution(self, task_id: str, iar_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        Record execution with IAR data.
        
        Args:
            task_id: The task identifier
            iar_data: The IAR data
            context: The execution context
        """
        validator = IARValidator()
        validation_result = validator.validate_content(iar_data, context)
        
        self.execution_history.append({
            'task_id': task_id,
            'timestamp': datetime.now().isoformat(),
            'iar_data': iar_data,
            'validation_result': validation_result,
            'context': context
        })
    
    def get_resonance_trend(self, window_size: int = 5) -> List[float]:
        """
        Get the resonance trend over recent executions.
        
        Args:
            window_size: Number of recent executions to consider
            
        Returns:
            List of resonance scores
        """
        if not self.execution_history:
            return []
        
        recent_executions = self.execution_history[-window_size:]
        return [execution['validation_result'].resonance_score for execution in recent_executions]
    
    def detect_resonance_issues(self) -> List[Dict[str, Any]]:
        """
        Detect potential resonance issues in recent executions.
        
        Returns:
            List of issues with details
        """
        issues = []
        
        if not self.execution_history:
            return issues
        
        # Get recent resonance trend
        resonance_trend = self.get_resonance_trend()
        
        # Check for low resonance
        if resonance_trend and min(resonance_trend) < self.resonance_threshold:
            issues.append({
                'type': 'low_resonance',
                'details': f"Resonance below threshold ({self.resonance_threshold})",
                'values': resonance_trend
            })
        
        # Check for resonance degradation
        if len(resonance_trend) >= 2:
            degradation = np.diff(resonance_trend)
            if any(d < 0 for d in degradation):
                issues.append({
                    'type': 'resonance_degradation',
                    'details': "Resonance showing degradation trend",
                    'values': resonance_trend
                })
        
        return issues
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of execution history.
        
        Returns:
            Dictionary containing execution summary
        """
        if not self.execution_history:
            return {
                'total_executions': 0,
                'average_resonance': 0.0,
                'issues_detected': 0
            }
        
        resonance_scores = [execution['validation_result'].resonance_score 
                          for execution in self.execution_history]
        
        return {
            'total_executions': len(self.execution_history),
            'average_resonance': np.mean(resonance_scores),
            'issues_detected': len(self.detect_resonance_issues())
        } 