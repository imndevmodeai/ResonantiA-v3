#!/usr/bin/env python3
"""
ArchE Interactive Agent - IAR Compliant Workflow Engine Interface
This script provides a command-line interface to execute workflows using
the IARCompliantWorkflowEngine, ensuring adherence to the ResonantiA Protocol.
"""

import sys
import os
import logging
import json
from pathlib import Path
from typing import Dict, Any, List
import argparse

# Add the project root to the path to allow direct imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.utils.reflection_utils import ExecutionStatus

# --- PTRF Integration: Import real dependencies ---
from Three_PointO_ArchE.proactive_truth_system import ProactiveTruthSystem
from Three_PointO_ArchE.llm_providers import OpenAIProvider # Assuming OpenAI as default
from Three_PointO_ArchE.tools.search_tool import SearchTool
from Three_PointO_ArchE.spr_manager import SPRManager
# --- End PTRF Integration ---

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ArchE_Workflow_CLI")

class ArchEWorkflowCLI:
    """
    A command-line interface for interacting with ArchE's IARCompliantWorkflowEngine.
    """
    
    def __init__(self):
        """Initialize the CLI and the workflow engine."""
        self.workflows_dir = project_root / "workflows"
        self.available_workflows = self._discover_workflows()
        self.engine = IARCompliantWorkflowEngine()
        logger.info(f"ArchE Workflow CLI initialized. Found {len(self.available_workflows)} workflows.")

        # --- PTRF Integration: Instantiate the live PTRF engine and its dependencies ---
        try:
            logger.info("Initializing Proactive Truth Resonance Framework engine...")
            # Note: This assumes default initializations are sufficient.
            # A real system would pull config from a file (e.g., for API keys).
            llm_provider = OpenAIProvider() # This would need an API key in environment
            web_search_tool = SearchTool() # This might need an API key
            spr_manager = SPRManager() # Assumes default KG path
            
            self.truth_seeker = ProactiveTruthSystem(
                workflow_engine=self.engine,
                llm_provider=llm_provider,
                web_search_tool=web_search_tool,
                spr_manager=spr_manager
            )
            self.ptrf_enabled = True
            logger.info("Proactive Truth Resonance Framework engine is ONLINE.")
        except Exception as e:
            self.truth_seeker = None
            self.ptrf_enabled = False
            logger.error(f"Failed to initialize PTRF engine: {e}. The 'truth_seek' command will be disabled.", exc_info=True)
            print("\nWARNING: Could not initialize the Proactive Truth Engine. The 'truth_seek' command will be disabled. Check logs and API key configurations.\n")
        # --- End PTRF Integration ---

    def _discover_workflows(self) -> List[str]:
        """Scans the workflows directory for available .json files."""
        if not self.workflows_dir.is_dir():
            logger.warning(f"Workflows directory not found at: {self.workflows_dir}")
            return []
        return sorted([f.name for f in self.workflows_dir.glob("*.json")])

    def list_workflows(self):
        """Prints the list of available workflows."""
        print("\nAvailable Workflows:")
        if not self.available_workflows:
            print("  No workflows found.")
            return
        for i, wf_name in enumerate(self.available_workflows, 1):
            print(f"  {i}. {wf_name}")
        print()

    def select_workflow(self) -> str | None:
        """Prompts the user to select a workflow and returns the chosen file name."""
        self.list_workflows()
        if not self.available_workflows:
            return None
        
        while True:
            try:
                choice_str = input(f"Select a workflow by number (1-{len(self.available_workflows)}) or 'exit': ")
                if choice_str.lower() == 'exit':
                    return None
                choice = int(choice_str) - 1
                if 0 <= choice < len(self.available_workflows):
                    return self.available_workflows[choice]
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def run(self):
        """The main interactive loop for the CLI."""
        print("Welcome to the ArchE Workflow CLI.")
        available_commands = "list, run, exit"
        if self.ptrf_enabled:
            available_commands = "list, run, truth_seek, exit"
        
        print(f"Type '{available_commands}'")

        while True:
            try:
                prompt_text = f"\n> Enter command ({available_commands}): "
                command = input(prompt_text).lower().strip()

                if command == 'exit':
                    print("Exiting ArchE Workflow CLI. Goodbye!")
                    break
                elif command == 'list':
                    self.list_workflows()
                elif command == 'run':
                    workflow_name = self.select_workflow()
                    if workflow_name:
                        workflow_path = self.workflows_dir / workflow_name
                        print(f"\nExecuting workflow: {workflow_name}")
                        try:
                            # For now, we run with an empty initial context.
                            # A more advanced version could prompt for context.
                            initial_context = {}
                            final_result = self.engine.run_workflow(str(workflow_path), initial_context)
                            
                            print("\n--- Workflow Execution Complete ---")
                            print(json.dumps(final_result, indent=2, default=str))
                            print("---------------------------------")
                            
                            final_reflection = final_result.get("reflection", {})
                            if final_reflection.get("status") == ExecutionStatus.CRITICAL_FAILURE:
                                logger.error("Workflow ended with CRITICAL_FAILURE.")
                            
                        except Exception as e:
                            logger.error(f"An error occurred while running the workflow '{workflow_name}': {e}", exc_info=True)
                            print(f"An error occurred. Check the logs for details.")
                elif command == 'truth_seek':
                    if not self.ptrf_enabled:
                        print("The 'truth_seek' command is disabled due to an initialization error. Please check the logs.")
                        continue
                    
                    query = input("Enter the factual query you want to verify: ")
                    if not query:
                        print("Query cannot be empty.")
                        continue
                        
                    print(f"\nInitiating Proactive Truth Resonance for: \"{query}\"")
                    print("This may take a moment as it involves live web searches and analysis...")
                    
                    try:
                        # Call the PTRF engine
                        stp = self.truth_seeker.seek_truth(query)
                        
                        # Convert dataclass to dict for clean JSON printing
                        stp_dict = {
                            "final_answer": stp.final_answer,
                            "confidence_score": stp.confidence_score,
                            "source_consensus": stp.source_consensus.value,
                            "transparency_note": stp.transparency_note,
                            "conflicting_information": stp.conflicting_information,
                            "crystallization_ready": stp.crystallization_ready,
                            "verification_trail": stp.verification_trail
                        }

                        print("\n--- Solidified Truth Packet ---")
                        print(json.dumps(stp_dict, indent=2))
                        print("-----------------------------")

                    except Exception as e:
                        logger.error(f"An error occurred during truth seeking for query '{query}': {e}", exc_info=True)
                        print(f"An error occurred during truth seeking. See logs for details.")
                else:
                    print(f"Unknown command. Available commands: {available_commands}")

            except KeyboardInterrupt:
                print("\nExiting ArchE Workflow CLI. Goodbye!")
                break
            except Exception as e:
                logger.error(f"An unexpected error occurred in the CLI main loop: {e}", exc_info=True)
                print("An unexpected error occurred. Check the logs.")

