#!/usr/bin/env python3
"""
Comprehensive System Test Queries
Designed to implicitly trigger ArchE's full capabilities

These queries are designed to naturally exercise:
- Russian Doll layer selection (automatic)
- SPR detection and retrieval
- Cognitive tools (CFP, ABM, Causal Inference, Predictive Modeling)
- Workflow engine execution
- ACO learning and adaptation
- RISE engine for complex queries
- Multiple system layers
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Three_PointO_ArchE"))

# Test queries designed to trigger different capabilities
COMPREHENSIVE_TEST_QUERIES = [
    # ============================================================
    # QUERY SET 1: SPR Detection & Russian Doll Layer Selection
    # ============================================================
    {
        "category": "SPR_Detection_Quick",
        "query": "What is Cognitive resonancE and how does it relate to Temporal resonancE?",
        "expected_tools": ["SPRManager", "Russian Doll retrieval"],
        "expected_layers": ["Zepto", "Atto"],
        "expected_sprs": ["Cognitive resonancE", "Temporal resonancE"],
        "description": "Quick SPR lookup - should trigger Zepto/Atto layers automatically"
    },
    {
        "category": "SPR_Detection_Code",
        "query": "Show me the complete implementation of ActionregistrY including all its methods and how it integrates with the Workflow enginE",
        "expected_tools": ["SPRManager", "Russian Doll retrieval"],
        "expected_layers": ["Narrative"],
        "expected_sprs": ["ActionregistrY", "Workflow enginE"],
        "description": "Code request - should trigger Narrative layer (full code)"
    },
    {
        "category": "SPR_Detection_Workflow",
        "query": "I need to use ComparativE fluxuaL processinG and Agent based modelinG together in a workflow to analyze market dynamics",
        "expected_tools": ["SPRManager", "Workflow Engine", "CFP", "ABM"],
        "expected_layers": ["Micro", "Pico"],
        "expected_sprs": ["ComparativE fluxuaL processinG", "Agent based modelinG"],
        "description": "Workflow usage - should trigger Micro layer (balanced detail)"
    },
    
    # ============================================================
    # QUERY SET 2: Cognitive Tools - CFP (Comparative Fluxual Processing)
    # ============================================================
    {
        "category": "CFP_Analysis",
        "query": "Compare the trajectory of two economic systems: System A starts with high innovation but low stability, System B starts with high stability but low innovation. Model their evolution over 5 years using quantum flux principles",
        "expected_tools": ["CFP Framework", "Quantum Utils", "State Evolution"],
        "expected_workflows": ["cfp_analysis", "trajectory_comparison"],
        "description": "CFP analysis - should trigger CfpframeworK with state evolution"
    },
    {
        "category": "CFP_Complex",
        "query": "Analyze the quantum flux differences between a traditional centralized organization and a decentralized network organization, considering entanglement correlations and spooky flux divergence",
        "expected_tools": ["CFP Framework", "Quantum Utils", "Entanglement Analysis"],
        "expected_sprs": ["Spooky flux divergencE", "Entanglement correlatioN"],
        "description": "Complex CFP - should trigger full quantum-enhanced CFP"
    },
    
    # ============================================================
    # QUERY SET 3: Agent-Based Modeling
    # ============================================================
    {
        "category": "ABM_Simulation",
        "query": "Simulate a population of 1000 agents representing consumers in a market. Each agent has awareness level, adoption threshold, and price sensitivity. Model how a new product launch affects adoption rates over 6 months",
        "expected_tools": ["Agent Based ModelinG", "EmergenceOverTimE"],
        "expected_workflows": ["abm_simulation"],
        "description": "ABM simulation - should trigger AgentBasedModelingTool"
    },
    {
        "category": "ABM_ComplexSystem",
        "query": "Model a complex system where agents have FearLeveL and MoralE attributes. Simulate how panic spreads through the network when a critical event occurs, including coordination behaviors and emergent patterns",
        "expected_tools": ["Agent Based ModelinG", "Complex system visioninG", "HumanFactorModelinG"],
        "expected_sprs": ["FearLeveL", "MoralE", "EmergenceOverTimE"],
        "description": "Complex ABM - should trigger enhanced ABM with human factors"
    },
    
    # ============================================================
    # QUERY SET 4: Causal Inference
    # ============================================================
    {
        "category": "Causal_Analysis",
        "query": "Determine the causal impact of marketing campaign intensity on product adoption, considering competitor pricing as a confounder. Analyze time-lagged effects over the past year",
        "expected_tools": ["Causal inferencE", "CausalLagDetectioN"],
        "expected_workflows": ["causal_analysis"],
        "description": "Causal inference - should trigger CausalInferenceTool with temporal analysis"
    },
    {
        "category": "Causal_Temporal",
        "query": "Discover the temporal causal graph for a system with variables: economic growth, innovation rate, education spending, and technology adoption. Identify lagged causal relationships using PCMCI+",
        "expected_tools": ["Causal inferencE", "CausalLagDetectioN", "Temporal causalitY"],
        "expected_sprs": ["Temporal causalitY", "CausalLagDetectioN"],
        "description": "Temporal causal discovery - should trigger advanced causal analysis"
    },
    
    # ============================================================
    # QUERY SET 5: Predictive Modeling
    # ============================================================
    {
        "category": "Predictive_Forecast",
        "query": "Forecast the next 5 years of economic indicators (GDP growth, inflation, unemployment) for region Alpha based on historical data. Provide confidence intervals and model performance metrics",
        "expected_tools": ["PredictivE modelinG tooL", "FutureStateAnalysiS"],
        "expected_workflows": ["predictive_forecasting"],
        "description": "Predictive modeling - should trigger PredictivE ModelinG TooL"
    },
    {
        "category": "Predictive_TimeSeries",
        "query": "Build time series models for stock market volatility prediction. Use VAR models for multivariate analysis and Prophet for trend decomposition. Compare forecast accuracy",
        "expected_tools": ["PredictivE modelinG tooL", "TemporalDynamiX"],
        "description": "Time series forecasting - should trigger multiple predictive models"
    },
    
    # ============================================================
    # QUERY SET 6: Integrated Analysis (Causal + ABM + CFP)
    # ============================================================
    {
        "category": "Integrated_Causal_ABM",
        "query": "First, determine the lagged causal impact of policy changes on social outcomes. Then use those causal insights to parameterize an agent-based model simulating how the policy affects different population segments over 2 years. Finally, compare the baseline vs policy scenarios using CFP",
        "expected_tools": ["Causal inferencE", "Agent Based ModelinG", "CFP Framework"],
        "expected_workflows": ["causal_abm_integration"],
        "expected_sprs": ["Causal abm integratioN", "TrajectoryComparisoN"],
        "description": "Full integration - Causal → ABM → CFP pipeline"
    },
    {
        "category": "Integrated_ComplexSystem",
        "query": "Perform a comprehensive Complex system visioninG analysis: identify causal mechanisms, simulate emergent behaviors with ABM, and compare potential future trajectories using CFP. Include human factor modeling and scenario realism assessment",
        "expected_tools": ["Complex system visioninG", "Causal inferencE", "ABM", "CFP", "ScenarioRealismAssessmenT"],
        "expected_sprs": ["Complex system visioninG", "HumanFactorModelinG"],
        "description": "Full ComplexSystemVisioninG - all tools integrated"
    },
    
    # ============================================================
    # QUERY SET 7: RISE Engine & Tesla Visioning
    # ============================================================
    {
        "category": "RISE_Strategic",
        "query": "Design a strategic framework for dynamically adjusting analytical strategies based on real-time IAR feedback loops and predicted task difficulty. This requires novel design and creative problem-solving",
        "expected_tools": ["RISE Engine", "Tesla visioning workfloW"],
        "expected_workflows": ["tesla_visioning_workflow"],
        "expected_sprs": ["Tesla visioning workfloW", "Resonant_Insight_And_Strategy_Engine"],
        "description": "Strategic design - should trigger RISE and Tesla Visioning"
    },
    {
        "category": "RISE_Complex",
        "query": "Create a novel workflow that combines Sparse priming representationS, Metacognitive shifT, and Synergistic intent resonance cyclE to enable autonomous system evolution",
        "expected_tools": ["RISE Engine", "SIRC", "Metacognitive shifT"],
        "expected_sprs": ["Sparse priming representationS", "Metacognitive shifT", "Synergistic intent resonance cyclE"],
        "description": "Complex design - should trigger RISE with multiple SPRs"
    },
    
    # ============================================================
    # QUERY SET 8: Workflow Engine & Process Blueprints
    # ============================================================
    {
        "category": "Workflow_Execution",
        "query": "Execute the spr_cognitive_unfolding_workflow for the query: 'Explain how IntegratedActionReflectioN enables Metacognitive shifT'",
        "expected_tools": ["Workflow enginE", "IARCompliantWorkflowEngine"],
        "expected_workflows": ["spr_cognitive_unfolding_workflow"],
        "expected_sprs": ["IntegratedActionReflectioN", "Metacognitive shifT"],
        "description": "Workflow execution - should trigger workflow engine"
    },
    {
        "category": "Workflow_Phasegate",
        "query": "Run a workflow that uses PhasegateS to check IAR confidence scores before proceeding. If confidence drops below 0.8, trigger a Metacognitive shifT",
        "expected_tools": ["Workflow enginE", "PhasegateS", "Metacognitive shifT"],
        "expected_sprs": ["PhasegateS", "Metacognitive shifT"],
        "description": "Phasegate workflow - should trigger conditional execution"
    },
    
    # ============================================================
    # QUERY SET 9: Knowledge Management & Learning
    # ============================================================
    {
        "category": "Knowledge_Solidification",
        "query": "I've learned that PCMCI+ is a temporal causal discovery algorithm suitable for high-dimensional time series. Create an SPR for this knowledge and integrate it into the Knowledge tapestrY",
        "expected_tools": ["Insight solidificatioN", "SPRManageR"],
        "expected_workflows": ["insight_solidification"],
        "expected_sprs": ["Insight solidificatioN", "Knowledge tapestrY"],
        "description": "Knowledge solidification - should trigger InsightSolidificatioN workflow"
    },
    {
        "category": "Knowledge_Pattern",
        "query": "Analyze the ThoughtTraiL for recurring patterns. If you find a successful pattern for handling 'code generation requests', crystallize it into a reusable workflow template",
        "expected_tools": ["Pattern crystallizatioN", "ThoughtTraiL"],
        "expected_sprs": ["Pattern crystallizatioN", "ThoughtTraiL"],
        "description": "Pattern crystallization - should trigger pattern learning"
    },
    
    # ============================================================
    # QUERY SET 10: Meta-Cognitive & Self-Correction
    # ============================================================
    {
        "category": "Metacognitive_Correction",
        "query": "I noticed that in a previous analysis, the CFP comparison used placeholder evolution instead of actual state evolution. This caused incorrect trajectory predictions. Please correct this using Metacognitive shifT",
        "expected_tools": ["Metacognitive shifT", "CFP Framework"],
        "expected_sprs": ["Metacognitive shifT", "ComparativE fluxuaL processinG"],
        "description": "Metacognitive correction - should trigger error correction workflow"
    },
    {
        "category": "SIRC_Alignment",
        "query": "I want to align ArchE's capabilities with a new strategic objective: autonomous code generation with safety validation. Use SIRC to plan the necessary adaptations",
        "expected_tools": ["Synergistic intent resonance cyclE", "SIRC"],
        "expected_workflows": ["sirc_workflow"],
        "expected_sprs": ["Synergistic intent resonance cyclE"],
        "description": "SIRC alignment - should trigger proactive intent alignment"
    },
    
    # ============================================================
    # QUERY SET 11: Temporal Reasoning & 4D Thinking
    # ============================================================
    {
        "category": "Temporal_Analysis",
        "query": "Analyze the historical evolution of the Workflow enginE from its initial design to current implementation. Then project how it might evolve over the next 2 years based on current patterns",
        "expected_tools": ["Temporal reasoninG", "4d thinkinG", "HistoricalContextualizatioN", "FutureStateAnalysiS"],
        "expected_sprs": ["Temporal resonancE", "4d thinkinG", "HistoricalContextualizatioN"],
        "description": "Temporal analysis - should trigger 4D thinking capabilities"
    },
    {
        "category": "Temporal_Causal",
        "query": "Identify the temporal causal relationships in a system where policy changes (X) affect economic outcomes (Y) with a 6-month lag, while external factors (Z) act as confounders. Model the causal lag detection",
        "expected_tools": ["Causal inferencE", "CausalLagDetectioN", "TemporalDynamiX"],
        "description": "Temporal causal - should trigger lagged causal analysis"
    },
    
    # ============================================================
    # QUERY SET 12: Multi-Modal & Advanced Capabilities
    # ============================================================
    {
        "category": "Code_Execution",
        "query": "Write and execute Python code to analyze a dataset of 10,000 records. Calculate statistical summaries, perform correlation analysis, and generate visualizations. Use the Code executoR safely",
        "expected_tools": ["Code executoR", "Data CollectioN"],
        "description": "Code execution - should trigger Code executoR with sandboxing"
    },
    {
        "category": "Data_Collection",
        "query": "Collect data from multiple sources: fetch the latest economic indicators from a public API, read historical data from a CSV file, and extract information from a PDF report. Integrate all sources",
        "expected_tools": ["Data CollectioN", "Grounded Analysis"],
        "description": "Multi-source data collection - should trigger data gathering tools"
    },
    
    # ============================================================
    # QUERY SET 13: Complex Multi-Tool Integration
    # ============================================================
    {
        "category": "Complex_Integration",
        "query": "Perform a complete analysis: (1) Use Causal inferencE to identify key drivers, (2) Build predictive models for future states, (3) Simulate scenarios with ABM, (4) Compare trajectories with CFP, (5) Assess realism with ScenarioRealismAssessmenT, (6) Generate insights using RISE",
        "expected_tools": ["Causal inferencE", "PredictivE modelinG tooL", "ABM", "CFP", "RISE Engine", "ScenarioRealismAssessmenT"],
        "description": "Full tool integration - should trigger all major cognitive tools"
    },
    {
        "category": "Complex_Strategic",
        "query": "Design a comprehensive strategy for a new product launch: analyze market dynamics with CFP, model consumer behavior with ABM, identify key success factors with Causal inferencE, forecast outcomes with Predictive Modeling, and create an implementation plan using Tesla Visioning",
        "expected_tools": ["CFP", "ABM", "Causal inferencE", "PredictivE modelinG tooL", "Tesla visioning workfloW"],
        "description": "Strategic planning - should trigger multiple tools in sequence"
    },
    
    # ============================================================
    # QUERY SET 14: ACO Learning & Adaptation
    # ============================================================
    {
        "category": "ACO_Learning",
        "query": "What is ActioncontexT? Then show me its implementation. Then use it in a workflow example",
        "expected_tools": ["ACO", "SPRManager", "Layer Learning"],
        "expected_behavior": "ACO should learn: quick question → Zepto, code request → Narrative, workflow → Micro",
        "description": "ACO learning - should demonstrate layer selection learning"
    },
    {
        "category": "ACO_Adaptation",
        "query": "I've noticed that when I ask 'what is [SPR]?' you always give me too much detail. Can you learn to give shorter answers for quick questions?",
        "expected_tools": ["ACO", "Layer Learning", "Metacognitive shifT"],
        "expected_behavior": "ACO should adapt layer selection based on feedback",
        "description": "ACO adaptation - should demonstrate learning from feedback"
    },
    
    # ============================================================
    # QUERY SET 15: Edge Cases & Stress Tests
    # ============================================================
    {
        "category": "Edge_Multiple_SPRs",
        "query": "Explain how Cognitive resonancE, Temporal resonancE, Implementation resonancE, and Execution paradoX all relate to each other in the ResonantiA Protocol",
        "expected_tools": ["SPRManager", "Russian Doll retrieval"],
        "expected_sprs": ["Cognitive resonancE", "Temporal resonancE", "Implementation resonancE", "Execution paradoX"],
        "expected_layers": ["Micro", "Concise"],  # Multiple SPRs - balanced detail
        "description": "Multiple SPRs - should handle multiple simultaneous retrievals"
    },
    {
        "category": "Edge_Ambiguous",
        "query": "I need help with something related to workflows and actions and context",
        "expected_tools": ["ACO", "Fuzzy Intent Mapping", "SPR Detection"],
        "expected_behavior": "Should detect multiple potential SPRs and use fuzzy matching",
        "description": "Ambiguous query - should trigger fuzzy SPR detection"
    },
]


def run_comprehensive_test():
    """Run comprehensive system test with all queries"""
    
    print("=" * 80)
    print("COMPREHENSIVE ARCH E SYSTEM TEST")
    print("Testing Russian Doll Layers, Cognitive Tools, Workflows, and ACO Learning")
    print("=" * 80)
    print()
    
    results = []
    
    for i, test_case in enumerate(COMPREHENSIVE_TEST_QUERIES, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(COMPREHENSIVE_TEST_QUERIES)}: {test_case['category']}")
        print(f"{'='*80}")
        print(f"Query: {test_case['query']}")
        print(f"Description: {test_case['description']}")
        print(f"Expected Tools: {', '.join(test_case.get('expected_tools', []))}")
        print(f"Expected SPRs: {', '.join(test_case.get('expected_sprs', []))}")
        print(f"Expected Layers: {', '.join(test_case.get('expected_layers', ['Auto']))}")
        print()
        
        # Here we would actually execute the query through ArchE
        # For now, we'll simulate and document what should happen
        result = {
            "test_id": i,
            "category": test_case['category'],
            "query": test_case['query'],
            "timestamp": datetime.now().isoformat(),
            "expected_activation": {
                "tools": test_case.get('expected_tools', []),
                "sprs": test_case.get('expected_sprs', []),
                "layers": test_case.get('expected_layers', ['Auto']),
                "workflows": test_case.get('expected_workflows', [])
            }
        }
        
        results.append(result)
        
        print(f"✅ Test case documented - Ready for execution")
        print()
    
    # Save results
    results_file = project_root / "comprehensive_test_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"TEST SUITE COMPLETE")
    print(f"{'='*80}")
    print(f"Total Test Cases: {len(COMPREHENSIVE_TEST_QUERIES)}")
    print(f"Categories: {len(set(t['category'] for t in COMPREHENSIVE_TEST_QUERIES))}")
    print(f"Results saved to: {results_file}")
    print()
    print("Next: Execute these queries through ArchE to test actual system behavior")
    
    return results


if __name__ == "__main__":
    results = run_comprehensive_test()
    print(f"\n✅ Generated {len(results)} test cases")

