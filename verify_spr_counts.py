#!/usr/bin/env python3
"""Script to verify SPR counts in spr_definitions_tv.json"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_spr_file(file_path):
    """Analyze SPR definitions file and return metrics"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_sprs = len(data)
    categories = set()
    rel_types = set()
    rel_count = 0
    
    for spr in data:
        # Count categories
        if 'category' in spr:
            categories.add(spr['category'])
        
        # Count relationships
        if 'relationships' in spr and isinstance(spr['relationships'], dict):
            rel_types.update(spr['relationships'].keys())
            # Count actual relationship entries (not just keys)
            for key, value in spr['relationships'].items():
                if isinstance(value, list):
                    rel_count += len(value)
                elif isinstance(value, str):
                    rel_count += 1
                elif isinstance(value, dict):
                    rel_count += len(value)
    
    return {
        'total_sprs': total_sprs,
        'categories': len(categories),
        'category_list': sorted(categories),
        'relationship_types': len(rel_types),
        'relationship_type_list': sorted(rel_types),
        'total_relationship_entries': rel_count
    }

if __name__ == '__main__':
    spr_file = Path('knowledge_graph/spr_definitions_tv.json')
    
    if not spr_file.exists():
        print(f"ERROR: File not found: {spr_file}")
        exit(1)
    
    metrics = analyze_spr_file(spr_file)
    
    print("=" * 60)
    print("SPR DEFINITIONS ANALYSIS")
    print("=" * 60)
    print(f"Total SPR objects: {metrics['total_sprs']}")
    print(f"Unique categories: {metrics['categories']}")
    print(f"Relationship types found: {metrics['relationship_types']}")
    print(f"Total relationship entries: {metrics['total_relationship_entries']}")
    print("\nCategories:")
    for cat in metrics['category_list']:
        print(f"  - {cat}")
    print("\nRelationship Types:")
    for rel_type in metrics['relationship_type_list']:
        print(f"  - {rel_type}")

