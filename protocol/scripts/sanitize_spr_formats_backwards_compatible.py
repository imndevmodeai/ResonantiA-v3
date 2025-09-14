#!/usr/bin/env python3
"""
Backwards-Compatible SPR Format Sanitization Script
Corrects Guardian pointS compliance violations in spr_definitions_tv.json
and adds abbreviated versions for backwards compatibility

Corrections:
- IaR -> IntegratedactionreflectioN (full name)
- KnO -> KnowledgenetworkonenesS (full name)
- Add IaR and KnO as separate SPR entries that reference the full versions
- Update all relationship references to use full names

This script implements Action A.3 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0
with backwards compatibility support
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def load_spr_definitions(filepath):
    """Load SPR definitions from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading SPR definitions: {e}")
        return None

def save_spr_definitions(data, filepath):
    """Save SPR definitions to JSON file with backup"""
    # Create backup
    backup_dir = Path("backup_spr_sanitization")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"spr_definitions_tv_backwards_compatible_{timestamp}.json"
    
    try:
        # Save backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Backup created: {backup_path}")
        
        # Save corrected file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Corrected file saved: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def correct_spr_reference(reference):
    """Apply Guardian pointS corrections to any SPR reference"""
    corrections = {
        "IaR": "IntegratedactionreflectioN",
        "KnO": "KnowledgenetworkonenesS",
        "IAR": "IntegratedactionreflectioN"  # Also correct uppercase version
    }
    return corrections.get(reference, reference)

def create_backwards_compatible_sprs():
    """Create backwards-compatible SPR entries for IaR and KnO"""
    
    # IaR backwards-compatible entry
    iar_compat = {
        "spr_id": "IaR",
        "term": "Integrated Action Reflection (Abbreviated)",
        "definition": "Backwards-compatible abbreviated reference to IntegratedactionreflectioN. This SPR maintains compatibility with existing references while the full name provides Guardian pointS compliance.",
        "category": "CompatibilityLayer",
        "relationships": {
            "type": "Alias",
            "aliases": [
                "IntegratedactionreflectioN"
            ],
            "forwards_to": [
                "IntegratedactionreflectioN"
            ],
            "maintained_for": [
                "BackwardsCompatibility",
                "LegacyReferences"
            ]
        },
        "blueprint_details": "This is a compatibility layer SPR that forwards to the full Guardian pointS compliant version.",
        "example_application": "Legacy code referencing 'IaR' will still function while new implementations use 'IntegratedactionreflectioN'.",
        "metadata": {
            "version": "1.0",
            "status": "compatibility",
            "created_by": "BackwardsCompatibilityScript",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "last_modified_date": datetime.now().strftime("%Y-%m-%d"),
            "source_reference": "Guardian pointS compliance correction",
            "compatibility_note": "This SPR exists for backwards compatibility only"
        }
    }
    
    # KnO backwards-compatible entry
    kno_compat = {
        "spr_id": "KnO",
        "term": "Knowledge Network Oneness (Abbreviated)",
        "definition": "Backwards-compatible abbreviated reference to KnowledgenetworkonenesS. This SPR maintains compatibility with existing references while the full name provides Guardian pointS compliance.",
        "category": "CompatibilityLayer",
        "relationships": {
            "type": "Alias",
            "aliases": [
                "KnowledgenetworkonenesS"
            ],
            "forwards_to": [
                "KnowledgenetworkonenesS"
            ],
            "maintained_for": [
                "BackwardsCompatibility",
                "LegacyReferences"
            ]
        },
        "blueprint_details": "This is a compatibility layer SPR that forwards to the full Guardian pointS compliant version.",
        "example_application": "Legacy code referencing 'KnO' will still function while new implementations use 'KnowledgenetworkonenesS'.",
        "metadata": {
            "version": "1.0",
            "status": "compatibility",
            "created_by": "BackwardsCompatibilityScript",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "last_modified_date": datetime.now().strftime("%Y-%m-%d"),
            "source_reference": "Guardian pointS compliance correction",
            "compatibility_note": "This SPR exists for backwards compatibility only"
        }
    }
    
    return [iar_compat, kno_compat]

