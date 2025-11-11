#!/usr/bin/env python3
"""
Test using Groq API Key 2 specifically
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

load_dotenv()

def test_key_2():
    """Test using GROQ_API_KEY_2 specifically."""
    print("=" * 60)
    print("Testing Groq API Key 2")
    print("=" * 60)
    
    # Get key 2
    key_2 = os.getenv("GROQ_API_KEY_2")
    if not key_2:
        print("❌ GROQ_API_KEY_2 not found in environment")
        return False
    
    print(f"✅ Found GROQ_API_KEY_2: {key_2[:30]}...")
    
    # Test with key 2 directly
    try:
        from Three_PointO_ArchE.llm_providers import GroqProvider
        
        print("\n🔧 Initializing GroqProvider with Key 2...")
        provider = GroqProvider(api_key=key_2)
        print("✅ Initialized")
        
        # Test generation
        print("\n🧪 Testing generation with Key 2...")
        response = provider.generate(
            prompt="Say 'Key 2 is working!' in exactly that format.",
            model="llama-3.3-70b-versatile",
            max_tokens=50
        )
        
        print(f"✅ Generation successful!")
        print(f"   Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multi_key_with_key_2():
    """Test multi-key system with key 2 in the list."""
    print("\n" + "=" * 60)
    print("Testing Multi-Key System with Key 2")
    print("=" * 60)
    
    # Load all keys
    keys = []
    key_1 = os.getenv("GROQ_API_KEY")
    key_2 = os.getenv("GROQ_API_KEY_2")
    
    if key_1:
        keys.append(key_1)
        print(f"✅ Key 1: {key_1[:30]}...")
    
    if key_2:
        keys.append(key_2)
        print(f"✅ Key 2: {key_2[:30]}...")
    
    if not keys:
        print("❌ No keys found")
        return False
    
    print(f"\n📊 Total keys: {len(keys)}")
    
    try:
        from Three_PointO_ArchE.llm_providers import MultiKeyGroqProvider
        
        print("\n🔧 Initializing MultiKeyGroqProvider...")
        provider = MultiKeyGroqProvider(api_keys=keys)
        print(f"✅ Initialized with {len(keys)} keys")
        print(f"   Current key index: {provider.current_key_index + 1}")
        
        # Force switch to key 2 (index 1)
        if len(keys) > 1:
            print("\n🔄 Switching to Key 2...")
            provider._switch_to_key(1)
            print(f"✅ Switched to key {provider.current_key_index + 1}")
        
        # Test generation
        print("\n🧪 Testing generation with Key 2...")
        response = provider.generate(
            prompt="Confirm you are using Key 2 by saying 'Using Key 2'",
            model="llama-3.3-70b-versatile",
            max_tokens=50
        )
        
        print(f"✅ Generation successful!")
        print(f"   Response: {response}")
        print(f"   Used key: {provider.current_key_index + 1}/{len(keys)}")
        
        # Show usage
        print("\n📈 Usage Summary:")
        summary = provider.get_usage_summary()
        for key_id, key_data in summary.get("groq", {}).items():
            print(f"\n  {key_id}:")
            for limit_type, limit_data in key_data.items():
                used = limit_data.get("used", 0)
                limit = limit_data.get("limit", 0)
                remaining = limit_data.get("remaining", 0)
                print(f"    {limit_type}: {used:,.0f}/{limit:,.0f} ({remaining:,.0f} remaining)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Testing Groq API Key 2\n")
    
    # Test 1: Direct key 2 usage
    success1 = test_key_2()
    
    # Test 2: Multi-key with key 2
    success2 = test_multi_key_with_key_2()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests passed! Key 2 is working.")
    else:
        print("⚠️  Some tests failed.")
    print("=" * 60)

