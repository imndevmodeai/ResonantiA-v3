#!/usr/bin/env python3
"""
Fix ASASF Workflow - Correct Data Passing Between Tasks
Ensures all execute_code tasks output their results as JSON for proper inter-task communication
"""

import json
import base64
import os

def fix_asasf_workflow():
    """Fix the ASASF workflow to ensure proper data passing between tasks"""
    
    # Load the current workflow
    with open('workflows/ASASF_Persistent_Parallel_ArchE_Workflow_v3.0.json', 'r') as f:
        workflow = json.load(f)
    
    # Fix Task 1: initialize_asasf_matrix - Add JSON output
    task1_code = workflow['tasks']['initialize_asasf_matrix']['inputs']['code']
    
    # Add JSON output to the end of Task 1
    fixed_task1_code = task1_code + """

# Output result as JSON for workflow engine to capture
print("=== WORKFLOW_RESULT ===")
print(json.dumps(result, indent=2))"""
    
    workflow['tasks']['initialize_asasf_matrix']['inputs']['code'] = fixed_task1_code
    
    # Fix Task 2: establish_parallel_streams - Add JSON output
    task2_code = workflow['tasks']['establish_parallel_streams']['inputs']['code']
    
    fixed_task2_code = task2_code + """

# Output result as JSON for workflow engine to capture
print("=== WORKFLOW_RESULT ===")
print(json.dumps(result, indent=2))"""
    
    workflow['tasks']['establish_parallel_streams']['inputs']['code'] = fixed_task2_code
    
    # Fix Task 3: activate_dimensional_resonance - Add JSON output
    task3_code = workflow['tasks']['activate_dimensional_resonance']['inputs']['code']
    
    fixed_task3_code = task3_code + """

# Output result as JSON for workflow engine to capture
print("=== WORKFLOW_RESULT ===")
print(json.dumps(result, indent=2))"""
    
    workflow['tasks']['activate_dimensional_resonance']['inputs']['code'] = fixed_task3_code
    
    # Check if generate_asasf_interface task exists and fix it
    if 'generate_asasf_interface' in workflow['tasks']:
        task4_code = workflow['tasks']['generate_asasf_interface']['inputs']['code']
        
        fixed_task4_code = task4_code + """

# Output result as JSON for workflow engine to capture
print("=== WORKFLOW_RESULT ===")
print(json.dumps(result, indent=2))"""
        
        workflow['tasks']['generate_asasf_interface']['inputs']['code'] = fixed_task4_code
    
    # Convert to JSON string
    workflow_json = json.dumps(workflow, indent=2)
    
    # Use base64 encoding to prevent truncation
    workflow_b64 = base64.b64encode(workflow_json.encode('utf-8')).decode('ascii')
    
    print(f"Original JSON size: {len(workflow_json)} characters")
    print(f"Base64 encoded size: {len(workflow_b64)} characters")
    
    # Decode and write to file safely
    decoded_json = base64.b64decode(workflow_b64).decode('utf-8')
    
    # Write the fixed workflow file
    output_file = 'workflows/ASASF_Persistent_Parallel_ArchE_Workflow_v3.0_FIXED.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(decoded_json)
    
    print(f"✅ Fixed ASASF workflow created: {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")
    
    # Validate JSON structure
    try:
        with open(output_file, 'r') as f:
            json.load(f)
        print("✅ JSON structure validated successfully")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON validation failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_asasf_workflow()
    if success:
        print("\n🎉 ASASF workflow fixed successfully!")
        print("🔧 All tasks now properly output JSON results")
        print("📊 Inter-task data passing should work correctly")
    else:
        print("\n❌ Workflow fix failed") 