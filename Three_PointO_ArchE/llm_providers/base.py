"""
Base classes for LLM providers.
"""
import logging
from typing import Dict, Any, Optional, List
from ..thought_trail import log_to_thought_trail

logger = logging.getLogger(__name__)

# Google Generative AI availability check
try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    genai = None
    GOOGLE_AVAILABLE = False

# --- Custom Exception Class ---
class LLMProviderError(Exception):
    """Custom exception for LLM provider related errors."""
    def __init__(self, message: str, provider: Optional[str] = None, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.provider = provider
        self.original_exception = original_exception

    def __str__(self):
        msg = super().__str__()
        if self.provider:
            msg = f"[{self.provider} Error] {msg}"
        if self.original_exception:
            msg += f" (Original: {type(self.original_exception).__name__}: {self.original_exception})"
        return msg

# --- Base Provider Class ---
class BaseLLMProvider:
    """Abstract base class for all LLM providers."""
    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        """
        Initializes the provider. Requires API key.

        Args:
            api_key: The API key for the provider.
            base_url: Optional base URL for custom endpoints or proxies.
            **kwargs: Additional provider-specific arguments from config.
        """
        if not api_key or not isinstance(api_key, str):
            raise ValueError(f"{self.__class__.__name__} requires a valid API key string.")
        self.api_key = api_key
        self.base_url = base_url
        self.provider_kwargs = kwargs # Store extra config args
        self._provider_name = self.__class__.__name__.replace("Provider", "").lower() # e.g., 'openai'
        try:
            # Initialize the specific client library connection
            self._client = self._initialize_client()
            logger.info(f"{self.__class__.__name__} initialized successfully.")
        except Exception as e_init:
            # Wrap initialization errors in LLMProviderError
            raise LLMProviderError(f"Failed to initialize {self.__class__.__name__}", provider=self._provider_name, original_exception=e_init) from e_init

    def _initialize_client(self):
        """Placeholder for initializing the provider-specific client."""
        raise NotImplementedError("Subclasses must implement _initialize_client.")

    @log_to_thought_trail
    def generate(self, prompt: str, model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """Generates text based on a single prompt (completion style)."""
        raise NotImplementedError("Subclasses must implement generate or generate_chat.")

    @log_to_thought_trail
    def generate_chat(self, messages: List[Dict[str, str]], model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """
        Generates text based on a list of chat messages (chat completion style).
        Provides a default implementation using the 'generate' method if not overridden.
        """
        logger.debug(f"Using default generate_chat implementation for {self.__class__.__name__} (converting messages to prompt).")
        # Construct a simple prompt from messages
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user').capitalize()
            content = msg.get('content', '')
            prompt_parts.append(f"{role}: {content}")
        # Add a final prompt for the assistant's turn
        prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
        # Call the standard generate method
        return self.generate(prompt, model, max_tokens, temperature, **kwargs)
