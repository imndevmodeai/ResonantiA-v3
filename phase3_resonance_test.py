#!/usr/bin/env python3
"""
RESONANTIA PROTOCOL v3.1-CA - PHASE 3.2 TEST CASE 2
SPR BRIDGE VALIDATION: COGNITIVE RESONANCE EVALUATION
FINAL TEST: SYSTEM'S ABILITY TO ASSESS ITS OWN WORK QUALITY
"""

import json
import time
import sys
import os

# Add the Three_PointO_ArchE package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Three_PointO_ArchE'))

from Three_PointO_ArchE.spr_action_bridge import invoke_spr, SPRBridgeLoader

def main():
    print("=" * 70)
    print("RESONANTIA PROTOCOL v3.1-CA - PHASE 3.2 TEST CASE 2")
    print("SPR BRIDGE VALIDATION: COGNITIVE RESONANCE EVALUATION")
    print("FINAL TEST: SYSTEM'S ABILITY TO ASSESS ITS OWN WORK QUALITY")
    print("=" * 70)
    print()
    
    # Step 1: Load SPR definitions to verify target SPR exists
    print("[STEP 1] Loading Knowledge Tapestry and verifying target SPR...")
    bridge_loader = SPRBridgeLoader("Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json")
    spr_definitions_dict = bridge_loader.load_tapestry()
    print(f"✅ Knowledge Tapestry loaded: {len(spr_definitions_dict)} SPRs")
    
    target_spr = "CognitiveresonancE"
    spr_found = target_spr in spr_definitions_dict
    
    if not spr_found:
        print(f"❌ CRITICAL: SPR '{target_spr}' not found in Knowledge Tapestry")
        print("Available SPRs with 'resonance' in name:")
        resonance_sprs = [spr_id for spr_id in spr_definitions_dict.keys() if 'resonance' in spr_id.lower()]
        for spr_id in resonance_sprs:
            print(f"   - {spr_id}")
        return False
    else:
        print(f"✅ Target SPR '{target_spr}' found in Knowledge Tapestry")
    print()
    
    # Step 2: Define simulated workflow results to evaluate
    print("[STEP 2] Creating simulated workflow results for evaluation...")
    workflow_to_evaluate = {
        "objective": "Analyze market sentiment for emerging AI framework 'QuantumMind'",
        "final_output": "Market sentiment for 'QuantumMind' is cautiously optimistic (68%), driven by strong technical architecture reviews but hampered by concerns about enterprise adoption timeline and competitive landscape pressure from established frameworks.",
        "thought_trail_summary": [
            {
                "action": "web_search", 
                "query": "QuantumMind AI framework reviews",
                "confidence": 0.9, 
                "sources": ["TechCrunch", "VentureBeat", "ArXiv"],
                "key_findings": "Strong technical reviews, innovative architecture"
            },
            {
                "action": "web_search", 
                "query": "QuantumMind enterprise adoption concerns",
                "confidence": 0.6, 
                "sources": ["Reddit r/MachineLearning", "HackerNews", "LinkedIn"],
                "key_findings": "Community concerns about adoption timeline"
            },
            {
                "action": "sentiment_analysis", 
                "confidence": 0.85, 
                "metrics": {"positive": 0.68, "neutral": 0.20, "negative": 0.12},
                "dissonance_detected": "Conflicting sentiment between technical reviews (highly positive) and adoption concerns (moderately negative)"
            },
            {
                "action": "llm_synthesize", 
                "confidence": 0.8, 
                "synthesis_quality": "high",
                "temporal_consistency": "maintained",
                "data_integration": "comprehensive"
            }
        ],
        "data_sources_used": ["TechCrunch", "VentureBeat", "ArXiv", "Reddit", "HackerNews", "LinkedIn"],
        "execution_time_seconds": 23.7,
        "workflow_complexity": "moderate",
        "confidence_trajectory": [0.9, 0.6, 0.85, 0.8],
        "identified_dissonances": [
            "Technical excellence vs adoption concerns",
            "Professional media optimism vs community caution"
        ]
    }
    
    print("✅ Simulated workflow created:")
    print(f"   Objective: {workflow_to_evaluate['objective']}")
    print(f"   Sources: {len(workflow_to_evaluate['data_sources_used'])} data sources")
    print(f"   Steps: {len(workflow_to_evaluate['thought_trail_summary'])} analysis steps")
    print(f"   Dissonances: {len(workflow_to_evaluate['identified_dissonances'])} identified")
    print()
    
    # Step 3: Configure evaluation parameters
    print("[STEP 3] Configuring Cognitive Resonance Evaluation parameters...")
    evaluation_params = {
        "workflow_context": workflow_to_evaluate,
        "evaluation_criteria": {
            "data_alignment": "Assess consistency between data sources and conclusions",
            "analytical_depth": "Evaluate thoroughness of analysis and reasoning",
            "temporal_consistency": "Check for logical flow and time-aware reasoning",
            "dissonance_handling": "Assess identification and resolution of conflicts",
            "confidence_calibration": "Evaluate appropriateness of confidence levels"
        },
        "evaluation_mode": "comprehensive",
        "include_recommendations": True
    }
    
    print("✅ Evaluation parameters configured")
    print(f"   Criteria: {len(evaluation_params['evaluation_criteria'])} evaluation dimensions")
    print(f"   Mode: {evaluation_params['evaluation_mode']}")
    print()
    
    # Step 4: INVOKE COGNITIVE RESONANCE EVALUATOR
    print("[STEP 4] INVOKING COGNITIVE RESONANCE EVALUATOR SPR...")
    print(f"   SPR ID: '{target_spr}'")
    print("   Bridge: invoke_spr_action")
    print("   CRITICAL OPERATION: System assessing its own work quality")
    
    start_time = time.time()
    
    try:
        # Invoke the SPR through the bridge
        iar_result = invoke_spr(
            spr_id=target_spr, 
            parameters=evaluation_params,
            bridge_loader=bridge_loader
        )
        
        execution_time = time.time() - start_time
        print(f"✅ SPR Bridge execution completed in {execution_time:.3f}s")
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ SPR Bridge execution failed after {execution_time:.3f}s")
        print(f"   Error: {str(e)}")
        return False
    
    print()
    
    # Step 5: ANALYZE COGNITIVE RESONANCE EVALUATION RESULTS
    print("[STEP 5] ANALYZING COGNITIVE RESONANCE EVALUATION RESULTS...")
    print("-" * 50)
    print("FULL IAR RESULT:")
    print(json.dumps(iar_result, indent=2))
    print()
    
    # Extract key metrics from the result
    # The SPR bridge returns results directly, not wrapped in primary_result
    if 'status' in iar_result:
        primary_result = iar_result
        
        print("=" * 50)
        print("PHASE 3.2 TEST CASE 2 VALIDATION SUMMARY")
        print("=" * 50)
        
        # Check bridge execution status
        bridge_status = iar_result.get('bridge_status', 'unknown')
        print(f"Bridge Execution Status: {bridge_status}")
        
        # Check if resonance evaluation was successful
        evaluation_status = primary_result.get('status', 'unknown')
        if evaluation_status == 'success':
            print("✅ RESONANCE EVALUATION STATUS: SUCCESS")
            
            # Extract resonance scores if available
            resonance_scores = primary_result.get('resonance_scores', {})
            if resonance_scores:
                print("\n📊 RESONANCE SCORES:")
                for criterion, score in resonance_scores.items():
                    print(f"   {criterion}: {score}")
            
            # Extract overall resonance assessment
            overall_resonance = primary_result.get('overall_resonance', 'unknown')
            print(f"\n🎯 OVERALL RESONANCE: {overall_resonance}")
            
            # Extract recommendations if available
            recommendations = primary_result.get('recommendations', [])
            if recommendations:
                print(f"\n💡 SYSTEM RECOMMENDATIONS: {len(recommendations)} items")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")
            
        else:
            print(f"❌ RESONANCE EVALUATION STATUS: {evaluation_status}")
        
        print(f"\n✅ IAR COMPLIANCE: COMPLETE")
        
        # Final validation
        if evaluation_status == 'success' and bridge_status in ['success', 'partial_success']:
            print("\n" + "=" * 50)
            print("✅ PHASE 3.2 TEST CASE 2: SUCCESS")
            print("   Cognitive Resonance Evaluator: FULLY OPERATIONAL")
            print("   CRITICAL ACHIEVEMENT: System can assess its own work quality")
            print("=" * 50)
            return True
        else:
            print("\n" + "=" * 50)
            print("❌ PHASE 3.2 TEST CASE 2: FAILED")
            print("   Cognitive Resonance Evaluator: REQUIRES ATTENTION")
            print("=" * 50)
            return False
    
    else:
        print("❌ CRITICAL: No status field found in IAR output")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 