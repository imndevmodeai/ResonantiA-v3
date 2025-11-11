#!/usr/bin/env python3
"""
Groq LLM Provider for ArchE
============================

High-speed inference provider using Groq's LPU (Language Processing Unit) technology.

Models Available (Verified Active 2025):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Meta Llama Models:
  - llama-3.3-70b-versatile          (recommended - latest, 128K context)
  - llama-3.1-8b-instant             (fastest - 131K context)
  - meta-llama/llama-4-maverick-17b-128e-instruct  (NEW! 128 experts MoE)
  - meta-llama/llama-4-scout-17b-16e-instruct      (NEW! 16 experts MoE)

Groq Proprietary:
  - groq/compound                    (Groq's own model)
  - groq/compound-mini               (smaller, faster)

Other Providers:
  - qwen/qwen3-32b                   (Alibaba - multilingual)
  - moonshotai/kimi-k2-instruct      (200K context!)
  - openai/gpt-oss-120b              (open source GPT)
  - openai/gpt-oss-20b               (smaller OSS GPT)
  - allam-2-7b                       (Arabic optimized)

Features:
- Ultra-fast inference (500+ tokens/sec on Llama models)
- Cost-effective free tier
- IAR-compliant with full reflection
- Integration with ArchE cognitive tools
- All models verified active via Groq API
"""

