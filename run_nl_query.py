import logging
import sys
import os
import json
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.syntax import Syntax

# Ensure the Three_PointO_ArchE package is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
    from Three_PointO_ArchE.natural_language_planner import NaturalLanguagePlanner
except ImportError as e:
    print(f"Error: Could not import necessary modules.")
    print(f"Please ensure you are running this script from the root of the 'Happier' project directory.")
    print(f"Details: {e}")
    sys.exit(1)

def setup_logging():
    """Sets up logging to display INFO level messages to the console."""
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[RichHandler(console=Console(), rich_tracebacks=True, show_path=False)]
    )
    logging.getLogger("Three_PointO_ArchE.workflow_engine").setLevel(logging.INFO)

def save_temp_workflow(plan: dict, directory: str) -> str:
    """Saves the generated workflow to a temporary file for the engine to read."""
    os.makedirs(directory, exist_ok=True)
    temp_file_name = f"temp_workflow_{plan['name']}.json"
    temp_file_path = os.path.join(directory, temp_file_name)
    with open(temp_file_path, 'w') as f:
        json.dump(plan, f, indent=2)
    return temp_file_name

def main():
    """
    Takes a natural language query, generates a plan, and executes it.
    """
    console = Console()
    console.rule("[bold magenta]Natural Language to Optimized Workflow Demonstration[/bold magenta]")

    setup_logging()
    
    # The natural language query that will be planned and executed
    nl_query = "Please fetch the latest user data and the current product information, then generate a report."

    console.print(Panel(f"[bold cyan]Natural Language Query:[/] '{nl_query}'", expand=False, border_style="cyan"))

    try:
        # Step 1: Generate the plan from the query
        planner = NaturalLanguagePlanner()
        workflow_plan = planner.generate_plan_from_query(nl_query)

        console.print("\n[yellow]Step 1: Plan Generation[/yellow]")
        console.print("The Natural Language Planner has generated the following workflow:")
        
        plan_syntax = Syntax(json.dumps(workflow_plan, indent=2), "json", theme="monokai", line_numbers=True)
        console.print(plan_syntax)
        console.print("Notice the two independent tasks and one dependent task, creating an opportunity for optimization.")

        # Step 2: Execute the generated plan
        console.print("\n[yellow]Step 2: Optimized Execution[/yellow]")
        
        engine_root = os.path.join(project_root, "Three_PointO_ArchE")
        temp_workflows_dir = os.path.join(engine_root, "temp_workflows")

        # The engine needs a file to load, so we save our dynamic plan to a temporary file
        temp_workflow_filename = save_temp_workflow(workflow_plan, temp_workflows_dir)
        
        engine = IARCompliantWorkflowEngine(workflows_dir=temp_workflows_dir)

        results = engine.run_workflow(
            workflow_name=temp_workflow_filename,
            initial_context={"query": nl_query}
        )
        
        console.rule("[bold blue]Workflow Execution Complete[/bold blue]")
        console.print("\n[cyan]Final Results:[/]")
        console.print(json.dumps(results, indent=2))

        console.print("\n[bold yellow]Analysis:[/]")
        console.print("As before, observe the log messages. The dynamically generated plan was successfully [bold]optimized into two stages[/bold] and executed.")
        console.print("[bold green]This demonstrates the complete pipeline: from natural language intent to intelligent, optimized action.[/bold green]")
        
        # Clean up the temporary file
        os.remove(os.path.join(temp_workflows_dir, temp_workflow_filename))

    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red]")
        console.log(e, exc_info=True)

if __name__ == "__main__":
    main()

