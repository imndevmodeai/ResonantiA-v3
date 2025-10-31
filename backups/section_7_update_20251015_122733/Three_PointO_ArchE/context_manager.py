from typing import Dict, Any

class ContextManager:
    """
    Manages the runtime context of a workflow, including initial context
    and the results of completed tasks.
    """
    def __init__(self, initial_context: Dict[str, Any]):
        self.runtime_context = {"initial_context": initial_context}

    def update_context(self, task_id: str, result: Dict[str, Any]):
        """Adds the result of a task to the runtime context."""
        self.runtime_context[task_id] = result

    def get_context(self) -> Dict[str, Any]:
        """Returns the entire runtime context."""
        return self.runtime_context 