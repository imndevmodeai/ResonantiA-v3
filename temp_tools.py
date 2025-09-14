# --- START OF FILE 3.0ArchE/tools.py ---
# ResonantiA Protocol v3.0 - tools.py
# Defines basic, general-purpose tool execution functions (actions).
# CRITICAL: All functions MUST implement and return the IAR dictionary.

import logging
import json
import requests # For potential real search implementation
import time
import numpy as np # For math tool, potentially simulations
from typing import Dict, Any, List, Optional, Union # Expanded type hints
import os # For os.getcwd()
import sys # For sys.path

# --- Custom Imports & Setup ---
from .spr_manager import SPRManager
from . import config # Access configuration settings
from .llm_providers import get_llm_provider, get_model_for_provider, LLMProviderError # Import LLM helpers
from .action_context import ActionContext # Import ActionContext from new file
from .predictive_modeling_tool import run_prediction # Predictive tool main function
from .system_representation import System, GaussianDistribution, HistogramDistribution, StringParam # Import the system representation classes
from .workflow_engine import IARCompliantWorkflowEngine

# Initialize logger early for use in import blocks
# Using a more specific name for this logger to avoid clashes if 'tools' is a common name
logger_tools_diag = logging.getLogger(__name__ + "_tools_diag") # Unique logger name
# Basic config for diagnostics if not already configured by the system
if not logger_tools_diag.handlers:
    handler_td = logging.StreamHandler()
    formatter_td = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler_td.setFormatter(formatter_td)
    logger_tools_diag.addHandler(handler_td)
    logger_tools_diag.setLevel(logging.DEBUG)

logger_tools_diag.info(f"TOOLS.PY: Module execution started.")
logger_tools_diag.info(f"TOOLS.PY: __name__ is {__name__}, __file__ is {globals().get('__file__')}")
logger_tools_diag.info(f"TOOLS.PY: Current working directory: {os.getcwd()}")
logger_tools_diag.info(f"TOOLS.PY: sys.path: {sys.path}")

# Use relative imports for internal modules
try:
    LLM_AVAILABLE = True
    logger_tools_diag.info("TOOLS.PY: Successfully imported .config, .llm_providers, .action_context.")
except ImportError as e:
    logger_tools_diag.error(f"TOOLS.PY: Failed import for other tools.py dependencies (config, llm_providers, or action_context): {e}. LLM tool may be unavailable.", exc_info=True)
    LLM_AVAILABLE = False
    if 'LLMProviderError' not in globals():
        class LLMProviderError(Exception): pass
    if 'config' not in globals():
        class FallbackConfig: SEARCH_PROVIDER='simulated_google'; SEARCH_API_KEY=None; LLM_DEFAULT_MAX_TOKENS=1024; LLM_DEFAULT_TEMP=0.7
        config = FallbackConfig()

import subprocess
import shutil # For file operations
import uuid # For unique temp dir names
import traceback

# --- Tool-Specific Configuration ---
SEARCH_PROVIDER = getattr(config, 'SEARCH_PROVIDER', 'simulated_google').lower()
SEARCH_API_KEY = getattr(config, 'SEARCH_API_KEY', None)
NODE_SEARCH_SCRIPT_PATH = getattr(config, 'NODE_SEARCH_SCRIPT_PATH', None)

# --- Global Singleton for SPR Manager ---
_GLOBAL_SPR_MANAGER_INSTANCE = None

def get_global_spr_manager() -> SPRManager:
    """
    Initializes and returns a global singleton instance of the SPRManager.
    The path to the SPR definitions file is retrieved from config.
    """
    global _GLOBAL_SPR_MANAGER_INSTANCE
    if _GLOBAL_SPR_MANAGER_INSTANCE is None:
        try:
            spr_file_path = getattr(config, 'SPR_JSON_FILE', "knowledge_graph/spr_definitions_tv.json")
            logger_tools_diag.info(f"Initializing global SPRManager with definition file: {spr_file_path}")
            _GLOBAL_SPR_MANAGER_INSTANCE = SPRManager(spr_filepath=spr_file_path)
            logger_tools_diag.info(f"SPRManager initialized successfully. Loaded {len(_GLOBAL_SPR_MANAGER_INSTANCE.get_all_sprs())} SPRs.")
        except Exception as e:
            logger_tools_diag.error(f"Failed to initialize global SPRManager: {e}", exc_info=True)
            raise RuntimeError(f"Could not initialize SPRManager: {e}") from e
    return _GLOBAL_SPR_MANAGER_INSTANCE

# --- IAR Helper Function ---
# (Reused for consistency)
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

