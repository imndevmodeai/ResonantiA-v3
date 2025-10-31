# This package contains various LLM provider implementations
from .base import BaseLLMProvider, LLMProviderError
from .google import GoogleProvider
from .cursor_arche import CursorArchEProvider
try:
    from .groq import GroqProvider
    GROQ_AVAILABLE = True
except ImportError:
    GroqProvider = None
    GROQ_AVAILABLE = False
from ..thought_trail import log_to_thought_trail

@log_to_thought_trail
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
                'openai': 'openai_api_key',
                'groq': 'groq_api_key',
                'cursor': 'cursor_arche_key',  # Not required but kept for consistency
                'cursor_arche': 'cursor_arche_key'
            }
            api_key_attr = api_key_attr_map.get(provider_name_lower)
            if api_key_attr and provider_name_lower not in ['cursor', 'cursor_arche', 'arche']:
                # Cursor ArchE doesn't require an API key, skip the check
                api_key = getattr(config_obj.api_keys, api_key_attr, None)
                if not api_key:
                    raise ValueError(f"No API key found for provider '{provider_name}' in configuration.")
        except Exception as e:
            raise ValueError(f"Could not retrieve API key for provider '{provider_name}': {e}")
    
    # Create provider instance based on name
    if provider_name_lower in ['cursor', 'cursor_arche', 'arche']:
        # Cursor ArchE provider (me, the AI assistant) - doesn't strictly need API key
        return CursorArchEProvider(api_key=api_key or "cursor_arche_v1")
    elif provider_name_lower == 'openai':
        # Import OpenAI provider if available
        try:
            from ..llm_providers import OpenAIProvider
            return OpenAIProvider(api_key=api_key)
        except ImportError:
            raise ValueError(f"OpenAI provider not available")
    elif provider_name_lower == 'google':
        return GoogleProvider(api_key=api_key)
    elif provider_name_lower == 'groq':
        if not GROQ_AVAILABLE:
            raise ValueError(f"Groq provider not available. Install with: pip install groq")
        if GroqProvider is None:
            raise ValueError(f"Groq provider not available. Install with: pip install groq")
        return GroqProvider(api_key=api_key)
    else:
        raise ValueError(f"Unsupported LLM provider: '{provider_name}'. Supported providers: cursor, openai, google, groq")

def get_model_for_provider(provider_name: str) -> str:
    """
    Returns a default model for a given provider.
    In a real implementation, this would read from config.
    
    NOTE: Changed from gemini-2.5-pro to gemini-2.0-flash-exp
    Reason: 2.5-pro blocks RISE workflow "agent" prompts, 2.0-flash-exp works perfectly
    """
    provider_name_lower = provider_name.lower() if provider_name else ""
    
    if provider_name_lower in ['cursor', 'cursor_arche', 'arche']:
        return "cursor-arche-v1"  # Cursor ArchE (me, the AI assistant)
    elif provider_name_lower == "google":
        return "gemini-2.0-flash-exp"  # More permissive, handles agent terminology
    elif provider_name_lower == "groq":
        return "llama-3.1-70b-versatile"  # Best quality, free tier
    else:
        # Fallback for other potential providers
        return "default-model"
