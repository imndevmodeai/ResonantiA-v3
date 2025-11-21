#!/usr/bin/env python3
"""
Multi-Key Groq Provider

Supports multiple Groq API keys with automatic rotation and quota management.
Intelligently selects the best available key based on quota usage.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from groq import Groq
from groq._exceptions import RateLimitError
from .base import BaseLLMProvider, LLMProviderError
from .groq_provider import GroqProvider
from .quota_tracker import get_quota_tracker, QuotaTracker
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MultiKeyGroqProvider(BaseLLMProvider):
    """
    Groq provider with support for multiple API keys and automatic rotation.
    
    Automatically selects the best available API key based on quota usage.
    Falls back to next key if current key hits rate limits.
    """
    
    def __init__(self, api_keys: List[str] = None, base_url: Optional[str] = None, **kwargs):
        """
        Initialize multi-key Groq provider.
        
        Args:
            api_keys: List of Groq API keys (if None, loads from env vars)
            base_url: Optional base URL (not used by Groq)
            **kwargs: Additional arguments
        """
        # Load API keys from environment if not provided
        if api_keys is None:
            api_keys = self._load_api_keys_from_env()
        
        if not api_keys:
            raise ValueError(
                "MultiKeyGroqProvider requires at least one API key. "
                "Set GROQ_API_KEY or GROQ_API_KEY_1, GROQ_API_KEY_2, etc."
            )
        
        self.api_keys = api_keys
        self.api_key_ids = [f"groq_key_{i+1}" for i in range(len(api_keys))]
        self.current_key_index = 0
        self.quota_tracker = get_quota_tracker()
        
        # Initialize quota tracking for each key
        for i, key_id in enumerate(self.api_key_ids):
            self.quota_tracker.register_api_key(
                provider="groq",
                api_key_id=key_id,
                limits={
                    "requests_per_day": 14400,
                    "tokens_per_day": 100000,
                }
            )
        
        # Initialize with first key
        super().__init__(api_key=api_keys[0], base_url=base_url, **kwargs)
        self._provider_name = "groq"
        self.default_model = kwargs.pop("model", "llama-3.3-70b-versatile")
        self.default_max_tokens = 8192
        self.default_temperature = 0.7
        
        # Create client for current key
        self._client = self._initialize_client()
    
    def _load_api_keys_from_env(self) -> List[str]:
        """Load API keys from environment variables."""
        keys = []
        seen_keys = set()  # Track seen keys to avoid duplicates
        
        # Try GROQ_API_KEY first
        primary_key = os.getenv("GROQ_API_KEY")
        if primary_key and primary_key not in seen_keys:
            keys.append(primary_key)
            seen_keys.add(primary_key)
        
        # Try GROQ_API_KEY_1, GROQ_API_KEY_2, etc. (sequential numbering)
        i = 1
        while True:
            key = os.getenv(f"GROQ_API_KEY_{i}")
            if not key:
                break
            if key not in seen_keys:  # Avoid duplicates
                keys.append(key)
                seen_keys.add(key)
            i += 1
        
        # Also try GROQ_API_KEY_2 directly (in case user skips _1)
        # This handles cases where user has GROQ_API_KEY and GROQ_API_KEY_2
        key_2 = os.getenv("GROQ_API_KEY_2")
        if key_2 and key_2 not in seen_keys:
            keys.append(key_2)
            seen_keys.add(key_2)
        
        return keys
    
    def _initialize_client(self):
        """Initialize Groq client for current API key."""
        try:
            current_key = self.api_keys[self.current_key_index]
            client = Groq(api_key=current_key)
            logger.info(f"Groq client initialized with key {self.current_key_index + 1}/{len(self.api_keys)}")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise LLMProviderError(
                f"Failed to initialize Groq client: {e}",
                provider="groq",
                original_exception=e
            )
    
    def _get_best_api_key_index(self, estimated_tokens: int = 0) -> int:
        """
        Get the index of the best available API key.
        
        Args:
            estimated_tokens: Estimated tokens needed for the request
            
        Returns:
            Index of best available key, or current index if none better
        """
        best_index = self.current_key_index
        best_remaining = -1.0
        
        for i, key_id in enumerate(self.api_key_ids):
            # Check tokens_per_day availability
            if self.quota_tracker.check_availability(
                provider="groq",
                api_key_id=key_id,
                limit_type="tokens_per_day",
                required_amount=estimated_tokens
            ):
                remaining = self.quota_tracker.quotas["groq"][f"{key_id}_tokens_per_day"].get_remaining()
                if remaining > best_remaining:
                    best_remaining = remaining
                    best_index = i
        
        return best_index
    
    def _switch_to_key(self, key_index: int):
        """Switch to a different API key."""
        if key_index != self.current_key_index:
            self.current_key_index = key_index
            self.api_key = self.api_keys[key_index]
            self._client = self._initialize_client()
            logger.info(f"Switched to Groq API key {key_index + 1}/{len(self.api_keys)}")
    
    def _handle_rate_limit_error(self, error: RateLimitError, estimated_tokens: int = 0):
        """
        Handle rate limit error by switching to next available key.
        
        Args:
            error: The rate limit error
            estimated_tokens: Estimated tokens for the request
            
        Returns:
            True if switched to another key, False if no keys available
        """
        current_key_id = self.api_key_ids[self.current_key_index]
        
        # Extract reset time from error if available
        reset_time = None
        error_message = str(error)
        if "Please try again in" in error_message:
            # Try to extract reset time
            try:
                # Error format: "Please try again in 16m42.239999999s"
                import re
                match = re.search(r'(\d+)m(\d+\.?\d*)s', error_message)
                if match:
                    minutes = int(match.group(1))
                    seconds = float(match.group(2))
                    reset_time = datetime.now() + timedelta(minutes=minutes, seconds=seconds)
            except:
                pass
        
        # Record that this key hit the limit
        if "tokens per day" in error_message.lower():
            limit_type = "tokens_per_day"
            # Use extracted reset_time or calculate next midnight UTC
            if not reset_time:
                reset_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            # Mark as used up (set to limit to show exhausted)
            quota_id = f"{current_key_id}_{limit_type}"
            if "groq" in self.quota_tracker.quotas and quota_id in self.quota_tracker.quotas["groq"]:
                # Set to limit value to show exhausted
                quota = self.quota_tracker.quotas["groq"][quota_id]
                quota.used_value = quota.limit_value
                quota.reset_time = reset_time
                quota.last_updated = datetime.now()
                self.quota_tracker._save_to_storage()
                logger.warning(f"Marked {current_key_id} as exhausted (used: {quota.used_value:.0f}/{quota.limit_value:.0f})")
            else:
                # Fallback: record usage
                self.quota_tracker.record_usage(
                    provider="groq",
                    api_key_id=current_key_id,
                    limit_type=limit_type,
                    amount=100000,  # Mark as exhausted
                    reset_time=reset_time
                )
        
        # Try to switch to another key
        best_index = self._get_best_api_key_index(estimated_tokens)
        if best_index != self.current_key_index:
            self._switch_to_key(best_index)
            return True
        
        # No other keys available
        return False
    
    def generate(self, prompt: str, model: str = None, max_tokens: int = None, 
                temperature: float = None, **kwargs) -> str:
        """
        Generate text using Groq with automatic key rotation.
        
        Args:
            prompt: Input prompt
            model: Model name (default: llama-3.3-70b-versatile)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        # Estimate tokens needed (rough estimate: 1 token ≈ 4 characters)
        estimated_tokens = len(prompt) // 4 + max_tokens
        
        # Select best available key
        best_index = self._get_best_api_key_index(estimated_tokens)
        if best_index != self.current_key_index:
            self._switch_to_key(best_index)
        
        current_key_id = self.api_key_ids[self.current_key_index]
        
        # Try with current key, with retry logic
        max_retries = len(self.api_keys)
        for attempt in range(max_retries):
            try:
                # Build messages for Groq
                messages = [{"role": "user", "content": prompt}]
                
                # Make API call
                response = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                
                # Extract response
                if response.choices and len(response.choices) > 0:
                    response_text = response.choices[0].message.content
                    
                    # Record usage with actual token count from API response
                    actual_tokens = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else estimated_tokens
                    # Calculate reset time: next midnight UTC
                    reset_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                    self.quota_tracker.record_usage(
                        provider="groq",
                        api_key_id=current_key_id,
                        limit_type="tokens_per_day",
                        amount=actual_tokens,
                        reset_time=reset_time
                    )
                    logger.debug(f"Recorded {actual_tokens} tokens for {current_key_id}")
                    
                    return response_text
                else:
                    logger.warning("Groq returned empty response")
                    return ""
                    
            except RateLimitError as e:
                logger.warning(f"Rate limit hit on key {self.current_key_index + 1}: {e}")
                
                # Try to switch to another key
                if self._handle_rate_limit_error(e, estimated_tokens):
                    current_key_id = self.api_key_ids[self.current_key_index]
                    continue  # Retry with new key
                else:
                    # No keys available
                    raise LLMProviderError(
                        f"All Groq API keys have hit rate limits: {e}",
                        provider="groq",
                        original_exception=e
                    )
                    
            except Exception as e:
                logger.error(f"Groq generation error: {e}", exc_info=True)
                raise LLMProviderError(
                    f"Groq API error during generation: {e}",
                    provider="groq",
                    original_exception=e
                )
        
        raise LLMProviderError("Failed to generate after trying all API keys", provider="groq")
    
    def generate_chat(self, messages: List[Dict[str, str]], model: str = None,
                     max_tokens: int = None, temperature: float = None, **kwargs) -> str:
        """
        Generate chat completion with automatic key rotation.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        # Convert messages to prompt for token estimation
        prompt = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
        return self.generate(prompt, model, max_tokens, temperature, **kwargs)
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary for all API keys."""
        return self.quota_tracker.get_usage_summary(provider="groq")


