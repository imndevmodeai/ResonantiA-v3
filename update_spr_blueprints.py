#!/usr/bin/env python3
"""
Update SPR blueprint_details with proper implementation mappings
This script adds executable blueprint_details to SPRs that have implementations
"""

import json
import sys
from pathlib import Path

def update_spr_blueprints():
    """Update SPR definitions with proper blueprint_details for implementation mapping"""
    
    spr_file = Path("Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json")
    
    # Load current SPRs
    with open(spr_file, 'r') as f:
        sprs = json.load(f)
    
    # Define implementation mappings for existing tools
    implementation_mappings = {
        # Core cognitive tools that exist  
        "ComparativEfluxuaLprocessinG": "cfp_framework.py/CfpframeworK.run_analysis",
        "CausalinferencE": "causal_inference_tool.py/perform_causal_inference:estimate_effect",
        "AgentbasedmodelinG": "agent_based_modeling_tool.py/perform_abm", 
        "PredictivemodelinGtooL": "predictive_modeling_tool.py/run_prediction:forecast_future_states",
        "CodeexecutoR": "code_executor.py/execute_code",
        "SearchtooL": "tools/search_tool.py/SearchTool.search",
        "LlmtooL": "llm_tool.py/generate_text_llm",
        
        # System components that exist
        "KnowledgecrystallizationsysteM": "knowledge_crystallization_system.py/crystallize_pattern",
        "ResonanceevaluatoR": "resonance_evaluator.py/evaluate_resonance",
        
        # Analysis tools that exist
        "Initial_Analysis_Standard": "proof_of_enhanced_capabilities.py/initial_analysis_standard",
        "Hypothesis_Generation": "proof_of_enhanced_capabilities.py/hypothesis_generation",
        "Code_Generation_Python": "proof_of_enhanced_capabilities.py/code_generation_python",
        
        # Workflow components
        "WorkflowenginE": "workflow_engine.py/WorkflowEngine.execute_workflow",
    }
    
    # Update SPRs with implementation mappings
    updated_count = 0
    for spr in sprs:
        spr_id = spr.get('spr_id', '')
        
        if spr_id in implementation_mappings:
            current_blueprint = spr.get('blueprint_details', '')
            new_blueprint = implementation_mappings[spr_id]
            
            # Update if different or empty
            if current_blueprint != new_blueprint:
                spr['blueprint_details'] = new_blueprint
                print(f"Updated {spr_id}: {new_blueprint}")
                updated_count += 1
    
    # Save updated SPRs
    if updated_count > 0:
        with open(spr_file, 'w') as f:
            json.dump(sprs, f, indent=2)
        print(f"\n✅ Updated {updated_count} SPRs with implementation mappings")
        print(f"📁 Saved to: {spr_file}")
    else:
        print("ℹ️  No SPRs needed updating")
    
    return updated_count

def verify_implementations():
    """Verify that the mapped implementations actually exist"""
    print("\n=== Verifying Implementation Files ===")
    
    spr_file = Path("Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json")
    with open(spr_file, 'r') as f:
        sprs = json.load(f)
    
    base_path = Path("Three_PointO_ArchE")
    
    for spr in sprs:
        blueprint = spr.get('blueprint_details', '')
        if '/' in blueprint and '.py' in blueprint:
            spr_id = spr.get('spr_id', 'Unknown')
            module_path, target = blueprint.split('/', 1)
            
            # Check if file exists
            file_path = base_path / module_path
            if file_path.exists():
                print(f"✅ {spr_id}: {module_path} exists")
            else:
                print(f"❌ {spr_id}: {module_path} NOT FOUND")
                # Try alternative paths
                alt_paths = [
                    Path(".") / module_path,
                    Path("Three_PointO_ArchE/tools") / module_path,
                ]
                for alt_path in alt_paths:
                    if alt_path.exists():
                        print(f"   ➡️  Found at: {alt_path}")
                        break

if __name__ == "__main__":
    print("SPR Blueprint Implementation Mapper")
    print("=" * 50)
    
    updated_count = update_spr_blueprints()
    
    if updated_count > 0:
        verify_implementations()
    
    print("\n" + "=" * 50)
    print("Blueprint mapping completed.") 