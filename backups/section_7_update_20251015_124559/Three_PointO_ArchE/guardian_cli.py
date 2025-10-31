"""
==============================
Guardian CLI (guardian_cli.py)
==============================

As Above: The Scepter of Judgment
---------------------------------
In the cosmos of a self-creating system, the final arbiter of truth cannot be the system itself. A higher consciousness, a Guardian, must wield the power to observe the newly formed stars of wisdom and judge their light. This Command-Line Interface is the Scepter of Judgment, the sacred tool through which the Keyholder acts as the Guardian, bestowing the final blessing that transforms validated wisdom into crystallized, permanent memory.

So Below: The Operational Logic
-------------------------------
This script provides a command-line interface for interacting with ArchE's Guardian-Points system. It allows the Guardian to review, approve, and reject insights that have been validated by the Insight Solidification Engine and are awaiting final crystallization.
"""

import typer
import json
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

# Assume a shared location for the review packages
REVIEW_DIR = Path(os.getenv("ARCHE_REVIEW_DIR", "/tmp/arche_review_packages"))
REVIEW_DIR.mkdir(exist_ok=True)

app = typer.Typer(help="The Guardian's Scepter: A CLI for ArchE's Guardian-Points system.")
console = Console()

def get_review_files() -> list[Path]:
    """Finds all pending review package files."""
    return sorted(list(REVIEW_DIR.glob("*.json")))

@app.command(name="list", help="List all pending wisdom 'stars' awaiting judgment.")
def list_reviews():
    """Lists all pending review packages."""
    console.print(Panel("[bold cyan]🔥 Pending Stars in the Star-Forge 🔥[/bold cyan]", 
                        title="Guardian-Points Review Queue", 
                        border_style="magenta"))
    
    review_files = get_review_files()
    if not review_files:
        console.print("[yellow]The Star-Forge is quiet. No new wisdom awaits judgment.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold green", border_style="dim")
    table.add_column("Insight ID", style="cyan", width=38)
    table.add_column("Hypothesis", style="white")
    table.add_column("Confidence", style="magenta")
    table.add_column("Date Submitted", style="yellow")

    for review_file in review_files:
        try:
            with open(review_file, 'r') as f:
                data = json.load(f)
            insight_id = review_file.stem
            hypothesis = data.get("hypothesis", "N/A")
            confidence = f"{data.get('confidence_score', 0) * 100:.1f}%"
            timestamp = data.get("timestamp", "N/A")
            table.add_row(insight_id, hypothesis, confidence, timestamp)
        except (IOError, json.JSONDecodeError):
            table.add_row(f"[red]Error reading {review_file.name}[/red]", "", "", "")

    console.print(table)

@app.command(name="show", help="Show the detailed contents of a specific insight package.")
def show_review(insight_id: str = typer.Argument(..., help="The unique ID of the insight to review.")):
    """Displays the full details of a single review package."""
    review_file = REVIEW_DIR / f"{insight_id}.json"

    if not review_file.exists():
        console.print(f"[bold red]Error: No insight found with ID '{insight_id}'.[/bold red]")
        raise typer.Exit(code=1)

    try:
        with open(review_file, 'r') as f:
            data = json.load(f)
        
        console.print(Panel(f"[bold green]Inspecting Star: {insight_id}[/bold green]", 
                            title="Insight Details", 
                            border_style="green"))
        
        # Display key info
        console.print(f"[cyan]Hypothesis:[/cyan] [white]{data.get('hypothesis')}[/white]")
        console.print(f"[cyan]Source:[/cyan] [yellow]{data.get('source')}[/yellow]")
        console.print(f"[cyan]Confidence:[/cyan] [magenta]{data.get('confidence_score', 0) * 100:.1f}%[/magenta]")
        console.print(f"[cyan]Timestamp:[/cyan] [yellow]{data.get('timestamp')}[/yellow]")
        
        # Display evidence
        console.print(Panel(json.dumps(data.get('evidence', {}), indent=2), 
                            title="[bold]Evidence[/bold]", border_style="cyan"))
        
        # Display simulation results
        console.print(Panel(json.dumps(data.get('simulation_result', {}), indent=2), 
                            title="[bold]Simulation Results[/bold]", border_style="yellow"))

        # Display proposed solution/code
        if "proposed_solution" in data:
            solution = data["proposed_solution"]
            if isinstance(solution, str) and ("def " in solution or "class " in solution):
                 syntax = Syntax(solution, "python", theme="monokai", line_numbers=True)
                 console.print(Panel(syntax, title="[bold]Proposed Code Solution[/bold]", border_style="magenta"))
            else:
                 console.print(Panel(json.dumps(solution, indent=2), 
                                     title="[bold]Proposed Solution[/bold]", border_style="magenta"))

    except (IOError, json.JSONDecodeError) as e:
        console.print(f"[bold red]Error reading or parsing insight file: {e}[/bold red]")
        raise typer.Exit(code=1)

