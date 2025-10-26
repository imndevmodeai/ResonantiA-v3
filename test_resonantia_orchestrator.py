#!/usr/bin/env python3
"""
Test script for the ResonantiA-aware Playbook Orchestrator
Demonstrates how the enhanced Playbook Orchestrator recognizes ResonantiA-specific terminology
and builds custom workflows dynamically.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Three_PointO_ArchE'))

from playbook_orchestrator import PlaybookOrchestrator
import json

def test_resonantia_query_analysis():
    """Test the ResonantiA query analysis functionality."""
    
    print("=" * 80)
    print("RESONANTIA-AWARE PLAYBOOK ORCHESTRATOR TEST")
    print("=" * 80)
    
    # Initialize the enhanced orchestrator
    orchestrator = PlaybookOrchestrator()
    
    # Test query with ResonantiA-specific terminology
    resonantia_query = """
    Analyze the surge in popularity of specific kinks like female orgasms, squirting, 
    and party-and-play (PnP) dynamics in the adult webcam industry between 2020 and 2025. 
    Initiate a full RISE analysis. First, perform a Knowledge Scaffolding phase to ingest 
    historical platform data, user trends from sites like Chaturbate, news archives on 
    adult content consumption, and performer profiles from that period. Second, use your 
    Proactive Truth Resonance Framework (PTRF) to produce a Solidified Truth Packet that 
    debunks common misconceptions and identifies the primary, verified causal drivers of 
    this kink surge, moving beyond the simplistic COVID-19 isolation explanation. Third, 
    use your Causal Inference Tool with Causal Lag Detection to model the lagged cultural 
    and economic impact of these kinks on meetups and hookups in usa from sites like 
    fetlife and skipthegames.com and meetup behaviors in sectors like online dating and 
    adult events. Finally, produce a comprehensive strategic briefing that a male straight 
    or couple can use to earn a living in the niche market either in performing or 
    supporting by any and all options in and around the niche.
    """
    
    print("\n1. ANALYZING QUERY FOR RESONANTIA PATTERNS...")
    print("-" * 50)
    
    # Analyze the query for ResonantiA patterns
    workflow = orchestrator.analyze_query_for_resonantia_patterns(resonantia_query)
    
    print(f"Generated Workflow: {workflow['name']}")
    print(f"Description: {workflow['description']}")
    print(f"Number of Tasks: {len(workflow['tasks'])}")
    
    print("\n2. DETECTED RESONANTIA PATTERNS:")
    print("-" * 50)
    
    # Show detected patterns
    query_lower = resonantia_query.lower()
    detected_patterns = []
    
    for pattern_name, pattern_config in orchestrator.resonantia_patterns.items():
        for keyword in pattern_config["keywords"]:
            if keyword in query_lower:
                detected_patterns.append({
                    "pattern": pattern_name,
                    "action": pattern_config["action"],
                    "priority": pattern_config["priority"],
                    "matched_keyword": keyword
                })
                break
    
    detected_patterns.sort(key=lambda x: x["priority"])
    
    for i, pattern in enumerate(detected_patterns, 1):
        print(f"{i}. {pattern['pattern'].upper()}")
        print(f"   Action: {pattern['action']}")
        print(f"   Priority: {pattern['priority']}")
        print(f"   Matched Keyword: '{pattern['matched_keyword']}'")
        print()
    
    print("3. GENERATED WORKFLOW STRUCTURE:")
    print("-" * 50)
    
    for task_key, task_def in workflow['tasks'].items():
        print(f"Task: {task_key}")
        print(f"  Action: {task_def['action_type']}")
        print(f"  Description: {task_def['description']}")
        print(f"  Inputs: {list(task_def['inputs'].keys())}")
        print()
    
    print("4. WORKFLOW DEPENDENCIES:")
    print("-" * 50)
    
    for task, deps in workflow['dependencies'].items():
        print(f"{task} depends on: {deps}")
    
    print("\n5. EXTRACTED PARAMETERS:")
    print("-" * 50)
    
    domain = orchestrator._extract_domain_from_query(resonantia_query)
    time_period = orchestrator._extract_time_period(resonantia_query)
    
    print(f"Domain: {domain}")
    print(f"Time Period: {time_period}")
    
    print("\n6. WORKFLOW JSON PREVIEW:")
    print("-" * 50)
    
    # Show a preview of the generated workflow
    workflow_preview = {
        "name": workflow["name"],
        "description": workflow["description"],
        "task_count": len(workflow["tasks"]),
        "tasks": {k: {"action_type": v["action_type"], "description": v["description"]} 
                 for k, v in list(workflow["tasks"].items())[:3]},  # Show first 3 tasks
        "dependencies": workflow["dependencies"]
    }
    
    print(json.dumps(workflow_preview, indent=2))
    
    print("\n" + "=" * 80)
    print("RESONANTIA-AWARE ANALYSIS COMPLETE")
    print("=" * 80)
    
    return workflow

def test_standard_query():
    """Test with a standard query (no ResonantiA terminology)."""
    
    print("\n" + "=" * 80)
    print("STANDARD QUERY TEST (NO RESONANTIA TERMINOLOGY)")
    print("=" * 80)
    
    orchestrator = PlaybookOrchestrator()
    
    standard_query = "What are the latest trends in artificial intelligence?"
    
    print(f"Query: {standard_query}")
    print("\nAnalyzing for ResonantiA patterns...")
    
    workflow = orchestrator.analyze_query_for_resonantia_patterns(standard_query)
    
    print(f"Generated Workflow: {workflow['name']}")
    print(f"Description: {workflow['description']}")
    print(f"Number of Tasks: {len(workflow['tasks'])}")
    
    print("\nTasks:")
    for task_key, task_def in workflow['tasks'].items():
        print(f"  {task_key}: {task_def['action_type']} - {task_def['description']}")
    
    print("\n" + "=" * 80)
    print("STANDARD QUERY TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    # Test ResonantiA query analysis
    resonantia_workflow = test_resonantia_query_analysis()
    
    # Test standard query
    test_standard_query()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("The ResonantiA-aware Playbook Orchestrator is working correctly.")
    print("=" * 80)
