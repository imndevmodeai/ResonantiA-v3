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

# --- Core Imports ---
from . import config
from .action_context import ActionContext
from .error_handler import handle_action_error

logger = logging.getLogger(__name__)

# --- Tool and Action Function Imports ---
from .enhanced_tools import call_api, perform_complex_data_analysis, interact_with_database
from .code_executor import execute_code
from .cfp_framework import CfpframeworK
from .causal_inference_tool import perform_causal_inference
from .agent_based_modeling_tool import perform_abm
from .predictive_modeling_tool import run_prediction
from .system_genesis_tool import perform_system_genesis_action
from .web_search_tool import search_web
from .llm_tool import generate_text_llm
from .self_interrogate_tool import self_interrogate
from .qa_tools import run_code_linter, run_workflow_suite
from .tools.search_tool import SearchTool
from .spr_action_bridge import invoke_spr, SPRBridgeLoader
from .predictive_flux_coupling_engine import run_predictive_flux_analysis

# --- Gemini Enhanced Tools Initialization ---
try:
    from .tools.gemini_enhanced_tools import get_gemini_tool_suite
    gemini_tool_suite = get_gemini_tool_suite()
    GEMINI_TOOLS_AVAILABLE = True
    logger.info("Gemini Enhanced Tool Suite initialized successfully.")
except ImportError as e:
    gemini_tool_suite = None
    GEMINI_TOOLS_AVAILABLE = False
    logger.warning(f"Gemini Enhanced Tool Suite could not be initialized: {e}")
except Exception as e:
    gemini_tool_suite = None
    GEMINI_TOOLS_AVAILABLE = False
    logger.error(f"An unexpected error occurred during Gemini tool suite initialization: {e}", exc_info=True)


# --- SPR Bridge Initialization ---
CONFIG = config.get_config()
SPR_TAPESTRY_PATH = CONFIG.paths.arche_root / "knowledge_graph" / "spr_definitions_tv.json"
SPR_LOADER = SPRBridgeLoader(tapestry_path=str(SPR_TAPESTRY_PATH))

# --- Helper Functions ---
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


# --- Standard Action Wrappers ---

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

