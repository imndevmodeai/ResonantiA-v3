#!/usr/bin/env python3
"""
Test script for multi-key Groq provider
Tests that the system can use multiple Groq API keys with automatic rotation
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_multi_key_groq():
    """Test multi-key Groq provider."""
    print("=" * 60)
    print("Multi-Key Groq Provider Test")
    print("=" * 60)
    
    # Check available keys
    keys = []
    primary = os.getenv("GROQ_API_KEY")
    if primary:
        keys.append(primary)
        print(f"✅ Found GROQ_API_KEY (Key 1)")
    
    i = 1
    while True:
        key = os.getenv(f"GROQ_API_KEY_{i}")
        if not key:
            break
        if key not in keys:
            keys.append(key)
            print(f"✅ Found GROQ_API_KEY_{i} (Key {len(keys)})")
        i += 1
    
    if not keys:
        print("❌ No Groq API keys found!")
        print("\nPlease add to .env file:")
        print("GROQ_API_KEY=your_key_here")
        print("GROQ_API_KEY_1=your_second_key_here")
        return False
    
    print(f"\n📊 Total keys found: {len(keys)}")
    
    # Test multi-key provider
    try:
        from Three_PointO_ArchE.llm_providers import MultiKeyGroqProvider
        
        print("\n🔧 Initializing MultiKeyGroqProvider...")
        provider = MultiKeyGroqProvider(api_keys=keys)
        print(f"✅ Initialized with {len(keys)} keys")
        
        # Get usage summary
        print("\n📈 Current Usage Summary:")
        summary = provider.get_usage_summary()
        for key_id, key_data in summary.get("groq", {}).items():
            print(f"\n  {key_id}:")
            for limit_type, limit_data in key_data.items():
                used = limit_data.get("used", 0)
                limit = limit_data.get("limit", 0)
                remaining = limit_data.get("remaining", 0)
                percent = limit_data.get("usage_percent", 0)
                available = limit_data.get("available", True)
                status = "✅ Available" if available else "❌ Exhausted"
                print(f"    {limit_type}:")
                print(f"      Used: {used:,.0f} / {limit:,.0f} ({percent:.1f}%)")
                print(f"      Remaining: {remaining:,.0f}")
                print(f"      Status: {status}")
        
        # Test generation with current key
        print("\n🧪 Testing generation...")
        print(f"   Current key: {provider.current_key_index + 1}/{len(keys)}")
        
        response = provider.generate(
            prompt="Say hello in exactly 5 words.",
            model="llama-3.3-70b-versatile",
            max_tokens=50
        )
        
        print(f"✅ Generation successful!")
        print(f"   Response: {response}")
        print(f"   Used key: {provider.current_key_index + 1}/{len(keys)}")
        
        # Show updated usage
        print("\n📈 Updated Usage Summary:")
        summary = provider.get_usage_summary()
        for key_id, key_data in summary.get("groq", {}).items():
            for limit_type, limit_data in key_data.items():
                used = limit_data.get("used", 0)
                limit = limit_data.get("limit", 0)
                remaining = limit_data.get("remaining", 0)
                percent = limit_data.get("usage_percent", 0)
                print(f"  {key_id} - {limit_type}: {used:,.0f}/{limit:,.0f} ({percent:.1f}%) - {remaining:,.0f} remaining")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_intelligent_orchestrator():
    """Test intelligent orchestrator with multi-key support."""
    print("\n" + "=" * 60)
    print("Intelligent Orchestrator Test")
    print("=" * 60)
    
    try:
        from Three_PointO_ArchE.llm_providers import get_llm_provider
        
        print("\n🔧 Initializing Intelligent Orchestrator...")
        orchestrator = get_llm_provider("intelligent")
        print("✅ Initialized")
        
        # Get stats
        print("\n📊 Initial Stats:")
        stats = orchestrator.get_stats()
        print(f"   Available providers: {stats.get('available_providers', [])}")
        print(f"   Current provider: {stats.get('current_provider', 'None')}")
        
        # Test generation
        print("\n🧪 Testing generation...")
        response = orchestrator.generate(
            prompt="Count to 3 in words.",
            max_tokens=20
        )
        
        print(f"✅ Generation successful!")
        print(f"   Response: {response}")
        
        # Get updated stats
        print("\n📊 Updated Stats:")
        stats = orchestrator.get_stats()
        print(f"   Total calls: {stats.get('total_calls', 0)}")
        print(f"   Provider calls: {stats.get('provider_calls', {})}")
        print(f"   Fallbacks: {stats.get('fallbacks', 0)}")
        print(f"   Errors: {stats.get('errors', 0)}")
        print(f"   Current provider: {stats.get('current_provider', 'None')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Starting Multi-Key Groq Tests\n")
    
    # Test 1: Multi-key provider
    success1 = test_multi_key_groq()
    
    # Test 2: Intelligent orchestrator
    success2 = test_intelligent_orchestrator()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed. Check output above.")
    print("=" * 60)

