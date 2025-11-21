import json
import os
import logging
from typing import Dict, Any

# Corrected import: Import the specific factory functions directly.
from Three_PointO_ArchE.llm_providers import get_llm_provider, get_model_for_provider
from Three_PointO_ArchE.iar_components import IAR_Prepper
import re

logger = logging.getLogger(__name__)

def invoke_llm_for_synthesis(**kwargs) -> Dict[str, Any]:
    """
    Invokes the appropriate LLM provider to synthesize information.
    Includes a pre-flight check for empty search results.
    """
    prompt = kwargs.get('prompt')
    if not prompt:
        return {
            "status": "error",
            "reason": "Input dictionary must contain a 'prompt' key.",
            "generated_text": "{}"
        }
        
    # Prong 2: Input Validation Pre-flight check
    # Use regex to find the search results section of the prompt
    match = re.search(r"SEARCH RESULTS:\s*(\[\]|NONE)", prompt, re.IGNORECASE)
    if match:
        # If the search results are empty, do not call the LLM.
        iar_prepper = IAR_Prepper("generate_text_llm", {"prompt": prompt, **kwargs})
        return {
            "status": "skipped",
            "reason": "Input search results were empty. LLM call was not made.",
            "generated_text": "{}", # Return empty JSON to satisfy downstream tasks
            "reflection": iar_prepper.finish_with_success({
                "status": "skipped",
                "reason": "Input search results were empty."
            })
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
        provider_name = kwargs.get('provider') # Can be None, factory will use default

        # Use the factory to get the correct, configured provider instance
        # Check if fallback provider is enabled
        enable_fallback = kwargs.get('enable_fallback', os.getenv('ARCHE_ENABLE_LLM_FALLBACK', 'true').lower() == 'true')
        
        if enable_fallback:
            try:
                from Three_PointO_ArchE.llm_providers.fallback_provider import FallbackLLMProvider
                # Use fallback provider with cascading loopback
                # Fallback chain: groq (both keys) -> cursor -> google -> openai -> mistral
                provider = FallbackLLMProvider(
                    primary_provider=provider_name or 'groq',
                    fallback_chain=['groq', 'cursor', 'google', 'openai', 'mistral'],
                    enable_zepto=kwargs.get('enable_zepto', os.getenv('ARCHE_ENABLE_ZEPTO_LLM', 'false').lower() == 'true')
                )
                logger.info(f"Using FallbackLLMProvider with primary: {provider_name or 'groq'}")
            except ImportError:
                logger.warning("FallbackLLMProvider not available, using direct provider")
                provider = get_llm_provider(provider_name)
        else:
            provider = get_llm_provider(provider_name)
        
        # Determine which model to use (input > provider default > provider backup)
        # For fallback provider, use primary provider's model
        if hasattr(provider, 'primary_provider'):
            model_to_use = model or get_model_for_provider(provider.primary_provider)
        else:
            model_to_use = model or get_model_for_provider(provider._provider_name)

        logger.info(f"Invoking LLM provider '{provider._provider_name}' with model '{model_to_use}'.")

        # --- CORRECTED PARAMETER HANDLING ---
        # Provider-aware parameter mapping
        # Google uses 'max_output_tokens', while Groq and others use 'max_tokens'
        
        # Unpack model_settings if it exists, otherwise use top-level kwargs.
        model_params = kwargs.get('model_settings', {})
        
        # Get max_tokens value from either source
        max_tokens_value = model_params.get('max_tokens', kwargs.get('max_tokens', 4096))
        temperature_value = model_params.get('temperature', kwargs.get('temperature', 0.7))
        
        # Start with a clean dictionary for the final generation config
        generation_config = {}
        
        # Map parameters based on provider
        provider_name = provider._provider_name.lower()
        
        if provider_name == 'google':
            # Google GenAI API uses 'max_output_tokens'
            VALID_GOOGLE_PARAMS = {'max_output_tokens', 'temperature', 'top_p', 'top_k', 'candidate_count', 'stop_sequences'}
            generation_config['max_output_tokens'] = max_tokens_value
            generation_config['temperature'] = temperature_value
            
            # Filter and pass through only the valid, known additional parameters
            all_potential_params = {**kwargs, **model_params}
            for key, value in all_potential_params.items():
                if key in VALID_GOOGLE_PARAMS and key not in generation_config:
                    generation_config[key] = value
        else:
            # Groq and other providers use 'max_tokens'
            generation_config['max_tokens'] = max_tokens_value
            generation_config['temperature'] = temperature_value
            
            # Remove any Google-specific parameters that might cause issues
            # and pass through other standard parameters
            # Also exclude RISE workflow context variables that shouldn't be passed to LLM providers
            excluded_params = {
                'max_output_tokens', 'model_settings', 'provider', 'model', 'prompt', 'context',
                # RISE workflow context variables (not valid LLM API parameters)
                'problem_description', 'strategy_dossier', 'user_query', 'session_id',
                'workflow_name', 'workflow_run_id', 'initial_context', 'query', 'problem',
                'vetting_report', 'vetting_dossier', 'original_strategy', 'final_strategy'
            }
            all_potential_params = {**kwargs, **model_params}
            for key, value in all_potential_params.items():
                if key not in excluded_params and key not in generation_config:
                    generation_config[key] = value

        generated_text = provider.generate(
            prompt=prompt,
            model=model_to_use,
            **generation_config
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