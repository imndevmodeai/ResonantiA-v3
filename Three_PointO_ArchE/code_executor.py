# --- START OF FILE 3.0ArchE/code_executor.py ---
# ResonantiA Protocol v3.0 - code_executor.py
# Executes code snippets securely using sandboxing (Docker recommended).
# Includes mandatory Integrated Action Reflection (IAR) output.
# WARNING: Improper configuration or use (especially disabling sandbox) is a MAJOR security risk.

import logging
import subprocess # For running external processes (docker, interpreters)
import tempfile # For creating temporary files/directories for code
import os
import json
import platform # Potentially useful for platform-specific commands/paths
import sys # To find python executable for subprocess fallback
import time # For timeouts and potentially timestamps
import shutil # Added for script copying
from typing import Dict, Any, Optional, List, Tuple # Expanded type hints
# Use relative imports for configuration
try:
    from . import config
except ImportError:
    # Fallback config if running standalone or package structure differs
    class FallbackConfig:
        CODE_EXECUTOR_SANDBOX_METHOD='subprocess'; CODE_EXECUTOR_USE_SANDBOX=True;
        CODE_EXECUTOR_DOCKER_IMAGE='python:3.11-slim'; CODE_EXECUTOR_TIMEOUT=30;
        CODE_EXECUTOR_DOCKER_MEM_LIMIT="256m"; CODE_EXECUTOR_DOCKER_CPU_LIMIT="0.5"
    config = FallbackConfig(); logging.warning("config.py not found for code_executor, using fallback configuration.")

logger = logging.getLogger(__name__)

# --- IAR Helper Function ---
# (Reused for consistency)
def _create_reflection(status: str, summary: str, confidence: Optional[float], alignment: Optional[str], issues: Optional[List[str]], preview: Any) -> Dict[str, Any]:
    """Helper function to create the standardized IAR reflection dictionary."""
    if confidence is not None: confidence = max(0.0, min(1.0, confidence))
    issues_list = issues if issues else None
    try:
        preview_str = str(preview) if preview is not None else None
        if preview_str and len(preview_str) > 150:
            preview_str = preview_str[:150] + "..."
    except Exception:
        preview_str = "[Preview Error]"
    return {"status": status, "summary": summary, "confidence": confidence, "alignment_check": alignment if alignment else "N/A", "potential_issues": issues_list, "raw_output_preview": preview_str}

# --- Sandboxing Configuration & Checks ---
# Read configuration settings, providing defaults if missing
SANDBOX_METHOD_CONFIG = getattr(config, 'CODE_EXECUTOR_SANDBOX_METHOD', 'subprocess').lower()
USE_SANDBOX_CONFIG = getattr(config, 'CODE_EXECUTOR_USE_SANDBOX', True)
DOCKER_IMAGE = getattr(config, 'CODE_EXECUTOR_DOCKER_IMAGE', "python:3.11-slim")
TIMEOUT_SECONDS = int(getattr(config, 'CODE_EXECUTOR_TIMEOUT', 60)) # Use integer timeout
DOCKER_MEM_LIMIT = getattr(config, 'CODE_EXECUTOR_DOCKER_MEM_LIMIT', "512m")
DOCKER_CPU_LIMIT = getattr(config, 'CODE_EXECUTOR_DOCKER_CPU_LIMIT', "1.0")

# Determine the actual sandbox method to use based on config
sandbox_method_resolved: str
if not USE_SANDBOX_CONFIG:
    sandbox_method_resolved = 'none'
    if SANDBOX_METHOD_CONFIG != 'none':
        logger.warning("CODE_EXECUTOR_USE_SANDBOX is False in config. Overriding method to 'none'. SIGNIFICANT SECURITY RISK.")
elif SANDBOX_METHOD_CONFIG in ['docker', 'subprocess', 'none']:
    sandbox_method_resolved = SANDBOX_METHOD_CONFIG
else:
    logger.warning(f"Invalid CODE_EXECUTOR_SANDBOX_METHOD '{SANDBOX_METHOD_CONFIG}' in config. Defaulting to 'subprocess'.")
    sandbox_method_resolved = 'subprocess' # Default to subprocess if config value is invalid

