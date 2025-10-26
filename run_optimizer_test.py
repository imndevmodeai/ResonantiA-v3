import logging
import sys
import os
from rich.console import Console
from rich.logging import RichHandler

# Ensure the Three_PointO_ArchE package is in the Python path
# This assumes the script is run from the root of the Happier project
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
except ImportError as e:
    print(f"Error: Could not import IARCompliantWorkflowEngine.")
    print(f"Please ensure you are running this script from the root of the 'Happier' project directory.")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

def setup_logging():
    """Sets up logging to display INFO level messages to the console."""
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[RichHandler(console=Console(), rich_tracebacks=True)]
    )
    # Set the workflow engine's logger to INFO to see the optimization stages
    logging.getLogger("Three_PointO_ArchE.workflow_engine").setLevel(logging.INFO)

def main():
    """
    Runs the optimizer test workflow and demonstrates the parallel execution plan.
    """
    console = Console()
    console.rule("[bold green]Workflow Optimizer Demonstration[/bold green]")

    setup_logging()

    try:
        # The engine will look for workflows in the "Three_PointO_ArchE/workflows" directory by default
        # if we adjust its workflows_dir attribute.
        engine_root = os.path.join(project_root, "Three_PointO_ArchE")
        engine = IARCompliantWorkflowEngine(workflows_dir=os.path.join(engine_root, "workflows"))

        workflow_file_name = "optimizer_test_workflow.json"
        initial_context = {"user_id": 123}

        console.print(f"\n[cyan]Executing workflow:[/] [bold]{workflow_file_name}[/bold]\n")

        results = engine.run_workflow(
            workflow_name=workflow_file_name,
            initial_context=initial_context
        )

        console.rule("[bold blue]Workflow Execution Complete[/bold blue]")
        console.print("\n[cyan]Final Results:[/]")
        
        # A simple print of the results dictionary
        import json
        console.print(json.dumps(results, indent=2))

        console.print("\n[bold yellow]Analysis:[/]")
        if "error" in results:
            console.print("[bold red]The workflow failed.[/bold red]")
        else:
            console.print("Observe the log messages above. You should see the engine executing the workflow in [bold]two stages[/bold]:")
            console.print("1. Stage 1: Running tasks [yellow]'A_fetch_user_data'[/yellow] and [yellow]'B_fetch_product_data'[/yellow].")
            console.print("2. Stage 2: Running task [yellow]'C_generate_report'[/yellow] after the first two are complete.")
            console.print("[bold green]This demonstrates the WorkflowOptimizer is correctly identifying and executing parallelizable tasks.[/bold green]")


    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red]")
        console.log(e, exc_info=True)

if __name__ == "__main__":
    main()

