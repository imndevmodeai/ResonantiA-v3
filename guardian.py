import os
import json
import time
import subprocess
import logging
from typing import Dict, Any, List, Set

# Configure logging for the Guardian
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Guardian] - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("guardian.log")
    ]
)

# --- Configuration ---
GUARDIAN_RULES_FILE = "guardian_rules.json"
OUTPUT_DIR = "outputs"
POLL_INTERVAL_SECONDS = 10
PYTHON_EXECUTABLE = "python3" # Or "python" depending on the environment

def load_rules() -> List[Dict[str, Any]]:
    """Loads automation rules from the JSON file."""
    try:
        with open(GUARDIAN_RULES_FILE, 'r') as f:
            rules = json.load(f)
        logging.info(f"Successfully loaded {len(rules)} rules from {GUARDIAN_RULES_FILE}.")
        return [rule for rule in rules if rule.get("enabled", False)]
    except FileNotFoundError:
        logging.error(f"CRITICAL: Rules file not found at {GUARDIAN_RULES_FILE}. Guardian cannot operate.")
        return []
    except json.JSONDecodeError:
        logging.error(f"CRITICAL: Could not decode JSON from {GUARDIAN_RULES_FILE}. Please check its format.")
        return []

def render_context(template: Dict[str, Any], trigger_data: Dict[str, Any]) -> str:
    """Renders a context dictionary using data from the trigger event."""
    # Simple string replacement; a more robust solution could use Jinja2
    rendered_str = json.dumps(template)
    for key, value in trigger_data.items():
        placeholder = f"{{{{ trigger.{key} }}}}"
        # Ensure value is a JSON-compatible string
        value_str = json.dumps(str(value)) 
        rendered_str = rendered_str.replace(placeholder, value_str)
    return rendered_str

def check_for_failed_workflows(rules: List[Dict[str, Any]], processed_runs: Set[str]) -> None:
    """Scans the output directory for failed workflow results that match rules."""
    completion_rules = [rule for rule in rules if rule.get("trigger", {}).get("type") == "on_workflow_completion"]
    if not completion_rules:
        return

    try:
        for filename in os.listdir(OUTPUT_DIR):
            if filename.startswith("result_") and filename.endswith(".json"):
                # Extract run_id from filename, assuming format result_*_run_id.json
                try:
                    # Find the last underscore, which precedes the run ID
                    run_id = filename.rsplit('_', 1)[1].replace('.json', '')
                except IndexError:
                    continue

                if run_id in processed_runs:
                    continue

                # Mark as processed immediately to avoid race conditions
                processed_runs.add(run_id)
                
                filepath = os.path.join(OUTPUT_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        result_data = json.load(f)
                except (IOError, json.JSONDecodeError) as e:
                    logging.warning(f"Could not read or parse result file {filepath}: {e}")
                    continue

                status = result_data.get("overall_status")
                workflow_file = result_data.get("workflow_name")

                for rule in completion_rules:
                    config = rule.get("trigger", {}).get("config", {})
                    watch_status = config.get("watch_status")
                    watch_workflow = config.get("watch_workflow_name")

                    # Check if the result matches the rule's criteria
                    if (status == watch_status) and (not watch_workflow or watch_workflow == workflow_file):
                        logging.info(f"TRIGGERED: Rule '{rule['rule_name']}' for failed workflow '{workflow_file}' (Run ID: {run_id}).")
                        
                        # Find the failed task summary
                        failed_summary = "Could not determine failed task."
                        if isinstance(result_data.get("task_summary"), dict):
                            for task, summary in result_data["task_summary"].items():
                                if summary.get("status") == "failed":
                                    failed_summary = f"Task '{task}' failed with error: {summary.get('error', 'Unknown error')}"
                                    break

                        trigger_data = {
                            "run_id": run_id,
                            "workflow_file": workflow_file,
                            "failed_task_summary": failed_summary
                        }
                        
                        execute_action(rule["action"], trigger_data)

    except Exception as e:
        logging.error(f"An error occurred while checking for failed workflows: {e}", exc_info=True)


def execute_action(action: Dict[str, Any], trigger_data: Dict[str, Any]) -> None:
    """Executes the action defined in a rule, e.g., running a new workflow."""
    if action.get("type") == "run_workflow":
        workflow_to_run = action.get("workflow_to_run")
        if not workflow_to_run:
            logging.error("Action 'run_workflow' is missing the 'workflow_to_run' key.")
            return

        context_json = "{}"
        if "context_template" in action:
            context_json = render_context(action["context_template"], trigger_data)

        command = [
            PYTHON_EXECUTABLE,
            "-m",
            "Three_PointO_ArchE.main",
            "run-workflow",
            workflow_to_run,
            "--context-json",
            context_json
        ]
        
        try:
            logging.info(f"Executing command: {' '.join(command)}")
            # Run the command in the background
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logging.info(f"Successfully launched diagnostic workflow '{workflow_to_run}' for trigger '{trigger_data.get('run_id')}'.")
        except Exception as e:
            logging.error(f"Failed to execute action for workflow '{workflow_to_run}': {e}", exc_info=True)

def main():
    """The main loop for the Guardian process."""
    logging.info("Guardian process started. Monitoring for trigger conditions...")
    rules = load_rules()
    processed_runs: Set[str] = set()

    if not rules:
        logging.warning("No enabled rules found. Guardian will idle.")
        return

    while True:
        try:
            check_for_failed_workflows(rules, processed_runs)
            # Future checks (like on_system_divergence) would be called here
            
            time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logging.info("Guardian process shutting down.")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred in the main Guardian loop: {e}", exc_info=True)
            # Avoid crash-looping by waiting a bit longer after an unexpected error
            time.sleep(POLL_INTERVAL_SECONDS * 3)


if __name__ == "__main__":
    # Add a check for the main entry point to add a --context-json argument
    # to the main.py file
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--context-json", help="JSON string of initial context data for the workflow.", type=str, default=None)
    
    main() 