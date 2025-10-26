# This package contains various LLM provider implementations
from .base import BaseLLMProvider, LLMProviderError
from .google import GoogleProvider

def get_llm_provider(provider_name: str = "google", api_key: str = None):
    """
    Factory function to get an LLM provider instance.
    
    Args:
        provider_name: Name of the provider ('openai', 'google', etc.)
        api_key: Optional API key. If not provided, will try to get from config.
        
    Returns:
        An instance of the requested LLM provider.
        
    Raises:
        ValueError: If provider is not supported or configuration is invalid.
        LLMProviderError: If provider initialization fails.
    """
    if provider_name is None:
        provider_name = "google" # Default to google
    provider_name_lower = provider_name.lower()
    
    # Get API key from config if not provided
    if not api_key:
        try:
            from .. import config
            config_obj = config.get_config()
            # Map provider names to actual config attribute names
            api_key_attr_map = {
                'google': 'google_api_key',
                'openai': 'openai_api_key'
            }
            api_key_attr = api_key_attr_map.get(provider_name_lower)
            if api_key_attr:
                api_key = getattr(config_obj.api_keys, api_key_attr, None)
            if not api_key:
                raise ValueError(f"No API key found for provider '{provider_name}' in configuration.")
        except Exception as e:
            raise ValueError(f"Could not retrieve API key for provider '{provider_name}': {e}")
    
    # Create provider instance based on name
    if provider_name_lower == 'openai':
        # Import OpenAI provider if available
        try:
            from ..llm_providers import OpenAIProvider
            return OpenAIProvider(api_key=api_key)
        except ImportError:
            raise ValueError(f"OpenAI provider not available")
    elif provider_name_lower == 'google':
        return GoogleProvider(api_key=api_key)
    else:
        raise ValueError(f"Unsupported LLM provider: '{provider_name}'. Supported providers: openai, google")

def get_model_for_provider(provider_name: str) -> str:
    """
    Returns a default model for a given provider.
    In a real implementation, this would read from config.
    
    NOTE: Changed from gemini-2.5-pro to gemini-2.0-flash-exp
    Reason: 2.5-pro blocks RISE workflow "agent" prompts, 2.0-flash-exp works perfectly
    """
    if provider_name == "google":
        return "gemini-2.0-flash-exp"  # More permissive, handles agent terminology
    else:
        # Fallback for other potential providers
        return "default-model"
