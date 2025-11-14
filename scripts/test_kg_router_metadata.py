#!/usr/bin/env python3
"""
Test script to verify KG-First Router metadata extraction.
FIXED: Metadata is merged directly into reflection, not nested under 'metadata' key.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Three_PointO_ArchE.llm_tool import generate_text_llm

test_queries = [
    ('What is Cognitive Resonance?', 'CognitivE'),
    ('What is IAR?', 'IaR'),
    ('Explain Sparse Priming Representations', 'RI'),
    ('What is the Workflow Engine?', 'WorkflowEnginE')
]

print('🧪 KG-First Router Metadata Test (FIXED)')
print('=' * 70)

for query, expected_spr in test_queries:
    print(f'\n📝 Query: {query}')
    print('-' * 70)
    
    result = generate_text_llm({'prompt': query, 'provider': 'groq'})
    
    if 'error' not in result:
        response = result['result']['response_text']
        reflection = result.get('reflection', {})
        
        # FIXED: Metadata is merged directly into reflection, not nested
        # Access confidence, spr_id, etc. directly from reflection
        spr_id = reflection.get('spr_id', 'unknown')
        confidence = reflection.get('confidence', 0.0)
        source = reflection.get('source', 'unknown')
        execution_mode = reflection.get('execution_mode', 'unknown')
        
        # Check if KG hit (look for footer or source field)
        if 'Source: Knowledge Graph' in response or source == 'knowledge_graph':
            print(f'✅ KG HIT!')
            print(f'   SPR: {spr_id} (expected: {expected_spr})')
            print(f'   Confidence: {confidence:.2f}')
            print(f'   Source: {source}')
            print(f'   Autonomous: {reflection.get("autonomous", False)}')
            print(f'   LLM Bypassed: {reflection.get("llm_bypassed", False)}')
            print(f'   Response length: {len(response)} chars')
            print(f'   Preview: {response[:150]}...')
        else:
            print(f'⚠️  Not a KG response')
            print(f'   Source: {source}')
            print(f'   Execution Mode: {execution_mode}')
            print(f'   Confidence: {confidence:.2f}')
            print(f'   Preview: {response[:150]}...')
    else:
        print(f'❌ Error: {result["error"]}')

print('\n' + '=' * 70)
print('✅ Metadata Test Complete!')
print('\n📊 Summary:')
print('   - Metadata fields (confidence, spr_id, source) are at top level of reflection')
print('   - Access directly: reflection.get("confidence"), not reflection.get("metadata", {}).get("confidence")')


