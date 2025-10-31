#!/usr/bin/env python3
"""
Add RessydmastergenerationworkfloW SPR to Knowledge Tapestry
This script implements Action B.3 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0
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
    backup_path = backup_dir / f"spr_definitions_tv_ressyd_added_{timestamp}.json"
    
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

def create_ressyd_spr():
    """Create the RessydmastergenerationworkfloW SPR definition"""
    
    ressyd_spr = {
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
                    "changelog.md"
                ],
                "metadata": [
                    "package_manifest.json",
                    "archive_manifest.json"
                ]
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
            "version": "1.0",
            "status": "active",
            "created_by": "Keyholder Directive KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "last_modified_date": datetime.now().strftime("%Y-%m-%d"),
            "source_reference": "Phase 2 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0",
            "implementation_status": "Complete",
            "workflow_ready": True
        }
    }
    
    return ressyd_spr

def add_ressyd_spr_to_knowledge_tapestry(data):
    """Add the RessydmastergenerationworkfloW SPR to the Knowledge Tapestry"""
    
    if not data or 'spr_definitions' not in data:
        print("Invalid SPR definitions structure")
        return None
    
    # Check if SPR already exists
    existing_sprs = [spr.get('spr_id', '') for spr in data['spr_definitions']]
    if 'RessydmastergenerationworkfloW' in existing_sprs:
        print("RessydmastergenerationworkfloW SPR already exists in Knowledge Tapestry")
        return data, False
    
    # Create the new SPR
    ressyd_spr = create_ressyd_spr()
    
    # Add to the Knowledge Tapestry
    data['spr_definitions'].append(ressyd_spr)
    
    print(f"Added RessydmastergenerationworkfloW SPR to Knowledge Tapestry")
    print(f"New SPR count: {len(data['spr_definitions'])}")
    
    return data, True

def main():
    """Main execution function"""
    print("=== Add RessydmastergenerationworkfloW SPR Script ===")
    print("Action B.3 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0")
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
    
    # Add RessydmastergenerationworkfloW SPR
    print("Adding RessydmastergenerationworkfloW SPR...")
    updated_data, added = add_ressyd_spr_to_knowledge_tapestry(data)
    
    if not updated_data:
        print("Error adding SPR")
        sys.exit(1)
    
    final_count = len(updated_data.get('spr_definitions', []))
    print()
    
    if added:
        print(f"✅ RessydmastergenerationworkfloW SPR added successfully")
        print(f"SPR count: {original_count} -> {final_count} (+1)")
        print()
        print("SPR Details:")
        print("  - ID: RessydmastergenerationworkfloW")
        print("  - Category: SystemWorkflow")
        print("  - Status: Active")
        print("  - Workflow Ready: True")
    else:
        print("ℹ️  RessydmastergenerationworkfloW SPR already exists")
    
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
    print("=== RessydmastergenerationworkfloW SPR Addition Complete ===")
    print("Phase 2 of KNOWLEDGE_TAPESTRY_HARMONIZATION_V1.0: COMPLETE")
    print("Ready for Phase 3: ResonantgratidsouL Harmonization")

if __name__ == "__main__":
    main() 