def run_cfp_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for executing CFP analysis using CfpframeworK class."""
    reflection = {
        "status": "Failure", "summary": "CFP action failed during initialization.",
        "confidence": 0.0, "alignment_check": "N/A",
        "potential_issues": ["Initialization error."], "raw_output_preview": None
    }
    primary_result = {"error": None} 

    try:
        if CfpframeworK is None:
            raise ImportError("CFP Framework class (CfpframeworK) is not available (check cfp_framework.py).")

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
        hamiltonian_a = inputs.get('hamiltonian_a') 
        hamiltonian_b = inputs.get('hamiltonian_b') 

        logger.debug(f"Initializing CfpframeworK with Observable='{observable}', T={time_horizon}, Evolution='{evolution_model}'...")
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
        analysis_results_with_internal_reflection = cfp_analyzer.run_analysis()
        internal_reflection = analysis_results_with_internal_reflection.pop('reflection', None)
        primary_result = analysis_results_with_internal_reflection

        if internal_reflection and isinstance(internal_reflection, dict):
            reflection["status"] = internal_reflection.get("status", "Success" if not primary_result.get("error") else "Failure")
            reflection["summary"] = internal_reflection.get("summary", f"CFP analysis completed using '{evolution_model}'.")
            reflection["confidence"] = internal_reflection.get("confidence", 0.9 if reflection["status"] == "Success" else 0.1)
            reflection["alignment_check"] = internal_reflection.get("alignment_check", "Aligned with comparing system dynamics.")
            reflection["potential_issues"] = internal_reflection.get("potential_issues", [])
            reflection["raw_output_preview"] = internal_reflection.get("raw_output_preview") or (json.dumps(primary_result, default=str)[:150] + "..." if primary_result else None)
        else: 
            reflection["status"] = "Success" if not primary_result.get("error") else "Failure"
            reflection["summary"] = f"CFP analysis completed (Internal reflection missing!). Status: {reflection['status']}"
            reflection["confidence"] = 0.5
            reflection["potential_issues"].append("CFP tool did not return standard IAR reflection.")
            reflection["raw_output_preview"] = json.dumps(primary_result, default=str)[:150] + "..." if primary_result else None

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

    if primary_result.get("error") and reflection.get("status") == "Success":
        reflection["status"] = "Failure"

    return {**primary_result, "reflection": reflection}


def search_tool_action(query: str, num_results: int = 5, provider: str = "google") -> Dict[str, Any]:
    """Wrapper for executing a search using the SearchTool."""
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

def invoke_spr_action(spr_id: str, **kwargs) -> Dict[str, Any]:
    """Action registry wrapper for the SPR bridge."""
    try:
        result = invoke_spr(spr_id=spr_id, parameters=kwargs, bridge_loader=SPR_LOADER)
        
        if "reflection" not in result:
            logger.warning(f"SPR Action '{spr_id}' did not return a standard IAR reflection. Creating a fallback.")
            fallback_reflection = _create_reflection(
                "Success" if "error" not in result else "Failure",
                f"SPR action '{spr_id}' executed.",
                0.7, "Alignment check needed.",
                [f"Error: {result['error']}"] if "error" in result else None,
                result
            )
            result["reflection"] = fallback_reflection
        return result
    except Exception as e:
        logger.error(f"Failed to invoke SPR action '{spr_id}': {e}", exc_info=True)
        return handle_action_error(f"invoke_spr:{spr_id}", e, {"spr_id": spr_id, **kwargs})


def run_predictive_flux_coupling(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for executing Predictive Flux Coupling (PFC) analysis."""
    try:
        operation = inputs.get('operation', 'calculate_pfc')
        
        valid_operations = ['calculate_pfc', 'ensemble_forecast', 'detect_patterns']
        if operation not in valid_operations:
            raise ValueError(f"Invalid operation '{operation}'. Valid operations: {valid_operations}")
        
        result = run_predictive_flux_analysis(operation=operation, **inputs)
        
        if 'reflection' not in result:
            result['reflection'] = {
                "status": "Warning",
                "summary": f"PFC operation '{operation}' completed but missing IAR reflection",
                "confidence": 0.5,
                "alignment_check": "Partially aligned - missing reflection",
                "potential_issues": ["Missing IAR reflection from PFC engine"]
            }
        
        return result
        
    except Exception as e:
        logger.error(f"PFC action failed: {e}", exc_info=True)
        return handle_action_error("run_predictive_flux_coupling", e, inputs)

# --- Gemini Enhanced Action Wrappers ---

