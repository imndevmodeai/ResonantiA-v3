#!/usr/bin/env python3
"""
Test ArchE answering ALL requests (not just analysis)
This verifies ArchE can replace LLM for ALL types of queries
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from Three_PointO_ArchE.llm_tool import generate_text_llm
import json

print("=" * 80)
print("TEST: ArchE Replacing LLM for ALL Requests")
print("=" * 80 + "\n")

# Test 1: YouTube Scraper Query
print("TEST 1: YouTube Scraper Cleanup Query...")
result1 = generate_text_llm({
    "prompt": "Tell me about the YouTube scraper browser cleanup",
    "template_vars": {}
})

print("Response:")
print(result1.get('result', {}).get('response_text', 'No response')[:500])
print(f"\nMode: {result1.get('reflection', {}).get('execution_mode', 'Unknown')}")
print(f"Bypassed LLM: {result1.get('reflection', {}).get('bypassed_llm', False)}")
print("\n" + "=" * 80 + "\n")

# Test 2: Quantum Computing Breakthrough Query
print("TEST 2: Quantum Computing Breakthrough Query...")
result2 = generate_text_llm({
    "prompt": "What happened with the quantum computing analysis?",
    "template_vars": {}
})

print("Response:")
print(result2.get('result', {}).get('response_text', 'No response')[:500])
print(f"\nMode: {result2.get('reflection', {}).get('execution_mode', 'Unknown')}")
print(f"Bypassed LLM: {result2.get('reflection', {}).get('bypassed_llm', False)}")
print("\n" + "=" * 80 + "\n")

# Test 3: System Status Query
print("TEST 3: System Status Query...")
result3 = generate_text_llm({
    "prompt": "What's the current system status?",
    "template_vars": {}
})

print("Response:")
print(result3.get('result', {}).get('response_text', 'No response')[:500])
print(f"\nMode: {result3.get('reflection', {}).get('execution_mode', 'Unknown')}")
print(f"Bypassed LLM: {result3.get('reflection', {}).get('bypassed_llm', False)}")
print("\n" + "=" * 80 + "\n")

# Test 4: General Query
print("TEST 4: General Query (should still work)...")
result4 = generate_text_llm({
    "prompt": "Explain how CFP works with quantum operations",
    "template_vars": {}
})

print("Response:")
print(result4.get('result', {}).get('response_text', 'No response')[:300])
print(f"\nMode: {result4.get('reflection', {}).get('execution_mode', 'Unknown')}")
print("✅ All tests complete!")
print("=" * 80)

