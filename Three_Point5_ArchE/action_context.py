from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class ActionContext:
    """
    Serves as the Memory Keeper of ArchE, preserving the contextual 
    information that surrounds every action execution.
    """
    task_key: str
    action_name: str
    action_type: str
    workflow_name: str
    run_id: str
    attempt_number: int
    max_attempts: int
    execution_start_time: datetime
    runtime_context: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """
        Validates that essential context fields are present after initialization.
        """
        if not self.task_key:
            raise ValueError("task_key must not be empty.")
        if not self.action_name:
            raise ValueError("action_name must not be empty.")
        if not self.action_type:
            raise ValueError("action_type must not be empty.")
        if not self.workflow_name:
            raise ValueError("workflow_name must not be empty.")
        if not self.run_id:
            raise ValueError("run_id must not be empty.")
