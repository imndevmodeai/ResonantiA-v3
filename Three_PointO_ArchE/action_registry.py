# --- START OF FILE 3.0ArchE/action_registry.py ---
# ResonantiA Protocol v3.0 - action_registry.py
# Maps action types defined in workflows to their Python execution functions.
# Includes conceptual validation ensuring actions return the required IAR structure.

import logging
import time
import json
import os
from typing import Dict, Any, Callable, Optional, List
import inspect
# Use relative imports for components within the package
from . import config
# Import action functions from various tool modules
# Ensure these imported functions are implemented to return the IAR dictionary
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
from .action_context import ActionContext # Import from new file
from .error_handler import handle_action_error, DEFAULT_ERROR_STRATEGY, DEFAULT_RETRY_ATTEMPTS
from .qa_tools import run_code_linter, run_workflow_suite
from .tools.search_tool import SearchTool

logger = logging.getLogger(__name__)

def _create_reflection(status: str, summary: str, confidence: Optional[float], alignment: Optional[str], issues: Optional[List[str]], preview: Any) -> Dict[str, Any]:
    """Helper function to create the standardized IAR reflection dictionary."""
    if confidence is not None: confidence = max(0.0, min(1.0, confidence))
    issues_list = issues if issues else None
    try:
        preview_str = json.dumps(preview, default=str) if isinstance(preview, (dict, list)) else str(preview)
        if preview_str and len(preview_str) > 150: preview_str = preview_str[:150] + "..."
    except Exception:
        try: preview_str = str(preview); preview_str = preview_str[:150] + "..." if len(preview_str) > 150 else preview_str
        except Exception: preview_str = "[Preview Error]"
    return {"status": status, "summary": summary, "confidence": confidence, "alignment_check": alignment if alignment else "N/A", "potential_issues": issues_list, "raw_output_preview": preview_str}

def list_directory(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Lists the contents of a specified directory."""
    directory = inputs.get("directory", ".")
    try:
        files = os.listdir(directory)
        return {
            "files": files,
            "reflection": _create_reflection("Success", f"Listed contents of '{directory}'.", 1.0, "Aligned", None, files)
        }
    except Exception as e:
        return {
            "error": str(e),
            "reflection": _create_reflection("Failure", f"Failed to list directory '{directory}'.", 0.0, "Misaligned", [str(e)], None)
        }

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
        time_horizon = float(inputs.get('timeframe', inputs.get('time_horizon', config.CONFIG.tools.cfp_default_time_horizon)))
        integration_steps = int(inputs.get('integration_steps', config.CONFIG.tools.cfp_default_integration_steps))
        evolution_model = inputs.get('evolution_model', config.CONFIG.tools.cfp_default_evolution_model)
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

def search_tool_action(query: str, num_results: int = 5, provider: str = "google") -> Dict[str, Any]:
    """
    Wrapper for executing a search using the SearchTool.
    """
    try:
        if not query:
            raise ValueError("Input 'query' is required for the search tool.")

        search_tool = SearchTool()
        result = search_tool.search(query=query, num_results=num_results, provider=provider)
        
        return result

    except Exception as e:
        return {
            "error": str(e),
            "reflection": {
                "tool_name": "SearchTool",
                "success": False,
                "message": f"An unexpected error occurred in search_tool_action: {e}",
                "data": {"query": query, "num_results": num_results}
            }
        }

# Centralized Action Registry
ACTION_REGISTRY: Dict[str, Callable] = {
    # Foundational Actions
    "execute_code": execute_code,
    "list_directory": list_directory,
    "search_web": search_tool_action,
    "generate_text_llm": generate_text_llm,
    
    # External Interaction
    "call_external_api": call_api,
    "perform_complex_data_analysis": perform_complex_data_analysis,
    "interact_with_database": interact_with_database,

    # Advanced Agentic & Metacognitive Actions
    "run_cfp": run_cfp_action,
    "perform_causal_inference": perform_causal_inference,
    "perform_abm": perform_abm,
    "perform_predictive_modeling": run_prediction,
    "perform_system_genesis_action": perform_system_genesis_action,
    "insight_solidification_sgew": perform_system_genesis_action,
    "self_interrogate": self_interrogate,
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

    try:
        handler = ACTION_REGISTRY[action_type]
        result = handler(**inputs)
        
        # Ensure result includes IAR reflection
        if isinstance(result, dict) and "reflection" not in result:
            result["reflection"] = {
                "status": "Success",
                "confidence": 1.0,
                "insight": "Action completed successfully",
                "action": action_type,
                "reflection": "No issues encountered"
            }
        
        return result

    except Exception as e:
        error_msg = f"Error executing action {action_type}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "insight": f"Error in {action_type}",
                "action": "None",
                "reflection": error_msg
            }
        }

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

    def get_registered_actions_summary(self) -> str:
        """
        Returns a string summary of all registered actions.
        """
        if not self.actions:
            return "No actions registered."
        
        summary_lines = ["Available Tools:"]
        for name, func in self.actions.items():
            doc = inspect.getdoc(func)
            first_line = doc.split('\\n')[0] if doc else "No description."
            summary_lines.append(f"- {name}: {first_line}")
        return "\\n".join(summary_lines)

# Create a singleton instance
action_registry = ActionRegistry()

# Export the class and instance
__all__ = ["ActionRegistry", "action_registry"] 