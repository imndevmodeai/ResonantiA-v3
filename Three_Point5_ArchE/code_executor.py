import logging
import subprocess
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

def _create_reflection(status: str, message: str, **kwargs) -> Dict[str, Any]:
    """Creates a standardized IAR reflection dictionary."""
    reflection = {
        "status": status,
        "message": message,
        "confidence": 0.0,
        "execution_time": 0.0,
    }
    reflection.update(kwargs)
    return reflection

def _execute_with_subprocess(code: str, language: str, timeout: int, input_data: str) -> Dict[str, Any]:
    """Executes code in a sandboxed subprocess."""
    if language.lower() not in ['python', 'bash', 'shell']:
        raise ValueError(f"Unsupported language: {language}")

    cmd = [language.lower(), "-c", code] if language.lower() == 'python' else ['bash', '-c', code]

    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  # We check the returncode manually
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds.",
            "return_code": -1
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"An unexpected error occurred during execution: {e}",
            "return_code": -1
        }

def execute_code(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes code in a secure sandbox and returns the result with an IAR reflection.
    """
    start_time = time.time()
    code = inputs.get("code")
    code_path = inputs.get("code_path")
    language = inputs.get("language")
    timeout = inputs.get("timeout", 30)
    input_data = inputs.get("input_data")

    if not code and code_path:
        try:
            with open(code_path, 'r') as f:
                code = f.read()
        except FileNotFoundError:
            return {
                "error": f"Code path not found: {code_path}",
                "reflection": _create_reflection(
                    "failure", f"Input validation failed: Code path '{code_path}' not found.",
                    execution_time=time.time() - start_time
                )
            }
            
    if not code or not language:
        return {
            "error": "Inputs 'code' (or 'code_path') and 'language' are required.",
            "reflection": _create_reflection(
                "failure", "Input validation failed: 'code' and 'language' are required.",
                execution_time=time.time() - start_time
            )
        }
    
    # In a full implementation, a Docker sandbox would be the preferred, more secure default.
    # For now, we use a subprocess as the primary containment method.
    exec_result = _execute_with_subprocess(code, language, timeout, input_data)

    success = exec_result["return_code"] == 0
    status = "success" if success else "failure"
    
    message = f"Execution completed with return code {exec_result['return_code']}."
    if not success and exec_result['stderr']:
         message += f" Stderr: {exec_result['stderr'][:200]}..." # Truncate long errors
    
    result_data = {
        "output": exec_result["stdout"],
        "stderr": exec_result["stderr"],
        "return_code": exec_result["return_code"]
    }

    return {
        "result": result_data,
        "reflection": _create_reflection(
            status=status,
            message=message,
            inputs=inputs,
            outputs=result_data,
            confidence=0.95 if success else 0.3,
            execution_time=time.time() - start_time
        )
    }
