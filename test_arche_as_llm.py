#!/usr/bin/env python3
"""
Test ArchE replacing LLM calls
Demonstrates that ArchE can now execute analysis directly instead of calling external LLMs
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from Three_PointO_ArchE.llm_tool import generate_text_llm

print("=" * 80)
print("TEST: ArchE as LLM Replacement")
print("=" * 80 + "\n")

# Test Case 1: CFP Analysis Request
print("TEST 1: Requesting CFP comparison analysis...")
result1 = generate_text_llm({
    "prompt": "Compare these two systems using quantum flux: System A=[0.6, 0.4] and System B=[0.5, 0.5]",
    "template_vars": {
        "system_a": {"quantum_state": [0.6, 0.4]},
        "system_b": {"quantum_state": [0.5, 0.5]}
    }
})

print("Result:")
print(result1.get('result', {}).get('response_text', 'No response'))
print(f"\nStatus: {result1.get('reflection', {}).get('status', 'Unknown')}")
print(f"Direct execution: {result1.get('reflection', {}).get('execution_mode', 'N/A')}")
print("\n" + "=" * 80 + "\n")

# Test Case 2: ABM Simulation Request
print("TEST 2: Requesting ABM simulation analysis...")
result2 = generate_text_llm({
    "prompt": "Simulate agent-based market dynamics",
    "template_vars": {
        "agent_count": 100,
        "environment": {"market_size": 1000},
        "steps": 50
    }
})

print("Result:")
print(result2.get('result', {}).get('response_text', 'No response')[:200] + "...")
print(f"\nStatus: {result2.get('reflection', {}).get('status', 'Unknown')}")
print("\n" + "=" * 80 + "\n")

# Test Case 3: Non-analysis request (should fall back to LLM)
print("TEST 3: Non-analysis request (should use LLM)...")
result3 = generate_text_llm({
    "prompt": "Write a poem about quantum computing",
    "template_vars": {}
})

print("Status:")
print(f"Mode: {result3.get('reflection', {}).get('execution_mode', 'LLM')}")
print(f"Bypassed: {result3.get('reflection', {}).get('bypassed_llm', False)}")
print("\n✅ Tests complete!")

