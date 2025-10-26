# Four_PointO_ArchE/workflow/action_registry.py

import os
import importlib.util
import inspect
from typing import Callable, Dict, Any

_registry: Dict[str, Callable[..., Any]] = {}

class ActionRegistry:
    """
    A registry for discovering and holding references to callable actions.
    """

    def __init__(self):
        self.actions: Dict[str, callable] = {}
        # self.discover_actions() # Remove automatic discovery on init

    def register_action(self, name: str, func: callable):
        """
        Manually register a function as an action.
        """
        self.actions[name] = func

    def get_action(self, action_name: str) -> callable:
        """
        Retrieve an action by its registered name.
        """
        if action_name not in self.actions:
            raise ValueError(f"Action '{action_name}' not found in registry.")
        return self.actions[action_name]

    def discover_actions(self, tool_module: Any):
        """
        Discovers actions within a given tool module or a directory path.
        If a module is passed, it inspects it directly.
        If a path is passed, it imports modules from it.
        """
        if isinstance(tool_module, str): # It's a path
            tools_dir = tool_module
            if not os.path.isdir(tools_dir):
                logger.warning(f"Tools directory not found: {tools_dir}")
                return

            for filename in os.listdir(tools_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = filename[:-3]
                    module_path = os.path.join(tools_dir, filename)
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, module_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        self._register_from_module(module)
                    except Exception as e:
                        logger.error(f"Failed to load module {module_name}: {e}")

        elif hasattr(tool_module, '__dict__'): # It's a module object
            self._register_from_module(tool_module)
        else:
            logger.warning(f"Cannot discover actions from type: {type(tool_module)}")

    def _register_from_module(self, module: Any):
        """Helper to register actions from a module object."""
        for name, func in inspect.getmembers(module, inspect.isfunction):
            # We assume any function that doesn't start with '_' is an action.
            # A more robust system might use decorators (e.g., @action).
            if not name.startswith('_'):
                self.register_action(name, func)

    def get_all_actions(self) -> Dict[str, callable]:
        return self.actions

# Global registry instance
registry = ActionRegistry()

def register_action(name: str) -> Callable:
    """
    A decorator for registering an action.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        registry.register_action(name, func)
        return func
    return decorator
