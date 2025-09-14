#!/usr/bin/env python3
"""
Proactive Truth Resonance Framework (PTRF) Demonstration
Based on Keyholder directive and Tesla visioning methodology

This script demonstrates the revolutionary approach to truth-seeking that solves
the "Oracle's Paradox" by proactively identifying uncertainty and targeting
verification efforts at the weakest points in our knowledge model.

Usage: python run_proactive_truth_demo.py
"""

import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path to allow for absolute imports
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.workflow_engine import WorkflowEngine
from Three_PointO_ArchE.utils.log_scribe import LogScribe

def run_proactive_truth_demonstration():
    """
    Runs a demonstration of the Proactive Truth Resonance Framework.
    This workflow takes a complex, potentially contentious user query and
    applies a structured four-phase process to arrive at a deeply
    vetted and synthesized answer.
    """
    scribe = LogScribe(
        log_dir="logs",
        log_level="INFO",
        log_to_console=True,
        log_to_file=True,
        log_filename="proactive_truth_demo.log"
    )

    scribe.info("--- Starting Proactive Truth Resonance Framework Demonstration ---")

    # Define the complex user query for the demonstration
    user_query = "What is the most effective and safe method for long-term carbon sequestration with the fewest negative ecological side effects, considering both natural and artificial technologies?"

    # Define the initial context for the workflow
    initial_context = {
        "user_query": user_query,
        "search_history": [],
        "internal_hypotheses": [],
        "verification_results": [],
        "synthesis_attempts": [],
        "final_answer": None,
        "confidence_threshold": 0.65  # A threshold below which targeted verification is triggered
    }

    scribe.info(f"Initial User Query: {user_query}")
    scribe.info(f"Initial Context: {json.dumps(initial_context, indent=2)}")

    # Define the path to the workflow file
    workflow_file = project_root / "workflows" / "proactive_truth_seeking_workflow.json"

    if not workflow_file.exists():
        scribe.error(f"Workflow file not found at: {workflow_file}")
        return

    # Instantiate the Workflow Engine
    try:
        workflow_engine = WorkflowEngine(str(workflow_file), scribe)
        scribe.info("WorkflowEngine instantiated successfully.")
    except Exception as e:
        scribe.error(f"Failed to instantiate WorkflowEngine: {e}", exc_info=True)
        return

    # Run the workflow
    scribe.info("Executing Proactive Truth Seeking Workflow...")
    final_context = workflow_engine.run(initial_context)

    scribe.info("--- Proactive Truth Resonance Framework Demonstration Complete ---")

    # Display the final results
    if final_context:
        scribe.info("Workflow execution finished. Final Context:")
        print(json.dumps(final_context, indent=4))
        final_answer = final_context.get("final_answer", {})
        print("\n" + "="*80)
        print("                 PROACTIVE TRUTH RESONANCE - FINAL ANSWER")
        print("="*80)
        print(f"User Query: {final_context.get('user_query')}")
        print("-"*80)
        print(f"Synthesized Answer: {final_answer.get('synthesized_answer', 'Not generated.')}")
        print(f"Overall Confidence: {final_answer.get('overall_confidence', 'N/A')}")
        print(f"Key Evidence/Sources: {json.dumps(final_answer.get('key_evidence', []), indent=2)}")
        print(f"Identified Uncertainties: {json.dumps(final_answer.get('uncertainties', []), indent=2)}")
        print("="*80)

    else:
        scribe.warning("Workflow execution did not return a final context.")

if __name__ == "__main__":
    run_proactive_truth_demonstration()