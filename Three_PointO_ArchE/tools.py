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
# Use relative imports for internal modules
try:
    from . import config # Access configuration settings
    from .llm_providers import get_llm_provider, get_model_for_provider, LLMProviderError # Import LLM helpers
    from .action_context import ActionContext # Import ActionContext from new file
    LLM_AVAILABLE = True
except ImportError as e:
    # Handle cases where imports might fail (e.g., missing dependencies)
    logging.getLogger(__name__).error(f"Failed import for tools.py (config or llm_providers): {e}. LLM tool may be unavailable.")
    LLM_AVAILABLE = False
    # Define fallback exception and config for basic operation
    class LLMProviderError(Exception): pass
    class FallbackConfig: SEARCH_PROVIDER='simulated_google'; SEARCH_API_KEY=None; LLM_DEFAULT_MAX_TOKENS=1024; LLM_DEFAULT_TEMP=0.7
    config = FallbackConfig()

import subprocess
import os
import shutil # For file operations
import uuid # For unique temp dir names

# --- Tool-Specific Configuration ---
# Get search provider settings from config
SEARCH_PROVIDER = getattr(config, 'SEARCH_PROVIDER', 'simulated_google').lower()
SEARCH_API_KEY = getattr(config, 'SEARCH_API_KEY', None) # API key needed if not using simulation
# Define path to the Node.js search script
NODE_SEARCH_SCRIPT_PATH = os.path.join(config.BASE_DIR, "ResonantiA", "browser_automation", "search.js")

