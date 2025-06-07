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
                    except Exception as e_cleanup:
                        logger_tools_diag.warning(f"Failed to clean up Node.js temporary archive directory {js_temp_archive_dir_abs}: {e_cleanup}")
                
                # Also clean up the base temp dir we created if it's empty or if the node script failed to create its own.
                if os.path.exists(search_tool_temp_base_dir):
                    try:
                        if not os.listdir(search_tool_temp_base_dir): # only remove if empty
                             shutil.rmtree(search_tool_temp_base_dir)
                             logger_tools_diag.info(f"Cleaned up empty base temporary directory: {search_tool_temp_base_dir}")
                        else:
                            # If it's not empty, it means js_temp_archive_dir_abs might not have been identified correctly,
                            # or the script put files directly in search_tool_temp_base_dir.
                            # This part of cleanup might need refinement based on exact search.js behavior.
                            # For now, if js_temp_archive_dir_abs was cleaned, this might be redundant or clean up other strays.
                            # Let's be cautious and only remove search_tool_temp_base_dir if js_temp_archive_dir_abs was NOT cleaned
                            # and search_tool_temp_base_dir IS js_temp_archive_dir_abs (meaning node script used the dir directly).
                            if not js_temp_archive_dir_abs or js_temp_archive_dir_abs != search_tool_temp_base_dir :
                                pass # Handled by js_temp_archive_dir_abs cleanup or has unexpected content
                            # If js_temp_archive_dir_abs IS search_tool_temp_base_dir and wasn't cleaned (e.g. error before), try cleaning.
                            elif js_temp_archive_dir_abs == search_tool_temp_base_dir:
                                shutil.rmtree(search_tool_temp_base_dir)
                                logger_tools_diag.info(f"Cleaned up base temporary directory (used directly by script): {search_tool_temp_base_dir}")
                    except Exception as e_base_cleanup:
                        logger_tools_diag.warning(f"Error during cleanup of base temporary directory {search_tool_temp_base_dir}: {e_base_cleanup}")

        elif provider_used.startswith("simulated"):
            # --- Simulation Logic ---
            simulated_results = []
            # Generate somewhat unique results based on query hash
            query_hash_part = str(hash(query) % 1000).zfill(3) # Use modulo for shorter hash part
            for i in range(num_results):
                simulated_results.append({
                    "title": f"Simulated Result {i+1}-{query_hash_part} for '{query[:30]}...'",
                    "link": f"http://simulated.example.com/{provider_used}?q={query.replace(' ', '+')}&id={query_hash_part}&result={i+1}",
                    "snippet": f"This is simulated snippet #{i+1} discussing concepts related to '{query[:50]}...'. Contains simulated data (ID: {query_hash_part})."
                })
            time.sleep(0.1) # Simulate network latency
            primary_result["results"] = simulated_results
            reflection_status = "Success"
            reflection_summary = f"Simulated search completed successfully for '{query[:50]}...'."
            reflection_confidence = 0.6 # Moderate confidence as results are simulated
            reflection_alignment = "Aligned with information gathering goal (simulated)."
            reflection_issues.append("Search results are simulated, not real-time web data.")
            reflection_preview = simulated_results[:2] # Preview first few simulated results

        # --- Placeholder for Real Search Provider Implementations ---
        # elif provider_used == "google_custom_search":
        #     # <<< INSERT Google Custom Search API call logic here >>>
        #     # Requires 'requests' library and valid API key/CX ID
        #     # Handle API errors, parse results into standard format
        #     primary_result["error"] = "Real Google Custom Search not implemented."
        #     reflection_issues.append(primary_result["error"])
        # elif provider_used == "serpapi":
        #     # <<< INSERT SerpApi call logic here >>>
        #     # Requires 'serpapi' library or 'requests' and valid API key
        #     # Handle API errors, parse results
        #     primary_result["error"] = "Real SerpApi search not implemented."
        #     reflection_issues.append(primary_result["error"])
        # Add other providers as needed...

        else:
            # Handle unsupported provider case
            primary_result["error"] = f"Unsupported search provider configured: {provider_used}"
            reflection_issues.append(primary_result["error"])
            reflection_summary = f"Configuration error: Unsupported search provider '{provider_used}'."

    except Exception as e_search:
        # Catch unexpected errors during search execution
        logger_tools_diag.error(f"Unexpected error during search operation: {e_search}", exc_info=True)
        primary_result["error"] = f"Unexpected search error: {e_search}"
        reflection_issues.append(f"System Error: {e_search}")
        reflection_summary = f"Unexpected error during search: {e_search}"

    # --- Finalize Reflection ---
    if primary_result["error"]:
        reflection_status = "Failure" # Ensure status reflects error
        if reflection_summary == "Search initialization failed.": # Update summary if error happened later
            reflection_summary = f"Search failed: {primary_result['error']}"
        reflection_confidence = 0.1 # Low confidence on failure

    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

