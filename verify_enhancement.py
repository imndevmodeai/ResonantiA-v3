#!/usr/bin/env python3
"""Quick verification script for Russian Doll enhancement"""

import json

with open('knowledge_graph/spr_definitions_tv.json', 'r') as f:
    sprs = json.load(f)

sample = sprs[0]
stages = sample.get('compression_stages', [])
stage_names = [s.get('stage_name') for s in stages]

print(f"Compression stages: {stage_names}")
print(f"Total stages: {len(stages)}")

narrative = next((s for s in stages if s.get('stage_name') == 'Narrative'), None)
print(f"\nHas Narrative layer: {narrative is not None}")

if narrative:
    content = narrative.get('content', '')
    print(f"Narrative content length: {len(content)} chars")
    print(f"Narrative preview: {content[:150]}...")

# Check symbol codex enhancement
codex = sample.get('symbol_codex', {})
if codex:
    sample_symbol = list(codex.values())[0]
    print(f"\nSymbol codex sample:")
    print(f"  Has original_patterns: {'original_patterns' in sample_symbol}")
    print(f"  Has critical_specifics: {'critical_specifics' in sample_symbol}")
    if 'original_patterns' in sample_symbol:
        patterns = sample_symbol.get('original_patterns', [])
        print(f"  Original patterns count: {len(patterns)}")
        if patterns:
            print(f"  Sample pattern: {patterns[0]}")



