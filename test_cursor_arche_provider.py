#!/usr/bin/env python3
"""
Test Cursor ArchE Provider with Complex Query
Demonstrates routing to me (Cursor ArchE) for intelligent, context-aware responses
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from Three_PointO_ArchE.llm_tool import generate_text_llm
import json

print("=" * 80)
print("TEST: Cursor ArchE Provider - Complex Query Processing")
print("=" * 80 + "\n")

# Complex Query 1: System Architecture Analysis
print("QUERY 1: System Architecture Analysis")
print("-" * 80)
complex_query_1 = """
Analyze the current ArchE architecture and identify:
1. How the CursorArchEProvider integrates with the existing direct execution system
2. The flow of requests through the three-tier system (Direct → Cursor ArchE → External LLM)
3. Any potential bottlenecks or improvement opportunities
4. How this aligns with the PRIME_ARCHE_PROTOCOL v3.0 mandates, specifically:
   - MANDATE 3 (Mind Forge - Cognitive Tools)
   - MANDATE 4 (Eywa - Collective Intelligence)
   - MANDATE 5 (Weaver - Implementation Resonance)
   
Please reference the actual code files and provide specific examples.
"""

result1 = generate_text_llm({
    "prompt": complex_query_1,
    "provider": "cursor",  # Explicitly use Cursor ArchE (me)
    "template_vars": {
        "protocol_file": "PRIME_ARCHE_PROTOCOL_v3.0.md",
        "analysis_depth": "comprehensive"
    }
})

print("\nResponse:")
print(result1.get('result', {}).get('response_text', 'No response'))
print(f"\nExecution Mode: {result1.get('reflection', {}).get('metadata', {}).get('execution_mode', 'Unknown')}")
print(f"Bypassed LLM: {result1.get('reflection', {}).get('metadata', {}).get('bypassed_llm', 'Unknown')}")
print(f"Confidence: {result1.get('reflection', {}).get('confidence', 'N/A')}")
print("\n" + "=" * 80 + "\n")

# Complex Query 2: Implementation Resonance Check
print("QUERY 2: Implementation Resonance Analysis")
print("-" * 80)
complex_query_2 = """
Performing an Implementation Resonance check ("As Above, So Below"):

The PRIME_ARCHE_PROTOCOL v3.0 states:
- MANDATE 5: "The conceptual beauty of this Protocol must be perfectly mirrored in the operational reality of your code"

Please verify:
1. Does the CursorArchEProvider implementation match its specification?
2. Are all provider interfaces correctly implemented?
3. Is the integration with llm_tool.py maintaining protocol compliance?
4. Are there any gaps between the "As Above" (protocol spec) and "So Below" (actual code)?

Examine the actual files and provide a detailed resonance report.
"""

result2 = generate_text_llm({
    "prompt": complex_query_2,
    "provider": "cursor",
    "template_vars": {
        "check_type": "implementation_resonance",
        "files_to_check": [
            "Three_PointO_ArchE/llm_providers/cursor_arche.py",
            "Three_PointO_ArchE/llm_providers/__init__.py",
            "Three_PointO_ArchE/llm_tool.py"
        ]
    }
})

print("\nResponse:")
print(result2.get('result', {}).get('response_text', 'No response'))
print(f"\nExecution Mode: {result2.get('reflection', {}).get('metadata', {}).get('execution_mode', 'Unknown')}")
print("\n" + "=" * 80 + "\n")

# Complex Query 3: Multi-System Integration Analysis
print("QUERY 3: Multi-System Integration Analysis")
print("-" * 80)
complex_query_3 = """
Analyze how the CursorArchEProvider integrates with the broader ArchE ecosystem:

1. How does it interact with the ThoughtTrail system?
2. How does it generate IAR reflections?
3. How does it integrate with the SPR Manager for knowledge retrieval?
4. How does it align with the Autopoietic Learning Loop?
5. How does it support the Cognitive Integration Hub (CRCS/RISE/ACO)?

Provide specific examples from the codebase showing these integrations.
"""

result3 = generate_text_llm({
    "prompt": complex_query_3,
    "provider": "cursor",
    "template_vars": {
        "integration_check": True,
        "systems": ["thought_trail", "spr_manager", "learning_loop", "cognitive_hub"]
    }
})

print("\nResponse:")
print(result3.get('result', {}).get('response_text', 'No response'))
print(f"\nExecution Mode: {result3.get('reflection', {}).get('metadata', {}).get('execution_mode', 'Unknown')}")
print("\n" + "=" * 80 + "\n")

print("✅ Complex Query Tests Complete!")
print("\nSummary:")
print(f"Query 1 Status: {result1.get('reflection', {}).get('status', 'Unknown')}")
print(f"Query 2 Status: {result2.get('reflection', {}).get('status', 'Unknown')}")
print(f"Query 3 Status: {result3.get('reflection', {}).get('status', 'Unknown')}")