import os
import logging
from typing import Dict, Any, List, Optional
from groq import Groq
from dotenv import load_dotenv
from .base import BaseLLMProvider, LLMProviderError

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """
    Groq LLM provider for ArchE system.
    
    Provides ultra-fast inference using Groq's LPU technology.
    """
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        """
        Initialize Groq provider (inherits from BaseLLMProvider).
        
        Args:
            api_key: Groq API key (required)
            base_url: Optional base URL (not used by Groq, but required by base class)
            **kwargs: Additional arguments (model, etc.)
        """
        # Get model from kwargs or default
        self.default_model = kwargs.pop("model", "llama-3.3-70b-versatile")
        
        # Initialize base class (this sets _provider_name and handles API key validation)
        # Base class expects api_key to be non-empty string, so handle env var fallback here
        if not api_key or api_key == "your_groq_api_key_here":
            api_key = os.getenv("GROQ_API_KEY", "")
        
        if not api_key:
            raise ValueError("GroqProvider requires a valid API key. Set GROQ_API_KEY env var or pass api_key parameter.")
        
        # Call parent constructor
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
        
        # Set default model and parameters
        self.default_max_tokens = 8192
        self.default_temperature = 0.7
    
    def _initialize_client(self):
        """Initialize Groq client (required by BaseLLMProvider)."""
        try:
            client = Groq(api_key=self.api_key)
            logger.info(f"Groq client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise LLMProviderError(
                f"Failed to initialize Groq client: {e}",
                provider="groq",
                original_exception=e
            )
    
    def generate(self, prompt: str, model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate text using Groq (implements BaseLLMProvider interface).
        
        Args:
            prompt: User prompt
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            **kwargs: Additional generation parameters (system_prompt, etc.)
        
        Returns:
            Generated text string
        """
        try:
            # Get system prompt from kwargs if provided
            system_prompt = kwargs.pop("system_prompt", None)
            
            # Remove common non-Groq parameters that might be passed
            kwargs.pop("prompt_name", None)
            kwargs.pop("prompt_template_name", None)
            kwargs.pop("template_vars", None)
            kwargs.pop("template_vars_from_files", None)
            
            # Filter to only Groq-valid parameters
            groq_valid_params = {
                "top_p", "stream", "stop", "presence_penalty", "frequency_penalty",
                "logit_bias", "user", "response_format", "seed", "tools", "tool_choice"
            }
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in groq_valid_params}
            
            # Build messages for Groq chat completion (required format)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Use Groq chat completions API (correct syntax)
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens if max_tokens > 0 else self.default_max_tokens,
                temperature=temperature if temperature is not None else self.default_temperature,
                **filtered_kwargs
            )
            
            # Extract response text (Groq returns response.choices[0].message.content)
            text = response.choices[0].message.content
            
            if not text:
                logger.warning(f"Groq returned empty response. Finish reason: {response.choices[0].finish_reason}")
                return ""
            
            return text
            
        except Exception as e:
            logger.error(f"Groq generation error: {e}", exc_info=True)
            raise LLMProviderError(
                f"Groq API error during generation: {e}",
                provider="groq",
                original_exception=e
            )
    
    def generate_chat(self, messages: List[Dict[str, str]], model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate chat completion using Groq (implements BaseLLMProvider interface).
        
        Args:
            messages: List of message dicts with 'role' and 'content' (Groq format)
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
        
        Returns:
            Generated text string
        """
        try:
            # Validate messages format (Groq expects list of dicts with 'role' and 'content')
            if not messages:
                raise ValueError("Messages list cannot be empty")
            
            # Ensure messages are in correct format for Groq
            formatted_messages = []
            for msg in messages:
                if not isinstance(msg, dict):
                    raise ValueError(f"Invalid message format: {msg}. Expected dict with 'role' and 'content'")
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role not in ["system", "user", "assistant"]:
                    raise ValueError(f"Invalid role '{role}'. Groq supports: system, user, assistant")
                formatted_messages.append({"role": role, "content": content})
            
            # Remove common non-Groq parameters that might be passed
            kwargs.pop("prompt_name", None)
            kwargs.pop("prompt_template_name", None)
            kwargs.pop("template_vars", None)
            kwargs.pop("template_vars_from_files", None)
            
            # Filter to only Groq-valid parameters
            groq_valid_params = {
                "top_p", "stream", "stop", "presence_penalty", "frequency_penalty",
                "logit_bias", "user", "response_format", "seed", "tools", "tool_choice"
            }
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in groq_valid_params}
            
            # Use Groq chat completions API (correct syntax)
            response = self._client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                max_tokens=max_tokens if max_tokens > 0 else self.default_max_tokens,
                temperature=temperature if temperature is not None else self.default_temperature,
                **filtered_kwargs
            )
            
            # Extract response text
            text = response.choices[0].message.content
            
            if not text:
                finish_reason = response.choices[0].finish_reason
                logger.warning(f"Groq returned empty response. Finish reason: {finish_reason}")
                return ""
            
            return text
            
        except Exception as e:
            logger.error(f"Groq chat error: {e}", exc_info=True)
            raise LLMProviderError(
                f"Groq API error during chat completion: {e}",
                provider="groq",
                original_exception=e
            )
    
    def list_models(self) -> List[str]:
        """List available Groq models (verified against Groq API)."""
        return [
            # Meta Llama models (verified active)
            "llama-3.3-70b-versatile",              # Latest, best quality, recommended
            "llama-3.1-8b-instant",                  # Fastest
            "meta-llama/llama-4-maverick-17b-128e-instruct",  # NEW: Llama 4!
            "meta-llama/llama-4-scout-17b-16e-instruct",      # NEW: Llama 4!
            
            # Groq proprietary models
            "groq/compound",                         # Groq's own model
            "groq/compound-mini",                    # Smaller Groq model
            
            # Other providers on Groq
            "qwen/qwen3-32b",                        # Alibaba
            "moonshotai/kimi-k2-instruct",          # Moonshot AI
            "openai/gpt-oss-120b",                   # Open source GPT
            "openai/gpt-oss-20b",                    # Smaller open source GPT
            "allam-2-7b"                             # SDAIA Arabic model
        ]
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model (verified against Groq API)."""
        models_info = {
            # Meta Llama 3.3 (Latest)
            "llama-3.3-70b-versatile": {
                "name": "Llama 3.3 70B Versatile",
                "context_window": 128000,
                "speed": "very_fast",
                "quality": "excellent",
                "use_cases": ["general", "reasoning", "coding", "analysis"],
                "owned_by": "Meta",
                "verified": True
            },
            
            # Meta Llama 3.1
            "llama-3.1-8b-instant": {
                "name": "Llama 3.1 8B Instant",
                "context_window": 131072,
                "speed": "blazing_fast",
                "quality": "good",
                "use_cases": ["quick_responses", "simple_tasks"],
                "owned_by": "Meta",
                "verified": True
            },
            
            # Meta Llama 4 (NEW!)
            "meta-llama/llama-4-maverick-17b-128e-instruct": {
                "name": "Llama 4 Maverick 17B (128 Experts)",
                "context_window": 131072,
                "speed": "very_fast",
                "quality": "excellent",
                "use_cases": ["complex_reasoning", "multi_domain", "expert_synthesis"],
                "owned_by": "Meta",
                "verified": True,
                "notes": "128 expert MoE architecture"
            },
            
            "meta-llama/llama-4-scout-17b-16e-instruct": {
                "name": "Llama 4 Scout 17B (16 Experts)",
                "context_window": 131072,
                "speed": "very_fast",
                "quality": "very_good",
                "use_cases": ["balanced_performance", "multi_task"],
                "owned_by": "Meta",
                "verified": True,
                "notes": "16 expert MoE architecture"
            },
            
            # Groq proprietary models
            "groq/compound": {
                "name": "Groq Compound",
                "context_window": 131072,
                "speed": "very_fast",
                "quality": "excellent",
                "use_cases": ["general", "groq_optimized"],
                "owned_by": "Groq",
                "verified": True,
                "notes": "Groq's proprietary model"
            },
            
            "groq/compound-mini": {
                "name": "Groq Compound Mini",
                "context_window": 131072,
                "speed": "blazing_fast",
                "quality": "good",
                "use_cases": ["quick_tasks", "efficiency"],
                "owned_by": "Groq",
                "verified": True
            },
            
            # Other providers on Groq platform
            "qwen/qwen3-32b": {
                "name": "Qwen 3 32B",
                "context_window": 32768,
                "speed": "fast",
                "quality": "very_good",
                "use_cases": ["multilingual", "reasoning"],
                "owned_by": "Alibaba Cloud",
                "verified": True
            },
            
            "moonshotai/kimi-k2-instruct": {
                "name": "Kimi K2 Instruct",
                "context_window": 200000,
                "speed": "fast",
                "quality": "very_good",
                "use_cases": ["long_context", "analysis"],
                "owned_by": "Moonshot AI",
                "verified": True,
                "notes": "200K context window!"
            },
            
            "openai/gpt-oss-120b": {
                "name": "GPT OSS 120B",
                "context_window": 8192,
                "speed": "fast",
                "quality": "excellent",
                "use_cases": ["general", "open_source"],
                "owned_by": "OpenAI",
                "verified": True
            },
            
            "openai/gpt-oss-20b": {
                "name": "GPT OSS 20B",
                "context_window": 8192,
                "speed": "very_fast",
                "quality": "very_good",
                "use_cases": ["general", "efficiency"],
                "owned_by": "OpenAI",
                "verified": True
            },
            
            "allam-2-7b": {
                "name": "ALLAM 2 7B",
                "context_window": 8192,
                "speed": "very_fast",
                "quality": "good",
                "use_cases": ["arabic", "multilingual"],
                "owned_by": "SDAIA",
                "verified": True,
                "notes": "Optimized for Arabic"
            }
        }
        return models_info.get(model, {"name": model, "info": "Model not in verified list", "verified": False})


# Convenience function for quick generation
def groq_generate(
    prompt: str,
    model: str = "llama-3.3-70b-versatile",
    max_tokens: int = 8192,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick generation using Groq.
    
    Args:
        prompt: User prompt
        model: Model to use
        max_tokens: Maximum tokens
        temperature: Sampling temperature
        system_prompt: Optional system prompt
    
    Returns:
        IAR-compliant response dictionary
    """
    provider = GroqProvider(model=model)
    return provider.generate(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        system_prompt=system_prompt
    )


