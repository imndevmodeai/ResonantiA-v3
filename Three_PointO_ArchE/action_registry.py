# --- START OF FILE 3.0ArchE/action_registry.py ---
# ResonantiA Protocol v3.0 - action_registry.py
# Maps action types defined in workflows to their Python execution functions.
# Includes conceptual validation ensuring actions return the required IAR structure.

import logging
import time
import json
import traceback
from typing import Dict, Any, Callable, Optional, List
# Use relative imports for components within the package
from . import config
# Import action functions from various tool modules
# Ensure these imported functions are implemented to return the IAR dictionary
from .tools import run_search, invoke_llm, display_output, calculate_math, placeholder_codebase_search, retrieve_spr_definitions, analyze_system_divergence, compare_system_factors, analyze_workflow_impact, run_code_linter, run_workflow_suite # Basic tools
from .enhanced_tools import call_api, perform_complex_data_analysis, interact_with_database # Enhanced tools
from .code_executor import execute_code # Code execution tool
from .cfp_framework import CfpframeworK # Import the class for the wrapper
from .causal_inference_tool import perform_causal_inference # Causal tool main function
from .agent_based_modeling_tool import perform_abm # ABM tool main function
from .predictive_modeling_tool import run_prediction # Predictive tool main function
from .system_genesis_tool import perform_system_genesis_action # System Genesis tool main function
from .web_search_tool import search_web
from .llm_tool import generate_text_llm
from .self_interrogate_tool import self_interrogate
import inspect
from .action_context import ActionContext # Import from new file
from .error_handler import handle_action_error, DEFAULT_ERROR_STRATEGY, DEFAULT_RETRY_ATTEMPTS

logger = logging.getLogger(__name__)

