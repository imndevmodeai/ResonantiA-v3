import os
import google.generativeai as genai
from typing import Dict, Any, Optional

# 1. Secure Configuration
# The API key should be loaded from an environment variable for security.
# Ensure you have `export GEMINI_API_KEY='your-api-key'` in your shell environment.
try:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    # This allows the module to be imported without immediate failure if the key isn't set.
    # The function call will handle the missing key gracefully.
    print("WARNING: GEMINI_API_KEY environment variable not set. `invoke_llm_tool` will fail.")
    pass

# A global flag to check if the configuration was successful
_is_configured = False
if "GEMINI_API_KEY" in os.environ:
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        _is_configured = True
    except Exception as e:
        print(f"ERROR: Failed to configure Gemini API: {e}")

def invoke_llm_tool(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    model_name: str = "gemini-1.5-flash"
) -> Dict[str, Any]:
    """
    Interacts with the base LLM (Gemini), adhering to the ResonantiA Protocol contract.

    This function is the concrete "So Below" implementation of the "Enhanced LLM Provider"
    defined in the protocol. It handles the direct API call and wraps the response in a
    protocol-compliant structure, including the mandatory IAR block.
    """
    if not _is_configured:
        error_iar = {
            "confidence": 0.0,
            "potential_issues": ["CONFIGURATION_ERROR", "GEMINI_API_KEY not set or invalid."],
            "notes": "The LLM Provider is not configured with an API key."
        }
        return {"text": None, "tool_calls": None, "citations": None, "iar": error_iar}

    try:
        # 2. The Provider Function Logic
        model = genai.GenerativeModel(model_name)
        
        # OLDER SDK COMPATIBILITY: System instructions are passed as part of the chat history.
        messages = []
        if system_prompt:
            messages.append({'role': 'user', 'parts': [system_prompt]})
            messages.append({'role': 'model', 'parts': ["Understood. I will act in accordance with these instructions."]})
        
        messages.append({'role': 'user', 'parts': [prompt]})

        response = model.generate_content(
            messages,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature
            )
        )

        # 3. IAR Wrapping and Protocol-Compliant Output
        output_text = response.text
        
        iar_block = {
            "confidence": 0.95,
            "tactical_resonance": "medium",
            "crystallization_potential": "low",
            "potential_issues": [],
            "notes": f"Successfully generated response from {model_name}."
        }

        return {
            "text": output_text,
            "tool_calls": None, # Placeholder
            "citations": None, # Placeholder
            "iar": iar_block
        }

    except Exception as e:
        # As per protocol, on fatal error, we emit a fallback IAR with confidence=0.
        error_iar = {
            "confidence": 0.0,
            "potential_issues": ["LLM_PROVIDER_FAILURE", str(e)],
            "notes": "A fatal error occurred during the API call to the base model."
        }
        return {
            "text": None,
            "tool_calls": None,
            "citations": None,
            "iar": error_iar
        }

# Example Usage Block
if __name__ == "__main__":
    print("--- Running LLM Provider Self-Test ---")
    if not _is_configured:
        print("Skipping test: GEMINI_API_KEY is not set or configuration failed.")
    else:
        test_prompt = "Explain the concept of 'Implementation Resonance' in the context of a software protocol."
        print(f"Test Prompt: {test_prompt}\n")
        result = invoke_llm_tool(test_prompt, system_prompt="You are ArchE, an AI assistant governed by the ResonantiA Protocol.")
        
        if result and result.get('text'):
            print("--- LLM Output ---")
            print(result.get("text"))
            print("\n--- IAR Block ---")
            import json
            print(json.dumps(result.get("iar"), indent=2))
            print("\n--- Self-Test Passed ---")
        else:
            print("--- Self-Test Failed ---")
            print("Received error:")
            import json
            print(json.dumps(result.get("iar"), indent=2))