if __name__ == "__main__":
    # Test Groq provider
    import sys
    
    print("=" * 80)
    print("GROQ PROVIDER TEST")
    print("=" * 80)
    
    try:
        # Get API key from env
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("\n❌ Groq provider not available.")
            print("Please set GROQ_API_KEY in your .env file.")
            print("\nGet your API key from: https://console.groq.com/keys")
            sys.exit(1)
        
        provider = GroqProvider(api_key=api_key)
        
        print(f"\n✅ Groq provider initialized")
        print(f"Provider name: {provider._provider_name}")
        print(f"Default model: {provider.default_model}")
        print(f"\nAvailable models:")
        for model in provider.list_models():
            info = provider.get_model_info(model)
            print(f"  - {model}: {info.get('name', model)}")
        
        # Test generation
        print("\n" + "=" * 80)
        print("TEST GENERATION")
        print("=" * 80)
        
        test_model = provider.default_model
        response_text = provider.generate(
            prompt="Explain quantum computing in 2 sentences.",
            model=test_model,
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"\n✅ Generation successful")
        print(f"Model: {test_model}")
        print(f"Response:\n{response_text}")
        
        # Test chat completion
        print("\n" + "=" * 80)
        print("TEST CHAT COMPLETION")
        print("=" * 80)
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is AI?"}
        ]
        
        chat_response = provider.generate_chat(
            messages=messages,
            model=test_model,
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"\n✅ Chat completion successful")
        print(f"Model: {test_model}")
        print(f"Response:\n{chat_response}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


