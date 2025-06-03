# --- START OF FILE Three_PointO_ArchE/main.py ---
# ResonantiA Protocol v3.0 - main.py
# Example entry point demonstrating initialization and execution of the Arche system.
# Handles workflow execution via WorkflowEngine and manages IAR-inclusive results.

import logging
import os
import json
import argparse
import sys
import time
import uuid # For unique workflow run IDs
from typing import Optional, Dict, Any, Union # Added for type hinting clarity

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
    from . import config # Use relative import within the package
    from .logging_config import setup_logging
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
    from .workflow_engine import WorkflowEngine
    from .spr_manager import SPRManager
    # config already imported above
except ImportError as import_err:
    logging.critical(f"Failed to import core ResonantiA modules (WorkflowEngine, SPRManager): {import_err}. Check installation and paths.", exc_info=True)
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


def main(workflow_to_run: str, initial_context_json: Optional[str] = None):
    """
    Main execution function: Initializes system, runs workflow, saves results.
    """
    logger.info("--- Arche System Initialization (ResonantiA Protocol v3.0) ---")
    logger.warning("Keyholder Override ('IMnDEVmode') is conceptually active for this session (as per protocol doc).") # Note: Actual check might be needed elsewhere

    # Ensure directories exist before initializing components that might need them
    try:
        ensure_directories()
    except Exception as dir_e:
        # If directory creation failed, log critical and exit
        logger.critical(f"Failed to ensure necessary directories: {dir_e}. Exiting.")
        sys.exit(1)

    # Initialize core components
    try:
        spr_manager = SPRManager(getattr(config, 'SPR_JSON_FILE', None)) # Pass configured path
        logger.info(f"SPR Manager initialized. Loaded {len(spr_manager.sprs)} SPRs from '{spr_manager.filepath}'.")
    except (ValueError, TypeError) as spr_init_err: # Catch config errors specifically
        logger.critical(f"Failed to initialize SPR Manager due to configuration issue (SPR_JSON_FILE): {spr_init_err}. Exiting.", exc_info=True)
        sys.exit(1)
    except Exception as spr_e:
        logger.critical(f"Unexpected error initializing SPR Manager: {spr_e}. Exiting.", exc_info=True)
        sys.exit(1)

    try:
        # Pass the initialized SPR manager to the engine if needed (e.g., for SPR context)
        workflow_engine = WorkflowEngine(spr_manager=spr_manager)
        logger.info("Workflow Engine initialized.")
    except Exception as wf_e:
        logger.critical(f"Failed to initialize Workflow Engine: {wf_e}. Exiting.", exc_info=True)
        sys.exit(1)

    # --- Prepare Initial Context ---
    initial_context: Dict[str, Any] = {}

    # initial_context_json = "{\"raw_user_query\": \"Can you provide an InnovativE SolutioN for energy crisis?\", \"user_id\": \"cli_keyholder_IMnDEVmode\", \"protocol_version\": \"3.0\"}" # HARCODED FOR TEST

    if initial_context_json:
        try:
            # Load context from JSON string argument
            initial_context = json.loads(initial_context_json)
            if not isinstance(initial_context, dict):
                # Ensure the loaded JSON is actually a dictionary
                raise json.JSONDecodeError("Initial context must be a JSON object (dictionary).", initial_context_json, 0)
            logger.info("Loaded initial context from command line argument.")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON provided for initial context: {e}. Starting with minimal context including error.", exc_info=True)
            initial_context = {"error_loading_context": f"Invalid JSON: {e}", "raw_context_input": initial_context_json}

    # Add/ensure essential context variables
    initial_context["user_id"] = initial_context.get("user_id", "cli_keyholder_IMnDEVmode") # Example user ID
    initial_context["workflow_run_id"] = initial_context.get("workflow_run_id", f"run_{uuid.uuid4().hex}") # Unique ID for this run
    initial_context["protocol_version"] = "3.0" # Stamp the protocol version

    # --- Execute Workflow ---
    logger.info(f"Attempting to execute workflow: '{workflow_to_run}' (Run ID: {initial_context['workflow_run_id']})")
    final_result: Dict[str, Any] = {}
    try:
        # Core execution call
        final_result = workflow_engine.run_workflow(workflow_to_run, initial_context)
        logger.info(f"Workflow '{workflow_engine.last_workflow_name or workflow_to_run}' execution finished.") # Use name loaded by engine if available

        # --- Save Full Results ---
        # Construct a unique filename for the results
        base_workflow_name = os.path.basename(workflow_to_run).replace('.json', '')
        output_filename = os.path.join(config.OUTPUT_DIR, f"result_{base_workflow_name}_{initial_context['workflow_run_id']}.json")

        logger.info(f"Attempting to save full final result dictionary to {output_filename}")
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                # Use default=str to handle potential non-serializable types gracefully (e.g., numpy types)
                json.dump(final_result, f, indent=2, default=str)
            logger.info(f"Final result saved successfully.")
        except TypeError as json_err:
            # Handle cases where the result dictionary contains objects JSON can't serialize directly
            logger.error(f"Could not serialize final result to JSON: {json_err}. Result likely contains non-standard objects (e.g., complex numbers, custom classes). Saving string representation as fallback.", exc_info=True)
            fallback_filename = output_filename.replace('.json', '_error_repr.txt')
            try:
                with open(fallback_filename, 'w', encoding='utf-8') as f:
                    f.write(f"Original JSON serialization error: {json_err}\n\n")
                    f.write("--- Full Result (repr) ---\n")
                    f.write(repr(final_result)) # Write the Python representation
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
            summary['workflow_name'] = workflow_engine.last_workflow_name or workflow_to_run
            summary['workflow_run_id'] = initial_context['workflow_run_id']
            summary['overall_status'] = final_result.get('workflow_status', 'Unknown')
            summary['run_duration_sec'] = final_result.get('workflow_run_duration_sec', 'N/A')

            # Summarize status and IAR reflection highlights for each task
            task_statuses = final_result.get('task_statuses', {})
            summary['task_summary'] = {}
            for task_id, status in task_statuses.items():
                task_result = final_result.get(task_id, {})
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

    except FileNotFoundError as e:
        # Handle case where the specified workflow file doesn't exist
        logger.error(f"Workflow file '{workflow_to_run}' not found in '{config.WORKFLOW_DIR}': {e}")
        print(f"ERROR: Workflow file '{workflow_to_run}' not found in '{config.WORKFLOW_DIR}'. Please check the filename and path.")
        sys.exit(1)
    except (ValueError, TypeError) as setup_err:
        # Handle errors likely related to configuration or workflow structure
        logger.critical(f"Workflow execution failed due to configuration or setup error: {setup_err}", exc_info=True)
        print(f"ERROR: Workflow setup failed. Check configuration ({config.__file__}) and workflow structure ({workflow_to_run}). Error: {setup_err}")
        sys.exit(1)
    except Exception as exec_err:
        # Catch any other unexpected errors during workflow execution
        logger.critical(f"An critical unexpected error occurred during workflow execution: {exec_err}", exc_info=True)
        print(f"ERROR: Workflow execution failed unexpectedly. Check logs at {config.LOG_FILE}. Error: {exec_err}")
        sys.exit(1)

    logger.info("--- Arche System Shutdown ---")

