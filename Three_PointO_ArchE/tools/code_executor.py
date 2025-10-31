# ResonantiA Protocol v3.5-GP - code_executor.py
# Executes provided code snippets securely (using sandboxing).

import logging
import subprocess
import tempfile
import os
import stat # Added for file permissions
import shutil # Added for removing temp dirs
from typing import Dict, Any, Tuple, Optional, NamedTuple
import sys

# Use try-except for config import to allow standalone testing
try:
    from Three_PointO_ArchE.config import config
except ImportError:
    class FallbackConfig:
        CODE_EXECUTO_TIMEOUT = 30
        CODE_EXECUTOR_USE_SANDBOX = True
        CODE_EXECUTOR_DOCKER_IMAGE = "python:3.10-slim"
    config = FallbackConfig()
    logging.getLogger(__name__).warning("Using fallback config for code_executor.py")

DOCKER_AVAILABLE = False
try:
    import docker
    from docker.errors import DockerException, ImageNotFound, APIError
    import requests # Docker lib uses requests
    DOCKER_AVAILABLE = True
    logging.getLogger(__name__).info("Docker library loaded successfully for code execution sandbox.")
except ImportError:
    logging.getLogger(__name__).error("Docker library not found. Docker sandboxing will be unavailable. Install 'docker' package.")
    DOCKER_AVAILABLE = False
except Exception as e:
    logging.getLogger(__name__).error(f"Unexpected error importing Docker library: {e}")
    DOCKER_AVAILABLE = False


logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "python": {"extension": ".py", "command": ["python3"]},
    "bash": {"extension": ".sh", "command": ["bash"]},
    "javascript": {"extension": ".js", "command": ["node"]},
}

class ExecutionResult(NamedTuple):
    """
    Structured result for code execution.
    """
    stdout: str
    stderr: str
    returncode: int
    error: Optional[str] = None # For setup/framework errors, not code errors

class CodeExecutor:
    """
    Manages the secure execution of code snippets in various languages.
    """
    def __init__(
        self,
        timeout: int = 30,
        use_sandbox: bool = True,
        sandbox_method: str = 'docker', # 'docker' or 'subprocess'
        docker_image: str = "python:3.10-slim"
    ):
        self.timeout = timeout
        self.use_sandbox = use_sandbox
        self.sandbox_method = sandbox_method
        self.docker_image = docker_image

        if self.use_sandbox and self.sandbox_method == 'docker' and not DOCKER_AVAILABLE:
            logger.error("Docker sandbox requested, but Docker SDK is not available. Falling back to subprocess.")
            self.sandbox_method = 'subprocess'

    def execute(self, language: str, code: str) -> ExecutionResult:
        """
        Executes a code snippet.
        """
        language = language.lower()
        if language not in SUPPORTED_LANGUAGES:
            return ExecutionResult("", "", -1, f"Unsupported language: {language}")

        logger.info(f"Executing code: Language={language}, Sandbox={self.use_sandbox}, Method={self.sandbox_method}")
        logger.debug(f"Code to execute:\n{code[:250]}{'...' if len(code) > 250 else ''}")

        if self.use_sandbox and self.sandbox_method == 'docker':
            return self._execute_in_docker(code, language)
        else:
            if not self.use_sandbox:
                logger.critical("!!! EXECUTING CODE WITHOUT ANY SANDBOXING !!!")
            return self._execute_with_subprocess(code, language)


    def _execute_in_docker(self, code: str, language: str) -> ExecutionResult:
        """Executes code inside a Docker container."""
        lang_config = SUPPORTED_LANGUAGES[language]
        try:
            client = docker.from_env()
            try:
                client.images.get(self.docker_image)
            except ImageNotFound:
                logger.warning(f"Docker image '{self.docker_image}' not found locally. Attempting to pull...")
                client.images.pull(self.docker_image)
        except DockerException as e:
            return ExecutionResult("", "", -1, f"Docker connection error: {e}")

        host_temp_dir = tempfile.mkdtemp()
        container_workdir = "/workspace"
        script_filename = f"script{lang_config['extension']}"
        container_script_path = os.path.join(container_workdir, script_filename)
        host_script_path = os.path.join(host_temp_dir, script_filename)

        try:
            with open(host_script_path, 'w', encoding='utf-8') as f:
                f.write(code)

            command = lang_config["command"] + [container_script_path]
            container = client.containers.run(
                image=self.docker_image,
                command=command,
                volumes={host_temp_dir: {'bind': container_workdir, 'mode': 'ro'}}, # Read-only mount
                working_dir=container_workdir,
                detach=True,
                network_mode='none',
                mem_limit='256m',
                security_opt=["no-new-privileges"],
            )

            try:
                exit_data = container.wait(timeout=self.timeout)
                exit_code = exit_data.get("StatusCode", -1)
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                container.stop(timeout=5)
                container.remove(force=True)
                return ExecutionResult("", "", -1, f"Execution timed out after {self.timeout} seconds.")

            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
            container.remove()

            return ExecutionResult(stdout, stderr, exit_code)

        except Exception as e:
            return ExecutionResult("", "", -1, f"Docker runtime error: {e}")
        finally:
            if os.path.exists(host_temp_dir):
                shutil.rmtree(host_temp_dir)

    def _execute_with_subprocess(self, code: str, language: str) -> ExecutionResult:
        """Executes code using the subprocess module (less secure)."""
        lang_config = SUPPORTED_LANGUAGES[language]
        script_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=lang_config["extension"], encoding='utf-8') as f:
                script_path = f.name
                f.write(code)

            if language == "bash":
                os.chmod(script_path, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)

            command = lang_config["command"] + [script_path]
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8',
                errors='replace'
            )
            return ExecutionResult(process.stdout, process.stderr, process.returncode)
        except subprocess.TimeoutExpired:
            return ExecutionResult("", "", -1, f"Execution timed out after {self.timeout} seconds.")
        except FileNotFoundError:
            return ExecutionResult("", "", -1, f"Command not found for language '{language}'. Is it installed and in PATH?")
        except Exception as e:
            return ExecutionResult("", "", -1, f"Subprocess execution error: {e}")
        finally:
            if script_path and os.path.exists(script_path):
                os.remove(script_path)

