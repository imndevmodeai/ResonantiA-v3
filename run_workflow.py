import json
import logging
import os
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
    # Get the absolute path to the workflows directory
    workflows_dir = os.path.abspath("workflows")
    
    # Initialize the workflow engine
    engine = IARCompliantWorkflowEngine(workflows_dir=workflows_dir)
    
    # Register mock actions
    engine.register_action("mock_action_a", mock_action_a)
    engine.register_action("mock_action_b", mock_action_b)
    engine.register_action("mock_action_c", mock_action_c)
    
    # Initial context
    initial_context = {
        "input_val": "Test input value",
        "workflow_run_id": "test_run_001"
    }
    
    try:
        # Run the workflow
        workflow_path = os.path.join(workflows_dir, "simple_test.json")
        results = engine.run_workflow(workflow_path, initial_context)
        
        # Print results
        print("\nWorkflow Execution Results:")
        print("=" * 50)
        print(f"Workflow Name: {results['workflow_name']}")
        print(f"Run ID: {results['workflow_run_id']}")
        print(f"Status: {results['workflow_status']}")
        print(f"Duration: {results['workflow_run_duration_sec']} seconds")
        
        print("\nTask Statuses:")
        for task, status in results['task_statuses'].items():
            print(f"- {task}: {status}")
        
        print("\nTask Outputs:")
        for task in ['task_a', 'task_b', 'task_c_conditional']:
            if task in results:
                print(f"\n{task} Output:")
                print(json.dumps(results[task], indent=2))
        
    except Exception as e:
        logging.error(f"Workflow execution failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 