#!/usr/bin/env python3
"""
ArchE Guardian CLI (arche_cli.py)
The direct channel for Guardian interaction with the ArchE cognitive architecture.

This script provides a command-line interface to send queries directly to the
CognitiveIntegrationHub, which serves as the single entry point for all
cognitive operations.

Usage:
    python arche_cli.py "Your query for ArchE"
"""

import argparse
import sys
from pathlib import Path

# Ensure the project root is in the Python path to allow for module imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from Three_PointO_ArchE.cognitive_integration_hub import CognitiveIntegrationHub
    from Three_PointO_ArchE.canonical_types import CognitiveResponse, QuantumProbability
except ImportError as e:
    print(f"FATAL: Could not import core ArchE modules. Ensure you are running from the project root.")
    print(f"Error: {e}")
    sys.exit(1)

def main():
    """Main function to run the ArchE Guardian CLI."""
    parser = argparse.ArgumentParser(description="ArchE Guardian Command-Line Interface")
    parser.add_argument("query", type=str, help="The query or command for ArchE.")
    parser.add_argument("--model", type=str, default=None, help="Specify a Google LLM model to use (e.g., 'gemini-1.5-pro-latest').")
    parser.add_argument("--workflow", type=str, default=None, help="Specify a custom workflow JSON file to use (e.g., 'rise_v2_robust').")
    args = parser.parse_args()

    print("\n    ..:: ArchE Guardian CLI ::..    \n")
    print("----------------------------------------------------")
    print("Initializing Cognitive Integration Hub...")
    
    try:
        hub = CognitiveIntegrationHub()
        print("   ✓ Hub initialized successfully.")
    except Exception as e:
        print(f"   ✗ FATAL: Failed to initialize CognitiveIntegrationHub: {e}")
        sys.exit(1)

    print(f"\nRouting query: '{args.query}'")
    print("----------------------------------------------------")

    try:
        # Pass the model and workflow arguments to the hub
        response = hub.route_query(args.query, model=args.model, workflow_name=args.workflow)
        
        print("\n--- ArchE Response ---")
        # Handle both dict and CognitiveResponse objects
        if isinstance(response, dict):
            content = response.get('content', response.get('final_strategy', str(response)))
            print(f"Content: {content}")
        else:
            print(f"Content: {response.content}")
        
        # Only print metadata if it's a CognitiveResponse object
        if not isinstance(response, dict):
            print(f"Processing Path: {response.processing_path}")
            print(f"Controller Used: {response.controller_used}")
            print(f"Confidence: {response.confidence.probability:.3f}")
        print("----------------------\n")

    except Exception as e:
        print(f"\n--- ✗ An error occurred during query processing ---")
        print(f"Error: {e}")
        print("---------------------------------------------------\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