from Three_PointO_ArchE.iar_components import IAR_Prepper

def execute_code(language: str, code: str, **kwargs) -> Dict[str, Any]:
    """
    Standalone function to execute code for the action registry.
    This provides a stateless entry point with IAR-compliant responses.
    """
    
    use_sandbox = kwargs.get('use_sandbox', True)
    sandbox_method = kwargs.get('sandbox_method', 'docker')
    timeout = kwargs.get('timeout', 30)
    
    # Initialize IAR Prepper
    iar_prepper = IAR_Prepper("execute_code", {"language": language, "code": code[:100] + "...", **kwargs})
    
    executor = CodeExecutor(
        use_sandbox=use_sandbox,
        sandbox_method=sandbox_method,
        timeout=timeout
    )
    result = executor.execute(language, code)

    # Ensure system_representation is available for the probabilistic matching script
    # This is a targeted dependency injection.
    if "System, GaussianDistribution, StringParam, Distribution" in code:
        try:
            # Construct the path to system_representation.py relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            lib_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'system_representation.py'))
            with open(lib_path, 'r') as f:
                lib_code = f.read()
            code = lib_code + '\n\n' + code
            logger.info("Successfully injected system_representation.py into the code.")
        except Exception as e:
            logger.error(f"Failed to inject system_representation.py: {e}")

    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py', encoding='utf-8') as tmp_file:
            tmp_file.write(code)
    except Exception as e:
        logger.error(f"Failed to create temporary file for code execution: {e}")
        return {
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "error": f"Failed to create temporary file for code execution: {e}"
        }

    # Build the result dictionary
    execution_result = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }
    
    # Determine if execution was successful
    is_success = result.returncode == 0 and not result.error
    
    if is_success:
        iar_response = iar_prepper.finish_with_success(
            execution_result,
            confidence=0.9,
            summary=f"Code executed successfully in {language} (exit code: {result.returncode})"
        )
    else:
        iar_response = iar_prepper.finish_with_error(
            result.error or f"Code execution failed with exit code {result.returncode}",
            confidence=0.1
        )
    
    # Return in the format expected by the workflow engine
    return {
        "result": execution_result,
        "reflection": iar_response,
        "error": result.error
    }