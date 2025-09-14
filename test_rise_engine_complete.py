#!/usr/bin/env python3
"""
Comprehensive Test Script for RISE Engine with Strategy Fusion Workflow
Tests the complete integration of CFP, ABM, Causal Inference, and Specialist Agent tools.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.action_registry import main_action_registry

def test_action_registry():
    """Test that all required actions are properly registered."""
    print("🔍 Testing Action Registry...")
    
    required_actions = [
        "perform_causal_inference",
        "perform_abm", 
        "run_cfp",
        "invoke_specialist_agent",
        "generate_text_llm",
        "display_output"
    ]
    
    missing_actions = []
    for action in required_actions:
        if not main_action_registry.get_action(action):
            missing_actions.append(action)
    
    if missing_actions:
        print(f"❌ Missing actions: {missing_actions}")
        return False
    else:
        print("✅ All required actions are registered")
        return True

def test_strategy_fusion_workflow():
    """Test the strategy_fusion workflow with sample data."""
    print("\n🎯 Testing Strategy Fusion Workflow...")
    
    # Load the workflow
    workflow_path = "workflows/strategy_fusion.json"
    if not os.path.exists(workflow_path):
        # Try alternative paths if running from subdirectory
        alt_paths = [
            "../workflows/strategy_fusion.json",
            "strategy_fusion.json"
        ]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                workflow_path = alt_path
                break
        else:
        print(f"❌ Workflow file not found: {workflow_path}")
            print(f"   Tried paths: {['workflows/strategy_fusion.json'] + alt_paths}")
        return False
    
    with open(workflow_path, 'r') as f:
        workflow_config = json.load(f)
    
    print(f"✅ Workflow loaded: {workflow_config.get('name', 'Unknown')}")
    
    # Create sample input data
    sample_inputs = {
        "problem_description": "Analyze the strategic implications of implementing a new AI-driven customer service system in a traditional retail company",
        "specialized_agent": {
            "domain": "retail_technology",
            "expertise": ["digital_transformation", "customer_experience", "change_management"],
            "perspective": "technology_optimist",
            "experience_level": "senior_executive"
        },
        "knowledge_base": {
            "industry_trends": "AI adoption in retail is accelerating",
            "success_factors": "Change management and employee training are critical",
            "risk_factors": "Customer resistance and technical complexity"
        },
        "initial_context": {
            "case_event_timeline": [
                {"date": "2024-01", "event": "Initial AI system proposal"},
                {"date": "2024-03", "event": "Stakeholder feedback collection"},
                {"date": "2024-06", "event": "Pilot program launch"}
            ],
            "core_hypothesis": "AI-driven customer service will improve customer satisfaction by 25% while reducing operational costs by 15%",
            "narrative_a": "Successful implementation with strong change management",
            "narrative_b": "Implementation failure due to resistance and poor planning",
            "scenario_a_config": {
                "change_management": "comprehensive",
                "training_budget": "adequate",
                "stakeholder_support": "high"
            },
            "scenario_b_config": {
                "change_management": "minimal",
                "training_budget": "insufficient", 
                "stakeholder_support": "low"
            }
        }
    }
    
    print("✅ Sample inputs prepared")
    
    # Test workflow execution
    try:
        engine = IARCompliantWorkflowEngine()
        result = engine.execute_workflow(workflow_config, sample_inputs)
        
        # Check if workflow completed successfully
        if result.get("workflow_status") == "Completed Successfully":
            print("✅ Strategy Fusion workflow executed successfully")
            print(f"📊 Tasks completed: {list(result.get('tasks', {}).keys())}")
            return True
        else:
            print(f"❌ Workflow execution failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Workflow execution error: {e}")
        return False

def test_parallel_pathways():
    """Test that all parallel pathways are properly configured."""
    print("\n🔄 Testing Parallel Pathways...")
    
    # Try to find the workflow file
    workflow_path = "workflows/strategy_fusion.json"
    if not os.path.exists(workflow_path):
        alt_paths = [
            "../workflows/strategy_fusion.json",
            "strategy_fusion.json"
        ]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                workflow_path = alt_path
                break
        else:
            print(f"❌ Workflow file not found for parallel pathways test")
            return False
    
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    tasks = workflow.get("tasks", {})
    
    # Check for parallel pathway tasks
    pathway_tasks = [
        "pathway_causal_analysis",
        "pathway_simulation_abm", 
        "pathway_comparative_cfp",
        "pathway_specialist_consultation"
    ]
    
    missing_pathways = []
    for pathway in pathway_tasks:
        if pathway not in tasks:
            missing_pathways.append(pathway)
    
    if missing_pathways:
        print(f"❌ Missing pathway tasks: {missing_pathways}")
        return False
    
    # Check that all pathways depend on initiate_fusion
    for pathway in pathway_tasks:
        dependencies = tasks[pathway].get("dependencies", [])
        if "initiate_fusion" not in dependencies:
            print(f"❌ Pathway {pathway} missing dependency on initiate_fusion")
            return False
    
    # Check that synthesis depends on all pathways
    synthesis_deps = tasks["synthesize_fused_dossier"].get("dependencies", [])
    for pathway in pathway_tasks:
        if pathway not in synthesis_deps:
            print(f"❌ Synthesis missing dependency on {pathway}")
            return False
    
    print("✅ All parallel pathways properly configured")
    return True

def test_advanced_tools_integration():
    """Test that advanced cognitive tools are properly integrated."""
    print("\n🧠 Testing Advanced Tools Integration...")
    
    # Test Causal Inference Tool
    try:
        causal_action = main_action_registry.get_action("perform_causal_inference")
        if causal_action:
            print("✅ Causal Inference tool available")
        else:
            print("❌ Causal Inference tool not found")
            return False
    except Exception as e:
        print(f"❌ Causal Inference tool error: {e}")
        return False
    
    # Test ABM Tool
    try:
        abm_action = main_action_registry.get_action("perform_abm")
        if abm_action:
            print("✅ Agent-Based Modeling tool available")
        else:
            print("❌ Agent-Based Modeling tool not found")
            return False
    except Exception as e:
        print(f"❌ ABM tool error: {e}")
        return False
    
    # Test CFP Tool
    try:
        cfp_action = main_action_registry.get_action("run_cfp")
        if cfp_action:
            print("✅ Comparative Fluxual Processing tool available")
        else:
            print("❌ CFP tool not found")
            return False
    except Exception as e:
        print(f"❌ CFP tool error: {e}")
        return False
    
    # Test Specialist Agent Tool
    try:
        specialist_action = main_action_registry.get_action("invoke_specialist_agent")
        if specialist_action:
            print("✅ Specialist Agent tool available")
        else:
            print("❌ Specialist Agent tool not found")
            return False
    except Exception as e:
        print(f"❌ Specialist Agent tool error: {e}")
        return False
    
    return True

def test_strategic_model():
    """Test the strategic interaction model."""
    print("\n🎲 Testing Strategic Interaction Model...")
    
    try:
        from models.strategic_interaction_model import StrategicInteractionModel
        
        # Create a simple test configuration
        config = {
            "agent_types": ["stakeholder", "decision_maker", "influencer", "resistor"],
            "num_agents": 20
        }
        
        model = StrategicInteractionModel(config)
        print(f"✅ Model created with {len(model.agents)} agents")
        
        # Run a short simulation
        result = model.run_simulation(10)
        print(f"✅ Simulation completed: {result['summary_metrics']['total_steps']} steps")
        
        # Check emergent metrics
        metrics = result['summary_metrics']
        print(f"📊 Emergent Metrics:")
        print(f"   - Average Consensus: {metrics.get('avg_consensus', 0):.3f}")
        print(f"   - Average Conflict: {metrics.get('avg_conflict', 0):.3f}")
        print(f"   - Average Efficiency: {metrics.get('avg_efficiency', 0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategic model error: {e}")
        return False

def main():
    """Run all tests or execute specific workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description='RISE Engine Test Suite and API')
    parser.add_argument('--workflow', type=str, help='Execute specific workflow')
    parser.add_argument('--session', type=str, help='Session ID for API calls')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    
    args = parser.parse_args()
    
    # If specific workflow requested, execute it
    if args.workflow:
        print(f"🚀 Executing RISE Engine workflow: {args.workflow}")
        print("=" * 50)
        
        try:
            # Load workflow
            engine = IARCompliantWorkflowEngine()
            workflow_config = engine.load_workflow(f"{args.workflow}.json")
            
            # Prepare sample inputs
            sample_inputs = {
                "problem_description": "Strategic analysis request from NextJS chat interface",
                "session_id": args.session or "default_session",
                "timestamp": "2025-07-26T08:00:00Z",
                "analysis_type": "chat_integration"
            }
            
            # Execute workflow
            result = engine.execute_workflow(workflow_config, sample_inputs)
            
            if result.get("workflow_status") == "Completed Successfully":
                print("✅ Workflow executed successfully")
                print(f"📊 Tasks completed: {list(result.get('tasks', {}).keys())}")
                return True
            else:
                print(f"❌ Workflow execution failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Workflow execution error: {e}")
            return False
    
    # Run test suite
    print("🚀 RISE Engine Complete Test Suite")
    print("=" * 50)
    
    tests = [
        ("Action Registry", test_action_registry),
        ("Strategy Fusion Workflow", test_strategy_fusion_workflow),
        ("Parallel Pathways", test_parallel_pathways),
        ("Advanced Tools Integration", test_advanced_tools_integration),
        ("Strategic Model", test_strategic_model)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RISE Engine is ready for production use.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 