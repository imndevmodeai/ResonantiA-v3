#!/usr/bin/env python3
"""
Demo: CrystallizedObjectiveGenerator Usage
Shows both direct user API usage and ArchE system integration examples.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from crystallized_objective_generator import (
    CrystallizedObjectiveGenerator,
    SPR,
    Mandate,
    CrystallizedObjective
)

# ============================================================================
# Example SPR Bank (Simplified)
# ============================================================================

def create_example_spr_bank() -> List[SPR]:
    """Create a minimal SPR bank for demonstration"""
    return [
        SPR(
            id="spr_data_collection",
            name="DataCollection",
            tags=["data", "collection", "research"],
            signature={"keywords": ["gather", "collect", "research", "fetch", "obtain"]},
            pattern="Collect data from sources X, Y, Z",
            preconditions={"requires_access": True},
            effects={"data_available": True},
            cost=1.0,
            temporal_hint="immediate"
        ),
        SPR(
            id="spr_temporal_analysis",
            name="TemporalAnalysis",
            tags=["temporal", "analysis", "4d_thinking"],
            signature={"keywords": ["temporal", "time", "historical", "future", "trend"]},
            pattern="Analyze temporal patterns and trends",
            preconditions={"requires_time_series": True},
            effects={"temporal_insights": True},
            cost=2.0,
            temporal_hint="ongoing"
        ),
        SPR(
            id="spr_causal_inference",
            name="CausalInference",
            tags=["causal", "inference", "mechanism"],
            signature={"keywords": ["cause", "effect", "causal", "mechanism", "relationship"]},
            pattern="Identify causal relationships between variables",
            preconditions={"requires_data": True},
            effects={"causal_model": True},
            cost=3.0,
            temporal_hint="lagged"
        ),
        SPR(
            id="spr_complex_visioning",
            name="ComplexSystemVisioning",
            tags=["complex_system", "visioning", "abm", "cfp"],
            signature={"keywords": ["complex", "system", "emergent", "visioning", "simulation"]},
            pattern="Model complex system behavior using ABM and CFP",
            preconditions={"requires_complexity": True},
            effects={"system_model": True},
            cost=5.0,
            temporal_hint="long_term"
        ),
        SPR(
            id="spr_workflow_execution",
            name="WorkflowExecution",
            tags=["workflow", "execution", "orchestration"],
            signature={"keywords": ["workflow", "execute", "orchestrate", "process"]},
            pattern="Execute workflow with IAR compliance",
            preconditions={"requires_workflow_definition": True},
            effects={"workflow_completed": True},
            cost=2.0,
            temporal_hint="immediate"
        ),
    ]

# ============================================================================
# Demo 1: Direct User API Usage
# ============================================================================

def demo_direct_usage():
    """Demonstrates direct Python API usage of COG"""
    print("=" * 80)
    print("DEMO 1: Direct User API Usage")
    print("=" * 80)
    
    # Initialize COG
    cog = CrystallizedObjectiveGenerator(
        spr_bank_loader=create_example_spr_bank,
        max_candidates=64
    )
    
    # Define a simple mandate
    mandate = {
        "id": "demo_001",
        "issuer": "user",
        "text": "Analyze the economic impact of implementing Universal Basic Income in region Alpha over the next 5 years",
        "priority": 1,
        "tags": ["economic", "policy", "temporal", "analysis"],
        "domain": "cognitive"
    }
    
    print(f"\n📋 Mandate:")
    print(f"   ID: {mandate['id']}")
    print(f"   Text: {mandate['text']}")
    print(f"   Tags: {', '.join(mandate['tags'])}")
    
    # Generate objective
    print(f"\n⚙️  Generating Crystallized Objective...")
    objective = cog.generate(mandate, mode="deterministic")
    
    # Display results
    print(f"\n✅ Generated Objective:")
    print(f"   Acceptance Score: {objective.acceptance_score:.3f}")
    print(f"   Number of Steps: {len(objective.steps)}")
    print(f"   Temporal Scope: {objective.temporal_scope.granularity}")
    print(f"   Explanations: {len(objective.explanations)}")
    
    print(f"\n📝 Steps:")
    for i, step in enumerate(objective.steps, 1):
        print(f"   {i}. [{step.id}] {step.title}")
        print(f"      {step.description[:80]}...")
        if step.dependencies:
            print(f"      Dependencies: {', '.join(step.dependencies)}")
        if step.estimated_cost > 0:
            print(f"      Estimated Cost: {step.estimated_cost:.2f}")
    
    print(f"\n🔍 Activated SPRs:")
    activated_sprs = objective.metadata.get("activated_sprs", [])
    for spr_info in activated_sprs[:5]:  # Show first 5
        if isinstance(spr_info, dict):
            print(f"   - {spr_info.get('spr_name', 'Unknown')} (weight: {spr_info.get('weight', 0):.3f})")
        else:
            print(f"   - {spr_info}")
    
    return objective

# ============================================================================
# Demo 2: M9 Complex Visioning Mandate
# ============================================================================

def demo_m9_complex_visioning():
    """Demonstrates COG with M9 (Complex System Visioning) mandate"""
    print("\n" + "=" * 80)
    print("DEMO 2: M9 Complex System Visioning Mandate")
    print("=" * 80)
    
    cog = CrystallizedObjectiveGenerator(
        spr_bank_loader=create_example_spr_bank,
        max_candidates=128
    )
    
    # M9 mandate (matches your symbolic chain example)
    m9_mandate = {
        "id": "m9_complex_vision",
        "issuer": "keyholder",
        "text": "Design a conceptual framework and workflow within ResonantiA v3.0 for dynamically adjusting analytical strategies based on real-time IAR feedback loops and predicted task difficulty",
        "priority": 9,
        "tags": ["complex_system", "visioning", "adaptive", "iar", "temporal", "workflow"],
        "domain": "cognitive",
        "constraints": {
            "requires_temporal_reasoning": True,
            "requires_abm": True,
            "requires_cfp": True,
            "requires_iar": True
        }
    }
    
    print(f"\n📋 M9 Mandate:")
    print(f"   ID: {m9_mandate['id']}")
    print(f"   Text: {m9_mandate['text']}")
    print(f"   Priority: {m9_mandate['priority']} (M9)")
    print(f"   Tags: {', '.join(m9_mandate['tags'])}")
    
    print(f"\n⚙️  Generating Crystallized Objective...")
    objective = cog.generate(m9_mandate, mode="deterministic")
    
    print(f"\n✅ Generated Objective:")
    print(f"   Acceptance Score: {objective.acceptance_score:.3f}")
    print(f"   Number of Steps: {len(objective.steps)}")
    
    # Show temporal analysis results
    temporal_results = objective.temporal_scope.analysis_results
    if temporal_results:
        print(f"\n⏱️  Temporal Analysis Results:")
        for subsystem, result in temporal_results.items():
            if result:
                print(f"   {subsystem}: {type(result).__name__}")
    
    print(f"\n📝 Key Steps (first 5):")
    for i, step in enumerate(objective.steps[:5], 1):
        print(f"   {i}. [{step.id}] {step.title}")
        print(f"      {step.description[:100]}...")
    
    return objective

# ============================================================================
# Demo 3: ArchE System Integration Example
# ============================================================================

def demo_arche_integration():
    """Demonstrates how ArchE would integrate COG into its workflow"""
    print("\n" + "=" * 80)
    print("DEMO 3: ArchE System Integration Example")
    print("=" * 80)
    
    # Simulate ArchE's integration pattern
    cog = CrystallizedObjectiveGenerator(
        spr_bank_loader=create_example_spr_bank,
        max_candidates=128
    )
    
    # Simulate a user query coming into ArchE
    user_query = "Analyze the 5-year economic and social consequences of implementing UBI policy Z in region Alpha"
    
    print(f"\n👤 User Query:")
    print(f"   {user_query}")
    
    # Step 1: Convert query to mandate (ArchE's cognitive integration hub would do this)
    mandate = {
        "id": "arche_query_001",
        "issuer": "user",
        "text": user_query,
        "priority": 1,
        "tags": ["economic", "social", "policy", "temporal", "analysis"],
        "domain": "cognitive",
        "context": {
            "query_type": "complex_analysis",
            "requires_temporal": True,
            "requires_modeling": True
        }
    }
    
    # Step 2: Generate objective (COG integration point)
    print(f"\n⚙️  ArchE invoking COG to generate objective...")
    objective = cog.generate(mandate, context=mandate.get("context"))
    
    # Step 3: Convert objective to workflow tasks (simulated)
    print(f"\n🔄 Converting objective to workflow tasks...")
    workflow_tasks = []
    for step in objective.steps:
        task = {
            "id": step.id,
            "name": step.title,
            "action": _map_step_to_action(step),
            "dependencies": step.dependencies,
            "inputs": step.outputs,
            "metadata": step.metadata
        }
        workflow_tasks.append(task)
    
    print(f"   Generated {len(workflow_tasks)} workflow tasks")
    
    # Step 4: Simulate workflow execution (would use IARCompliantWorkflowEngine)
    print(f"\n▶️  Simulating workflow execution...")
    print(f"   Tasks would be executed in dependency order")
    print(f"   Each task would generate IAR-compliant output")
    print(f"   Temporal resonance would be maintained throughout")
    
    # Display workflow structure
    print(f"\n📊 Workflow Structure:")
    for i, task in enumerate(workflow_tasks[:5], 1):
        print(f"   {i}. [{task['id']}] {task['name']}")
        print(f"      Action: {task['action']}")
        if task['dependencies']:
            print(f"      Depends on: {', '.join(task['dependencies'])}")
    
    return objective, workflow_tasks

def _map_step_to_action(step) -> str:
    """Maps a COG step to an ArchE action type"""
    step_lower = step.description.lower()
    if "collect" in step_lower or "gather" in step_lower:
        return "data_collection"
    elif "analyze" in step_lower or "analysis" in step_lower:
        return "run_analysis"
    elif "model" in step_lower or "simulate" in step_lower:
        return "run_cfp"  # or perform_abm
    elif "causal" in step_lower:
        return "perform_causal_inference"
    else:
        return "generate_text_llm"

# ============================================================================
# Demo 4: Objective Comparison (Deterministic vs Stochastic)
# ============================================================================

def demo_objective_comparison():
    """Compares deterministic vs stochastic objective generation"""
    print("\n" + "=" * 80)
    print("DEMO 4: Deterministic vs Stochastic Mode Comparison")
    print("=" * 80)
    
    cog = CrystallizedObjectiveGenerator(
        spr_bank_loader=create_example_spr_bank,
        max_candidates=64
    )
    
    mandate = {
        "id": "comparison_demo",
        "issuer": "user",
        "text": "Analyze market trends for the next quarter",
        "priority": 1,
        "tags": ["market", "trends", "temporal"],
        "domain": "cognitive"
    }
    
    # Generate with deterministic mode
    print(f"\n🔒 Deterministic Mode (same seed → same result):")
    obj_det_1 = cog.generate(mandate, mode="deterministic")
    obj_det_2 = cog.generate(mandate, mode="deterministic")
    
    print(f"   Run 1: {len(obj_det_1.steps)} steps, score: {obj_det_1.acceptance_score:.3f}")
    print(f"   Run 2: {len(obj_det_2.steps)} steps, score: {obj_det_2.acceptance_score:.3f}")
    print(f"   Same result: {len(obj_det_1.steps) == len(obj_det_2.steps)}")
    
    # Generate with stochastic mode
    print(f"\n🎲 Stochastic Mode (different results each run):")
    obj_stoch_1 = cog.generate(mandate, mode="stochastic")
    obj_stoch_2 = cog.generate(mandate, mode="stochastic")
    
    print(f"   Run 1: {len(obj_stoch_1.steps)} steps, score: {obj_stoch_1.acceptance_score:.3f}")
    print(f"   Run 2: {len(obj_stoch_2.steps)} steps, score: {obj_stoch_2.acceptance_score:.3f}")
    print(f"   Same result: {len(obj_stoch_1.steps) == len(obj_stoch_2.steps)}")
    
    # Custom seed for reproducibility
    print(f"\n🌱 Custom Seed (reproducible):")
    mandate_seeded = {**mandate, "seed": 42}
    obj_seed_1 = cog.generate(mandate_seeded)
    obj_seed_2 = cog.generate(mandate_seeded)
    
    print(f"   Run 1: {len(obj_seed_1.steps)} steps, score: {obj_seed_1.acceptance_score:.3f}")
    print(f"   Run 2: {len(obj_seed_2.steps)} steps, score: {obj_seed_2.acceptance_score:.3f}")
    print(f"   Same result: {len(obj_seed_1.steps) == len(obj_seed_2.steps)}")

# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("CrystallizedObjectiveGenerator (COG) Usage Demo")
    print("=" * 80)
    
    try:
        # Demo 1: Direct usage
        demo_direct_usage()
        
        # Demo 2: M9 complex visioning
        demo_m9_complex_visioning()
        
        # Demo 3: ArchE integration
        demo_arche_integration()
        
        # Demo 4: Comparison
        demo_objective_comparison()
        
        print("\n" + "=" * 80)
        print("✅ All demos completed successfully!")
        print("=" * 80)
        print("\nFor more details, see COG_USAGE_GUIDE.md")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

