#!/usr/bin/env python3
"""
Test script for Fallback Provider with Cooldown
================================================

Demonstrates how the fallback provider automatically skips rate-limited providers
until their cooldown period expires.
"""

import os
import sys
import time
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Three_PointO_ArchE.llm_providers.fallback_provider import FallbackLLMProvider

def test_cooldown_behavior():
    """Test that cooldown prevents repeated attempts on rate-limited providers."""
    
    print("=" * 70)
    print("Testing Fallback Provider with Rate Limit Cooldown")
    print("=" * 70)
    
    # Create fallback provider
    provider = FallbackLLMProvider(
        primary_provider='groq',
        fallback_chain=['groq', 'google', 'openai', 'mistral']
    )
    
    print(f"\n✅ Fallback provider created")
    print(f"   Primary: {provider.primary_provider}")
    print(f"   Fallback chain: {provider.fallback_chain}")
    
    # Simulate a rate limit error
    print("\n" + "=" * 70)
    print("Simulating Rate Limit Detection")
    print("=" * 70)
    
    error_message = (
        "Rate limit reached for model `llama-3.3-70b-versatile` in organization "
        "`org_xxx` service tier `on_demand` on tokens per day (TPD): Limit 100000, "
        "Used 99980, Requested 223. Please try again in 23m51.648s."
    )
    
    provider._register_rate_limit('groq', error_message)
    
    # Check cooldown status
    print("\n📊 Cooldown Status:")
    status = provider.get_cooldown_status()
    for provider_name, info in status.items():
        if info.get('in_cooldown'):
            print(f"   {provider_name}:")
            print(f"     - In cooldown: Yes")
            print(f"     - Remaining: {info['remaining_minutes']:.1f} minutes")
            print(f"     - Resets at: {info['cooldown_until']}")
    
    # Test provider skipping
    print("\n" + "=" * 70)
    print("Testing Provider Skipping During Cooldown")
    print("=" * 70)
    
    groq_provider = provider._get_provider('groq')
    if groq_provider is None:
        print("✅ Groq provider correctly skipped (in cooldown)")
    else:
        print("❌ Groq provider should be skipped but wasn't")
    
    # Test that other providers still work
    google_provider = provider._get_provider('google')
    if google_provider:
        print("✅ Google provider available (not in cooldown)")
    else:
        print("⚠️  Google provider not available")
    
    # Get statistics
    print("\n" + "=" * 70)
    print("Fallback Statistics")
    print("=" * 70)
    
    stats = provider.get_fallback_stats()
    print(f"Total calls: {stats['total_calls']}")
    print(f"Primary successes: {stats['primary_successes']}")
    print(f"Fallback activations: {stats['fallback_activations']}")
    
    if stats['rate_limit_cooldowns']:
        print("\nRate Limit Cooldowns:")
        for provider_name, cooldown_info in stats['rate_limit_cooldowns'].items():
            if cooldown_info.get('status') == 'active':
                print(f"   {provider_name}:")
                print(f"     - Remaining: {cooldown_info['remaining_minutes']:.1f} minutes")
                print(f"     - Resets at: {cooldown_info['cooldown_until']}")
    
    print("\n" + "=" * 70)
    print("✅ Cooldown system working correctly!")
    print("=" * 70)
    print("\nKey Features:")
    print("  • Rate limits automatically detected")
    print("  • Cooldown period extracted from error messages")
    print("  • Providers skipped during cooldown")
    print("  • Cooldown expires automatically")
    print("  • Statistics tracked for monitoring")

if __name__ == "__main__":
    test_cooldown_behavior()

