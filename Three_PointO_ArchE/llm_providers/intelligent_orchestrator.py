#!/usr/bin/env python3
"""
Intelligent LLM Provider Orchestrator

Automatically selects the best available LLM provider based on:
- Quota availability
- Free tier limits
- Provider capabilities
- Cost optimization

Handles provider-specific syntax differences and provides unified interface.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from .base import BaseLLMProvider, LLMProviderError
from .quota_tracker import get_quota_tracker
from .multi_key_groq_provider import MultiKeyGroqProvider
from .groq_provider import GroqProvider
from .google import GoogleProvider

# Try to import Mistral (optional)
try:
    from .mistral_provider import MistralProvider
    MISTRAL_AVAILABLE = True
except ImportError:
    MistralProvider = None
    MISTRAL_AVAILABLE = False

# Try to import Groq RateLimitError
try:
    from groq._exceptions import RateLimitError
except ImportError:
    # Fallback: create a dummy exception class
    class RateLimitError(Exception):
        pass

logger = logging.getLogger(__name__)


class IntelligentLLMOrchestrator(BaseLLMProvider):
    """
    Intelligent orchestrator that automatically selects the best LLM provider.
    
    Features:
    - Multi-key support for Groq with automatic rotation
    - Quota tracking and management
    - Automatic fallback when limits are hit
    - Unified interface that handles provider syntax differences
    - Cost optimization (prefers free tier providers)
    """
    
    # Provider priority order (prefer free tier first)
    PROVIDER_PRIORITY = [
        "groq",      # Free tier, fast
        "mistral",   # Free tier, fast
        "google",    # Free tier available, high quality
        "openai",    # Paid, high quality
    ]
    
    def __init__(self, preferred_provider: Optional[str] = None, 
                 enable_multi_key_groq: bool = True, **kwargs):
        """
        Initialize intelligent orchestrator.
        
        Args:
            preferred_provider: Preferred provider (None for auto-selection)
            enable_multi_key_groq: Enable multi-key Groq support
            **kwargs: Additional arguments
        """
        # Use a dummy API key for base class (we'll use actual providers)
        super().__init__(api_key="orchestrator", base_url=None, **kwargs)
        self._provider_name = "intelligent_orchestrator"
        
        self.preferred_provider = preferred_provider
        self.enable_multi_key_groq = enable_multi_key_groq
        self.quota_tracker = get_quota_tracker()
        
        # Provider instances (lazy initialization)
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._current_provider: Optional[BaseLLMProvider] = None
        self._current_provider_name: Optional[str] = None
        
        # Statistics
        self.stats = {
            "total_calls": 0,
            "provider_calls": {},
            "fallbacks": 0,
            "errors": 0,
        }
    
    def _initialize_client(self):
        """Orchestrator doesn't need a client."""
        return None
    
    def _get_provider(self, provider_name: str) -> Optional[BaseLLMProvider]:
        """
        Get or create a provider instance.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider instance or None if unavailable
        """
        if provider_name in self._providers:
            return self._providers[provider_name]
        
        try:
            if provider_name == "groq":
                if self.enable_multi_key_groq:
                    # Check if multiple keys are available
                    api_keys = self._load_groq_keys()
                    if len(api_keys) > 1:
                        provider = MultiKeyGroqProvider(api_keys=api_keys)
                    else:
                        provider = GroqProvider(api_key=api_keys[0] if api_keys else os.getenv("GROQ_API_KEY"))
                else:
                    provider = GroqProvider(api_key=os.getenv("GROQ_API_KEY"))
                    
            elif provider_name == "google":
                provider = GoogleProvider(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
                
            elif provider_name == "mistral":
                if not MISTRAL_AVAILABLE or MistralProvider is None:
                    raise ValueError("Mistral provider not available. Install with: pip install mistralai")
                provider = MistralProvider(api_key=os.getenv("MISTRAL_API_KEY"))
                
            else:
                # Try to get from factory
                from . import get_llm_provider
                provider = get_llm_provider(provider_name)
            
            self._providers[provider_name] = provider
            return provider
            
        except Exception as e:
            logger.warning(f"Failed to initialize provider {provider_name}: {e}")
            return None
    
    def _load_groq_keys(self) -> List[str]:
        """Load all available Groq API keys from environment."""
        keys = []
        
        # Primary key
        primary = os.getenv("GROQ_API_KEY")
        if primary:
            keys.append(primary)
        
        # Additional keys
        i = 1
        while True:
            key = os.getenv(f"GROQ_API_KEY_{i}")
            if not key:
                break
            if key not in keys:
                keys.append(key)
            i += 1
        
        return keys
    
    def _select_best_provider(self, estimated_tokens: int = 0, 
                             model: Optional[str] = None) -> Optional[str]:
        """
        Select the best available provider based on quotas and availability.
        
        Args:
            estimated_tokens: Estimated tokens needed
            model: Desired model (may influence provider selection)
            
        Returns:
            Best provider name or None
        """
        # If model specified, prefer provider that supports it
        if model:
            if "llama" in model.lower() or "groq" in model.lower():
                if self._check_provider_available("groq", estimated_tokens):
                    return "groq"
            elif "gemini" in model.lower() or "google" in model.lower():
                if self._check_provider_available("google", estimated_tokens):
                    return "google"
            elif "mistral" in model.lower():
                if self._check_provider_available("mistral", estimated_tokens):
                    return "mistral"
        
        # Use preferred provider if specified and available
        if self.preferred_provider:
            if self._check_provider_available(self.preferred_provider, estimated_tokens):
                return self.preferred_provider
        
        # Try providers in priority order
        for provider_name in self.PROVIDER_PRIORITY:
            if self._check_provider_available(provider_name, estimated_tokens):
                return provider_name
        
        return None
    
    def _check_provider_available(self, provider_name: str, estimated_tokens: int = 0) -> bool:
        """
        Check if a provider is available and has quota.
        
        Args:
            provider_name: Provider name
            estimated_tokens: Estimated tokens needed
            
        Returns:
            True if available
        """
        # Check if provider can be initialized
        provider = self._get_provider(provider_name)
        if not provider:
            return False
        
        # Check quota for Groq (has specific limits)
        if provider_name == "groq":
            # Check if multi-key Groq has any available keys
            if isinstance(provider, MultiKeyGroqProvider):
                best_key = provider.quota_tracker.get_best_api_key(
                    provider="groq",
                    limit_type="tokens_per_day",
                    required_amount=estimated_tokens
                )
                return best_key is not None
            else:
                # Single key - check quota
                return self.quota_tracker.check_availability(
                    provider="groq",
                    api_key_id="groq_key_1",
                    limit_type="tokens_per_day",
                    required_amount=estimated_tokens
                )
        
        # For other providers, assume available if initialized
        return True
    
    def _normalize_parameters(self, provider_name: str, **kwargs) -> Dict[str, Any]:
        """
        Normalize parameters for provider-specific syntax.
        
        Args:
            provider_name: Provider name
            **kwargs: Original parameters
            
        Returns:
            Normalized parameters
        """
        normalized = kwargs.copy()
        
        # Handle max_tokens vs max_output_tokens
        if "max_output_tokens" in normalized and "max_tokens" not in normalized:
            normalized["max_tokens"] = normalized.pop("max_output_tokens")
        
        # Provider-specific adjustments
        if provider_name == "google":
            # Google uses max_output_tokens
            if "max_tokens" in normalized:
                normalized["max_output_tokens"] = normalized.pop("max_tokens")
        
        return normalized
    
    def generate(self, prompt: str, model: str = None, max_tokens: int = 500, 
                temperature: float = 0.7, **kwargs) -> str:
        """
        Generate text using the best available provider.
        
        Args:
            prompt: Input prompt
            model: Model name (optional, will select best provider)
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        self.stats["total_calls"] += 1
        
        # Estimate tokens needed
        estimated_tokens = len(prompt) // 4 + max_tokens
        
        # Select best provider
        provider_name = self._select_best_provider(estimated_tokens, model)
        if not provider_name:
            raise LLMProviderError(
                "No available LLM providers. All providers have hit rate limits or are unavailable.",
                provider="intelligent_orchestrator"
            )
        
        provider = self._get_provider(provider_name)
        if not provider:
            raise LLMProviderError(
                f"Failed to initialize provider: {provider_name}",
                provider="intelligent_orchestrator"
            )
        
        # Normalize parameters for provider
        normalized_kwargs = self._normalize_parameters(provider_name, **kwargs)
        
        # Try with selected provider, with fallback
        max_fallback_attempts = len(self.PROVIDER_PRIORITY)
        for attempt in range(max_fallback_attempts):
            try:
                # Update current provider
                self._current_provider = provider
                self._current_provider_name = provider_name
                
                # Make the call
                response = provider.generate(
                    prompt=prompt,
                    model=model or self._get_default_model(provider_name),
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **normalized_kwargs
                )
                
                # Record success
                self.stats["provider_calls"][provider_name] = \
                    self.stats["provider_calls"].get(provider_name, 0) + 1
                
                logger.info(f"Successfully generated using {provider_name}")
                return response
                
            except (RateLimitError, LLMProviderError) as e:
                error_str = str(e).lower()
                
                # Check if it's a rate limit error
                if "rate limit" in error_str or "429" in error_str or "quota" in error_str:
                    logger.warning(f"Rate limit hit on {provider_name}, trying fallback...")
                    self.stats["fallbacks"] += 1
                    
                    # Mark provider as unavailable
                    if provider_name == "groq" and isinstance(provider, MultiKeyGroqProvider):
                        # Multi-key provider will handle rotation internally
                        # But if all keys exhausted, try next provider
                        if not provider._get_best_api_key_index(estimated_tokens):
                            provider_name = None  # Force next provider
                    
                    # Try next provider
                    if attempt < max_fallback_attempts - 1:
                        # Remove current provider from consideration
                        remaining_providers = [p for p in self.PROVIDER_PRIORITY 
                                              if p != provider_name]
                        for next_provider_name in remaining_providers:
                            if self._check_provider_available(next_provider_name, estimated_tokens):
                                provider_name = next_provider_name
                                provider = self._get_provider(provider_name)
                                if provider:
                                    normalized_kwargs = self._normalize_parameters(
                                        provider_name, **kwargs
                                    )
                                    break
                        else:
                            # No other providers available
                            self.stats["errors"] += 1
                            raise LLMProviderError(
                                f"All providers exhausted. Last error: {e}",
                                provider="intelligent_orchestrator",
                                original_exception=e
                            )
                    else:
                        self.stats["errors"] += 1
                        raise
                else:
                    # Non-rate-limit error, don't retry
                    self.stats["errors"] += 1
                    raise
        
        self.stats["errors"] += 1
        raise LLMProviderError("Failed to generate after all fallback attempts")
    
    def generate_chat(self, messages: List[Dict[str, str]], model: str = None,
                     max_tokens: int = 500, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate chat completion using best available provider.
        
        Args:
            messages: List of message dicts
            model: Model name
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        # Convert messages to prompt for token estimation
        prompt = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
        estimated_tokens = len(prompt) // 4 + max_tokens
        
        # Select provider
        provider_name = self._select_best_provider(estimated_tokens, model)
        if not provider_name:
            raise LLMProviderError("No available providers")
        
        provider = self._get_provider(provider_name)
        if not provider:
            raise LLMProviderError(f"Failed to initialize provider: {provider_name}")
        
        # Normalize parameters
        normalized_kwargs = self._normalize_parameters(provider_name, **kwargs)
        
        # Call provider's generate_chat if available, otherwise use generate
        if hasattr(provider, 'generate_chat'):
            return provider.generate_chat(
                messages=messages,
                model=model or self._get_default_model(provider_name),
                max_tokens=max_tokens,
                temperature=temperature,
                **normalized_kwargs
            )
        else:
            # Fallback to generate
            return self.generate(prompt, model, max_tokens, temperature, **kwargs)
    
    def _get_default_model(self, provider_name: str) -> str:
        """Get default model for provider."""
        defaults = {
            "groq": "llama-3.3-70b-versatile",
            "google": "gemini-2.0-flash-exp",
            "mistral": "mistral-small-latest",
            "openai": "gpt-4o",
        }
        return defaults.get(provider_name, "default")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            **self.stats,
            "current_provider": self._current_provider_name,
            "available_providers": list(self._providers.keys()),
            "quota_summary": self.quota_tracker.get_usage_summary(),
        }

