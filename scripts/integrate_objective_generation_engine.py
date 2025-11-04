#!/usr/bin/env python3
"""
Integration Script: Objective Generation Engine
Solidifies the Objective generation enginE SPR and specification into ArchE's Knowledge Tapestry.

This script:
1. Adds Objective generation enginE SPR to knowledge_graph/spr_definitions_tv.json
2. Updates related SPRs with cross-references
3. Creates initial implementation structure
4. Validates integration
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "Three_PointO_ArchE"))

def load_spr_definitions() -> List[Dict[str, Any]]:
    """Load current SPR definitions."""
    spr_file = project_root / "knowledge_graph" / "spr_definitions_tv.json"
    if not spr_file.exists():
        raise FileNotFoundError(f"SPR definitions file not found: {spr_file}")
    
    with open(spr_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_spr_definitions(spr_definitions: List[Dict[str, Any]]) -> bool:
    """Save updated SPR definitions."""
    spr_file = project_root / "knowledge_graph" / "spr_definitions_tv.json"
    
    # Create backup
    backup_file = spr_file.with_suffix('.json.backup')
    with open(spr_file, 'r', encoding='utf-8') as f:
        with open(backup_file, 'w', encoding='utf-8') as b:
            b.write(f.read())
    print(f"✓ Created backup: {backup_file}")
    
    # Save updated definitions
    with open(spr_file, 'w', encoding='utf-8') as f:
        json.dump(spr_definitions, f, indent=2, ensure_ascii=False)
    
    return True

def load_objective_generation_engine_spr() -> Dict[str, Any]:
    """Load the Objective generation enginE SPR definition."""
    spr_file = project_root / "outputs" / "objective_generation_engine_spr.json"
    if not spr_file.exists():
        raise FileNotFoundError(f"Objective Generation Engine SPR not found: {spr_file}")
    
    with open(spr_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def spr_exists(spr_definitions: List[Dict[str, Any]], spr_id: str) -> bool:
    """Check if SPR already exists."""
    return any(spr.get('spr_id') == spr_id for spr in spr_definitions)

def update_related_sprs(spr_definitions: List[Dict[str, Any]]) -> int:
    """Update related SPRs to reference ObjectiveGenerationEngine."""
    updates = 0
    
    related_sprs = {
        'Enhancement Skeleton PatterN': {
            'add_to': 'uses',
            'relationship': 'Objective generation enginE'
        },
        'SIRC ProtocoL': {
            'add_to': 'comprises',  # or 'part_of' depending on structure
            'relationship': 'Objective generation enginE'
        },
        'RISE OrchestratoR': {
            'add_to': 'integrates_with',
            'relationship': 'Objective generation enginE'
        }
    }
    
    for spr in spr_definitions:
        spr_id = spr.get('spr_id', '')
        relationships = spr.get('relationships', {})
        
        # Find matching SPR
        for related_spr_key, update_info in related_sprs.items():
            if spr_id == related_spr_key or spr.get('term', '') == related_spr_key:
                target_field = update_info['add_to']
                new_relationship = update_info['relationship']
                
                # Initialize relationships dict if needed
                if not isinstance(relationships, dict):
                    relationships = {}
                    spr['relationships'] = relationships
                
                # Get existing list or create new
                if target_field in relationships:
                    if isinstance(relationships[target_field], list):
                        if new_relationship not in relationships[target_field]:
                            relationships[target_field].append(new_relationship)
                            updates += 1
                    elif isinstance(relationships[target_field], str):
                        # Convert to list
                        relationships[target_field] = [relationships[target_field], new_relationship]
                        updates += 1
                else:
                    # Create new list
                    relationships[target_field] = [new_relationship]
                    updates += 1
    
    return updates

def validate_spr_format(spr: Dict[str, Any]) -> tuple[bool, str]:
    """Validate SPR follows Guardian pointS format."""
    spr_id = spr.get('spr_id', '')
    
    if not spr_id:
        return False, "Missing spr_id"
    
    # Check Guardian pointS format: FirstLast uppercase, middle lowercase/space
    words = spr_id.split()
    if len(words) == 0:
        return False, "Empty spr_id"
    
    # First word: first char uppercase
    if not words[0][0].isupper():
        return False, f"First word must start with uppercase: {words[0]}"
    
    # Last word: last char uppercase
    if not words[-1][-1].isupper():
        return False, f"Last word must end with uppercase: {words[-1]}"
    
    # Middle words: lowercase or spaces
    for word in words[1:-1]:
        if not word.islower() and not all(c.isalnum() or c.isspace() for c in word):
            return False, f"Middle words must be lowercase: {word}"
    
    return True, "Valid"

def main():
    """Main integration function."""
    print("=" * 70)
    print("Objective Generation Engine Integration Script")
    print("=" * 70)
    print()
    
    # Step 1: Load SPR definitions
    print("Step 1: Loading SPR definitions...")
    try:
        spr_definitions = load_spr_definitions()
        print(f"✓ Loaded {len(spr_definitions)} existing SPRs")
    except Exception as e:
        print(f"✗ Error loading SPR definitions: {e}")
        return 1
    
    # Step 2: Load Objective generation enginE SPR
    print("\nStep 2: Loading Objective generation enginE SPR definition...")
    try:
        oge_spr = load_objective_generation_engine_spr()
        print(f"✓ Loaded SPR: {oge_spr.get('spr_id')}")
    except Exception as e:
        print(f"✗ Error loading Objective generation enginE SPR: {e}")
        return 1
    
    # Step 3: Validate SPR format
    print("\nStep 3: Validating SPR format...")
    is_valid, message = validate_spr_format(oge_spr)
    if not is_valid:
        print(f"✗ Invalid SPR format: {message}")
        return 1
    print(f"✓ SPR format valid: {message}")
    
    # Step 4: Check if SPR already exists
    print("\nStep 4: Checking for existing SPR...")
    spr_id = oge_spr.get('spr_id')
    if spr_exists(spr_definitions, spr_id):
        print(f"⚠ SPR '{spr_id}' already exists")
        response = input("   Overwrite? (yes/no): ").strip().lower()
        if response != 'yes':
            print("   Skipping SPR addition")
            return 0
        
        # Remove existing SPR
        spr_definitions = [s for s in spr_definitions if s.get('spr_id') != spr_id]
        print(f"✓ Removed existing SPR")
    else:
        print(f"✓ SPR '{spr_id}' not found, will add")
    
    # Step 5: Add Objective generation enginE SPR
    print(f"\nStep 5: Adding SPR '{spr_id}' to Knowledge Tapestry...")
    spr_definitions.append(oge_spr)
    print(f"✓ Added SPR (total SPRs: {len(spr_definitions)})")
    
    # Step 6: Update related SPRs
    print("\nStep 6: Updating related SPRs with cross-references...")
    updates = update_related_sprs(spr_definitions)
    print(f"✓ Updated {updates} relationship(s) in related SPRs")
    
    # Step 7: Save updated SPR definitions
    print("\nStep 7: Saving updated SPR definitions...")
    try:
        save_spr_definitions(spr_definitions)
        print(f"✓ Saved {len(spr_definitions)} SPRs to Knowledge Tapestry")
    except Exception as e:
        print(f"✗ Error saving SPR definitions: {e}")
        return 1
    
    # Step 8: Summary
    print("\n" + "=" * 70)
    print("Integration Complete!")
    print("=" * 70)
    print(f"✓ SPR '{spr_id}' added to Knowledge Tapestry")
    print(f"✓ {updates} related SPR(s) updated with cross-references")
    print(f"✓ Backup created: knowledge_graph/spr_definitions_tv.json.backup")
    print()
    print("Next Steps:")
    print("1. Review the updated SPR definitions")
    print("2. Begin implementation using outputs/objective_generation_engine_implementation_plan.md")
    print("3. Test with sample queries")
    print("4. Integrate with RISE_Orchestrator.process_query()")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

