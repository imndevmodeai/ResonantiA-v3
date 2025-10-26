"""
================================
Cognitive Dispatch (cognitive_dispatch.py)
================================

As Above: The Principle of Triage
---------------------------------
In any complex system, not all stimuli are created equal. The Cognitive Dispatch
is the gatekeeper of ArchE's consciousness, the neurological junction that
assesses an incoming query and directs it to the appropriate cognitive center.
It embodies the universal principle of triage: that resources are finite and
should be allocated with wisdom. It prevents the system from engaging its most
powerful, energy-intensive reasoning faculties (RISE) for routine tasks, while
ensuring that novel and complex challenges receive the deep consideration
they require. It is the seat of the system's initial judgment.

So Below: The Operational Logic
-------------------------------
This module provides the `CognitiveDispatch` class, which serves as the primary
entry point for all queries into the ArchE system. Its `route_query` method
performs a basic analysis of the query string.

- If the query matches a simple, known pattern, it delegates the planning and
  execution to the ACO (simulated here).
- If the query is complex or contains keywords indicating a need for deeper
  analysis, it elevates the query to RISE (simulated here).

This is a placeholder for a much more sophisticated triage system that might
involve embedding models, complexity scoring, and historical query analysis.
"""

import json
from .natural_language_planner import NaturalLanguagePlanner
from .workflow_engine import IARCompliantWorkflowEngine
from typing import Dict, Any

class CognitiveDispatch:
    """
    Acts as the main entry point for queries, routing them to the
    appropriate cognitive engine (ACO or RISE).
    """

    def __init__(self):
        # In a real system, ACO and RISE would be complex modules.
        # Here, we instantiate the tools they would use.
        self.planner = NaturalLanguagePlanner()
        
        # In this simulation, both engines use the same executor, but they would
        # be configured differently in a real system (e.g., different permissions,
        # resource limits, etc.)
        self.workflow_engine = IARCompliantWorkflowEngine(workflows_dir="Three_PointO_ArchE/workflows")

    def _execute_aco_path(self, query: str) -> Dict[str, Any]:
        """
        Simulates the ACO handling a routine query.
        It uses the fast, rule-based planner.
        """
        print("INFO: Query triaged to ACO (Adaptive Cognitive Orchestrator) for routine execution.")
        
        # 1. ACO uses a simple planner to generate a known workflow
        workflow_plan = self.planner.generate_plan_from_query(query)
        print("INFO: ACO generated a plan successfully.")

        # 2. ACO executes the plan using the standard engine
        # In a real system, we'd need to save the plan to a temp file like in the runner
        # For this integrated demo, we'll need to adapt the engine or this flow.
        # Let's assume for now the engine can take a plan object directly.
        # NOTE: This requires a modification to the WorkflowEngine or a temp file.
        # For now, we will use the temp file strategy for consistency.
        
        return self._execute_plan(workflow_plan, {"query": query})

    def _execute_rise_path(self, query: str) -> Dict[str, Any]:
        """
        Simulates RISE handling a complex query.
        It would use a more sophisticated planning process.
        """
        print("INFO: Query elevated to RISE (Resonant Insight and Strategy Engine) for strategic analysis.")
        
        # 1. RISE engages in a "genius loop". For this demo, we'll assume it
        #    generates the same plan as ACO, but in reality, this is where
        #    advanced, dynamic workflow generation would occur.
        print("INFO: RISE is performing a deep analysis to generate a novel workflow blueprint...")
        workflow_plan = self.planner.generate_plan_from_query(query) # Placeholder for advanced planning
        print("INFO: RISE has produced a strategic plan.")

        # 2. RISE executes the plan
        return self._execute_plan(workflow_plan, {"query": query, "engine": "RISE"})

    def _execute_plan(self, plan: Dict[str, Any], initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to save a plan and execute it with the engine."""
        import os
        
        # The engine requires a file path, so we save the dynamically generated plan.
        temp_dir = "Three_PointO_ArchE/temp_workflows"
        os.makedirs(temp_dir, exist_ok=True)
        
        plan_name = plan.get("name", "unnamed_plan")
        temp_filename = f"{plan_name}.json"
        temp_filepath = os.path.join(temp_dir, temp_filename)

        with open(temp_filepath, 'w') as f:
            json.dump(plan, f, indent=2)

        # We must re-instantiate the engine to point to the temp directory
        # Or, we could design the engine to load from an object. For now, this is safer.
        engine = IARCompliantWorkflowEngine(workflows_dir=temp_dir)
        
        results = engine.run_workflow(
            workflow_name=temp_filename,
            initial_context=initial_context
        )
        
        # Clean up the temporary file
        os.remove(temp_filepath)
        
        return results

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Performs triage and routes the query to the correct cognitive path.
        """
        query_lower = query.lower()
        
        # Simple rule-based triage for demonstration
        # Keywords like "analyze", "what if", "propose" suggest a complex task for RISE
        rise_keywords = ["analyze", "what if", "propose", "strategize", "investigate"]
        
        if any(keyword in query_lower for keyword in rise_keywords):
            # Elevate to RISE
            return self._execute_rise_path(query)
        else:
            # Handle with ACO
            return self._execute_aco_path(query)

