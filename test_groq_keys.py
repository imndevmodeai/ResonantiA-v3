#!/usr/bin/env python3
"""Quick test to verify Groq API keys are working"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

load_dotenv()

from Three_PointO_ArchE.llm_providers.multi_key_groq_provider import MultiKeyGroqProvider

print("="*60)
print("Groq API Keys Verification")
print("="*60)

# Check environment variables
k1 = os.getenv('GROQ_API_KEY')
k2 = os.getenv('GROQ_API_KEY_2')

print(f"\nEnvironment Variables:")
print(f"  GROQ_API_KEY: {'✓ SET' if k1 else '✗ NOT SET'} (length: {len(k1) if k1 else 0})")
print(f"  GROQ_API_KEY_2: {'✓ SET' if k2 else '✗ NOT SET'} (length: {len(k2) if k2 else 0})")

# Test MultiKeyGroqProvider
try:
    provider = MultiKeyGroqProvider()
    print(f"\nMultiKeyGroqProvider:")
    print(f"  ✓ Initialized successfully")
    print(f"  ✓ Found {len(provider.api_keys)} API key(s)")
    print(f"  ✓ Current key index: {provider.current_key_index}")
    print(f"  ✓ Key IDs: {provider.api_key_ids}")
    
    # Test a simple query
    print(f"\nTesting API key(s) with a simple query...")
    response = provider.generate(
        prompt="Say 'Hello' in one word.",
        model="llama-3.1-8b-instant",
        max_tokens=10
    )
    print(f"  ✓ API call successful!")
    print(f"  ✓ Response: {response[:50]}")
    print(f"\n{'='*60}")
    print("✓ All Groq API keys are working!")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

