#!/usr/bin/env python3

import json
import logging
from pathlib import Path
from Three_PointO_ArchE.pattern_reflection_system import PatternReflectionSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_workflow(workflow_path: str) -> dict:
    """Load the workflow definition from a JSON file."""
    try:
        with open(workflow_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load workflow: {str(e)}")
        raise

def execute_workflow(workflow: dict, system: PatternReflectionSystem) -> dict:
    """Execute the workflow tasks in sequence."""
    results = {}
    completed_tasks = set()

    def can_execute_task(task_name: str) -> bool:
        """Check if a task's dependencies have been completed."""
        dependencies = workflow["tasks"][task_name].get("dependencies", [])
        return all(dep in completed_tasks for dep in dependencies)

    while len(completed_tasks) < len(workflow["tasks"]):
        for task_name, task in workflow["tasks"].items():
            if task_name in completed_tasks:
                continue

            if can_execute_task(task_name):
                logger.info(f"Executing task: {task_name}")
                
                try:
                    # Execute the task based on its action type
                    if task["action_type"] == "perform_system_genesis_action":
                        operation = task["inputs"]["operation"]
                        
                        if operation == "initialize_hierarchy":
                            result = system.initialize_hierarchy(
                                bidirectional=task["inputs"].get("bidirectional", True)
                            )
                        elif operation == "extract_patterns":
                            result = system.extract_patterns(
                                level=task["inputs"]["level"],
                                source=task["inputs"]["source"]
                            )
                        elif operation == "reflect_patterns":
                            result = system.reflect_patterns(
                                direction=task["inputs"]["direction"],
                                patterns=task["inputs"]["patterns"],
                                levels=task["inputs"]["levels"]
                            )
                        elif operation == "synthesize_patterns":
                            result = system.synthesize_patterns(
                                upward_patterns=task["inputs"]["upward_patterns"],
                                downward_patterns=task["inputs"]["downward_patterns"]
                            )
                        elif operation == "validate_coherence":
                            result = system.validate_coherence(
                                synthesized_patterns=task["inputs"]["synthesized_patterns"],
                                threshold=task["inputs"]["threshold"]
                            )
                        elif operation == "integrate_patterns":
                            result = system.integrate_patterns(
                                validated_patterns=task["inputs"]["validated_patterns"],
                                target_system=task["inputs"]["target_system"]
                            )
                        elif operation == "generate_report":
                            result = system.generate_report(
                                integration_results=task["inputs"]["integration_results"],
                                format=task["inputs"]["format"]
                            )
                        else:
                            raise ValueError(f"Unknown operation: {operation}")
                        
                        results[task_name] = result
                        completed_tasks.add(task_name)
                        
                    elif task["action_type"] == "display_output":
                        # For display tasks, just store the content
                        results[task_name] = {
                            "status": "success",
                            "content": task["inputs"]["content"]
                        }
                        completed_tasks.add(task_name)
                    
                    else:
                        raise ValueError(f"Unknown action type: {task['action_type']}")
                    
                except Exception as e:
                    logger.error(f"Failed to execute task {task_name}: {str(e)}")
                    results[task_name] = {
                        "status": "error",
                        "message": str(e)
                    }
                    completed_tasks.add(task_name)
                    continue

    return results

def main():
    # Load the workflow
    workflow_path = "workflows/as_above_so_below_workflow.json"
    workflow = load_workflow(workflow_path)
    
    # Initialize the pattern reflection system
    knowledge_tapestry_path = "Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json"
    system = PatternReflectionSystem(knowledge_tapestry_path)
    
    # Execute the workflow
    results = execute_workflow(workflow, system)
    
    # Save the results
    output_path = "outputs/as_above_so_below_results.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Workflow execution completed. Results saved to {output_path}")
    
    # Display the final report if available
    if "final_output" in results and results["final_output"]["status"] == "success":
        print("\nFinal Report:")
        print(results["final_output"]["content"])

if __name__ == "__main__":
    main() 