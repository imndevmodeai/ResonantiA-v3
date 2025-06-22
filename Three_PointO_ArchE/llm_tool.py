import logging
from typing import Dict, Any, Optional
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

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
except ValueError as e:
    logger.warning(f"Gemini API key not configured: {e}. The LLM tool will not work.")
    # Allow the module to be imported, but the function will fail if called.
    pass


def generate_text_llm(
    prompt: str,
    max_tokens: int = 2048, # Increased for complex synthesis
    temperature: float = 0.5,
    provider: str = "gemini",
    model: str = "gemini-1.5-flash-latest" 
) -> Dict[str, Any]:
    """
    Generate text using a real LLM (Gemini) and return results with IAR reflection.
    
    Args:
        prompt: Input prompt for text generation
        max_tokens: Maximum number of tokens to generate (Note: ignored by this Gemini model)
        temperature: Sampling temperature (0.0 to 1.0)
        provider: The LLM provider to use (currently only 'gemini' is implemented)
        model: Model to use for generation
        
    Returns:
        Dictionary containing generated text and IAR reflection
    """
    if provider != "gemini":
        not_implemented_msg = f"LLM provider '{provider}' is not implemented."
        return {
            "error": not_implemented_msg,
            "response_text": "",
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "insight": not_implemented_msg,
                "action": "generate_text_llm",
                "reflection": "Configuration error."
            }
        }
        
    try:
        gemini_model = genai.GenerativeModel(model)
        response = gemini_model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=temperature))
        
        # The API returns the response in `response.text`
        response_text = response.text.strip()
        
        return {
            "response_text": response_text,
            "reflection": {
                "status": "Success",
                "confidence": 0.9, # High confidence as it's a direct API call
                "insight": f"Text generation completed successfully using {model}.",
                "action": "generate_text_llm",
                "reflection": "Generated response meets requirements"
            }
        }
        
    except Exception as e:
        error_msg = f"Error generating text with Gemini: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "response_text": "",
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "insight": "Text generation failed during API call.",
                "action": "generate_text_llm",
                "reflection": error_msg
            }
        } 