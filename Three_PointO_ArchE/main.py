# --- START OF FILE Three_PointO_ArchE/main.py ---
# ResonantiA Protocol v3.0 - main.py
# Example entry point demonstrating initialization and execution of the Arche system.
# Handles workflow execution via IARCompliantWorkflowEngine and manages IAR-inclusive results.

import logging
import os
import json
import argparse
import sys
import time
import uuid # For unique workflow run IDs
from typing import Optional, Dict, Any, Union # Added for type hinting clarity
import asyncio # Import asyncio

# Add the parent directory of Three_PointO_ArchE to sys.path if running this script directly
# This allows absolute imports from the 'Three_PointO_ArchE' package
if __name__ == "__main__" and os.path.basename(sys.argv[0]) == os.path.basename(__file__):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logging.info(f"Added project root {project_root} to sys.path for direct execution.")

# --- Helper function to truncate values for summary ---
def truncate_value(value: Any, max_len: int = 70) -> str:
    """Converts a value to string and truncates it if too long."""
    try:
        s_value = str(value)
        if len(s_value) > max_len:
            return s_value[:max_len-3] + "..."
        return s_value
    except Exception:
        return "[Unrepresentable Value]"
# --- End helper function ---

# Setup logging FIRST using the centralized configuration
try:
    # Assumes config and logging_config are in the same package directory
    from Three_PointO_ArchE import config # Changed to absolute import
    from Three_PointO_ArchE.logging_config import setup_logging # Changed to absolute import
    setup_logging() # Initialize logging based on config settings
except ImportError as cfg_imp_err:
    # Basic fallback logging if config files are missing during setup
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stdout)
    logging.warning(f"Could not import config/logging_config via relative import: {cfg_imp_err}. Using basic stdout logging.", exc_info=True)
except Exception as log_setup_e:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stdout)
    logging.error(f"Error setting up logging from logging_config.py: {log_setup_e}. Using basic config.", exc_info=True)

# Now import other core ResonantiA modules AFTER logging is configured
try:
    from Three_PointO_ArchE.resonant_workflow_engine_v3_1_ca import ResonantWorkflowEngine_v3_1_CA as IARCompliantWorkflowEngine # Changed to use renamed new engine
    from Three_PointO_ArchE.spr_manager import SPRManager # Changed to absolute import
    # config already imported above
except ImportError as import_err:
    logging.critical(f"Failed to import core ResonantiA modules (IARCompliantWorkflowEngine, SPRManager): {import_err}. Check installation and paths.", exc_info=True)
    sys.exit(1) # Critical failure if core components cannot be imported

logger = logging.getLogger(__name__) # Get logger specifically for this module

def ensure_directories():
    """Creates necessary directories defined in config.py if they don't exist."""
    # Fetches paths from the config module
    dirs_to_check = [
        getattr(config, 'LOG_DIR', 'logs'),
        getattr(config, 'OUTPUT_DIR', 'outputs'),
        getattr(config, 'WORKFLOW_DIR', 'workflows'),
        getattr(config, 'KNOWLEDGE_GRAPH_DIR', 'knowledge_graph'),
        getattr(config, 'MODEL_SAVE_DIR', 'outputs/models') # Includes subdirectory for models
    ]
    logger.info(f"Ensuring base directories exist: {dirs_to_check}")
    for d in dirs_to_check:
        if d and isinstance(d, str): # Check if path is valid string
            try:
                os.makedirs(d, exist_ok=True) # exist_ok=True prevents error if dir exists
            except OSError as e:
                # Log critical error and raise to halt execution if essential dirs can't be made
                logger.critical(f"CRITICAL: Failed to create directory {d}: {e}. Check permissions.", exc_info=True)
                raise
        else:
            logger.warning(f"Skipping invalid directory path configured: {d}")

    # Specifically ensure the SPR definitions file exists, creating an empty list if not
    spr_file = getattr(config, 'SPR_JSON_FILE', None)
    if spr_file and isinstance(spr_file, str):
        if not os.path.exists(spr_file):
            try:
                spr_dir = os.path.dirname(spr_file)
                if spr_dir: os.makedirs(spr_dir, exist_ok=True)
                with open(spr_file, 'w', encoding='utf-8') as f:
                    json.dump([], f) # Create file with an empty JSON list
                logger.info(f"Created empty SPR definitions file at {spr_file}")
            except IOError as e:
                logger.error(f"Could not create empty SPR file at {spr_file}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error ensuring SPR file exists: {e}", exc_info=True)
    else:
        logger.warning("SPR_JSON_FILE not configured or invalid in config.py.")