# Ensure the package can be found if running the script directly
# This might be less necessary when running with `python -m` but kept for broader compatibility
package_dir = os.path.dirname(__file__) # Directory of main.py (e.g., .../ResonantiA/3.0ArchE)
project_root = os.path.abspath(os.path.join(package_dir, '..')) # Project root (e.g., .../ResonantiA)
if project_root not in sys.path:
    sys.path.insert(0, project_root) # Add project root to Python path

# --- Command Line Argument Parsing ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ResonantiA Protocol v3.0 - Arche System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # --- run-workflow sub-command ---
    run_parser = subparsers.add_parser("run-workflow", help="Run a specified workflow JSON file.")
    run_parser.add_argument("workflow_file", help="Path to the workflow JSON file to execute.")
    input_group = run_parser.add_mutually_exclusive_group()
    input_group.add_argument("--inputs", "-i", help="JSON string of initial context data for the workflow.", type=str, default=None)
    input_group.add_argument("--context-file", "-cf", help="Path to a JSON file containing initial context data.", type=str, default=None)
    # Optional: For running a single task from a workflow for debugging/testing
    run_parser.add_argument("--task-id", help="(Optional) Specific task ID to run within the workflow.", default=None)

    # --- (Future sub-commands can be added here, e.g., manage-spr, etc.) ---
    # spr_parser = subparsers.add_parser("manage-spr", help="Manage Strategic Processing Routines.")
    # ... add arguments for manage-spr

    args = parser.parse_args()

    initial_context_data_json: Optional[str] = None
    if args.command == "run-workflow":
        if args.context_file:
            logger.info(f"Loading initial context from file: {args.context_file}")
            try:
                with open(args.context_file, 'r', encoding='utf-8') as f_context:
                    initial_context_data_json = f_context.read()
                # Basic validation of the JSON string read
                json.loads(initial_context_data_json) 
            except FileNotFoundError:
                logger.error(f"Context file not found: {args.context_file}")
                print(f"ERROR: Context file not found: {args.context_file}")
                sys.exit(1)
            except json.JSONDecodeError as e_json_ctx:
                logger.error(f"Invalid JSON in context file {args.context_file}: {e_json_ctx}")
                print(f"ERROR: Invalid JSON in context file {args.context_file}: {e_json_ctx}")
                sys.exit(1)
            except Exception as e_ctx_file:
                logger.error(f"Error reading context file {args.context_file}: {e_ctx_file}")
                print(f"ERROR: Could not read context file {args.context_file}: {e_ctx_file}")
                sys.exit(1)
        elif args.inputs:
            initial_context_data_json = args.inputs
            # Basic validation of the JSON string provided
            try:
                json.loads(initial_context_data_json)
            except json.JSONDecodeError as e_json_inputs:
                logger.error(f"Invalid JSON string provided via --inputs: {e_json_inputs}")
                print(f"ERROR: Invalid JSON string for --inputs: {e_json_inputs}")
                sys.exit(1)

        # Call the existing main function, potentially adapting it if --task-id is used
        # For now, --task-id is parsed but not directly used by the main() call here.
        # The main() function itself would need modification to handle single task runs,
        # or WorkflowEngine.run_workflow would need a task_id parameter.
        if args.task_id:
            logger.warning(f"--task-id '{args.task_id}' was specified, but current main() does not directly support single task execution. Will run full workflow.")
            # If you want to support single task runs, you'd modify how main() or workflow_engine.run_workflow is called here.
        
        main(workflow_to_run=os.path.basename(args.workflow_file), initial_context_json=initial_context_data_json)
    
    # --- Handle other commands if/when added ---
    # elif args.command == "manage-spr":
    #    logger.info("Executing manage-spr command...")
    #    # Call a function to handle SPR management with args
    else:
        logger.error(f"Unrecognized command: {args.command}")
        parser.print_help()
        sys.exit(1)

# --- END OF FILE Three_PointO_ArchE/main.py --- 