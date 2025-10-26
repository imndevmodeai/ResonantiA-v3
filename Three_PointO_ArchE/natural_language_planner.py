"""
================================
Natural Language Planner (natural_language_planner.py)
================================

As Above: The Principle of Emergent Order
------------------------------------------
Intent, when spoken, is a wave of possibility. The Natural Language Planner
is the lens that focuses this wave into a coherent beam of action. It embodies
the principle that order can emerge from the chaos of language. By recognizing
patterns, keywords, and causal relationships within a query, it can crystallize
a fluid human request into the rigid, logical structure of a Process Blueprint.
It is the bridge between the world of ideas and the world of execution.

So Below: The Operational Logic
-------------------------------
This module provides the `NaturalLanguagePlanner` class. It takes a natural
language query and, using a set of predefined rules, generates a workflow
definition dictionary that can be executed by the IARCompliantWorkflowEngine.
In a production system, this would be backed by a sophisticated LLM, but for
demonstration, it uses keyword matching to construct tasks and their dependencies.
"""

import json
from typing import Dict, Any, List

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now, now_iso, ago, from_now, format_log, format_filename


class NaturalLanguagePlanner:
    """
    Generates a workflow plan from a natural language query.
    """

    def __init__(self):
        # In a real system, we might pass in an action registry to validate
        # generated actions. For this demo, it's self-contained.
        pass

    def generate_plan_from_query(self, query: str) -> Dict[str, Any]:
        """
        Parses a query and generates a structured workflow plan.

        Args:
            query (str): The natural language input from the user.

        Returns:
            A dictionary representing the workflow definition.
        """
        query_lower = query.lower()
        tasks = {}
        dependencies = {}

        # Rule 1: Look for fetching user data
        if "user data" in query_lower:
            tasks["A_fetch_user_data"] = {
                "action_type": "display_output",
                "description": "Simulates fetching user data based on the NL query.",
                "inputs": { "content": "Fetched user data for user_id 123" }
            }

        # Rule 2: Look for fetching product data
        if "product data" in query_lower or "product information" in query_lower:
            tasks["B_fetch_product_data"] = {
                "action_type": "display_output",
                "description": "Simulates fetching product data based on the NL query.",
                "inputs": { "content": "Fetched product data for product_id 456" }
            }
        
        # Rule 3: Look for generating a report
        if "generate" in query_lower and "report" in query_lower:
            report_task_id = "C_generate_report"
            report_dependencies = []
            
            # If the report is generated, it likely depends on the data fetching tasks
            if "A_fetch_user_data" in tasks:
                report_dependencies.append("A_fetch_user_data")
            if "B_fetch_product_data" in tasks:
                report_dependencies.append("B_fetch_product_data")

            tasks[report_task_id] = {
                "action_type": "display_output",
                "description": "Generates a report using previously fetched data.",
                "inputs": {
                    "content": "Generated report using data from prior steps."
                }
            }
            if report_dependencies:
                dependencies[report_task_id] = report_dependencies

        # Rule 4: Look for date, time, or location
        if any(keyword in query_lower for keyword in ["date", "time", "where", "located"]):
            tasks["D_get_system_info"] = {
                "action_type": "execute_code",
                "description": "Executes a python script to get the current date, time, and location.",
                "inputs": {
                    "code": "import datetime; import geocoder; g = geocoder.ip('me'); print(f'Current Date and Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, Location: {g.city}, {g.country}')"
                }
            }
        
        # Rule 5: Handle NFL prediction queries with QUANTUM CFP ANALYSIS (proper ArchE action)
        if "nfl" in query_lower and ("plays" in query_lower or "game" in query_lower or "thursday" in query_lower or "predict" in query_lower or "odds" in query_lower):
            tasks["E_predict_nfl_game"] = {
                "action_type": "predict_nfl_game",
                "description": "Uses Quantum CFP Evolution to predict NFL game outcome, player performance, and betting odds.",
                "inputs": {
                    "team1": "Kansas City Chiefs",
                    "team2": "Baltimore Ravens",
                    "weather": "normal",
                    "home_team": "Kansas City Chiefs"
                }
            }
            
            # Add a display task to show the results in a formatted way
            tasks["F_display_nfl_results"] = {
                "action_type": "display_output",
                "description": "Display the quantum NFL prediction results in a user-friendly format.",
                "inputs": {
                    "content": "{{ E_predict_nfl_game }}"
                }
            }
            
            dependencies["F_display_nfl_results"] = ["E_predict_nfl_game"]

        # Rule 6: Handle comprehensive AI system analysis queries
        # More specific keywords to avoid false positives
        ai_analysis_keywords = ["ai safety", "ai ethics", "spr definitions", "knowledge base", "error handling", "system optimization"]
        system_analysis_keywords = ["ai system", "current state", "comprehensive report", "gaps", "optimizations"]
        
        # Only trigger for queries that are specifically about AI system analysis
        is_ai_system_analysis = (
            any(keyword in query_lower for keyword in ai_analysis_keywords) or
            (any(keyword in query_lower for keyword in system_analysis_keywords) and 
             ("ai" in query_lower or "system" in query_lower) and
             ("analyze" in query_lower or "analysis" in query_lower))
        )
        
        if is_ai_system_analysis:
            # Phase 1: Web search for recent developments related to the user's query
            tasks["A_search_ai_developments"] = {
                "action_type": "web_search",
                "description": "Search for recent developments related to the user's analysis request",
                "inputs": {
                    "query": query,  # Use the actual user query instead of hardcoded AI safety query
                    "max_results": 10
                }
            }
            
            # Phase 2: Analyze current SPR definitions
            tasks["B_analyze_spr_definitions"] = {
                "action_type": "analyze_spr_definitions",
                "description": "Analyze current SPR definitions for gaps and opportunities",
                "inputs": {
                    "spr_file": "knowledge_graph/spr_definitions_tv.json",
                    "analysis_type": "gap_analysis"
                }
            }
            
            # Phase 3: Evaluate error handling capabilities
            tasks["C_evaluate_error_handling"] = {
                "action_type": "evaluate_error_handling",
                "description": "Analyze current error handling capabilities and suggest optimizations",
                "inputs": {
                    "system_components": ["workflow_engine", "action_registry", "cognitive_dispatch"]
                }
            }
            
            # Phase 4: Generate comprehensive report
            tasks["D_generate_comprehensive_report"] = {
                "action_type": "generate_comprehensive_report",
                "description": "Synthesize all analysis results into a comprehensive report with recommendations",
                "inputs": {
                    "sources": ["{{ A_search_ai_developments }}", "{{ B_analyze_spr_definitions }}", "{{ C_evaluate_error_handling }}"],
                    "report_type": "ai_system_analysis",
                    "include_recommendations": True
                }
            }
            
            # Set dependencies
            dependencies["D_generate_comprehensive_report"] = ["A_search_ai_developments", "B_analyze_spr_definitions", "C_evaluate_error_handling"]

        # Rule 7: Handle SPR-specific queries
        if "spr" in query_lower and ("analyze" in query_lower or "evaluate" in query_lower or "gap" in query_lower):
            tasks["A_spr_analysis"] = {
                "action_type": "analyze_spr_definitions",
                "description": "Perform comprehensive analysis of SPR definitions",
                "inputs": {
                    "spr_file": "knowledge_graph/spr_definitions_tv.json",
                    "analysis_type": "comprehensive"
                }
            }
            
            tasks["B_spr_recommendations"] = {
                "action_type": "generate_spr_recommendations",
                "description": "Generate recommendations for SPR improvements",
                "inputs": {
                    "analysis_results": "{{ A_spr_analysis }}"
                }
            }
            
            dependencies["B_spr_recommendations"] = ["A_spr_analysis"]

        # Rule 8: Handle web search queries
        if "search" in query_lower and ("recent" in query_lower or "latest" in query_lower or "current" in query_lower):
            search_query = query  # Use the full query as search terms
            tasks["A_web_search"] = {
                "action_type": "web_search",
                "description": "Perform web search for current information",
                "inputs": {
                    "query": search_query,
                    "max_results": 15
                }
            }
            
            tasks["B_synthesize_results"] = {
                "action_type": "synthesize_search_results",
                "description": "Synthesize and analyze search results",
                "inputs": {
                    "search_results": "{{ A_web_search }}",
                    "synthesis_type": "comprehensive"
                }
            }
            
            dependencies["B_synthesize_results"] = ["A_web_search"]

        # Rule 7: General analysis queries (fallback for comprehensive analysis requests)
        if not tasks and ("analyze" in query_lower or "analysis" in query_lower or "research" in query_lower):
            # Phase 1: Web search for the user's specific query
            tasks["A_web_search"] = {
                "action_type": "web_search",
                "description": "Search for information related to the user's analysis request",
                "inputs": {
                    "query": query,  # Use the actual user query
                    "max_results": 10
                }
            }
            
            # Phase 2: Synthesize results
            tasks["B_synthesize_results"] = {
                "action_type": "synthesize_search_results",
                "description": "Synthesize and analyze search results",
                "inputs": {
                    "search_results": "{{ A_web_search }}",
                    "synthesis_type": "comprehensive"
                }
            }
            
            dependencies["B_synthesize_results"] = ["A_web_search"]

        if not tasks:
            raise ValueError("Could not generate any tasks from the query. Please be more specific.")

        workflow_plan = {
            "name": f"Dynamic_Workflow_for_Query_{hash(query)}",
            "tasks": tasks,
            "dependencies": dependencies
        }

        return workflow_plan

