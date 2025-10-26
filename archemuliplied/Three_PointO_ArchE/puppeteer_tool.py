import logging
import json
import os
from typing import Dict, Any, List, Optional

# Assuming execute_code is available via action_registry directly or passed
# For direct use, we might need a way to invoke other actions from here.
# For now, let's assume this tool gets `execute_code` as an injected dependency
# or, more cleanly, we rely on the `action_registry.execute_action` to handle it.

# We'll pass the execute_action callable to this tool when it's registered.

logger = logging.getLogger(__name__)

# Helper function to create the standardized IAR reflection dictionary (reused)
def _create_reflection(status: str, summary: str, confidence: Optional[float], alignment: Optional[str], issues: Optional[List[str]], preview: Any) -> Dict[str, Any]:
    if confidence is not None: confidence = max(0.0, min(1.0, confidence))
    issues_list = issues if issues else None
    try:
        preview_str = json.dumps(preview, default=str) if isinstance(preview, (dict, list)) else str(preview)
        if preview_str and len(preview_str) > 150: preview_str = preview_str[:150] + "..."
    except Exception:
        try: preview_str = str(preview); preview_str = preview_str[:150] + "..." if len(preview_str) > 150 else preview_str
        except Exception: preview_str = "[Preview Error]"
    return {"status": status, "summary": summary, "confidence": confidence, "alignment_check": alignment if alignment else "N/A", "potential_issues": issues_list, "raw_output_preview": preview_str}

