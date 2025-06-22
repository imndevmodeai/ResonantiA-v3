#!/usr/bin/env python3
"""
RESONANTIA PROTOCOL v3.1-CA - PHASE 3.2 TEST CASE 1
SPR Bridge Validation: Knowledge Crystallization System
Architecture: AI Studio ArchE | Implementation: Cursor ArchE

CRITICAL TEST: System's ability to learn and evolve its own knowledge base
"""

import json
import os
from datetime import datetime
from Three_PointO_ArchE.action_registry import invoke_spr_action

def load_knowledge_tapestry():
    """Load the current Knowledge Tapestry for verification"""
    tapestry_path = "Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json"
    try:
        with open(tapestry_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading Knowledge Tapestry: {e}")
        return None

def verify_spr_exists(spr_id):
    """Verify if a specific SPR exists in the Knowledge Tapestry"""
    tapestry = load_knowledge_tapestry()
    if tapestry is None:
        return False, "Could not load Knowledge Tapestry"
    
    if isinstance(tapestry, list):
        # List format - search by spr_id field
        for spr_def in tapestry:
            if spr_def.get('spr_id') == spr_id:
                return True, spr_def
        return False, f"SPR '{spr_id}' not found in tapestry (list format, {len(tapestry)} SPRs)"
    else:
        # Dict format - direct key lookup
        if spr_id in tapestry:
            return True, tapestry[spr_id]
        return False, f"SPR '{spr_id}' not found in tapestry (dict format, {len(tapestry)} SPRs)"

def execute_phase3_test1():
    """
    Phase 3.2 Test Case 1: Knowledge Crystallization System SPR Bridge Validation
    """
    print("=" * 70)
    print("RESONANTIA PROTOCOL v3.1-CA - PHASE 3.2 TEST CASE 1")
    print("SPR BRIDGE VALIDATION: KNOWLEDGE CRYSTALLIZATION SYSTEM")
    print("CRITICAL TEST: SYSTEM'S ABILITY TO LEARN AND EVOLVE")
    print("=" * 70)
    
    # Step 1: Record initial state of Knowledge Tapestry
    print("\n[STEP 1] Recording initial Knowledge Tapestry state...")
    initial_tapestry = load_knowledge_tapestry()
    if initial_tapestry:
        initial_count = len(initial_tapestry)
        print(f"✅ Initial Knowledge Tapestry loaded: {initial_count} SPRs")
    else:
        print("❌ Failed to load initial Knowledge Tapestry")
        return None, False
    
    # Step 2: Define the pattern to crystallize
    print("\n[STEP 2] Defining observed pattern for crystallization...")
    observed_pattern = {
        "name": "Topical Research and Briefing",
        "description": "A common workflow that performs a web search on a given topic and then generates a concise summary of the findings.",
        "steps": [
            {"action": "web_search", "parameters": {"query": "{topic}"}},
            {"action": "llm_summarize", "parameters": {"text": "output_of_step_1"}}
        ],
        "input_parameters": ["topic"],
        "output": "A summary briefing.",
        "success_metrics": {
            "completeness": 0.85,
            "accuracy": 0.90,
            "efficiency": 0.75
        },
        "usage_frequency": 12,
        "last_observed": "2025-06-22T07:00:00Z"
    }
    
    proposed_spr_id = "ResearchAndBriefingPatterN"
    print(f"✅ Pattern defined: {observed_pattern['name']}")
    print(f"   Proposed SPR ID: {proposed_spr_id}")
    print(f"   Pattern complexity: {len(observed_pattern['steps'])} steps")
    print(f"   Success metrics: {observed_pattern['success_metrics']}")
    
    # Step 3: Verify SPR doesn't already exist
    print("\n[STEP 3] Verifying SPR doesn't already exist...")
    exists_before, details_before = verify_spr_exists(proposed_spr_id)
    if exists_before:
        print(f"⚠️  SPR '{proposed_spr_id}' already exists! This may affect test validity.")
        print(f"   Existing definition: {details_before.get('definition', 'N/A')}")
    else:
        print(f"✅ SPR '{proposed_spr_id}' does not exist. Test can proceed.")
    
    # Step 4: Configure crystallization parameters
    print("\n[STEP 4] Configuring Knowledge Crystallization parameters...")
    crystallization_params = {
        "insight_candidate": observed_pattern,
        "insight_type": "workflow_pattern",
        "proposed_spr_id": proposed_spr_id,
        "evidence_source": "Observation of repeated successful workflows in session_log_alpha.txt",
        "confidence_threshold": 0.7,
        "validation_required": True
    }
    print("✅ Crystallization parameters configured")
    print(f"   Insight Type: {crystallization_params['insight_type']}")
    print(f"   Evidence Source: {crystallization_params['evidence_source']}")
    print(f"   Confidence Threshold: {crystallization_params['confidence_threshold']}")
    
    # Step 5: Invoke Knowledge Crystallization System through SPR Bridge
    print("\n[STEP 5] INVOKING KNOWLEDGE CRYSTALLIZATION SYSTEM...")
    print("   SPR ID: 'KnowledgecrystallizationsysteM'")
    print("   Bridge: invoke_spr_action")
    print("   CRITICAL OPERATION: System learning from its own experience")
    
    start_time = datetime.now()
    
    try:
        iar_result = invoke_spr_action(spr_id="KnowledgecrystallizationsysteM", **crystallization_params)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ SPR Bridge execution completed in {execution_time:.3f}s")
        
        # Step 6: Analyze crystallization results
        print("\n[STEP 6] ANALYZING KNOWLEDGE CRYSTALLIZATION RESULTS...")
        print("-" * 50)
        
        # Print full IAR for architectural analysis
        print("FULL IAR RESULT:")
        print(json.dumps(iar_result, indent=2, default=str))
        
        # Extract key validation metrics
        primary_result = iar_result.get('primary_result', {})
        reflection = iar_result.get('reflection', {})
        
        print("\n" + "=" * 50)
        print("PHASE 3.2 TEST CASE 1 VALIDATION SUMMARY")
        print("=" * 50)
        
        # Bridge Status
        bridge_status = reflection.get('status', 'unknown')
        print(f"Bridge Execution Status: {bridge_status}")
        
        # Crystallization Results Validation
        raw_result = primary_result.get('raw_result', {})
        test_passed = True
        
        # Check if crystallization was successful
        crystallization_success = False
        if 'crystallization_successful' in raw_result:
            crystallization_success = raw_result['crystallization_successful']
        elif 'success' in raw_result:
            crystallization_success = raw_result['success']
        elif raw_result.get('error') is None and bridge_status == 'success':
            crystallization_success = True
            
        if crystallization_success:
            print("✅ CRYSTALLIZATION STATUS: SUCCESSFUL")
        else:
            print("❌ CRYSTALLIZATION STATUS: FAILED")
            test_passed = False
        
        # Check for new SPR creation
        if 'new_spr_id' in raw_result:
            created_spr_id = raw_result['new_spr_id']
            print(f"✅ NEW SPR CREATED: {created_spr_id}")
        elif 'spr_id' in raw_result:
            created_spr_id = raw_result['spr_id']
            print(f"✅ SPR PROCESSED: {created_spr_id}")
        else:
            print("❌ NEW SPR ID NOT FOUND IN RESULTS")
            created_spr_id = proposed_spr_id  # Assume it should be our proposed ID
            test_passed = False
        
        # Step 7: CRITICAL VERIFICATION - Check Knowledge Tapestry
        print("\n[STEP 7] CRITICAL VERIFICATION: KNOWLEDGE TAPESTRY EVOLUTION...")
        print("-" * 50)
        
        # Reload and verify the Knowledge Tapestry
        updated_tapestry = load_knowledge_tapestry()
        if updated_tapestry:
            updated_count = len(updated_tapestry)
            print(f"Updated Knowledge Tapestry: {updated_count} SPRs")
            print(f"Change in SPR count: {updated_count - initial_count}")
            
            # Verify the new SPR exists
            exists_after, spr_details = verify_spr_exists(proposed_spr_id)
            if exists_after:
                print(f"🎉 VERIFICATION SUCCESS: SPR '{proposed_spr_id}' EXISTS!")
                print(f"   Definition: {spr_details.get('definition', 'N/A')}")
                print(f"   Category: {spr_details.get('category', 'N/A')}")
                if 'blueprint_details' in spr_details:
                    print(f"   Blueprint: {spr_details['blueprint_details']}")
                
                # Check if it's a meaningful addition (not just a placeholder)
                definition = spr_details.get('definition', '')
                if len(definition) > 50 and 'research' in definition.lower():
                    print("✅ SPR QUALITY: MEANINGFUL DEFINITION")
                else:
                    print("⚠️  SPR QUALITY: DEFINITION MAY BE PLACEHOLDER")
                    
            else:
                print(f"❌ VERIFICATION FAILED: SPR '{proposed_spr_id}' NOT FOUND")
                print(f"   Details: {spr_details}")
                test_passed = False
        else:
            print("❌ FAILED TO RELOAD KNOWLEDGE TAPESTRY")
            test_passed = False
        
        # IAR Compliance Check
        required_iar_fields = ['status', 'confidence', 'potential_issues', 'alignment_check']
        missing_fields = [field for field in required_iar_fields if field not in reflection]
        
        if not missing_fields:
            print("✅ IAR COMPLIANCE: COMPLETE")
        else:
            print(f"❌ IAR COMPLIANCE: MISSING {missing_fields}")
            test_passed = False
        
        # Overall Test Result
        print("\n" + "=" * 50)
        if test_passed and exists_after:
            print("🎉 PHASE 3.2 TEST CASE 1: PASSED")
            print("   Knowledge Crystallization System: OPERATIONAL")
            print("   System Learning Capability: VALIDATED")
            print("   Knowledge Tapestry Evolution: CONFIRMED")
        else:
            print("❌ PHASE 3.2 TEST CASE 1: FAILED")
            print("   Knowledge Crystallization System: REQUIRES ATTENTION")
            if not exists_after:
                print("   CRITICAL ISSUE: Knowledge Tapestry not updated")
        
        print("=" * 50)
        
        return iar_result, test_passed and exists_after
        
    except Exception as e:
        print(f"❌ SPR Bridge execution failed: {str(e)}")
        print(f"   Execution time: {(datetime.now() - start_time).total_seconds():.3f}s")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        return None, False

if __name__ == "__main__":
    result, passed = execute_phase3_test1()
    exit(0 if passed else 1) 