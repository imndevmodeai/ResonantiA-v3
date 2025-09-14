import argparse
import sys
import os

# Adjust path to allow importing from the parent 'mastermind' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mastermind.validator import run_validation_suite

def main():
    """
    Main deployment script for the Mastermind_AI system.
    This script initializes the system by running the full validation suite.
    """
    parser = argparse.ArgumentParser(description="Mastermind_AI Deployment and Validation Orchestrator")
    parser.add_argument(
        "--primer_url",
        type=str,
        help="Optional: Specify a primer URL to override the one in the graph. Not currently used in validation.",
    )
    args = parser.parse_args()

    print("==============================================")
    print("Executing Mastermind_AI Deployment Orchestrator")
    print("==============================================")
    
    if args.primer_url:
        print(f"-> Primer URL specified: {args.primer_url} (Note: validation uses URL from graph)")

    print("\nPhase 1: Running System Validation Suite...")
    run_validation_suite()
    
    print("\nDeployment orchestration complete.")
    print("The system has been validated and is considered online.")
    print("==============================================")


if __name__ == "__main__":
    # This allows the script to be run with `python -m mastermind.SPR_Orchestrator.spr_deploy`
    # if the parent directory is in the python path.
    main() 