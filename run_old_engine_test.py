import sys
import os
import json
import importlib.util

# Construct the full path to workflow_engine.old.py
old_engine_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Three_PointO_ArchE', 'workflow_engine.old.py'))

try:
    with open(old_engine_path, 'r') as f:
        old_engine_code = f.read()

    # Ultra-aggressive dynamic indentation correction:
    # Strip ALL leading and trailing whitespace from each line.
    # This should remove any hidden/problematic characters or mixed indents.
    cleaned_code_lines = [line.strip() for line in old_engine_code.splitlines()]
    # Filter out empty lines that might result from stripping
    cleaned_code_lines = [line for line in cleaned_code_lines if line]

    # Re-join with newlines. This ensures a clean slate, with no leading indents.
    # Python's parser will then expect the correct indentation from line 1.
    cleaned_old_engine_code = "\n".join(cleaned_code_lines)

    # Prepare a dictionary for the exec() context to capture defined objects
    exec_globals = {}
    exec_locals = {}
    # Execute the corrected code in the context of this script
    exec(cleaned_old_engine_code, exec_globals, exec_locals)

    # Now get the IARCompliantWorkflowEngine class from the executed code
    IARCompliantWorkflowEngine = exec_locals['IARCompliantWorkflowEngine']

except Exception as e:
    print(f"Error loading and executing workflow_engine.old.py dynamically: {e}")
    sys.exit(1)

from Three_PointO_ArchE.action_registry import register_action

# Define a simple mock action, as the old engine might need actions registered
def mock_action_a(inputs, context_for_action):
    print(f"Mock Action A executed with inputs: {inputs}")
    # The old engine's execute_action path passes a simpler context
    # This mock's return needs to conform to expected IAR for the old engine
    return {"output": "Mock A output", "reflection": {"status": "Success", "summary": "Mock action A completed.", "confidence": 1.0, "alignment_check": "N/A", "potential_issues": [], "raw_output_preview": "Mock A output"}}

def mock_action_b(inputs, context_for_action):
    print(f"Mock Action B executed with inputs: {inputs}")
    return {"output": "Mock B output", "reflection": {"status": "Success", "summary": "Mock action B completed.", "confidence": 1.0, "alignment_check": "N/A", "potential_issues": [], "raw_output_preview": "Mock B output"}}

def mock_action_c(inputs, context_for_action):
    print(f"Mock Action C executed with inputs: {inputs}")
    return {"output": "Mock C output", "reflection": {"status": "Success", "summary": "Mock action C completed.", "confidence": 1.0, "alignment_check": "N/A", "potential_issues": [], "raw_output_preview": "Mock C output"}}

# Register mock actions with the engine's registry
register_action("mock_action_a", mock_action_a, force=True)
register_action("mock_action_b", mock_action_b, force=True)
register_action("mock_action_c", mock_action_c, force=True)

if __name__ == "__main__":
    workflow_path = "simple_test.json"
    initial_context = {"user_input": "Run a basic test workflow using the old engine.", "workflow_run_id": "test_run_old_engine"}

    # Instantiate the old workflow engine
    engine = IARCompliantWorkflowEngine(workflows_dir="workflows")

    print(f"Attempting to run workflow: {workflow_path} with the OLD engine ({old_engine_path})...")
    try:
        # The old engine's run_workflow expects workflow_name (e.g., "simple_test.json")
        # and initial_context
        result = engine.run_workflow(workflow_name=workflow_path, initial_context=initial_context)
        print("\n--- Workflow Execution Result (Old Engine) ---")
        print(json.dumps(result, indent=2))
        print("---------------------------------------------")
    except Exception as e:
        print(f"An error occurred during workflow execution with the OLD engine: {e}") 