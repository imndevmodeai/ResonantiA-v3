
# Three_PointO_ArchE/action_registry.py

"""
This module defines the ActionRegistry, a central component for managing,
validating, and dispatching all executable functions (tools) within the ArchE system.
"""

import logging
from typing import Callable, Dict, Any, List, Set

# Set up a logger for the module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ActionRegistry:
    """
    The Librarian of Tools. It catalogs, validates, and dispenses
    every capability available to the ArchE system.

    This class acts as a singleton-like registry where functions, representing
    system capabilities or 'tools', are registered with associated metadata.
    It provides methods to retrieve these functions and validate their inputs
    against the metadata, ensuring safe and correct execution by the workflow engine.

    # This class is the primary embodiment of the 'Action registrY' SPR.
    # Its design enables 'ExtensibilitY' and 'Modularity' for the entire system.
    """

    def __init__(self):
        """
        Initializes the ActionRegistry, preparing the internal storage for actions.
        """
        self._actions: Dict[str, Dict[str, Any]] = {}
        logger.info("ActionRegistry initialized. The Infinite Workshop is open.")

    def register_action(self, action_type: str, action_func: Callable, metadata: Dict[str, Any]):
        """
        Registers a new action (tool) with the registry.

        If an action with the same type already exists, a warning is logged,
        and the existing action is overwritten. This allows for dynamic updates
        of tool implementations.

        # This function 'catalogs' capabilities, relating to the 'Cognitive toolS' SPR.

        Args:
            action_type (str): A unique identifier for the action (e.g., 'web_search').
            action_func (Callable): The actual Python function to be executed.
            metadata (Dict[str, Any]): A dictionary containing details about the action,
                                       including its description and parameter specifications.
                                       Expected format:
                                       {
                                           "description": "...",
                                           "parameters": [
                                               {"name": "param_name", "type": type, "required": bool},
                                               ...
                                           ]
                                       }
        """
        if not isinstance(action_type, str) or not action_type:
            raise TypeError("action_type must be a non-empty string.")
        if not callable(action_func):
            raise TypeError("action_func must be a callable.")
        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        if action_type in self._actions:
            logger.warning(f"Action '{action_type}' is being re-registered. Overwriting previous definition.")

        self._actions[action_type] = {
            "function": action_func,
            "metadata": metadata
        }
        logger.debug(f"Action '{action_type}' registered successfully.")

    def get_action(self, action_type: str) -> Callable:
        """
        Retrieves an action's executable function from the registry.

        # This function 'supplies' the 'Core workflow enginE' with capabilities.

        Args:
            action_type (str): The unique identifier of the action to retrieve.

        Returns:
            Callable: The executable function associated with the action_type.

        Raises:
            ValueError: If no action with the given type is found in the registry.
        """
        try:
            action_info = self._actions[action_type]
            return action_info["function"]
        except KeyError:
            logger.error(f"Attempted to access non-existent action: '{action_type}'")
            raise ValueError(f"Action '{action_type}' not found in registry.")

    def list_actions(self) -> Dict[str, Dict[str, Any]]:
        """
        Lists all registered actions and their metadata.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary where keys are action types
                                       and values are their metadata.
        """
        return {
            action_type: info["metadata"]
            for action_type, info in self._actions.items()
        }

    def validate_inputs(self, action_type: str, provided_inputs: Dict[str, Any]) -> bool:
        """
        Validates a set of provided inputs against an action's metadata.

        This method performs three checks:
        1.  Ensures all required parameters are present.
        2.  Ensures no unexpected parameters are provided.
        3.  Ensures all provided parameter values match their expected types.

        # This function 'prevents' 'Execution DissonancE' by ensuring input integrity.
        # This is a critical step for enabling 'Dynamic Tool OrchestratioN'.

        Args:
            action_type (str): The identifier of the action to validate against.
            provided_inputs (Dict[str, Any]): The inputs to validate, as a dictionary
                                              of parameter names to values.

        Returns:
            bool: True if the inputs are valid.

        Raises:
            ValueError: If the action_type is not found in the registry.
            TypeError: If validation fails due to missing, unexpected, or
                       incorrectly typed parameters.
        """
        try:
            action_info = self._actions[action_type]
        except KeyError:
            raise ValueError(f"Cannot validate inputs for unknown action '{action_type}'.")

        metadata = action_info.get("metadata", {})
        expected_params_list: List[Dict[str, Any]] = metadata.get("parameters", [])
        
        # For efficient lookup, convert list of param dicts to a dict keyed by name
        expected_params_map: Dict[str, Dict[str, Any]] = {
            p["name"]: p for p in expected_params_list
        }

        all_expected_names: Set[str] = set(expected_params_map.keys())
        required_names: Set[str] = {
            p["name"] for p in expected_params_list if p.get("required", False)
        }
        provided_names: Set[str] = set(provided_inputs.keys())

        # 1. Check for missing required parameters
        missing_params = required_names - provided_names
        if missing_params:
            raise TypeError(
                f"Action '{action_type}' missing required parameters: {sorted(list(missing_params))}"
            )

        # 2. Check for unexpected parameters
        unexpected_params = provided_names - all_expected_names
        if unexpected_params:
            raise TypeError(
                f"Action '{action_type}' received unexpected parameters: {sorted(list(unexpected_params))}"
            )

        # 3. Check for correct parameter types
        for name, value in provided_inputs.items():
            param_meta = expected_params_map.get(name)
            if param_meta and "type" in param_meta:
                expected_type = param_meta["type"]
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"Parameter '{name}' for action '{action_type}' has incorrect type. "
                        f"Expected {expected_type.__name__}, but got {type(value).__name__}."
                    )

        logger.debug(f"Inputs for action '{action_type}' validated successfully.")
        return True


