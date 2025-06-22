import asyncio
import logging
import os

# This setup assumes the script is run from the repository root
# and the Three_PointO_ArchE package is in the PYTHONPATH.
# If not, you might need to add `sys.path.append('.')` before imports.
from Three_PointO_ArchE.resonant_workflow_engine_v3_1_ca import ResonantWorkflowEngine_v3_1_CA, example_usage

async def main():
    engine = ResonantWorkflowEngine_v3_1_CA()
    
    # Ensure the action registry is populated with mock tools and custom file tool
    await example_usage()
    
    logging.info("\n\n--- STARTING SIMPLE TEST WORKFLOW ---")
    
    workflow_to_run_path = "simple_test.json" # Running the simple_test.json workflow
    initial_context = {"user": "RealAssessment", "run_id": "rs_001"}
    
    final_summary = await engine.run_workflow(workflow_to_run_path, initial_context)
    
    logging.info("\n--- SIMPLE TEST WORKFLOW COMPLETE ---")
    
    # No assertions: Provide a raw assessment by simply printing the final summary.
    print("\n--- REAL ASSESSMENT REPORT ---")
    print(f"Workflow Name: {final_summary.get('workflow_name')}")
    print(f"Run ID: {final_summary.get('workflow_run_id')}")
    print(f"Status: {final_summary.get('workflow_status')}")
    print(f"Duration: {final_summary.get('workflow_run_duration_sec')} seconds")
    print("Resonance Summary:")
    for key, value in final_summary.get('resonance_summary', {}).items():
        print(f"  {key}: {value}")
    print("Final Outputs (Reflections):")
    for task_key, reflection in final_summary.get('final_outputs', {}).items():
        print(f"  Task {task_key}: Status={reflection.get('status')}, Confidence={reflection.get('confidence')}, Summary={reflection.get('summary')}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    asyncio.run(main()) 