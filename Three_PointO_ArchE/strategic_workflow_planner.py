"""
Strategic Workflow Planner (The Mind of RISE)
==============================================

As Above: The Principle of Isomorphism
---------------------------------------
The universe repeats its patterns at every scale. The optimal path for a fleet of vehicles delivering packages is, structurally, the same problem as the optimal path for a series of cognitive actions achieving a complex goal. Both are graphs of nodes (locations/tasks) and edges (travel time/dependencies) that can be solved with the same universal principles of combinatorial optimization. This planner is the bridge between these two domains. It does not invent new logic; it recognizes the isomorphism between a complex query and a Vehicle Routing Problem and performs the translation.

So Below: The Operational Logic
-------------------------------
This module provides the `StrategicWorkflowPlanner` class. Its purpose is to act as the "mind" for the RISE engine. It takes a high-concept, multi-step query (a "blueprint") and translates it into a formal optimization problem that can be solved by the existing `AdvancedTSPSolver` (which uses Google OR-Tools).

The process is as follows:
1.  **Deconstruction:** An LLM is used to break the blueprint into abstract goals and their dependencies.
2.  **Problem Formulation:** These goals are mapped to concrete system actions, and the dependencies are used to define constraints. Costs are estimated.
3.  **Translation to VRP:** The entire abstract workflow is converted into a dictionary that matches the input schema of the `AdvancedTSPSolver` (the Vehicle Routing Problem format).
4.  **Invocation:** The solver is called to find the optimal sequence of actions.
5.  **Translation to Workflow:** The solver's output (a set of routes) is translated back into a standard, executable ArchE workflow JSON file.
"""

import logging
import json
from typing import Dict, Any, List

from Three_PointO_ArchE.action_registry import main_action_registry

