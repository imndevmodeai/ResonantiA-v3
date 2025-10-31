#!/usr/bin/env python3
"""
Test script to verify RISE orchestrator path fix
"""

import os
import sys

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'Three_PointO_ArchE'))

try:
    from rise_orchestrator import RISE_Orchestrator
    
    # Get the correct workflows directory path
    workflows_dir = os.path.join(project_root, 'workflows')
    print(f"Testing RISE_Orchestrator with workflows_dir: {workflows_dir}")
    
    # Check if workflows directory exists
    if not os.path.exists(workflows_dir):
        print(f"❌ Workflows directory not found: {workflows_dir}")
        sys.exit(1)
    
    # Check for expected workflow files
    expected_files = [
        "knowledge_scaffolding.json",
        "metamorphosis_protocol.json", 
        "strategy_fusion.json",
        "high_stakes_vetting.json",
        "distill_spr.json"
    ]
    
    missing_files = []
    for file in expected_files:
        file_path = os.path.join(workflows_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
        else:
            print(f"✅ Found: {file}")
    
    if missing_files:
        print(f"⚠️  Missing files: {missing_files}")
    
    # Initialize RISE_Orchestrator
    orchestrator = RISE_Orchestrator(workflows_dir=workflows_dir)
    print("✅ RISE_Orchestrator initialized successfully!")
    
    # Test workflow loading
    try:
        workflow = orchestrator.workflow_engine.load_workflow("knowledge_scaffolding.json")
        print("✅ Successfully loaded knowledge_scaffolding.json workflow")
    except Exception as e:
        print(f"❌ Failed to load workflow: {e}")
        sys.exit(1)
    
    print("🎉 All tests passed! RISE orchestrator is working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1) 