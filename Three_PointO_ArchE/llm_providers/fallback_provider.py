#!/usr/bin/env python3
"""
Fallback LLM Provider with Cascading Loopback
==============================================

Automatically tries multiple LLM providers in sequence when one fails.
Implements a robust loopback mechanism that cascades through fallback providers.

Example:
    Primary: Groq (fails with rate limit)
    → Fallback 1: Google (fails with API error)
    → Fallback 2: OpenAI (succeeds)
"""

import logging
import re
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from .base import BaseLLMProvider, LLMProviderError
from . import get_llm_provider, get_model_for_provider

logger = logging.getLogger(__name__)


class FallbackLLMProvider(BaseLLMProvider):
    """
    LLM Provider with automatic cascading fallback.
    
    When a provider call fails, automatically tries the next provider in the chain.
    Continues until one succeeds or all providers are exhausted.
    """
    
    # Default fallback chain (in order of preference)
    # After both Groq keys are exhausted, fallback to Cursor, then other providers
    DEFAULT_FALLBACK_CHAIN = ['groq', 'cursor', 'google', 'openai', 'mistral']
    
    def __init__(
        self,
        primary_provider: str = 'groq',
        fallback_chain: Optional[List[str]] = None,
        api_keys: Optional[Dict[str, str]] = None,
        enable_zepto: bool = False,
        **kwargs
    ):
        """
        Initialize fallback provider with cascading loopback.
        
        Args:
            primary_provider: Primary provider to use first
            fallback_chain: List of provider names to try in order (default: groq, google, openai, mistral, cursor)
            api_keys: Optional dict of provider_name -> api_key (otherwise uses config/env)
            enable_zepto: Whether to use Zepto compression (requires zepto_llm_wrapper)
            **kwargs: Additional arguments passed to providers
        """
        # Store configuration
        self.primary_provider = primary_provider.lower()
        self.fallback_chain = fallback_chain or self.DEFAULT_FALLBACK_CHAIN.copy()
        
        # Ensure primary is first in chain
        if self.primary_provider not in self.fallback_chain:
            self.fallback_chain.insert(0, self.primary_provider)
        else:
            # Move primary to front
            self.fallback_chain.remove(self.primary_provider)
            self.fallback_chain.insert(0, self.primary_provider)
        
        self.api_keys = api_keys or {}
        self.enable_zepto = enable_zepto
        self.provider_kwargs = kwargs
        
        # Initialize providers lazily (only when needed)
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._zepto_wrappers: Dict[str, Any] = {}
        
        # Track fallback usage
        self.fallback_stats = {
            'total_calls': 0,
            'primary_successes': 0,
            'fallback_activations': 0,
            'fallback_successes': 0,
            'total_failures': 0,
            'provider_usage': {},  # provider_name -> count
            'fallback_chains': []  # List of chains used
        }
        
        # Rate limit tracking (circuit breaker pattern)
        self.rate_limit_cooldowns: Dict[str, datetime] = {}  # provider_name -> cooldown_until
        self.rate_limit_detections: Dict[str, Dict[str, Any]] = {}  # provider_name -> detection_info
        
        # Initialize base class with dummy API key (we'll use actual providers)
        super().__init__(api_key="fallback_provider", **kwargs)
        self._provider_name = "fallback"
    
    def _initialize_client(self):
        """Not used - we initialize providers lazily."""
        return None
    
    def _is_provider_in_cooldown(self, provider_name: str) -> Tuple[bool, Optional[datetime]]:
        """
        Check if provider is in rate limit cooldown period.
        
        Returns:
            (is_in_cooldown, cooldown_until)
        """
        provider_name_lower = provider_name.lower()
        
        if provider_name_lower not in self.rate_limit_cooldowns:
            return False, None
        
        cooldown_until = self.rate_limit_cooldowns[provider_name_lower]
        now = datetime.now()
        
        if now < cooldown_until:
            # Still in cooldown
            remaining = (cooldown_until - now).total_seconds()
            return True, cooldown_until
        
        # Cooldown expired, remove it
        del self.rate_limit_cooldowns[provider_name_lower]
        if provider_name_lower in self.rate_limit_detections:
            del self.rate_limit_detections[provider_name_lower]
        logger.info(f"✅ Cooldown expired for {provider_name_lower}, provider available again")
        return False, None
    
    def _extract_rate_limit_reset_time(self, error_message: str) -> Optional[datetime]:
        """
        Extract rate limit reset time from error message.
        
        Examples:
        - "Please try again in 3m2.304s"
        - "Please try again in 23m51.648s"
        - "Rate limit resets at 2025-11-21 03:00:00"
        """
        # Pattern 1: "Please try again in XmYs" or "in Xs"
        time_pattern = r'Please try again in (?:(\d+)m)?(?:(\d+\.?\d*)s)?'
        match = re.search(time_pattern, error_message, re.IGNORECASE)
        if match:
            minutes = int(match.group(1) or 0)
            seconds = float(match.group(2) or 0)
            total_seconds = minutes * 60 + seconds
            reset_time = datetime.now() + timedelta(seconds=total_seconds)
            return reset_time
        
        # Pattern 2: ISO timestamp or date string
        iso_pattern = r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})'
        match = re.search(iso_pattern, error_message)
        if match:
            try:
                reset_time = datetime.fromisoformat(match.group(1).replace(' ', 'T'))
                return reset_time
            except:
                pass
        
        # Pattern 3: "resets at" or "reset time"
        reset_pattern = r'reset[s]? (?:at|time|in) (.+?)(?:\.|,|$)'
        match = re.search(reset_pattern, error_message, re.IGNORECASE)
        if match:
            # Try to parse various date formats
            reset_str = match.group(1).strip()
            # This would need more sophisticated parsing
        
        # Default: If rate limit detected but no time specified, use 1 hour cooldown
        return datetime.now() + timedelta(hours=1)
    
    def _register_rate_limit(self, provider_name: str, error_message: str):
        """
        Register a rate limit for a provider and set cooldown period.
        """
        provider_name_lower = provider_name.lower()
        
        # Extract reset time from error
        reset_time = self._extract_rate_limit_reset_time(error_message)
        
        if reset_time:
            self.rate_limit_cooldowns[provider_name_lower] = reset_time
            self.rate_limit_detections[provider_name_lower] = {
                'detected_at': datetime.now(),
                'reset_time': reset_time,
                'error_message': error_message,
                'cooldown_duration': (reset_time - datetime.now()).total_seconds()
            }
            
            remaining = (reset_time - datetime.now()).total_seconds()
            logger.warning(
                f"⏸️  Rate limit detected for {provider_name_lower}. "
                f"Cooldown until {reset_time.strftime('%Y-%m-%d %H:%M:%S')} "
                f"({remaining/60:.1f} minutes remaining). "
                f"Provider will be skipped until cooldown expires."
            )
        else:
            # Fallback: 1 hour cooldown if we can't parse the time
            reset_time = datetime.now() + timedelta(hours=1)
            self.rate_limit_cooldowns[provider_name_lower] = reset_time
            self.rate_limit_detections[provider_name_lower] = {
                'detected_at': datetime.now(),
                'reset_time': reset_time,
                'error_message': error_message,
                'cooldown_duration': 3600
            }
            logger.warning(
                f"⏸️  Rate limit detected for {provider_name_lower} (could not parse reset time). "
                f"Using 1-hour cooldown."
            )
    
    def _get_provider(self, provider_name: str) -> Optional[BaseLLMProvider]:
        """
        Get or create a provider instance (lazy initialization).
        
        Returns None if provider is not available or in cooldown.
        """
        provider_name_lower = provider_name.lower()
        
        # Check if provider is in cooldown
        is_cooldown, cooldown_until = self._is_provider_in_cooldown(provider_name_lower)
        if is_cooldown:
            remaining = (cooldown_until - datetime.now()).total_seconds()
            logger.info(
                f"⏭️  Skipping {provider_name_lower} (rate limit cooldown, "
                f"{remaining/60:.1f} minutes remaining)"
            )
            return None
        
        # Return cached provider if available
        if provider_name_lower in self._providers:
            return self._providers[provider_name_lower]
        
        # Try to create provider
        try:
            api_key = self.api_keys.get(provider_name_lower)
            provider = get_llm_provider(provider_name_lower, api_key=api_key)
            
            # Wrap with Zepto if enabled
            if self.enable_zepto:
                try:
                    from .zepto_llm_wrapper import ZeptoLLMWrapper
                    provider = ZeptoLLMWrapper(provider, enable_compression=True)
                    self._zepto_wrappers[provider_name_lower] = provider
                except ImportError:
                    logger.warning(f"Zepto wrapper not available for {provider_name_lower}")
            
            self._providers[provider_name_lower] = provider
            logger.info(f"✅ Initialized fallback provider: {provider_name_lower}")
            return provider
            
        except Exception as e:
            logger.warning(f"⚠️  Provider {provider_name_lower} not available: {e}")
            return None
    
    def _try_provider_chain(
        self,
        method_name: str,
        *args,
        **kwargs
    ) -> Tuple[Optional[str], Optional[str], List[Dict[str, Any]]]:
        """
        Try providers in fallback chain until one succeeds.
        
        Returns:
            (result_text, successful_provider, error_history)
        """
        self.fallback_stats['total_calls'] += 1
        error_history = []
        fallback_chain_used = []
        
        # Try each provider in the chain
        for provider_name in self.fallback_chain:
            provider = self._get_provider(provider_name)
            if not provider:
                error_history.append({
                    'provider': provider_name,
                    'error': 'Provider not available',
                    'error_type': 'UnavailableError'
                })
                continue
            
            fallback_chain_used.append(provider_name)
            
            try:
                logger.info(f"🔄 Trying provider: {provider_name}")
                
                # Call the appropriate method
                if method_name == 'generate':
                    result = provider.generate(*args, **kwargs)
                elif method_name == 'generate_chat':
                    result = provider.generate_chat(*args, **kwargs)
                else:
                    raise ValueError(f"Unknown method: {method_name}")
                
                # Success!
                is_primary = provider_name == self.primary_provider
                if is_primary:
                    self.fallback_stats['primary_successes'] += 1
                else:
                    self.fallback_stats['fallback_activations'] += 1
                    self.fallback_stats['fallback_successes'] += 1
                
                # Track provider usage
                self.fallback_stats['provider_usage'][provider_name] = \
                    self.fallback_stats['provider_usage'].get(provider_name, 0) + 1
                
                # Track fallback chain
                if len(fallback_chain_used) > 1:
                    self.fallback_stats['fallback_chains'].append(fallback_chain_used)
                
                logger.info(f"✅ Provider {provider_name} succeeded")
                return result, provider_name, error_history
                
            except LLMProviderError as e:
                error_info = {
                    'provider': provider_name,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'original_exception': str(e.original_exception) if e.original_exception else None
                }
                error_history.append(error_info)
                
                # Check if this is a rate limit error
                error_str_lower = str(e).lower()
                is_rate_limit = (
                    'rate limit' in error_str_lower or
                    '429' in str(e) or
                    'quota' in error_str_lower or
                    'limit' in error_str_lower or
                    'tokens per day' in error_str_lower or
                    'tpd' in error_str_lower or
                    'all' in error_str_lower and 'keys' in error_str_lower and ('rate limit' in error_str_lower or 'hit' in error_str_lower)  # "All Groq API keys have hit rate limits"
                )
                
                # If rate limit detected, register cooldown
                if is_rate_limit:
                    self._register_rate_limit(provider_name, str(e))
                    logger.warning(f"⚠️  Provider {provider_name} rate limited: {e}")
                    logger.info(f"🔄 Looping back to next provider in chain (will skip {provider_name} until cooldown expires)...")
                    continue  # Try next provider
                
                # Check if this is a temporary error (should try next provider)
                is_temporary = (
                    'timeout' in str(e).lower() or
                    'connection' in str(e).lower() or
                    'network' in str(e).lower() or
                    'temporary' in str(e).lower()
                )
                
                if is_temporary:
                    logger.warning(f"⚠️  Provider {provider_name} failed (temporary): {e}")
                    logger.info(f"🔄 Looping back to next provider in chain...")
                    continue  # Try next provider
                else:
                    # Permanent error (e.g., invalid API key) - skip this provider for this call
                    logger.warning(f"⚠️  Provider {provider_name} failed (permanent): {e}")
                    continue  # Try next provider anyway
                    
            except Exception as e:
                error_info = {
                    'provider': provider_name,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
                error_history.append(error_info)
                logger.warning(f"⚠️  Provider {provider_name} failed with exception: {e}")
                logger.info(f"🔄 Looping back to next provider in chain...")
                continue  # Try next provider
        
        # All providers failed
        self.fallback_stats['total_failures'] += 1
        logger.error(f"❌ All providers in fallback chain failed")
        
        # Build error message
        error_summary = "\n".join([
            f"  {err['provider']}: {err['error_type']} - {err['error']}"
            for err in error_history
        ])
        
        raise LLMProviderError(
            f"All fallback providers exhausted. Errors:\n{error_summary}",
            provider="fallback",
            original_exception=None
        )
    
    def generate(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text with automatic fallback loopback.
        
        Tries primary provider first, then cascades through fallback chain on failure.
        """
        # Use provider-specific model if not specified
        if not model:
            model = get_model_for_provider(self.primary_provider)
        
        result, successful_provider, error_history = self._try_provider_chain(
            'generate',
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        return result
    
    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate chat completion with automatic fallback loopback.
        
        Tries primary provider first, then cascades through fallback chain on failure.
        """
        # Use provider-specific model if not specified
        if not model:
            model = get_model_for_provider(self.primary_provider)
        
        result, successful_provider, error_history = self._try_provider_chain(
            'generate_chat',
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        return result
    
    def get_fallback_stats(self) -> Dict[str, Any]:
        """Get fallback statistics."""
        stats = self.fallback_stats.copy()
        
        # Calculate success rates
        if stats['total_calls'] > 0:
            stats['primary_success_rate'] = stats['primary_successes'] / stats['total_calls']
            stats['fallback_activation_rate'] = stats['fallback_activations'] / stats['total_calls']
            stats['overall_success_rate'] = (
                stats['primary_successes'] + stats['fallback_successes']
            ) / stats['total_calls']
        else:
            stats['primary_success_rate'] = 0.0
            stats['fallback_activation_rate'] = 0.0
            stats['overall_success_rate'] = 0.0
        
        # Add rate limit cooldown information
        stats['rate_limit_cooldowns'] = {}
        now = datetime.now()
        for provider_name, cooldown_until in self.rate_limit_cooldowns.items():
            if now < cooldown_until:
                remaining_seconds = (cooldown_until - now).total_seconds()
                stats['rate_limit_cooldowns'][provider_name] = {
                    'cooldown_until': cooldown_until.isoformat(),
                    'remaining_seconds': remaining_seconds,
                    'remaining_minutes': remaining_seconds / 60,
                    'status': 'active'
                }
            else:
                # Cooldown expired, will be cleaned up on next check
                stats['rate_limit_cooldowns'][provider_name] = {
                    'status': 'expired'
                }
        
        # Add rate limit detection history
        stats['rate_limit_detections'] = {
            provider: {
                'detected_at': info['detected_at'].isoformat(),
                'reset_time': info['reset_time'].isoformat(),
                'cooldown_duration_seconds': info['cooldown_duration']
            }
            for provider, info in self.rate_limit_detections.items()
        }
        
        return stats
    
    def reset_stats(self):
        """Reset fallback statistics."""
        self.fallback_stats = {
            'total_calls': 0,
            'primary_successes': 0,
            'fallback_activations': 0,
            'fallback_successes': 0,
            'total_failures': 0,
            'provider_usage': {},
            'fallback_chains': []
        }
    
    def clear_cooldown(self, provider_name: str = None):
        """
        Clear rate limit cooldown for a specific provider or all providers.
        
        Args:
            provider_name: Provider to clear cooldown for (None = all providers)
        """
        if provider_name:
            provider_name_lower = provider_name.lower()
            if provider_name_lower in self.rate_limit_cooldowns:
                del self.rate_limit_cooldowns[provider_name_lower]
            if provider_name_lower in self.rate_limit_detections:
                del self.rate_limit_detections[provider_name_lower]
            logger.info(f"✅ Cleared cooldown for {provider_name_lower}")
        else:
            self.rate_limit_cooldowns.clear()
            self.rate_limit_detections.clear()
            logger.info("✅ Cleared all rate limit cooldowns")
    
    def get_cooldown_status(self) -> Dict[str, Any]:
        """Get current cooldown status for all providers."""
        now = datetime.now()
        status = {}
        
        for provider_name, cooldown_until in self.rate_limit_cooldowns.items():
            if now < cooldown_until:
                remaining = (cooldown_until - now).total_seconds()
                status[provider_name] = {
                    'in_cooldown': True,
                    'cooldown_until': cooldown_until.isoformat(),
                    'remaining_seconds': remaining,
                    'remaining_minutes': remaining / 60,
                    'remaining_hours': remaining / 3600
                }
            else:
                status[provider_name] = {
                    'in_cooldown': False,
                    'cooldown_expired': True
                }
        
        return status

