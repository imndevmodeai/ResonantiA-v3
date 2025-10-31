import os
import sys
import json
from pprint import pprint

# --- Path Setup ---
# This ensures that the script can find the Three_PointO_ArchE package
# even when run from the 'examples' directory.
def setup_project_path():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the project root (which is one level up from 'examples')
    project_root = os.path.dirname(script_dir)
    # Add the project root to the Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"Added project root to path: {project_root}")

setup_project_path()

# Now we can import from the ArchE package
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.spr_manager import SPRManager
from Three_PointO_ArchE.config import get_config

def run_greeting_example():
    """
    Demonstrates how to instantiate the workflow engine and run the 
    example_greeting_workflow.json blueprint.
    """
    print("--- Initializing Workflow Engine for Greeting Example ---")
    
    # Load system configuration to get paths
    config = get_config()
    
    # 1. Instantiate the SPRManager (required by the engine)
    # The SPRManager needs the path to the definitions file.
    spr_manager = SPRManager(spr_filepath=str(config.paths.spr_definitions))
    
    # 2. Instantiate the IARCompliantWorkflowEngine
    # The engine needs to know where to find the workflow JSON files.
    # We point it to the 'core_workflows' directory from our config.
    workflows_directory = str(config.paths.workflows)
    print(f"Using workflows directory: {workflows_directory}")
    
    engine = IARCompliantWorkflowEngine(
        workflows_dir=workflows_directory,
        spr_manager=spr_manager
    )

    # 3. Define the name of the workflow to run
    workflow_to_run = "example_greeting_workflow.json"

    # 4. Define the initial context
    # This dictionary provides the starting data for the workflow.
    # The keys here must match the placeholders used in the workflow JSON.
    # In our case, the workflow expects 'user_name'.
    initial_context_data = {
        "user_name": "Keyholder"
    }
    
    print(f"\n--- Running Workflow: {workflow_to_run} ---")
    print("Initial Context:")
    pprint(initial_context_data)
    
    try:
        # 5. Execute the workflow
        # The run_workflow method takes the workflow filename and the initial context.
        final_result = engine.run_workflow(
            workflow_name=workflow_to_run,
            initial_context=initial_context_data
        )
        
        print("\n--- Workflow Execution Complete ---")
        
        # 6. Process the results
        # The engine returns a comprehensive dictionary with all task outputs and metadata.
        print("\nFinal Workflow Result:")
        pprint(final_result)

        # You can access specific outputs defined in the workflow's "output" section
        final_greeting = final_result.get('final_greeting')
        if final_greeting:
            print("\n" + "="*50)
            print("Extracted Final Greeting:")
            print(final_greeting)
            print("="*50)
        else:
            print("\nCould not find the 'final_greeting' in the workflow output.")
            
    except FileNotFoundError:
        print(f"\\nERROR: The workflow file '{workflow_to_run}' could not be found in '{workflows_directory}'.")
        print("Please ensure the file exists and the path is correct.")
    except Exception as e:
        print(f"\\nAn unexpected error occurred during workflow execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_greeting_example()
