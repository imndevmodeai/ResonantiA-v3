import json
import os
from typing import Dict, Any, Optional, List

class WorkflowOrchestrator:
    """
    Manages the discovery, loading, and execution of cognitive routines (workflows)
    based on a central registry. This decouples the system's core logic from the
    physical location of workflow files, enabling modularity and resilience.
    """
    _instance = None

    def __new__(cls, registry_path: str = 'core_workflows/registry.json'):
        if cls._instance is None:
            cls._instance = super(WorkflowOrchestrator, cls).__new__(cls)
            cls._instance.registry_path = registry_path
            cls._instance.registry = cls._instance.load_registry()
            cls._instance.workflows = cls._instance.flatten_workflows()
        return cls._instance

    def load_registry(self) -> Dict[str, Any]:
        """Loads the workflow registry file."""
        if not os.path.exists(self.registry_path):
            raise FileNotFoundError(f"Workflow registry not found at: {self.registry_path}")
        with open(self.registry_path, 'r') as f:
            return json.load(f)

    def flatten_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Creates a flat dictionary of workflows for quick lookup by ID."""
        flat_map = {}
        for category_data in self.registry.get('categories', {}).values():
            for workflow in category_data.get('workflows', []):
                if 'id' in workflow:
                    flat_map[workflow['id']] = workflow
        return flat_map

    def get_workflow_details(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the details (path, description) for a given workflow ID.

        Args:
            workflow_id: The unique identifier of the workflow.

        Returns:
            A dictionary containing the workflow's details, or None if not found.
        """
        return self.workflows.get(workflow_id)

    def get_workflow_path(self, workflow_id: str) -> Optional[str]:
        """
        Gets the file path for a given workflow ID.

        Args:
            workflow_id: The unique identifier of the workflow.

        Returns:
            The file path as a string, or None if the ID is not found.
        """
        details = self.get_workflow_details(workflow_id)
        return details.get('path') if details else None

    def list_workflows(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists all available workflows, optionally filtered by category.
        """
        if category:
            return self.registry.get('categories', {}).get(category, {}).get('workflows', [])
        return list(self.workflows.values())

    def select_workflow_for_query(self, query: str) -> Optional[str]:
        """
        Selects the most appropriate workflow for a given query using a simple
        keyword-based scoring system. This is a basic implementation of the ACO's
        routing logic.
        """
        scores: Dict[str, int] = {wf_id: 0 for wf_id in self.workflows.keys()}
        query_lower = query.lower()

        # Define keyword mappings to boost scores for specific intents
        keyword_map = {
            'temporal_forecasting_workflow': ['forecast', 'predict', 'future', 'project', 'estimate'],
            'temporal_causal_analysis_workflow': ['why', 'cause', 'impact', 'effect', 'reason', 'correlation', 'affect'],
            'agentic_research': ['research', 'find information', 'what is', 'who is', 'summarize', 'look up'],
            'tesla_visioning_workflow': ['design', 'create', 'invent', 'conceptualize', 'framework', 'build a plan for'],
        }

        # Score based on direct keyword mapping
        for wf_id, keywords in keyword_map.items():
            for keyword in keywords:
                if keyword in query_lower:
                    scores[wf_id] += 5  # High score for a direct keyword match

        # Generic scoring based on word overlap in the workflow's description
        query_words = set(query_lower.split())
        for wf_id, details in self.workflows.items():
            description_words = set(details.get('description', '').lower().split())
            common_words = description_words.intersection(query_words)
            scores[wf_id] += len(common_words)

        # Find the workflow with the highest score
        if not any(s > 0 for s in scores.values()):
            print("INFO: No specific keywords matched. Defaulting to RISE engine for deep analysis.")
            return 'rise_cognitive_scaffolding_and_grounding'

        best_workflow_id = max(scores, key=scores.get)
        
        # If the best score is low, it's likely a generic query better suited for the full RISE engine
        if scores[best_workflow_id] < 3:
            print("INFO: No specific workflow matched strongly. Defaulting to RISE engine for deep analysis.")
            return 'rise_cognitive_scaffolding_and_grounding'

        return best_workflow_id

    def search_workflows(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Performs a simple search across workflow IDs and descriptions.

        Args:
            search_term: The term to search for (case-insensitive).

        Returns:
            A list of matching workflow detail dictionaries.
        """
        results = []
        term = search_term.lower()
        for workflow_id, details in self.workflows.items():
            if term in workflow_id.lower() or term in details.get('description', '').lower():
                results.append(details)
        return results

    def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a workflow by its ID.

        NOTE: This is a placeholder for integration with the full IARCompliantWorkflowEngine.
              In a real implementation, this method would instantiate and run the engine
              with the workflow definition loaded from the path.
        """
        print(f"--- [WorkflowOrchestrator] ---")
        print(f"REQUEST: SIMULATE execution of workflow '{workflow_id}'")
        
        workflow_path = self.get_workflow_path(workflow_id)
        if not workflow_path:
            print(f"ERROR: Workflow ID '{workflow_id}' not found in registry.")
            return {"status": "error", "message": "Workflow not found"}
            
        if not os.path.exists(workflow_path):
            print(f"ERROR: Workflow file not found at path: {workflow_path}")
            return {"status": "error", "message": "Workflow file missing"}

        print(f"INFO: Loading workflow definition from: {workflow_path}")
        # Placeholder for actual execution engine logic
        print(f"INFO: Simulating execution with inputs: {inputs}")
        print(f"SUCCESS: Workflow '{workflow_id}' simulation complete.")
        print(f"---------------------------------")
        
        return {
            "status": "simulated_success",
            "workflow_id": workflow_id,
            "inputs": inputs,
            "output": {"message": "Placeholder output from simulated execution."}
        }

if __name__ == '__main__':
    # --- DEMONSTRATION OF DYNAMIC ORCHESTRATOR (ACO) USAGE ---
    try:
        orchestrator = WorkflowOrchestrator()

        print("--- Workflow Orchestrator (ACO Simulation) Initialized ---")
        print("This is a basic simulation of the ACO's dynamic dispatch.")
        print("Enter a query, and the orchestrator will select and run the best workflow.")
        print("Example queries:")
        print("  'forecast the stock price'")
        print("  'what is the impact of gdp on inflation?'")
        print("  'design a new cognitive protocol'")
        print("  'tell me about the ResonantiA Protocol'")
        print("Type 'quit' to exit.")

        while True:
            user_query = input("\nEnter your query: ")
            if user_query.lower() == 'quit':
                break
            
            if not user_query:
                continue

            print(f"\n[ACO] Analyzing query: '{user_query}'")
            selected_workflow_id = orchestrator.select_workflow_for_query(user_query)
            
            if selected_workflow_id:
                details = orchestrator.get_workflow_details(selected_workflow_id)
                print(f"[ACO] Best workflow selected: '{selected_workflow_id}'")
                print(f"[ACO] Reason: {details.get('description')}")
                
                # In a real system, we would dynamically construct the inputs based on the workflow's schema.
                # For this demo, we'll just pass the raw query.
                simulated_inputs = {"user_query": user_query}
                
                orchestrator.execute_workflow(selected_workflow_id, simulated_inputs)
            else:
                # This case is unlikely with the default fallback, but included for completeness
                print("[ACO] Could not determine a suitable workflow for the query.")

    except FileNotFoundError as e:
        print(f"FATAL ERROR: Could not initialize orchestrator. {e}")