def find_last_successful_run_id(output_dir: str) -> Optional[str]:
    """Finds the most recent successfully completed workflow run ID."""
    try:
        result_files = [f for f in os.listdir(output_dir) if f.startswith("result_") and f.endswith(".json")]
        result_files.sort(key=lambda f: os.path.getmtime(os.path.join(output_dir, f)), reverse=True)

        for filename in result_files:
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'r') as f:
                result_data = json.load(f)
                if result_data.get("workflow_status") == "Completed Successfully":
                    run_id = result_data.get("workflow_run_id")
                    if run_id:
                        logger.info(f"Found last successful run_id: {run_id} from file {filename}")
                        return run_id
    except Exception as e:
        logger.error(f"Could not determine last successful run ID: {e}", exc_info=True)
    return None

async def handle_run_workflow(args):
    """Handler for the 'run-workflow' command."""
    logger.info(f"--- Received command to run workflow: {args.workflow_name} ---")
    initial_context = {}
    workflow_def = None

    # Load workflow definition from file
    workflow_path = os.path.join(config.WORKFLOW_DIR, args.workflow_name) # Assume workflow_name is just the filename
    if not os.path.exists(workflow_path):
        logger.error(f"Workflow file not found: {workflow_path}")
        print(f"ERROR: Workflow file not found: {workflow_path}")
        return

    try:
        with open(workflow_path, 'r') as f:
            workflow_def = json.load(f)
        logger.info(f"Loaded workflow definition from: {workflow_path}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding workflow file {workflow_path}: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error loading workflow file {workflow_path}: {e}", exc_info=True)
        return

    if args.context_file:
        try:
            with open(args.context_file, 'r') as f:
                initial_context = json.load(f)
            logger.info(f"Loaded initial context from: {args.context_file}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading context file {args.context_file}: {e}")
            return 

    if args.initial_context_json:
        try:
            initial_context = json.loads(args.initial_context_json)
            logger.info("Loaded initial context from JSON string.")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding initial context JSON: {e}")
            return

    if workflow_def is None:
        logger.critical("Workflow definition could not be loaded. Aborting.")
        return

    try:
        engine = IARCompliantWorkflowEngine(spr_manager=SPRManager()) # Pass SPRManager to new engine
        final_context = await engine.run_workflow(workflow_def, initial_context) # Pass workflow_def dictionary
        
        # Determine the final status for logging
        final_status = final_context.get("workflow_status", "Unknown")

        # Save the final context to a file
        output_dir = config.OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)
        
        # Sanitize workflow name for the filename and add run_id
        sanitized_name = os.path.splitext(os.path.basename(args.workflow_name))[0].replace(" ", "_")
        run_id = final_context.get('workflow_run_id', 'no_run_id')
        output_filename = os.path.join(output_dir, f"result_{sanitized_name}_{run_id}.json")

        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                # Use default=str to handle potential non-serializable types gracefully (e.g., numpy types)
                json.dump(final_context, f, indent=2, default=str)
            logger.info(f"Final result saved successfully to {output_filename}")
        except TypeError as json_err:
            # Handle cases where the result dictionary contains objects JSON can't serialize directly
            logger.error(f"Could not serialize final result to JSON: {json_err}. Result likely contains non-standard objects (e.g., complex numbers, custom classes). Saving string representation as fallback.", exc_info=True)
            fallback_filename = output_filename.replace('.json', '_error_repr.txt')
            try:
                with open(fallback_filename, 'w', encoding='utf-8') as f:
                    f.write(f"Original JSON serialization error: {json_err}\n\n")
                    f.write("--- Full Result (repr) ---\n")
                    f.write(repr(final_context)) # Write the Python representation
                logger.info(f"String representation saved to {fallback_filename}")
            except Exception as write_err:
                logger.error(f"Could not write fallback string representation: {write_err}")
        except IOError as io_err:
            logger.error(f"Could not write final result to {output_filename}: {io_err}")
        except Exception as save_err:
            logger.error(f"Unexpected error saving final result: {save_err}", exc_info=True)

        # --- Print Summary to Console ---
        # Provides a quick overview of the execution outcome
        print("\n--- Workflow Final Result Summary (v3.0) ---")
        try:
            summary = {}
            summary['workflow_name'] = args.workflow_name
            summary['workflow_run_id'] = run_id
            summary['overall_status'] = final_status
            summary['run_duration_sec'] = final_context.get('workflow_run_duration_sec', 'N/A')

            # Summarize status and IAR reflection highlights for each task
            task_statuses = final_context.get('task_statuses', {})
            summary['task_summary'] = {}
            for task_id, status in task_statuses.items():
                task_result = final_context.get(task_id, {})
                reflection = task_result.get('reflection', {}) if isinstance(task_result, dict) else {}
                
                inputs_preview = {}
                if isinstance(task_result, dict) and 'resolved_inputs' in task_result and isinstance(task_result['resolved_inputs'], dict):
                    for k, v in task_result['resolved_inputs'].items():
                        inputs_preview[k] = truncate_value(v)
                
                outputs_preview = {}
                if isinstance(task_result, dict):
                    # Exclude known meta-keys and reflection from outputs preview
                    excluded_output_keys = ['reflection', 'resolved_inputs', 'error', 'status', 'start_time', 'end_time', 'duration_sec', 'attempt_number']
                    for k, v in task_result.items():
                        if k not in excluded_output_keys:
                            outputs_preview[k] = truncate_value(v)

                summary['task_summary'][task_id] = {
                    "status": status,
                    "inputs_preview": inputs_preview if inputs_preview else "N/A",
                    "outputs_preview": outputs_preview if outputs_preview else "N/A",
                    "reflection_status": reflection.get('status', 'N/A'),
                    "reflection_confidence": reflection.get('confidence', 'N/A'),
                    "reflection_issues": reflection.get('potential_issues', None),
                    "error": truncate_value(task_result.get('error', None)) # Also truncate error messages
                }
            # Print the summary dict as formatted JSON
            print(json.dumps(summary, indent=2, default=str))
        except Exception as summary_e:
            print(f"(Could not generate summary: {summary_e})")
            print(f"Full results saved to {output_filename} (or fallback file).")
        print("---------------------------------------------\n")

    except Exception as e:
        logger.critical(f"A critical error occurred in the main execution block: {e}", exc_info=True)

