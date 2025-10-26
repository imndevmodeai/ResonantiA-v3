# --- START OF FILE 3.0ArchE/action_registry_v2.py ---
import logging
from typing import Dict, Any, Callable
import subprocess
import os
import sys
import tempfile

# --- Core Imports ---
try:
    from . import config
    from .error_handler import handle_action_error
except ImportError:
    import config
    from error_handler import handle_action_error

logger = logging.getLogger(__name__)

# --- Tool Imports ---
from Three_PointO_ArchE.tools.enhanced_search_tool import perform_web_search
from Three_PointO_ArchE.tools.synthesis_tool import invoke_llm_for_synthesis
from Three_PointO_ArchE.tools.code_executor import execute_code

class ActionRegistry:
    """A central registry for all callable actions (tools) in the system."""
    def __init__(self):
        self.actions: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        logger.info("ActionRegistry initialized.")

    def register_action(self, action_type: str, function: Callable[[Dict[str, Any]], Dict[str, Any]], force: bool = False):
        if action_type in self.actions and not force:
            logger.warning(f"Action '{action_type}' already registered. Skipping.")
        else:
            self.actions[action_type] = function
            logger.info(f"Action '{action_type}' registered.")

    def get_action(self, name: str) -> Callable:
        action = self.actions.get(name)
        if not action:
            logger.error(f"Action '{name}' not found. Available: {list(self.actions.keys())}")
            raise KeyError(f"Action '{name}' not found.")
        return action

main_action_registry = ActionRegistry()

# --- Placeholder & Utility Functions ---
def display_output(content: str, **kwargs) -> Dict[str, Any]:
    """Placeholder: Prints content to the console."""
    import pprint
    logger.info("DISPLAY_OUTPUT Action Fired:")
    pprint.pprint(content)
    return {'status': 'success', 'message': 'Content displayed.'}

def calculate_math(expression: str, **kwargs) -> Dict[str, Any]:
    """Evaluates a simple mathematical expression."""
    logger.info(f"CALCULATE_MATH Action Fired with expression: {expression}")
    try:
        result = eval(str(expression))
        return {'status': 'success', 'result': result}
    except Exception as e:
        logger.error(f"Error evaluating math expression '{expression}': {e}", exc_info=True)
        return {'status': 'error', 'message': str(e)}

# --- Registering Core Actions ---
main_action_registry.register_action("execute_code", execute_code)
main_action_registry.register_action("search_web", perform_web_search)
main_action_registry.register_action("generate_text_llm", invoke_llm_for_synthesis)
main_action_registry.register_action("display_output", display_output)
main_action_registry.register_action("calculate_math", calculate_math)

# --- Global Execute Function ---
def execute_action(action_type: str, inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Executes a registered action by name."""
    try:
        logger.info(f"Executing action '{action_type}'...")
        action_func = main_action_registry.get_action(action_type)
        result = action_func(**inputs)
        logger.info(f"Action '{action_type}' executed successfully.")
        return result
    except KeyError:
        return {"status": "error", "message": f"Action '{action_type}' not found."}
    except Exception as e:
        logger.error(f"An unexpected error occurred during execution of action '{action_type}': {e}", exc_info=True)
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}
