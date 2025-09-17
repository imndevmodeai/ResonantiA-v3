# --- START OF FILE Three_PointO_ArchE/llm_providers.py ---
# ResonantiA Protocol v3.0 - llm_providers.py
# Provides a standardized interface for interacting with various LLM APIs.
# Abstracts provider-specific details for use by the invoke_llm tool.

import logging
import os
import json
from typing import Dict, Any, Optional, List, Type, Tuple # Expanded type hints
# Use relative imports for configuration
try:
    from . import config
except ImportError:
    try:
        import config
    except ImportError:
        # Fallback config if running standalone or package structure differs
        class FallbackConfig: DEFAULT_LLM_PROVIDER = 'openai'; LLM_PROVIDERS = {'openai': {}, 'google': {}}
        config = FallbackConfig(); logging.warning("config.py not found for llm_providers, using fallback configuration.")

# --- Import Provider-Specific SDKs ---
# Import libraries only if they are intended to be used and installed.
# Set flags indicating availability.

# OpenAI
try:
    # Use 'openai' package version >= 1.0
    from openai import OpenAI, OpenAIError, APIError, RateLimitError, APIConnectionError, AuthenticationError
    OPENAI_AVAILABLE = True
    logger_prov = logging.getLogger(__name__)
    logger_prov.info("OpenAI library found.")
except ImportError:
    # Define dummy classes/exceptions if library is not installed
    OpenAI = None; OpenAIError = None; APIError = Exception; RateLimitError = Exception; APIConnectionError = Exception; AuthenticationError = Exception;
    OPENAI_AVAILABLE = False
    logging.getLogger(__name__).warning("OpenAI library not installed. OpenAIProvider will be unavailable.")

# Google Generative AI (Gemini)
try:
    import google.generativeai as genai
    from google.api_core import exceptions as GoogleApiExceptions # Specific exceptions
    GOOGLE_AVAILABLE = True
    logger_prov = logging.getLogger(__name__)
    logger_prov.info("Google Generative AI library found.")
except ImportError:
    genai = None; GoogleApiExceptions = None;
    GOOGLE_AVAILABLE = False
    logging.getLogger(__name__).warning("Google Generative AI library not installed. GoogleProvider will be unavailable.")

# Anthropic (Example - Uncomment if needed)
# try:
#     from anthropic import Anthropic, APIError as AnthropicAPIError # Example import
#     ANTHROPIC_AVAILABLE = True
#     logger_prov = logging.getLogger(__name__)
#     logger_prov.info("Anthropic library found.")
# except ImportError:
#     Anthropic = None; AnthropicAPIError = Exception
#     ANTHROPIC_AVAILABLE = False
#     logging.getLogger(__name__).warning("Anthropic library not installed. AnthropicProvider will be unavailable.")


