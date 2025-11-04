#!/usr/bin/env python3
"""
Re-run the last RISE query with enhanced RISE-SRCS capabilities.
Last query: "Validate and optimize the LLM provider strategy through complete RISE process"
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.spr_manager import SPRManager
from Three_PointO_ArchE.thought_trail import ThoughtTrail

def main():
    """Run the last RISE query with enhanced capabilities"""
    
    # Last RISE query from RISE_ANALYSIS_LLM_PROVIDER_STRATEGY.md
    problem_description = """Validate and optimize the LLM provider strategy through complete RISE process. 
    Ensure the strategy is robust, cost-effective, scalable, and aligned with ArchE's mission.
    
    Focus areas:
    - Multi-provider architecture (Google, Groq, Cursor ArchE)
    - Cost optimization and provider selection algorithms
    - Failover and reliability mechanisms
    - Performance benchmarking
    - Integration complexity and maintainability"""
    
    print("🚀 Re-running Last RISE Query with Enhanced RISE-SRCS")
    print(f"📋 Problem: {problem_description[:100]}...")
    print("=" * 80)
    
    try:
        # Initialize components
        workflows_dir = project_root / "workflows"
        spr_manager = SPRManager(str(project_root / "knowledge_graph" / "spr_definitions_tv.json"))
        workflow_engine = IARCompliantWorkflowEngine(str(workflows_dir))
        thought_trail = ThoughtTrail()
        
        # Initialize RISE Orchestrator (with RISE-SRCS enabled)
        rise_orchestrator = RISE_Orchestrator(
            workflows_dir=str(workflows_dir),
            spr_manager=spr_manager,
            workflow_engine=workflow_engine
        )
        
        # Set thought trail
        rise_orchestrator.thought_trail = thought_trail
        
        print("✅ RISE Orchestrator initialized with RISE-SRCS capabilities")
        print("   - CodebaseArchaeologist: ENABLED")
        print("   - Codebase Pattern Search: ENABLED")
        print("   - Hybrid Synthesis: ENABLED")
        print("   - Iterative Looping: ENABLED")
        print()
        
        # Execute RISE query with provider selection
        # Default for this script: Use Cursor ArchE (overrides system default for this run)
        # System default remains Google - can be overridden via ARCHE_LLM_PROVIDER env var
        import os
        provider_choice = os.getenv("ARCHE_LLM_PROVIDER", "cursor")  # This script defaults to cursor
        model_choice = "cursor-arche-v1" if provider_choice == "cursor" else None
        
        print(f"🔄 Executing RISE workflow with provider: {provider_choice}")
        print(f"   Model: {model_choice or 'provider default'}")
        
        results = rise_orchestrator.process_query(
            problem_description=problem_description,
            context={"provider": provider_choice},  # Pass provider in context
            model=model_choice  # Pass model if specified
        )
        
        # Display results
        print("\n" + "=" * 80)
        print("✅ RISE Execution Complete")
        print("=" * 80)
        print(f"Session ID: {results.get('session_id')}")
        print(f"Status: {results.get('execution_status')}")
        print(f"Duration: {results.get('total_duration', 0):.2f}s")
        
        # Check for codebase synthesis results
        phase_b_results = results.get('phase_results', {}).get('phase_b', {})
        fused_dossier = phase_b_results.get('fused_strategic_dossier', {})
        codebase_synthesis = fused_dossier.get('codebase_synthesis', {})
        
        if codebase_synthesis:
            print("\n🏛️ Codebase Synthesis Results:")
            print(f"   Novel Combinations: {len(codebase_synthesis.get('novel_combinations', []))}")
            print(f"   Implementation Suggestions: {len(codebase_synthesis.get('implementation_suggestions', []))}")
            print(f"   Synthesis Confidence: {codebase_synthesis.get('confidence', 0.0):.2f}")
        
        # Check for iterative loops
        if results.get('execution_metrics', {}).get('iterative_loops', 0) > 0:
            print(f"\n🔄 Iterative Loops Executed: {results.get('execution_metrics', {}).get('iterative_loops', 0)}")
        
        # Save results
        output_file = project_root / f"RISE_REEXECUTION_{results.get('session_id')}.json"
        import json
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {output_file}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error executing RISE: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()

