from datetime import datetime
from typing import Dict, List, Any, Optional
import json

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
    
    def add_entry(self, 
                 task_id: str,
                 action_type: str,
                 inputs: Dict[str, Any],
                 outputs: Dict[str, Any],
                 iar_reflection: Dict[str, Any],
                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a new entry to the ThoughtTraiL with full IAR data.
        
        Args:
            task_id: Unique identifier for the task
            action_type: Type of action performed
            inputs: Input parameters for the action
            outputs: Results from the action
            iar_reflection: IAR reflection dictionary
            context: Additional context data
            
        Returns:
            The complete trail entry
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
        return entry
    
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
            if (entry['iar_reflection'].get('confidence', 1.0) < 0.7 or
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