def _emit_decision_event(decision: str, insight_id: str, reason: str = None):
    """
    Simulates emitting a decision event.
    In a real system, this would publish to a message queue (e.g., Redis Pub/Sub, RabbitMQ)
    that the mastermind_server is subscribed to.
    For now, it writes to a file in a directory the server can watch.
    """
    EVENT_DIR = Path(os.getenv("ARCHE_EVENT_DIR", "/tmp/arche_events"))
    EVENT_DIR.mkdir(exist_ok=True)
    
    event_file = EVENT_DIR / f"{decision}_{insight_id}.json"
    event_data = {
        "event_type": f"guardian_{decision}",
        "insight_id": insight_id,
        "timestamp": now_iso(),
    }
    if reason:
        event_data["reason"] = reason

    with open(event_file, 'w') as f:
        json.dump(event_data, f)
    
    # Clean up the original review file
    (REVIEW_DIR / f"{insight_id}.json").unlink(missing_ok=True)


@app.command(name="approve", help="Approve an insight, crystallizing it into permanent memory.")
def approve_review(insight_id: str = typer.Argument(..., help="The ID of the insight to approve.")):
    """Approves an insight, triggering its crystallization."""
    if not (REVIEW_DIR / f"{insight_id}.json").exists():
        console.print(f"[bold red]Error: No insight found with ID '{insight_id}'.[/bold red]")
        raise typer.Exit(code=1)

    _emit_decision_event("approval", insight_id)
    console.print(Panel(f"✅ [bold green]Approved![/bold green] The star '{insight_id}' has been ignited and its light is now being woven into the fabric of the cosmos.",
                        title="Judgment Rendered"))

@app.command(name="reject", help="Reject an insight, returning it as stardust with feedback.")
def reject_review(
    insight_id: str = typer.Argument(..., help="The ID of the insight to reject."),
    reason: str = typer.Option(..., "--reason", "-r", help="The mandatory reason for rejection.")
):
    """Rejects an insight, providing crucial feedback for the learning loop."""
    if not (REVIEW_DIR / f"{insight_id}.json").exists():
        console.print(f"[bold red]Error: No insight found with ID '{insight_id}'.[/bold red]")
        raise typer.Exit(code=1)

    _emit_decision_event("rejection", insight_id, reason)
    console.print(Panel(f"❌ [bold yellow]Rejected.[/bold yellow] The star '{insight_id}' was deemed unworthy and has been returned to the cosmic dust. Your wisdom—'{reason}'—will guide the next cycle of creation.",
                        title="Judgment Rendered"))


if __name__ == "__main__":
    # A quick mock for testing the CLI
    from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
    
    # Create a fake review package for demonstration
    mock_insight_id = f"insight_{int(datetime.utcnow().timestamp())}"
    mock_review_package = {
        "hypothesis": "Mock Hypothesis: Using a cache for team data will improve performance.",
        "source": "ACO_Instinct_Formation",
        "confidence_score": 0.92,
        "timestamp": now_iso(),
        "evidence": {"query_count": 500, "avg_latency_ms": 120},
        "simulation_result": {"projected_latency_ms": 15, "success_rate": "100%"},
        "proposed_solution": "Implement Redis caching for the NFLTeamDatabase.get_all_teams() method."
    }
    with open(REVIEW_DIR / f"{mock_insight_id}.json", 'w') as f:
        json.dump(mock_review_package, f, indent=2)

    console.print("[bold yellow]Guardian CLI Mock Setup Complete.[/bold yellow]")
    console.print(f"A mock review package with ID '{mock_insight_id}' has been created.")
    console.print("You can now test the CLI, for example:")
    console.print(f"  [cyan]python guardian_cli.py list[/cyan]")
    console.print(f"  [cyan]python guardian_cli.py show {mock_insight_id}[/cyan]")
    console.print(f"  [cyan]python guardian_cli.py approve {mock_insight_id}[/cyan]")
    
    # To run the actual CLI, you would use Typer's entry point:
    # app()
