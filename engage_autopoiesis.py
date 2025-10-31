import os
import json
from dotenv import load_dotenv

# Ensure the package is in the path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Four_PointO_ArchE.workflow.engine import WorkflowEngine
from Four_PointO_ArchE.tools import (
    genesis_tools,
    llm_tool,
    perception_engine,
    rise_actions,
    utils
)
from Four_PointO_ArchE.workflow.action_registry import ActionRegistry

def main():
    """
    Engages the full autopoietic genesis protocol for ArchE V4.0.
    """
    print("--- Engaging Autopoietic Genesis Protocol ---")
    
    # Load environment variables, including the Google API key
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("ERROR: GOOGLE_API_KEY not found in .env file.")
        return

    try:
        # 1. Create and populate the Action Registry
        print("Creating and populating the Action Registry...")
        action_registry = ActionRegistry()
        
        # Discover all available actions from tool modules
        action_registry.discover_actions(genesis_tools)
        action_registry.discover_actions(llm_tool)
        action_registry.discover_actions(perception_engine)
        action_registry.discover_actions(rise_actions)
        
        print(f"Total actions registered: {len(action_registry.get_actions())}")

        # 2. Initialize the workflow engine with the populated registry
        engine = WorkflowEngine(action_registry=action_registry)
        
        # Define the path to the main genesis workflow
        workflow_path = os.path.join("Happier", "workflows", "autopoietic_genesis_protocol.json")
        print(f"Loading workflow from: {workflow_path}")
        
        if not os.path.exists(workflow_path):
            print(f"ERROR: Workflow file not found at {workflow_path}")
            return
            
        # Load the workflow definition
        workflow = engine.load_workflow(workflow_path)
        
        # Define the initial context for the workflow
        # This workflow is self-contained and reads specs, so initial context is minimal
        initial_context = {
            "specifications_directory": "specifications"
        }

        print("Executing workflow...")
        final_results = engine.execute_workflow(workflow, initial_context)

        print("\n--- Autopoietic Genesis Protocol Execution Complete ---")
        print(json.dumps(final_results, indent=2))

    except Exception as e:
        print(f"\n--- An unexpected error occurred during workflow execution ---")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