# --- LLM Tool ---
def invoke_llm(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Invokes a configured LLM provider (via llm_providers.py)
    using either a direct prompt or a list of chat messages.
    Handles provider/model selection, parameter passing, error handling, and IAR generation.
    """
    # --- Initialize Results & Reflection ---
    # Default to failure state for initialization issues
    primary_result = {"response_text": None, "error": None, "provider_used": None, "model_used": None}
    reflection_status = "Failure"
    reflection_summary = "LLM invocation initialization failed."
    reflection_confidence = 0.0
    reflection_alignment = "N/A"
    reflection_issues: List[str] = ["Initialization error."]
    reflection_preview = None

    # Check if LLM module is even available
    if not LLM_AVAILABLE:
        primary_result["error"] = "LLM Providers module (llm_providers.py) is not available or failed to import."
        reflection_issues = [primary_result["error"]]
        reflection_summary = "LLM module unavailable."
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

    # --- Input Extraction ---
    prompt_template_str = inputs.get("prompt") 
    if not prompt_template_str:
        prompt_template_str = inputs.get("prompt_text")

    messages = inputs.get("messages")
    prompt_vars = inputs.get("prompt_vars")
    provider_name_override = inputs.get("provider") 
    model_name_override = inputs.get("model") 
    max_tokens = inputs.get("max_tokens", getattr(config, 'LLM_DEFAULT_MAX_TOKENS', 1024))
    temperature = inputs.get("temperature", getattr(config, 'LLM_DEFAULT_TEMP', 0.7))
    standard_keys = ['prompt', 'prompt_text', 'messages', 'prompt_vars', 'provider', 'model', 'max_tokens', 'temperature']
    extra_params = {k: v for k, v in inputs.items() if k not in standard_keys}

    final_prompt_str = None
    if prompt_template_str and isinstance(prompt_template_str, str):
        if isinstance(prompt_vars, dict) and prompt_vars:
            try:
                final_prompt_str = prompt_template_str.format(**prompt_vars)
                logger_tools_diag.info(f"Substituted prompt_vars into prompt_text. Original: '{prompt_template_str[:100]}...', Vars: {prompt_vars}")
            except KeyError as e_key:
                logger_tools_diag.warning(f"KeyError during .format() in invoke_llm: {e_key}. Using prompt_template as is. Ensure placeholders in prompt_text match keys in prompt_vars.")
                final_prompt_str = prompt_template_str # Fallback to original template
            except Exception as e_fmt:
                logger_tools_diag.error(f"Unexpected error during .format() in invoke_llm: {e_fmt}. Using prompt_template as is.", exc_info=True)
                final_prompt_str = prompt_template_str # Fallback
        else:
            final_prompt_str = prompt_template_str # No vars to substitute

    # --- Input Validation ---
    if not final_prompt_str and not messages:
        primary_result["error"] = "LLM invocation requires either 'prompt' (string, after var substitution) or 'messages' (list of dicts) input."
        reflection_issues = ["Missing required input ('prompt' or 'messages')."]
        reflection_summary = "Input validation failed: Missing prompt/messages."
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}
    
    if final_prompt_str and messages:
        logger_tools_diag.warning("Both 'prompt' (after var substitution) and 'messages' provided to invoke_llm. Prioritizing 'messages' for chat completion.")
        final_prompt_str = None # Clear prompt if messages are present, messages take precedence

    # --- Execute LLM Call ---
    try:
        provider = get_llm_provider(provider_name_override)
        provider_name_used = provider._provider_name
        primary_result["provider_used"] = provider_name_used
        model_to_use = model_name_override or get_model_for_provider(provider_name_used)
        primary_result["model_used"] = model_to_use

        logger_tools_diag.info(f"Invoking LLM: Provider='{provider_name_used}', Model='{model_to_use}'")
        api_kwargs = {"max_tokens": max_tokens, "temperature": temperature, **extra_params}
        response_text = ""
        start_time = time.time()

        if messages:
            response_text = provider.generate_chat(messages=messages, model=model_to_use, **api_kwargs)
        elif final_prompt_str:
            response_text = provider.generate(prompt=final_prompt_str, model=model_to_use, **api_kwargs)
        # If both are None (e.g. prompt became None due to messages taking precedence, or was never there)
        # the input validation above should have caught it. This path implies one was valid.

        duration = time.time() - start_time

        # --- Process Successful Response ---
        primary_result["response_text"] = response_text
        parsing_type = inputs.get("parsing_type", "text").lower()

        if parsing_type == "json" and response_text:
            try:
                # Ensure response_text is not just whitespace or empty before trying to parse
                if response_text.strip():
                    # Attempt to strip common markdown code fences if present
                    cleaned_response_text = response_text.strip()
                    if cleaned_response_text.startswith("```json"): # Handle ```json ... ```
                        cleaned_response_text = cleaned_response_text[7:]
                        if cleaned_response_text.endswith("```"):
                            cleaned_response_text = cleaned_response_text[:-3]
                    elif cleaned_response_text.startswith("```") and cleaned_response_text.endswith("```"): # Handle ``` ... ```
                         cleaned_response_text = cleaned_response_text[3:-3]

                    parsed_data = json.loads(cleaned_response_text.strip())
                    if isinstance(parsed_data, dict):
                        for key, value in parsed_data.items():
                            if key not in primary_result: # Prioritize existing keys like 'response_text'
                                primary_result[key] = value
                            else:
                                primary_result[f"parsed_{key}"] = value 
                                logger_tools_diag.warning(f"Key '{key}' from parsed JSON already exists in primary_result. Stored as 'parsed_{key}'.")
                        logger_tools_diag.info("Successfully parsed JSON response and merged into primary_result.")
                    else:
                        primary_result["parsed_json_output"] = parsed_data
                        logger_tools_diag.info("Successfully parsed JSON response (non-dict) into 'parsed_json_output'.")
                else:
                    logger_tools_diag.warning("Response_text is empty or whitespace; skipping JSON parsing.")
                    # Potentially add to reflection_issues if JSON was expected but got empty response
                    if "reflection_issues" not in locals(): reflection_issues = [] # Ensure reflection_issues exists
                    reflection_issues.append("LLM response was empty/whitespace, expected JSON.")

            except json.JSONDecodeError as e_json:
                logger_tools_diag.warning(f"Failed to parse response_text as JSON: {e_json}. LLM output (raw) was: {response_text[:500]}...")
                if "reflection_issues" not in locals(): reflection_issues = [] # Ensure reflection_issues exists
                reflection_issues.append(f"Output Parsing Error: Failed to parse LLM response as JSON. Error: {e_json}")
        
        reflection_status = "Success"
        reflection_summary = f"LLM call to {model_to_use} via {provider_name_used} completed successfully in {duration:.2f}s."
        # Confidence: LLMs can hallucinate, so confidence is inherently moderate unless further vetted
        reflection_confidence = 0.80
        reflection_alignment = "Assumed aligned with generation/analysis goal (content requires vetting)."
        reflection_issues = ["LLM output may contain inaccuracies or reflect biases from training data."] # Standard LLM caveat
        # Check for potential issues based on provider response (e.g., content filters)
        # This requires providers to potentially return more than just text, or parse specific error messages
        if "Content blocked" in str(response_text): # Example check
            reflection_issues.append("LLM response may have been blocked or filtered by provider.")
            reflection_confidence = max(0.1, reflection_confidence - 0.3) # Lower confidence if filtered
        reflection_preview = (response_text[:100] + '...') if isinstance(response_text, str) and len(response_text) > 100 else response_text
        logger_tools_diag.info(f"LLM invocation successful (Duration: {duration:.2f}s).")

    # --- Handle LLM Provider Errors ---
    except (ValueError, LLMProviderError) as e_llm: # Catch validation errors or specific provider errors
        error_msg = f"LLM invocation failed: {e_llm}"
        logger_tools_diag.error(error_msg, exc_info=True if isinstance(e_llm, LLMProviderError) else False)
        primary_result["error"] = error_msg
        reflection_status = "Failure"
        reflection_summary = f"LLM call failed: {e_llm}"
        reflection_confidence = 0.0
        reflection_alignment = "Failed to interact with LLM."
        # Add specific error type to issues
        reflection_issues = [f"API/Configuration Error: {type(e_llm).__name__}"]
        if hasattr(e_llm, 'provider') and e_llm.provider: primary_result["provider_used"] = e_llm.provider # type: ignore
    except Exception as e_generic:
        # Catch any other unexpected errors
        error_msg = f"Unexpected error during LLM invocation: {e_generic}"
        logger_tools_diag.error(error_msg, exc_info=True)
        primary_result["error"] = error_msg
        reflection_status = "Failure"
        reflection_summary = f"Unexpected error during LLM call: {e_generic}"
        reflection_confidence = 0.0
        reflection_alignment = "Failed due to system error."
        reflection_issues = [f"System Error: {type(e_generic).__name__}"]

    # --- Final Return ---
    # Ensure provider/model used are recorded even on failure if determined before error
    if primary_result["provider_used"] is None and 'provider' in locals(): primary_result["provider_used"] = provider._provider_name # type: ignore
    if primary_result["model_used"] is None and 'model_to_use' in locals(): primary_result["model_used"] = model_to_use

    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

# --- Display Tool ---
def display_output(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Displays content to the console/log.
    Returns a reflection of the display action.
    """
    # --- Input Extraction ---
    content_to_display = inputs.get("content", "[No content provided]")

    # --- Initialize Reflection ---
    reflection_status = "Success"
    reflection_summary = "Content displayed successfully."
    reflection_confidence = 1.0
    reflection_alignment = "Aligned with output/display goal."
    reflection_issues: List[str] = []

    # --- Execute Display ---
    logger_tools_diag.info("Displaying output content via print().")
    # A more structured output format
    display_str = f"\n--- Arche Display Output (v3.0) ---\n{_format_output_content(content_to_display)}\n-----------------------------------\n"
    print(display_str) # Print to standard output

    # --- Finalize and Return ---
    primary_result = {"status": "displayed", "content_preview": str(content_to_display)[:75] + "..."}
    reflection = _create_reflection(
        status=reflection_status,
        summary=reflection_summary,
        confidence=reflection_confidence,
        alignment=reflection_alignment,
        issues=reflection_issues,
        preview=content_to_display
    )
    return {**primary_result, "reflection": reflection}

# --- RunCFP Tool Wrapper ---
# This function exists only to be registered. The actual logic is in the wrapper
# within action_registry.py which calls the CfpframeworK class.
def run_cfp(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled Placeholder] Action function for 'run_cfp'.
    NOTE: The primary implementation logic resides in the `run_cfp_action` wrapper
    within `action_registry.py` (Section 7.4), which utilizes the `CfpframeworK` class.
    This function should ideally not be called directly if using the registry.
    Returns an error indicating it should be called via the registry.
    """
    logger_tools_diag.error("Direct call to tools.run_cfp detected. Action 'run_cfp' should be executed via the action registry using the run_cfp_action wrapper.")
    error_msg = "Placeholder tools.run_cfp called directly. Use 'run_cfp' action type via registry/WorkflowEngine."
    return {
        "error": error_msg,
        "reflection": _create_reflection(
            status="Failure",
            summary=error_msg,
            confidence=0.0,
            alignment="Misaligned - Incorrect invocation.",
            issues=["Incorrect workflow configuration or direct tool call."],
            preview=None
        )
    }

# --- Simple Math Tool ---
def calculate_math(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Safely evaluates a simple mathematical expression string
    using the 'numexpr' library (if available) to prevent security risks
    associated with standard eval(). Requires 'numexpr' to be installed.
    """
    # --- Input Extraction ---
    expression = inputs.get("expression")

    # --- Initialize Results & Reflection ---
    primary_result = {"result": None, "error": None}
    reflection_status = "Failure"
    reflection_summary = "Math calculation initialization failed."
    reflection_confidence = 0.0
    reflection_alignment = "N/A"
    reflection_issues: List[str] = []
    reflection_preview = None

    # --- Input Validation ---
    if not expression or not isinstance(expression, str):
        primary_result["error"] = "Mathematical expression (string) required as 'expression' input."
        reflection_issues.append(primary_result["error"])
        reflection_summary = "Input validation failed: Missing expression."
    else:
        # Assume alignment if input is valid, will be overridden on failure
        reflection_alignment = "Aligned with calculation goal."

    # --- Execute Calculation (using numexpr) ---
    if primary_result["error"] is None:
        try:
            # Import numexpr dynamically to check availability per call
            import numexpr
            logger_tools_diag.debug(f"Attempting to evaluate expression using numexpr: '{expression}'")
            # Evaluate the expression using numexpr.evaluate()
            # Use casting='safe' and potentially truedivide=True
            # Consider local_dict={} for safety if needed, though numexpr aims to be safe
            result_val = numexpr.evaluate(expression, local_dict={})
            # Convert result to standard Python float (handles numpy types)
            numeric_result = float(result_val.item() if hasattr(result_val, 'item') else result_val)

            if not np.isfinite(numeric_result): # Check for NaN or infinity
                    primary_result["error"] = "Evaluation resulted in non-finite number (NaN or Infinity)."
                    reflection_issues.append(primary_result["error"])
            else:
                    primary_result["result"] = numeric_result
                    reflection_status = "Success"
                    reflection_summary = f"Expression '{expression}' evaluated successfully using numexpr."
                    reflection_confidence = 1.0 # High confidence in numexpr calculation
                    reflection_preview = numeric_result

        except ImportError:
            primary_result["error"] = "Required library 'numexpr' not installed. Cannot perform safe evaluation."
            logger_tools_diag.error(primary_result["error"])
            reflection_issues.append("Missing dependency: numexpr.")
            reflection_summary = primary_result["error"]
        except SyntaxError as e_syntax:
            primary_result["error"] = f"Syntax error in mathematical expression: {e_syntax}"
            logger_tools_diag.warning(f"Syntax error evaluating '{expression}': {e_syntax}")
            reflection_issues.append(f"Invalid expression syntax: {e_syntax}")
            reflection_summary = primary_result["error"]
        except Exception as e_eval:
            # Catch other errors during numexpr evaluation (e.g., invalid names, unsupported functions)
            primary_result["error"] = f"Failed to evaluate expression using numexpr: {e_eval}"
            logger_tools_diag.error(f"Error evaluating expression '{expression}' with numexpr: {e_eval}", exc_info=True)
            reflection_issues.append(f"Numexpr evaluation error: {e_eval}.")
            reflection_summary = primary_result["error"]

    # --- Finalize Reflection ---
    if primary_result["error"]:
        reflection_status = "Failure" # Ensure status reflects error
        if reflection_summary == "Math calculation initialization failed.": # Update summary if error happened later
            reflection_summary = f"Math calculation failed: {primary_result['error']}"
        reflection_confidence = 0.1 # Low confidence on failure

    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

# --- Placeholder for Codebase Search Tool ---
def placeholder_codebase_search(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Placeholder for actual codebase search functionality.
    Returns an empty result set and a note that it's not implemented.
    """
    query = inputs.get("query", "N/A")
    logger_tools_diag.info(f"Executing PLACEHOLDER codebase search for query: '{query}'")

    summary_text = f"Placeholder: Codebase search for '{query}' - Actual implementation pending."
    primary_result = {
        "search_results": [],
        "summary": summary_text,
        "stdout": summary_text,
        "error": None
    }

    reflection = _create_reflection(
        status="Success", # The placeholder itself ran successfully
        summary="Placeholder codebase search executed. No actual search performed.",
        confidence=0.1, # Low confidence as it's a placeholder
        alignment="Partially aligned - acknowledges request but provides no data.",
        issues=["Actual codebase search functionality is not implemented. This is a placeholder."],
        preview=summary_text
    )
    return {**primary_result, "reflection": reflection}

# --- Helper for display_output ---
def _format_output_content(content: Any) -> str:
    """Formats content for display, handling dicts/lists with JSON."""
    if isinstance(content, (dict, list)):
        try:
            return json.dumps(content, indent=2, default=str) # pretty print
        except TypeError:
            return str(content) # fallback for non-serializable
    return str(content)

# Tool function for retrieving SPR definitions
def retrieve_spr_definitions(inputs: Dict[str, Any], context_for_action: ActionContext) -> Dict[str, Any]:
    task_key = context_for_action.task_key
    action_name = context_for_action.action_name
    logger_tools_diag.info(f"TOOLS.PY: Task '{task_key}' (Action: {action_name}) - Starting SPR retrieval.")

    spr_ids_input = inputs.get("spr_ids")
    spr_details_output: Dict[str, Any] = {}
    retrieval_errors: Dict[str, str] = {}
    all_found = True
    
    def default_failure_reflection_local(summary: str) -> Dict[str, Any]:
        return _create_reflection("Failure",summary,0.0,"N/A",["System Error: Default failure reflection"],None)

    try:
        spr_manager_instance = get_global_spr_manager() 

        if not spr_ids_input or (not isinstance(spr_ids_input, list) and spr_ids_input != "ALL"):
            logger_tools_diag.warning(f"Task '{task_key}': 'spr_ids' must be a non-empty list or 'ALL'.")
            return {
                "spr_details": {},
                "errors": {"input_error": "'spr_ids' must be a non-empty list or the string 'ALL'."},
                "reflection": default_failure_reflection_local("Input validation failed: 'spr_ids' missing or invalid type.")
            }

        if spr_ids_input == "ALL":
            all_sprs = spr_manager_instance.get_all_sprs()
            spr_details_output = {spr.spr_id: spr.to_dict() for spr in all_sprs}
        else:
            for spr_id in spr_ids_input:
                if not isinstance(spr_id, str):
                    retrieval_errors[str(spr_id)] = f"Invalid ID type {type(spr_id)}, must be string."
                    all_found = False
                    continue
                
                spr_detail = spr_manager_instance.get_spr(spr_id)
                if spr_detail:
                    spr_details_output[spr_id] = spr_detail.to_dict() if hasattr(spr_detail, 'to_dict') else spr_detail
                else:
                    retrieval_errors[spr_id] = "SPR not found."
                    all_found = False
        
        summary = "Successfully retrieved all specified SPRs." if all_found and spr_details_output else "Completed SPR retrieval with some issues or no results."
        if retrieval_errors: summary += f" Errors: {len(retrieval_errors)}"
        if spr_ids_input == "ALL": summary = f"Successfully retrieved all {len(spr_details_output)} SPRs from the Knowledge Graph."


        return {
            "spr_details": spr_details_output,
            "errors": retrieval_errors,
            "reflection": _create_reflection(
                status="Success" if spr_details_output else "Failure",
                summary=summary,
                confidence=0.95 if spr_details_output else 0.4,
                alignment="High",
                potential_issues=list(retrieval_errors.values()),
                raw_output_preview=f"Retrieved: {list(spr_details_output.keys())[:5]}"
            )
        }

    except RuntimeError as rne:
        logger_tools_diag.error(f"Task '{task_key}': Runtime error during SPR retrieval (likely from get_global_spr_manager): {rne}", exc_info=True)
        return {
            "spr_details": {}, "errors": {"initialization_error": str(rne)},
            "reflection": default_failure_reflection_local(f"SPRManager initialization failed: {rne}")
        }
    except Exception as e_retrieval:
        logger_tools_diag.error(f"Task '{task_key}': Unexpected error during SPR retrieval: {e_retrieval}", exc_info=True)
        return {
            "spr_details": {}, "errors": {"retrieval_error": f"Failed to retrieve SPRs: {e_retrieval}"},
            "reflection": default_failure_reflection_local(f"Unexpected error in SPR retrieval: {e_retrieval}")
        }

# --- MAIN FUNCTION ROUTER (Conceptual, used by Action Registry) ---
# This dictionary maps action_type strings to their respective tool functions.
# It's a conceptual guide for how the Action Registry might dispatch calls.
# The actual registration happens in action_registry.py.
TOOL_FUNCTIONS = {
    # Example: "execute_code": execute_code_sandboxed,
    # "generate_text_llm": invoke_llm,
    # etc. Will be populated by action_registry.py based on registrations.
}

# --- Utility for default reflections ---
def default_failure_reflection(summary: str) -> Dict[str, Any]:
    return _create_reflection(
        status="Failure",
        summary=summary,
        confidence=0.0,
        alignment="N/A",
        issues=["System Error: Default failure reflection"],
        preview=None
    )

# --- Tool for System Divergence Analysis ---

def _create_system_from_json(config: Dict[str, Any]) -> System:
    """Helper function to build a System object from a JSON config."""
    system = System(system_id=config['system_id'], name=config['name'])
    for param_conf in config.get('parameters', []):
        param_type = param_conf.pop('type', None)
        if param_type == "Gaussian":
            system.add_parameter(GaussianDistribution(**param_conf))
        elif param_type == "Histogram":
            system.add_parameter(HistogramDistribution(**param_conf))
        elif param_type == "String":
            system.add_parameter(StringParam(**param_conf))
    
    # If there's historical data, update the distributions
    if 'history_data' in config:
        for param_name, values in config['history_data'].items():
            if param_name in system.parameters:
                for value in values:
                    system.parameters[param_name].update(value)
    
    return system

def analyze_system_divergence(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Analyzes the divergence between two systems defined in JSON files.
    """
    system_a_path = inputs.get("system_a_path")
    system_b_path = inputs.get("system_b_path")
    method = inputs.get("method", "kld")

    if not system_a_path or not system_b_path:
        # Handle missing input error
        error_msg = "Input error: Both 'system_a_path' and 'system_b_path' are required."
        logger_tools_diag.error(error_msg)
        reflection = _create_reflection(
            status="Failure",
            summary=error_msg,
            confidence=0.0,
            alignment="N/A",
            issues=["Missing required input arguments."],
            preview=None
        )
        return {"error": error_msg, "reflection": reflection}

    try:
        with open(system_a_path, 'r') as f:
            config_a = json.load(f)
        with open(system_b_path, 'r') as f:
            config_b = json.load(f)

        system_a = _create_system_from_json(config_a)
        system_b = _create_system_from_json(config_b)

        divergence_score = system_a.calculate_divergence(system_b, method=method)
        
        analysis_summary = f"Divergence ({method.upper()}) between '{system_a.name}' and '{system_b.name}': {divergence_score:.4f}\\n"
        
        primary_result = {
            "divergence_score": divergence_score,
            "analysis_summary": analysis_summary
        }
        
        reflection = _create_reflection(
            status="Success",
            summary="Divergence analysis completed successfully.",
            confidence=0.95,
            alignment="Aligned with system comparison goal.",
            issues=None,
            preview=analysis_summary
        )
        return {**primary_result, "reflection": reflection}

    except Exception as e:
        error_msg = f"Failed to analyze system divergence: {e}"
        logger_tools_diag.error(error_msg, exc_info=True)
        reflection = _create_reflection(
            status="Failure",
            summary=error_msg,
            confidence=0.0,
            alignment="N/A",
            issues=[f"System Error: {e}"],
            preview=None
        )
        return {"error": error_msg, "reflection": reflection}

def compare_system_factors(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Provides a detailed, parameter-by-parameter comparison between two systems.
    """
    system_a_path = inputs.get("system_a_path")
    system_b_path = inputs.get("system_b_path")
    # Default methods; could be made configurable via inputs
    comparison_methods = ["kld", "emd", "value_diff"] 

    if not system_a_path or not system_b_path:
        error_msg = "Input error: Both 'system_a_path' and 'system_b_path' are required."
        logger_tools_diag.error(error_msg)
        return {"error": error_msg, "reflection": _create_reflection(status="Failure", summary=error_msg, issues=["Missing required inputs."])}

    try:
        with open(system_a_path, 'r') as f:
            config_a = json.load(f)
        with open(system_b_path, 'r') as f:
            config_b = json.load(f)

        system_a = _create_system_from_json(config_a)
        system_b = _create_system_from_json(config_b)

        parameter_comparison = []
        overall_kld = system_a.calculate_divergence(system_b, method='kld')
        overall_emd = system_a.calculate_divergence(system_b, method='emd')

        all_param_names = set(system_a.parameters.keys()) | set(system_b.parameters.keys())

        for name in sorted(list(all_param_names)):
            param_a = system_a.get_parameter(name)
            param_b = system_b.get_parameter(name)
            
            param_details = {"parameter_name": name}

            if param_a and param_b and type(param_a) == type(param_b):
                param_details.update({
                    "type": param_a.__class__.__name__,
                    "system_a_value": param_a.get_value(),
                    "system_b_value": param_b.get_value(),
                    "kld": param_a.kl_divergence(param_b),
                    "emd": param_a.earth_movers_distance(param_b)
                })
                if isinstance(param_a.get_value(), (int, float)) and isinstance(param_b.get_value(), (int, float)):
                    param_details["value_difference"] = param_a.get_value() - param_b.get_value()
                
            elif param_a and not param_b:
                param_details.update({"status": "unique_to_system_a", "value": param_a.get_value()})
            elif not param_a and param_b:
                param_details.update({"status": "unique_to_system_b", "value": param_b.get_value()})
            else:
                 param_details.update({"status": "type_mismatch", "system_a_type": type(param_a).__name__, "system_b_type": type(param_b).__name__})

            parameter_comparison.append(param_details)
        
        primary_result = {
            "comparison_summary": {
                "system_a_name": system_a.name,
                "system_b_name": system_b.name,
                "overall_kld": overall_kld,
                "overall_emd": overall_emd
            },
            "parameter_comparison": parameter_comparison
        }
        
        reflection = _create_reflection(
            status="Success",
            summary=f"Factor comparison between '{system_a.name}' and '{system_b.name}' complete.",
            confidence=0.98,
            alignment="Aligned with detailed system analysis goal.",
            issues=None,
            preview=f"Compared {len(parameter_comparison)} parameters. Overall KLD: {overall_kld:.4f}"
        )
        return {**primary_result, "reflection": reflection}

    except Exception as e:
        error_msg = f"Failed to compare system factors: {e}"
        logger_tools_diag.error(error_msg, exc_info=True)
        return {"error": error_msg, "reflection": _create_reflection(
            status="Failure", 
            summary=error_msg, 
            issues=[f"System Error: {e}"],
            confidence=0.0,
            alignment="N/A",
            preview=None
            )
        }

def analyze_workflow_impact(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Analyzes a workflow event log to identify root causes for changes in a specific system parameter.
    """
    run_id = inputs.get("run_id")
    parameter_name = inputs.get("parameter_name")

    if not run_id or not parameter_name:
        error_msg = "Input error: Both 'run_id' and 'parameter_name' are required."
        logger_tools_diag.error(error_msg)
        return {"error": error_msg, "reflection": _create_reflection(status="Failure", summary=error_msg, issues=["Missing required inputs."], confidence=0.0, alignment="N/A", preview=None)}

    event_log_path = os.path.join(config.OUTPUT_DIR, f"run_events_{run_id}.jsonl")
    if not os.path.exists(event_log_path):
        error_msg = f"Event log not found for run_id '{run_id}' at path '{event_log_path}'."
        logger_tools_diag.error(error_msg)
        return {"error": error_msg, "reflection": _create_reflection(status="Failure", summary=error_msg, issues=[f"Event log file not found."], confidence=0.1, alignment="N/A", preview=None)}

    try:
        events = []
        with open(event_log_path, 'r') as f:
            for line in f:
                events.append(json.loads(line))

        analysis = {}
        if parameter_name == "seconds_per_task":
            runtimes = {}
            for event in events:
                action = event.get("action_type")
                duration = event.get("duration_sec", 0)
                if action not in runtimes:
                    runtimes[action] = []
                runtimes[action].append(duration)
            
            analysis["type"] = "runtime_analysis"
            analysis["details"] = [{"action": k, "average_duration": np.mean(v), "count": len(v)} for k, v in runtimes.items()]
            analysis["summary"] = f"Analyzed runtimes for {len(events)} events across {len(runtimes)} unique actions."

        elif parameter_name == "tool_success_rate":
            statuses = {}
            for event in events:
                action = event.get("action_type")
                status = event.get("result", {}).get("reflection", {}).get("status", "Failure")
                if action not in statuses:
                    statuses[action] = {"Success": 0, "Failure": 0}
                statuses[action][status] += 1

            analysis["type"] = "success_rate_analysis"
            details = []
            for action, counts in statuses.items():
                total = counts["Success"] + counts["Failure"]
                rate = counts["Success"] / total if total > 0 else 0
                details.append({"action": action, "success_rate": rate, "success_count": counts["Success"], "failure_count": counts["Failure"]})
            analysis["details"] = details
            analysis["summary"] = f"Analyzed success rates for {len(events)} events across {len(statuses)} unique actions."
        
        else:
            analysis["type"] = "unsupported_parameter"
            analysis["summary"] = f"Analysis for parameter '{parameter_name}' is not currently supported."

        reflection = _create_reflection(
            status="Success",
            summary=f"Workflow impact analysis for '{parameter_name}' completed.",
            confidence=0.95,
            alignment="Aligned with root cause analysis goal.",
            issues=None,
            preview=analysis.get("summary")
        )
        return {"analysis": analysis, "reflection": reflection}

    except Exception as e:
        error_msg = f"Failed during workflow impact analysis: {e}"
        logger_tools_diag.error(error_msg, exc_info=True)
        return {"error": error_msg, "reflection": _create_reflection(status="Failure", summary=error_msg, issues=[f"System Error: {e}"], confidence=0.0, alignment="N/A", preview=None)}

def run_code_linter(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Runs a linter (flake8) on the project directory and returns the output.
    """
    target_directory = inputs.get("directory", "Three_PointO_ArchE")
    logger_tools_diag.info(f"Running linter on directory: {target_directory}")
    try:
        process = subprocess.run(
            ['flake8', target_directory],
            capture_output=True,
            text=True,
            check=False 
        )
        
        issues_found = process.stdout.strip().split('\\n') if process.stdout.strip() else []
        status = "Completed with issues" if issues_found else "Completed successfully"
        summary = f"Linter run complete. Found {len(issues_found)} issues."

        reflection = _create_reflection("Success", summary, 0.99, "Aligned with code quality goal.", issues_found, f"Found {len(issues_found)} issues.")
        return {"linter_report": {"status": status, "issues": issues_found}, "reflection": reflection}

    except FileNotFoundError:
        error_msg = "Linter tool 'flake8' not found. Please ensure it is installed."
        logger_tools_diag.error(error_msg)
        reflection = _create_reflection("Failure", error_msg, 0.1, "Misaligned, dependency missing.", [error_msg], None)
        return {"error": error_msg, "reflection": reflection}
    except Exception as e:
        error_msg = f"An unexpected error occurred during linting: {e}"
        logger_tools_diag.error(error_msg, exc_info=True)
        reflection = _create_reflection("Failure", error_msg, 0.1, "Misaligned, unexpected error.", [str(e)], None)
        return {"error": error_msg, "reflection": reflection}

def run_workflow_suite(inputs: Dict[str, Any], action_context: Optional[ActionContext] = None) -> Dict[str, Any]:
    """
    [IAR Enabled] Discovers and runs all workflows in the specified directory.
    """
    # Moved import here to break the circular dependency
    from .workflow_engine import WorkflowEngine 

    workflows_dir = inputs.get("directory", config.WORKFLOW_DIR)
    test_cases_file = inputs.get("test_cases_file")
    exclude_file = inputs.get("exclude_workflow_file")
    logger_tools_diag.info(f"Starting workflow suite run for directory: {workflows_dir}")

    test_cases = {}
    default_context = {}
    if test_cases_file and os.path.exists(test_cases_file):
        try:
            with open(test_cases_file, 'r') as f:
                test_config = json.load(f)
                test_cases = test_config.get("test_cases", {})
                default_context = test_config.get("default_context", {})
            logger_tools_diag.info(f"Loaded {len(test_cases)} specific test cases from {test_cases_file}.")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger_tools_diag.error(f"Failed to load or parse test cases file {test_cases_file}: {e}")

    try:
        # Get all .json files from the directory, excluding the one running the suite and the test case config
        all_workflow_files = [
            f for f in os.listdir(workflows_dir) 
            if f.endswith(".json") and f != exclude_file and (not test_cases_file or f != os.path.basename(test_cases_file))
        ]
        if exclude_file:
            logger_tools_diag.info(f"Excluding '{exclude_file}' from the test suite.")

        suite_summary = {
            "total_run": 0,
            "successful": [],
            "failed": [],
            "success_details": [],
            "failure_details": []
        }

        # Iterate through all found workflow files, not just the ones in test_cases
        for wf_file in all_workflow_files:
            logger_tools_diag.info(f"--- Running workflow: {wf_file} ---")
            suite_summary["total_run"] += 1
            
            # Determine the initial context for this specific workflow
            # Use the specific test case if available, otherwise use the default
            initial_context = test_cases.get(wf_file, default_context).copy()
            initial_context["workflow_run_id"] = f"suite_run_{uuid.uuid4().hex}"

            try:
                # Each workflow needs its own engine instance
                workflow_engine = WorkflowEngine(config)
                # We only need the filename, as the engine knows the directory
                final_context = workflow_engine.run_workflow(wf_file, initial_context)
                
                suite_summary["successful"].append(wf_file)
                suite_summary["success_details"].append({
                    "workflow": wf_file,
                    "final_status": final_context.get("workflow_status", "Unknown")
                })
                logger_tools_diag.info(f"--- Finished workflow: {wf_file} (Success) ---")
            except Exception as e:
                logger_tools_diag.error(f"Critical error running workflow {wf_file}: {e}", exc_info=True)
                suite_summary["failed"].append(wf_file)
                suite_summary["failure_details"].append({"file": wf_file, "reason": f"Critical engine error: {e}"})

        summary_text = f"Workflow suite run complete. Passed: {len(suite_summary['successful'])}. Failed: {len(suite_summary['failed'])}."
        reflection = _create_reflection("Success", summary_text, 1.0, "Aligned with testing goal.", None, summary_text)
        
        return {"suite_summary": suite_summary, "reflection": reflection}

    except Exception as e:
        error_msg = f"Failed during workflow suite run: {e}"
        logger_tools_diag.error(error_msg, exc_info=True)
        return {"error": error_msg, "reflection": _create_reflection(status="Failure", summary=error_msg, issues=[f"System Error: {e}"], confidence=0.0, alignment="N/A", preview=None)}

# --- END OF FILE 3.0ArchE/tools.py --- 