# --- Action Function Wrapper Example (CFP) ---
# Wrappers adapt underlying classes/functions to the expected action signature
# and ensure IAR generation if the underlying code doesn't handle it directly.
def run_cfp_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for executing CFP analysis using CfpframeworK class.
    Handles initialization, execution, and IAR generation for the 'run_cfp' action type.
    """
    # Initialize reflection structure with default failure state
    reflection = {
        "status": "Failure", "summary": "CFP action failed during initialization.",
        "confidence": 0.0, "alignment_check": "N/A",
        "potential_issues": ["Initialization error."], "raw_output_preview": None
    }
    primary_result = {"error": None} # Store primary metrics or error message

    try:
        # Check if the required class/dependency is available
        if CfpframeworK is None:
            raise ImportError("CFP Framework class (CfpframeworK) is not available (check cfp_framework.py).")

        # Extract and validate inputs required by CfpframeworK
        system_a_config = inputs.get('system_a_config', inputs.get('system_a'))
        system_b_config = inputs.get('system_b_config', inputs.get('system_b'))
        if not system_a_config or not isinstance(system_a_config, dict) or 'quantum_state' not in system_a_config:
            raise ValueError("Missing or invalid 'system_a_config' (must be dict with 'quantum_state').")
        if not system_b_config or not isinstance(system_b_config, dict) or 'quantum_state' not in system_b_config:
            raise ValueError("Missing or invalid 'system_b_config' (must be dict with 'quantum_state').")

        observable = inputs.get('observable', 'position')
        time_horizon = float(inputs.get('timeframe', inputs.get('time_horizon', config.CFP_DEFAULT_TIMEFRAME)))
        integration_steps = int(inputs.get('integration_steps', 100))
        evolution_model = inputs.get('evolution_model', config.CFP_EVOLUTION_MODEL_TYPE)
        hamiltonian_a = inputs.get('hamiltonian_a') # Optional Hamiltonian matrix (e.g., numpy array)
        hamiltonian_b = inputs.get('hamiltonian_b') # Optional Hamiltonian matrix

        logger.debug(f"Initializing CfpframeworK with Observable='{observable}', T={time_horizon}, Evolution='{evolution_model}'...")
        # Initialize the CFP framework class with validated parameters
        cfp_analyzer = CfpframeworK(
            system_a_config=system_a_config,
            system_b_config=system_b_config,
            observable=observable,
            time_horizon=time_horizon,
            integration_steps=integration_steps,
            evolution_model_type=evolution_model,
            hamiltonian_a=hamiltonian_a,
            hamiltonian_b=hamiltonian_b
        )
        # Run the analysis - assumes run_analysis() itself returns a dict
        # *including* its own detailed reflection now (as per Section 7.6 enhancement)
        analysis_results_with_internal_reflection = cfp_analyzer.run_analysis()

        # Extract primary results and the internal reflection from the tool
        internal_reflection = analysis_results_with_internal_reflection.pop('reflection', None)
        primary_result = analysis_results_with_internal_reflection # Remaining keys are primary results

        # --- Generate Wrapper-Level IAR Reflection ---
        # Use the status and summary from the internal reflection if available
        if internal_reflection and isinstance(internal_reflection, dict):
            reflection["status"] = internal_reflection.get("status", "Success" if not primary_result.get("error") else "Failure")
            reflection["summary"] = internal_reflection.get("summary", f"CFP analysis completed using '{evolution_model}'.")
            reflection["confidence"] = internal_reflection.get("confidence", 0.9 if reflection["status"] == "Success" else 0.1)
            reflection["alignment_check"] = internal_reflection.get("alignment_check", "Aligned with comparing system dynamics.")
            reflection["potential_issues"] = internal_reflection.get("potential_issues", [])
            # Use internal preview if available, otherwise generate one
            reflection["raw_output_preview"] = internal_reflection.get("raw_output_preview") or (json.dumps(primary_result, default=str)[:150] + "..." if primary_result else None)
        else: # Fallback if internal reflection is missing (protocol violation by tool)
            reflection["status"] = "Success" if not primary_result.get("error") else "Failure"
            reflection["summary"] = f"CFP analysis completed (Internal reflection missing!). Status: {reflection['status']}"
            reflection["confidence"] = 0.5 # Lower confidence due to missing internal reflection
            reflection["potential_issues"].append("CFP tool did not return standard IAR reflection.")
            reflection["raw_output_preview"] = json.dumps(primary_result, default=str)[:150] + "..." if primary_result else None

        # Ensure any error from the primary result is logged in the reflection summary/issues
        if primary_result.get("error"):
            reflection["status"] = "Failure"
            reflection["summary"] = f"CFP analysis failed: {primary_result.get('error')}. " + reflection["summary"]
            if "potential_issues" not in reflection or reflection["potential_issues"] is None: reflection["potential_issues"] = []
            if primary_result.get("error") not in reflection["potential_issues"]: reflection["potential_issues"].append(f"Execution Error: {primary_result.get('error')}")

    except ImportError as e:
        primary_result["error"] = f"CFP execution failed due to missing dependency: {e}"
        reflection["summary"] = f"CFP action failed: {primary_result['error']}"
        reflection["potential_issues"] = ["Missing quantum_utils or cfp_framework."]
    except (ValueError, TypeError) as e:
        primary_result["error"] = f"CFP input error: {e}"
        reflection["summary"] = f"CFP action failed: {primary_result['error']}"
        reflection["potential_issues"] = ["Invalid input configuration."]
    except Exception as e:
        logger.error(f"Unexpected error executing run_cfp action: {e}", exc_info=True)
        primary_result["error"] = f"Unexpected error in CFP action: {str(e)}"
        reflection["summary"] = f"CFP action failed critically: {primary_result['error']}"
        reflection["potential_issues"] = ["Unexpected system error during CFP wrapper execution."]

    # Ensure the final reflection status matches whether an error is present
    if primary_result.get("error") and reflection.get("status") == "Success":
        reflection["status"] = "Failure" # Correct status if error occurred

    # Combine primary results and the generated reflection
    return {**primary_result, "reflection": reflection}

# --- Action Registry Dictionary ---
# Maps action_type strings (used in workflows) to the corresponding callable function.
# Assumes all registered functions adhere to the IAR return structure (dict with 'reflection').
ACTION_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    # Core Tools (from tools.py - assumed updated for IAR)
    "execute_code": execute_code,
    "search_web": run_search,
    "search_codebase": placeholder_codebase_search,
    "generate_text_llm": invoke_llm, # Example IAR implementation shown in tools.py
    "display_output": display_output,
    "calculate_math": calculate_math,
    "analyze_system_divergence": analyze_system_divergence,
    "compare_system_factors": compare_system_factors,
    "analyze_workflow_impact": analyze_workflow_impact,
    "run_code_linter": run_code_linter,
    "run_workflow_suite": run_workflow_suite,

    # Enhanced Tools (from enhanced_tools.py - assumed updated for IAR)
    "call_external_api": call_api,
    "perform_complex_data_analysis": perform_complex_data_analysis, # Simulation needs full IAR
    "interact_with_database": interact_with_database, # Simulation needs full IAR

    # Specialized Analytical Tools
    "run_cfp": run_cfp_action, # Use the wrapper defined above
    "perform_causal_inference": perform_causal_inference, 
    "perform_abm": perform_abm, 
    "perform_predictive_modeling": run_prediction,

    # --- ResonantiA Protocol v3.0 Tools ---
    "get_spr_details": retrieve_spr_definitions,  # Use the function directly

    # System Genesis and Evolution Workflow Tools
    "perform_system_genesis_action": perform_system_genesis_action,
    "insight_solidification_sgew": perform_system_genesis_action,  # Maps to the same function with different operation

    # Web and search tools
    "search_web": search_web,
    
    # LLM and text generation tools
    "generate_text_llm": generate_text_llm,

    # Self-interrogation tools
    "self_interrogate": self_interrogate
}

def register_action(action_type: str, function: Callable[[Dict[str, Any]], Dict[str, Any]], force: bool = False):
    """Registers a new action type or updates an existing one."""
    if not isinstance(action_type, str) or not action_type:
        logger.error("Action type must be a non-empty string.")
        return False
    if not callable(function):
        logger.error(f"Provided item for action '{action_type}' is not callable.")
        return False

    if action_type in ACTION_REGISTRY and not force:
        logger.warning(f"Action type '{action_type}' is already registered. Use force=True to overwrite.")
        return False

    ACTION_REGISTRY[action_type] = function
    log_msg = f"Registered action type: '{action_type}' mapped to function '{getattr(function, '__name__', repr(function))}'."
    if force and action_type in ACTION_REGISTRY:
        log_msg += " (Forced Update)"
    logger.info(log_msg)
    return True

def execute_action(
    task_key: str, 
    action_name: str, 
    action_type: str, 
    inputs: Dict[str, Any],
    context_for_action: Any,
    max_attempts: int = 1,
    attempt_number: int = 1
) -> Dict[str, Any]:
    """
    Execute an action using the appropriate handler from the action registry.
    Returns a dictionary containing both the primary result and the IAR reflection.
    """
    if action_type not in ACTION_REGISTRY:
        error_msg = f"Unknown action type: {action_type}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "insight": "Action type not found in registry",
                "action": "None",
                "reflection": error_msg
            }
        }

    start_time = time.time()
    try:
        handler = ACTION_REGISTRY[action_type]
        
        # Original logic for finding and executing the action:
        # This typically involves calling a method on action_registry_instance,
        # for example:
        # result_payload = action_registry_instance.execute_action(action_name, params, context, config)

        # IMPORTANT: Replace the comment above with your actual action execution logic.
        # The key is that if an error occurs *within this try block*, the except block below handles it.
        # For this example, we assume the main call is to handler(**inputs)
        
        result_payload = handler(**inputs)

        # If result_payload is already a full IAR, ensure exec_time is present or added.
        # This top-level function might be responsible for adding overall timing if not done by the instance method.
        if isinstance(result_payload, dict) and "reflection" in result_payload:
            if "exec_time" not in result_payload["reflection"]:
                 result_payload["reflection"]["exec_time"] = time.time() - start_time
        # If result_payload is not a dict or not full IAR, this indicates a deeper issue
        # or that this function has more responsibility in formatting the success response.
        # For now, we assume handler(**inputs) provides a compliant structure on success.

        return result_payload

    except Exception as e:
        # This is the critical block for the IAR-compliant error return
        exec_time = time.time() - start_time
        
        # Attempt to get workflow_id and step_id from context if available
        # Ensure context is a dictionary before attempting to use .get()
        current_workflow_id = "N/A"
        current_step_id = "N/A"
        # The context_for_action parameter is passed to this function. Use it.
        if isinstance(context_for_action, dict):
            current_workflow_id = context_for_action.get("workflow_id", "N/A")
            current_step_id = context_for_action.get("step_id", "N/A")

        error_details_for_iar = {
            "action_name": action_name, # This is the action_name parameter of this execute_action function
            "action_type": action_type, # This is the action_type parameter of this execute_action function
            "inputs_provided": inputs, # Parameters provided to the action handler
            "workflow_id": current_workflow_id,
            "step_id": current_step_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
                "confidence": 0.0,
            "potential_issues": [
                f"Action execution failed due to an internal error: {type(e).__name__}.",
                "The system was unable to complete the requested action."
            ],
            "suggestions_for_improvement": [
                "Review the traceback and error message for the root cause.",
                "Verify action parameters and context.",
                "Ensure the action's internal logic handles all edge cases."
            ],
            "exec_time": exec_time
        }
        
        # Construct the final IAR error object
        iar_error_response = {
            "output": None,
            "error": str(e), # Simple error message for quick view
            "success": False,
            "reflection": error_details_for_iar
        }
        return iar_error_response

class ActionRegistry:
    """Registry for workflow actions with dependency tracking."""
    
    def __init__(self):
        """Initialize the action registry."""
        self.actions: Dict[str, Callable] = {}
        self.dependencies: Dict[str, set] = {}
    
    def register_action(self, action_name: str, action_func: Callable) -> None:
        """
        Register a new action with the registry.
        
        Args:
            action_name: Name of the action
            action_func: Function implementing the action
        """
        self.actions[action_name] = action_func
        self.dependencies[action_name] = set(getattr(action_func, "dependencies", []))
        logger.info(f"Registered action: {action_name}")
    
    def get_action(self, action_name: str) -> Optional[Callable]:
        """
        Get an action by name.
        
        Args:
            action_name: Name of the action to retrieve
            
        Returns:
            The action function if found, None otherwise
        """
        return self.actions.get(action_name)
    
    def get_dependencies(self, action_name: str) -> set:
        """
        Get dependencies for an action.
        
        Args:
            action_name: Name of the action
            
        Returns:
            Set of dependency names
        """
        return self.dependencies.get(action_name, set())
    
    def execute_action(self, action_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action with the given inputs.
        
        Args:
            action_name: Name of the action to execute
            inputs: Input parameters for the action
            
        Returns:
            Result of the action execution
            
        Raises:
            ValueError: If the action is not found
        """
        action = self.get_action(action_name)
        if not action:
            raise ValueError(f"Action not found: {action_name}")
        
        try:
            result = action(**inputs)
            return result
        except Exception as e:
            logger.error(f"Error executing action {action_name}: {str(e)}")
            raise

# Create a singleton instance
action_registry = ActionRegistry()

# Export the class and instance
__all__ = ["ActionRegistry", "action_registry"] 