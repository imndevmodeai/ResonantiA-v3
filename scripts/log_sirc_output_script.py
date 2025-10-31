# scripts/log_sirc_output_script.py
import logging
import json
import sys
import os

logger = logging.getLogger("workflow_task_log")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

null = None
final_output_for_workflow = None
error_messages = []

try:
    refined_objective_str = os.environ.get("SIRC_REFINED_OBJECTIVE")
    refined_tasks_json_str = os.environ.get("SIRC_REFINED_TASKS_SUGGESTIONS")
    process_notes_str = os.environ.get("SIRC_PROCESS_NOTES")

    if refined_objective_str is None:
        error_messages.append("SIRC_REFINED_OBJECTIVE environment variable not found.")
    if refined_tasks_json_str is None:
        error_messages.append("SIRC_REFINED_TASKS_SUGGESTIONS environment variable not found.")
    # process_notes_str can be optional or empty, handled by default in construction

    logger.info(f"SIRC log_sirc_output_script: REFINED_OBJECTIVE (first 100 chars): {str(refined_objective_str)[:100]}")
    logger.info(f"SIRC log_sirc_output_script: REFINED_TASKS_JSON_STR (first 100 chars): {str(refined_tasks_json_str)[:100]}")
    logger.info(f"SIRC log_sirc_output_script: PROCESS_NOTES_STR (first 100 chars): {str(process_notes_str)[:100]}")

    sirc_results_dict = {}
    valid_data_present = False

    if refined_objective_str:
        sirc_results_dict["sirc_refined_objective"] = refined_objective_str
        valid_data_present = True
    else:
        sirc_results_dict["sirc_refined_objective"] = None
        if "SIRC_REFINED_OBJECTIVE environment variable not found." not in error_messages: # only add if not already there due to None
             error_messages.append("SIRC_REFINED_OBJECTIVE was empty.")


    if refined_tasks_json_str:
        try:
            # Clean up potential markdown code blocks if any
            cleaned_tasks_str = refined_tasks_json_str.strip()
            if cleaned_tasks_str.startswith("```json") and cleaned_tasks_str.endswith("```"):
                cleaned_tasks_str = cleaned_tasks_str[7:-3].strip()
            elif cleaned_tasks_str.startswith("```") and cleaned_tasks_str.endswith("```"):
                cleaned_tasks_str = cleaned_tasks_str[3:-3].strip()
            
            if cleaned_tasks_str.lower() == "null" or not cleaned_tasks_str:
                 sirc_results_dict["sirc_refined_tasks_suggestions"] = None
                 if cleaned_tasks_str.lower() == "null":
                      error_messages.append("SIRC_REFINED_TASKS_SUGGESTIONS was 'null'.")
                 else:
                      error_messages.append("SIRC_REFINED_TASKS_SUGGESTIONS was empty after cleaning.")
            else:
                sirc_results_dict["sirc_refined_tasks_suggestions"] = json.loads(cleaned_tasks_str)
                valid_data_present = True
        except json.JSONDecodeError as je:
            error_messages.append(f"Failed to parse SIRC_REFINED_TASKS_SUGGESTIONS JSON: {je}. Value (first 100): {refined_tasks_json_str[:100]}")
            sirc_results_dict["sirc_refined_tasks_suggestions"] = None
    else:
        sirc_results_dict["sirc_refined_tasks_suggestions"] = None
        if "SIRC_REFINED_TASKS_SUGGESTIONS environment variable not found." not in error_messages:
            error_messages.append("SIRC_REFINED_TASKS_SUGGESTIONS was empty or None.")


    sirc_results_dict["sirc_process_notes"] = process_notes_str if process_notes_str else None # Handles empty string or None from env
    if process_notes_str: # only consider it valid_data_present if it's not None/empty
        valid_data_present = True


    if not valid_data_present and not error_messages: # If all inputs were None/empty but not explicitly "not found"
        error_messages.append("All SIRC output environment variables were effectively empty or None.")

    if error_messages:
        logger.warning("SIRC log_sirc_output_script: Errors encountered while processing environment variables: " + "; ".join(error_messages))
        final_output_for_workflow = {
            "sirc_refined_outputs_preview": sirc_results_dict, # Show what was partially assembled
            "message": "Errors processing SIRC output from environment variables.",
            "errors_logged": error_messages
        }
    else:
        logger.info("SIRC log_sirc_output_script: Successfully processed SIRC outputs from environment variables.")
        final_output_for_workflow = {"sirc_refined_outputs": sirc_results_dict}

except Exception as e:
    logger.error(f"SIRC log_sirc_output_script: General error. Error: {e}", exc_info=True)
    # Capture env vars for debugging if general error
    env_vars_preview = {
        "SIRC_REFINED_OBJECTIVE_PREVIEW": str(os.environ.get("SIRC_REFINED_OBJECTIVE"))[:100],
        "SIRC_REFINED_TASKS_SUGGESTIONS_PREVIEW": str(os.environ.get("SIRC_REFINED_TASKS_SUGGESTIONS"))[:100],
        "SIRC_PROCESS_NOTES_PREVIEW": str(os.environ.get("SIRC_PROCESS_NOTES"))[:100]
    }
    final_output_for_workflow = {
        "error": "General failure in processing SIRC output for logging (script error).",
        "details": str(e),
        "env_vars_preview": env_vars_preview
    }

try:
    if final_output_for_workflow is None: # Should not happen with current logic but as a safeguard
        final_output_for_workflow = {"error": "final_output_for_workflow was None before final print! Script logic error."}
    print(json.dumps(final_output_for_workflow))
except Exception as e_final_print:
    # Fallback for critical failure during the final print itself
    fallback_error_payload = {
        "error": "Critical: Exception during final json.dumps in log_sirc_output_script!",
        "details": str(e_final_print),
        "type_of_final_output_var": str(type(final_output_for_workflow)),
        "final_output_var_str_attempt": str(final_output_for_workflow)[:200] + "..."
    }
    print(json.dumps(fallback_error_payload))
 