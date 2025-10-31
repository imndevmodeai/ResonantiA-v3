"""
Enhanced ArchE Query Interface with Visual Cognitive Debugger Integration

This is the canonical entry point for interacting with ArchE via natural language,
now enhanced with VCD (Visual Cognitive Debugger) integration for rich visualization
and debugging of the cognitive process.

It uses the CognitiveDispatch module to correctly triage and route the user's
query to the appropriate internal cognitive engine (ACO or RISE), while providing
real-time visual feedback through the VCD system.
"""

import asyncio
import logging
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import numpy as np
from typing import Dict
import json # Import the json library

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Three_PointO_ArchE.cognitive_integration_hub import CognitiveIntegrationHub
from Three_PointO_ArchE.utils.json_sanitizer import _sanitize_for_json # Import the sanitizer
from Three_PointO_ArchE.visualization.visualize import (
    display_superposition_details,
    generate_cognitive_flow_diagram
)
from Three_PointO_ArchE.logging_config import setup_logging

def create_query_superposition(query: str) -> Dict[str, float]:
    """
    Creates a quantum superposition of intents from a natural language query.
    This is a simplified example. A real implementation would use a more
    sophisticated NLP model.
    """
    superposition = {
        "generic_inquiry": 0.1,
        "analysis_request": 0.0,
        "content_generation": 0.0,
        "code_execution": 0.0,
        "research_task": 0.0,
        "creative_synthesis": 0.0,
        "system_analysis": 0.0,
        "strategic_planning": 0.0,
    }

    query_lower = query.lower()
    keywords = {
        "analysis_request": ["analyze", "evaluate", "assess", "compare"],
        "content_generation": ["create", "write", "generate", "summarize"],
        "code_execution": ["run", "execute", "implement", "code"],
        "research_task": ["find", "research", "locate", "discover"],
        "creative_synthesis": ["design", "invent", "conceptualize"],
        "system_analysis": ["debug", "optimize", "refactor", "monitor"],
        "strategic_planning": ["plan", "strategize", "roadmap"],
    }

    for intent, keys in keywords.items():
        if any(key in query_lower for key in keys):
            superposition[intent] += 0.8  # Strong boost for keyword match

    # Normalize probabilities to sum to 1
    total_prob = sum(superposition.values())
    normalized_superposition = {k: v / total_prob for k, v in superposition.items()}

    # Add quantum state representation with all non-zero amplitudes
    quantum_terms = []
    for intent, prob in normalized_superposition.items():
        if prob > 0.01:
            amplitude = np.sqrt(prob)
            quantum_terms.append(f"{amplitude:.3f}|{intent}⟩")
    _arche_vcd_analysis_enhanced.py
- ✅ VCDAnal
        normalized_superposition["quantum_state"] = f"|ψ⟩ = {' + '.join(quantum_terms)}"
    else:
        normalized_superposition["quantum_state"] = "|ψ⟩ = 1.000|generic_inquiry⟩"
    
    return normalized_superposition

async def main():
    """Main execution function."""
    console = Console()
    setup_logging()

    query = " ".join(sys.argv[1:])
    if not query:
        console.print("[bold red]Error: No query provided.[/bold red]")
        sys.exit(1)

    console.print(Panel(Text(query, justify="center"), title="[bold green]Executing Query[/bold green]"))

    # Phase 0: Query Superposition Analysis
    query_superposition = create_query_superposition(query)
    display_superposition_details(query_superposition)

    # Phase 1: ArchE Processing
    dispatcher = CognitiveIntegrationHub()
    results = dispatcher.route_query(query, superposition_context=query_superposition)
    
    # --- DEFINITIVE FIX: Sanitize results immediately upon receipt ---
    sanitized_results = _sanitize_for_json(results)

    # Phase 2: Display Results and Cognitive Flow
    console.print("\n[bold green]✔ Query Execution Complete[/bold green]")
    # Use the sanitized results for all downstream processing
    console.print(sanitized_results.get("summary", "No summary available."))
    generate_cognitive_flow_diagram(query, sanitized_results, sanitized_results)

    # For structured output, dump the sanitized results to a file or stdout
    with open("final_sanitized_output.json", "w") as f:
        json.dump(sanitized_results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
