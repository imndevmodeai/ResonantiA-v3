#!/usr/bin/env python3
"""
Test dynamic workflow and action discovery
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_workflow_discovery():
    """Test that we can discover workflows and actions"""
    from Three_PointO_ArchE.workflow_action_discovery import WorkflowActionDiscovery
    from Three_PointO_ArchE.action_registry import ActionRegistry
    
    print("Testing Workflow and Action Discovery...")
    
    # Initialize discovery
    discovery = WorkflowActionDiscovery(
        workflows_dir="workflows",
        action_registry=None  # Will discover from ActionRegistry
    )
    
    print(f"\nDiscovered {len(discovery.workflows_catalog)} workflows")
    print(f"Discovered {len(discovery.actions_catalog)} actions")
    
    # Test search
    results = discovery.search_workflows("search")
    print(f"\nWorkflows matching 'search': {len(results)}")
    for workflow in results[:3]:
        print(f"  - {workflow.get('name')}")
    
    # Test recommendations
    problem = "How many men would it take to defeat a gorilla in a fight?"
    recommendations = discovery.recommend_workflows_for_problem(problem)
    print(f"\nRecommendations for gorilla problem: {len(recommendations)}")
    for rec in recommendations:
        workflow = rec.get('workflow', {})
        print(f"  - {workflow.get('name')}: {rec.get('match_reason')}")
    
    print("\n✅ Workflow discovery test passed!")
    return True

def test_specialized_agent_with_discovery():
    """Test specialized agent with dynamic discovery"""
    from Three_PointO_ArchE.specialized_agent import SpecializedAgent
    from Three_PointO_ArchE.action_registry import ActionRegistry
    
    print("\nTesting Specialized Agent with Discovery...")
    
    # Initialize agent with discovery
    agent = SpecializedAgent(
        domain_expertise="combat_modeling",
        resonantia_capabilities=['ABM', 'CFP', 'CausalInference'],
        workflows_dir="workflows",
        action_registry=None  # Would need actual registry
    )
    
    print(f"Agent domain: {agent.domain_expertise}")
    print(f"Agent capabilities: {agent.resonantia_capabilities}")
    print(f"Discovery enabled: {agent.discovery is not None}")
    
    if agent.discovery:
        problem = "Analyze how many men would be needed to defeat a gorilla using simulations"
        discovery_results = agent.discover_relevant_workflows_and_actions(problem)
        
        print(f"\nDiscovered {len(discovery_results.get('recommended_workflows', []))} workflows")
        print(f"Discovered {len(discovery_results.get('recommended_actions', []))} actions")
        
        # Generate dynamic workflow
        dynamic_workflow = agent.generate_dynamic_workflow_from_discovered_items(
            problem, discovery_results
        )
        print(f"\nGenerated dynamic workflow with {dynamic_workflow['total_steps']} steps")
        print(f"Includes workflows: {dynamic_workflow['includes_workflows']}")
        print(f"Includes actions: {dynamic_workflow['includes_actions']}")
    
    print("\n✅ Specialized agent discovery test passed!")
    return True

def test_playbook_orchestrator_dynamic_execution():
    """Test PlaybookOrchestrator can execute workflows and actions dynamically"""
    from Three_PointO_ArchE.playbook_orchestrator import PlaybookOrchestrator
    
    print("\nTesting Playbook Orchestrator Dynamic Execution...")
    
    orchestrator = PlaybookOrchestrator()
    
    # Test that we can call individual actions
    print(f"Available actions in registry: {len(orchestrator.action_registry.list_actions())}")
    
    # List some actions
    actions = orchestrator.action_registry.list_actions()
    print(f"\nSample actions:")
    for action in actions[:5]:
        print(f"  - {action}")
    
    print("\n✅ Playbook orchestrator test passed!")
    return True

if __name__ == "__main__":
    test_workflow_discovery()
    test_specialized_agent_with_discovery()
    test_playbook_orchestrator_dynamic_execution()
    print("\n🎉 All tests passed!")


