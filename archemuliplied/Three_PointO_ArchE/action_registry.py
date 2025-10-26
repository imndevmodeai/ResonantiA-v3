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
from .utils.reflection_utils import create_reflection, ExecutionStatus

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
from .tools.codebase_search_tool import search_codebase as search_codebase_action
from .tools.navigate_web import navigate_web
from .spr_action_bridge import invoke_spr, SPRBridgeLoader
from .predictive_flux_coupling_engine import run_predictive_flux_analysis
from .llm_providers import get_llm_provider, get_model_for_provider, LLMProviderError

# Capability functions are optional; guard import for runtime resilience
try:
    from .capability_functions import (
        workflow_debugging,
        implementation_resonance,
        strategic_to_tactical,
        iterative_refinement,
        solution_crystallization,
    )
    CAPABILITY_FUNCS_AVAILABLE = True
except Exception as e:
    logger.warning(
        "Optional capability_functions not available; skipping registration. Error: %s",
        getattr(e, "message", str(e)),
    )
    CAPABILITY_FUNCS_AVAILABLE = False

# Define display_output function directly
def display_output(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Display output content."""
    content = inputs.get('content', '')
    print(f"[DISPLAY] {content}")
    return {
        "output": content,
        "reflection": {
            "status": "success",
            "message": "Content displayed successfully"
        }
    }

def perform_causal_inference_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper that unpacks dict inputs for causal tool (expects kwargs)."""
    try:
        # Normalize 'data' input: allow JSON string, and unwrap top-level {"data": {...}}
        data = inputs.get("data")
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                if isinstance(parsed, dict):
                    # If loader produced {"data": {...}}, unwrap to inner dict
                    if "data" in parsed and isinstance(parsed["data"], dict):
                        inputs = {**inputs, "data": parsed["data"]}
                    else:
                        inputs = {**inputs, "data": parsed}
            except Exception:
                # keep original string if it isn't JSON
                pass
        return perform_causal_inference(**inputs)
    except TypeError as e:
        return handle_action_error(
            "perform_causal_inference",
            "perform_causal_inference",
            {"error": f"Invalid inputs for causal inference: {e}"},
            inputs,
            1,
        )

    # --- Gemini Enhanced Tools Initialization ---
    # gemini_tool_suite = None
    # GEMINI_TOOLS_AVAILABLE = False
    #
    # try:
    #     from .gemini_enhanced_tools import (
    #         execute_gemini_code,
    #         process_gemini_file,
    #         generate_with_grounding,
    #         generate_with_function_calling,
    #         generate_with_structured_output
    #     )
    #     GEMINI_TOOLS_AVAILABLE = True
    #     logger.info("Gemini Enhanced Tools loaded successfully.")
    # except ImportError as e:
    #     logger.warning(f"Gemini Enhanced Tool Suite could not be initialized: {e}")
    #     GEMINI_TOOLS_AVAILABLE = False

# --- Action Registry Class ---
class ActionRegistry:
    """Central registry for all available actions in the ArchE system."""
    
    def __init__(self):
        self.actions: Dict[str, Callable] = {}
        self.action_metadata: Dict[str, Dict[str, Any]] = {}
        logger.info("ActionRegistry initialized.")

    def register_action(self, action_name: str, action_func: Callable, force: bool = False) -> None:
        """Register an action function with the registry."""
        if action_name in self.actions and not force:
            logger.warning(f"Action '{action_name}' is being overwritten in the registry.")
        
        self.actions[action_name] = action_func
        self.action_metadata[action_name] = {
            "function": action_func.__name__,
            "module": action_func.__module__,
            "registered_at": time.time()
        }
        logger.debug(f"Registered action: {action_name} -> {action_func.__name__}")

    def get_action(self, action_name: str) -> Optional[Callable]:
        """Get an action function by name."""
        return self.actions.get(action_name)

    def list_actions(self) -> List[str]:
        """List all registered action names."""
        return list(self.actions.keys())
    
    def get_action_metadata(self, action_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific action."""
        return self.action_metadata.get(action_name)
    
    def validate_action(self, action_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that an action can be executed with the given inputs."""
        action_func = self.get_action(action_name)
        if not action_func:
            return {
                "valid": False,
                "error": f"Action '{action_name}' not found in registry",
                "available_actions": self.list_actions()
            }
        
        # Basic validation - check if function signature can accept the inputs
        try:
            sig = inspect.signature(action_func)
            sig.bind(**inputs)
            return {"valid": True, "action": action_name}
        except Exception as e:
            return {
                "valid": False,
                "error": f"Input validation failed for action '{action_name}': {e}",
                "expected_signature": str(sig)
            }

# --- Global Registry Instance ---
# Singleton instance of the ActionRegistry
main_action_registry = ActionRegistry()

def populate_main_registry():
    """Registers all standard and enhanced actions into the main registry."""
    logger.info("Populating the main action registry...")
    
    # Standard Tools
    main_action_registry.register_action("list_directory", list_directory)
    main_action_registry.register_action("read_file", read_file)
    main_action_registry.register_action("create_file", create_file)
    main_action_registry.register_action("run_cfp", run_cfp_action)
    main_action_registry.register_action("search_web", search_web)
    main_action_registry.register_action("search_codebase", search_codebase_action)
    main_action_registry.register_action("navigate_web", navigate_web)
    main_action_registry.register_action("generate_text", generate_text_llm)
    main_action_registry.register_action("generate_text_llm", generate_text_llm)
    main_action_registry.register_action("execute_code", execute_code)
    main_action_registry.register_action("perform_causal_inference", perform_causal_inference_action)
    main_action_registry.register_action("perform_abm", perform_abm)
    main_action_registry.register_action("run_prediction", run_prediction)
    main_action_registry.register_action("causal_inference_tool", perform_causal_inference)
    main_action_registry.register_action("agent_based_modeling_tool", perform_abm)
    main_action_registry.register_action("invoke_specialist_agent", invoke_specialist_agent_action)
    main_action_registry.register_action("predictive_modeling_tool", run_prediction)
    main_action_registry.register_action("call_api", call_api)
    main_action_registry.register_action("interact_with_database", interact_with_database)
    main_action_registry.register_action("perform_complex_data_analysis", perform_complex_data_analysis)
    main_action_registry.register_action("display_output", display_output)
    
    # Meta/System Tools
    main_action_registry.register_action("invoke_spr", invoke_spr_action)
    main_action_registry.register_action("self_interrogate", self_interrogate)
    main_action_registry.register_action("system_genesis", perform_system_genesis_action)
    main_action_registry.register_action("run_code_linter", run_code_linter)
    main_action_registry.register_action("run_workflow_suite", run_workflow_suite)
    main_action_registry.register_action("run_predictive_flux_coupling", run_predictive_flux_analysis)
    main_action_registry.register_action("invoke_llm", invoke_llm_action)
    main_action_registry.register_action("synthesize_final_output", synthesize_final_output_action)
    
    # Base64 tools for robust data handling
    main_action_registry.register_action("encode_base64", encode_base64)
    main_action_registry.register_action("decode_base64_and_write_file", decode_base64_and_write_file)
    
    # Capability Functions
    if CAPABILITY_FUNCS_AVAILABLE:
        main_action_registry.register_action("workflow_debugging", workflow_debugging)
        main_action_registry.register_action("implementation_resonance", implementation_resonance)
        main_action_registry.register_action("strategic_to_tactical", strategic_to_tactical)
        main_action_registry.register_action("iterative_refinement", iterative_refinement)
        main_action_registry.register_action("solution_crystallization", solution_crystallization)
    else:
        logger.info("Capability functions not registered (module missing).")

    # Gemini Enhanced Tools (if available)
    # if GEMINI_TOOLS_AVAILABLE:
    #     main_action_registry.register_action("execute_gemini_code", execute_gemini_code)
    #     main_action_registry.register_action("process_gemini_file", process_gemini_file)
    #     main_action_registry.register_action("generate_with_grounding", generate_with_grounding)
    #     main_action_registry.register_action("generate_with_function_calling", generate_with_function_calling)
    #     main_action_registry.register_action("generate_with_structured_output", generate_with_structured_output)
    #     logger.info("Gemini Enhanced Tools have been registered.")
    # else:
    #     logger.warning("Skipping registration of Gemini Enhanced Tools as they are not available.")
        
    logger.info(f"Action registry populated. Total actions: {len(main_action_registry.actions)}.")

def register_action(action_name: str, action_func: Callable, force: bool = False) -> None:
    """Module-level helper to register an action into the main registry."""
    main_action_registry.register_action(action_name, action_func, force=force)

def execute_action(
    *,
    task_key: str,
    action_name: str,
    action_type: str,
    inputs: Dict[str, Any],
    context_for_action: ActionContext,
    max_attempts: int = 1,
    attempt_number: int = 1,
) -> Dict[str, Any]:
    """
    Executes a registered action with engine-provided context. Signature matches engine calls.
    Performs a single attempt; engine oversees retries.
    """
    action_func = main_action_registry.get_action(action_type)
    if action_func is None:
        logger.error(f"Unknown action type: {action_type}")
        return {
            "error": f"Unknown action type: {action_type}",
            "reflection": {
                "status": "error",
                "message": f"Action '{action_type}' not found in registry",
                "confidence": 0.0
            }
        }
    try:
        call_inputs = inputs if isinstance(inputs, dict) else {}
        # Adapt call based on action function signature (supports engine-bound methods)
        try:
            sig = inspect.signature(action_func)
            if 'context_for_action' in sig.parameters:
                result = action_func(call_inputs, context_for_action)
            else:
                result = action_func(call_inputs)
        except Exception:
            # Fallback to simplest call
            result = action_func(call_inputs)
        if not isinstance(result, dict):
            result = {"result": result}
        # annotate minimal execution metadata
        result.setdefault("reflection", {
            "status": "success",
            "message": f"Action '{action_type}' executed (task '{task_key}', attempt {attempt_number}/{max_attempts})",
            "confidence": 1.0
        })
        # --- Terminal echo: print concise action output preview ---
        try:
            echo_enabled = True  # could be toggled via env later
            if echo_enabled:
                refl = result.get("reflection", {}) or {}
                status = str(refl.get("status", "?"))
                conf = refl.get("confidence")
                conf_str = f"{conf:.2f}" if isinstance(conf, (int, float)) else str(conf)
                print(f"[ACTION {action_type}] status={status} confidence={conf_str}")
                # Common shapes
                payload = result.get("result") if isinstance(result.get("result"), dict) else result
                # search_web: payload.results
                if isinstance(payload, dict) and isinstance(payload.get("results"), list):
                    items = payload.get("results")
                    print(f"[ACTION {action_type}] results={len(items)}")
                    for i, it in enumerate(items[:3]):
                        title = it.get("title") or it.get("body") or it.get("description") or "(no title)"
                        link = it.get("url") or it.get("href") or it.get("link") or ""
                        print(f"  {i+1}. {title[:120]}\n     {link}")
                # navigate_web: show title/selection
                elif isinstance(result, dict) and any(k in result for k in ("title", "selection")):
                    title = result.get("title")
                    selection = result.get("selection")
                    if title:
                        print(f"[navigate_web] title: {str(title)[:160]}")
                    if selection:
                        snip = selection if isinstance(selection, str) else str(selection)
                        print(f"[navigate_web] selection: {snip[:200]}")
                # generic: output/content
                else:
                    out = result.get("output") or result.get("content")
                    if out:
                        text = out if isinstance(out, str) else str(out)
                        print(text[:400])
        except Exception:
            # Do not fail action on echo issues
            pass
        return result
    except Exception as e:
        logger.exception(
            f"Exception during action '{action_type}' (task '{task_key}', attempt {attempt_number}/{max_attempts})"
        )
        context_payload = context_for_action.__dict__ if hasattr(context_for_action, '__dict__') else {}
        return handle_action_error(task_key, action_type, {"error": str(e)}, context_payload, attempt_number)

# --- Action Wrapper Functions ---
def list_directory(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """List directory contents."""
    path = inputs.get("path", ".")
    action_name = "list_directory"
    try:
        contents = os.listdir(path)
        return {
            "result": {"contents": contents, "path": path},
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.SUCCESS,
                message=f"Successfully listed directory: {path}",
                inputs=inputs,
                outputs={"file_count": len(contents)},
                confidence=1.0
            )
        }
    except Exception as e:
        error_msg = f"Error listing directory '{path}': {str(e)}"
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.FAILURE,
                message=error_msg,
                inputs=inputs,
                potential_issues=[type(e).__name__]
            )
        }



