from typing import Dict, Any, Tuple
import os
import google.generativeai as genai
from .utils import create_iar

# Configure the API key from environment variables
# For this implementation, we will allow it to be passed in, but check os.environ as a fallback
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_text(inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    [V4 Implementation] Interacts with a Google Generative AI model to generate text based on a prompt.
    """
    prompt = inputs.get("prompt")
    model_name = inputs.get("model", "gemini-2.5-pro") # Default to a fast and capable model
    temperature = inputs.get("temperature", 0.7)
    api_key = inputs.get("api_key")

    if not prompt:
        result = {"error": "Missing required input: prompt."}
        iar = create_iar(0.1, 0.0, ["Prompt is required."])
        return result, iar

    # Allow overriding the environment API key
    if api_key:
        genai.configure(api_key=api_key)
        current_key = api_key
    else:
        current_key = GOOGLE_API_KEY

    if not current_key:
        result = {"error": "Google API key not provided or found in GOOGLE_API_KEY environment variable."}
        iar = create_iar(0.1, 0.0, ["API key is missing."])
        return result, iar

    try:
        model = genai.GenerativeModel(model_name)
        
        # Enable JSON mode by setting the response_mime_type in generation_config
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json"
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        # In JSON mode, the response.text is a JSON string.
        # The calling function is responsible for parsing it.
        generated_text = response.text.strip()
        
        result = {
            "generated_text": generated_text,
            "model_used": model_name
        }
        iar = create_iar(
            confidence=0.9, # Confidence in the API call, not the content
            tactical_resonance=0.9,
            potential_issues=[],
            metadata={"model": model_name}
        )
        return result, iar

    except Exception as e:
        result = {"error": f"An unexpected error occurred with the Google GenAI API: {e}"}
        iar = create_iar(0.1, 0.1, [f"Unexpected API Error: {e}"])
        return result, iar