def handle_list_workflows(args):
    """Handler for the 'list-workflows' command."""
    logger.info("--- Listing available workflows ---")
    workflows_dir = config.WORKFLOW_DIR
    if not os.path.isdir(workflows_dir):
        logger.error(f"Workflow directory not found: {workflows_dir}")
        print(f"ERROR: Workflow directory not found: {workflows_dir}")
        return

    workflow_files = [f for f in os.listdir(workflows_dir) if f.endswith('.json')]
    if not workflow_files:
        print(f"No workflow JSON files found in {workflows_dir}")
        return

    print(f"\nAvailable Workflows in {workflows_dir}:")
    for wf in sorted(workflow_files):
        print(f"- {wf}")
    print("------------------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="ResonantiA Protocol ArchE - Workflow and System Management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Subparser for 'run-workflow' command
    run_workflow_parser = subparsers.add_parser('run-workflow', help='Run a specified workflow')
    run_workflow_parser.add_argument('workflow_name', type=str, help='Path to the workflow JSON file (e.g., workflows/basic_analysis.json)')
    run_workflow_parser.add_argument('--context_file', type=str, help='Optional: Path to a JSON file containing initial context for the workflow')
    run_workflow_parser.add_argument('--initial_context_json', type=str, help='Optional: JSON string containing initial context for the workflow')
    run_workflow_parser.set_defaults(func=handle_run_workflow)

    # Subparser for 'find-last-successful-run' command
    find_run_parser = subparsers.add_parser('find-last-successful-run', help='Find the ID of the last successful workflow run')
    find_run_parser.set_defaults(func=lambda args: logger.info(f"Last successful run ID: {find_last_successful_run_id(config.OUTPUT_DIR)}"))

    # Add a subparser for listing workflows
    list_workflows_parser = subparsers.add_parser('list-workflows', help='List all available workflow JSON files')
    list_workflows_parser.set_defaults(func=handle_list_workflows)

    args = parser.parse_args()

    ensure_directories()

    if hasattr(args, 'func'):
        if asyncio.iscoroutinefunction(args.func):
            asyncio.run(args.func(args))
        else:
            args.func(args)
    else:
        parser.print_help()

# Ensure the package can be found if running the script directly
# This might be less necessary when running with `python -m` but kept for broader compatibility
package_dir = os.path.dirname(__file__) # Directory of main.py (e.g., .../ResonantiA/3.0ArchE)
project_root = os.path.abspath(os.path.join(package_dir, '..')) # Project root (e.g., .../ResonantiA)
if project_root not in sys.path:
    sys.path.insert(0, project_root) # Add project root to Python path

# --- Command Line Argument Parsing ---
if __name__ == "__main__":
    main()

# --- END OF FILE Three_PointO_ArchE/main.py --- 