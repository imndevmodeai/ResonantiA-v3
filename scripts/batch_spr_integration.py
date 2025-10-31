import json
import os
import sys
from typing import List, Dict, Any

# Ensure the project root is in the Python path to allow for imports from the main package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Dynamically find the main package name instead of hardcoding
# This assumes the directory containing the engine is a package.
main_package_dir = os.path.join(project_root, 'Three_PointO_ArchE')
if main_package_dir not in sys.path:
     sys.path.insert(0, main_package_dir)

try:
    from insight_solidification_engine import (
        InsightSolidificationEngine,
        InsightCandidate,
        InsightType,
        SolidificationMethod
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current sys.path: {sys.path}")
    print("Please ensure you are running this script from the project root or the 'scripts' directory is configured correctly.")
    sys.exit(1)

def load_sprs_from_string(data_string: str) -> List[Dict[str, Any]]:
    """Loads SPR definitions from a JSON string."""
    try:
        data = json.loads(data_string)
        # The actual data is under the 'spr_definitions' key
        return data.get('spr_definitions', [])
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error: Could not decode or find 'spr_definitions' key in JSON string: {e}")
        return []

def map_spr_to_insight_candidate(spr_data: Dict[str, Any]) -> InsightCandidate:
    """Maps a raw SPR data dictionary to an InsightCandidate object."""
    spr_id = spr_data.get("spr_id") or spr_data.get("name") or "Unknown_SPR"
    
    # Handle different schema structures gracefully
    definition = spr_data.get("definition") or spr_data.get("description", "No definition provided.")
    source_ref = "Keyholder_Directive_Batch_Load"
    if "metadata" in spr_data and spr_data["metadata"] is not None:
        source_ref = spr_data["metadata"].get("source_reference", source_ref)

    return InsightCandidate(
        insight_id=f"batch_load_{spr_id}",
        insight_type=InsightType.CONCEPTUAL,
        core_concept=spr_data.get("term", spr_data.get("name", "Unknown Term")),
        supporting_details=definition,
        source_reference=source_ref,
        evidence_strength=spr_data.get("metadata", {}).get("evidence_strength", 0.9) if spr_data.get("metadata") else 0.9,
        confidence=spr_data.get("metadata", {}).get("confidence", 0.95) if spr_data.get("metadata") else 0.95,
        suggested_spr_name=spr_id,
        proposed_category=spr_data.get("category", "GeneralConcept"),
        proposed_relationships=spr_data.get("relationships", {}),
        raw_data=spr_data # Pass the full original data
    )

def main():
    """Main function to run the batch SPR integration."""
    print("--- Starting Batch SPR Integration (Controlled Knowledge Expansion) ---")

    # The user attached the full canonical file. Let's use that.
    canonical_spr_file_path = os.path.join(project_root, 'knowledge_graph', 'spr_definitions_tv.json')
    try:
        with open(canonical_spr_file_path, 'r', encoding='utf-8') as f:
            new_sprs_data_string = f.read()
        print(f"Loaded canonical SPR data from: {canonical_spr_file_path}")
    except FileNotFoundError:
        print(f"ERROR: Canonical SPR file not found at {canonical_spr_file_path}")
        return
    except Exception as e:
        print(f"ERROR: Could not read canonical SPR file: {e}")
        return

    new_sprs_data = load_sprs_from_string(new_sprs_data_string)

    if not new_sprs_data:
        print("No new SPRs to process from the canonical file. Exiting.")
        return

    # Path to the primary Knowledge Tapestry
    knowledge_path = os.path.join(project_root, 'knowledge_graph', 'spr_definitions_tv.json')
    
    # Instantiate the engine
    engine = InsightSolidificationEngine(knowledge_path)

    # Backup the current knowledge tapestry before starting
    if engine.config['auto_backup_enabled']:
        backup_created = engine.spr_manager.create_backup()
        if not backup_created:
            print("Warning: Failed to create knowledge base backup. Proceeding without one.")

    success_count = 0
    failure_count = 0
    updated_count = 0
    new_count = 0

    print(f"\nFound {len(new_sprs_data)} SPR definitions to integrate.")
    print("--- Starting solidification process (with OVERWRITE enabled) ---\n")

    for i, spr_data in enumerate(new_sprs_data):
        spr_id = spr_data.get('spr_id') or spr_data.get('name', 'N/A')
        print(f"Processing SPR {i+1}/{len(new_sprs_data)}: {spr_id}")
        
        insight_candidate = map_spr_to_insight_candidate(spr_data)
        
        # CORRECTIVE ACTION: Pass solidification_method=SolidificationMethod.OVERWRITE
        # to ensure existing SPRs are updated with the canonical data.
        result = engine.solidify_insight(
            insight_candidate, 
            solidification_method=SolidificationMethod.OVERWRITE
        )
        
        if result.knowledge_tapestry_updated:
            if "updated_spr" in result.spr_changes_made[0]:
                updated_count += 1
                print(f"  -> SUCCESS (Updated): {result.spr_changes_made}")
            else: # Assumes "created_spr"
                new_count += 1
                print(f"  -> SUCCESS (New): {result.spr_changes_made}")
            success_count += 1
        else:
            print(f"  -> FAILURE: {result.execution_status} - {result.lessons_learned}")
            failure_count += 1

    print("\n--- Batch SPR Integration Complete ---")
    print(f"Total SPRs processed: {len(new_sprs_data)}")
    print(f"Successfully integrated (New): {new_count}")
    print(f"Successfully integrated (Updated): {updated_count}")
    print(f"Total Success: {success_count}")
    print(f"Failed to integrate: {failure_count}")

    # Final verification
    try:
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            final_tapestry = json.load(f)
            final_count = len(final_tapestry.get('spr_definitions', []))
            print(f"\nFinal Knowledge Tapestry now contains {final_count} SPRs.")
    except Exception as e:
        print(f"\nCould not verify final SPR count: {e}")

if __name__ == "__main__":
    main() 