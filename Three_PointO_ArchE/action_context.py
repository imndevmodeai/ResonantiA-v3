
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class ActionContext:
    """Contextual information passed to an action during execution."""
    task_key: str
    action_name: str
    action_type: str
    workflow_name: str
    run_id: str
    attempt_number: int
    max_attempts: int
    execution_start_time: datetime
    runtime_context: Dict[str, Any] = field(default_factory=dict)
    # Potentially add other useful context items here later
    # e.g., access_to_global_resources, etc.
    # For now, keeping it minimal with info available at action call time.
    # _workflow_meta could be passed here too, or parts of it.

    # Example of how you might include more detailed workflow context:
    # full_workflow_context_snapshot: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not all([self.task_key, self.action_name, self.action_type, self.workflow_name, self.run_id]):
            raise ValueError("Core ActionContext fields cannot be empty.") 