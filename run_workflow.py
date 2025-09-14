import json
import logging
import os
import argparse
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def mock_action_a(inputs):
    """Mock action A implementation"""
    return {
        "out_a": f"Processed: {inputs.get('in_a', 'No input')}",
        "reflection": {
            "status": "Success",
            "confidence": 0.9,
            "summary": "Action A completed successfully",
            "alignment_check": True,
            "potential_issues": [],
            "raw_output_preview": "Sample output from action A"
        }
    }

def mock_action_b(inputs):
    """Mock action B implementation"""
    return {
        "out_b": f"Processed B: {inputs.get('in_b', 'No input')}",
        "reflection": {
            "status": "Success",
            "confidence": 0.85,
            "summary": "Action B completed successfully",
            "alignment_check": True,
            "potential_issues": [],
            "raw_output_preview": "Sample output from action B"
        }
    }

def mock_action_c(inputs):
    """Mock action C implementation"""
    return {
        "out_c": "Conditional task C executed",
        "reflection": {
            "status": "Success",
            "confidence": 0.95,
            "summary": "Action C completed successfully",
            "alignment_check": True,
            "potential_issues": [],
            "raw_output_preview": "Sample output from action C"
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Run an Arche workflow with optional initial context and query")
    parser.add_argument("--workflow", required=False, help="Path to workflow JSON file (relative to workflows/ or absolute)")
    parser.add_argument("--context", required=False, help="JSON string for initial context overrides")
    parser.add_argument("--query", required=False, help="Arbitrary user query to add to initial context under 'user_query'")
    args = parser.parse_args()

    # Dynamic path resolution - find project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    workflows_dir = os.path.join(project_root, "workflows")

    # Initialize the workflow engine
    engine = IARCompliantWorkflowEngine(workflows_dir=workflows_dir)

    # Register mock actions (kept for compatibility)
    engine.register_action("mock_action_a", mock_action_a)
    engine.register_action("mock_action_b", mock_action_b)
    engine.register_action("mock_action_c", mock_action_c)

    # Base initial context
    initial_context = {
        "workflow_run_id": "run_generic_001"
    }

    # If query provided, inject
    if args.query:
        initial_context["user_query"] = args.query

    # Merge JSON context overrides if provided
    if args.context:
        try:
            overrides = json.loads(args.context)
            if isinstance(overrides, dict):
                initial_context.update(overrides)
        except Exception as e:
            logging.error(f"Failed to parse --context JSON: {e}")

    # Resolve workflow path
    workflow_path = args.workflow or "resilience_service_workflow.json"

    try:
        results = engine.run_workflow(workflow_path, initial_context)

        # Print results summary
        print("\nWorkflow Execution Results:")
        print("=" * 50)
        print(f"Workflow Name: {results.get('workflow_name')}")
        print(f"Run ID: {results.get('workflow_run_id')}")
        print(f"Status: {results.get('workflow_status')}")
        print(f"Duration: {results.get('workflow_run_duration_sec')} seconds")

        print("\nTask Statuses:")
        for task, status in results.get('task_statuses', {}).items():
            print(f"- {task}: {status}")

    except Exception as e:
        logging.error(f"Workflow execution failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 