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
        preview_str = json.dumps(preview, default=str) if isinstance(preview, (dict, list)) else str(preview)
        if preview_str and len(preview_str) > 150: preview_str = preview_str[:150] + "..."
    except Exception:
        try: preview_str = str(preview); preview_str = preview_str[:150] + "..." if len(preview_str) > 150 else preview_str
        except Exception: preview_str = "[Preview Error]"
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
    [IAR Enabled] Executes a code snippet using the configured sandbox method.
    Validates inputs, selects execution strategy (Docker, subprocess, none),
    runs the code, and returns results including stdout, stderr, exit code,
    error messages, and a detailed IAR reflection.

    Args:
        inputs (Dict[str, Any]): Dictionary containing:
            language (str): The programming language (e.g., 'python', 'javascript'). Required.
            code (str): The code snippet to execute. Required.
            input_data (str, optional): Data to be passed as standard input to the code. Defaults to "".

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
    input_data = inputs.get("input_data", "") # Default to empty string if not provided

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
    elif not isinstance(input_data, str):
        # Attempt to convert input_data to string if it's not, log warning
        try:
            input_data = str(input_data)
            logger.warning(f"Input 'input_data' was not a string ({type(inputs.get('input_data'))}), converted to string.")
        except Exception as e_str:
            primary_result["error"] = f"Invalid 'input_data': Cannot convert type {type(inputs.get('input_data'))} to string ({e_str})."
            reflection_issues.append(primary_result["error"])

    if primary_result["error"]:
        reflection_summary = f"Input validation failed: {primary_result['error']}"
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

    language = language.lower() # Normalize language name
    method_to_use = sandbox_method_resolved # Use the resolved method based on config and checks
    primary_result["sandbox_method_used"] = method_to_use # Record the method being attempted

    logger.info(f"Attempting to execute '{language}' code using sandbox method: '{method_to_use}'")

    # --- Select Execution Strategy ---
    exec_result: Dict[str, Any] = {} # Dictionary to store results from internal execution functions
    if method_to_use == 'docker':
        if DOCKER_AVAILABLE:
            exec_result = _execute_with_docker(language, code, input_data)
        else:
            # Fallback if Docker configured but unavailable
            logger.warning("Docker configured but unavailable. Falling back to 'subprocess' (less secure).")
            primary_result["sandbox_method_used"] = 'subprocess' # Update actual method used
            reflection_issues.append("Docker unavailable, fell back to subprocess.")
            exec_result = _execute_with_subprocess(language, code, input_data)
            if exec_result.get("error"): # If subprocess also failed (e.g., interpreter missing)
                reflection_issues.append(f"Subprocess fallback failed: {exec_result.get('error')}")
    elif method_to_use == 'subprocess':
        logger.warning("Executing code via 'subprocess' sandbox. This provides limited isolation and is less secure than Docker.")
        exec_result = _execute_with_subprocess(language, code, input_data)
    elif method_to_use == 'none':
        logger.critical("Executing code with NO SANDBOX ('none'). This is EXTREMELY INSECURE and should only be used in trusted debugging environments with full awareness of risks.")
        reflection_issues.append("CRITICAL SECURITY RISK: Code executed without sandbox.")
        # Use subprocess logic for actual execution, but flag clearly that no sandbox was intended
        exec_result = _execute_with_subprocess(language, code, input_data)
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
        if error not in reflection_issues: reflection_issues.append(f"Execution/Setup Error: {error}")
        reflection_preview = stderr if stderr else stdout # Preview error or output if available
    elif exit_code == 0: # Successful execution (code ran and returned 0)
        reflection_status = "Success"
        reflection_summary = f"Code executed successfully (Exit Code: 0) using '{primary_result['sandbox_method_used']}' sandbox."
        reflection_confidence = 0.95 # High confidence in successful execution
        reflection_alignment = "Assumed aligned with computational goal (code ran successfully)."
        if stderr: # Add stderr content as a potential issue if present, even on success
            reflection_issues.append(f"Stderr generated (may contain warnings): {stderr[:100]}...")
        reflection_preview = stdout # Preview standard output
    # Handle specific exit code for timeout if possible (depends on subprocess/docker implementation)
    # Example: Check if exit code is specific timeout signal or if error message indicates timeout
    elif "Timeout" in (error or "") or (isinstance(exit_code, int) and exit_code == -9): # Check if timeout was explicitly reported or signaled (SIGKILL)
        reflection_status = "Failure"
        reflection_summary = f"Code execution timed out after ~{TIMEOUT_SECONDS}s."
        reflection_confidence = 0.0
        reflection_alignment = "Failed due to timeout."
        if "Execution Timeout" not in reflection_issues: reflection_issues.append("Execution Timeout")
        reflection_issues.append("Code may be inefficient, stuck in loop, or timeout too short.")
        reflection_preview = stderr if stderr else stdout
    else: # Non-zero exit code indicates runtime error *within* the user's code
        reflection_status = "Failure" # Treat non-zero exit as failure of the code's objective
        reflection_summary = f"Code execution finished with non-zero exit code: {exit_code}."
        reflection_confidence = 0.3 # Code ran but failed internally
        reflection_alignment = "Code failed to execute as intended (runtime error)."
        reflection_issues.append(f"Runtime Error (Exit Code: {exit_code})")
        if stderr: reflection_issues.append(f"Check stderr for details: {stderr[:100]}...")
        else: reflection_issues.append("No stderr captured.")
        reflection_preview = stderr if stderr else stdout # Prefer stderr for errors

    # Final reflection generation
    final_reflection = _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)

    return {**primary_result, "reflection": final_reflection}

