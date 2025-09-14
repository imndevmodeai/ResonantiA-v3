import logging
import os
import json
import argparse
import sys
import time
from typing import Optional

try:
    from Three_PointO_ArchE import config
    from Three_PointO_ArchE.resonantia_maestro import ResonantiaMaestro # Import the Maestro
    from Three_PointO_ArchE.spr_manager import SPRManager
except ImportError as import_err:
    logging.critical(f"Failed to import core ResonantiA modules: {import_err}. Please check installation and paths.", exc_info=True)
    sys.exit(1) # Exit if core components missing

logger = logging.getLogger(__name__)

def ensure_directories():
    """Creates necessary directories defined in config if they don't exist."""
    dirs_to_check = [
        config.LOG_DIR,
        config.OUTPUT_DIR,
        config.WORKFLOW_DIR,
        config.KNOWLEDGE_GRAPH_DIR,
        config.MODEL_SAVE_DIR
    ]
    logger.info(f"Ensuring directories exist: {dirs_to_check}")
    for d in dirs_to_check:
        if d:
            try:
                os.makedirs(d, exist_ok=True)
            except OSError as e:
                logger.error(f"CRITICAL: Failed to create directory {d}: {e}. Check permissions.")
                raise

    if config.SPR_JSON_FILE and not os.path.exists(config.SPR_JSON_FILE):
        try:
            spr_dir = os.path.dirname(config.SPR_JSON_FILE)
            if spr_dir: os.makedirs(spr_dir, exist_ok=True)
            with open(config.SPR_JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
            logger.info(f"Created empty SPR definitions file at {config.SPR_JSON_FILE}")
        except IOError as e:
            logger.error(f"Could not create empty SPR file at {config.SPR_JSON_FILE}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error ensuring SPR file exists: {e}", exc_info=True)

def main(workflow_to_run: Optional[str], initial_context_json: Optional[str] = None, user_query: Optional[str] = None, mode: str = "orchestrate"):
    """Main execution function."""
    logger.info("--- Arche System Initialization (ResonantiA Protocol v3.5) ---")
    logger.warning("Keyholder Override ('IMnDEVmode') is conceptually active for this session.")

    try:
        ensure_directories()
    except Exception as dir_e:
         logger.critical(f"Failed to ensure necessary directories: {dir_e}. Exiting.")
         sys.exit(1)

    # Initialize the master orchestrator
    try:
        maestro = ResonantiaMaestro()
        logger.info("Resonantia Maestro initialized.")
    except Exception as maestro_e:
         logger.critical(f"Failed to initialize Resonantia Maestro: {maestro_e}. Exiting.", exc_info=True)
         sys.exit(1)

    # --- Execution Logic ---
    initial_context = {}
    if initial_context_json:
        try:
            initial_context = json.loads(initial_context_json)
            if not isinstance(initial_context, dict):
                 raise json.JSONDecodeError("Initial context must be a JSON object (dictionary).", initial_context_json, 0)
            logger.info("Loaded initial context from command line argument.")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON provided for initial context: {e}. Starting with empty context.")
            initial_context = {"error": "Invalid initial context JSON provided.", "raw_input": initial_context_json}

    # Add default context if needed
    initial_context.setdefault("user_id", "cli_keyholder_IMnDEVmode")
    initial_context["workflow_run_id"] = f"run_{int(time.time())}"

    # Determine the primary query or task
    if user_query:
        query_text = user_query
        logger.info(f"Executing query from command line: '{query_text[:100]}...'")
    elif 'user_query' in initial_context:
        query_text = initial_context['user_query']
        logger.info(f"Executing query found in initial context: '{query_text[:100]}...'")
    elif workflow_to_run:
        query_text = f"Execute the '{workflow_to_run}' workflow."
        initial_context['workflow_to_run'] = workflow_to_run # Ensure maestro knows about it
        logger.info(f"Executing direct workflow request: {workflow_to_run}")
    else:
        logger.error("No query or workflow provided. Nothing to execute.")
        print("ERROR: You must provide a query using -q/--query or a workflow file to run.")
        sys.exit(1)
        
    try:
        # --- Execution based on selected mode ---
        if mode == "orchestrate":
            logger.info("Executing in 'orchestrate' mode (Modern RISE Engine).")
            final_result = maestro.orchestrate_query(query_text, initial_context)
            logger.info("Maestro orchestration finished.")
        
        elif mode == "weave":
            logger.info("Executing in 'weave' mode (Legacy Weaving Method).")
            final_result = maestro.weave_response(query_text)
            logger.info("Maestro weaving finished.")

        elif mode == "compare":
            logger.info("Executing in 'compare' mode. Running both modern and legacy methods.")
            
            logger.info("--- Running Modern Orchestration ---")
            orchestrate_result = maestro.orchestrate_query(query_text, initial_context)
            logger.info("--- Modern Orchestration Finished ---")

            logger.info("--- Running Legacy Weaving ---")
            weave_result = maestro.weave_response(query_text)
            logger.info("--- Legacy Weaving Finished ---")

            # Combine results for output
            final_result = {
                "comparison_results": {
                    "modern_orchestration": orchestrate_result,
                    "legacy_weaving": weave_result
                }
            }
            logger.info("Comparison finished.")
        
        else:
            # This case should not be reachable due to argparse 'choices'
            logger.error(f"Invalid mode '{mode}' specified.")
            sys.exit(1)

        # Determine output filename
        base_name = os.path.basename(workflow_to_run).replace('.json', '') if workflow_to_run else f"{mode}_query_run"
        output_filename = os.path.join(config.OUTPUT_DIR, f"result_{base_name}_{initial_context['workflow_run_id']}.json")

        # Save final result to output directory
        logger.info(f"Attempting to save final result to {output_filename}")
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, indent=2, default=str)
            logger.info(f"Final result saved successfully.")
        except TypeError as e:
            logger.error(f"Could not serialize final result to JSON: {e}. Result likely contains non-standard objects. Saving string representation instead.")
            fallback_filename = output_filename.replace('.json', '_error_repr.txt')
            try:
                with open(fallback_filename, 'w', encoding='utf-8') as f:
                    f.write(f"Original serialization error: {e}\\n\\n")
                    f.write(repr(final_result))
                logger.info(f"String representation saved to {fallback_filename}")
            except Exception as write_err:
                logger.error(f"Could not write fallback string representation: {write_err}")
        except IOError as e:
            logger.error(f"Could not write final result to {output_filename}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving final result: {e}", exc_info=True)

        print("\\n--- Workflow Final Result (Summary) ---")
        try:
            summary = {}
            has_errors = any(isinstance(v, dict) and v.get('error') for k, v in final_result.items() if k not in ['initial_context', 'workflow_definition', 'task_statuses', 'workflow_status'])
            summary['workflow_status'] = final_result.get('workflow_status', 'Completed with Errors' if has_errors else 'Completed Successfully')

            for k, v in final_result.items():
                if k in ['initial_context', 'workflow_definition', 'task_statuses', 'workflow_status']: continue
                if isinstance(v, dict) and v.get('error') is not None:
                    summary[k] = {"status": "Failed", "error": str(v['error'])[:200]+"..."}
                elif isinstance(v, dict):
                    preview = {pk: (str(pv)[:50]+"..." if isinstance(pv, (str, list, dict)) and len(str(pv)) > 50 else pv) for pk, pv in v.items()}
                    summary[k] = {"status": "Success", "keys": list(v.keys()), "preview": preview}
                elif isinstance(v, list):
                    summary[k] = {"status": "Success", "count": len(v), "preview": str(v)[:200]+"..."}
                elif isinstance(v, str) and len(v) > 200:
                    summary[k] = str(v)[:200] + "..."
                else:
                    summary[k] = v

            print(json.dumps(summary, indent=2, default=str))
        except Exception as summary_e:
            print(f"(Could not generate summary: {summary_e})")
            print(f"Full results saved to {output_filename} (or fallback file).")

        print("-------------------------------------\\n")

    except FileNotFoundError as e:
        logger.error(f"Workflow file '{workflow_to_run}' not found: {e}")
        print(f"ERROR: Workflow file '{workflow_to_run}' not found in '{config.WORKFLOW_DIR}'.")
        sys.exit(1)
    except (ValueError, TypeError) as e:
        logger.critical(f"Workflow execution failed due to configuration or setup error: {e}", exc_info=True)
        print(f"ERROR: Workflow setup failed. Check configuration and logs. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An critical error occurred during workflow execution: {e}", exc_info=True)
        print(f"ERROR: Workflow execution failed unexpectedly. Check logs at {config.LOG_FILE}. Error: {e}")
        sys.exit(1)

    logger.info("--- Arche System Shutdown ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Arche (ResonantiA Protocol v3.5) Master Orchestrator.")
    parser.add_argument(
        "workflow",
        nargs='?', # Make workflow optional
        default=None,
        help="Optional: Name of a specific workflow file to run directly (e.g., basic_analysis.json)."
    )
    parser.add_argument(
        "-c", "--context",
        type=str,
        default=None,
        help="JSON string representing the initial context for the workflow (e.g., '{\"user_query\": \"Analyze X\"}')."
    )
    parser.add_argument(
        "-q", "--query",
        type=str,
        default=None,
        help="A user query to be processed by the Maestro's intelligent routing. Overrides queries in context."
    )
    parser.add_argument(
        "-m", "--mode",
        type=str,
        default="orchestrate",
        choices=["orchestrate", "weave", "compare"],
        help="Execution mode: 'orchestrate' for modern RISE engine, 'weave' for legacy method, 'compare' for both."
    )
    args = parser.parse_args()

    main(workflow_to_run=args.workflow, initial_context_json=args.context, user_query=args.query, mode=args.mode)