import logging
import json
import os
import base64
import time
from typing import Dict, Any, Optional

import google.generativeai as genai
from .prompt_manager import PromptManager

logger = logging.getLogger(__name__)

# Configure the API key from environment variables
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY environment variable not set. LLM tool will fail.")
    genai.configure(api_key=api_key)
except Exception as e:
    logger.error(f"Failed to configure Google Generative AI: {e}")
    genai = None

def _parse_llm_response(raw_text: str) -> Dict[str, Any]:
    """Cleans and parses the raw text response from the LLM."""
    cleaned_text = raw_text.strip()
    parsed_json = None
    
    # Attempt to find and parse a JSON object within the text
    try:
        json_match = re.search(r"```json\n({.*?})\n```", cleaned_text, re.DOTALL)
        if json_match:
            parsed_json = json.loads(json_match.group(1))
    except (json.JSONDecodeError, TypeError):
        logger.warning("Could not parse JSON from LLM response.")
        
    return {"cleaned_text": cleaned_text, "parsed_json": parsed_json}

def generate_text_llm(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    The Oracle of ArchE. Consults a Large Language Model with a structured,
    context-aware prompt and returns an IAR-compliant result.
    """
    start_time = time.time()
    reflection = {"status": "failure", "potential_issues": []}
    
    if not genai:
        reflection["potential_issues"].append("Google Generative AI SDK not configured.")
        return {"result": None, "reflection": reflection}

    try:
        prompt_manager = PromptManager()
        
        prompt = inputs.get("prompt")
        template_name = inputs.get("prompt_template_name")

        if template_name:
            template_vars = inputs.get("template_vars", {})
            files_vars = inputs.get("template_vars_from_files", {})
            
            for key, path in files_vars.items():
                try:
                    with open(path, 'r') as f:
                        template_vars[key] = f.read()
                except FileNotFoundError:
                    raise ValueError(f"Template variable file not found: {path}")

            prompt = prompt_manager.render_template(template_name, **template_vars)
        
        if not prompt:
            raise ValueError("A 'prompt' or 'prompt_template_name' must be provided.")

        model_name = inputs.get("model", "gemini-1.5-flash-latest")
        model = genai.GenerativeModel(model_name)

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=inputs.get("max_tokens", 2048),
            temperature=inputs.get("temperature", 0.7)
        )

        response = model.generate_content(prompt, generation_config=generation_config)
        
        parsed_response = _parse_llm_response(response.text)
        
        output_text = parsed_response["cleaned_text"]
        if inputs.get("encode_output_base64", False):
            output_text = base64.b64encode(output_text.encode()).decode()

        result = {
            "response_text": output_text,
            "parsed_json": parsed_response["parsed_json"]
        }

        reflection["status"] = "success"
        reflection["confidence"] = 0.85 # Default confidence, can be improved with response validation

    except Exception as e:
        logger.error(f"LLM tool execution failed: {e}", exc_info=True)
        reflection["potential_issues"].append(str(e))
        result = None

    reflection["execution_time"] = time.time() - start_time
    return {"result": result, "reflection": reflection}
