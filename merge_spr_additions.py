#!/usr/bin/env python3
"""
Merge SPR additions into the main knowledge graph.
Ensures no duplicates and maintains proper JSON structure.
"""

import json
from pathlib import Path

def merge_sprs():
    """Merge new SPR definitions into main knowledge graph."""
    
    # Paths
    main_kg = Path("knowledge_graph/spr_definitions_tv.json")
    additions = Path("knowledge_graph/spr_workflow_optimization_additions.json")
    backup = Path("knowledge_graph/spr_definitions_tv.json.backup")
    
    # Load existing SPRs
    print(f"📖 Loading existing knowledge graph: {main_kg}")
    with open(main_kg, 'r') as f:
        existing_sprs = json.load(f)
    
    print(f"   Found {len(existing_sprs)} existing SPRs")
    
    # Create backup
    print(f"💾 Creating backup: {backup}")
    with open(backup, 'w') as f:
        json.dump(existing_sprs, f, indent=2)
    
    # Load additions
    print(f"📥 Loading SPR additions: {additions}")
    with open(additions, 'r') as f:
        new_sprs = json.load(f)
    
    print(f"   Found {len(new_sprs)} new SPRs to add")
    
    # Get existing SPR IDs
    existing_ids = {spr['spr_id'] for spr in existing_sprs}
    
    # Add new SPRs (skip duplicates)
    added_count = 0
    skipped_count = 0
    
    for new_spr in new_sprs:
        spr_id = new_spr['spr_id']
        if spr_id in existing_ids:
            print(f"   ⚠️  Skipping duplicate: {spr_id}")
            skipped_count += 1
        else:
            print(f"   ✅ Adding: {spr_id}")
            existing_sprs.append(new_spr)
            existing_ids.add(spr_id)
            added_count += 1
    
    # Write merged SPRs
    print(f"\n💾 Writing merged knowledge graph...")
    with open(main_kg, 'w') as f:
        json.dump(existing_sprs, f, indent=2)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ SPR Knowledge Graph Update Complete!")
    print(f"{'='*60}")
    print(f"Original SPR count:  {len(existing_sprs) - added_count}")
    print(f"New SPRs added:      {added_count}")
    print(f"Duplicates skipped:  {skipped_count}")
    print(f"Final SPR count:     {len(existing_sprs)}")
    print(f"Backup saved to:     {backup}")
    print(f"{'='*60}")
    
    # List added SPRs
    if added_count > 0:
        print(f"\n📝 New SPRs added to Knowledge Tapestry:")
        for new_spr in new_sprs:
            if new_spr['spr_id'] not in existing_ids or new_spr in existing_sprs[-added_count:]:
                print(f"   • {new_spr['spr_id']}: {new_spr['term']}")

if __name__ == "__main__":
    merge_sprs()

