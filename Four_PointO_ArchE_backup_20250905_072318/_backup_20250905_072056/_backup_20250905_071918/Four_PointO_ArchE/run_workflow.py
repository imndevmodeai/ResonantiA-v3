import sys
import os
import json
import argparse

# This is a critical adjustment to ensure the script can find the V4 modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from workflow.engine import WorkflowEngine
from tools.action_registry import canonical_registry

def main():
    """
    [V4.1 - CANONICAL] The single, unified entry point for executing any
    ArchE workflow.
    """
    parser = argparse.ArgumentParser(description="ArchE V4 Canonical Workflow Runner")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file.")
    parser.add_argument("-c", "--context", help="JSON string for the initial context.", default="{}")
    args = parser.parse_args()

    try:
        initial_context = json.loads(args.context)
    except json.JSONDecodeError:
        print("Error: Invalid JSON provided for initial context.")
        sys.exit(1)

    # We will instantiate the V4 engine and pass it the canonical registry
    engine = WorkflowEngine(action_registry=canonical_registry)
    
    # The V4 engine is expected to have a `run` method
    final_result = engine.run(
        workflow_path=args.workflow_file,
        initial_context=initial_context
    )

    print("\n--- WORKFLOW COMPLETE ---")
    print(json.dumps(final_result, indent=2))

if __name__ == "__main__":
    main()
