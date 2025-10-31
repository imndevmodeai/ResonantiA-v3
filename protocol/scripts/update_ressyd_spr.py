#!/usr/bin/env python3
"""
Update RessydmastergenerationworkfloW SPR Definition
This script updates the SPR definition to reflect the comprehensive workflow and correct GitHub file structure.
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
    backup_path = backup_dir / f"spr_definitions_tv_ressyd_updated_{timestamp}.json"
    
    try:
        # Save backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Backup created: {backup_path}")
        
        # Save updated file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Updated file saved: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def update_ressyd_spr_definition(spr_def):
    """Update the RessydmastergenerationworkfloW SPR definition"""
    
    updated_spr = {
        "spr_id": "RessydmastergenerationworkfloW",
        "term": "Ressyd Master Generation Workflow",
        "definition": "A comprehensive system workflow that orchestrates the collection, validation, and packaging of all protocol documents, workflow definitions, Knowledge tapestrY components, and system implementations into a complete master package for distribution, deployment, and archival purposes. This workflow ensures the integrity and completeness of the entire ResonantiA Protocol ecosystem.",
        "category": "SystemWorkflow",
        "relationships": {
            "type": "PackagingOrchestration",
            "manages": [
                "Protocol documents",
                "Workflow definitions", 
                "Knowledge tapestrY",
                "System components",
                "Documentation generation"
            ],
            "produces": [
                "Master package",
                "Deployment guide",
                "System overview",
                "Change log",
                "Archive manifest"
            ],
            "validates": [
                "File integrity",
                "Document completeness",
                "Knowledge graph coherence",
                "Workflow consistency"
            ],
            "integrates_with": [
                "InsightsolidificatioN",
                "PatterncrystallizatioN",
                "KnowledgenetworkonenesS",
                "IntegratedactionreflectioN"
            ],
            "supports": [
                "System deployment",
                "Knowledge distribution",
                "Protocol evolution",
                "Collective consciousnesS"
            ]
        },
        "blueprint_details": {
            "workflow_file": "workflows/system/ressyd_master_generation.json",
            "phases": [
                "Protocol Document Audit",
                "Workflow System Audit", 
                "Knowledge Tapestry Audit",
                "Master Package Generation",
                "Documentation Generation",
                "Validation and Archival"
            ],
            "outputs": {
                "primary": "master_package.tar.gz",
                "documentation": [
                    "deployment_guide.md",
                    "system_overview.md", 
                    "changelog.md",
                    "file_structure_map.md"
                ],
                "metadata": [
                    "package_manifest.json",
                    "archive_manifest.json"
                ]
            },
            "file_structure": {
                "protocol/": "CRITICAL_MANDATES.md, ResonantiA_Protocol_v3.0.md, ResonantiA_Protocol_v3.1-CA.md",
                "workflows/": "All workflow JSON files",
                "knowledge_graph/": "spr_definitions_tv.json and related files",
                "three_pointo_arche/": "Complete Three_PointO_ArchE system components",
                "mastermind/": "Complete Mastermind system components",
                "scripts/": "Utility and maintenance scripts"
            },
            "iar_compliance": "Full"
        },
        "example_application": "When preparing a new release of the ResonantiA Protocol, the RessydmastergenerationworkfloW is executed to gather all updated protocol documents, workflow definitions, and Knowledge tapestrY changes into a complete, validated package ready for distribution to other ArchE instances.",
        "activation_prompts": {
            "initiate": "Initiate the RessydmastergenerationworkfloW to create a complete master package of the current system state.",
            "validate": "Validate the completeness and integrity of the generated master package using the RessydmastergenerationworkfloW validation phase.",
            "deploy": "Use the RessydmastergenerationworkfloW outputs to deploy the complete system to a new environment."
        },
        "metadata": {
            "version": "1.1",
            "status": "active",
            "created_by": "Keyholder Directive KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "last_modified_date": datetime.now().strftime("%Y-%m-%d"),
            "source_reference": "Phase 2 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0 - Updated for GitHub Structure",
            "implementation_status": "Complete",
            "workflow_ready": True,
            "file_structure_updated": True
        }
    }
    
    return updated_spr

def update_ressyd_spr_in_knowledge_tapestry(data):
    """Update the RessydmastergenerationworkfloW SPR in the Knowledge Tapestry"""
    
    if not data or 'spr_definitions' not in data:
        print("Invalid SPR definitions structure")
        return None
    
    # Find and update the RessydmastergenerationworkfloW SPR
    for i, spr_def in enumerate(data['spr_definitions']):
        if spr_def.get('spr_id') == 'RessydmastergenerationworkfloW':
            print(f"Updating RessydmastergenerationworkfloW SPR definition...")
            data['spr_definitions'][i] = update_ressyd_spr_definition(spr_def)
            print(f"✅ RessydmastergenerationworkfloW SPR updated successfully")
            return data, True
    
    print("RessydmastergenerationworkfloW SPR not found in Knowledge Tapestry")
    return data, False

def main():
    """Main execution function"""
    print("=== Update RessydmastergenerationworkfloW SPR Definition ===")
    print("GitHub File Structure Correction")
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
    
    # Update RessydmastergenerationworkfloW SPR
    print("Updating RessydmastergenerationworkfloW SPR definition...")
    updated_data, updated = update_ressyd_spr_in_knowledge_tapestry(data)
    
    if not updated_data:
        print("Error updating SPR")
        sys.exit(1)
    
    print()
    
    if updated:
        print("✅ RessydmastergenerationworkfloW SPR definition updated successfully")
        print()
        print("Updated Features:")
        print("  - Comprehensive workflow description")
        print("  - Correct GitHub file structure mapping")
        print("  - Enhanced blueprint details")
        print("  - Updated activation prompts")
        print("  - File structure documentation")
        print("  - Version 1.1 metadata")
    else:
        print("ℹ️  RessydmastergenerationworkfloW SPR not found")
    
    print()
    
    # Save updated file
    print("Saving updated file...")
    if save_spr_definitions(updated_data, spr_filepath):
        print("✅ Knowledge Tapestry updated successfully")
        print("✅ Backup created for safety")
    else:
        print("❌ Error saving updated file")
        sys.exit(1)
    
    print()
    print("=== RessydmastergenerationworkfloW SPR Update Complete ===")
    print("GitHub file structure correction applied")
    print("Workflow now reflects actual repository structure")

if __name__ == "__main__":
    main() 