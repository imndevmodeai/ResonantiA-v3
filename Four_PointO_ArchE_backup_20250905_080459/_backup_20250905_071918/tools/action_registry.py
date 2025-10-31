from typing import Dict, Any, Callable
from .perception_orchestrator import execute_web_task

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
        self.register_action('execute_web_task', execute_web_task)

    def register_action(self, name: str, function: Callable[[Dict[str, Any]], Any]):
        self._actions[name] = function

    def get_action(self, name: str) -> Callable[[Dict[str, Any]], Any]:
        action = self._actions.get(name)
        if not action:
            raise ValueError(f"Action '{name}' not found in the canonical registry.")
        return action

canonical_registry = ActionRegistry()

def execute_action(action_name: str, inputs: Dict[str, Any]) -> Any:
    try:
        action = canonical_registry.get_action(action_name)
        return action(inputs)
    except ValueError as e:
        return {"error": str(e), "status": "ActionNotFound"}