def execute_gemini_code(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Action wrapper for Gemini Code Executor."""
    if not GEMINI_TOOLS_AVAILABLE:
        return handle_action_error("execute_gemini_code", "Gemini tools are not available.", inputs)
    try:
        code = inputs.get("code")
        if not code:
            raise ValueError("Input 'code' is required for execute_gemini_code.")
        # Pass all inputs to the tool method
        return gemini_tool_suite.execute_gemini_code(**inputs)
    except Exception as e:
        return handle_action_error("execute_gemini_code", e, inputs)

def process_gemini_file(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Action wrapper for Gemini File Processor."""
    if not GEMINI_TOOLS_AVAILABLE:
        return handle_action_error("process_gemini_file", "Gemini tools are not available.", inputs)
    try:
        file_url = inputs.get("file_url")
        if not file_url:
            raise ValueError("Input 'file_url' is required for process_gemini_file.")
        return gemini_tool_suite.process_gemini_file(**inputs)
    except Exception as e:
        return handle_action_error("process_gemini_file", e, inputs)

def generate_with_grounding(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Action wrapper for Gemini Grounded Generation."""
    if not GEMINI_TOOLS_AVAILABLE:
        return handle_action_error("generate_with_grounding", "Gemini tools are not available.", inputs)
    try:
        prompt = inputs.get("prompt")
        sources = inputs.get("sources")
        if not prompt or sources is None:
            raise ValueError("Inputs 'prompt' and 'sources' are required for generate_with_grounding.")
        return gemini_tool_suite.generate_with_grounding(**inputs)
    except Exception as e:
        return handle_action_error("generate_with_grounding", e, inputs)

def generate_with_function_calling(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Action wrapper for Gemini Function Calling."""
    if not GEMINI_TOOLS_AVAILABLE:
        return handle_action_error("generate_with_function_calling", "Gemini tools are not available.", inputs)
    try:
        prompt = inputs.get("prompt")
        functions = inputs.get("functions")
        if not prompt or functions is None:
            raise ValueError("Inputs 'prompt' and 'functions' are required for generate_with_function_calling.")
        return gemini_tool_suite.generate_with_function_calling(**inputs)
    except Exception as e:
        return handle_action_error("generate_with_function_calling", e, inputs)

def generate_with_structured_output(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Action wrapper for Gemini Structured Output."""
    if not GEMINI_TOOLS_AVAILABLE:
        return handle_action_error("generate_with_structured_output", "Gemini tools are not available.", inputs)
    try:
        prompt = inputs.get("prompt")
        schema = inputs.get("schema")
        if not prompt or schema is None:
            raise ValueError("Inputs 'prompt' and 'schema' are required for generate_with_structured_output.")
        return gemini_tool_suite.generate_with_structured_output(**inputs)
    except Exception as e:
        return handle_action_error("generate_with_structured_output", e, inputs)


# --- Registry Instantiation and Population ---

class ActionRegistry:
    """A central registry for all available actions in the ArchE system."""
    def __init__(self):
        self.actions: Dict[str, Callable] = {}
        logger.info("ActionRegistry initialized.")

    def register_action(self, action_name: str, action_func: Callable) -> None:
        """Registers an action function with a given name."""
        if action_name in self.actions:
            logger.warning(f"Action '{action_name}' is being overwritten in the registry.")
        self.actions[action_name] = action_func
        logger.debug(f"Action '{action_name}' registered.")

    def get_action(self, action_name: str) -> Optional[Callable]:
        """Retrieves an action function from the registry."""
        return self.actions.get(action_name)

    def get_dependencies(self, action_name: str) -> set:
        """
        Analyzes an action function's signature to determine its input dependencies.
        (Conceptual implementation)
        """
        action_func = self.get_action(action_name)
        if not action_func:
            return set()
        
        sig = inspect.signature(action_func)
        # Assumes inputs are passed as a single dictionary
        # A more complex analysis would inspect the tool's signature directly
        return set(sig.parameters.keys())

    def execute_action(self, action_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Looks up and executes an action from the registry."""
        action_func = self.get_action(action_name)
        if not action_func:
            msg = f"Action '{action_name}' not found in registry."
            logger.error(msg)
            return handle_action_error(action_name, ValueError(msg), inputs)
        
        logger.info(f"Executing action '{action_name}'...")
        try:
            # The action function is expected to handle the IAR reflection internally
            result = action_func(inputs)
            return result
        except Exception as e:
            logger.error(f"Exception during execution of action '{action_name}': {e}", exc_info=True)
            return handle_action_error(action_name, e, inputs)

    def get_registered_actions_summary(self) -> str:
        """Returns a string summary of all registered actions."""
        if not self.actions:
            return "No actions registered."
        
        summary_lines = ["Registered Actions:", "-------------------"]
        for name in sorted(self.actions.keys()):
            summary_lines.append(f"- {name}")
        return "\n".join(summary_lines)

# --- Global Registry Instance ---
# Singleton instance of the ActionRegistry
main_action_registry = ActionRegistry()

def populate_main_registry():
    """Registers all standard and enhanced actions into the main registry."""
    logger.info("Populating the main action registry...")
    
    # Standard Tools
    main_action_registry.register_action("list_directory", list_directory)
    main_action_registry.register_action("run_cfp", run_cfp_action)
    main_action_registry.register_action("search_web", search_web) # Assumes search_web is adapted to the standard wrapper
    main_action_registry.register_action("generate_text", generate_text_llm)
    main_action_registry.register_action("execute_code", execute_code)
    main_action_registry.register_action("perform_causal_inference", perform_causal_inference)
    main_action_registry.register_action("perform_abm", perform_abm)
    main_action_registry.register_action("run_prediction", run_prediction)
    main_action_registry.register_action("call_api", call_api)
    main_action_registry.register_action("interact_with_database", interact_with_database)
    main_action_registry.register_action("perform_complex_data_analysis", perform_complex_data_analysis)
    
    # Meta/System Tools
    main_action_registry.register_action("invoke_spr", invoke_spr_action)
    main_action_registry.register_action("self_interrogate", self_interrogate)
    main_action_registry.register_action("system_genesis", perform_system_genesis_action)
    main_action_registry.register_action("run_code_linter", run_code_linter)
    main_action_registry.register_action("run_workflow_suite", run_workflow_suite)
    main_action_registry.register_action("run_predictive_flux_coupling", run_predictive_flux_coupling)

    # Gemini Enhanced Tools (if available)
    if GEMINI_TOOLS_AVAILABLE:
        main_action_registry.register_action("execute_gemini_code", execute_gemini_code)
        main_action_registry.register_action("process_gemini_file", process_gemini_file)
        main_action_registry.register_action("generate_with_grounding", generate_with_grounding)
        main_action_registry.register_action("generate_with_function_calling", generate_with_function_calling)
        main_action_registry.register_action("generate_with_structured_output", generate_with_structured_output)
        logger.info("Gemini Enhanced Tools have been registered.")
    else:
        logger.warning("Skipping registration of Gemini Enhanced Tools as they are not available.")
        
    logger.info(f"Action registry populated. Total actions: {len(main_action_registry.actions)}.")

# Populate the registry when the module is loaded
populate_main_registry()


# The old execute_action function can be deprecated or refactored to use the registry.
# For now, we will leave it to avoid breaking other parts of the system that might call it directly.
# A future refactoring task under CRDSP would be to unify all action execution through the registry.
def execute_action(
    task_key: str, 
    action_name: str, 
    action_type: str, 
    inputs: Dict[str, Any],
    context_for_action: ActionContext,
    max_attempts: int = 1,
    attempt_number: int = 1
) -> Dict[str, Any]:
    """
    Main entry point for executing an action.
    This function will now use the main_action_registry.
    """
    logger.debug(f"Executing action via legacy entrypoint: type='{action_type}', name='{action_name}'")
    
    # The action_type is the key for the registry
    action_to_run = main_action_registry.get_action(action_type)
    
    if not action_to_run:
        msg = f"Action type '{action_type}' not found in main_action_registry."
        logger.error(msg)
        return handle_action_error(action_type, ValueError(msg), inputs)

    try:
        # Start timer for execution metrics
        start_time = time.time()
        
        # Execute the action function from the registry
        result = action_to_run(inputs)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # --- IAR Compliance Vetting ---
        if 'reflection' not in result or not isinstance(result['reflection'], dict):
            logger.critical(f"ACTION '{action_type}' FAILED IAR COMPLIANCE: Missing or invalid 'reflection'.")
            # Create a failure reflection
            failure_reflection = _create_reflection(
                "Critical Failure",
                "Action failed IAR compliance vetting: 'reflection' object was missing or invalid.",
                0.0,
                "Non-Compliant",
                ["IAR_COMPLIANCE_VIOLATION"],
                result.get("result", result.get("error"))
            )
            result['reflection'] = failure_reflection
            result['error'] = result.get('error', "IAR Compliance Violation")

        # Log execution metrics
        logger.info(f"Action '{action_type}' completed in {duration:.4f} seconds.")
        
        return result
        
    except Exception as e:
        logger.error(f"Critical error during execution of action '{action_type}': {e}", exc_info=True)
        return handle_action_error(action_type, e, inputs)

# --- DEPRECATED ---
def register_action(action_type: str, function: Callable[[Dict[str, Any]], Dict[str, Any]], force: bool = False):
    """This function is deprecated. Use main_action_registry.register_action() instead."""
    logger.warning("The standalone 'register_action' function is deprecated. Use main_action_registry.register_action().")
    main_action_registry.register_action(action_type, function) 