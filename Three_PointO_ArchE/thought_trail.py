from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class TriggerType(Enum):
    """Types of triggers that can activate Thought traiL analysis."""
    DISSONANCE = "dissonance"  # When IAR indicates potential issues
    LOW_CONFIDENCE = "low_confidence"  # When confidence falls below threshold
    PATTERN_DETECTED = "pattern_detected"  # When specific patterns are detected
    METACOGNITIVE_SHIFT = "metacognitive_shift"  # When Metacognitive shifT is triggered
    SIRC_ACTIVATION = "sirc_activation"  # When SIRC is activated
    INSIGHT_SOLIDIFICATION = "insight_solidification"  # When Insight solidificatioN occurs

class ThoughtTrail:
    """
    Manages the IAR-enriched processing history (ThoughtTraiL) for ArchE.
    Each entry in the trail contains the full context of a processing step,
    including inputs, outputs, and the IAR reflection dictionary.
    """
    
    def __init__(self, max_history: int = 1000):
        self.trail: List[Dict[str, Any]] = []
        self.max_history = max_history
        self.current_context: Dict[str, Any] = {}
        self.triggers: Dict[TriggerType, List[Callable]] = {
            trigger_type: [] for trigger_type in TriggerType
        }
        self.confidence_threshold = 0.7
        self.pattern_detectors: List[Callable[[Dict[str, Any]], bool]] = []
    
    def add_entry(self, 
                 task_id: str,
                 action_type: str,
                 inputs: Dict[str, Any],
                 outputs: Dict[str, Any],
                 iar_reflection: Dict[str, Any],
                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a new entry to the ThoughtTraiL with full IAR data.
        Automatically checks for triggers and executes associated handlers.
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'task_id': task_id,
            'action_type': action_type,
            'inputs': inputs,
            'outputs': outputs,
            'iar_reflection': iar_reflection,
            'context': context or self.current_context
        }
        
        self.trail.append(entry)
        self._trim_history()
        
        # Check for triggers
        self._check_triggers(entry)
        
        return entry
    
    def register_trigger_handler(self, 
                               trigger_type: TriggerType, 
                               handler: Callable[[Dict[str, Any]], None]) -> None:
        """Register a handler function for a specific trigger type."""
        if trigger_type not in self.triggers:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
        self.triggers[trigger_type].append(handler)
        logger.info(f"Registered handler for trigger type: {trigger_type}")
    
    def register_pattern_detector(self, detector: Callable[[Dict[str, Any]], bool]) -> None:
        """Register a pattern detector function."""
        self.pattern_detectors.append(detector)
        logger.info("Registered new pattern detector")
    
    def _check_triggers(self, entry: Dict[str, Any]) -> None:
        """Check for triggers and execute associated handlers."""
        iar = entry['iar_reflection']
        
        # Check for dissonance
        if iar.get('potential_issues'):
            self._execute_trigger_handlers(TriggerType.DISSONANCE, entry)
        
        # Check for low confidence
        if iar.get('confidence', 1.0) < self.confidence_threshold:
            self._execute_trigger_handlers(TriggerType.LOW_CONFIDENCE, entry)
        
        # Check for patterns
        for detector in self.pattern_detectors:
            if detector(entry):
                self._execute_trigger_handlers(TriggerType.PATTERN_DETECTED, entry)
                break
        
        # Check for specific action types that trigger analysis
        if entry['action_type'] == 'metacognitive_shift':
            self._execute_trigger_handlers(TriggerType.METACOGNITIVE_SHIFT, entry)
        elif entry['action_type'] == 'sirc_activation':
            self._execute_trigger_handlers(TriggerType.SIRC_ACTIVATION, entry)
        elif entry['action_type'] == 'insight_solidification':
            self._execute_trigger_handlers(TriggerType.INSIGHT_SOLIDIFICATION, entry)
    
    def _execute_trigger_handlers(self, trigger_type: TriggerType, entry: Dict[str, Any]) -> None:
        """Execute all handlers registered for a trigger type."""
        for handler in self.triggers[trigger_type]:
            try:
                handler(entry)
            except Exception as e:
                logger.error(f"Error executing trigger handler for {trigger_type}: {str(e)}")
    
    def get_recent_entries(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent entries from the trail."""
        return self.trail[-count:]
    
    def get_entries_by_task_id(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all entries associated with a specific task ID."""
        return [entry for entry in self.trail if entry['task_id'] == task_id]
    
    def get_entries_with_dissonance(self) -> List[Dict[str, Any]]:
        """Get entries where IAR indicates potential issues or low confidence."""
        return [
            entry for entry in self.trail
            if (entry['iar_reflection'].get('confidence', 1.0) < self.confidence_threshold or
                entry['iar_reflection'].get('potential_issues'))
        ]
    
    def get_context_surrounding_dissonance(self, 
                                         dissonance_entry: Dict[str, Any],
                                         context_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Get the trail entries surrounding a dissonance event.
        Includes entries before and after the dissonance for context.
        """
        try:
            index = self.trail.index(dissonance_entry)
            start = max(0, index - context_depth)
            end = min(len(self.trail), index + context_depth + 1)
            return self.trail[start:end]
        except ValueError:
            return []
    
    def export_trail(self, filepath: str) -> None:
        """Export the complete trail to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.trail, f, indent=2)
    
    def import_trail(self, filepath: str) -> None:
        """Import a trail from a JSON file."""
        with open(filepath, 'r') as f:
            self.trail = json.load(f)
    
    def _trim_history(self) -> None:
        """Maintain the trail within the maximum history limit."""
        if len(self.trail) > self.max_history:
            self.trail = self.trail[-self.max_history:]
    
    def update_current_context(self, context: Dict[str, Any]) -> None:
        """Update the current context for new trail entries."""
        self.current_context.update(context) 