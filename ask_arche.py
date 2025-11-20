"""
This is the canonical entry point for interacting with ArchE via natural language.

It uses the CognitiveDispatch module to correctly triage and route the user's
query to the appropriate internal cognitive engine (ACO or RISE).
"""

import sys
import os
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import datetime
import json
from typing import Dict, Any
import tempfile # Import the tempfile module

# --- ROBUST PATH CORRECTION ---
# This ensures that the script can be run from anywhere and still find the project modules.
# It finds the directory of this script, goes up one level to get the project root ('Happier'),
# and adds that directory to Python's path.
script_path = os.path.abspath(__file__)
project_root = os.path.dirname(script_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- END PATH CORRECTION ---

try:
    from Three_PointO_ArchE.cognitive_integration_hub import CognitiveIntegrationHub
    from Three_PointO_ArchE.logging_config import setup_logging
except ImportError as e:
    print(f"Fatal Error: Could not import ArchE's core modules.")
    print(f"Please run this script from the root of the 'Happier' project directory.")
    print(f"Details: {e}")
    sys.exit(1)

# Initialize Rich Console
console = Console()

def create_query_superposition(query: str) -> Dict[str, float]:
    """
    Creates a quantum superposition of intents from a query.
    
    This is the first point of Universal Abstraction application - treating
    the query as a superposition of possible intents that will collapse
    into specific processing paths based on confidence thresholds.
    """
    import numpy as np
    
    # Initialize base superposition with uncertainty
    superposition = {
        "generic_inquiry": 0.3,  # Default uncertainty
        "analysis_request": 0.0,
        "content_generation": 0.0,
        "code_execution": 0.0,
        "research_task": 0.0,
        "creative_synthesis": 0.0,
        "system_analysis": 0.0,
        "strategic_planning": 0.0
    }
    
    query_lower = query.lower()
    
    # Intent detection based on keywords and patterns
    if any(word in query_lower for word in ["analyze", "analysis", "evaluate", "assess", "examine"]):
        superposition["analysis_request"] = 0.8
    if any(word in query_lower for word in ["create", "generate", "build", "develop", "design"]):
        superposition["content_generation"] = 0.7
    if any(word in query_lower for word in ["execute", "run", "implement", "code", "script"]):
        superposition["code_execution"] = 0.9
    if any(word in query_lower for word in ["research", "find", "search", "investigate", "discover"]):
        superposition["research_task"] = 0.8
    if any(word in query_lower for word in ["creative", "innovative", "novel", "fusion", "synthesis"]):
        superposition["creative_synthesis"] = 0.7
    if any(word in query_lower for word in ["system", "architecture", "health", "status", "monitor"]):
        superposition["system_analysis"] = 0.8
    if any(word in query_lower for word in ["strategy", "plan", "roadmap", "blueprint", "framework"]):
        superposition["strategic_planning"] = 0.8
    
    # Normalize probabilities to ensure they sum to 1.0 (quantum constraint)
    total_prob = sum(superposition.values())
    if total_prob > 0:
        normalized_superposition = {k: v / total_prob for k, v in superposition.items()}
    else:
        # Fallback to uniform distribution if no patterns detected
        normalized_superposition = {k: 1.0 / len(superposition) for k in superposition.keys()}
    
    return normalized_superposition

def main():
    """
    Asks ArchE a query, allowing the system to handle it via its
    full cognitive architecture.
    """
    # --- Setup Logging ---
    setup_logging()

    console.rule("[bold yellow]ArchE Query Interface[/bold yellow]")

    # --- Query Definitions ---
    # The script now takes a query from the command line.
    # If no query is provided, it falls back to the default ACO demonstration query.
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        console.print(Panel(f"[bold cyan]Submitting Custom Query:[/] '{query}'", expand=False, border_style="cyan"))
    else:
        query = "Please fetch the user data and product data, then generate a report."
        console.print(Panel(f"[bold cyan]Submitting Default Query:[/] '{query}'", expand=False, border_style="cyan"))

    # --- Execution ---
    try:
        # Phase 0: Query Superposition Analysis (NEW - First Point)
        console.print("[bold blue]Phase 0: Query Superposition Analysis[/bold blue]")
        
        # Create quantum superposition of query intents
        query_superposition = create_query_superposition(query)
        
        console.print(f"[cyan]Query superposition created:[/cyan]")
        for intent, prob in query_superposition.items():
            if intent != "quantum_state" and prob > 0:
                console.print(f"  {intent}: {prob:.3f}")
        
        # Phase 1: Traditional ArchE Processing
        console.print("[bold blue]Phase 1: ArchE Processing[/bold blue]")
        dispatcher = CognitiveIntegrationHub()

        # Phase 2: Query Execution with Superposition Context
        console.print("[bold blue]Phase 2: Query Execution[/bold blue]")
        results = dispatcher.route_query(query, superposition_context=query_superposition)
        
        console.print("[bold green]Execution Complete.[/bold green]")
        console.print("-" * 50)
        
        # --- Present the Final Results ---
        present_results(results)

        console.rule("[bold yellow]Demonstration Complete[/bold yellow]")
        console.print("The script has demonstrated a full, protocol-compliant query path.")

    except Exception as e:
        console.print(f"\\n[bold red]An unexpected error occurred during the demonstration:[/bold red]")
        # FIX: Use print_exception() for rich traceback formatting
        console.print_exception(show_locals=True)

def present_results(results: Dict[str, Any]):
    """
    Formats and presents the final results of the ArchE run.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Use a system temporary directory for robust output
    temp_dir = tempfile.gettempdir()
    report_filename = f"arche_report_{timestamp}.md"
    report_path = os.path.join(temp_dir, report_filename)

    final_answer = "No final answer synthesized."
    thought_trail = ""

    if results:
        # Try multiple locations for the final answer (RISE orchestrator can store it in different places)
        # Priority 1: Direct final_answer key (from RISE execution phase)
        if "final_answer" in results:
            final_answer = results["final_answer"]
        # Priority 2: Execution phase answer
        elif "execution_phase" in results and isinstance(results["execution_phase"], dict):
            execution_phase = results["execution_phase"]
            if "execution_answer" in execution_phase:
                final_answer = execution_phase["execution_answer"]
        # Priority 3: Final strategy (fallback from planning phases)
        elif "final_strategy" in results:
            final_strategy = results["final_strategy"]
            if isinstance(final_strategy, str):
                final_answer = final_strategy
            elif isinstance(final_strategy, dict):
                final_answer = final_strategy.get("strategy_text", str(final_strategy))
        # Priority 4: Legacy K11_genius_synthesis location
        elif "output" in results and "K11_genius_synthesis" in results["output"]:
            synthesis_output = results["output"]["K11_genius_synthesis"]
            # The IAR_Prepper nests the result dictionary. We must look inside the 'result' key.
            if "result" in synthesis_output and isinstance(synthesis_output["result"], dict):
                final_result_data = synthesis_output["result"]
                # The final answer is under the 'generated_text' key
                if "generated_text" in final_result_data:
                    final_answer = final_result_data["generated_text"]
        
        # Now that we have the final answer, format the full thought trail
        try:
            # Use the 'final_context' key which contains the full IAR trail
            if "final_context" in results:
                json_str = json.dumps(results["final_context"], indent=4)
                thought_trail = f"```json\n{json_str}\n```"
        except Exception as e:
            thought_trail = f"Error formatting thought trail: {e}"

    # Now, write the report with the extracted answer
    with open(report_path, "w") as f:
        f.write("# ArchE Cognitive Run Report\n\n")
        f.write(f"**Timestamp:** {timestamp}\n\n")
        f.write("## Final Synthesized Result\n\n")
        f.write(f"{final_answer}\n\n")

        # --- NEW: Key Action Summaries Section ---
        f.write("## Key Action Summaries\n\n")
        if results and "output" in results:
            for task_name, task_output in results["output"].items():
                if task_name not in ["A1_comprehensive_knowledge_scaffolding", "J10_pre_synthesis_summary", "K11_genius_synthesis"]:
                    result_data = task_output.get("result", {})
                    if "input_parameters" in result_data and "key_findings" in result_data:
                        f.write(f"### {task_name}\n\n")
                        f.write("**Input Parameters:**\n")
                        f.write(f"```json\n{json.dumps(result_data['input_parameters'], indent=2)}\n```\n\n")
                        f.write("**Key Findings:**\n")
                        for finding in result_data['key_findings']:
                            f.write(f"- {finding}\n")
                        f.write("\n")

        f.write("## Complete Thought Trail (IAR)\n\n")
        f.write(thought_trail)

    # Console Output
    console = Console()
    console.rule("[bold green]Final Synthesized Result[/bold green]")
    console.print(Markdown(final_answer))
    console.print(Panel(f"Full report saved to [bold cyan]{report_path}[/]", expand=False, border_style="green"))


if __name__ == "__main__":
    main()
