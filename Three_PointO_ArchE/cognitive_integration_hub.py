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
import logging
import tempfile # Import the tempfile module
from Three_PointO_ArchE.natural_language_planner import NaturalLanguagePlanner
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.playbook_orchestrator import PlaybookOrchestrator
from Three_PointO_ArchE.rise_enhanced_synergistic_inquiry import RISEEnhancedSynergisticInquiry
from Three_PointO_ArchE.strategic_workflow_planner import StrategicWorkflowPlanner # Import the new planner
from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator # Import the RISE Orchestrator
from typing import Dict, Any

# Mock solver for now, will be replaced with the real one
from advanced_tsp_solver import AdvancedTSPSolver
from Three_PointO_ArchE.llm_providers.google import GoogleProvider
import os # Import os to access environment variables


logger = logging.getLogger(__name__)

class CognitiveIntegrationHub:
    """
    Acts as the main entry point for queries, routing them to the
    appropriate cognitive engine (ACO or RISE).
    """

    def __init__(self):
        # In a real system, ACO and RISE would be complex modules.
        # Here, we instantiate the tools they would use.
        self.planner = NaturalLanguagePlanner()
        
        # ResonantiA-aware Playbook Orchestrator for genius-level analysis
        self.playbook_orchestrator = PlaybookOrchestrator()
        
        # RISE-Enhanced Synergistic Inquiry Orchestrator for PhD-level analysis
        self.rise_enhanced_orchestrator = RISEEnhancedSynergisticInquiry()
        
        # Instantiate the new Strategic Planner for the RISE path
        # In a real system, these would be properly configured singletons
        
        # Correctly instantiate the GoogleProvider by fetching the API key from the environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
            
        self.strategic_planner = StrategicWorkflowPlanner(
            llm_provider=GoogleProvider(api_key=api_key), 
            solver=AdvancedTSPSolver()
        )

        # In this simulation, both engines use the same executor, but they would
        # be configured differently in a real system (e.g., different permissions,
        # resource limits, etc.)
        self.workflow_engine = IARCompliantWorkflowEngine(workflows_dir="Three_PointO_ArchE/workflows")
        self.rise_orchestrator = RISE_Orchestrator() # Instantiate the orchestrator

    def _execute_aco_path(self, query: str) -> Dict[str, Any]:
        """
        Simulates the ACO handling a routine query.
        It uses the fast, rule-based planner.
        """
        logger.info("Query triaged to ACO (Adaptive Cognitive Orchestrator) for routine execution.")
        
        # 1. ACO uses a simple planner to generate a known workflow
        workflow_plan = self.planner.generate_plan_from_query(query)
        logger.info("ACO generated a plan successfully.")

        # 2. ACO executes the plan using the standard engine
        # In a real system, we'd need to save the plan to a temp file like in the runner
        # For this integrated demo, we'll need to adapt the engine or this flow.
        # Let's assume for now the engine can take a plan object directly.
        # NOTE: This requires a modification to the WorkflowEngine or a temp file.
        # For now, we will use the temp file strategy for consistency.
        
        return self._execute_plan(workflow_plan, {"query": query})

    def _execute_rise_path(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handles a complex query by invoking the full RISE Orchestrator.
        Can receive additional context from specialized upstream orchestrators.
        """
        logger.info("Query elevated to RISE. Engaging RISE_Orchestrator.")
        
        # The new implementation now calls the RISE Orchestrator directly
        try:
            # Pass the original query and any additional context to the orchestrator
            rise_results = self.rise_orchestrator.process_query(
                problem_description=query,
                context=context
            )
            logger.info("RISE Orchestrator has completed its workflow.")
            return rise_results
        except Exception as e:
            logger.error(f"RISE Orchestrator execution failed catastrophically: {e}", exc_info=True)
            return {
                "status": "RISE_EXECUTION_ERROR",
                "error": str(e),
                "details": "The RISE workflow failed to execute. Check the logs for details.",
                "output": {}
            }

    def _execute_plan(self, plan: Dict[str, Any], initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to save a plan and execute it with the engine."""
        import os
        from pathlib import Path
        
        # Save the plan to outputs directory for persistence
        plan_name = plan.get("name", "unnamed_plan")
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        
        # Create a timestamped filename for the plan
        import time
        timestamp = int(time.time())
        plan_filename = f"workflow_plan_{plan_name}_{timestamp}.json"
        plan_filepath = outputs_dir / plan_filename
        
        # Save the plan to outputs directory
        try:
            with open(plan_filepath, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2)
            logger.info(f"Workflow plan saved to: {plan_filepath}")
        except Exception as e:
            logger.warning(f"Failed to save workflow plan to outputs: {e}")
        
        # Execute the workflow directly from the saved plan file
        try:
            # Use the saved plan file directly instead of temporary directory
            engine = IARCompliantWorkflowEngine(workflows_dir=str(outputs_dir))
            
            results = engine.run_workflow(
                workflow_name=plan_filename,
                initial_context=initial_context
            )
        except Exception as e:
            logger.error(f"Workflow execution failed catastrophically: {e}", exc_info=True)
            # Return a structured error that the presentation layer can understand.
            results = {
                "status": "WORKFLOW_EXECUTION_ERROR",
                "error": str(e),
                "details": f"The workflow '{plan_name}' failed to execute. Check the logs for run ID associated with this workflow.",
                "output": {} # Ensure output key exists to prevent downstream crashes
            }
        
        return results

    def route_query(self, query: str, superposition_context: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Routes a query to the appropriate cognitive engine based on
        its complexity and content. Now includes ResonantiA-aware routing and RISE-Enhanced analysis.
        
        Args:
            query: The natural language query string
            superposition_context: Optional quantum superposition of query intents
        """
        # Log superposition context if provided
        if superposition_context:
            logger.info(f"Query superposition context: {superposition_context}")
            
            # Use superposition to influence routing decisions
            analysis_prob = superposition_context.get("analysis_request", 0.0)
            generation_prob = superposition_context.get("content_generation", 0.0)
            research_prob = superposition_context.get("research_task", 0.0)
            
            # Collapse superposition based on highest probability intent
            dominant_intent = max(superposition_context.items(), key=lambda x: x[1] if x[0] != "quantum_state" else 0)
            logger.info(f"Dominant intent from superposition: {dominant_intent[0]} (probability: {dominant_intent[1]:.3f})")
        
        # First check if query contains ResonantiA-specific terminology
        if self._has_resonantia_patterns(query):
            logger.info("ResonantiA Protocol patterns detected! Routing to genius-level Playbook Orchestrator.")
            return self._execute_resonantia_path(query)
        
        # Check for complex queries that would benefit from RISE-Enhanced analysis
        if self._requires_rise_enhanced_analysis(query):
            logger.info("Complex query detected! Routing to RISE-Enhanced Synergistic Inquiry Orchestrator.")
            return self._execute_rise_enhanced_path(query)
        
        # Enhanced routing using superposition context
        if superposition_context:
            # Use superposition probabilities to make routing decisions
            analysis_prob = superposition_context.get("analysis_request", 0.0)
            research_prob = superposition_context.get("research_task", 0.0)
            strategic_prob = superposition_context.get("strategic_planning", 0.0)
            
            # Route to RISE if analysis, research, or strategic planning probabilities are high
            if analysis_prob > 0.6 or research_prob > 0.6 or strategic_prob > 0.6:
                logger.info(f"Superposition-based routing to RISE (analysis: {analysis_prob:.3f}, research: {research_prob:.3f}, strategic: {strategic_prob:.3f})")
                return self._execute_rise_path(query)
        
        # Fallback to traditional keyword-based routing
        rise_keywords = [
            "analyze", "strategy", "complex", "research", "deep", "comprehensive",
            # NEW: Keywords to catch philosophical, architectural, or self-reflective queries
            "dissonance", "resonance", "consciousness", "golem", "unify", "blueprint",
            "architecture", "feedback loop", "system health", "ontological",
            # NEW: Keywords for analytical and synthesis tasks
            "report", "generate", "synthesis", "evaluation", "assessment", "analysis"
        ]
        
        if any(keyword in query.lower() for keyword in rise_keywords):
            return self._execute_rise_path(query)
        else:
            return self._execute_aco_path(query)
    
    def _has_resonantia_patterns(self, query: str) -> bool:
        """
        Check if query contains ResonantiA-specific terminology.
        """
        resonantia_keywords = [
            "knowledge scaffolding", "ptrf", "proactive truth resonance framework",
            "solidified truth packet", "causal inference", "causal lag detection",
            "rise analysis", "sirc", "synergistic intent resonance cycle",
            "cfp", "comparative fluxual processing", "temporal resonance",
            "abm", "agent-based modeling", "digital resilience twin"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in resonantia_keywords)
    
    def _execute_resonantia_path(self, query: str) -> Dict[str, Any]:
        """
        Uses the PlaybookOrchestrator to generate a dynamic, GENIUS-LEVEL workflow
        and then passes that workflow blueprint to the main RISE_Orchestrator for execution.
        """
        logger.info("Executing ResonantiA Protocol path: Dynamic Workflow Generation -> RISE Execution.")
        
        try:
            # 1. Generate the dynamic, genius-level workflow using the Playbook Orchestrator
            dynamic_workflow_plan = self.playbook_orchestrator.analyze_query_for_resonantia_patterns(query)
            
            # Extract the name of the generated plan for execution
            # This requires saving the plan and having the engine load it.
            # For a more integrated approach, we can pass the plan name to RISE.
            
            # Save the dynamic workflow to the outputs directory to make it executable
            import os
            import time
            from pathlib import Path

            outputs_dir = Path("outputs")
            outputs_dir.mkdir(exist_ok=True)
            timestamp = int(time.time())
            plan_name = dynamic_workflow_plan.get("name", "unnamed_genius_plan")
            plan_filename = f"dynamic_workflow_{plan_name}_{timestamp}.json"
            plan_filepath = outputs_dir / plan_filename
            
            with open(plan_filepath, 'w', encoding='utf-8') as f:
                json.dump(dynamic_workflow_plan, f, indent=2)
            logger.info(f"Dynamically generated ResonantiA workflow saved to: {plan_filepath}")

            # 2. Prepare context for the RISE Orchestrator
            # We are telling RISE to use our dynamically generated workflow for Phase A
            # instead of its default "knowledge_scaffolding.json".
            rise_context = {
                "execution_mode": "resonantia_playbook",
                "phase_a_workflow_blueprint": plan_filename,
                "workflows_dir_override": str(outputs_dir) # Tell the engine where to find this dynamic plan
            }

            # 3. Execute the main RISE path with the specialized context
            logger.info(f"Passing dynamically generated workflow '{plan_filename}' to RISE_Orchestrator.")
            return self._execute_rise_path(query, context=rise_context)

        except Exception as e:
            logger.error(f"ResonantiA path execution failed catastrophically: {e}", exc_info=True)
            # Fallback to the standard RISE path if dynamic generation fails
            return self._execute_rise_path(query, context={"error_fallback": True, "reason": str(e)})
    
    def _requires_rise_enhanced_analysis(self, query: str) -> bool:
        """
        Check if query requires RISE-Enhanced analysis based on complexity indicators.
        """
        complexity_indicators = [
            "tactical analysis", "blow-by-blow", "detailed breakdown", "comprehensive analysis",
            "strategic briefing", "multi-factor", "complex dynamics", "systematic approach",
            "in-depth", "thorough", "extensive", "detailed explanation", "complete analysis",
            "who would win", "battle analysis", "combat analysis", "tactical breakdown"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in complexity_indicators)
    
    def _execute_rise_enhanced_path(self, query: str) -> Dict[str, Any]:
        """
        Uses the RISEEnhancedSynergisticInquiry orchestrator to perform a deep
        analysis of the query, then passes the resulting insights and context
        into the main RISE_Orchestrator for execution.
        """
        logger.info("Executing RISE-Enhanced Synergistic Inquiry path: Deep Analysis -> RISE Execution.")
        
        try:
            # 1. Perform the deep, PhD-level analysis of the query
            enhanced_analysis_results = self.rise_enhanced_orchestrator.execute_rise_enhanced_inquiry(query)
            
            # 2. Prepare the context for the main RISE Orchestrator
            # This context will enrich the standard RISE workflow with deeper initial understanding.
            rise_context = {
                "execution_mode": "rise_enhanced_inquiry",
                "initial_query_analysis": enhanced_analysis_results.get("rise_analysis"),
                "detected_resonantia_patterns": enhanced_analysis_results.get("resonantia_patterns"),
                "analytical_approach": enhanced_analysis_results.get("analytical_approach")
            }
            
            # 3. Execute the main RISE path with the enhanced context
            logger.info("Passing enhanced analysis context to RISE_Orchestrator.")
            return self._execute_rise_path(query, context=rise_context)
            
        except Exception as e:
            logger.error(f"RISE-Enhanced path execution failed catastrophically: {e}", exc_info=True)
            # Fallback to the standard RISE path if the enhanced analysis fails
            return self._execute_rise_path(query, context={"error_fallback": True, "reason": str(e)})

