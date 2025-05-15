# --- START OF FILE 3.0ArchE/llm_providers.py ---
# ResonantiA Protocol v3.0 - llm_providers.py
# Provides a standardized interface for interacting with various LLM APIs.
# Abstracts provider-specific details for use by the invoke_llm tool.

import logging
import os
import json
from typing import Dict, Any, Optional, List, Type, Tuple
import numpy as np # For QuantizationUtils if/when fully implemented
# Use relative imports for configuration
try:
    from . import config
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

# --- Conceptual Placeholder for Quantization Utilities ---
# Based on your findings in arche_v3, this is where QuantizationUtils for model weights would go.
# For now, it's a conceptual stub. The WorkflowEngine will have its own data quantization mixin.

class QuantizationUtils:
    """
    Conceptual placeholder for utility class for quantizing and dequantizing model weights.
    This is for LLM model weights, distinct from potential data quantization in the workflow engine.
    Actual implementation would involve details for different bit depths (e.g., 8, 4, 2 bits).
    """
    @staticmethod
    def quantize_weights(weights: np.ndarray, bits: int = 8) -> Tuple[np.ndarray, float, float]:
        """Simulates weight quantization. Not a functional implementation."""
        logger.info(f"Conceptual: Quantizing weights to {bits} bits.")
        if not isinstance(weights, np.ndarray):
            raise TypeError("Weights must be a NumPy array.")
        # This is a very naive simulation. Real quantization is much more complex.
        scale = np.max(np.abs(weights)) / ((2**(bits - 1)) - 1)
        zero_point = 0.0 # Simplified for symmetric quantization
        quantized_weights = np.round(weights / scale).astype(np.int8) # Example for int8
        logger.warning("QuantizationUtils.quantize_weights is a non-functional stub.")
        return quantized_weights, float(scale), float(zero_point)

    @staticmethod
    def dequantize_weights(quantized: np.ndarray, scale: float, zero_point: float) -> np.ndarray:
        """Simulates weight dequantization. Not a functional implementation."""
        logger.info(f"Conceptual: Dequantizing weights with scale={scale}, zero_point={zero_point}.")
        if not isinstance(quantized, np.ndarray):
            raise TypeError("Quantized weights must be a NumPy array.")
        logger.warning("QuantizationUtils.dequantize_weights is a non-functional stub.")
        return quantized.astype(float) * scale # Simplified
    
    @staticmethod
    def mixed_precision_matmul(A: np.ndarray, B: np.ndarray, quantize_a: bool = True, quantize_b: bool = True, bits: int = 8) -> np.ndarray:
        """Simulates mixed-precision matrix multiplication. Not functional."""
        logger.info(f"Conceptual: Mixed-precision matmul, quantize_A={quantize_a}, quantize_B={quantize_b}, bits={bits}.")
        if quantize_a:
            A_quant, scale_a, zp_a = QuantizationUtils.quantize_weights(A, bits)
            A_dequant = QuantizationUtils.dequantize_weights(A_quant, scale_a, zp_a)
        else:
            A_dequant = A
        if quantize_b:
            B_quant, scale_b, zp_b = QuantizationUtils.quantize_weights(B, bits)
            B_dequant = QuantizationUtils.dequantize_weights(B_quant, scale_b, zp_b)
        else:
            B_dequant = B
        logger.warning("QuantizationUtils.mixed_precision_matmul is a non-functional stub performing float multiplication.")
        return A_dequant @ B_dequant

