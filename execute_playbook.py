# --- execute_playbook.py ---
import sys
import os
import pprint
from Three_PointO_ArchE.playbook_orchestrator import run_playbook
from Three_PointO_ArchE.config import configure_logging

def main():
    """
    The clean, modern entry point for executing strategic playbooks.
    Usage: python execute_playbook.py <path_to_playbook.json>
    """
    # Configure logging for the entire system
    configure_logging()

    # Find the playbook file
    if len(sys.argv) < 2:
        print("Usage: python execute_playbook.py <path_to_playbook.json>")
        # Default to the strategic intelligence workflow if no path is provided
        playbook_path = os.path.join(os.path.dirname(__file__), 'workflows', 'strategic_intelligence_workflow.json')
        print(f"No playbook path provided. Defaulting to: {playbook_path}")
    else:
        playbook_path = sys.argv[1]

    if not os.path.exists(playbook_path):
        print(f"Error: Playbook file not found at '{playbook_path}'")
        sys.exit(1)

    # Run the playbook using the new orchestrator
    result = run_playbook(playbook_path)

    # Print the final result
    print("\n--- PLAYBOOK EXECUTION COMPLETE ---")
    pprint.pprint(result)
    print("---------------------------------")

if __name__ == "__main__":
    main()
