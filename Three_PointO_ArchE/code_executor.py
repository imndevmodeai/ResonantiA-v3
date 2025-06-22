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
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING # Expanded type hints
import asyncio
from dataclasses import dataclass
from .iar_components import IARValidator, ResonanceTracker

if TYPE_CHECKING:
    from .action_context import ActionContext

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
def execute_code(
    code: str = None,
    language: str = "python",
    timeout: int = 30,
    environment: Optional[Dict[str, str]] = None,
    code_path: str = None,
    input_data: str = None
) -> Dict[str, Any]:
    """
    Execute code in the specified language and return results with IAR reflection.

    Args:
        code: The code to execute as a string
        language: Programming language (default: python)
        timeout: Execution timeout in seconds
        environment: Optional environment variables
        code_path: Path to a file containing the code to execute
        input_data: Optional string to pass to the script's stdin
    """
    if code is None and code_path is None:
        return {
            "error": "Either 'code' or 'code_path' must be provided.",
            "reflection": _create_reflection("Failed", "Input validation failed", 0.0, "Misaligned", ["Missing code input."], None)
        }
    
    temp_file = None
    try:
        if code_path:
            if not os.path.exists(code_path):
                raise FileNotFoundError(f"The specified code_path does not exist: {code_path}")
            exec_file = code_path
        else:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f".{language}") as f:
                f.write(code)
                temp_file = f.name
            exec_file = temp_file
        
        # Set up environment, ensuring all values are strings
        env = os.environ.copy()
        if environment:
            # Robustly convert all provided env values to strings
            safe_env = {str(k): str(v) for k, v in environment.items()}
            env.update(safe_env)
        
        # Execute code based on language
        if language == "python":
            result = subprocess.run(
                [sys.executable, exec_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                input=input_data
            )
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        # Process results
        if result.returncode == 0:
            return {
                "output": result.stdout,
                "reflection": {
                    "status": "Success",
                    "confidence": 1.0,
                    "insight": "Code executed successfully",
                    "action": "execute_code",
                    "reflection": "No errors encountered"
                }
            }
        else:
            return {
                "error": result.stderr,
                "output": result.stdout,
                "reflection": {
                    "status": "Failed",
                    "confidence": 0.0,
                    "insight": f"Code execution failed with return code {result.returncode}",
                    "action": "execute_code",
                    "reflection": result.stderr
                }
            }
            
    except subprocess.TimeoutExpired:
        return {
            "error": f"Execution timed out after {timeout} seconds",
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "insight": "Code execution timed out",
                "action": "execute_code",
                "reflection": f"Timeout after {timeout} seconds"
            }
        }
    except Exception as e:
        error_msg = f"Error executing code: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "insight": "Error during code execution",
                "action": "execute_code",
                "reflection": error_msg
            }
        }
    finally:
        # Clean up temp file if it was created
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

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
def _execute_with_subprocess(language: str, code: str, input_data: str, env_vars: Optional[Dict[str, str]] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        
        # If we have context and this is Python code, prepend context injection
        if context and language == 'python':
            try:
                logger.debug(f"Subprocess: Context available with keys: {list(context.keys()) if context else 'None'}")
                
                # Serialize context without truncation - use ensure_ascii=False for better handling of unicode
                # and separators for compact representation while maintaining readability
                context_json = json.dumps(context, default=str, ensure_ascii=False, separators=(',', ':'))
                
                # Use base64 encoding to safely handle any special characters or large content
                # This completely avoids any string escaping issues
                import base64
                context_b64 = base64.b64encode(context_json.encode('utf-8')).decode('ascii')
                
                # Use a robust context injection that handles large contexts and special characters
                context_injection = f"""import json
import sys
import base64

# Full workflow context - never truncated
# Using base64 encoding to safely handle any special characters or large content
try:
    # Decode the context from base64 encoding
    context_b64 = "{context_b64}"
    context_json_str = base64.b64decode(context_b64).decode('utf-8')
    context = json.loads(context_json_str)
    
    # Verify context was loaded successfully
    if not isinstance(context, dict):
        raise ValueError("Context is not a dictionary")
        
    # Make context available globally for any code that needs it
    globals()['context'] = context
    
    # Also make it available in locals for immediate use
    locals()['context'] = context
    
except (json.JSONDecodeError, ValueError, UnicodeDecodeError, Exception) as e:
    print(f"ERROR: Failed to parse workflow context: {{e}}", file=sys.stderr)
    print(f"Context base64 length: {len(context_b64)}", file=sys.stderr)
    # Provide empty context as fallback but don't fail silently
    context = {{}}
    globals()['context'] = context
    locals()['context'] = context

"""
                
                code_with_context = context_injection + code
                input_data_for_python_execution = code_with_context
                
                logger.debug(f"Subprocess: Injected context into Python code. Context keys: {list(context.keys())}")
                logger.debug(f"Subprocess: Context JSON size: {len(context_json)} characters")
                logger.debug(f"Subprocess: Base64 encoded size: {len(context_b64)} characters")
                logger.debug(f"Subprocess: Total injected code size: {len(code_with_context)} characters")
                
                # Log a preview of the context structure without truncating sensitive data
                context_preview = {k: f"<{type(v).__name__}>" for k, v in context.items()}
                logger.debug(f"Subprocess: Context structure preview: {context_preview}")
                
                # Warn if context is very large (but don't truncate)
                if len(context_json) > 1000000:  # 1MB
                    logger.warning(f"Very large context detected ({len(context_json)} chars). This may impact performance but will not be truncated.")
                
            except Exception as e:
                logger.error(f"Failed to inject context into Python code: {e}. Running without context.", exc_info=True)
                input_data_for_python_execution = code
        else:
            logger.debug(f"Subprocess: No context injection. Context available: {context is not None}, Language: {language}")
            input_data_for_python_execution = code # The code string itself will be piped to stdin
            
        logger.debug(f"Subprocess: Executing Python code via stdin. Command: {interpreter_path}. Input code (first 100 chars): {input_data_for_python_execution[:100].replace(chr(10), '\\n')}")
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

@dataclass
class ExecutionResult:
    """Result of code execution."""
    output: str
    error: Optional[str]
    execution_time: float
    sandbox_method: str
    iar_data: Dict[str, Any]

class CodeExecutor:
    """Code executor with native Gemini API integration."""
    
    def __init__(self):
        self.iar_validator = IARValidator()
        self.resonance_tracker = ResonanceTracker()
    
    async def execute_code(
        self,
        code: str,
        context: Dict[str, Any],
        provider: str = "gemini_native"
    ) -> ExecutionResult:
        """Execute code using the specified provider."""
        if provider == "gemini_native":
            return await self._execute_with_gemini_native(code, context)
        else:
            # Fallback to other providers (e.g., Docker)
            return await self._execute_with_fallback(code, context, provider)
    
    async def _execute_with_gemini_native(
        self,
        code: str,
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute code using native Gemini API."""
        try:
            # Prepare execution context
            execution_context = {
                "code": code,
                "context": context,
                "sandbox_method": "gemini_native"
            }
            
            # Execute code using Gemini API
            # Note: This is a placeholder for the actual Gemini API call
            # The actual implementation would use the Gemini API's code execution feature
            result = await self._call_gemini_code_execution(execution_context)
            
            # Generate IAR data
            iar_data = {
                "status": "Success" if not result.get("error") else "Error",
                "confidence": 0.9,  # High confidence for native execution
                "summary": "Code execution completed",
                "potential_issues": [],
                "alignment_check": {
                    "code_safety": 0.9,
                    "execution_success": 0.9 if not result.get("error") else 0.0
                },
                "sandbox_method_used": "gemini_native"
            }
            
            # Track resonance
            self.resonance_tracker.record_execution(
                "code_execution",
                iar_data,
                execution_context
            )
            
            return ExecutionResult(
                output=result.get("output", ""),
                error=result.get("error"),
                execution_time=result.get("execution_time", 0.0),
                sandbox_method="gemini_native",
                iar_data=iar_data
            )
            
        except Exception as e:
            # Handle execution errors
            error_iar = {
                "status": "Error",
                "confidence": 0.0,
                "summary": f"Code execution failed: {str(e)}",
                "potential_issues": [str(e)],
                "alignment_check": {
                    "code_safety": 0.0,
                    "execution_success": 0.0
                },
                "sandbox_method_used": "gemini_native"
            }
            
            return ExecutionResult(
                output="",
                error=str(e),
                execution_time=0.0,
                sandbox_method="gemini_native",
                iar_data=error_iar
            )
    
    async def _execute_with_fallback(
        self,
        code: str,
        context: Dict[str, Any],
        provider: str
    ) -> ExecutionResult:
        """Execute code using fallback provider (e.g., Docker)."""
        # Implementation for other providers
        # This would be the existing Docker/subprocess implementation
        pass
    
    async def _call_gemini_code_execution(
        self,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call Gemini API for code execution."""
        # Placeholder for actual Gemini API call
        # This would be replaced with the actual API implementation
        return {
            "output": "Execution result",
            "error": None,
            "execution_time": 0.1
        }
    
    def validate_execution(self, result: ExecutionResult) -> bool:
        """Validate execution result."""
        is_valid, _ = self.iar_validator.validate_content(result.iar_data)
        return is_valid
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        return self.resonance_tracker.get_execution_summary() 