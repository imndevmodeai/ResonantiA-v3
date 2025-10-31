#!/usr/bin/env python3
"""
SPR Format Sanitization Script
Corrects Guardian pointS compliance violations in spr_definitions_tv.json

Corrections:
- IaR -> IntegratedactionreflectioN
- KnO -> KnowledgenetworkonenesS

This script implements Action A.2 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0
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
    backup_path = backup_dir / f"spr_definitions_tv_backup_{timestamp}.json"
    
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

def correct_spr_id(spr_id):
    """Apply Guardian pointS corrections to SPR ID"""
    corrections = {
        "IaR": "IntegratedactionreflectioN",
        "KnO": "KnowledgenetworkonenesS"
    }
    return corrections.get(spr_id, spr_id)

def sanitize_spr_definitions(data):
    """Sanitize all SPR definitions for Guardian pointS compliance"""
    if not data or 'spr_definitions' not in data:
        print("Invalid SPR definitions structure")
        return None
    
    corrections_made = []
    
    for spr_def in data['spr_definitions']:
        original_id = spr_def.get('spr_id', '')
        corrected_id = correct_spr_id(original_id)
        
        if original_id != corrected_id:
            print(f"Correcting: {original_id} -> {corrected_id}")
            spr_def['spr_id'] = corrected_id
            corrections_made.append((original_id, corrected_id))
    
    # Also correct any references in relationships
    for spr_def in data['spr_definitions']:
        if 'relationships' in spr_def:
            relationships = spr_def['relationships']
            
            # Check all relationship arrays
            for key, value in relationships.items():
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        corrected_item = correct_spr_id(item)
                        if item != corrected_item:
                            print(f"Correcting relationship reference: {item} -> {corrected_item}")
                            value[i] = corrected_item
                            corrections_made.append((item, corrected_item))
    
    return data, corrections_made

def main():
    """Main execution function"""
    print("=== SPR Format Sanitization Script ===")
    print("Action A.2 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0")
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
    
    print(f"Loaded {len(data.get('spr_definitions', []))} SPR definitions")
    print()
    
    # Sanitize SPR definitions
    print("Applying Guardian pointS corrections...")
    corrected_data, corrections = sanitize_spr_definitions(data)
    
    if not corrected_data:
        print("Error during sanitization")
        sys.exit(1)
    
    print()
    print(f"Total corrections made: {len(corrections)}")
    
    if corrections:
        print("\nCorrections applied:")
        for original, corrected in corrections:
            print(f"  {original} -> {corrected}")
    else:
        print("No corrections needed - file already compliant")
    
    print()
    
    # Save corrected file
    print("Saving corrected file...")
    if save_spr_definitions(corrected_data, spr_filepath):
        print("✅ SPR format sanitization completed successfully")
        print("✅ Guardian pointS compliance achieved")
        print("✅ Backup created for safety")
    else:
        print("❌ Error saving corrected file")
        sys.exit(1)
    
    print()
    print("=== Sanitization Complete ===")
    print("Phase 1 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0: COMPLETE")
    print("Ready for Phase 2: RessydmastergenerationworkfloW Solidification")

if __name__ == "__main__":
    main() 