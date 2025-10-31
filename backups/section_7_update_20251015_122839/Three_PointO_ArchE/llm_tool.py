import logging
from typing import Dict, Any, Optional
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .utils.reflection_utils import create_reflection, ExecutionStatus
from .llm_providers import get_llm_provider, get_model_for_provider, LLMProviderError
import time
import base64

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# --- Jinja2 Environment Setup ---
# Assumes a 'prompts' directory exists at the root of the project.
# This path might need to be made more robust via the main config system.
PROMPT_DIR = os.path.join(os.path.dirname(__file__), '..', 'prompts')
if not os.path.isdir(PROMPT_DIR):
    logger.warning(f"Jinja2 prompt directory not found at '{PROMPT_DIR}'. Template-based generation will fail.")
    jinja_env = None
else:
    jinja_env = Environment(
        loader=FileSystemLoader(PROMPT_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )

# --- Gemini API Configuration (moved to provider) ---
# We still detect key presence for early diagnostics, but provider handles client init.
GEMINI_API_AVAILABLE = bool(os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"))

def _render_prompt_from_template(template_name: str, template_vars: Dict[str, Any], template_vars_from_files: Dict[str, str]) -> str:
    """Renders a prompt from a Jinja2 template, injecting variables and file contents."""
    if not jinja_env:
        raise EnvironmentError("Jinja2 environment is not configured. Cannot render template.")
        
    # Load content from files and add to template_vars
    for var_name, file_path in template_vars_from_files.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                template_vars[var_name] = f.read()
        except Exception as e:
            logger.error(f"Failed to read file '{file_path}' for template variable '{var_name}': {e}")
            # Inject error message into the template variable so it's visible during generation
            template_vars[var_name] = f"[ERROR: Could not load file '{file_path}']"
            
    try:
        template = jinja_env.get_template(template_name)
        return template.render(template_vars)
    except Exception as e:
        logger.error(f"Failed to render Jinja2 template '{template_name}': {e}", exc_info=True)
        raise

def generate_text_llm(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate text using a real LLM (Gemini) with advanced templating, and return results with IAR reflection.
    """
    start_time = time.time()
    action_name = "generate_text"

    prompt = inputs.get("prompt")
    prompt_template_name = inputs.get("prompt_template_name")
    template_vars = inputs.get("template_vars", {})
    template_vars_from_files = inputs.get("template_vars_from_files", {})
    
    provider = inputs.get("provider", "google")
    # If model not provided, resolve via provider config
    model = inputs.get("model") or get_model_for_provider(provider)
    temperature = inputs.get("temperature", 0.5)
    encode_output_base64 = inputs.get("encode_output_base64", False)

    final_prompt = ""
    try:
        if prompt_template_name:
            final_prompt = _render_prompt_from_template(prompt_template_name, template_vars, template_vars_from_files)
        elif prompt:
            final_prompt = prompt
        else:
            raise ValueError("Either 'prompt' or 'prompt_template_name' must be provided.")
    except Exception as e:
        return {
            "error": str(e),
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.FAILURE,
                message=f"Prompt generation failed: {e}",
                inputs=inputs,
                execution_time=time.time() - start_time
            )
        }

    # Initialize provider (Google/Gemini)
    try:
        base_provider = get_llm_provider(provider)
    except Exception as e:
        error_msg = f"Failed to initialize LLM provider '{provider}': {e}"
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.FAILURE,
                message=error_msg,
                inputs=inputs,
                potential_issues=[str(e)],
                execution_time=time.time() - start_time
            )
        }
        
    try:
        # Use standardized provider interface
        response_text = base_provider.generate(final_prompt, model=model, temperature=temperature)
        response_text = (response_text or "").strip()
        
        if encode_output_base64:
            response_text = base64.b64encode(response_text.encode('utf-8')).decode('utf-8')

        execution_time = time.time() - start_time
        outputs = {"response_text": response_text}
        
        return {
            "result": outputs,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.SUCCESS,
                message=f"Text generation completed successfully using {model}.",
                inputs=inputs,
                outputs=outputs,
                confidence=0.9,
                execution_time=execution_time
            )
        }
    except LLMProviderError as e:
        error_msg = f"LLM provider error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        execution_time = time.time() - start_time
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.CRITICAL_FAILURE,
                message=error_msg,
                inputs=inputs,
                potential_issues=[str(e)],
                execution_time=execution_time
            )
        }
    except Exception as e:
        error_msg = f"Unexpected LLM error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        execution_time = time.time() - start_time
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.CRITICAL_FAILURE,
                message=error_msg,
                inputs=inputs,
                potential_issues=[str(e)],
                execution_time=execution_time
            )
        } 