def main():
    """Main function to run the ArchE Workflow CLI."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="ArchE Interactive Agent - IAR Compliant Workflow Engine Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 -m mastermind.interact                    # Interactive mode
  python3 -m mastermind.interact "What is AI?"      # Direct query mode
  python3 -m mastermind.interact --truth-seek "Is the Earth round?"  # Truth-seeking mode
        """
    )
    parser.add_argument(
        'query', 
        nargs='?', 
        help='Query to process directly (non-interactive mode)'
    )
    parser.add_argument(
        '--truth-seek', 
        action='store_true',
        help='Use the Proactive Truth Resonance Framework to verify the query'
    )
    
    args = parser.parse_args()
    
    cli = ArchEWorkflowCLI()
    
    # Non-interactive mode: process the query directly
    if args.query:
        if args.truth_seek:
            if not cli.ptrf_enabled:
                print("ERROR: The Proactive Truth Resonance Framework is not available.")
                print("Check logs and API key configurations.")
                sys.exit(1)
            
            print(f"Initiating Proactive Truth Resonance for: \"{args.query}\"")
            print("This may take a moment as it involves live web searches and analysis...")
            
            try:
                stp = cli.truth_seeker.seek_truth(args.query)
                
                # Convert dataclass to dict for clean JSON printing
                stp_dict = {
                    "final_answer": stp.final_answer,
                    "confidence_score": stp.confidence_score,
                    "source_consensus": stp.source_consensus.value,
                    "transparency_note": stp.transparency_note,
                    "conflicting_information": stp.conflicting_information,
                    "crystallization_ready": stp.crystallization_ready,
                    "verification_trail": stp.verification_trail
                }

                print("\n--- Solidified Truth Packet ---")
                print(json.dumps(stp_dict, indent=2))
                print("-----------------------------")
                
            except Exception as e:
                logger.error(f"An error occurred during truth seeking for query '{args.query}': {e}", exc_info=True)
                print(f"ERROR: An error occurred during truth seeking. See logs for details.")
                sys.exit(1)
        else:
            # For now, we'll treat a direct query as a request for general processing
            # In a more advanced system, this might trigger a specific workflow or LLM interaction
            print(f"Processing query: \"{args.query}\"")
            print("Note: Direct query processing is not yet fully implemented.")
            print("The query has been received and logged. For full functionality, use interactive mode or --truth-seek.")
    
    # Interactive mode: run the normal CLI loop
    else:
        cli.run()

if __name__ == "__main__":
    main() 