# --- Base LLM Provider (Abstract Concept) ---
class BaseLLMProvider:
    """
    Abstract base class for LLM providers. Defines a common interface.
    Actual implementations would handle API calls to specific services (OpenAI, Google, etc.).
    """
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
    def _initialize_client(self) -> Optional[Any]: # Returns the genai module/object
        """Configures the Google Generative AI client using the 'google-generativeai' library."""
        if not GOOGLE_AVAILABLE:
            raise LLMProviderError("Google Generative AI library not installed.", provider="google")
        try:
            # Configuration is typically done once via genai.configure
            genai.configure(api_key=self.api_key)
            # Optional: Add transport, client_options from provider_kwargs if needed
            # genai.configure(api_key=self.api_key, **self.provider_kwargs)
            logger.info("Google Generative AI client configured successfully.")
            # Return the configured module itself or a specific client object if the library provides one
            return genai # Return the module as the 'client'
        except GoogleApiExceptions.GoogleAPIError as e:
            raise LLMProviderError(f"Google API configuration failed", provider="google", original_exception=e)
        except Exception as e_init:
            raise LLMProviderError(f"Unexpected Google configuration error", provider="google", original_exception=e_init)

    def _prepare_google_config(self, max_tokens: int, temperature: float, kwargs: Dict[str, Any]) -> Tuple[Optional[Any], Optional[List[Dict[str, str]]]]:
        """Helper to create GenerationConfig and safety_settings for Google API calls."""
        if not GOOGLE_AVAILABLE: return None, None # Should not happen if initialized

        # Generation Config (temperature, max tokens, top_p, top_k)
        gen_config_args = {"temperature": temperature}
        if max_tokens is not None: gen_config_args["max_output_tokens"] = max_tokens
        if 'top_p' in kwargs: gen_config_args["top_p"] = kwargs['top_p']
        if 'top_k' in kwargs: gen_config_args["top_k"] = kwargs['top_k']
        # Add stop_sequences if needed: gen_config_args["stop_sequences"] = kwargs.get('stop_sequences')
        generation_config = self._client.types.GenerationConfig(**gen_config_args)

        # Safety Settings (customize or disable as needed)
        # Default: Block most harmful content at medium threshold
        safety_settings = kwargs.get('safety_settings')
        if safety_settings is None: # Apply default safety if not overridden
            safety_settings = [
                {"category": c, "threshold": "BLOCK_MEDIUM_AND_ABOVE"} for c in [
                        "HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
                        "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"
                ]
            ]
        # Example to disable safety: safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in [...]]
        # Note: Disabling safety might violate terms of service.

        return generation_config, safety_settings

    def generate(self, prompt: str, model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """Generates text using the Google GenerativeModel generate_content method."""
        if not self._client: raise LLMProviderError("Google client not configured.", provider="google")
        logger.debug(f"Calling Google generate_content for model '{model}'")

        try:
            generation_config, safety_settings = self._prepare_google_config(max_tokens, temperature, kwargs)
            # Get the generative model instance
            llm = self._client.GenerativeModel(model_name=model)
            # Make the API call
            response = llm.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
                # Add stream=False if needed, tools=... for function calling
            )

            # --- Process Google Response ---
            try:
                # Accessing response.text raises ValueError if blocked
                text_response = response.text
                logger.debug(f"Google generation successful. Finish Reason: {getattr(response, 'candidates', [{}])[0].get('finish_reason', 'N/A')}")
                # Check for truncation (might require parsing response differently if API indicates it)
                # if getattr(response, 'candidates', [{}])[0].get('finish_reason') == 'MAX_TOKENS':
                #     logger.warning(f"Google response may be truncated due to max_output_tokens.")
                return text_response
            except ValueError as e_resp_val:
                # This typically indicates the response was blocked due to safety or other reasons
                logger.warning(f"ValueError accessing Google response text (likely blocked or empty): {e_resp_val}")
                try:
                    # Attempt to get block reason from prompt_feedback
                    block_reason = response.prompt_feedback.block_reason
                    block_message = response.prompt_feedback.block_reason_message
                    logger.error(f"Google generation blocked. Reason: {block_reason}. Message: {block_message}")
                    raise LLMProviderError(f"Content blocked by Google API. Reason: {block_reason}", provider="google")
                except AttributeError:
                    # If prompt_feedback or block_reason isn't available
                    logger.error(f"Google generation failed. Could not access response text and no block reason found. Response: {response}")
                    raise LLMProviderError("Google response blocked or invalid, reason unavailable.", provider="google")
            except AttributeError as e_attr:
                # Handle cases where the response structure is missing expected attributes like '.text'
                logger.error(f"Google response object missing expected attribute '.text'. Response structure: {response}. Error: {e_attr}")
                raise LLMProviderError("Google response format unexpected (missing .text).", provider="google")

        # --- Handle Google API Specific Errors ---
        except GoogleApiExceptions.PermissionDenied as e:
            logger.error(f"Google API Permission Denied: {e}. Check API key and project permissions.")
            raise LLMProviderError(f"Google API Permission Denied", provider="google", original_exception=e)
        except GoogleApiExceptions.ResourceExhausted as e: # Rate limiting
            logger.error(f"Google API Resource Exhausted (Rate Limit): {e}.")
            raise LLMProviderError(f"Google API Resource Exhausted (Rate Limit)", provider="google", original_exception=e)
        except GoogleApiExceptions.InvalidArgument as e: # Errors in request parameters
            logger.error(f"Google API Invalid Argument: {e}. Check model name, parameters, prompt format.")
            raise LLMProviderError(f"Google API Invalid Argument", provider="google", original_exception=e)
        except GoogleApiExceptions.GoogleAPIError as e: # Catch other general Google API errors
            logger.error(f"Google API error: {e}")
            raise LLMProviderError(f"Google API error", provider="google", original_exception=e)
        except Exception as e_unexp:
            # Catch any other unexpected exceptions
            logger.error(f"Unexpected error during Google generation: {e_unexp}", exc_info=True)
            raise LLMProviderError(f"Unexpected Google generation error", provider="google", original_exception=e_unexp)

    def generate_chat(self, messages: List[Dict[str, str]], model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """Generates text using the Google GenerativeModel chat session (start_chat/send_message)."""
        if not self._client: raise LLMProviderError("Google client not configured.", provider="google")
        logger.debug(f"Calling Google generate_chat (using chat session) for model '{model}'")

        # Validate message format
        if not isinstance(messages, list) or not messages:
            raise ValueError("Input 'messages' must be a non-empty list of dictionaries.")

        # Convert ResonantiA roles ('user', 'assistant') to Google roles ('user', 'model')
        history = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            if role and content is not None:
                google_role = 'model' if role == 'assistant' else 'user'
                # Google expects content as a list of parts (usually just one text part)
                history.append({'role': google_role, 'parts': [content]})
            else:
                logger.warning(f"Skipping invalid message format in chat history: {msg}")
        if not history: raise ValueError("Chat history is empty after processing messages.")

        # Google's chat requires the last message to be from the 'user'
        if history[-1]['role'] != 'user':
            # Option 1: Raise error if last message isn't user (strict)
            # raise ValueError("Last message in chat history must have role 'user' for Google API.")
            # Option 2: Send the whole history as context if last is 'model' (less conversational)
            logger.warning("Last chat message role is 'model'. Sending full history as context to generate_content instead of chat.")
            try:
                generation_config, safety_settings = self._prepare_google_config(max_tokens, temperature, kwargs)
                llm = self._client.GenerativeModel(model_name=model)
                response = llm.generate_content(history, generation_config=generation_config, safety_settings=safety_settings)
                # Process response (same logic as in generate method)
                try: text_response = response.text; return text_response
                except ValueError as e_resp_val: raise LLMProviderError(f"Content blocked by Google API. Reason: {getattr(response.prompt_feedback, 'block_reason', 'Unknown')}", provider="google") from e_resp_val
                except AttributeError: raise LLMProviderError("Google response format unexpected (missing .text).", provider="google")
            except Exception as e_gen_cont: raise LLMProviderError("Failed to generate content from history.", provider="google", original_exception=e_gen_cont) from e_gen_cont


        try:
            generation_config, safety_settings = self._prepare_google_config(max_tokens, temperature, kwargs)
            llm = self._client.GenerativeModel(model_name=model)

            # Start chat session with history *excluding* the last user message
            chat_session = llm.start_chat(history=history[:-1])
            # Send the last user message
            response = chat_session.send_message(
                history[-1]['parts'], # Send content of the last user message
                generation_config=generation_config,
                safety_settings=safety_settings
                # stream=False
            )

            # --- Process Google Response (same as generate method) ---
            try:
                text_response = response.text
                logger.debug(f"Google chat generation successful. Finish Reason: {getattr(response, 'candidates', [{}])[0].get('finish_reason', 'N/A')}")
                return text_response
            except ValueError as e_resp_val:
                logger.warning(f"ValueError accessing Google chat response text (likely blocked): {e_resp_val}")
                try:
                    block_reason = response.prompt_feedback.block_reason
                    block_message = response.prompt_feedback.block_reason_message
                    logger.error(f"Google chat generation blocked. Reason: {block_reason}. Message: {block_message}")
                    raise LLMProviderError(f"Chat content blocked by Google API. Reason: {block_reason}", provider="google")
                except AttributeError:
                    logger.error(f"Google chat generation failed. Could not access response text and no block reason found. Response: {response}")
                    raise LLMProviderError("Google chat response blocked or invalid, reason unavailable.", provider="google")
            except AttributeError as e_attr:
                logger.error(f"Google chat response object missing expected attribute '.text'. Response structure: {response}. Error: {e_attr}")
                raise LLMProviderError("Google chat response format unexpected (missing .text).", provider="google")

        # --- Handle Google API Specific Errors (same as generate method) ---
        except GoogleApiExceptions.PermissionDenied as e: raise LLMProviderError(f"Google API Permission Denied", provider="google", original_exception=e)
        except GoogleApiExceptions.ResourceExhausted as e: raise LLMProviderError(f"Google API Resource Exhausted (Rate Limit)", provider="google", original_exception=e)
        except GoogleApiExceptions.InvalidArgument as e: raise LLMProviderError(f"Google API Invalid Argument", provider="google", original_exception=e)
        except GoogleApiExceptions.GoogleAPIError as e: raise LLMProviderError(f"Google API error", provider="google", original_exception=e)
        except Exception as e_unexp: raise LLMProviderError(f"Unexpected Google chat generation error", provider="google", original_exception=e_unexp)


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
        # Construct conventional environment variable name (e.g., OPENAI_API_KEY)
        env_var_name = f"{provider_name_lower.upper()}_API_KEY"
        api_key_env = os.environ.get(env_var_name)
        if api_key_env:
            logger.info(f"Using API key for '{provider_name_lower}' from environment variable {env_var_name}.")
            api_key = api_key_env
        else:
            # If key is missing/placeholder in config AND not found in env var, raise error
            raise ValueError(f"API key for '{provider_name_lower}' is missing or placeholder in config and not found in environment variable {env_var_name}.")

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

# --- END OF FILE 3.0ArchE/llm_providers.py ---