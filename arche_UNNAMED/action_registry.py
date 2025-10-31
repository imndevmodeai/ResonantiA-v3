"""
Action Registry - ResonantiA Protocol v3.5-GP
Maps abstract action types to concrete implementation functions.
All actions must return IAR-compliant dictionaries.
"""

import logging
from typing import Dict, Any, Callable, Optional, List
from functools import wraps
import time

from .iar import IARReflection, IARStatus, create_error_iar, create_success_iar

logger = logging.getLogger(__name__)


class ActionRegistry:
    """
    Central registry for action implementations.
    
    Every action must:
    1. Accept a dictionary of inputs
    2. Return a dictionary with an embedded 'reflection' field containing IAR data
    3. Handle errors gracefully and return error information in IAR
    """
    
    def __init__(self):
        self._registry: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self._action_metadata: Dict[str, Dict[str, Any]] = {}
        logger.info("Action Registry initialized")
    
    def register(
        self,
        action_type: str,
        action_function: Callable[[Dict[str, Any]], Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> bool:
        """
        Register an action type with its implementation function.
        
        Args:
            action_type: The action type identifier (e.g., 'search_web', 'run_cfp').
            action_function: The function that implements the action.
                           Must accept dict inputs and return dict with 'reflection' IAR field.
            metadata: Optional metadata about the action (description, capabilities, etc.).
            force: If True, overwrite existing registration.
        
        Returns:
            True if registered successfully, False otherwise.
        """
        if not isinstance(action_type, str) or not action_type:
            logger.error(f"Invalid action_type: {action_type}")
            return False
        
        if not callable(action_function):
            logger.error(f"action_function must be callable for action_type '{action_type}'")
            return False
        
        if action_type in self._registry and not force:
            logger.warning(f"Action type '{action_type}' already registered. Use force=True to overwrite.")
            return False
        
        self._registry[action_type] = action_function
        self._action_metadata[action_type] = metadata or {}
        self._action_metadata[action_type]["action_type"] = action_type
        
        logger.info(f"Registered action type: {action_type}")
        return True
    
    def get_action(self, action_type: str) -> Optional[Callable[[Dict[str, Any]], Dict[str, Any]]]:
        """
        Retrieve the implementation function for an action type.
        
        Args:
            action_type: The action type identifier.
        
        Returns:
            The action function, or None if not registered.
        """
        return self._registry.get(action_type)
    
    def is_registered(self, action_type: str) -> bool:
        """Check if an action type is registered."""
        return action_type in self._registry
    
    def get_metadata(self, action_type: str) -> Optional[Dict[str, Any]]:
        """Get metadata for an action type."""
        return self._action_metadata.get(action_type)
    
    def list_actions(self) -> List[str]:
        """Return list of all registered action types."""
        return list(self._registry.keys())
    
    def execute(
        self,
        action_type: str,
        inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a registered action with inputs and return IAR-compliant result.
        
        Args:
            action_type: The action type to execute.
            inputs: Input dictionary for the action.
            context: Optional workflow context (for access to previous results, etc.).
        
        Returns:
            Dictionary containing:
            - 'result': The action's primary output (if successful)
            - 'reflection': IAR dictionary with self-assessment
            - 'error': Error message if execution failed (reflection.status will be 'error')
        """
        if action_type not in self._registry:
            logger.error(f"Unknown action type: '{action_type}'")
            error_iar = create_error_iar(
                error=f"Unknown action type: {action_type}",
                confidence=0.0
            )
            return {
                "result": None,
                "reflection": error_iar,
                "error": f"Unknown action type: {action_type}"
            }
        
        action_function = self._registry[action_type]
        
        # Prepare execution context
        execution_start_time = time.time()
        
        try:
            # Execute the action
            logger.debug(f"Executing action '{action_type}' with inputs: {list(inputs.keys())}")
            action_result = action_function(inputs)
            
            # Ensure action returned a dictionary
            if not isinstance(action_result, dict):
                logger.warning(f"Action '{action_type}' returned non-dict result: {type(action_result)}")
                action_result = {"result": action_result}
            
            # Extract IAR reflection from result
            reflection = action_result.get("reflection")
            if reflection is None:
                # Action didn't provide IAR, create a default success IAR
                logger.warning(f"Action '{action_type}' did not provide IAR reflection. Creating default.")
                reflection = create_success_iar(
                    confidence=0.7,
                    notes=f"Action '{action_type}' executed but did not provide IAR reflection"
                )
                action_result["reflection"] = reflection
            
            # Validate IAR reflection
            is_valid, validation_error = IARReflection.validate(reflection)
            if not is_valid:
                logger.error(f"Action '{action_type}' returned invalid IAR reflection: {validation_error}")
                # Replace with valid error IAR
                reflection = create_error_iar(
                    error=f"Invalid IAR returned by action: {validation_error}",
                    confidence=0.1
                )
                action_result["reflection"] = reflection
            
            # Add execution metadata to IAR if not present
            execution_time_ms = (time.time() - execution_start_time) * 1000
            if "execution_time_ms" not in reflection:
                reflection["execution_time_ms"] = execution_time_ms
            
            # Ensure result field exists
            if "result" not in action_result:
                action_result["result"] = action_result.get("output") or action_result.get("data") or None
            
            # Ensure reflection is in result
            action_result["reflection"] = reflection
            
            # Add error field if IAR indicates error
            if IARReflection.has_error(reflection):
                error_msg = reflection.get("error") or f"Action '{action_type}' failed with status: {reflection.get('status')}"
                action_result["error"] = error_msg
            
            logger.debug(f"Action '{action_type}' completed with status: {reflection.get('status')}, confidence: {reflection.get('confidence')}")
            return action_result
            
        except Exception as e:
            logger.error(f"Exception during execution of action '{action_type}': {e}", exc_info=True)
            error_iar = create_error_iar(
                error=f"Exception during action execution: {str(e)}",
                confidence=0.0,
                potential_issues=[f"Unhandled exception in action '{action_type}': {type(e).__name__}"]
            )
            error_iar["execution_time_ms"] = (time.time() - execution_start_time) * 1000
            
            return {
                "result": None,
                "reflection": error_iar,
                "error": str(e)
            }


# Global registry instance
_global_registry = ActionRegistry()


def register_action(
    action_type: str,
    action_function: Callable[[Dict[str, Any]], Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None,
    force: bool = False
) -> bool:
    """
    Register an action type in the global registry.
    
    Convenience function for registering actions.
    """
    return _global_registry.register(action_type, action_function, metadata, force)


def execute_action(
    action_type: str,
    inputs: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute an action from the global registry.
    
    Convenience function for executing actions.
    """
    return _global_registry.execute(action_type, inputs, context)


def get_action(action_type: str) -> Optional[Callable[[Dict[str, Any]], Dict[str, Any]]]:
    """Get an action function from the global registry."""
    return _global_registry.get_action(action_type)


def list_actions() -> List[str]:
    """List all registered action types."""
    return _global_registry.list_actions()


def iar_compliant(action_function: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Callable:
    """
    Decorator to ensure an action function returns IAR-compliant output.
    
    Usage:
        @iar_compliant
        def my_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
            # ... action logic ...
            result = compute_something()
            return {
                "result": result,
                "reflection": create_success_iar(confidence=0.9)
            }
    """
    @wraps(action_function)
    def wrapper(inputs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = action_function(inputs)
            
            # Ensure result is a dict
            if not isinstance(result, dict):
                result = {"result": result}
            
            # Ensure reflection field exists
            if "reflection" not in result:
                # Try to infer status from result
                has_error = "error" in result or result.get("status") in ["error", "failure"]
                confidence = 0.9 if not has_error else 0.3
                
                result["reflection"] = create_success_iar(
                    confidence=confidence
                ) if not has_error else create_error_iar(
                    error=result.get("error", "Action failed without explicit error message"),
                    confidence=confidence
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Exception in action function: {e}", exc_info=True)
            return {
                "result": None,
                "reflection": create_error_iar(
                    error=f"Unhandled exception: {str(e)}",
                    confidence=0.0
                ),
                "error": str(e)
            }
    
    return wrapper