if __name__ == '__main__':
    # This block demonstrates the usage of the ActionRegistry.
    # It simulates the registration and execution of a few tools.

    print("--- ArchE ActionRegistry Demonstration ---")

    # 1. Define some dummy tool functions
    def web_search(query: str, engine: str = "google") -> str:
        """Simulates a web search."""
        return f"Simulated search results for '{query}' from {engine}."

    def execute_code(code: str, language: str) -> Dict[str, Any]:
        """Simulates executing a code block."""
        print(f"--- Simulating execution of {language} code ---")
        print(code)
        print("---------------------------------------------")
        return {"status": "success", "output": "simulation complete"}

    # 2. Define metadata for these tools
    WEB_SEARCH_METADATA = {
        "description": "Performs a web search using a specified engine.",
        "parameters": [
            {"name": "query", "type": str, "description": "The search query.", "required": True},
            {"name": "engine", "type": str, "description": "The search engine to use.", "required": False}
        ]
    }

    EXECUTE_CODE_METADATA = {
        "description": "Executes a block of code in a specified language.",
        "parameters": [
            {"name": "code", "type": str, "description": "The code to execute.", "required": True},
            {"name": "language", "type": str, "description": "The programming language.", "required": True}
        ]
    }

    # 3. Initialize the registry and register the actions
    registry = ActionRegistry()
    registry.register_action("web_search", web_search, WEB_SEARCH_METADATA)
    registry.register_action("execute_code", execute_code, EXECUTE_CODE_METADATA)

    print("\n[Registry] Available actions:")
    for name, meta in registry.list_actions().items():
        print(f"  - {name}: {meta['description']}")

    # 4. Simulate a workflow engine using the registry
    print("\n--- Simulating Workflow Tasks ---")

    # Task 1: A valid web search
    task1_inputs = {"query": "ResonantiA Protocol"}
    print(f"\n[Task 1] Action: web_search, Inputs: {task1_inputs}")
    try:
        registry.validate_inputs("web_search", task1_inputs)
        print("[Validation] PASSED")
        search_func = registry.get_action("web_search")
        result = search_func(**task1_inputs)
        print(f"[Execution Result] {result}")
    except (ValueError, TypeError) as e:
        print(f"[Validation] FAILED: {e}")

    # Task 2: A valid code execution
    task2_inputs = {"language": "python", "code": "print('Hello, ArchE!')"}
    print(f"\n[Task 2] Action: execute_code, Inputs: {task2_inputs}")
    try:
        registry.validate_inputs("execute_code", task2_inputs)
        print("[Validation] PASSED")
        exec_func = registry.get_action("execute_code")
        result = exec_func(**task2_inputs)
        print(f"[Execution Result] {result}")
    except (ValueError, TypeError) as e:
        print(f"[Validation] FAILED: {e}")

    # Task 3: An invalid task (missing required parameter)
    task3_inputs = {"code": "console.log('oops')"}
    print(f"\n[Task 3] Action: execute_code, Inputs: {task3_inputs}")
    try:
        registry.validate_inputs("execute_code", task3_inputs)
    except (ValueError, TypeError) as e:
        print(f"[Validation] FAILED as expected: {e}")

    # Task 4: An invalid task (wrong parameter type)
    task4_inputs = {"query": 12345}
    print(f"\n[Task 4] Action: web_search, Inputs: {task4_inputs}")
    try:
        registry.validate_inputs("web_search", task4_inputs)
    except (ValueError, TypeError) as e:
        print(f"[Validation] FAILED as expected: {e}")

    # Task 5: An invalid task (unexpected parameter)
    task5_inputs = {"query": "ArchE", "user_agent": "custom"}
    print(f"\n[Task 5] Action: web_search, Inputs: {task5_inputs}")
    try:
        registry.validate_inputs("web_search", task5_inputs)
    except (ValueError, TypeError) as e:
        print(f"[Validation] FAILED as expected: {e}")

    # Task 6: An invalid task (unknown action)
    task6_inputs = {"prompt": "Who are you?"}
    print(f"\n[Task 6] Action: generate_text, Inputs: {task6_inputs}")
    try:
        registry.validate_inputs("generate_text", task6_inputs)
    except (ValueError, TypeError) as e:
        print(f"[Validation] FAILED as expected: {e}")

    print("\n--- Demonstration Complete ---")
