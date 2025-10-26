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

        if not tasks:
            raise ValueError("Could not generate any tasks from the query. Please be more specific.")

        workflow_plan = {
            "name": f"Dynamic_Workflow_for_Query_{hash(query)}",
            "tasks": tasks,
            "dependencies": dependencies
        }

        return workflow_plan