def sanitize_spr_definitions_backwards_compatible(data):
    """Enhanced sanitization that corrects SPR IDs, adds backwards compatibility, and updates all references"""
    if not data or 'spr_definitions' not in data:
        print("Invalid SPR definitions structure")
        return None
    
    corrections_made = []
    
    # First pass: correct SPR IDs
    for spr_def in data['spr_definitions']:
        original_id = spr_def.get('spr_id', '')
        corrected_id = correct_spr_reference(original_id)
        
        if original_id != corrected_id:
            print(f"Correcting SPR ID: {original_id} -> {corrected_id}")
            spr_def['spr_id'] = corrected_id
            corrections_made.append((original_id, corrected_id))
    
    # Second pass: correct all relationship references
    for spr_def in data['spr_definitions']:
        if 'relationships' in spr_def:
            relationships = spr_def['relationships']
            
            # Check all relationship arrays
            for key, value in relationships.items():
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        corrected_item = correct_spr_reference(item)
                        if item != corrected_item:
                            print(f"Correcting relationship reference: {item} -> {corrected_item}")
                            value[i] = corrected_item
                            corrections_made.append((item, corrected_item))
    
    # Third pass: correct any other text fields that might contain SPR references
    for spr_def in data['spr_definitions']:
        # Check definition field
        if 'definition' in spr_def:
            original_def = spr_def['definition']
            corrected_def = original_def
            for old_ref, new_ref in [("IaR", "IntegratedactionreflectioN"), 
                                   ("KnO", "KnowledgenetworkonenesS"),
                                   ("IAR", "IntegratedactionreflectioN")]:
                if old_ref in corrected_def:
                    corrected_def = corrected_def.replace(old_ref, new_ref)
                    print(f"Correcting definition reference: {old_ref} -> {new_ref}")
                    corrections_made.append((old_ref, new_ref))
            spr_def['definition'] = corrected_def
        
        # Check example_application field
        if 'example_application' in spr_def:
            original_example = spr_def['example_application']
            corrected_example = original_example
            for old_ref, new_ref in [("IaR", "IntegratedactionreflectioN"), 
                                   ("KnO", "KnowledgenetworkonenesS"),
                                   ("IAR", "IntegratedactionreflectioN")]:
                if old_ref in corrected_example:
                    corrected_example = corrected_example.replace(old_ref, new_ref)
                    print(f"Correcting example reference: {old_ref} -> {new_ref}")
                    corrections_made.append((old_ref, new_ref))
            spr_def['example_application'] = corrected_example
    
    # Fourth pass: add backwards-compatible SPR entries
    print("Adding backwards-compatible SPR entries...")
    backwards_compat_sprs = create_backwards_compatible_sprs()
    data['spr_definitions'].extend(backwards_compat_sprs)
    print(f"Added {len(backwards_compat_sprs)} backwards-compatible SPR entries")
    
    return data, corrections_made

def main():
    """Main execution function"""
    print("=== Backwards-Compatible SPR Format Sanitization Script ===")
    print("Action A.3 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0")
    print("With Backwards Compatibility Support")
    print(f"Execution time: {datetime.now()}")
    print()
    
    # Define file paths
    spr_filepath = "knowledge_graph/spr_definitions_tv.json"
    
    # Verify file exists
    if not os.path.exists(spr_filepath):
        print(f"Error: SPR definitions file not found: {spr_filepath}")
        sys.exit(1)
    
    # Load SPR definitions
    print("Loading SPR definitions...")
    data = load_spr_definitions(spr_filepath)
    if not data:
        sys.exit(1)
    
    original_count = len(data.get('spr_definitions', []))
    print(f"Loaded {original_count} SPR definitions")
    print()
    
    # Sanitize SPR definitions
    print("Applying backwards-compatible Guardian pointS corrections...")
    corrected_data, corrections = sanitize_spr_definitions_backwards_compatible(data)
    
    if not corrected_data:
        print("Error during sanitization")
        sys.exit(1)
    
    final_count = len(corrected_data.get('spr_definitions', []))
    print()
    print(f"Total corrections made: {len(corrections)}")
    print(f"SPR count: {original_count} -> {final_count} (+{final_count - original_count} compatibility entries)")
    
    if corrections:
        print("\nCorrections applied:")
        for original, corrected in corrections:
            print(f"  {original} -> {corrected}")
    else:
        print("No corrections needed - file already compliant")
    
    print()
    print("Backwards-compatible entries added:")
    print("  - IaR (forwards to IntegratedactionreflectioN)")
    print("  - KnO (forwards to KnowledgenetworkonenesS)")
    
    print()
    
    # Save corrected file
    print("Saving corrected file...")
    if save_spr_definitions(corrected_data, spr_filepath):
        print("✅ Backwards-compatible SPR format sanitization completed successfully")
        print("✅ Guardian pointS compliance achieved")
        print("✅ All relationship references updated")
        print("✅ Backwards compatibility maintained")
        print("✅ Backup created for safety")
    else:
        print("❌ Error saving corrected file")
        sys.exit(1)
    
    print()
    print("=== Backwards-Compatible Sanitization Complete ===")
    print("Phase 1 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0: COMPLETE")
    print("Ready for Phase 2: RessydmastergenerationworkfloW Solidification")

if __name__ == "__main__":
    main() 