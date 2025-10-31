from typing import Dict, Any, Callable

class ExecutionManager:
    """
    Manages the execution of tasks, including handling dependencies and retries.
    """
    def __init__(self, action_registry: Dict[str, Callable]):
        self.action_registry = action_registry

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a single task.
        """
        action_type = task.get("action_type")
        if not action_type or action_type not in self.action_registry:
            return {"error": f"Invalid or missing action_type: {action_type}"}

        action_func = self.action_registry[action_type]
        inputs = task.get("inputs", {})
        
        try:
            result = action_func(**inputs)
            return result
        except Exception as e:
            return {"error": str(e)} 