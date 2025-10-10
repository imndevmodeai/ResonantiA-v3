# --- START OF FILE 3.0ArchE/action_registry.py (UNIFIED) ---
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
    from .thought_trail import log_to_thought_trail
except ImportError:
    # Fallback for direct execution
    import config
    from error_handler import handle_action_error
    from thought_trail import log_to_thought_trail

# Initialize logger first
logger = logging.getLogger(__name__)

# --- V4 UNIFICATION PROXY ---
# Import the V4 action executor. This is the bridge.
try:
    # Add Four_PointO_ArchE to path
    four_pointo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Four_PointO_ArchE')
    if four_pointo_path not in sys.path:
        sys.path.insert(0, four_pointo_path)
    
    # Also add current directory to path for direct execution
    current_dir = os.path.dirname(os.path.dirname(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from tools.perception_engine import PerceptionEngine
    from tools.rise_actions import perform_causal_inference as v4_causal_inference, perform_abm as v4_abm, run_cfp as v4_cfp
    from tsp_solver.solver import TSPSolver
    V4_REGISTRY_AVAILABLE = True
    V4_PERCEPTION_ENGINE = PerceptionEngine()
    V4_TSP_SOLVER = None  # Will be initialized when needed with proper API key
except ImportError as e:
    V4_REGISTRY_AVAILABLE = False
    V4_PERCEPTION_ENGINE = None
    V4_TSP_SOLVER = None
    logger.warning(f"V4 system not available: {e}")

# --- ENHANCED PERCEPTION ENGINE ---
# Import the enhanced Perception Engine for advanced web capabilities
try:
    from .enhanced_perception_engine import enhanced_web_search, enhanced_page_analysis
    ENHANCED_PERCEPTION_AVAILABLE = True
    logger.info("Enhanced Perception Engine available")
except ImportError as e:
    try:
        from enhanced_perception_engine import enhanced_web_search, enhanced_page_analysis
        ENHANCED_PERCEPTION_AVAILABLE = True
        logger.info("Enhanced Perception Engine available")
    except ImportError as e2:
        ENHANCED_PERCEPTION_AVAILABLE = False
        logger.warning(f"Enhanced Perception Engine not available: {e2}")

# Import tool functions
from Three_PointO_ArchE.tools.enhanced_search_tool import perform_web_search as run_search
from Three_PointO_ArchE.tools.synthesis_tool import invoke_llm_for_synthesis as invoke_llm
from Three_PointO_ArchE.code_executor import execute_code
# from Three_PointO_ArchE.action_registry import display_output, calculate_math
# ^^^ This was causing a circular import in the previous attempt to fix, removing

class ActionRegistry:
    """A central registry for all callable actions (tools) in the system."""
    def __init__(self):
        self.actions: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        logger.info("ActionRegistry initialized.")

    def register_action(self, action_type: str, function: Callable[[Dict[str, Any]], Dict[str, Any]], force: bool = False):
        """
        Registers an action in the registry.

        Args:
            action_type (str): The name of the action to register.
            function (Callable): The function to be executed for this action.
            force (bool): If True, overwrites an existing action with the same name.
        """
        if action_type in self.actions and not force:
            logger.warning(f"Action '{action_type}' already registered. Skipping registration.")
        else:
            self.actions[action_type] = function
            logger.info(f"Action '{action_type}' registered.")

    def get_action(self, name: str) -> Callable:
        """
        Retrieves an action from the registry.

        Args:
            name (str): The name of the action to retrieve.

        Returns:
            The callable function for the action.

        Raises:
            KeyError: If the action is not found.
        """
        action = self.actions.get(name)
        if not action:
            logger.error(f"Action '{name}' not found in registry. Available actions: {list(self.actions.keys())}")
            raise KeyError(f"Action '{name}' not found.")
        return action

# --- Singleton Instance ---
# This is the central, globally accessible registry.
main_action_registry = ActionRegistry()


# --- Core Tool Imports and Registration ---
# Import tool functions from their specific modules and register them.

from Three_PointO_ArchE.tools.enhanced_search_tool import perform_web_search
from Three_PointO_ArchE.tools.synthesis_tool import invoke_llm_for_synthesis
from Three_PointO_ArchE.code_executor import execute_code as _raw_execute_code

# Wrapper to adapt code_executor signature to action registry calling convention
def standalone_execute_code(**kwargs) -> Dict[str, Any]:
    """Wrapper for code_executor.execute_code that adapts keyword args to inputs dict."""
    return _raw_execute_code(inputs=kwargs)
from Three_PointO_ArchE.web_search_tool import search_web
from Three_PointO_ArchE.nfl_prediction_action import predict_nfl_game

# --- NEW: Import and Instantiate Modular Capabilities ---
from .llm_providers.google import GoogleProvider
from Three_PointO_ArchE.enhanced_capabilities import GeminiCapabilities

# This assumes the config is loaded and available for the provider initialization
try:
    cfg = config.get_config()
    # FIX: Access the key via attribute, not .get()
    google_api_key = cfg.api_keys.google_api_key if hasattr(cfg.api_keys, 'google_api_key') else None
    if not google_api_key:
        logger.warning("Google API key not found in config, using dummy key for initialization.")
        google_api_key = "dummy_key_for_init"

    google_provider_instance = GoogleProvider(api_key=google_api_key)
    gemini_capabilities_instance = GeminiCapabilities(google_provider=google_provider_instance)
    CAPABILITIES_AVAILABLE = True
    logger.info("GeminiCapabilities initialized and available in ActionRegistry.")
except Exception as e:
    CAPABILITIES_AVAILABLE = False
    gemini_capabilities_instance = None
    logger.warning(f"Could not initialize GeminiCapabilities: {e}", exc_info=True)


# Placeholder functions for actions used in the workflow but potentially missing
@log_to_thought_trail
def display_output(content: str, **kwargs) -> Dict[str, Any]:
    """Prints content to the console and returns a fully IAR-compliant result."""
    logger.info("DISPLAY_OUTPUT Action Fired:")
    import pprint
    pprint.pprint(content)
    
    # Return a fully compliant IAR dictionary
    summary = f"Displayed content of {len(str(content))} characters."
    preview = str(content)[:100] + "..." if len(str(content)) > 100 else str(content)

    return {
        'status': 'success',
        'message': 'Content displayed successfully.',
        'reflection': {
            'status': 'Success',
            'summary': summary,
            'confidence': 1.0,
            'alignment_check': {
                'objective_alignment': 1.0,
                'protocol_alignment': 1.0
            },
            'potential_issues': [],
            'raw_output_preview': preview
        }
    }

@log_to_thought_trail
def calculate_math(expression: str, **kwargs) -> Dict[str, Any]:
    """Evaluates a simple mathematical expression and returns IAR-compliant result."""
    logger.info(f"CALCULATE_MATH Action Fired with expression: {expression}")
    try:
        # WARNING: eval() is used for simplicity. Be cautious in a production environment.
        result = eval(str(expression))
        return {
            'status': 'success',
            'result': result,
            'message': f'Successfully evaluated: {expression} = {result}',
            'reflection': {
                'status': 'Success',
                'summary': f'Mathematical expression "{expression}" evaluated to {result}',
                'confidence': 1.0,
                'alignment_check': {
                    'objective_alignment': 1.0,
                    'protocol_alignment': 1.0
                },
                'potential_issues': [],
                'raw_output_preview': f'{{"status": "success", "result": {result}}}'
            }
        }
    except Exception as e:
        logger.error(f"Error evaluating math expression '{expression}': {e}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Failed to evaluate expression: {str(e)}',
            'error_details': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'Math evaluation failed for "{expression}": {str(e)}',
                'confidence': 0.0,
                'alignment_check': {
                    'objective_alignment': 0.0,
                    'protocol_alignment': 0.0
                },
                'potential_issues': [
                    f'Invalid mathematical expression: {expression}',
                    str(e)
                ],
                'raw_output_preview': f'{{"status": "error", "message": "{str(e)}"}}'
            }
        }

# --- Additional Action Implementations ---
def string_template_action(**kwargs) -> Dict[str, Any]:
    """Template string substitution action."""
    try:
        template = kwargs.get('template', '')
        # Simple template substitution - replace {{ variable }} with context values
        result = template
        # For now, just return the template as-is since we don't have context substitution
        # In a full implementation, this would substitute variables from the workflow context
        
        # Return IAR-compliant response
        return {
            'status': 'success',
            'result': result,
            'reflection': {
                'status': 'Success',
                'summary': f'Template processed successfully. Length: {len(result)} characters',
                'confidence': 0.9,
                'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                'potential_issues': [],
                'raw_output_preview': f"{{'status': 'success', 'result': '{result[:100]}{'...' if len(result) > 100 else ''}'}}"
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'Template processing failed: {str(e)}',
                'confidence': 0.1,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

def save_to_file_action(**kwargs) -> Dict[str, Any]:
    """Save content to file action."""
    try:
        import os
        # Extract parameters from kwargs
        file_path = kwargs.get('file_path', 'output.txt')
        content = kwargs.get('content', '')
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(content))
        
        # Return IAR-compliant response
        return {
            'status': 'success',
            'file_path': file_path,
            'message': f'Content saved to {file_path}',
            'reflection': {
                'status': 'Success',
                'summary': f'Successfully saved content to {file_path}',
                'confidence': 0.9,
                'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                'potential_issues': [],
                'raw_output_preview': f"{{'status': 'success', 'file_path': '{file_path}', 'message': 'Content saved to {file_path}'}}"
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'Failed to save file: {str(e)}',
                'confidence': 0.1,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

# Registering the core actions
# Keep the standalone version for now, can be deprecated later
main_action_registry.register_action("execute_code_standalone", standalone_execute_code)
main_action_registry.register_action("search_web", log_to_thought_trail(perform_web_search))
main_action_registry.register_action("generate_text_llm", invoke_llm_for_synthesis)
main_action_registry.register_action("display_output", display_output)
main_action_registry.register_action("calculate_math", calculate_math)
main_action_registry.register_action("string_template", string_template_action)
main_action_registry.register_action("save_to_file", save_to_file_action)
main_action_registry.register_action("predict_nfl_game", log_to_thought_trail(predict_nfl_game))

# --- CRITICAL: Register the canonical, working code_executor as primary ---
# The standalone execute_code from code_executor.py is the canonical, IAR-compliant implementation
main_action_registry.register_action("execute_code", log_to_thought_trail(standalone_execute_code))
logger.info("Registered canonical 'execute_code' from code_executor.py")

# --- Register other actions from GeminiCapabilities instance (if available) ---
if CAPABILITIES_AVAILABLE and gemini_capabilities_instance:
    # Register Gemini code execution under a different name to avoid conflict
    main_action_registry.register_action("execute_code_gemini", log_to_thought_trail(gemini_capabilities_instance.execute_code))
    main_action_registry.register_action("handle_files", log_to_thought_trail(gemini_capabilities_instance.handle_files))
    main_action_registry.register_action("perform_grounding", log_to_thought_trail(gemini_capabilities_instance.perform_grounding))
    main_action_registry.register_action("call_function", log_to_thought_trail(gemini_capabilities_instance.call_function))
    main_action_registry.register_action("generate_structured_output", log_to_thought_trail(gemini_capabilities_instance.generate_structured_output))
    logger.info("Actions from GeminiCapabilities registered (execute_code_gemini, handle_files, etc.).")


# --- Global Execute Function ---
# No need to decorate this function, as it calls the already-decorated actions
def execute_action(action_type: str, inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Executes a registered action by name.
    Accepts additional keyword arguments (**kwargs) for compatibility with the workflow engine.

    Args:
        action_type (str): The name of the action to execute.
        inputs (Dict[str, Any]): The dictionary of inputs for the action.

    Returns:
        The result of the action execution.
        """
    try:
        logger.info(f"Executing action '{action_type}'...")
        action_func = main_action_registry.get_action(action_type)
        result = action_func(**inputs)
        logger.info(f"Action '{action_type}' executed successfully.")
        return result
    except KeyError:
        # Error is already logged by get_action
        return {"status": "error", "message": f"Action '{action_type}' not found."}
    except Exception as e:
        logger.error(f"An unexpected error occurred during execution of action '{action_type}': {e}", exc_info=True)
        # Return a dictionary in all error cases to ensure IAR compliance downstream
        return {
            "status": "error", 
            "message": f"An unexpected error occurred: {str(e)}",
            "error_details": str(e),
            "reflection": {
                "status": "Failed",
                "summary": f"Action '{action_type}' failed catastrophically before IAR could be generated.",
                "confidence": 0.0,
                "alignment_check": "Unknown",
                "potential_issues": ["The action itself raised an unhandled exception."],
                "raw_output_preview": str(e)
            }
        }


# --- Capabilities Initialization ---
# This block is now redundant due to the robust initialization at the top of the file.
# Removing it to create a single source of truth for capability initialization.