logger = logging.getLogger(__name__)

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
        if num_results <= 0: num_results = 5; logger.warning("num_results must be positive, defaulting to 5.")
    except (ValueError, TypeError):
        num_results = 5; logger.warning(f"Invalid num_results value, defaulting to 5.")

    logger.info(f"Performing web search via '{provider_used}' for query: '{query}' (max {num_results} results)")

    # --- Execute Search (Simulation or Actual) ---
    try:
        if provider_used == "puppeteer_nodejs":
            if not os.path.exists(NODE_SEARCH_SCRIPT_PATH):
                primary_result["error"] = f"Node.js search script not found at {NODE_SEARCH_SCRIPT_PATH}"
                reflection_issues.append(primary_result["error"])
                reflection_summary = "Configuration error: Node.js search script missing."
            else:
                # Create a unique base temporary directory for the Node.js script to use for its run-specific archives
                # This will be cleaned up by this Python function.
                # The Node script will create a sub-directory within this.
                search_tool_temp_base_dir = os.path.join(config.OUTPUT_DIR, "search_tool_temp")
                os.makedirs(search_tool_temp_base_dir, exist_ok=True)
                # Pass this base dir to Node.js script so it knows where to create its unique run folder
                
                cmd = ["node", NODE_SEARCH_SCRIPT_PATH, query, str(num_results), "duckduckgo", search_tool_temp_base_dir]
                # TODO: Allow overriding search engine via inputs["search_engine_js"]
                
                logger.info(f"Executing Node.js search script: {' '.join(cmd)}")
                process = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=180) # Increased timeout for scraping/screenshots

                js_temp_archive_dir_abs = None
                if process.stderr:
                    logger.debug(f"Node.js script stderr:\n{process.stderr}")
                    for line in process.stderr.splitlines():
                        if "Archives for this run will be stored in:" in line:
                            js_temp_archive_dir_abs = line.split("Archives for this run will be stored in:")[-1].strip()
                            logger.info(f"Node.js script created archives in: {js_temp_archive_dir_abs}")
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
                                relative_path_from_node = item.get(archive_key)
                                # js_temp_archive_dir_abs is the specific run folder like .../search_archives/run-XXXXXX
                                # relative_path_from_node as returned by search.js is like search_archives/run-XXXXXX/file.html
                                # search_tool_temp_base_dir is .../search_tool_temp
                                
                                if relative_path_from_node and search_tool_temp_base_dir: # Check search_tool_temp_base_dir also
                                    # Construct absolute source path using the base dir given to Node and the relative path it returned
                                    abs_source_path = os.path.abspath(os.path.join(search_tool_temp_base_dir, relative_path_from_node))
                                    
                                    if os.path.exists(abs_source_path):
                                        file_basename = os.path.basename(abs_source_path)
                                        abs_dest_path = os.path.join(final_archives_base_dir, file_basename)
                                        try:
                                            shutil.copy2(abs_source_path, abs_dest_path)
                                            # Store path relative to OUTPUT_DIR for cleaner context
                                            item[archive_key] = os.path.relpath(abs_dest_path, config.OUTPUT_DIR)
                                            logger.debug(f"Copied {abs_source_path} to {abs_dest_path}. Stored rel path: {item[archive_key]}")
                                        except Exception as e_copy:
                                            logger.error(f"Failed to copy archive file {abs_source_path} to {abs_dest_path}: {e_copy}")
                                            item[archive_key] = None # Nullify if copy failed
                                    else:
                                        logger.warning(f"Archived file reported by Node.js script not found at {abs_source_path} (original relative: {relative_path_from_node})")
                                        item[archive_key] = None
                                elif relative_path_from_node:
                                    logger.warning(f"Could not resolve absolute path for {relative_path_from_node} as search_tool_temp_base_dir was not found.")
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
                        logger.error(f"Error processing results from Node.js script: {e_processing_results}", exc_info=True)
                        primary_result["error"] = f"Error processing results from Node.js script: {str(e_processing_results)}"
                        reflection_issues.append("Result processing error.")
                        reflection_summary = "Error processing script results."
                else:
                    primary_result["error"] = f"Node.js search script failed (Code {process.returncode}): {process.stderr[:500]}"
                    reflection_issues.append(f"Node.js script execution error: {process.stderr[:100]}")
                    reflection_summary = "Node.js script execution failed."
                    logger.error(f"Node.js search script stderr: {process.stderr}")
                
                # Cleanup the temporary directory created by the Node.js script, if identified
                if js_temp_archive_dir_abs and os.path.exists(js_temp_archive_dir_abs):
                    try:
                        shutil.rmtree(js_temp_archive_dir_abs)
                        logger.info(f"Cleaned up Node.js temporary archive directory: {js_temp_archive_dir_abs}")
                    except Exception as e_cleanup:
                        logger.error(f"Failed to clean up Node.js temporary archive directory {js_temp_archive_dir_abs}: {e_cleanup}")

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
        logger.error(f"Unexpected error during search operation: {e_search}", exc_info=True)
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
    prompt = inputs.get("prompt") # For single-turn completion
    messages = inputs.get("messages") # For chat-based completion (list of dicts)
    provider_name_override = inputs.get("provider") # Optional override for provider
    model_name_override = inputs.get("model") # Optional override for model
    # Get generation parameters, using config defaults if not provided
    max_tokens = inputs.get("max_tokens", getattr(config, 'LLM_DEFAULT_MAX_TOKENS', 1024))
    temperature = inputs.get("temperature", getattr(config, 'LLM_DEFAULT_TEMP', 0.7))
    # Collect any other inputs to pass as extra parameters to the provider's API call
    standard_keys = ['prompt', 'messages', 'provider', 'model', 'max_tokens', 'temperature']
    extra_params = {k: v for k, v in inputs.items() if k not in standard_keys}

    # --- Input Validation ---
    if not prompt and not messages:
        primary_result["error"] = "LLM invocation requires either 'prompt' (string) or 'messages' (list of dicts) input."
        reflection_issues = ["Missing required input ('prompt' or 'messages')."]
        reflection_summary = "Input validation failed: Missing prompt/messages."
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}
    if prompt and messages:
        logger.warning("Both 'prompt' and 'messages' provided to invoke_llm. Prioritizing 'messages' for chat completion.")
        prompt = None # Clear prompt if messages are present

    # --- Execute LLM Call ---
    try:
        # Get the appropriate LLM provider instance (handles config lookup, key errors)
        provider = get_llm_provider(provider_name_override)
        provider_name_used = provider._provider_name # Get actual provider name used
        primary_result["provider_used"] = provider_name_used

        # Get the appropriate model name for the provider
        model_to_use = model_name_override or get_model_for_provider(provider_name_used)
        primary_result["model_used"] = model_to_use

        logger.info(f"Invoking LLM: Provider='{provider_name_used}', Model='{model_to_use}'")
        # Prepare common API arguments
        api_kwargs = {"max_tokens": max_tokens, "temperature": temperature, **extra_params}

        # Call the appropriate provider method
        response_text = ""
        start_time = time.time()
        if messages:
            # Use generate_chat for message lists
            response_text = provider.generate_chat(messages=messages, model=model_to_use, **api_kwargs)
        elif prompt:
            # Use generate for single prompts
            response_text = provider.generate(prompt=prompt, model=model_to_use, **api_kwargs)
        duration = time.time() - start_time

        # --- Process Successful Response ---
        primary_result["response_text"] = response_text
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
        logger.info(f"LLM invocation successful (Duration: {duration:.2f}s).")

    # --- Handle LLM Provider Errors ---
    except (ValueError, LLMProviderError) as e_llm: # Catch validation errors or specific provider errors
        error_msg = f"LLM invocation failed: {e_llm}"
        logger.error(error_msg, exc_info=True if isinstance(e_llm, LLMProviderError) else False)
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
        logger.error(error_msg, exc_info=True)
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
    [IAR Enabled] Displays content provided in the 'content' input key to the
    primary output stream (typically the console). Handles basic formatting.
    """
    # --- Input Extraction ---
    content = inputs.get("content", "<No Content Provided to Display>")
    display_format = inputs.get("format", "auto").lower() # e.g., auto, json, text

    # --- Initialize Results & Reflection ---
    primary_result = {"status": "Error", "error": None} # Default to error
    reflection_status = "Failure"
    reflection_summary = "Display output initialization failed."
    reflection_confidence = 0.0
    reflection_alignment = "N/A"
    reflection_issues: List[str] = ["Initialization error."]
    reflection_preview = None

    # --- Format and Display ---
    try:
        display_str: str
        # Format content based on type or specified format
        if display_format == 'json' or (display_format == 'auto' and isinstance(content, (dict, list))):
            try:
                # Pretty-print JSON
                display_str = json.dumps(content, indent=2, default=str) # Use default=str for safety
            except TypeError as json_err:
                display_str = f"[JSON Formatting Error: {json_err}]\nFallback Representation:\n{repr(content)}"
                reflection_issues.append(f"JSON serialization failed: {json_err}")
        else: # Default to string conversion
            display_str = str(content)

        reflection_preview = display_str # Use the formatted string for preview (truncated later)

        # Print formatted content to standard output
        logger.info("Displaying output content via print().")
        # Add header/footer for clarity in console logs
        print("\n--- Arche Display Output (v3.0) ---")
        print(display_str)
        print("-----------------------------------\n")

        primary_result["status"] = "Displayed"
        reflection_status = "Success"
        reflection_summary = "Content successfully formatted and printed to standard output."
        reflection_confidence = 1.0 # High confidence in successful display action
        reflection_alignment = "Aligned with goal of presenting information."
        # Clear initial issue if successful, keep formatting issue if it occurred
        reflection_issues = [iss for iss in reflection_issues if "JSON serialization failed" in iss] if reflection_issues else None

    except Exception as e_display:
        # Catch errors during formatting or printing
        error_msg = f"Failed to format or display output: {e_display}"
        logger.error(error_msg, exc_info=True)
        primary_result["error"] = error_msg
        reflection_status = "Failure"
        reflection_summary = f"Display output failed: {error_msg}"
        reflection_confidence = 0.1
        reflection_alignment = "Failed to present information."
        reflection_issues = [f"Display Error: {e_display}"]
        # Attempt fallback display using repr()
        try:
            print("\n--- Arche Display Output (Fallback Repr) ---")
            print(repr(content))
            print("--------------------------------------------\n")
            primary_result["status"] = "Displayed (Fallback)"
            reflection_issues.append("Used fallback repr() for display.")
        except Exception as fallback_e:
            logger.critical(f"Fallback display using repr() also failed: {fallback_e}")
            primary_result["error"] = f"Primary display failed: {e_display}. Fallback display failed: {fallback_e}"

    # --- Final Return ---
    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

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
    logger.error("Direct call to tools.run_cfp detected. Action 'run_cfp' should be executed via the action registry using the run_cfp_action wrapper.")
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
            logger.debug(f"Attempting to evaluate expression using numexpr: '{expression}'")
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
            logger.error(primary_result["error"])
            reflection_issues.append("Missing dependency: numexpr.")
            reflection_summary = primary_result["error"]
        except SyntaxError as e_syntax:
            primary_result["error"] = f"Syntax error in mathematical expression: {e_syntax}"
            logger.warning(f"Syntax error evaluating '{expression}': {e_syntax}")
            reflection_issues.append(f"Invalid expression syntax: {e_syntax}")
            reflection_summary = primary_result["error"]
        except Exception as e_eval:
            # Catch other errors during numexpr evaluation (e.g., invalid names, unsupported functions)
            primary_result["error"] = f"Failed to evaluate expression using numexpr: {e_eval}"
            logger.error(f"Error evaluating expression '{expression}' with numexpr: {e_eval}", exc_info=True)
            reflection_issues.append(f"Numexpr evaluation error: {e_eval}.")
            reflection_summary = primary_result["error"]

    # --- Finalize Reflection ---
    if primary_result["error"]:
        reflection_status = "Failure" # Ensure status reflects error
        if reflection_summary == "Math calculation initialization failed.": # Update summary if error happened later
            reflection_summary = f"Math calculation failed: {primary_result['error']}"
        reflection_confidence = 0.1 # Low confidence on failure

    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

# --- END OF FILE 3.0ArchE/tools.py --- 