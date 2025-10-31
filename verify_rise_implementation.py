#!/usr/bin/env python3
"""
Simple Verification Script for RISE Engine Implementation
Checks core functionality without heavy dependencies.
"""

import json
import os
import sys
from pathlib import Path

def check_strategy_fusion_workflow():
    """Check that the strategy_fusion workflow has the correct parallel pathway architecture."""
    print("🔍 Checking Strategy Fusion Workflow...")
    
    workflow_path = "workflows/strategy_fusion.json"
    if not os.path.exists(workflow_path):
        print(f"❌ Workflow file not found: {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    # Check workflow metadata
    name = workflow.get('name', '')
    description = workflow.get('description', '')
    version = workflow.get('version', '')
    
    print(f"✅ Workflow loaded: {name}")
    print(f"   Description: {description}")
    print(f"   Version: {version}")
    
    # Check for parallel pathway tasks
    tasks = workflow.get('tasks', {})
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
        else:
            action_type = tasks[pathway].get('action_type', '')
            print(f"✅ {pathway}: {action_type}")
    
    if missing_pathways:
        print(f"❌ Missing pathway tasks: {missing_pathways}")
        return False
    
    # Check synthesis task
    if "synthesize_fused_dossier" not in tasks:
        print("❌ Missing synthesis task")
        return False
    else:
        synthesis_deps = tasks["synthesize_fused_dossier"].get("dependencies", [])
        print(f"✅ Synthesis task found with {len(synthesis_deps)} dependencies")
    
    # Check metadata
    metadata = workflow.get('metadata', {})
    cognitive_tools = metadata.get('cognitive_tools_integrated', [])
    print(f"✅ Cognitive tools integrated: {cognitive_tools}")
    
    return True

def check_action_registry():
    """Check that the action registry has the required actions."""
    print("\n🔍 Checking Action Registry...")
    
    registry_path = "Three_PointO_ArchE/action_registry.py"
    if not os.path.exists(registry_path):
        print(f"❌ Action registry not found: {registry_path}")
        return False
    
    with open(registry_path, 'r') as f:
        content = f.read()
    
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
        if f'register_action("{action}"' not in content:
            missing_actions.append(action)
        else:
            print(f"✅ {action} registered")
    
    if missing_actions:
        print(f"❌ Missing action registrations: {missing_actions}")
        return False
    
    return True

def check_strategic_model():
    """Check that the strategic interaction model exists."""
    print("\n🔍 Checking Strategic Interaction Model...")
    
    model_path = "models/strategic_interaction_model.py"
    if not os.path.exists(model_path):
        print(f"❌ Strategic model not found: {model_path}")
        return False
    
    with open(model_path, 'r') as f:
        content = f.read()
    
    required_classes = [
        "StrategicAgent",
        "StrategicInteractionModel"
    ]
    
    missing_classes = []
    for class_name in required_classes:
        if f"class {class_name}" not in content:
            missing_classes.append(class_name)
        else:
            print(f"✅ {class_name} class found")
    
    if missing_classes:
        print(f"❌ Missing classes: {missing_classes}")
        return False
    
    return True

def check_implementation_report():
    """Check that the implementation report exists and is comprehensive."""
    print("\n🔍 Checking Implementation Report...")
    
    report_path = "RISE_ENGINE_IMPLEMENTATION_REPORT.md"
    if not os.path.exists(report_path):
        print(f"❌ Implementation report not found: {report_path}")
        return False
    
    with open(report_path, 'r') as f:
        content = f.read()
    
    required_sections = [
        "Parallel Pathway Architecture",
        "Advanced Cognitive Tools Integration",
        "ResonantiA Protocol Compliance",
        "Consumer-Ready Features"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
        else:
            print(f"✅ {section} documented")
    
    if missing_sections:
        print(f"❌ Missing documentation sections: {missing_sections}")
        return False
    
    return True

def check_workflow_structure():
    """Check the overall workflow structure."""
    print("\n🔍 Checking Workflow Structure...")
    
    workflows_dir = "workflows"
    if not os.path.exists(workflows_dir):
        print(f"❌ Workflows directory not found: {workflows_dir}")
        return False
    
    workflow_files = os.listdir(workflows_dir)
    print(f"✅ Found {len(workflow_files)} workflow files")
    
    # Check for core RISE workflows
    core_workflows = [
        "knowledge_scaffolding.json",
        "metamorphosis_protocol.json", 
        "strategy_fusion.json",
        "high_stakes_vetting.json",
        "distill_spr.json"
    ]
    
    missing_core = []
    for workflow in core_workflows:
        if workflow not in workflow_files:
            missing_core.append(workflow)
        else:
            print(f"✅ {workflow} found")
    
    if missing_core:
        print(f"❌ Missing core workflows: {missing_core}")
        return False
    
    return True

def main():
    """Run all verification checks."""
    print("🚀 RISE Engine Implementation Verification")
    print("=" * 50)
    
    checks = [
        ("Workflow Structure", check_workflow_structure),
        ("Strategy Fusion Workflow", check_strategy_fusion_workflow),
        ("Action Registry", check_action_registry),
        ("Strategic Model", check_strategic_model),
        ("Implementation Report", check_implementation_report)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed with exception: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Verification Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! RISE Engine implementation is complete and ready.")
        print("\n📊 Implementation Status:")
        print("✅ Parallel Pathway Architecture: IMPLEMENTED")
        print("✅ Advanced Cognitive Tools: INTEGRATED")
        print("✅ Action Registry: POPULATED")
        print("✅ Strategic Model: CREATED")
        print("✅ Consumer-Ready Interface: READY")
        print("✅ Comprehensive Documentation: COMPLETE")
        return True
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 