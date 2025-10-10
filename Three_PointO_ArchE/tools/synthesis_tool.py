import json
import os
import logging
from typing import Dict, Any

# Corrected import: Import the entire module to access its factory function.
from .. import llm_providers 
from ..iar_components import IAR_Prepper
import re

logger = logging.getLogger(__name__)

def invoke_llm_for_synthesis(prompt: str, **kwargs) -> Dict[str, Any]:
    """
    Invokes the appropriate LLM provider to synthesize information.
    Includes a pre-flight check for empty search results.
    """
    # Prong 2: Input Validation Pre-flight check
    # Use regex to find the search results section of the prompt
    match = re.search(r"SEARCH RESULTS:\s*(\[\]|NONE)", prompt, re.IGNORECASE)
    if match:
        # If the search results are empty, do not call the LLM.
        return {
            "status": "skipped",
            "reason": "Input search results were empty. LLM call was not made.",
            "generated_text": "{}" # Return empty JSON to satisfy downstream tasks
        }
        
    iar_prepper = IAR_Prepper("generate_text_llm", {"prompt": prompt, **kwargs})
    try:
        if not prompt:
            raise ValueError("Input dictionary must contain a 'prompt' key.")
        
        context = kwargs.get('context', '')
        # Simple context injection if context is provided
        if context:
            # This is a basic placeholder for context injection.
            # A more robust solution might use a templating engine.
            prompt = f"{prompt}\n\n--- Context ---\n{json.dumps(context, indent=2)}"

        model = kwargs.get('model') # Can be None, factory will use default
        provider_name = kwargs.get('provider', 'google') # Can be None, factory will use default

        # Use the factory to get the correct, configured provider instance
        provider = llm_providers.get_llm_provider(provider_name)
        
        # Determine which model to use (input > provider default > provider backup)
        # The model from input is used directly if provided. If not, the factory inside generate will resolve it.
        model_to_use = model or llm_providers.get_model_for_provider(provider._provider_name)


        logger.info(f"Invoking LLM provider '{provider._provider_name}' with model '{model_to_use}'.")

        # Prepare generation parameters
        max_tokens = kwargs.get('max_tokens', 4096)
        temperature = kwargs.get('temperature', 0.7)
        
        # Pass through any other kwargs
        additional_kwargs = {k: v for k, v in kwargs.items() if k not in ['prompt', 'context', 'model', 'provider', 'max_tokens', 'temperature']}

        generated_text = provider.generate(
            prompt=prompt,
            model=model_to_use,
            max_tokens=max_tokens,
            temperature=temperature,
            **additional_kwargs
        )
        
        logger.info("LLM generation successful.")
        result = {"generated_text": generated_text}
        iar_response = iar_prepper.finish_with_success(result)
        
        # Return in the format expected by the workflow engine
        return {
            "result": result,
            "reflection": iar_response
        }

    except Exception as e:
        logger.error(f"Error during LLM synthesis: {e}", exc_info=True)
        # Use IAR Prepper to format the error response
        iar_response = iar_prepper.finish_with_error(str(e))
        
        # Return in the format expected by the workflow engine
        return {
            "result": None,
            "reflection": iar_response,
            "error": str(e)
        }


def synthesize_search_results(user_query: str, search_results: list) -> str:
    """
    Synthesizes search results into a final answer using an LLM.
    This function is now a wrapper around the generic invoke_llm_for_synthesis.
    """
    # This path will need to be adjusted to be relative to the project root
    workflow_path = os.path.join(os.path.dirname(__file__), '../../../workflows/agentic_research.json')

    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        synthesis_task = workflow['tasks']['synthesize_results']
        prompt_template = synthesis_task['inputs']['prompt']
    except (IOError, KeyError) as e:
        logger.error(f"Could not load synthesis prompt from workflow: {e}")
        # Fallback prompt
        prompt_template = "Based on the following search results, please provide a comprehensive answer to the user's query: '{{ initial_context.user_query }}'.\n\nSearch Results:\n{{ execute_searches.results | to_json }}"

    # Prepare the prompt
    prompt = prompt_template.replace('{{ initial_context.user_query }}', user_query)
    prompt = prompt.replace('{{ execute_searches.results | to_json }}', json.dumps(search_results, indent=2))

    # Prepare inputs for the generic LLM tool
    llm_inputs = {
        "prompt": prompt,
        "model": "gemini-1.5-flash", # Or determine dynamically
        "provider": "google",
        "max_tokens": 2048
    }

    # Call the generic synthesis function
    result = invoke_llm_for_synthesis(llm_inputs)

    if result.get('status') == 'success' and result.get('result', {}).get('generated_text'):
        return result['result']['generated_text']
    else:
        error_message = result.get('error', 'An unknown error occurred during synthesis.')
        logger.error(f"Synthesis failed: {error_message}")
        return f"I apologize, but I was unable to synthesize the search results. Error: {error_message}" 