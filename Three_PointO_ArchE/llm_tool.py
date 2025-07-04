import logging
from typing import Dict, Any, Optional
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from .utils.reflection_utils import create_reflection, ExecutionStatus
import time

logger = logging.getLogger(__name__)

# Load environment variables from a .env file if it exists
# This is useful for local development.
load_dotenv()

# Configure the Gemini API key
try:
    # It's best practice to use environment variables for API keys
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
except (ValueError, ImportError) as e:
    logger.warning(f"Gemini API key not configured or library not available: {e}. The LLM tool will not work.")
    # Allow the module to be imported, but the function will fail if called.
    pass


def generate_text_llm(
    inputs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate text using a real LLM (Gemini) and return results with IAR reflection.
    
    Args:
        inputs (Dict): A dictionary containing:
            - prompt (str): Input prompt for text generation.
            - max_tokens (int): Maximum tokens (Note: Gemini API may have its own limits).
            - temperature (float): Sampling temperature (0.0 to 1.0).
            - provider (str): The LLM provider (default: 'gemini').
            - model (str): The model to use.
        
    Returns:
        Dictionary containing generated text and a compliant IAR reflection.
    """
    start_time = time.time()
    action_name = "generate_text"

    prompt = inputs.get("prompt")
    provider = inputs.get("provider", "gemini")
    model = inputs.get("model", "gemini-1.5-flash-latest")
    temperature = inputs.get("temperature", 0.5)

    if not prompt:
        return {
            "error": "Input 'prompt' is required.",
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.FAILURE,
                message="Input validation failed: 'prompt' is required.",
                inputs=inputs,
                execution_time=time.time() - start_time
            )
        }

    if provider != "gemini":
        error_msg = f"LLM provider '{provider}' is not implemented."
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.FAILURE,
                message=error_msg,
                inputs=inputs,
                potential_issues=["ConfigurationError"],
                execution_time=time.time() - start_time
            )
        }
        
    try:
        gemini_model = genai.GenerativeModel(model)
        response = gemini_model.generate_content(
            prompt, 
            generation_config=genai.types.GenerationConfig(temperature=temperature)
        )
        
        response_text = response.text.strip()
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
        
    except Exception as e:
        error_msg = f"Error generating text with Gemini: {str(e)}"
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