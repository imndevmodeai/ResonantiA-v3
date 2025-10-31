#!/usr/bin/env python3
"""
Test script to verify that auto-log organization works for future logs.
"""

import os
import json
import tempfile
from datetime import datetime
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine

def test_auto_log_organization():
    """Test that new logs are automatically organized."""
    
    print("🧪 Testing Auto-Log Organization...")
    
    # Create a simple test workflow
    test_workflow = {
        "name": "Test Auto Organization Workflow",
        "description": "Test workflow to verify auto-log organization",
        "tasks": {
            "test_task": {
                "action_type": "generate_text_llm",
                "inputs": {
                    "prompt": "Generate a simple test message",
                    "model_settings": {"temperature": 0.1, "max_tokens": 100}
                }
            }
        }
    }
    
    # Initialize workflow engine
    engine = IARCompliantWorkflowEngine()
    
    # Run the test workflow
    print("🚀 Running test workflow...")
    result = engine.run_workflow(
        workflow_name="test_auto_organization",
        initial_context={},
        timeout=30
    )
    
    print(f"✅ Workflow completed with status: {result.get('workflow_status', 'Unknown')}")
    
    # Check if log was auto-organized
    run_id = result.get('run_id', 'unknown')
    original_log_path = f"outputs/run_events_{run_id}.jsonl"
    
    if os.path.exists(original_log_path):
        print(f"📝 Original log created: {original_log_path}")
        
        # Check if organized log exists
        organized_logs_dir = "logs_organized"
        if os.path.exists(organized_logs_dir):
            print("🔍 Checking for auto-organized logs...")
            
            # Look for the organized log
            found_organized = False
            for root, dirs, files in os.walk(organized_logs_dir):
                for file in files:
                    if run_id[:8] in file and file.endswith('.jsonl'):
                        print(f"✅ Found auto-organized log: {os.path.join(root, file)}")
                        found_organized = True
                        
                        # Check if metadata file exists
                        metadata_file = file.replace('.jsonl', '.metadata.json')
                        metadata_path = os.path.join(root, metadata_file)
                        if os.path.exists(metadata_path):
                            print(f"✅ Found metadata file: {metadata_path}")
                            
                            # Read and display metadata
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                            print(f"📊 Metadata: {metadata['workflow_name']} - {metadata['task_count']} tasks, {metadata['error_count']} errors")
                        break
                if found_organized:
                    break
            
            if not found_organized:
                print("❌ Auto-organized log not found!")
                return False
        else:
            print("❌ Organized logs directory not found!")
            return False
    else:
        print(f"❌ Original log not found: {original_log_path}")
        return False
    
    print("🎉 Auto-log organization test PASSED!")
    return True

if __name__ == "__main__":
    success = test_auto_log_organization()
    if success:
        print("\n✅ Future logs will be automatically organized!")
        print("🔧 The system is now set up for continuous log organization.")
    else:
        print("\n❌ Auto-log organization test FAILED!")
        print("🔧 Manual organization still required.")
