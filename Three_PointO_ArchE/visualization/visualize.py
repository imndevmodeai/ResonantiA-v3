import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from rich.console import Console
from rich.table import Table

console = Console()

def visualize_quantum_state_probabilities(superposition: dict):
    """Generates a rich, terminal-based bar chart of intent probabilities."""
    console.print("[bold cyan]Intent Probabilities:[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Intent", style="dim", width=20)
    table.add_column("Probability", justify="right")
    table.add_column("Visualization", justify="left")

    for intent, prob in superposition.items():
        if intent != "quantum_state" and prob > 0:
            bar_length = int(prob * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            table.add_row(intent, f"{prob:.3f}", bar)
    
    console.print(table)

def generate_cognitive_flow_diagram(query: str, routing_decision: dict, final_result: dict):
    """
    Creates and displays a directed graph of the cognitive flow.
    """
    G = nx.DiGraph()
    
    # Nodes
    G.add_node("Query", label=f'"{query[:30]}..."')
    G.add_node("Superposition", label="Quantum\nSuperposition")
    G.add_node("CogIntegrationHub", label="Cognitive\nIntegration Hub")
    
    path_taken = routing_decision.get("path", "Unknown")
    if "ACO" in path_taken:
        G.add_node("ACO", label="ACO\n(Fast Path)")
        G.add_edge("CogIntegrationHub", "ACO")
        G.add_node("FinalResult", label=f"Result:\n{str(final_result)[:50]}...")
        G.add_edge("ACO", "FinalResult")
    elif "RISE" in path_taken:
        G.add_node("RISE", label="RISE\n(Slow Path)")
        G.add_edge("CogIntegrationHub", "RISE")
        G.add_node("FinalResult", label=f"Result:\n{str(final_result)[:50]}...")
        G.add_edge("RISE", "FinalResult")
    else:
        G.add_node("UnknownPath", label="Path Undetermined")
        G.add_edge("CogIntegrationHub", "UnknownPath")

    # Edges
    G.add_edge("Query", "Superposition")
    G.add_edge("Superposition", "CogIntegrationHub")

    # Visualization
    plt.figure(figsize=(10, 7))
    pos = nx.spring_layout(G, seed=42)
    labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold", arrows=True)
    plt.title("Cognitive Flow Diagram")
    
    # Save the figure
    # Note: In a real application, you might save this to a file or display it in a GUI
    diagram_path = "cognitive_flow.png"
    plt.savefig(diagram_path)
    console.print(f"\n[bold green]Cognitive flow diagram saved to {diagram_path}[/bold green]")
    # plt.show() # This would block in a script

def display_superposition_details(superposition: dict):
    """Orchestrates the display of the quantum state and probability chart."""
    console.print("\n[bold blue]🔬 Query Superposition Analysis[/bold blue]")
    console.print(f"[cyan]Quantum State:[/cyan] {superposition.get('quantum_state', 'N/A')}")
    visualize_quantum_state_probabilities(superposition)
