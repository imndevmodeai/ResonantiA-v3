from typing import Dict, Any, Callable
from .perception_orchestrator import execute_web_task
# We will add other non-web tools here as we migrate them
# from .some_other_tool import some_action

class ActionRegistry:
    """
    [V4.1 - CANONICAL] The single source of truth for all actions available
    to the ArchE system. It ensures that the Perception Engine is the sole
    gateway for all external web interactions.
    """
    def __init__(self):
        self._actions = {}
        self._register_core_actions()

    def _register_core_actions(self):
        """
        Register the foundational actions of the V4 architecture.
        """
        self.register_action('execute_web_task', execute_web_task)
        # self.register_action('some_other_action', some_action)

    def register_action(self, name: str, function: Callable[[Dict[str, Any]], Any]):
        self._actions[name] = function

    def get_action(self, name: str) -> Callable[[Dict[str, Any]], Any]:
        action = self._actions.get(name)
        if not action:
            raise ValueError(f"Action '{name}' not found in the canonical registry.")
        return action

# Singleton instance
canonical_registry = ActionRegistry()

def execute_action(action_name: str, inputs: Dict[str, Any]) -> Any:
    """
    The single, unified entry point for executing any action in the system.
    """
    try:
        action = canonical_registry.get_action(action_name)
        # Note: IAR compliance will be handled within each action function
        return action(inputs)
    except ValueError as e:
        # This provides a clear error if a deprecated or unknown action is called
        return {"error": str(e), "status": "ActionNotFound"}