def create_file(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new file with specified content."""
    file_path = inputs.get("file_path")
    content = inputs.get("content", "")
    action_name = "create_file"
    
    if not file_path:
        return {
            "error": "No file_path provided.",
            "reflection": create_reflection(
                action_name=action_name, status=ExecutionStatus.FAILURE,
                message="Input validation failed: 'file_path' is required.",
                inputs=inputs
            )
        }
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        outputs = {
            "file_path": file_path,
            "content_length": len(content),
            "created": True
        }
        return {
            "result": outputs,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.SUCCESS,
                message=f"Successfully created file: {file_path}",
                inputs=inputs,
                outputs=outputs,
                confidence=1.0
            )
        }
    except Exception as e:
        error_msg = f"Error creating file: {str(e)}"
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.CRITICAL_FAILURE,
                message=error_msg,
                inputs=inputs,
                potential_issues=[type(e).__name__]
            )
        }

def read_file(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Read file contents."""
    file_path = inputs.get("file_path")
    action_name = "read_file"

    if not file_path:
        return {
            "error": "No file_path provided.",
            "reflection": create_reflection(
                action_name=action_name, status=ExecutionStatus.FAILURE,
                message="Input validation failed: 'file_path' is required.",
                inputs=inputs
            )
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "result": {
                "content": content,
                "file_path": file_path,
                "file_size": len(content),
            },
            "reflection": create_reflection(
                action_name=action_name, status=ExecutionStatus.SUCCESS,
                message=f"Successfully read file: {file_path}",
                inputs=inputs,
                outputs={"content_length": len(content)},
                confidence=1.0
            )
        }
    except FileNotFoundError:
        error_msg = f"File not found: {file_path}"
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name=action_name, status=ExecutionStatus.FAILURE,
                message=error_msg,
                inputs=inputs,
                potential_issues=["FileNotFound"]
            )
        }
    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name=action_name, status=ExecutionStatus.CRITICAL_FAILURE,
                message=error_msg,
                inputs=inputs,
                potential_issues=[type(e).__name__]
            )
        }

