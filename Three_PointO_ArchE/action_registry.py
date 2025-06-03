# --- START OF FILE 3.0ArchE/action_registry.py ---
# ResonantiA Protocol v3.0 - action_registry.py
# Maps action types defined in workflows to their Python execution functions.
# Includes conceptual validation ensuring actions return the required IAR structure.

import logging
import time
import json
from typing import Dict, Any, Callable, Optional, List
# Use relative imports for components within the package
from . import config
# Import action functions from various tool modules
# Ensure these imported functions are implemented to return the IAR dictionary
from .tools import run_search, invoke_llm, display_output, calculate_math, placeholder_codebase_search, retrieve_spr_definitions # Basic tools
from .enhanced_tools import call_api, perform_complex_data_analysis, interact_with_database # Enhanced tools
from .code_executor import execute_code # Code execution tool
from .cfp_framework import CfpframeworK # Import the class for the wrapper
from .causal_inference_tool import perform_causal_inference # Causal tool main function
from .agent_based_modeling_tool import perform_abm # ABM tool main function
from .predictive_modeling_tool import run_prediction # Predictive tool main function
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
    "get_spr_details": {
        "tool_function": retrieve_spr_definitions, # New tool function
        "description": "Retrieves detailed information for one or more SPRs from the Knowledge Graph.",
        "input_schema": {
            "spr_ids": "(list of strings) A list of SPR IDs to retrieve."
        },
        "output_schema": {
            "spr_details": "(dict) A dictionary where keys are SPR IDs and values are the SPR definition objects.",
            "errors": "(dict) A dictionary of errors encountered, keyed by SPR ID or a general error key."
        }
    },

    # Add other custom actions here
    # "my_custom_action": my_custom_action_function,
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
    context_for_action: ActionContext, 
    max_attempts: int, 
    attempt_number: int 
) -> Dict[str, Any]:
    """
    Core function to execute a registered action (tool) with IAR handling.
    """
    if not isinstance(action_type, str) or action_type not in ACTION_REGISTRY:
        error_msg = f"Unknown or invalid action type: '{action_type}'"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "reflection": {
                "status": "Failure", "summary": "Action type not found in registry.",
                "confidence": 0.0, "alignment_check": "N/A",
                "potential_issues": ["Invalid workflow definition or unregistered action."],
                "raw_output_preview": None
            }
        }

    action_definition_or_callable = ACTION_REGISTRY[action_type]
    actual_tool_function: Optional[Callable] = None

    if callable(action_definition_or_callable):
        actual_tool_function = action_definition_or_callable
    elif isinstance(action_definition_or_callable, dict):
        func = action_definition_or_callable.get("tool_function")
        if callable(func):
            actual_tool_function = func
    
    if not actual_tool_function:
        error_msg = f"Tool function for action '{action_type}' is not defined or not callable in ACTION_REGISTRY."
        logger.error(error_msg)
        # Return IAR error structure
        return {
            "error": error_msg,
            "reflection": {
                "status": "Failure", "summary": f"Action '{action_type}' configuration error.",
                "confidence": 0.0, "alignment_check": "N/A",
                "potential_issues": ["Action registration issue or invalid workflow definition."],
                "raw_output_preview": None
            }
        }

    logger.debug(f"Executing action '{action_type}' with resolved function '{getattr(actual_tool_function, '__name__', repr(actual_tool_function))}'")

    try:
        # This log line directly uses .__name__ which is safe now.
        logger.debug(f"Calling resolved tool function '{actual_tool_function.__name__}' with inputs: {str(inputs)[:200]}... and action_context")
        
        func_signature = inspect.signature(actual_tool_function)
        # Check for the specific parameter name used by retrieve_spr_definitions
        expects_context_for_action = "context_for_action" in func_signature.parameters 
        # Keep the old check for other tools that might use "action_context"
        expects_action_context = "action_context" in func_signature.parameters

        tool_kwargs = {**inputs}
        operation_val = tool_kwargs.pop("operation", None)
        first_param_name = list(func_signature.parameters.keys())[0] if func_signature.parameters else None

        if operation_val is not None and first_param_name == "operation":
            final_call_kwargs = {**tool_kwargs}
            if expects_context_for_action:
                final_call_kwargs["context_for_action"] = context_for_action
            elif expects_action_context:
                final_call_kwargs["action_context"] = context_for_action
            tool_result = actual_tool_function(operation_val, **final_call_kwargs)
        else:
            final_call_args = {}
            final_call_kwargs = {}
            # Populate kwargs based on actual parameter names found
            if expects_context_for_action: # For retrieve_spr_definitions
                final_call_kwargs["context_for_action"] = context_for_action
            elif expects_action_context: # For other tools potentially using this name
                final_call_kwargs["action_context"] = context_for_action
            
            # Compare actual_tool_function with imported function objects directly
            # Ensure all functions compared here are imported at the top of the file.
            if actual_tool_function is execute_code or \
               actual_tool_function is display_output or \
               actual_tool_function is perform_abm or \
               actual_tool_function is perform_causal_inference or \
               actual_tool_function is run_prediction or \
               actual_tool_function is invoke_llm or \
               actual_tool_function is retrieve_spr_definitions:
                actual_inputs_for_tool = {**tool_kwargs}
                if operation_val is not None:
                    actual_inputs_for_tool["operation"] = operation_val
                final_call_args['inputs'] = actual_inputs_for_tool
                tool_result = actual_tool_function(inputs=final_call_args['inputs'], **final_call_kwargs)
            else:
                # Default for other tools (e.g. run_cfp_action which takes **tool_kwargs directly after operation)
                # This path might need review if other tools have specific signature needs.
                # For now, assuming they take individual kwargs or a single operation arg + kwargs.
                actual_inputs_for_tool = {**tool_kwargs}
                if operation_val is not None:
                     # If operation_val exists and the first param is 'operation', it's passed positionally.
                    if first_param_name == "operation":
                        tool_result = actual_tool_function(operation_val, **{**actual_inputs_for_tool, **final_call_kwargs})
                    else: # Pass operation as a kwarg if not the first positional, or if no first_param_name
                        actual_inputs_for_tool["operation"] = operation_val
                        tool_result = actual_tool_function(**{**actual_inputs_for_tool, **final_call_kwargs})
                else: # No operation_val
                    tool_result = actual_tool_function(**{**actual_inputs_for_tool, **final_call_kwargs})

        # Validate tool_result structure (must be dict, should have 'reflection')
        if not isinstance(tool_result, dict):
            error_msg = f"Action '{action_type}' returned non-dict result: {type(tool_result)}. Expected dict with 'reflection'."
            logger.error(error_msg)
            return {
                "error": error_msg,
                "original_result": tool_result, 
                "reflection": {
                    "status": "Failure", "summary": "Action implementation error: Returned non-dict.",
                    "confidence": 0.0, "alignment_check": "Non-compliant with IAR.",
                    "potential_issues": ["Action needs code update for IAR v3.0 compliance."],
                    "raw_output_preview": str(tool_result)[:150]+"..."
                }
            }
        elif "reflection" not in tool_result:
            error_msg = f"Action '{action_type}' result dictionary missing mandatory 'reflection' key."
            logger.error(error_msg)
            # Add error to tool_result if not already present, then build a reflection
            if "error" not in tool_result: tool_result["error"] = error_msg
            tool_result["reflection"] = {
                "status": "Failure", 
                "summary": "Action implementation error: Missing 'reflection' key.",
                "confidence": 0.1, 
                "potential_issues": ["Action missing IAR v3.0 reflection structure."],
                "raw_output_preview": json.dumps({k:v for k,v in tool_result.items() if k not in ['reflection', 'error']}, default=str)[:150]+"..."
            }
        
        # ActionContext is for providing context TO the action, not for storing its results.
        # The reflection comes FROM the tool_result. No need to set things on context_for_action here.

        # Log success/failure based on reflection status
        reflection_data = tool_result.get("reflection", {}) # Get the reflection from the tool's result
        if reflection_data.get("status") == "Failure":
            logger.error(f"Action '{action_type}' completed with reflection status: {reflection_data.get('status')}. Error: {tool_result.get('error')}. Summary: {reflection_data.get('summary')}")
        else:
            logger.debug(f"Action '{action_type}' completed successfully (Reflection Status: {reflection_data.get('status', 'N/A')}).")

        return tool_result

    except Exception as e:
        logger.error(f"Critical error during execution of action '{action_type}': {e}", exc_info=True)
        error_msg = f"System error in action '{action_type}': {e}"
        # Construct reflection directly for this exception case
        critical_failure_reflection = {
            "status": "Failure",
            "summary": f"Action '{action_type}' failed due to system error: {e}",
            "confidence": 0.0,
            "alignment_check": "N/A",
            "potential_issues": [f"System Error: {e}"],
            "raw_output_preview": None
        }
        return {
            "error": error_msg,
            "reflection": critical_failure_reflection
        }

# --- END OF FILE 3.0ArchE/action_registry.py --- 