# --- Search Tool ---
def run_search(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Performs web search using configured provider or simulates results.
    Returns search results list and IAR reflection.
    Requires implementation for real search providers (e.g., SerpApi, Google Search API).
    """
    # --- Input Extraction ---
    query = inputs.get("query")
    num_results = inputs.get("num_results", 5) # Default to 5 results
    provider_used = inputs.get("provider", SEARCH_PROVIDER) # Use specific provider or config default
    api_key_used = inputs.get("api_key", SEARCH_API_KEY) # Use specific key or config default

    # --- Initialize Results & Reflection ---
    primary_result = {"results": [], "error": None, "provider_used": provider_used}
    reflection_status = "Failure"
    reflection_summary = "Search initialization failed."
    reflection_confidence = 0.0
    reflection_alignment = "N/A"
    reflection_issues: List[str] = []
    reflection_preview = None

    # --- Input Validation ---
    if not query or not isinstance(query, str):
        primary_result["error"] = "Search query (string) is required."
        reflection_issues.append(primary_result["error"])
        reflection_summary = "Input validation failed: Missing query."
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}
    try: # Ensure num_results is a sensible integer
        num_results = int(num_results)
        if num_results <= 0: num_results = 5; logger_tools_diag.warning("num_results must be positive, defaulting to 5.")
    except (ValueError, TypeError):
        num_results = 5; logger_tools_diag.warning(f"Invalid num_results value, defaulting to 5.")

    logger_tools_diag.info(f"Performing web search via '{provider_used}' for query: '{query}' (max {num_results} results)")

    # --- Execute Search (Simulation or Actual) ---
    try:
        if provider_used == "puppeteer_nodejs":
            if not NODE_SEARCH_SCRIPT_PATH or not os.path.exists(NODE_SEARCH_SCRIPT_PATH):
                error_msg = f"Node.js search script path not configured or not found. Expected at: {NODE_SEARCH_SCRIPT_PATH}"
                primary_result["error"] = error_msg
                reflection_issues.append(primary_result["error"])
                reflection_summary = "Configuration error: Node.js search script missing or path not set."
            else:
                # Create a unique base temporary directory for the Node.js script to use for its run-specific archives
                # This will be cleaned up by this Python function.
                # The Node script will create a sub-directory within this.
                search_tool_temp_base_dir = os.path.join(config.OUTPUT_DIR, "search_tool_temp", f"run_{uuid.uuid4().hex[:8]}")
                os.makedirs(search_tool_temp_base_dir, exist_ok=True)
                
                # Determine search engine for Node.js script
                search_engine_js = inputs.get("search_engine_js", "duckduckgo") # Default to duckduckgo, allow override
                
                cmd = ["node", NODE_SEARCH_SCRIPT_PATH, query, str(num_results), search_engine_js, search_tool_temp_base_dir]
                if inputs.get("debug_js", False): # Changed from debug_js_search to debug_js
                    cmd.append("--debug")

                logger_tools_diag.info(f"Executing Node.js search script: {' '.join(cmd)}")
                process = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=180) # Increased timeout for scraping/screenshots

                js_temp_archive_dir_abs = None
                if process.stderr:
                    logger_tools_diag.debug(f"Node.js script stderr:\n{process.stderr}")
                    for line in process.stderr.splitlines():
                        if "Archives for this run will be stored in:" in line:
                            js_temp_archive_dir_abs = line.split("Archives for this run will be stored in:")[-1].strip()
                            logger_tools_diag.info(f"Node.js script created archives in: {js_temp_archive_dir_abs}")
                            break
                
                if process.returncode == 0:
                    try:
                        raw_script_results = json.loads(process.stdout)
                        processed_script_results = []
                        
                        # Prepare final archive directory for this workflow run
                        workflow_run_id = "unknown_run_fallback"
                        if action_context and action_context.run_id:
                            workflow_run_id = action_context.run_id
                        elif inputs.get('workflow_run_id'): # Fallback to explicitly passed if any
                            workflow_run_id = inputs.get('workflow_run_id')
                        else:
                            workflow_run_id = f"unknown_run_{uuid.uuid4().hex[:8]}"
                        
                        final_archives_base_dir = os.path.join(config.OUTPUT_DIR, workflow_run_id, "search_archives")
                        os.makedirs(final_archives_base_dir, exist_ok=True)

                        for item in raw_script_results:
                            if item.get("error") == "Main process_failed": # Handle critical error from Node script
                                raise Exception(f"Node.js script main process failed: {item.get('details', 'Unknown error')}")

                            # Resolve archive paths and copy files
                            for key_suffix in ["html_path", "screenshot_path"]:
                                archive_key = f"archived_{key_suffix}"
                                relative_path_from_node = item.get(archive_key) # This is relative to search_tool_temp_base_dir
                                
                                if relative_path_from_node and js_temp_archive_dir_abs: # js_temp_archive_dir_abs is the actual run-XXXXXX dir
                                    # Construct absolute source path using the unique run directory identified from script's stderr
                                    # and the relative path it returned (which should be relative to that unique run dir)
                                    abs_source_path = os.path.abspath(os.path.join(js_temp_archive_dir_abs, os.path.basename(relative_path_from_node)))
                                    
                                    if os.path.exists(abs_source_path):
                                        file_basename = os.path.basename(abs_source_path)
                                        abs_dest_path = os.path.join(final_archives_base_dir, file_basename)
                                        try:
                                            shutil.copy2(abs_source_path, abs_dest_path)
                                            # Store path relative to OUTPUT_DIR for cleaner context
                                            item[archive_key] = os.path.relpath(abs_dest_path, config.OUTPUT_DIR)
                                            logger_tools_diag.debug(f"Copied {abs_source_path} to {abs_dest_path}. Stored rel path: {item[archive_key]}")
                                        except Exception as e_copy:
                                            logger_tools_diag.error(f"Failed to copy archive file {abs_source_path} to {abs_dest_path}: {e_copy}")
                                            item[archive_key] = None # Nullify if copy failed
                                    else:
                                        logger_tools_diag.warning(f"Archived file reported by Node.js script not found at {abs_source_path} (original relative: {relative_path_from_node})")
                                        item[archive_key] = None
                                elif relative_path_from_node:
                                    logger_tools_diag.warning(f"Could not resolve absolute path for {relative_path_from_node} as search_tool_temp_base_dir was not found.")
                                    item[archive_key] = None
                            processed_script_results.append(item)
                        
                        primary_result["results"] = processed_script_results
                        reflection_status = "Success"
                        reflection_summary = f"Puppeteer (Node.js) search completed for '{query[:50]}...'"
                        reflection_confidence = 0.85
                        reflection_alignment = "Aligned with information gathering goal (live web)."
                        reflection_preview = primary_result["results"][:1] if primary_result["results"] else None
                        if not primary_result["results"]:
                            reflection_issues.append("Node.js script returned no results or processed results are empty.")
                            reflection_summary += " (No results processed)"

                    except json.JSONDecodeError as e_json_parse:
                        primary_result["error"] = f"Failed to parse JSON output from Node.js script: {e_json_parse}. Output: {process.stdout[:500]}"
                        reflection_issues.append("JSON parsing error from script.")
                        reflection_summary = "Script output parsing error."
                    except Exception as e_processing_results: # Catch errors during result processing (like path issues)
                        logger_tools_diag.error(f"Error processing results from Node.js script: {e_processing_results}", exc_info=True)
                        primary_result["error"] = f"Error processing results from Node.js script: {str(e_processing_results)}"
                        reflection_issues.append("Result processing error.")
                        reflection_summary = "Error processing script results."
                else:
                    primary_result["error"] = f"Node.js search script failed (Code {process.returncode}): {process.stderr[:500]}"
                    reflection_issues.append(f"Node.js script execution error: {process.stderr[:100]}")
                    reflection_summary = "Node.js script execution failed."
                    logger_tools_diag.error(f"Node.js search script stderr: {process.stderr}")
                
                # Cleanup the temporary directory created by the Node.js script, if identified
                # This is js_temp_archive_dir_abs which is like .../search_tool_temp/run-XXXXXX/run-YYYYYY
                # The parent search_tool_temp_base_dir (e.g. .../search_tool_temp/run_abc123) should be cleaned up instead
                # as the node script creates its own sub-sub-folder.
                # Actually, search.js creates 'run-...' inside the passed outputDirArg.
                # So js_temp_archive_dir_abs is what we want to clean up, it's the 'run-...' dir.
                if js_temp_archive_dir_abs and os.path.exists(js_temp_archive_dir_abs):
                    try:
                        shutil.rmtree(js_temp_archive_dir_abs)
                        logger_tools_diag.info(f"Cleaned up Node.js temporary archive directory: {js_temp_archive_dir_abs}")
                    except Exception as e_rm:
                        logger_tools_diag.warning(f"Failed to clean up temporary directory {js_temp_archive_dir_abs}: {e_rm}")
        
        elif provider_used == "serpapi":
            # Real SerpApi search implementation would go here
            # Requires 'requests' library: pip install requests
            if not api_key_used:
                primary_result["error"] = "SerpApi API key is required."
            else:
                # ... SerpApi implementation ...
                primary_result["results"] = [{"source": "SerpApi", "title": "Placeholder", "snippet": "Real implementation needed."}]
                reflection_status = "Success"
                reflection_summary = "SerpApi search would be performed."
                reflection_confidence = 0.9
            
        else: # Default to simulated search
            logger_tools_diag.info(f"Using simulated search for provider '{provider_used}'.")
            primary_result["results"] = [
                {"source": "Simulated Search", "title": f"Simulated Result for '{query}' 1", "snippet": "This is a simulated search result. The system is configured to not use a real search provider."},
                {"source": "Simulated Search", "title": f"Simulated Result for '{query}' 2", "snippet": "To use a real provider, configure SEARCH_PROVIDER in config.py (e.g., 'serpapi' or 'puppeteer_nodejs')."}
            ]
            reflection_status = "Success"
            reflection_summary = "Simulated web search was performed successfully."
            reflection_confidence = 0.5
            reflection_alignment = "Aligned with information gathering goal (simulated)."
            reflection_issues.append("Search results are simulated and not from the live web.")
            reflection_preview = primary_result["results"][0] if primary_result["results"] else None

    except Exception as e:
        logger_tools_diag.error(f"An unexpected error occurred during search: {e}", exc_info=True)
        primary_result["error"] = f"An unexpected error occurred: {str(e)}"
        reflection_status = "Failure"
        reflection_summary = f"Search failed with an unexpected error: {str(e)[:100]}"
        reflection_confidence = 0.1
        reflection_issues.append(primary_result["error"])

    # --- Final Output ---
    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}


# --- LLM Invocation Tool ---
def invoke_llm(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Invokes a configured Large Language Model (LLM) with a given prompt.
    Returns the LLM's response and an IAR reflection.
    """
    # --- Input Extraction ---
    prompt = inputs.get("prompt")
    prompt_template = inputs.get("prompt_template")
    template_vars = inputs.get("template_vars", {})
    provider = inputs.get("provider") # Can override default from config
    model = inputs.get("model") # Can override default for provider from config
    max_tokens = inputs.get("max_tokens", getattr(config, 'LLM_DEFAULT_MAX_TOKENS', 1024))
    temperature = inputs.get("temperature", getattr(config, 'LLM_DEFAULT_TEMP', 0.7))
    is_json_output = inputs.get("json_output", False) # Hint that we expect JSON back

    # --- Initialize Results & Reflection ---
    primary_result = {"llm_response": None, "error": None, "provider_used": None, "model_used": None}
    reflection_status = "Failure"
    reflection_summary = "LLM invocation initialization failed."
    reflection_confidence = 0.0
    reflection_alignment = "N/A"
    reflection_issues: List[str] = []
    reflection_preview = None

    # --- Input Validation and Prompt Formatting ---
    if prompt_template and isinstance(prompt_template, str):
        try:
            prompt = prompt_template.format(**template_vars)
        except (KeyError, IndexError) as e:
            error_msg = f"Failed to format prompt template: Missing key '{e}'"
            primary_result["error"] = error_msg
            reflection_issues.append(error_msg)
            reflection_summary = "Input validation failed: Prompt template formatting error."
            return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}
    
    if not prompt or not isinstance(prompt, str):
        error_msg = "A non-empty prompt (string) is required."
        primary_result["error"] = error_msg
        reflection_issues.append(error_msg)
        reflection_summary = "Input validation failed: Missing prompt."
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

    logger_tools_diag.info(f"Attempting to invoke LLM. Prompt starts with: '{prompt[:150]}...'")

    # --- Execute LLM Invocation ---
    try:
        if not LLM_AVAILABLE:
            raise LLMProviderError("LLM libraries (e.g., openai, google-generativeai) not installed or configured.")

        # Get the provider instance
        llm_provider_instance = get_llm_provider(provider)
        primary_result["provider_used"] = llm_provider_instance.get_provider_name()
        
        # Get the specific model name to use
        model_name = get_model_for_provider(primary_result["provider_used"], model)
        primary_result["model_used"] = model_name

        # Invoke the LLM
        response_text = llm_provider_instance.invoke(
            prompt=prompt,
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            json_output=is_json_output
        )

        if is_json_output:
            try:
                # Attempt to parse the response as JSON
                primary_result["llm_response"] = json.loads(response_text)
                reflection_status = "Success"
                reflection_summary = f"LLM ({primary_result['model_used']}) invoked successfully, returned valid JSON."
                reflection_confidence = 0.9
            except json.JSONDecodeError as e_json:
                logger_tools_diag.warning(f"LLM was asked for JSON but returned non-JSON output. Error: {e_json}. Raw: {response_text[:200]}...")
                primary_result["error"] = f"LLM response was not valid JSON: {e_json}"
                primary_result["llm_response"] = response_text # Return raw text as fallback
                reflection_status = "Partial"
                reflection_summary = "LLM invoked, but failed to return valid JSON as requested."
                reflection_confidence = 0.6
                reflection_issues.append("LLM output failed JSON parsing.")
        else:
            primary_result["llm_response"] = response_text
            reflection_status = "Success"
            reflection_summary = f"LLM ({primary_result['model_used']}) invoked successfully."
            reflection_confidence = 0.85

        reflection_alignment = "Aligned with reasoning/generation goal."
        reflection_preview = primary_result["llm_response"]

    except LLMProviderError as e_provider:
        logger_tools_diag.error(f"LLM provider error: {e_provider}", exc_info=True)
        primary_result["error"] = str(e_provider)
        reflection_summary = f"LLM provider error: {str(e_provider)[:100]}"
        reflection_issues.append("LLM provider configuration or availability issue.")
    except Exception as e_unexpected:
        logger_tools_diag.error(f"An unexpected error occurred during LLM invocation: {e_unexpected}", exc_info=True)
        primary_result["error"] = f"An unexpected error occurred: {str(e_unexpected)}"
        reflection_summary = f"LLM invocation failed with an unexpected error: {str(e_unexpected)[:100]}"
        reflection_issues.append(primary_result["error"])

    # --- Final Output ---
    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