logger = logging.getLogger(__name__) # Logger for this module

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

    def generate(self, prompt: str, model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """Generates text based on a single prompt (completion style)."""
        raise NotImplementedError("Subclasses must implement generate or generate_chat.")

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

# --- OpenAI Provider Implementation ---
class OpenAIProvider(BaseLLMProvider):
    """LLM Provider implementation for OpenAI models (GPT-3.5, GPT-4, etc.)."""
    def _initialize_client(self) -> Optional[OpenAI]:
        """Initializes the OpenAI client using the 'openai' library >= v1.0."""
        if not OPENAI_AVAILABLE:
            raise LLMProviderError("OpenAI library not installed.", provider="openai")
        try:
            client_args = {"api_key": self.api_key}
            # Add base_url if provided in config (for proxies like LiteLLM, Azure OpenAI)
            if self.base_url:
                client_args["base_url"] = self.base_url
                logger.info(f"Initializing OpenAI client with custom base URL: {self.base_url}")
            else:
                logger.info("Initializing OpenAI client with default base URL.")

            # Add any other relevant kwargs from config (e.g., timeout, max_retries - check openai lib docs)
            client_args.update(self.provider_kwargs)

            client = OpenAI(**client_args)
            # Optional: Perform a simple test call like listing models? Might be too slow/costly.
            # client.models.list()
            return client
        except OpenAIError as e:
            # Catch specific OpenAI errors during initialization
            raise LLMProviderError(f"OpenAI client initialization failed", provider="openai", original_exception=e)
        except Exception as e_init:
            # Catch other unexpected errors
            raise LLMProviderError(f"Unexpected OpenAI initialization error", provider="openai", original_exception=e_init)

    def generate(self, prompt: str, model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """Generates text using OpenAI's ChatCompletion endpoint (preferred even for single prompts)."""
        if not self._client: raise LLMProviderError("OpenAI client not initialized.", provider="openai")
        logger.debug(f"Calling OpenAI generate (using ChatCompletion) for model '{model}'")
        # Convert single prompt to chat message format
        messages = [{"role": "user", "content": prompt}]
        # Combine default params with any overrides from kwargs
        api_kwargs = {"max_tokens": max_tokens, "temperature": temperature, **kwargs}
        # Delegate to the chat generation method
        return self._call_openai_chat(messages, model, api_kwargs)

    def generate_chat(self, messages: List[Dict[str, str]], model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """Generates text using OpenAI's ChatCompletion endpoint."""
        if not self._client: raise LLMProviderError("OpenAI client not initialized.", provider="openai")
        logger.debug(f"Calling OpenAI generate_chat for model '{model}'")
        # Validate message format
        if not isinstance(messages, list) or not all(isinstance(m, dict) and 'role' in m and 'content' in m for m in messages):
            raise ValueError("Input 'messages' must be a list of dictionaries, each with 'role' and 'content' keys.")
        # Combine default params with any overrides from kwargs
        api_kwargs = {"max_tokens": max_tokens, "temperature": temperature, **kwargs}
        return self._call_openai_chat(messages, model, api_kwargs)

    def _call_openai_chat(self, messages: List[Dict[str, str]], model: str, api_kwargs: Dict[str, Any]) -> str:
        """Internal helper to make the ChatCompletion API call and handle errors."""
        try:
            # Make the API call
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                **api_kwargs # Pass combined parameters
            )
            # Process the response
            if response.choices and len(response.choices) > 0:
                message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason
                if message and message.content:
                    content = message.content.strip()
                    logger.debug(f"OpenAI call successful. Finish reason: {finish_reason}. Tokens: {response.usage}") # Log usage if available
                    if finish_reason == "length":
                        logger.warning(f"OpenAI response truncated due to max_tokens ({api_kwargs.get('max_tokens')}). Consider increasing max_tokens.")
                    elif finish_reason == "content_filter":
                        logger.warning(f"OpenAI response stopped due to content filter.")
                    return content
                else:
                    # Handle cases where content might be empty or message object is unexpected
                    logger.warning(f"OpenAI response message content is empty or missing. Finish reason: {finish_reason}.")
                    return "" # Return empty string for empty content
            else:
                # Handle cases where response structure is unexpected (no choices)
                logger.warning(f"OpenAI response missing 'choices' array. Full response: {response}")
                return "" # Return empty string if no valid choice found
        except AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error: {e}. Check API key validity and permissions.")
            raise LLMProviderError(f"OpenAI Authentication Error", provider="openai", original_exception=e)
        except RateLimitError as e:
            logger.error(f"OpenAI Rate Limit Error: {e}. Check usage limits and billing.")
            raise LLMProviderError(f"OpenAI Rate Limit Error", provider="openai", original_exception=e)
        except APIConnectionError as e:
            logger.error(f"OpenAI API Connection Error: {e}. Check network connectivity and OpenAI status.")
            raise LLMProviderError(f"OpenAI API Connection Error", provider="openai", original_exception=e)
        except APIError as e: # Catch broader OpenAI API errors
            logger.error(f"OpenAI API Error: {e} (Status Code: {getattr(e, 'status_code', 'N/A')}, Type: {getattr(e, 'type', 'N/A')})")
            raise LLMProviderError(f"OpenAI API error ({getattr(e, 'status_code', 'N/A')})", provider="openai", original_exception=e)
        except Exception as e_unexp:
            # Catch any other unexpected exceptions during the API call
            logger.error(f"Unexpected error during OpenAI API call: {e_unexp}", exc_info=True)
            raise LLMProviderError(f"Unexpected OpenAI API error", provider="openai", original_exception=e_unexp)

# --- Google Provider Implementation ---
class GoogleProvider(BaseLLMProvider):
    """LLM Provider implementation for Google Generative AI models (Gemini)."""
    def _initialize_client(self) -> Optional[Any]:
        """Configures the Google Generative AI client using the 'google-generativeai' library."""
        if not GOOGLE_AVAILABLE:
            raise LLMProviderError("Google Generative AI library not installed.", provider="google")
        try:
            # Configuration is typically done once via genai.configure
            genai.configure(api_key=self.api_key)
            # Enable code execution and other advanced features
            genai.configure(
                api_key=self.api_key,
                transport="rest",  # Use REST transport for better compatibility
                client_options={
                    "api_endpoint": "generativelanguage.googleapis.com",
                    "quota_project_id": self.provider_kwargs.get("quota_project_id")
                }
            )
            logger.info("Google Generative AI client configured successfully with advanced capabilities.")
            return genai
        except GoogleApiExceptions.GoogleAPIError as e:
            raise LLMProviderError(f"Google API configuration failed", provider="google", original_exception=e)
        except Exception as e_init:
            raise LLMProviderError(f"Unexpected Google configuration error", provider="google", original_exception=e_init)

    def _prepare_google_config(self, max_tokens: int, temperature: float, kwargs: Dict[str, Any]) -> Tuple[Optional[Any], Optional[List[Dict[str, str]]]]:
        """Helper to create GenerationConfig and safety_settings for Google API calls."""
        if not GOOGLE_AVAILABLE: return None, None

        # Enhanced Generation Config with new capabilities
        gen_config_args = {
            "temperature": temperature,
            "candidate_count": kwargs.get("candidate_count", 1),
            "stop_sequences": kwargs.get("stop_sequences", []),
            "top_p": kwargs.get("top_p", 0.95),
            "top_k": kwargs.get("top_k", 40)
        }
        if max_tokens is not None: gen_config_args["max_output_tokens"] = max_tokens
        
        # Add structured output configuration if specified
        if "output_schema" in kwargs:
            gen_config_args["output_schema"] = kwargs["output_schema"]
            
        generation_config = self._client.types.GenerationConfig(**gen_config_args)

        # Safety Settings with configurable thresholds
        safety_settings = kwargs.get('safety_settings')
        if safety_settings is None:
            safety_settings = [
                {"category": c, "threshold": kwargs.get("safety_threshold", "BLOCK_MEDIUM_AND_ABOVE")} 
                for c in [
                    "HARM_CATEGORY_HARASSMENT", 
                    "HARM_CATEGORY_HATE_SPEECH",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT", 
                    "HARM_CATEGORY_DANGEROUS_CONTENT"
                ]
            ]

        return generation_config, safety_settings

    def _prepare_tools_config(self, kwargs: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Prepare tools configuration for function calling."""
        tools = kwargs.get("tools", [])
        if not tools:
            return None
            
        formatted_tools = []
        for tool in tools:
            formatted_tool = {
                "name": tool.get("name"),
                "description": tool.get("description"),
                "parameters": tool.get("parameters", {})
            }
            formatted_tools.append(formatted_tool)
        return formatted_tools

    def _prepare_grounding_config(self, kwargs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Prepare grounding configuration for source-based responses."""
        grounding = kwargs.get("grounding")
        if not grounding:
            return None
            
        return {
            "sources": grounding.get("sources", []),
            "citation_style": grounding.get("citation_style", "default"),
            "citation_format": grounding.get("citation_format", "text")
        }

    def generate(self, prompt: str, model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """Enhanced text generation with support for code execution, grounding, and function calling."""
        if not self._client: 
            raise LLMProviderError("Google client not configured.", provider="google")
        logger.debug(f"Calling Google generate_content for model '{model}' with enhanced capabilities")

        try:
            # Prepare configurations
            generation_config, safety_settings = self._prepare_google_config(max_tokens, temperature, kwargs)
            
            # --- FORCE DISABLE FUNCTION CALLING ---
            tool_config = {'function_calling_config': {'mode': 'none'}}
            
            # Get the generative model instance
            llm = self._client.GenerativeModel(
                model_name=model,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tool_config=tool_config # Explicitly set tool config
            )

            # Prepare content parts
            content_parts = [prompt]
            
            # Add file content if provided
            if "file_content" in kwargs:
                content_parts.append(kwargs["file_content"])
                
            # Add grounding sources if provided
            grounding_config = self._prepare_grounding_config(kwargs)
            if grounding_config and grounding_config.get("sources"):
                content_parts.extend(grounding_config["sources"])

            # Make the API call with detailed error handling
            try:
                logger.info(f"Sending request to Google API. Prompt: '{str(prompt)[:100]}...'")
                # Add a request timeout to prevent indefinite hanging
                request_options = {"timeout": 60} # 60 second timeout
                response = llm.generate_content(
                    content_parts,
                    request_options=request_options
                )
                logger.info("Received response from Google API.")
            except Exception as api_call_error:
                logger.error(f"Direct exception during llm.generate_content call: {api_call_error}", exc_info=True)
                raise LLMProviderError("Exception during API call to Google.", provider="google", original_exception=api_call_error)


            # Process response with enhanced error handling
            try:
                # Handle regular text response first
                if hasattr(response, 'text') and response.text:
                    text_response = response.text
                    finish_reason = getattr(response.candidates[0], 'finish_reason', 'N/A') if response.candidates else 'N/A'
                    logger.debug(f"Google generation successful. Finish Reason: {finish_reason}")
                    
                    # Add citations if present
                    if hasattr(response, 'citations') and response.citations:
                        text_response += "\n\nCitations:\n" + "\n".join(
                            f"- {citation.text}: {citation.url}" 
                            for citation in response.citations
                        )
                    
                    return text_response

                # Handle function calls if present (but we disabled them, so this should not happen)
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        # Check for function calls
                        if hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'function_call'):
                                    fn = getattr(part.function_call, 'name', '')
                                    args = getattr(part.function_call, 'args', None)
                                    logger.warning(f"Unexpected function call detected despite being disabled: {fn}")
                                    # Return a fallback response instead of function call
                                    return f"I apologize, but I encountered an issue generating a proper response. Please try rephrasing your request."

                # Fallback to detailed parsing
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    first_candidate = response.candidates[0]
                    text_response = first_candidate.content.parts[0].text
                    finish_reason = first_candidate.finish_reason
                    logger.debug(f"Google generation successful (via candidates). Finish Reason: {finish_reason}")
                    return text_response
                
                # Additional fallback for empty responses
                if response.candidates and response.candidates[0]:
                    candidate = response.candidates[0]
                    finish_reason = getattr(candidate, 'finish_reason', 'N/A')
                    logger.warning(f"Google response has no text content. Finish Reason: {finish_reason}")
                    
                    # Return a helpful message based on finish reason
                    if finish_reason == 1:  # SAFETY
                        return "I apologize, but I cannot provide a response to that request due to safety concerns."
                    elif finish_reason == 2:  # RECITATION
                        return "I apologize, but I cannot provide a response to that request."
                    else:
                        return "I received your message, but I am unable to generate a response at this time."
                    
                raise LLMProviderError("Google response format unexpected or empty", provider="google")

            except ValueError as e_resp_val:
                logger.warning(f"ValueError accessing Google response: {e_resp_val}")
                if hasattr(response, 'prompt_feedback'):
                    block_reason = getattr(response.prompt_feedback, 'block_reason', 'unknown')
                    # block_reason_message might not exist in all versions
                    try:
                        block_message = getattr(response.prompt_feedback, 'block_reason_message', 'No additional details')
                    except AttributeError:
                        block_message = 'No additional details'
                    raise LLMProviderError(
                        f"Content blocked by Google API. Reason: {block_reason}. Message: {block_message}", 
                        provider="google"
                    )
                raise LLMProviderError("Google response blocked or invalid", provider="google")

        except GoogleApiExceptions.GoogleAPIError as e:
            logger.error(f"Google API error: {e}")
            raise LLMProviderError(f"Google API error: {str(e)}", provider="google", original_exception=e)
        except Exception as e_unexp:
            logger.error(f"Unexpected error during Google generation: {e_unexp}", exc_info=True)
            raise LLMProviderError(f"Unexpected Google generation error", provider="google", original_exception=e_unexp)

    def execute_code(self, code: str, **kwargs) -> Dict[str, Any]:
        """Execute Python code using Gemini's built-in code interpreter."""
        if not self._client:
            raise LLMProviderError("Google client not configured.", provider="google")
            
        try:
            llm = self._client.GenerativeModel(model_name="gemini-1.5-pro-latest")
            response = llm.generate_content(
                f"Execute the following Python code and return the results:\n```python\n{code}\n```",
                generation_config=self._client.types.GenerationConfig(
                    temperature=0.0,  # Use 0 temperature for code execution
                    max_output_tokens=kwargs.get("max_tokens", 1000)
                )
            )
            
            if hasattr(response, 'text'):
                return {
                    "output": response.text,
                    "status": "success",
                    "error": None
                }
            else:
                return {
                    "output": None,
                    "status": "error",
                    "error": "Failed to get execution results"
                }
                
        except Exception as e:
            return {
                "output": None,
                "status": "error",
                "error": str(e)
            }

    def process_file(self, file_url: str, **kwargs) -> Dict[str, Any]:
        """Process a file from a URL using Gemini's file handling capabilities."""
        if not self._client:
            raise LLMProviderError("Google client not configured.", provider="google")
            
        try:
            llm = self._client.GenerativeModel(model_name="gemini-1.5-pro-latest")
            response = llm.generate_content(
                f"Process and analyze the content of this file: {file_url}",
                generation_config=self._client.types.GenerationConfig(
                    temperature=kwargs.get("temperature", 0.7),
                    max_output_tokens=kwargs.get("max_tokens", 1000)
                )
            )
            
            if hasattr(response, 'text'):
                return {
                    "content": response.text,
                    "status": "success",
                    "error": None
                }
            else:
                return {
                    "content": None,
                    "status": "error",
                    "error": "Failed to process file"
                }
                
        except Exception as e:
            return {
                "content": None,
                "status": "error",
                "error": str(e)
            }

# --- Provider Factory ---
# Maps provider names (lowercase) to their implementation classes.
PROVIDER_MAP: Dict[str, Type[BaseLLMProvider]] = {}
if OPENAI_AVAILABLE:
    PROVIDER_MAP["openai"] = OpenAIProvider
if GOOGLE_AVAILABLE:
    PROVIDER_MAP["google"] = GoogleProvider
# if ANTHROPIC_AVAILABLE: # Example
#     PROVIDER_MAP["anthropic"] = AnthropicProvider

def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """
    Factory function to get an initialized LLM provider instance based on name.
    Uses default provider from config if name is None. Reads config for API keys etc.

    Args:
        provider_name (str, optional): The name of the provider (e.g., 'openai', 'google').
                                    If None, uses config.DEFAULT_LLM_PROVIDER.

    Returns:
        An initialized instance of the requested BaseLLMProvider subclass.

    Raises:
        ValueError: If the provider name is invalid, not configured, or library unavailable.
        LLMProviderError: If initialization of the provider fails (e.g., bad API key).
    """
    provider_name_to_use = provider_name or getattr(config, 'DEFAULT_LLM_PROVIDER', None)
    if not provider_name_to_use:
        raise ValueError("No LLM provider specified and no default provider configured.")

    provider_name_lower = provider_name_to_use.lower()

    # Check if provider is configured in config.py
    if provider_name_lower not in getattr(config, 'LLM_PROVIDERS', {}):
        raise ValueError(f"Configuration for LLM provider '{provider_name_to_use}' not found in config.LLM_PROVIDERS.")

    # Check if provider implementation class exists and its library is available
    if provider_name_lower not in PROVIDER_MAP:
        available_impl = list(PROVIDER_MAP.keys())
        raise ValueError(f"LLM Provider implementation '{provider_name_to_use}' not available or library not installed. Available: {available_impl}")

    # Get configuration for the specific provider
    provider_config = config.LLM_PROVIDERS[provider_name_lower]

    # Get API key (prefer config value, fallback to env var based on convention)
    api_key = provider_config.get("api_key")
    if not api_key or "YOUR_" in api_key or "_HERE" in api_key:
        # Environment variable resolution with Gemini alias
        env_names = [f"{provider_name_lower.upper()}_API_KEY"]
        if provider_name_lower == "google":
            env_names.append("GEMINI_API_KEY")
        api_key_env = None
        for env_var_name in env_names:
            api_key_env = os.environ.get(env_var_name)
            if api_key_env:
                logger.info(f"Using API key for '{provider_name_lower}' from environment variable {env_var_name}.")
                break
        if api_key_env:
            api_key = api_key_env
        else:
            raise ValueError(f"API key for '{provider_name_lower}' not found. Checked: {env_names}.")

    # Get optional base_url
    base_url = provider_config.get("base_url") # Will be None if not present

    # Get the provider class
    ProviderClass = PROVIDER_MAP[provider_name_lower]

    try:
        # Extract additional kwargs from config for the provider, excluding standard ones
        init_kwargs = {k: v for k, v in provider_config.items() if k not in ['api_key', 'base_url', 'default_model', 'backup_model']}
        # Create and return the provider instance
        provider_instance = ProviderClass(api_key=api_key, base_url=base_url, **init_kwargs)
        # Store the provider name on the instance for potential error reporting
        provider_instance._provider_name = provider_name_lower # type: ignore
        return provider_instance
    except LLMProviderError as e:
        # Catch and re-raise initialization errors from the provider constructor
        logger.error(f"Failed to initialize provider '{provider_name_to_use}': {e}")
        raise e
    except Exception as e_create:
        # Catch other unexpected errors during instantiation
        logger.error(f"Unexpected error creating provider instance for '{provider_name_to_use}': {e_create}", exc_info=True)
        raise LLMProviderError(f"Could not create provider instance for '{provider_name_to_use}'.", provider=provider_name_lower, original_exception=e_create)

def get_model_for_provider(provider_name: Optional[str] = None) -> str:
    """
    Determines the appropriate model name to use for a given provider.
    Prioritizes config.DEFAULT_LLM_MODEL, then provider's default, then provider's backup.

    Args:
        provider_name (str, optional): Name of the provider. Uses default if None.

    Returns:
        The resolved model name string.

    Raises:
        ValueError: If no suitable model name can be found in the configuration.
    """
    provider_name_to_use = provider_name or getattr(config, 'DEFAULT_LLM_PROVIDER', None)
    if not provider_name_to_use:
        raise ValueError("Cannot determine model: No provider specified and no default provider configured.")

    provider_name_lower = provider_name_to_use.lower()
    provider_configs = getattr(config, 'LLM_PROVIDERS', {})
    if provider_name_lower not in provider_configs:
        raise ValueError(f"Configuration for LLM provider '{provider_name_to_use}' not found.")

    provider_config = provider_configs[provider_name_lower]

    # Priority: Global default -> Provider default -> Provider backup
    model = getattr(config, 'DEFAULT_LLM_MODEL', None) # Check global default first
    if not model:
        model = provider_config.get("default_model") # Check provider's default
        if not model:
            model = provider_config.get("backup_model") # Check provider's backup
            if not model:
                    # If no model found after checking all levels, raise error
                    raise ValueError(f"No default or backup model configured for provider '{provider_name_to_use}' in config.py.")
            else:
                    logger.warning(f"Default model not found for '{provider_name_lower}', using configured backup model '{model}'.")
        else:
            logger.debug(f"Using default model '{model}' configured for provider '{provider_name_lower}'.")
    else:
        logger.debug(f"Using globally configured default model '{model}' for provider '{provider_name_lower}'.")

    return model

# --- END OF FILE Three_PointO_ArchE/llm_providers.py --- 