# The actual tool function for Puppeteer search
def run_puppeteer_search(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    [IAR Enabled] Executes a headless browser search using the `ResonantiA/browser_automation/search.js` script.
    Requires Node.js and Puppeteer dependencies installed on the system where the `execute_code` action runs.
    Returns search results parsed from stdout and an IAR reflection.
    
    IAR Contract Fulfillment:
      - confidence: Based on successful execution (exit code 0), presence of results, and absence of stderr.
                    Lower if errors, warnings, or no results.
      - potential_issues:
          - "Node.js/Puppeteer script failed: [stderr content]"
          - "No search results extracted (page structure changed or query failed)"
          - "JSON parsing error from script stdout: [error_message]"
          - "Puppeteer launch/browser error"
          - "External script execution (via CodeExecutor) carries inherent risks."
      - status: "Success" if JSON output parsed with results, "Failure" otherwise.
      - alignment_check: "Aligned with information gathering goal."
    """
    # Assume `execute_action` (from action_registry) is how we run other actions
    # We need to make sure this tool is registered with `execute_action` as an injected dependency
    # Or, for simplicity in this file, we assume `action_registry` will handle the `execute_code` call itself.
    # Let's adjust action_registry.py to inject `execute_action` into tools when they need to call other tools.

    query = inputs.get("query")
    num_results = inputs.get("num_results", 5)
    search_engine = inputs.get("search_engine", "google") # Default to Google now
    debug_mode = inputs.get("debug", False) # Pass debug flag to JS

    primary_result = {"results": [], "error": None}
    reflection_status = "Failure"
    reflection_summary = "Puppeteer search failed to initialize."
    reflection_confidence = 0.0
    reflection_issues = []
    reflection_preview = None

    if not query or not isinstance(query, str):
        primary_result["error"] = "Search query (string) is required."
        reflection_issues.append(primary_result["error"])
        reflection_summary = "Input validation failed: Missing query."
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}
    
    # Ensure num_results is a sensible integer
    try:
        num_results = int(num_results)
        if num_results <= 0: num_results = 5; logger.warning("num_results must be positive, defaulting to 5.")
    except (ValueError, TypeError):
        num_results = 5; logger.warning(f"Invalid num_results value, defaulting to 5.")

    # Construct the command to run the JavaScript file using Node.js via execute_code
    # Align path with repository browser_search directory
    js_script_path = os.path.join(os.path.dirname(__file__), "browser_search", "standalone_search.js")
    if not os.path.exists(js_script_path):
        primary_result["error"] = f"Puppeteer script not found at {js_script_path}"
        reflection_issues.append(primary_result["error"])
        reflection_summary = "Puppeteer script missing."
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, "N/A", reflection_issues, reflection_preview)}

    # Parameters for the JavaScript script are passed as CLI arguments
    js_args = [
        f"--query={query}",
        f"--numResults={num_results}",
        f"--searchEngine={search_engine}"
    ]
    if debug_mode:
        js_args.append("--debug")

    js_code_to_run = f"node {js_script_path} {' '.join(js_args)}"
    
    logger.info(f"Executing Puppeteer search: {js_code_to_run}")

    # Call the `execute_code` action to run the Node.js script
    # This assumes execute_action is in scope, or we inject it properly
    # For this pattern, we'll call it via its fully qualified path (conceptual) to avoid circular imports
    # Prefer direct subprocess to avoid requiring bash mode in code_executor
    import subprocess
    try:
        proc = subprocess.run(js_code_to_run.split(" "), capture_output=True, text=True, timeout=90)
        stdout = proc.stdout
        stderr = proc.stderr
        exit_code = proc.returncode
        exec_error = None
    except Exception as e:
        stdout = ""; stderr = str(e); exit_code = -1; exec_error = str(e)

    # Process the result from the `execute_code` action
    # stdout, stderr, exit_code, exec_error already set above

    if exec_error or exit_code != 0:
        primary_result["error"] = f"Puppeteer script execution failed: {exec_error or 'Non-zero exit code'} ({exit_code}). Stderr: {stderr}"
        reflection_issues.append(primary_result["error"])
        reflection_summary = "Puppeteer script failed to run or crashed."
        reflection_confidence = 0.0
    else:
        try:
            # Expected output from search.js is a JSON string to stdout
            parsed_results = json.loads(stdout)
            if not isinstance(parsed_results, list):
                raise ValueError("Expected JSON array of results, got different type.")
            
            primary_result["results"] = parsed_results
            reflection_status = "Success"
            reflection_summary = f"Puppeteer search completed successfully. Found {len(parsed_results)} results."
            reflection_confidence = 0.9 # High if executed successfully and parsed JSON
            reflection_alignment = "Aligned with information gathering goal."
            reflection_preview = parsed_results[:1] if parsed_results else None # Preview first result

            if not parsed_results:
                reflection_issues.append("No search results extracted (page structure changed or query failed).")
                reflection_confidence = 0.5 # Lower confidence if no results
                reflection_status = "Partial" # Partial success if no results but no script error
            if stderr: # Warnings or non-critical errors from the JS script
                reflection_issues.append(f"Puppeteer script reported warnings/errors to stderr: {stderr[:150]}...")
                reflection_confidence = max(0.6, reflection_confidence * 0.8) # Reduce confidence for stderr

        except json.JSONDecodeError as e:
            primary_result["error"] = f"JSON parsing error from Puppeteer script stdout: {e}. Raw stdout: {stdout[:200]}..."
            reflection_issues.append(primary_result["error"])
            reflection_summary = "Puppeteer script returned malformed JSON."
            reflection_confidence = 0.1
        except ValueError as e:
            primary_result["error"] = f"Data format error from Puppeteer script: {e}. Raw stdout: {stdout[:200]}..."
            reflection_issues.append(primary_result["error"])
            reflection_summary = "Puppeteer script returned unexpected data format."
            reflection_confidence = 0.1
        except Exception as e:
            primary_result["error"] = f"Unexpected error processing Puppeteer script output: {e}. Raw stdout: {stdout[:200]}..."
            reflection_issues.append(primary_result["error"])
            reflection_summary = "Unexpected error in Python wrapper during output processing."
            reflection_confidence = 0.0
            
    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, "Aligned with information gathering goal.", reflection_issues, reflection_preview)} 