# --- Display Output Tool (for debugging and final output) ---
def display_output(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Displays formatted content to the console.
    This is primarily for providing a final, human-readable output for a workflow.
    """
    content = inputs.get("content")
    format_type = inputs.get("format", "text").lower()

    formatted_content = _format_output_content(content)
    
    print("\n" + "="*20 + " WORKFLOW FINAL OUTPUT " + "="*20)
    print(formatted_content)
    print("="*63 + "\n")

    primary_result = {"status": "Output displayed."}
    reflection = _create_reflection(
        status="Success",
        summary="Final output was successfully formatted and displayed.",
        confidence=1.0,
        alignment="Aligned with workflow completion goal.",
        issues=None,
        preview=formatted_content
    )
    return {**primary_result, "reflection": reflection}

# --- Run CFP Tool ---
def run_cfp(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Placeholder for running the Comparative Fluxual Processing framework.
    """
    logger_tools_diag.warning("run_cfp is a placeholder and does not perform real CFP analysis yet.")
    
    primary_result = {"cfp_results": "Placeholder CFP results.", "inputs_received": inputs}
    reflection = _create_reflection(
        status="Success",
        summary="Placeholder CFP tool executed successfully.",
        confidence=0.5,
        alignment="Aligned with complex system analysis goal (simulated).",
        issues=["CFP analysis is currently a placeholder."],
        preview=primary_result["cfp_results"]
    )
    return {**primary_result, "reflection": reflection}

# --- Math Calculation Tool ---
def calculate_math(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """

    [IAR Enabled] Calculates a mathematical expression using numpy.
    Supports basic arithmetic, functions (sin, cos, tan, sqrt, log, exp), and constants (pi, e).
    """
    expression = inputs.get("expression")
    primary_result = {"result": None, "error": None}
    
    if not expression:
        primary_result["error"] = "Input 'expression' is required."
        reflection = _create_reflection("Failure", "Missing required input 'expression'.", 0.0, "N/A", [primary_result["error"]], None)
        return {**primary_result, "reflection": reflection}

    # Define a safe namespace for evaluation
    safe_dict = {
        "np": np,
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "sqrt": np.sqrt, "log": np.log, "log10": np.log10, "exp": np.exp,
        "pi": np.pi, "e": np.e,
        "rad2deg": np.rad2deg, "deg2rad": np.deg2rad,
        "arcsin": np.arcsin, "arccos": np.arccos, "arctan": np.arctan
    }

    try:
        # Use a more restricted eval by disabling builtins
        result = eval(expression, {"__builtins__": None}, safe_dict)
        
        # Convert numpy types to native Python types for JSON serialization
        if isinstance(result, (np.ndarray, np.generic)):
            if result.ndim == 0: # It's a scalar
                primary_result["result"] = result.item()
            else: # It's an array
                primary_result["result"] = result.tolist()
        else:
            primary_result["result"] = result

        reflection = _create_reflection(
            status="Success",
            summary=f"Successfully calculated '{expression}'.",
            confidence=0.98,
            alignment="Aligned with quantitative analysis goal.",
            issues=None,
            preview=f"Result: {primary_result['result']}"
        )

    except NameError as e:
        primary_result["error"] = f"Invalid name or function in expression: {e}. Only numpy functions (e.g., sin, sqrt) and constants (pi, e) are allowed."
        reflection = _create_reflection("Failure", "Invalid name in expression.", 0.2, "Misaligned (invalid input).", [primary_result["error"]], None)
    except Exception as e:
        primary_result["error"] = f"Failed to evaluate expression: {e}"
        reflection = _create_reflection("Failure", f"Expression evaluation failed: {e}", 0.1, "Misaligned (invalid input).", [primary_result["error"]], None)

    return {**primary_result, "reflection": reflection}


# --- Placeholder Codebase Search Tool ---
def placeholder_codebase_search(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Simulates searching the codebase.
    In a real implementation, this would use a tool like ripgrep, AST analysis,
    or a vector database of code embeddings.
    """
    query = inputs.get("query")
    search_type = inputs.get("type", "semantic") # "semantic" or "exact"

    if not query:
        primary_result = {"error": "Input 'query' is required."}
        reflection = _create_reflection("Failure", "Missing required input.", 0.0, "N/A", [primary_result["error"]], None)
        return {**primary_result, "reflection": reflection}

    logger_tools_diag.info(f"Simulating codebase search (type: {search_type}) for query: '{query}'")

    primary_result = {
        "results": [
            {"file": "Three_PointO_ArchE/workflow_engine.py", "line": 123, "match": "class IARCompliantWorkflowEngine:", "score": 0.92},
            {"file": "Three_PointO_ArchE/tools.py", "line": 50, "match": "def run_workflow_suite(...)", "score": 0.85},
            {"file": "workflows/quality_assurance_workflow.json", "line": 5, "match": "\"name\": \"quality_assurance_workflow\"", "score": 0.78}
        ]
    }
    reflection = _create_reflection(
        status="Success",
        summary=f"Simulated codebase search for '{query}' completed.",
        confidence=0.5,
        alignment="Aligned with code analysis goal (simulated).",
        issues=["Codebase search is currently a placeholder."],
        preview=primary_result["results"][0]
    )
    return {**primary_result, "reflection": reflection}


def _format_output_content(content: Any) -> str:
    """Helper to format content for display_output."""
    if isinstance(content, (dict, list)):
        try:
            return json.dumps(content, indent=2, default=str)
        except Exception:
            return str(content)
    return str(content)

# In tools.py

def retrieve_spr_definitions(inputs: Dict[str, Any], context_for_action: ActionContext) -> Dict[str, Any]:
    """
    [IAR Enabled] Retrieves definitions for specified SPRs using the SPRManager.
    """
    def default_failure_reflection_local(summary: str) -> Dict[str, Any]:
        """Creates a standardized failure reflection dictionary."""
        return _create_reflection(
            status="Failure",
            summary=summary,
            confidence=0.1,
            alignment="Misaligned - tool failed to initialize or execute.",
            issues=[summary],
            preview=None
        )

    # --- Input validation and SPR Manager acquisition ---
    spr_keys_input = inputs.get("spr_keys")
    if not spr_keys_input:
        error_msg = "Input 'spr_keys' (a list of strings) is required."
        return {"error": error_msg, "definitions": {}, "reflection": default_failure_reflection_local(error_msg)}

    if isinstance(spr_keys_input, str):
        spr_keys = [spr_keys_input] # Allow single string for convenience
    elif isinstance(spr_keys_input, list):
        spr_keys = spr_keys_input
    else:
        error_msg = "'spr_keys' must be a string or a list of strings."
        return {"error": error_msg, "definitions": {}, "reflection": default_failure_reflection_local(error_msg)}

    try:
        # Use the spr_manager from the context if available, otherwise get the global one.
        spr_manager = context_for_action.spr_manager if context_for_action and context_for_action.spr_manager else get_global_spr_manager()
    except Exception as e:
        error_msg = f"Failed to get SPR Manager instance: {e}"
        logger_tools_diag.error(error_msg, exc_info=True)
        return {"error": error_msg, "definitions": {}, "reflection": default_failure_reflection_local(error_msg)}

    # --- Main logic ---
    definitions = {}
    not_found = []
    for key in spr_keys:
        try:
            definition = spr_manager.get_spr_definition(key)
            if definition:
                definitions[key] = definition
            else:
                not_found.append(key)
        except Exception as e:
            logger_tools_diag.error(f"Error retrieving definition for SPR '{key}': {e}", exc_info=True)
            not_found.append(key)

    # --- Reflection and Output Generation ---
    if not definitions and not not_found:
        summary = "No SPR keys were provided or processed."
        status = "Partial"
        confidence = 0.4
    elif not definitions and not_found:
        summary = f"Could not find definitions for any of the requested SPRs: {', '.join(not_found)}"
        status = "Failure"
        confidence = 0.3
    elif definitions and not_found:
        summary = f"Successfully retrieved {len(definitions)} SPRs. Could not find: {', '.join(not_found)}"
        status = "Partial"
        confidence = 0.75
    else: # All found
        summary = f"Successfully retrieved all {len(definitions)} requested SPR definitions."
        status = "Success"
        confidence = 0.95

    issues = [f"SPRs not found: {', '.join(not_found)}"] if not_found else None

    reflection = _create_reflection(
        status=status,
        summary=summary,
        confidence=confidence,
        alignment="Aligned with knowledge retrieval goal.",
        issues=issues,
        preview=list(definitions.keys())
    )

    return {"definitions": definitions, "not_found": not_found, "reflection": reflection}

def default_failure_reflection(summary: str) -> Dict[str, Any]:
    """Creates a standardized failure reflection dictionary."""
    return _create_reflection(
        status="Failure",
        summary=summary,
        confidence=0.1,
        alignment="Misaligned - tool failed to initialize or execute.",
        issues=[summary],
        preview=None
    )


def _create_system_from_json(config: Dict[str, Any]) -> System:
    """Helper to create a System object from a JSON-like dict."""
    name = config.get("name", "UnnamedSystem")
    params = []
    for p_config in config.get("parameters", []):
        p_name = p_config.get("name")
        p_dist = p_config.get("distribution")
        p_type = p_dist.get("type")
        
        if p_type == "gaussian":
            params.append(GaussianDistribution(p_name, p_dist.get("mean"), p_dist.get("stddev")))
        elif p_type == "histogram":
            params.append(HistogramDistribution(p_name, p_dist.get("bins"), p_dist.get("weights")))
        elif p_type == "string":
            params.append(StringParam(p_name, p_dist.get("value")))
            
    return System(name, params)


def analyze_system_divergence(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Analyzes the divergence between two system configurations.
    """
    system1_config = inputs.get("system1")
    system2_config = inputs.get("system2")

    if not system1_config or not system2_config:
        error_msg = "Inputs 'system1' and 'system2' configurations are required."
        return {"error": error_msg, "divergence": -1, "details": {}, "reflection": default_failure_reflection(error_msg)}
    
    try:
        system1 = _create_system_from_json(system1_config)
        system2 = _create_system_from_json(system2_config)
        
        divergence, details = system1.compare(system2)
        
        primary_result = {
            "divergence": divergence,
            "details": details
        }
        
        reflection = _create_reflection(
            status="Success",
            summary=f"Successfully analyzed divergence between {system1.name} and {system2.name}. Total divergence: {divergence:.4f}",
            confidence=0.9,
            alignment="Aligned with system comparison goal.",
            issues=None,
            preview=f"Divergence: {divergence:.4f}"
        )
        
        return {**primary_result, "reflection": reflection}

    except Exception as e:
        error_msg = f"Failed to analyze system divergence: {e}"
        logger_tools_diag.error(error_msg, exc_info=True)
        return {"error": error_msg, "divergence": -1, "details": {}, "reflection": default_failure_reflection(error_msg)}


def compare_system_factors(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Compares specific factors between two system configurations.
    """
    system1_config = inputs.get("system1")
    system2_config = inputs.get("system2")
    factor_names = inputs.get("factors")

    if not all([system1_config, system2_config, factor_names]):
        error_msg = "Inputs 'system1', 'system2', and 'factors' are required."
        return {"error": error_msg, "comparison": {}, "reflection": default_failure_reflection(error_msg)}

    if isinstance(factor_names, str):
        factor_names = [factor_names]
        
    try:
        system1 = _create_system_from_json(system1_config)
        system2 = _create_system_from_json(system2_config)
        
        comparison = {}
        total_divergence = 0
        
        for factor_name in factor_names:
            param1 = system1.get_parameter(factor_name)
            param2 = system2.get_parameter(factor_name)
            
            if not param1 or not param2:
                comparison[factor_name] = {"error": "Factor not found in one or both systems."}
                continue

            divergence, details = param1.compare(param2)
            comparison[factor_name] = {
                "divergence": divergence,
                "details": details,
                "system1_value": param1.get_value(),
                "system2_value": param2.get_value()
            }
            total_divergence += divergence
            
        avg_divergence = total_divergence / len(factor_names) if factor_names else 0

        primary_result = {
            "comparison": comparison,
            "average_divergence": avg_divergence
        }

        reflection = _create_reflection(
            status="Success",
            summary=f"Successfully compared {len(factor_names)} factors. Average divergence: {avg_divergence:.4f}",
            confidence=0.9,
            alignment="Aligned with detailed factor comparison.",
            issues=None,
            preview=f"Compared factors: {', '.join(factor_names)}. Avg divergence: {avg_divergence:.4f}"
        )

        return {**primary_result, "reflection": reflection}
        
    except Exception as e:
        error_msg = f"Failed to compare system factors: {e}"
        logger_tools_diag.error(error_msg, exc_info=True)
        return {"error": error_msg, "comparison": {}, "reflection": default_failure_reflection(error_msg)}


def analyze_workflow_impact(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Analyzes the potential impact of a workflow on a system.
    """
    workflow_config = inputs.get("workflow_config")
    system_config = inputs.get("system_config")
    
    if not workflow_config or not system_config:
        error_msg = "Inputs 'workflow_config' and 'system_config' are required."
        return {"error": error_msg, "impact_analysis": {}, "reflection": default_failure_reflection(error_msg)}
        
    try:
        system = _create_system_from_json(system_config)
        
        # This is a conceptual placeholder for a much more complex analysis.
        # A real implementation would need to simulate the workflow's effects.
        
        tasks = workflow_config.get("tasks", {})
        impact_score = 0
        impact_details = {}
        
        for task_name, task_def in tasks.items():
            action = task_def.get("action")
            task_inputs = task_def.get("inputs", {})
            
            # Conceptual impact scoring
            if action == "run_prediction":
                impact_score += 0.5
                impact_details[task_name] = "High impact: predictive modeling can alter future state understanding."
            elif action == "invoke_llm":
                if "update_system_parameter" in task_inputs.get("prompt", ""):
                    impact_score += 0.8
                    impact_details[task_name] = "Very high impact: LLM may directly modify system parameters."
                else:
                    impact_score += 0.2
                    impact_details[task_name] = "Low impact: LLM used for reasoning or generation."
            elif action == "run_code_linter":
                 impact_score += 0.1
                 impact_details[task_name] = "Low impact: Linter is an observational tool."
            else:
                 impact_score += 0.1
                 impact_details[task_name] = f"Low impact: Action '{action}' has undefined impact."
        
        # Normalize score
        max_possible_score = len(tasks)
        normalized_impact = impact_score / max_possible_score if max_possible_score > 0 else 0
        
        primary_result = {
            "impact_analysis": {
                "normalized_impact_score": normalized_impact,
                "details": impact_details,
                "summary": f"Workflow '{workflow_config.get('name', 'Unnamed')}' has a potential normalized impact of {normalized_impact:.2f} on system '{system.name}'."
            }
        }
        
        reflection = _create_reflection(
            status="Success",
            summary=f"Successfully analyzed impact for workflow '{workflow_config.get('name', 'Unnamed')}'.",
            confidence=0.6, # Confidence is moderate as this is a simulation
            alignment="Aligned with impact analysis goal.",
            issues=["Impact analysis is a conceptual simulation, not a real execution."],
            preview=primary_result["impact_analysis"]["summary"]
        )
        
        return {**primary_result, "reflection": reflection}

    except Exception as e:
        error_msg = f"Failed to analyze workflow impact: {e}"
        logger_tools_diag.error(error_msg, exc_info=True)
        return {"error": error_msg, "impact_analysis": {}, "reflection": default_failure_reflection(error_msg)}


def run_code_linter(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Runs a linter on a given code string.
    """
    code_string = inputs.get("code")
    linter = inputs.get("linter", "pylint") # or "flake8", "eslint", etc.
    
    if not code_string:
        error_msg = "Input 'code' (string) is required."
        return {"error": error_msg, "linting_results": {}, "reflection": default_failure_reflection(error_msg)}

    # This is a conceptual placeholder. A real implementation would need to
    # write the code to a temporary file and run the linter executable.
    
    # Simulate pylint output
    if linter == "pylint":
        # Simple heuristic: count lines and common style issues
        lines = code_string.split('\n')
        num_lines = len(lines)
        issues = []
        if num_lines > 200:
            issues.append("C0301: Line too long (simulated for files > 200 lines)")
        if "import os" in code_string and "os.system" not in code_string:
            issues.append("W0611: Unused import os (simulated)")

        score = max(0, 10.0 - len(issues) * 2.5)

        primary_result = {
            "linter": "pylint",
            "issues_found": len(issues),
            "score": score,
            "report": issues
        }
        summary = f"Simulated pylint check. Score: {score}/10"

    else:
        primary_result = {"error": f"Linter '{linter}' is not supported in this simulation."}
        summary = f"Unsupported linter '{linter}'"

    reflection = _create_reflection(
        status="Success" if "error" not in primary_result else "Failure",
        summary=summary,
        confidence=0.5,
        alignment="Aligned with code quality check (simulated).",
        issues=["Linter tool is a conceptual simulation."],
        preview=f"Issues found: {primary_result.get('issues_found', 'N/A')}"
    )
    
    return {**primary_result, "reflection": reflection}


def run_workflow_suite(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Runs a suite of workflows and aggregates their results.
    Injects the suite's run_id into each sub-workflow's initial context.
    """
    workflow_files = inputs.get("workflow_files")
    if not isinstance(workflow_files, list):
        error_msg = "Input 'workflow_files' (a list of workflow file paths) is required."
        return {"error": error_msg, "suite_results": [], "reflection": default_failure_reflection(error_msg)}

    suite_run_id = action_context.run_id if action_context else str(uuid.uuid4())
    logger_tools_diag.info(f"Starting workflow suite with run_id: {suite_run_id}")

    # Initialize a workflow engine instance to run the sub-workflows
    try:
        engine = IARCompliantWorkflowEngine(spr_manager=get_global_spr_manager())
    except Exception as e:
        error_msg = f"Failed to initialize IARCompliantWorkflowEngine for suite: {e}"
        logger_tools_diag.error(error_msg, exc_info=True)
        return {"error": error_msg, "suite_results": [], "reflection": default_failure_reflection(error_msg)}

    suite_results = []
    failed_workflows = []
    successful_workflows = 0

    for workflow_file in workflow_files:
        try:
            logger_tools_diag.info(f"Running workflow '{workflow_file}' as part of suite '{suite_run_id}'.")
            # Prepare initial context for the sub-workflow, injecting the suite's run_id
            initial_context_for_sub = {
                "suite_run_id": suite_run_id,
                "run_id": suite_run_id, # Also add as top-level 'run_id' for compatibility
                "initial_input": inputs.get("initial_input_for_suite") # Pass along any initial data
            }

            # Run the workflow
            result = engine.run_workflow(workflow_file, initial_context_for_sub)
            suite_results.append(result)

            if result.get("status") == "Failed" or result.get("error"):
                failed_workflows.append(workflow_file)
                logger_tools_diag.error(f"Workflow '{workflow_file}' failed in suite. Result: {result.get('error', 'Unknown error')}")
            else:
                successful_workflows += 1
                logger_tools_diag.info(f"Workflow '{workflow_file}' completed successfully in suite.")

        except Exception as e:
            error_summary = {
                "workflow_name": workflow_file,
                "status": "Failed",
                "error": f"Crashed during execution in suite: {e}"
            }
            suite_results.append(error_summary)
            failed_workflows.append(workflow_file)
            logger_tools_diag.error(f"Workflow '{workflow_file}' crashed in suite.", exc_info=True)

    # --- Reflection and Output Generation ---
    total_run = len(workflow_files)
    if total_run == 0:
        summary = "Workflow suite ran with an empty list of workflows."
        status = "Partial"
        confidence = 0.5
    elif not failed_workflows:
        summary = f"All {total_run} workflows in the suite completed successfully."
        status = "Success"
        confidence = 0.98
    else:
        summary = f"Suite completed with {len(failed_workflows)}/{total_run} failures: {', '.join(failed_workflows)}"
        status = "Partial" if successful_workflows > 0 else "Failure"
        confidence = 0.7

    reflection = _create_reflection(
        status=status,
        summary=summary,
        confidence=confidence,
        alignment="Aligned with QA/batch processing goal.",
        issues=[f"Failed workflows: {failed_workflows}"] if failed_workflows else None,
        preview={"successful": successful_workflows, "failed": len(failed_workflows), "total": total_run}
    )

    return {"suite_results": suite_results, "summary": summary, "reflection": reflection} 