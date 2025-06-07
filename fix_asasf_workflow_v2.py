#!/usr/bin/env python3
"""
Fix ASASF Workflow v2 - Correct JSON Output for Workflow Engine
Ensures all execute_code tasks output ONLY JSON to stdout for proper parsing
"""

import json
import base64
import os

def fix_asasf_workflow_v2():
    """Fix the ASASF workflow to ensure proper JSON output to stdout"""
    
    # Load the current workflow
    with open('workflows/ASASF_Persistent_Parallel_ArchE_Workflow_v3.0.json', 'r') as f:
        workflow = json.load(f)
    
    # Fix Task 1: initialize_asasf_matrix - Move prints to stderr, output only JSON to stdout
    task1_code = workflow['tasks']['initialize_asasf_matrix']['inputs']['code']
    
    # Replace the print statements and add proper JSON output
    fixed_task1_code = task1_code.replace(
        'print(f\'ASASF Matrix initialized with {len(asasf_matrix["dimensional_layers"])} dimensional layers\')\nprint(f\'Session directory: {session_dir}\')',
        'import sys\nsys.stderr.write(f\'ASASF Matrix initialized with {len(asasf_matrix["dimensional_layers"])} dimensional layers\\n\')\nsys.stderr.write(f\'Session directory: {session_dir}\\n\')'
    ) + """

# Output ONLY the result as JSON to stdout for workflow engine to capture
print(json.dumps(result, indent=2))"""
    
    workflow['tasks']['initialize_asasf_matrix']['inputs']['code'] = fixed_task1_code
    
    # Fix Task 2: establish_parallel_streams - Move prints to stderr, output only JSON to stdout
    task2_code = workflow['tasks']['establish_parallel_streams']['inputs']['code']
    
    fixed_task2_code = task2_code.replace(
        'print(f\'Parallel streams established: {active_streams}/{len(stream_processors)}\')\nprint(f\'Coherence level: {coherence_level:.2f}\')',
        'import sys\nsys.stderr.write(f\'Parallel streams established: {active_streams}/{len(stream_processors)}\\n\')\nsys.stderr.write(f\'Coherence level: {coherence_level:.2f}\\n\')'
    ) + """

# Output ONLY the result as JSON to stdout for workflow engine to capture
print(json.dumps(result, indent=2))"""
    
    workflow['tasks']['establish_parallel_streams']['inputs']['code'] = fixed_task2_code
    
    # Fix Task 3: activate_dimensional_resonance - Move prints to stderr, output only JSON to stdout
    task3_code = workflow['tasks']['activate_dimensional_resonance']['inputs']['code']
    
    fixed_task3_code = task3_code.replace(
        'print(f\'Dimensional resonance activated across {len(dimensional_resonances)} layers\')\nprint(f\'System coherence: {system_coherence:.3f}\')\nprint(f\'As above, so below principle: ACTIVE\')',
        'import sys\nsys.stderr.write(f\'Dimensional resonance activated across {len(dimensional_resonances)} layers\\n\')\nsys.stderr.write(f\'System coherence: {system_coherence:.3f}\\n\')\nsys.stderr.write(f\'As above, so below principle: ACTIVE\\n\')'
    ) + """

# Output ONLY the result as JSON to stdout for workflow engine to capture
print(json.dumps(result, indent=2))"""
    
    workflow['tasks']['activate_dimensional_resonance']['inputs']['code'] = fixed_task3_code
    
    # Convert to JSON string
    workflow_json = json.dumps(workflow, indent=2)
    
    # Use base64 encoding to prevent truncation
    workflow_b64 = base64.b64encode(workflow_json.encode('utf-8')).decode('ascii')
    
    print(f"Original JSON size: {len(workflow_json)} characters")
    print(f"Base64 encoded size: {len(workflow_b64)} characters")
    
    # Decode and write to file safely
    decoded_json = base64.b64decode(workflow_b64).decode('utf-8')
    
    # Write the fixed workflow file
    output_file = 'workflows/ASASF_Persistent_Parallel_ArchE_Workflow_v3.0_FIXED_V2.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(decoded_json)
    
    print(f"✅ Fixed ASASF workflow v2 created: {output_file}")
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
    success = fix_asasf_workflow_v2()
    if success:
        print("\n🎉 ASASF workflow v2 fixed successfully!")
        print("🔧 All tasks now output ONLY JSON to stdout")
        print("📊 Workflow engine should parse JSON correctly")
        print("💬 Debug messages moved to stderr")
    else:
        print("\n❌ Workflow fix v2 failed") 