# We will eventually import the TSP solver and LLM provider
# from advanced_tsp_solver import AdvancedTSPSolver
# from Three_PointO_ArchE.llm_providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class StrategicWorkflowPlanner:
    """
    Translates a complex natural language query into an optimized workflow
    by leveraging a combinatorial optimization solver.
    """

    def __init__(self, llm_provider: Any, solver: Any):
        """
        Initializes the planner with a language model and a solver.

        Args:
            llm_provider: An instance of a large language model provider.
            solver: An instance of the AdvancedTSPSolver.
        """
        self.llm = llm_provider
        self.solver = solver
        self.action_registry = main_action_registry
        logger.info("StrategicWorkflowPlanner initialized.")

    def deconstruct_blueprint(self, blueprint_query: str) -> Dict[str, Any]:
        """
        Uses an LLM to deconstruct a complex query into a sequence of executable actions.
        """
        logger.info(f"Deconstructing blueprint: {blueprint_query[:100]}...")

        action_signatures = self.action_registry.get_action_signatures()

        prompt = f"""
        You are an expert system architect. Your task is to analyze a user's request and deconstruct it into a sequence of executable tasks for the ArchE system.
        You must only use the actions available in the provided "Action API Reference". Pay close attention to the required parameters for each action.

        **User Request:**
        "{blueprint_query}"

        **Action API Reference:**
        ```json
        {json.dumps(action_signatures, indent=2)}
        ```

        **CRITICAL INSTRUCTION:** The `inputs` for each task MUST be a flat JSON object where the keys are the parameter names from the 'params' section of the Action API Reference. DO NOT nest the inputs inside another `inputs` or `kwargs` key.

        **Instructions:**
        1.  Carefully read the User Request to understand the overall goal.
        2.  Identify the sequence of steps required to fulfill the request.
        3.  For each step, select the most appropriate action from the "Action API Reference".
        4.  **PRIORITY: Use federated agents for web searches and research tasks:**
           - For web searches, use `invoke_specialist_agent` with `agent_type: "search"` or `agent_type: "academic"`
           - For YouTube video analysis, use `invoke_specialist_agent` with `agent_type: "visual"`
           - For community/social research, use `invoke_specialist_agent` with `agent_type: "community"`
        5.  Construct the `inputs` for each action precisely as defined in its `params`.
        6.  Values for inputs can be static (from the query) or dynamic, referencing outputs from previous tasks using the format `{{{{TASK_ID.output.key}}}}`.
        7.  Provide a concise, human-readable `description` for each task.
        8.  Define the `dependencies` between tasks. A task can only depend on tasks that come before it in the execution plan.
        9.  Return a single JSON object containing the `tasks` and `dependencies`.

        **Example Output Format:**
        {{
            "tasks": {{
                "TASK_1_WEB_SEARCH": {{
                    "description": "Search for latest developments using federated search agents",
                    "action_type": "invoke_specialist_agent",
                    "inputs": {{
                        "agent_type": "search",
                        "query": "latest developments in quantum computing",
                        "max_results": 5
                    }}
                }},
                "TASK_2_YOUTUBE_ANALYSIS": {{
                    "description": "Analyze YouTube videos about quantum supremacy using visual synthesis agent",
                    "action_type": "invoke_specialist_agent",
                    "inputs": {{
                        "agent_type": "visual",
                        "query": "quantum supremacy breakthroughs",
                        "max_results": 3
                    }}
                }},
                "TASK_3_SYNTHESIS": {{
                    "description": "Synthesize findings from web search and video analysis",
                    "action_type": "generate_text_llm",
                    "inputs": {{
                        "prompt": "Based on the web search results: {{{{TASK_1_WEB_SEARCH.output}}}} and YouTube analysis: {{{{TASK_2_YOUTUBE_ANALYSIS.output}}}}, provide a comprehensive analysis of quantum computing developments."
                    }}
                }}
            }},
            "dependencies": {{
                "TASK_2_YOUTUBE_ANALYSIS": ["TASK_1_WEB_SEARCH"],
                "TASK_3_SYNTHESIS": ["TASK_1_WEB_SEARCH", "TASK_2_YOUTUBE_ANALYSIS"]
            }}
        }}

        **Begin Deconstruction:**
        """

        try:
            response = self.llm.generate(prompt=prompt, model="gemini-2.0-flash-exp")
            # The response from the LLM is expected to be a JSON string.
            # It might be wrapped in markdown ```json ... ```, so we need to clean it.
            cleaned_response = response.strip().strip("`").strip()
            if cleaned_response.startswith("json"):
                cleaned_response = cleaned_response[4:].strip()
            
            deconstructed_plan = json.loads(cleaned_response)
            logger.info("Blueprint deconstructed successfully by LLM.")
            return deconstructed_plan
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to deconstruct blueprint. LLM output was not valid JSON: {e}")
            # Fallback to a safe, empty plan
            return {"tasks": {}, "dependencies": {}}
        except Exception as e:
            logger.error(f"An unexpected error occurred during blueprint deconstruction: {e}")
            return {"tasks": {}, "dependencies": {}}


    def formulate_optimization_problem(self, deconstruction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formulates the deconstructed goals into a formal problem for the solver.
        (This is a placeholder).
        """
        logger.info("Formulating optimization problem...")
        # This would involve mapping goals to actions, estimating costs, etc.
        placeholder_problem = {
            # This structure needs to match the input of the AdvancedTSPSolver
            "locations": ["Depot"] + list(deconstruction.get("tasks", {}).keys()),
            "num_vehicles": 1,
            "depot": 0
            # ... plus distance/cost matrices, constraints, etc.
        }
        logger.info("Optimization problem formulated.")
        return placeholder_problem

    def translate_solution_to_workflow(self, deconstruction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates the deconstructed and potentially optimized plan into a full ArchE workflow.
        """
        logger.info("Translating deconstructed plan to an executable workflow...")
        
        # For now, we are skipping the optimization step and using the direct deconstruction.
        workflow = {
            "name": "Strategically_Generated_Workflow",
            "description": "This workflow was dynamically generated by the StrategicWorkflowPlanner.",
            "tasks": deconstruction.get("tasks", {}),
            "dependencies": deconstruction.get("dependencies", {})
        }
        
        logger.info("Workflow translated successfully.")
        return workflow

    def generate_workflow_from_blueprint(self, blueprint_query: str) -> Dict[str, Any]:
        """
        The main entry point that orchestrates the entire translation process.
        """
        logger.info("Starting strategic workflow generation from blueprint.")
        
        # Step 1: Deconstruct the query into executable tasks
        deconstruction = self.deconstruct_blueprint(blueprint_query)
        
        # Save the deconstruction blueprint to outputs directory
        try:
            from pathlib import Path
            import time
            
            outputs_dir = Path("outputs")
            outputs_dir.mkdir(exist_ok=True)
            
            timestamp = int(time.time())
            blueprint_filename = f"blueprint_deconstruction_{timestamp}.json"
            blueprint_filepath = outputs_dir / blueprint_filename
            
            blueprint_data = {
                "original_query": blueprint_query,
                "deconstruction": deconstruction,
                "timestamp": timestamp
            }
            
            with open(blueprint_filepath, 'w', encoding='utf-8') as f:
                json.dump(blueprint_data, f, indent=2)
            logger.info(f"Blueprint deconstruction saved to: {blueprint_filepath}")
        except Exception as e:
            logger.warning(f"Failed to save blueprint deconstruction: {e}")
        
        if not deconstruction or not deconstruction.get("tasks"):
            logger.warning("Deconstruction resulted in an empty plan. Aborting workflow generation.")
            return {
                "name": "Empty_Workflow",
                "description": "Workflow generation failed because the blueprint could not be deconstructed into actions.",
                "tasks": {},
                "dependencies": {}
            }

        # Step 2: Formulate the problem for the solver (currently a placeholder)
        # optimization_problem = self.formulate_optimization_problem(deconstruction)
        
        # Step 3: Invoke the solver (conceptual)
        # For now, we will just use the sequence from the deconstruction.
        # solver_solution = {"route": list(deconstruction.get("tasks", {}).keys())} # Placeholder
        # logger.info(f"Solver found optimal path: {solver_solution['route']}")
        
        # Step 4: Translate the deconstruction back to a workflow
        executable_workflow = self.translate_solution_to_workflow(deconstruction)
        
        logger.info("Strategic workflow generation complete.")
        return executable_workflow

# Example usage:
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Mock LLM and Solver for demonstration
    class MockLLM:
        def generate_text(self, prompt: str, model: str) -> str:
            # Simulate a simple LLM response for demonstration
            if "Forge the CognitiveOperationalBridgE" in prompt:
                return json.dumps({
                    "tasks": {
                        "A": {"action_type": "create_universal_ledger", "inputs": {}},
                        "B": {"action_type": "refactor_logger", "inputs": {}},
                        "C": {"action_type": "integrate_scribe_actions", "inputs": {}}
                    },
                    "dependencies": {
                        "B": ["A"],
                        "C": ["A"]
                    }
                })
            elif "Establish a universal ledger" in prompt:
                return json.dumps({
                    "tasks": {
                        "A": {"action_type": "create_universal_ledger", "inputs": {}},
                        "B": {"action_type": "refactor_logger", "inputs": {}},
                        "C": {"action_type": "integrate_scribe_actions", "inputs": {}}
                    },
                    "dependencies": {
                        "B": ["A"],
                        "C": ["A"]
                    }
                })
            else:
                return json.dumps({
                    "tasks": {
                        "A": {"action_type": "create_universal_ledger", "inputs": {}},
                        "B": {"action_type": "refactor_logger", "inputs": {}},
                        "C": {"action_type": "integrate_scribe_actions", "inputs": {}}
                    },
                    "dependencies": {
                        "B": ["A"],
                        "C": ["A"]
                    }
                })

    class MockSolver:
        pass
        
    planner = StrategicWorkflowPlanner(llm_provider=MockLLM(), solver=MockSolver())
    
    blueprint = "Forge the CognitiveOperationalBridgE by first creating a Universal Ledger, then refactoring the system to use it, and finally integrating the Scribe's actions."
    
    final_workflow = planner.generate_workflow_from_blueprint(blueprint)
    
    print("\n--- Generated Workflow ---")
    print(json.dumps(final_workflow, indent=2))
    print("------------------------")