# --- Internal Helper: Docker Execution ---
def _execute_with_docker(language: str, code: str, input_data: str) -> Dict[str, Any]:
    """Executes code inside a Docker container. Returns partial result dict."""
    # Map language to interpreter command and filename within container
    # Ensure image specified in config.py has these interpreters installed
    exec_details: Dict[str, Tuple[str, str]] = {
        'python': ('python', 'script.py'),
        'javascript': ('node', 'script.js'),
        # Add other languages here (e.g., 'bash': ('bash', 'script.sh'))
    }
    if language not in exec_details:
        return {"error": f"Docker execution unsupported for language: '{language}'.", "exit_code": -1, "stdout": "", "stderr": ""}

    interpreter, script_filename = exec_details[language]
    temp_dir_obj = None # To ensure cleanup happens

    try:
        # Create a temporary directory on the host to mount into the container
        temp_dir_obj = tempfile.TemporaryDirectory(prefix="resonatia_docker_exec_")
        temp_dir = temp_dir_obj.name
        code_filepath = os.path.join(temp_dir, script_filename)

        # Write the user's code to the temporary file
        try:
            with open(code_filepath, 'w', encoding='utf-8') as f:
                f.write(code)
        except IOError as e_write:
            return {"error": f"Failed to write temporary code file: {e_write}", "exit_code": -1, "stdout": "", "stderr": ""}

        # Construct the Docker command
        # --rm: Remove container automatically after exit
        # --network none: Disable networking inside container (increases security)
        # --memory/--cpus: Resource limits from config
        # --security-opt=no-new-privileges: Prevent privilege escalation
        # -v ...:/sandbox:ro: Mount temp dir read-only into /sandbox inside container
        # -w /sandbox: Set working directory inside container
        # DOCKER_IMAGE: The container image (e.g., python:3.11-slim)
        # interpreter script_filename: Command to run inside container
        abs_temp_dir = os.path.abspath(temp_dir) # Docker needs absolute path for volume mount
        docker_command = [
            "docker", "run", "--rm", "--network", "none",
            "--memory", DOCKER_MEM_LIMIT, "--memory-swap", DOCKER_MEM_LIMIT, # Limit memory
            "--cpus", DOCKER_CPU_LIMIT, # Limit CPU
            "--security-opt=no-new-privileges", # Enhance security
            "-v", f"{abs_temp_dir}:/sandbox:ro", # Mount code read-only
            "-w", "/sandbox", # Set working directory
            DOCKER_IMAGE,
            interpreter, script_filename
        ]
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
def _execute_with_subprocess(language: str, code: str, input_data: str) -> Dict[str, Any]:
    """Executes code using a local subprocess. Less secure. Returns partial result dict."""
    cmd: Optional[List[str]] = None
    interpreter_path: Optional[str] = None
    # Find interpreter path - requires interpreters to be in system PATH
    try: import shutil # Import here as it's only needed for this method
    except ImportError: shutil = None

    if language == 'python':
        # Use the same Python executable that's running Arche if possible
        interpreter_path = sys.executable
        if not interpreter_path or not os.path.exists(interpreter_path):
            # Fallback to just 'python' hoping it's in PATH
            interpreter_path = "python" if platform.system() != "Windows" else "python.exe"
            logger.warning(f"Could not find sys.executable, attempting '{interpreter_path}'.")
        # Use '-c' to pass code directly as command line argument
        cmd = [interpreter_path, "-c", code]
    elif language == 'javascript':
        # Find 'node' executable using shutil.which (cross-platform PATH search)
        if shutil: interpreter_path = shutil.which('node')
        if interpreter_path:
            # Use '-e' to pass code directly
            cmd = [interpreter_path, "-e", code]
        else:
            return {"error": "Node.js interpreter ('node') not found in system PATH.", "exit_code": -1, "stdout": "", "stderr": ""}
    # Add other languages here (e.g., bash using 'bash -c')
    # elif language == 'bash':
    #     interpreter_path = shutil.which('bash')
    #     if interpreter_path: cmd = [interpreter_path, "-c", code]
    #     else: return {"error": "Bash interpreter ('bash') not found.", "exit_code": -1, "stdout": "", "stderr": ""}
    else:
        return {"error": f"Unsupported language for subprocess execution: {language}", "exit_code": -1, "stdout": "", "stderr": ""}

    logger.debug(f"Executing subprocess command: {' '.join(cmd)}")
    try:
        # Run the command as a subprocess
        process = subprocess.run(
            cmd,
            input=input_data.encode('utf-8'), # Pass input data as stdin
            capture_output=True, # Capture stdout/stderr
            timeout=TIMEOUT_SECONDS, # Apply timeout
            check=False, # Do not raise exception on non-zero exit
            shell=False, # DO NOT use shell=True for security
            env=os.environ.copy() # Pass environment variables (consider scrubbing sensitive ones)
        )
        # Decode stdout/stderr
        stdout = process.stdout.decode('utf-8', errors='replace').strip()
        stderr = process.stderr.decode('utf-8', errors='replace').strip()
        exit_code = process.returncode

        if exit_code != 0:
            logger.warning(f"Subprocess execution finished with non-zero exit code {exit_code}. Stderr:\n{stderr}")
        else:
            logger.debug(f"Subprocess execution successful (Exit Code: 0). Stdout:\n{stdout}")

        return {"stdout": stdout, "stderr": stderr, "exit_code": exit_code, "error": None}

    except subprocess.TimeoutExpired:
        logger.error(f"Subprocess execution timed out after {TIMEOUT_SECONDS}s.")
        return {"error": f"TimeoutExpired: Execution exceeded {TIMEOUT_SECONDS}s limit.", "exit_code": -1, "stdout": "", "stderr": "Timeout Error"}
    except FileNotFoundError:
        # Error if the interpreter itself wasn't found
        logger.error(f"Interpreter for '{language}' ('{interpreter_path or language}') not found.")
        return {"error": f"Interpreter not found: {interpreter_path or language}", "exit_code": -1, "stdout": "", "stderr": ""}
    except OSError as e_os:
        # Catch OS-level errors during process creation (e.g., permissions)
        logger.error(f"OS error during subprocess execution: {e_os}", exc_info=True)
        return {"error": f"OS error during execution: {e_os}", "exit_code": -1, "stdout": "", "stderr": str(e_os)}
    except Exception as e_subproc:
        # Catch other unexpected errors
        logger.error(f"Subprocess execution failed unexpectedly: {e_subproc}", exc_info=True)
        return {"error": f"Subprocess execution failed: {e_subproc}", "exit_code": -1, "stdout": "", "stderr": str(e_subproc)}

# --- END OF FILE 3.0ArchE/code_executor.py ---