"""
LLM Provider implementation for Groq API.
Groq provides high-speed inference for open-source models like Llama 3.
"""
import logging
from typing import Optional, Any, List, Dict
import os

logger = logging.getLogger(__name__)

# Try to import groq library
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_AVAILABLE = False

from .base import BaseLLMProvider, LLMProviderError
from ..thought_trail import log_to_thought_trail

class GroqProvider(BaseLLMProvider):
    """
    LLM Provider implementation for Groq API.
    
    Groq provides very fast inference for open-source models like Llama 3,
    Mixtral, and others. Free tier: 14,400 requests/day.
    """
    
    def _initialize_client(self) -> Optional[Any]:
        """Initializes the Groq client."""
        if not GROQ_AVAILABLE:
            raise LLMProviderError(
                "Groq library not installed. Install with: pip install groq",
                provider="groq"
            )
        
        try:
            client = Groq(api_key=self.api_key)
            logger.info("Groq client initialized successfully.")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}", exc_info=True)
            raise LLMProviderError(
                f"Failed to initialize Groq client: {e}",
                provider="groq",
                original_exception=e
            ) from e

    @log_to_thought_trail
    def generate(self, prompt: str, model: str = "llama-3.1-70b-versatile", max_tokens: int = 2048, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate text using Groq.
        
        Available models:
        - llama-3.1-70b-versatile (best quality)
        - llama-3.1-8b-instant
        - mixtral-8x7b-32768
        - gemma-7b-it
        - llama-v2-70b-chat
        
        Args:
            prompt: Input prompt for the model
            model: Model name to use (default: llama-3.1-70b-versatile)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        try:
            if not self._client:
                raise LLMProviderError("Groq client not initialized", provider="groq")
            
            # Generate completion
            response = self._client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract response text
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise LLMProviderError("No response generated", provider="groq")
                
        except Exception as e:
            error_message = str(e)
            error_type = type(e).__name__
            logger.error(f"Groq generation failed: {error_type}: {error_message}", exc_info=True)
            
            raise LLMProviderError(
                f"Groq generation failed: {error_type}: {error_message}",
                provider="groq",
                original_exception=e
            ) from e

    @log_to_thought_trail
    def generate_chat(self, messages: List[Dict[str, str]], model: str = "llama-3.1-70b-versatile", max_tokens: int = 2048, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate chat completion using Groq.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional parameters
            
        Returns:
            Generated chat response
        """
        try:
            if not self._client:
                raise LLMProviderError("Groq client not initialized", provider="groq")
            
            # Generate chat completion
            response = self._client.chat.completions.create(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise LLMProviderError("No chat response generated", provider="groq")
                
        except Exception as e:
            logger.error(f"Groq chat generation failed: {e}", exc_info=True)
            raise LLMProviderError(
                f"Groq chat generation failed: {e}",
                provider="groq",
                original_exception=e
            ) from e

