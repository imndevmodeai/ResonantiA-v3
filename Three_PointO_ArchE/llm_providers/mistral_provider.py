#!/usr/bin/env python3
"""
Mistral AI LLM Provider for ArchE

Mistral AI recently launched a free tier for developers (September 2024).
This provider enables ArchE to use Mistral's models as an alternative to Groq.

Free Tier: Available for testing and prototyping
Models: mistral-small-latest, mistral-medium-latest, mistral-large-latest
Speed: Fast inference
Quality: Excellent (comparable to Groq)

Registration: https://console.mistral.ai
API Documentation: https://docs.mistral.ai
"""

import os
import logging
from typing import Optional, List, Dict, Any
from .base import BaseLLMProvider, LLMProviderError

logger = logging.getLogger(__name__)

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    Mistral = None
    MISTRAL_AVAILABLE = False
    logger.warning("mistralai package not installed. Install with: pip install mistralai")


class MistralProvider(BaseLLMProvider):
    """
    Mistral AI LLM provider for ArchE system.
    
    Provides fast inference using Mistral's models with free tier support.
    """
    
    def __init__(self, api_key: str = None, base_url: Optional[str] = None, **kwargs):
        """
        Initialize Mistral provider (inherits from BaseLLMProvider).
        
        Args:
            api_key: Mistral API key (required)
            base_url: Optional base URL (not used by Mistral, but required by base class)
            **kwargs: Additional arguments passed to base class
        """
        if not MISTRAL_AVAILABLE:
            raise LLMProviderError(
                "Mistral provider not available. Install with: pip install mistralai",
                provider="mistral"
            )
        
        # Base class expects api_key to be non-empty string, so handle env var fallback here
        if not api_key or api_key == "your_mistral_api_key_here":
            api_key = os.getenv("MISTRAL_API_KEY", "")
        
        if not api_key:
            raise ValueError("MistralProvider requires a valid API key. Set MISTRAL_API_KEY env var or pass api_key parameter.")
        
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
        self._provider_name = "mistral"
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Mistral client (required by BaseLLMProvider)."""
        try:
            self._client = Mistral(api_key=self.api_key)
            logger.info(f"Mistral client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Mistral client: {e}")
            raise LLMProviderError(
                f"Failed to initialize Mistral client: {e}",
                provider="mistral"
            )
    
    def generate(self, prompt: str, model: str = "mistral-small-latest", **kwargs) -> str:
        """
        Generate text using Mistral (implements BaseLLMProvider interface).
        
        Args:
            prompt: Input prompt text
            model: Model name (default: mistral-small-latest)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated text response
            
        Raises:
            LLMProviderError: If generation fails
        """
        try:
            # Build messages for Mistral chat completion (required format)
            messages = [{"role": "user", "content": prompt}]
            
            # Extract common parameters
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", kwargs.get("max_output_tokens", 4096))
            
            # Use Mistral chat completions API
            response = self._client.chat.complete(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response text (Mistral returns response.choices[0].message.content)
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                logger.warning(f"Mistral returned empty response. Finish reason: {response.choices[0].finish_reason if response.choices else 'unknown'}")
                return ""
                
        except Exception as e:
            logger.error(f"Mistral generation error: {e}", exc_info=True)
            raise LLMProviderError(
                f"Mistral API error during generation: {e}",
                provider="mistral"
            )
    
    def generate_chat(self, messages: List[Dict[str, str]], model: str = "mistral-small-latest", **kwargs) -> str:
        """
        Generate chat completion using Mistral (implements BaseLLMProvider interface).
        
        Args:
            messages: List of message dicts with 'role' and 'content' (Mistral format)
            model: Model name (default: mistral-small-latest)
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
            
        Raises:
            LLMProviderError: If generation fails
        """
        try:
            # Validate messages format (Mistral expects list of dicts with 'role' and 'content')
            if not messages or not isinstance(messages, list):
                raise ValueError("Messages must be a non-empty list")
            
            # Ensure messages are in correct format for Mistral
            formatted_messages = []
            for msg in messages:
                if not isinstance(msg, dict):
                    raise ValueError("Each message must be a dictionary")
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # Validate role (Mistral supports: system, user, assistant)
                if role not in ["system", "user", "assistant"]:
                    raise ValueError(f"Invalid role '{role}'. Mistral supports: system, user, assistant")
                
                formatted_messages.append({"role": role, "content": content})
            
            # Extract common parameters
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", kwargs.get("max_output_tokens", 4096))
            
            # Use Mistral chat completions API
            response = self._client.chat.complete(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response text
            if response.choices and len(response.choices) > 0:
                finish_reason = response.choices[0].finish_reason
                if finish_reason == "stop":
                    return response.choices[0].message.content
                else:
                    logger.warning(f"Mistral returned empty response. Finish reason: {finish_reason}")
                    return ""
            else:
                logger.warning(f"Mistral returned no choices in response")
                return ""
                
        except Exception as e:
            logger.error(f"Mistral chat error: {e}", exc_info=True)
            raise LLMProviderError(
                f"Mistral API error during chat completion: {e}",
                provider="mistral"
            )
    
    def list_models(self) -> List[str]:
        """
        List available Mistral models (verified against Mistral API).
        
        Returns:
            List of available model names
        """
        return [
            "mistral-small-latest",      # Recommended for free tier
            "mistral-medium-latest",      # Better quality
            "mistral-large-latest",       # Best quality
            "mistral-tiny",               # Fastest, smallest
            "pixtral-12b-2409",           # Vision model
        ]
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model (verified against Mistral API).
        
        Args:
            model: Model name
            
        Returns:
            Dictionary with model information
        """
        model_info = {
            "mistral-small-latest": {
                "name": "Mistral Small",
                "description": "Fast and efficient model, recommended for free tier",
                "context_length": 32000,
                "use_cases": ["general", "chat", "code"],
                "owned_by": "Mistral AI",
                "free_tier": True
            },
            "mistral-medium-latest": {
                "name": "Mistral Medium",
                "description": "Balanced performance and quality",
                "context_length": 32000,
                "use_cases": ["general", "chat", "code", "analysis"],
                "owned_by": "Mistral AI",
                "free_tier": True
            },
            "mistral-large-latest": {
                "name": "Mistral Large",
                "description": "Best quality model",
                "context_length": 32000,
                "use_cases": ["general", "chat", "code", "analysis", "complex"],
                "owned_by": "Mistral AI",
                "free_tier": True
            },
            "mistral-tiny": {
                "name": "Mistral Tiny",
                "description": "Fastest, smallest model",
                "context_length": 32000,
                "use_cases": ["quick", "simple"],
                "owned_by": "Mistral AI",
                "free_tier": True
            },
        }
        
        return model_info.get(model, {
            "name": model,
            "description": "Unknown model",
            "context_length": 32000,
            "use_cases": ["general"],
            "owned_by": "Mistral AI",
            "free_tier": True
        })


def mistral_generate(
    prompt: str,
    model: str = "mistral-small-latest",
    api_key: str = None,
    **kwargs
) -> str:
    """
    Quick generation using Mistral.
    
    Args:
        prompt: Input prompt
        model: Model name
        api_key: Optional API key (uses env var if not provided)
        **kwargs: Additional parameters
        
    Returns:
        Generated text
    """
    provider = MistralProvider(api_key=api_key or os.getenv("MISTRAL_API_KEY"))
    return provider.generate(prompt, model=model, **kwargs)


if __name__ == "__main__":
    # Test Mistral provider
    print("MISTRAL PROVIDER TEST")
    print("=" * 50)
    
    try:
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            print("\n❌ Mistral provider not available.")
            print("Please set MISTRAL_API_KEY in your .env file.")
            print("\nGet your API key from: https://console.mistral.ai")
        else:
            provider = MistralProvider(api_key=api_key)
            print(f"\n✅ Mistral provider initialized")
            print(f"Available models: {', '.join(provider.list_models())}")
            
            # Test generation
            test_prompt = "Say hello in a friendly way!"
            print(f"\nTesting with prompt: '{test_prompt}'")
            response = provider.generate(test_prompt)
            print(f"Response: {response}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