# Check Docker availability if 'docker' method is resolved
DOCKER_AVAILABLE = False
if sandbox_method_resolved == 'docker':
    try:
        # Run 'docker info' to check daemon connectivity. Capture output to suppress it.
        docker_info_cmd = ["docker", "info"]
        process = subprocess.run(docker_info_cmd, check=True, capture_output=True, timeout=5)
        DOCKER_AVAILABLE = True
        logger.info("Docker runtime detected and appears responsive.")
    except FileNotFoundError:
        logger.warning("Docker command not found. Docker sandbox unavailable. Will fallback if possible.")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Docker daemon check failed (command {' '.join(docker_info_cmd)} returned error {e.returncode}). Docker sandbox likely unavailable. Stderr: {e.stderr.decode(errors='ignore')}")
    except subprocess.TimeoutExpired:
        logger.warning("Docker daemon check timed out. Docker sandbox likely unavailable.")
    except Exception as e_docker_check:
        logger.warning(f"Unexpected error checking Docker status: {e_docker_check}. Assuming Docker unavailable.")

# --- Main Execution Function ---
def execute_code(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    [IAR Enabled] Executes a code snippet or script using the configured sandbox method.
    Validates inputs, selects execution strategy (Docker, subprocess, none),
    runs the code, and returns results including stdout, stderr, exit code,
    error messages, and a detailed IAR reflection.

    Args:
        inputs (Dict[str, Any]): Dictionary containing:
            language (str): The programming language (e.g., 'python', 'javascript', 'python_script'). Required.
            code (str): The code snippet or script path to execute. Required.
            input_data (str, optional): Data to be passed as standard input to the code. Defaults to "".
            prompt_vars (Dict[str, str], optional): Environment variables to set for the execution.

    Returns:
        Dict[str, Any]: Dictionary containing execution results and IAR reflection:
            stdout (str): Standard output from the executed code.
            stderr (str): Standard error output from the executed code.
            exit_code (int): Exit code of the executed process (-1 on setup/timeout error).
            error (Optional[str]): Error message if execution failed before running code.
            sandbox_method_used (str): The actual sandbox method employed ('docker', 'subprocess', 'none').
            reflection (Dict[str, Any]): Standardized IAR dictionary.
    """
    language = inputs.get("language")
    code = inputs.get("code")
    # Preserve the original input_data for logging/type checking, create new var for stdin
    original_input_data_val = inputs.get("input_data", "")
    prompt_vars = inputs.get("prompt_vars", None) # Get prompt_vars
    input_data_for_stdin: str

    logger.debug(f"Code Executor: Received original_input_data_val type: {type(original_input_data_val)}, value (first 200 chars): {str(original_input_data_val)[:200]}")

    # --- Initialize Results & Reflection ---
    primary_result = {"stdout": "", "stderr": "", "exit_code": -1, "error": None, "sandbox_method_used": "N/A"}
    reflection_status = "Failure"
    reflection_summary = "Code execution initialization failed."
    reflection_confidence = 0.0
    reflection_alignment = "N/A"
    reflection_issues: List[str] = [] # Use list for potential issues
    reflection_preview = None

    # --- Input Validation ---
    if not language or not isinstance(language, str):
        primary_result["error"] = "Missing or invalid 'language' string input."; reflection_issues.append(primary_result["error"])
    elif not code or not isinstance(code, str):
        primary_result["error"] = "Missing or invalid 'code' string input."; reflection_issues.append(primary_result["error"])

    # Process input_data specifically for stdin
    if isinstance(original_input_data_val, dict):
        logger.debug(f"Code Executor: original_input_data_val is a dict. Attempting json.dumps.")
        try:
            input_data_for_stdin = json.dumps(original_input_data_val)
            logger.debug(f"Code Executor: input_data_for_stdin after json.dumps (first 200 chars): {input_data_for_stdin[:200]}")
        except TypeError as e_json:
            primary_result["error"] = f"Invalid 'input_data' dictionary: Cannot serialize to JSON ({e_json})."
            reflection_issues.append(primary_result["error"])
            input_data_for_stdin = "" # Fallback to empty string on error
    elif isinstance(original_input_data_val, str):
        input_data_for_stdin = original_input_data_val
        logger.debug(f"Code Executor: original_input_data_val was already a string (first 200 chars): {input_data_for_stdin[:200]}")
    else: # Not a dict, not a string
        logger.warning(f"Code Executor: original_input_data_val type is {type(original_input_data_val)}. Attempting str() conversion for stdin.")
        try:
            input_data_for_stdin = str(original_input_data_val)
        except Exception as e_str_conv:
            primary_result["error"] = f"Could not convert input_data of type {type(original_input_data_val)} to string for stdin: {e_str_conv}"
            reflection_issues.append(primary_result["error"])
            input_data_for_stdin = "" # Fallback

    if primary_result["error"]: # Check if any error occurred during input validation or input_data processing
        reflection_summary = f"Input processing failed: {primary_result['error']}"
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

    language = language.lower() # Normalize language name
    method_to_use = sandbox_method_resolved # Use the resolved method based on config and checks
    primary_result["sandbox_method_used"] = method_to_use # Record the method being attempted

    logger.info(f"Attempting to execute '{language}' code using sandbox method: '{method_to_use}'")

    # Prepare environment variables for the execution
    effective_env = os.environ.copy()
    if prompt_vars:
        if isinstance(prompt_vars, dict):
            # Ensure all prompt_vars are strings
            str_prompt_vars = {str(k): str(v) for k, v in prompt_vars.items()}
            effective_env.update(str_prompt_vars)
            logger.debug(f"Updated effective_env with prompt_vars: {str_prompt_vars}")
        else:
            logger.warning(f"prompt_vars were provided but not a dict: {type(prompt_vars)}. Ignoring.")

    # --- Select Execution Strategy ---
    exec_result: Dict[str, Any] = {} # Dictionary to store results from internal execution functions
    if method_to_use == 'docker':
        if DOCKER_AVAILABLE:
            # Pass only prompt_vars for Docker -e flags for clarity, not the whole effective_env
            docker_env_vars = {str(k): str(v) for k, v in prompt_vars.items()} if prompt_vars and isinstance(prompt_vars, dict) else None
            exec_result = _execute_with_docker(language, code, input_data_for_stdin, docker_env_vars)
        else:
            # Fallback if Docker configured but unavailable
            logger.warning("Docker configured but unavailable. Falling back to 'subprocess' (less secure).")
            primary_result["sandbox_method_used"] = 'subprocess' # Update actual method used
            reflection_issues.append("Docker unavailable, fell back to subprocess.")
            exec_result = _execute_with_subprocess(language, code, input_data_for_stdin, effective_env) # Pass full env
            if exec_result.get("error"): # If subprocess also failed (e.g., interpreter missing)
                reflection_issues.append(f"Subprocess fallback failed: {exec_result.get('error')}")
    elif method_to_use == 'subprocess':
        logger.warning("Executing code via 'subprocess' sandbox. This provides limited isolation and is less secure than Docker.")
        exec_result = _execute_with_subprocess(language, code, input_data_for_stdin, effective_env) # Pass full env
    elif method_to_use == 'none':
        logger.critical("Executing code with NO SANDBOX ('none'). This is EXTREMELY INSECURE and should only be used in trusted debugging environments with full awareness of risks.")
        reflection_issues.append("CRITICAL SECURITY RISK: Code executed without sandbox.")
        # Use subprocess logic for actual execution, but flag clearly that no sandbox was intended
        exec_result = _execute_with_subprocess(language, code, input_data_for_stdin, effective_env) # Pass full env
        exec_result["note"] = "Executed with NO SANDBOX ('none' method)." # Add note to result
    else: # Should not happen due to resolution logic, but safeguard
        exec_result = {"error": f"Internal configuration error: Unsupported sandbox method '{method_to_use}' resolved.", "exit_code": -1}

    # --- Process Execution Result and Generate IAR ---
    # Update primary result fields from the execution outcome
    primary_result.update({k: v for k, v in exec_result.items() if k in primary_result})
    primary_result["error"] = exec_result.get("error", primary_result.get("error")) # Prioritize error from execution

    # Determine final IAR based on outcome
    exit_code = primary_result["exit_code"]
    stderr = primary_result["stderr"]
    stdout = primary_result["stdout"]
    error = primary_result["error"]

    if error: # Indicates failure *before* or *during* execution setup (e.g., Docker error, timeout, interpreter not found)
        reflection_status = "Failure"
        reflection_summary = f"Code execution failed for language '{language}': {error}"
        reflection_confidence = 0.0
        reflection_alignment = "Failed to execute code."
        reflection_issues.append(f"Execution setup/runtime error: {error}") # Add specific error to issues
        reflection_preview = stderr[:150] + "..." if stderr else None
    elif exit_code != 0:
        reflection_status = "Failure"
        reflection_summary = f"Code execution finished with non-zero exit code: {exit_code}."
        reflection_confidence = 0.3 # Higher than setup error, code ran but failed
        reflection_alignment = "Code executed but resulted in an error."
        reflection_issues.append(f"Runtime Error (Exit Code: {exit_code})")
        # Include a preview of stderr if available, truncated for brevity
        stderr_preview = (stderr[:70] + "...") if stderr and len(stderr) > 70 else stderr
        reflection_issues.append(f"Check stderr for details: {stderr_preview}") 
        reflection_preview = stdout[:150] + "..." if stdout else None
    else: # Successful execution (exit code 0)
        reflection_status = "Success"
        reflection_summary = f"Code executed successfully for language '{language}'."
        reflection_confidence = 0.95 # High confidence for successful run
        reflection_alignment = "Code executed as expected."
        reflection_preview = stdout[:150] + "..." if stdout else None
        
        # Attempt to parse stdout as JSON if it's not empty
        if stdout:
            try:
                parsed_stdout = json.loads(stdout)
                if isinstance(parsed_stdout, dict):
                    logger.info("Successfully parsed stdout as JSON and merged into results.")
                    primary_result["raw_stdout"] = stdout # Store original stdout
                    primary_result["stdout"] = parsed_stdout # Replace stdout with parsed dict
                    # Merge the parsed dictionary into the primary_result
                    # This makes its keys directly accessible (e.g., result['actual_output_key'])
                    for key, value in parsed_stdout.items():
                        if key not in primary_result: # Avoid overwriting standard keys like 'exit_code'
                            primary_result[key] = value
                        else:
                            logger.warning(f"Key '{key}' from parsed stdout conflicts with standard result key. Not overwriting.")
                    reflection_summary += " Output parsed as JSON."
                    reflection_issues.append("Output successfully parsed as JSON.") # Add as an issue/note
                else:
                    # Stdout was valid JSON, but not a dictionary. Keep stdout as string.
                    logger.info("Stdout parsed as JSON, but was not a dictionary. Storing as raw string.")
                    reflection_issues.append("Output was valid JSON but not an object, stored as string.")
            except json.JSONDecodeError:
                logger.info("Stdout was not valid JSON. Storing as raw string.")
                reflection_issues.append("Output was not valid JSON.") # Add as an issue/note

    primary_result["reflection"] = _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)
    return primary_result

# --- Internal Helper: Docker Execution ---
def _execute_with_docker(language: str, code: str, input_data: str, env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Executes code inside a Docker container. Returns partial result dict."""
    # Define language-specific interpreters and script filenames within the container
    exec_details: Dict[str, Tuple[str, str]] = {
        'python': ('python', 'script.py'),         # For executing Python code strings
        'python_script': ('python', 'script.py'),  # For executing Python script files
        'javascript': ('node', 'script.js'),
        # Future: 'bash': ('bash', 'script.sh')
    }

    if language not in exec_details:
        return {"error": f"Docker execution unsupported for language: '{language}'.", "exit_code": -1, "stdout": "", "stderr": ""}

    interpreter, script_filename_in_container = exec_details[language]
    temp_dir_obj = None # For ensuring cleanup with try/finally

    try:
        temp_dir_obj = tempfile.TemporaryDirectory(prefix="resonatia_docker_exec_")
        temp_dir = temp_dir_obj.name
        
        code_filepath_in_temp = os.path.join(temp_dir, script_filename_in_container)

        if language.endswith('_script'): # e.g. 'python_script'
            host_script_path = code # 'code' parameter is the host path to the script
            if not os.path.isfile(host_script_path):
                logger.error(f"Script file for Docker execution not found on host: {host_script_path}")
                return {"error": f"Script file not found on host: {host_script_path}", "exit_code": -1, "stdout": "", "stderr": ""}
            try:
                shutil.copy2(host_script_path, code_filepath_in_temp)
                logger.debug(f"Copied script '{host_script_path}' to temporary Docker mount target '{code_filepath_in_temp}'.")
            except Exception as e_copy:
                logger.error(f"Failed to copy script '{host_script_path}' to temp dir '{temp_dir}': {e_copy}")
                return {"error": f"Failed to copy script to temp dir for Docker: {e_copy}", "exit_code": -1, "stdout": "", "stderr": ""}
        else: # For language == 'python', 'javascript' (code strings)
            try:
                with open(code_filepath_in_temp, 'w', encoding='utf-8') as f:
                    f.write(code)
            except IOError as e_write:
                logger.error(f"Failed to write temporary code file for Docker: {e_write}")
                return {"error": f"Failed to write temporary code file: {e_write}", "exit_code": -1, "stdout": "", "stderr": ""}

        abs_temp_dir = os.path.abspath(temp_dir)
        
        docker_command = [
            "docker", "run", "--rm", "--network", "none",
            "--memory", DOCKER_MEM_LIMIT, "--memory-swap", DOCKER_MEM_LIMIT, # Enforce memory limits
            "--cpus", DOCKER_CPU_LIMIT, # Enforce CPU limits
            "--security-opt=no-new-privileges", # Prevent privilege escalation
            "-v", f"{abs_temp_dir}:/sandbox:ro", # Mount code read-only
            "-w", "/sandbox", # Set working directory inside container
        ]
        
        # Add environment variables from prompt_vars
        if env_vars:
            for key, value in env_vars.items():
                docker_command.extend(["-e", f"{key}={value}"])

        docker_command.extend([DOCKER_IMAGE, interpreter, script_filename_in_container])

        logger.debug(f"Executing Docker command: {' '.join(docker_command)}")

        # Run the Docker container process
        try:
            process = subprocess.run(
                docker_command,
                input=input_data.encode('utf-8'), # Pass input_data as stdin
                capture_output=True, # Capture stdout/stderr
                timeout=TIMEOUT_SECONDS, # Apply timeout
                check=False # Do not raise exception on non-zero exit code
            )

            # Decode stdout/stderr, replacing errors
            stdout = process.stdout.decode('utf-8', errors='replace').strip()
            stderr = process.stderr.decode('utf-8', errors='replace').strip()
            exit_code = process.returncode

            if exit_code != 0:
                logger.warning(f"Docker execution finished with non-zero exit code {exit_code}. Stderr:\n{stderr}")
            else:
                logger.debug(f"Docker execution successful (Exit Code: 0). Stdout:\n{stdout}")

            return {"stdout": stdout, "stderr": stderr, "exit_code": exit_code, "error": None}

        except subprocess.TimeoutExpired:
            logger.error(f"Docker execution timed out after {TIMEOUT_SECONDS}s.")
            # Try to cleanup container if possible (might fail if unresponsive)
            # docker ps -q --filter "ancestor=DOCKER_IMAGE" | xargs -r docker stop | xargs -r docker rm
            return {"error": f"TimeoutExpired: Execution exceeded {TIMEOUT_SECONDS}s limit.", "exit_code": -1, "stdout": "", "stderr": "Timeout Error"}
        except FileNotFoundError:
            # Should be caught by earlier check, but safeguard
            logger.error("Docker command not found during execution attempt.")
            return {"error": "Docker command not found.", "exit_code": -1, "stdout": "", "stderr": ""}
        except Exception as e_docker_run:
            logger.error(f"Docker container execution failed unexpectedly: {e_docker_run}", exc_info=True)
            return {"error": f"Docker execution failed: {e_docker_run}", "exit_code": -1, "stdout": "", "stderr": str(e_docker_run)}

    except Exception as e_setup:
        # Catch errors during temp directory creation etc.
        logger.error(f"Failed setup for Docker execution: {e_setup}", exc_info=True)
        return {"error": f"Failed setup for Docker execution: {e_setup}", "exit_code": -1, "stdout": "", "stderr": ""}
    finally:
        # Ensure temporary directory is always cleaned up
        if temp_dir_obj:
            try:
                temp_dir_obj.cleanup()
                logger.debug("Cleaned up temporary directory for Docker execution.")
            except Exception as cleanup_e:
                # Log error but don't crash if cleanup fails
                logger.error(f"Error cleaning up temporary directory '{getattr(temp_dir_obj,'name','N/A')}': {cleanup_e}")

# --- Internal Helper: Subprocess Execution ---
def _execute_with_subprocess(language: str, code: str, input_data: str, env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Executes code using a local subprocess. Returns partial result dict."""
    # Determine interpreter path (sys.executable for Python, 'node' for JavaScript)
    interpreter_path = ""
    if language == 'python' or language == 'python_script': # For both python code strings and scripts
        interpreter_path = sys.executable
    elif language == 'javascript':
        interpreter_path = "node"
    else:
        return {"error": f"Unsupported language for subprocess execution: {language}", "exit_code": -1, "stdout": "", "stderr": f"Unsupported language: {language}"}

    if not interpreter_path:
        return {"error": "Interpreter path could not be determined.", "exit_code": -1, "stdout": "", "stderr": "Interpreter path missing."}

    # Construct the command
    command: List[str]
    input_data_for_python_execution: Optional[str] = None # Specifically for piping python code

    if language == 'python_script':
        script_path = os.path.abspath(code) # Ensure absolute path for security/consistency
        if not os.path.isfile(script_path):
            return {"error": f"Python script not found: {script_path}", "exit_code": -1, "stdout": "", "stderr": f"Script not found: {script_path}"}
        command = [interpreter_path, script_path]
        logger.debug(f"Subprocess: Executing Python script. Command: {' '.join(command)}")
        input_data_for_python_execution = input_data # Regular input_data for scripts
    elif language == 'python':
        # For Python code strings, execute the interpreter and pipe the code to stdin
        command = [interpreter_path]
        input_data_for_python_execution = code # The code string itself will be piped to stdin
        logger.debug(f"Subprocess: Executing Python code via stdin. Command: {interpreter_path}. Input code (first 100 chars): {code[:100].replace('\n', '\\n')}")
    elif language == 'javascript':
        command = [interpreter_path, "-e", code]
    else:
        # Explicitly prevent 'shell' due to original error context, though it should be caught by 'unsupported' anyway.
        if language == 'shell':
             logger.error(f"Language 'shell' is not directly supported for security reasons via subprocess. Use 'bash' or a script language like 'python_script'.")
             return {"error": f"Language 'shell' is not directly supported for security reasons via subprocess. Use 'bash' or script language.", "exit_code": -1, "stdout": "", "stderr": ""}
        logger.error(f"Unsupported language for subprocess execution: {language}")
        return {"error": f"Unsupported language for subprocess execution: {language}", "exit_code": -1, "stdout": "", "stderr": ""}

    # Actual execution
    try:
        logger.debug(f"Executing subprocess command: {' '.join(command)} with env: {env_vars is not None}")
        process = subprocess.run(
            command,
            input=input_data_for_python_execution if language == 'python' else input_data, # Use specific input for python direct execution
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False, # Do not raise CalledProcessError, handle exit code manually
            env=env_vars # Pass the prepared environment variables
        )
        return {"stdout": process.stdout, "stderr": process.stderr, "exit_code": process.returncode}
    except subprocess.TimeoutExpired:
        logger.error(f"Subprocess execution timed out after {TIMEOUT_SECONDS}s.")
        return {"error": f"TimeoutExpired: Execution exceeded {TIMEOUT_SECONDS}s limit.", "exit_code": -1, "stdout": "", "stderr": "Timeout Error"}
    except FileNotFoundError:
        # Error if the interpreter itself wasn't found
        logger.error(f"Interpreter for '{language}' ('{interpreter_path if interpreter_path else language}') not found.")
        return {"error": f"Interpreter not found: {interpreter_path if interpreter_path else language}", "exit_code": -1, "stdout": "", "stderr": ""}
    except OSError as e_os:
        # Catch OS-level errors during process creation (e.g., permissions)
        logger.error(f"OS error during subprocess execution: {e_os}", exc_info=True)
        return {"error": f"OS error during execution: {e_os}", "exit_code": -1, "stdout": "", "stderr": str(e_os)}
    except Exception as e_subproc:
        # Catch other unexpected errors
        logger.error(f"Subprocess execution failed unexpectedly: {e_subproc}", exc_info=True)
        return {"error": f"Subprocess execution failed: {e_subproc}", "exit_code": -1, "stdout": "", "stderr": str(e_subproc)}

# --- END OF FILE 3.0ArchE/code_executor.py --- 