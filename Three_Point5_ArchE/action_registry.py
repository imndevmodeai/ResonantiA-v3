import inspect
from typing import Dict, Any, Callable, Optional, List

class ActionRegistry:
    """Central registry for all available actions in the ArchE system."""

    def __init__(self):
        """Initializes the ActionRegistry."""
        self.actions: Dict[str, Callable] = {}
        self.action_metadata: Dict[str, Dict[str, Any]] = {}

    def register_action(self, action_name: str, action_func: Callable, module: str = "unknown", force: bool = False):
        """Register an action function with the registry."""
        if action_name in self.actions and not force:
            raise ValueError(f"Action '{action_name}' is already registered.")
        
        self.actions[action_name] = action_func
        
        sig = inspect.signature(action_func)
        self.action_metadata[action_name] = {
            "name": action_name,
            "module": module,
            "doc": inspect.getdoc(action_func),
            "parameters": {
                param.name: {
                    "type": str(param.annotation),
                    "default": param.default if param.default != inspect.Parameter.empty else "REQUIRED"
                }
                for param in sig.parameters.values()
            }
        }

    def get_action(self, action_name: str) -> Optional[Callable]:
        """Get an action function by name."""
        return self.actions.get(action_name)

    def list_actions(self) -> List[str]:
        """List all registered action names."""
        return list(self.actions.keys())

    def get_action_metadata(self, action_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific action."""
        return self.action_metadata.get(action_name)

    def validate_action(self, action_name: str, inputs: Dict[str, Any]) -> bool:
        """Validate that an action can be executed with the given inputs."""
        if action_name not in self.actions:
            raise ValueError(f"Action '{action_name}' not found in registry.")
        
        action_func = self.actions[action_name]
        sig = inspect.signature(action_func)
        
        try:
            sig.bind(**inputs)
            return True
        except TypeError as e:
            raise ValueError(f"Input validation failed for action '{action_name}': {e}") from e

# --- Global Registry Instance and Population ---
main_action_registry = ActionRegistry()

def populate_main_registry():
    """Registers all standard and enhanced actions into the main registry."""
    main_action_registry.register_action("display_output", display_output, module="action_registry")

# --- Action Wrapper Functions (Stubs) ---
def list_directory(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Lists the contents of a directory."""
    pass

def read_file(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Reads the content of a file."""
    pass

def display_output(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Displays output to the user."""
    print(inputs.get("content", ""))
    return {"status": "success"}
