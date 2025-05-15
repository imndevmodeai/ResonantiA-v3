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
from .tools import run_search, invoke_llm, display_output, calculate_math # Basic tools
from .enhanced_tools import call_api, perform_complex_data_analysis, interact_with_database # Enhanced tools
from .code_executor import execute_code # Code execution tool
from .cfp_framework import CFPFramework # Import the class for the wrapper
from .causal_inference_tool import perform_causal_inference # Causal tool main function
from .agent_based_modeling_tool import perform_abm # ABM tool main function
from .predictive_modeling_tool import run_prediction # Predictive tool main function
from .synergy_analysis_tool import perform_synergy_analysis 
#from .causal_discovery_tool import CausalDiscoveryTool #yet to be built

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
        if CFPFramework is None:
            raise ImportError("CFP Framework class (CFPFramework) is not available (check cfp_framework.py).")

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
        # Extract potential ODE functions if passed
        ode_func_a = inputs.get('ode_func_a')
        ode_func_b = inputs.get('ode_func_b')

        logger.debug(f"Initializing CfpframeworK with Observable='{observable}', T={time_horizon}, Evolution='{evolution_model}'...")
        # Initialize the CFP framework class with validated parameters
        cfp_analyzer = CFPFramework(
            system_a_config=system_a_config,
            system_b_config=system_b_config,
            observable=observable,
            time_horizon=time_horizon,
            integration_steps=integration_steps,
            evolution_model_type=evolution_model,
            hamiltonian_a=hamiltonian_a,
            hamiltonian_b=hamiltonian_b,
            ode_func_a=ode_func_a, # Pass ODE funcs
            ode_func_b=ode_func_b
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
    "generate_text_llm": invoke_llm, # Example IAR implementation shown in tools.py
    "display_output": display_output,
    "calculate_math": calculate_math,

    # Enhanced Tools (from enhanced_tools.py - assumed updated for IAR)
    "call_external_api": call_api,
    "perform_complex_data_analysis": perform_complex_data_analysis, # Simulation needs full IAR
    "interact_with_database": interact_with_database, # Simulation needs full IAR

    # Specialized Analytical Tools (Now pointing to implemented versions)
    "run_cfp": run_cfp_action, # Use the wrapper defined above
    "perform_causal_inference": perform_causal_inference, # Points to implemented version
    "perform_abm": perform_abm, # Points to implemented version
    "run_prediction": run_prediction, # Points to implemented version
    "perform_synergy_analysis": perform_synergy_analysis, # Points to implemented version

    # Add other custom actions here
    # "my_custom_action": my_custom_action_function,
}

def register_action(action_type: str, function: Callable[[Dict[str, Any]], Dict[str, Any]], force: bool = False):
    """Registers a new action type or updates an existing one."""
    # (Code identical to v2.9.5 - manages the registry dict)
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

def execute_action(action_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Looks up and executes the function associated with the given action_type.
    Performs conceptual validation for the presence and basic structure of the
    IAR 'reflection' key in the returned dictionary.
    """
    if not isinstance(action_type, str) or action_type not in ACTION_REGISTRY:
        error_msg = f"Unknown or invalid action type: '{action_type}'"
        logger.error(error_msg)
        # Return a standardized error dictionary adhering to IAR structure
        return {
            "error": error_msg,
            "reflection": {
                "status": "Failure", "summary": "Action type not found in registry.",
                "confidence": 0.0, "alignment_check": "N/A",
                "potential_issues": ["Invalid workflow definition or unregistered action."],
                "raw_output_preview": None
            }
        }

    action_function = ACTION_REGISTRY[action_type]
    logger.debug(f"Executing action '{action_type}' with function '{getattr(action_function, '__name__', repr(action_function))}'")

    try:
        # Execute the registered function
        result = action_function(inputs)

        # --- Conceptual IAR Validation ---
        if not isinstance(result, dict):
            # If result is not a dict, it cannot contain the reflection key. Wrap it.
            error_msg = f"Action '{action_type}' returned non-dict result: {type(result)}. Expected dict with 'reflection'."
            logger.error(error_msg)
            return {
                "error": error_msg,
                "original_result": result, # Include original for debugging
                "reflection": {
                    "status": "Failure", "summary": "Action implementation error: Returned non-dict.",
                    "confidence": 0.0, "alignment_check": "Non-compliant with IAR.",
                    "potential_issues": ["Action needs code update for IAR v3.0 compliance."],
                    "raw_output_preview": str(result)[:150]+"..."
                }
            }
        elif "reflection" not in result:
            # If result is a dict but missing the 'reflection' key. Add error reflection.
            error_msg = f"Action '{action_type}' result dictionary missing mandatory 'reflection' key."
            logger.error(error_msg)
            # Add error message and default reflection to the original result dict
            result["error"] = result.get("error", error_msg) # Preserve original error if any
            result["reflection"] = {
                "status": "Failure", # Assume failure if reflection is missing
                "summary": "Action implementation error: Missing 'reflection' key.",
                "confidence": 0.1, # Low confidence due to non-compliance
                "alignment_check": "Non-compliant with IAR.",
                "potential_issues": ["Action needs code update for IAR v3.0 compliance."],
                # Preview original result keys excluding the added reflection/error
                "raw_output_preview": json.dumps({k:v for k,v in result.items() if k not in ['reflection','error']}, default=str)[:150]+"..."
            }
            return result
        elif not isinstance(result.get("reflection"), dict):
            # If 'reflection' key exists but is not a dictionary
            error_msg = f"Action '{action_type}' returned 'reflection' value that is not a dictionary: {type(result.get('reflection'))}."
            logger.error(error_msg)
            result["error"] = result.get("error", error_msg)
            # Overwrite the invalid reflection with a default error one
            result["reflection"] = {
                "status": "Failure", "summary": "Action implementation error: Invalid 'reflection' format (not a dict).",
                "confidence": 0.0, "alignment_check": "Non-compliant with IAR.",
                "potential_issues": ["Action needs code update for IAR v3.0 compliance."],
                "raw_output_preview": json.dumps({k:v for k,v in result.items() if k not in ['reflection','error']}, default=str)[:150]+"..."
            }
            return result
        # --- End IAR Validation ---

        # Log reflection status for monitoring purposes
        reflection_status = result.get("reflection", {}).get("status", "Unknown")
        if reflection_status != "Success":
            # Log warnings or errors based on the reported reflection status
            log_message = f"Action '{action_type}' completed with reflection status: {reflection_status}. Error: {result.get('error')}. Summary: {result.get('reflection',{}).get('summary')}"
            if reflection_status == "Failure":
                logger.error(log_message)
            else:
                logger.warning(log_message)
        else:
            logger.debug(f"Action '{action_type}' completed successfully (Reflection Status: Success).")

        # Return the validated (or wrapped) result dictionary
        return result

    except Exception as e:
        # Catch unexpected errors during the action function call itself
        error_msg = f"Critical exception during action '{action_type}' execution: {e}"
        logger.error(error_msg, exc_info=True)
        # Return a standardized error dictionary adhering to IAR structure
        return {
            "error": error_msg,
            "reflection": {
                "status": "Failure", "summary": f"Critical exception during execution: {e}",
                "confidence": 0.0, "alignment_check": "N/A",
                "potential_issues": ["Unexpected system error during action execution."],
                "raw_output_preview": None
            }
        }

# --- END OF FILE 3.0ArchE/action_registry.py