def run_cfp_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Run CFP (Complex Framework Processing) analysis."""
    try:
        cfp = CfpframeworK()
        result = cfp.analyze(inputs.get("data", {}))
        return {
            "results": result,
            "reflection": {
                "status": "success",
                "message": "CFP analysis completed successfully",
                "confidence": 0.85
            }
        }
    except Exception as e:
        return handle_action_error("run_cfp", "run_cfp", {"error": str(e)}, inputs, 1)

def invoke_llm_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Action wrapper for invoking LLM providers.
    Handles provider selection, model resolution, and error handling.
    """
    provider_name = inputs.get("provider") # Uses default from config if None
    model_name_override = inputs.get("model")
    prompt = inputs.get("prompt")
    messages = inputs.get("messages")

    if not prompt and not messages:
        return handle_action_error("invoke_llm", "invoke_llm", {"error": "Missing 'prompt' or 'messages' input."}, inputs, 1)

    try:
        # Get the correct, initialized provider instance
        provider = get_llm_provider(provider_name)
        # Determine the final model name to use
        model_to_use = model_name_override or get_model_for_provider(provider._provider_name)

        # Get other parameters
        max_tokens = inputs.get("max_tokens", config.LLM_DEFAULT_MAX_TOKENS)
        temperature = inputs.get("temperature", config.LLM_DEFAULT_TEMP)
        
        # Force chat-style generation for more direct textual responses
        if prompt:
             messages = [{"role": "user", "content": prompt}]
        
        response_obj = provider.generate_chat(messages, model_to_use, max_tokens, temperature)

        # Robustly extract text from the response object
        if isinstance(response_obj, dict) and 'text' in response_obj:
            response_text = response_obj['text']
        elif isinstance(response_obj, str):
            response_text = response_obj
        else:
            response_text = str(response_obj)

        return {
            "response": response_text,
            "reflection": {
                "status": "success",
                "message": f"LLM invoked successfully using provider '{provider._provider_name}' and model '{model_to_use}'.",
                "confidence": 0.95
            }
        }
    except (ValueError, LLMProviderError) as e:
        logger.error(f"LLM invocation failed: {e}", exc_info=True)
        return handle_action_error("invoke_llm", "invoke_llm", {"error": f"LLMProviderError: {e}"}, inputs, 1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during LLM invocation: {e}", exc_info=True)
        return handle_action_error("invoke_llm", "invoke_llm", {"error": f"Unexpected LLM Error: {e}"}, inputs, 1)


def synthesize_final_output_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes structured analysis data and synthesizes a final, human-readable conclusion.
    """
    analysis_data = inputs.get("analysis_data")
    if not analysis_data:
        return handle_action_error("synthesize_final_output", "synthesize_final_output", {"error": "Missing 'analysis_data' input."}, inputs, 1)

    try:
        # The input is a dictionary containing the results of the causal analysis.
        if "error" in analysis_data:
            return handle_action_error("synthesize_final_output", "synthesize_final_output", {"error": f"Upstream analysis failed: {analysis_data['error']}"}, inputs, 1)
        
        # Handle the output of 'train_and_predict'
        if "feature_importance" in analysis_data:
            importances = analysis_data["feature_importance"]
            primary_driver = max(importances, key=lambda k: abs(importances[k]))
            effect_value = importances[primary_driver]

            final_sentence = f"Based on the predictive model, the factor with the highest impact on customer churn is '{primary_driver}' (importance score: {effect_value:.4f}). A proposed retention strategy is to focus on this area. For instance, if the driver is 'on_time_payment_percentage', implementing flexible payment reminders or small incentives for consistent on-time payments could significantly improve customer retention."

        # Handle the output of 'estimate_average_treatment_effect'
        elif "estimated_effects" in analysis_data:
            effects = analysis_data["estimated_effects"]
            # Find the variable with the largest absolute effect
            primary_driver = max(effects, key=lambda k: abs(effects[k]))
            effect_value = effects[primary_driver]
            
            final_sentence = f"Based on the causal analysis, the variable '{primary_driver}' has the most significant causal effect on churn (coefficient: {effect_value:.4f}). A proposed retention strategy would be to focus interventions on this factor. For example, if the driver is 'service_calls', a proactive maintenance program could be implemented to reduce service incidents and improve customer satisfaction."
        else:
            # Fallback for other or unexpected structures
            variable = analysis_data.get("variable", "N/A")
            effect = analysis_data.get("effect", "N/A")
            if variable == "N/A":
                 final_sentence = "The causal analysis was inconclusive and no single significant variable was identified."
            else:
                 final_sentence = f"Based on the causal analysis, the variable '{variable}' has the most significant effect ({effect}). A proposed intervention would be to directly address or modify the factors contributing to this variable to influence the desired outcome."

        return {
            "response": final_sentence,
            "reflection": {
                "status": "success",
                "message": "Successfully synthesized final output.",
                "confidence": 1.0
            }
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred during final synthesis: {e}", exc_info=True)
        return handle_action_error("synthesize_final_output", "synthesize_final_output", {"error": f"Unexpected Synthesis Error: {e}"}, inputs, 1)


def invoke_spr_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for invoke_spr action."""
    try:
        logger.info(f"Executing invoke_spr action with inputs: {inputs}")
        result = invoke_spr(inputs)
        logger.info(f"invoke_spr action completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error in invoke_spr action: {e}", exc_info=True)
        return handle_action_error("invoke_spr", "invoke_spr", {"error": str(e)}, inputs, 1)

def invoke_specialist_agent_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for invoke_specialist_agent action."""
    try:
        logger.info(f"Executing invoke_specialist_agent action with inputs: {inputs}")
        
        # Extract inputs
        specialized_agent = inputs.get("specialized_agent", {})
        task_prompt = inputs.get("task_prompt", "")
        context_injection = inputs.get("context_injection", {})
        response_format = inputs.get("response_format", "structured_analysis")
        
        # Validate inputs
        if not specialized_agent:
            return {
                "error": "Missing specialized_agent input",
                "reflection": {
                    "status": "failure",
                    "message": "Specialized agent not provided"
                }
            }
        
        if not task_prompt:
            return {
                "error": "Missing task_prompt input", 
                "reflection": {
                    "status": "failure",
                    "message": "Task prompt not provided"
                }
            }
        
        # Create specialist consultation context
        consultation_context = {
            "agent_profile": specialized_agent,
            "task": task_prompt,
            "knowledge_base": context_injection,
            "response_format": response_format
        }
        
        # Use the LLM tool to simulate specialist consultation
        specialist_prompt = f"""🎭 **Specialist Agent Consultation**

You are now embodying the specialized agent with the following profile:
{json.dumps(specialized_agent, indent=2)}

**Task:** {task_prompt}

**Available Knowledge Base:**
{json.dumps(context_injection, indent=2)}

**Response Format:** {response_format}

Provide your expert analysis in the specialized agent's voice and style, drawing upon your domain expertise and the provided knowledge base."""

        # Execute specialist consultation using LLM
        llm_result = generate_text_llm({
            "prompt": specialist_prompt,
            "model": "gemini-1.5-pro-latest",
            "temperature": 0.4,
            "max_tokens": 3000
        })
        
        result = {
            "results": llm_result.get("output", "Specialist consultation completed"),
            "specialist_profile": specialized_agent,
            "consultation_context": consultation_context,
            "reflection": {
                "status": "success",
                "message": "Specialist agent consultation completed successfully"
            }
        }
        
        logger.info(f"invoke_specialist_agent action completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error in invoke_specialist_agent action: {e}", exc_info=True)
        return handle_action_error("invoke_specialist_agent", "invoke_specialist_agent", {"error": str(e)}, inputs, 1)

# --- Base64 Tool Implementations ---
import base64

def encode_base64(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Encodes a string to Base64."""
    content = inputs.get("content")
    if content is None:
        return handle_action_error("encode_base64", "encode_base64", {"error": "No content provided"}, inputs, 1)
    try:
        if not isinstance(content, str):
            content = str(content)
        
        content_bytes = content.encode('utf-8')
        encoded_bytes = base64.b64encode(content_bytes)
        encoded_string = encoded_bytes.decode('utf-8')
        
        return {
            "result": {"encoded_content": encoded_string},
            "reflection": {
                "status": "success",
                "message": f"Successfully encoded content (length: {len(content)} -> {len(encoded_string)}).",
                "confidence": 1.0
            }
        }
    except Exception as e:
        return handle_action_error("encode_base64", "encode_base64", {"error": f"Error encoding to Base64: {str(e)}"}, inputs, 1)

def decode_base64_and_write_file(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Decodes a Base64 string and writes it to a file."""
    encoded_content = inputs.get("encoded_content")
    file_path = inputs.get("file_path")

    if not encoded_content or not file_path:
        return handle_action_error("decode_base64_and_write_file", "decode_base64_and_write_file", {"error": "Missing encoded_content or file_path"}, inputs, 1)

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        decoded_bytes = base64.b64decode(encoded_content)
        decoded_string = decoded_bytes.decode('utf-8')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(decoded_string)
            
        return {
            "result": {
                "file_path": file_path,
                "content_length": len(decoded_string),
                "status": "File written successfully."
            },
            "reflection": {
                "status": "success",
                "message": f"Successfully decoded and wrote to file: {file_path}",
                "confidence": 1.0
            }
        }
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        return handle_action_error("decode_base64_and_write_file", "decode_base64_and_write_file", {"error": f"Error decoding Base64 content: {str(e)}"}, inputs, 1)
    except Exception as e:
        return handle_action_error("decode_base64_and_write_file", "decode_base64_and_write_file", {"error": f"Error writing decoded file: {str(e)}"}, inputs, 1)

# --- Initialize the registry ---
populate_main_registry() 

# Export register_action for dynamic registration from other modules
def register_action(action_name: str, action_func: Callable, force: bool = False) -> None:
    main_action_registry.register_action(action_name, action_func, force=force) 