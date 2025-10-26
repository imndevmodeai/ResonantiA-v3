# Three_PointO_ArchE/qa_tools.py
import subprocess
import json
from typing import Dict, Any
from .utils.reflection_utils import create_reflection, ExecutionStatus

def run_code_linter(directory: str, **kwargs) -> Dict[str, Any]:
    """
    Runs pylint on a specified directory and returns a detailed report.
    Accepts directory as a keyword argument.
    """
    if not directory:
        return {
            "error": "Input 'directory' is required.",
            "reflection": create_reflection(
                action_name="run_code_linter",
                status=ExecutionStatus.FAILURE,
                message="Missing required input: directory.",
                confidence=0.0
            )
        }

    try:
        command = [
            "pylint",
            "--output-format=json",
            directory
        ]
        process = subprocess.run(command, capture_output=True, text=True, check=False)

        # pylint exits with a non-zero status code for various reasons,
        # so we process the output regardless of the exit code.
        raw_report = process.stdout
        
        try:
            linter_report_json = json.loads(raw_report)
            # Attempt to find the score in the stats object
            stats = next((item for item in linter_report_json if item.get("type") == "statement" and "stats" in item), None)
            score = stats.get("stats", {}).get("global_note") if stats else "N/A"

            summary = f"Pylint completed on '{directory}'. Score: {score}. Found {len(linter_report_json)} messages."
            
            return {
                "linter_report": linter_report_json,
                "summary": summary,
                "score": score,
                "reflection": create_reflection(
                    action_name="run_code_linter",
                    status=ExecutionStatus.SUCCESS,
                    message=summary,
                    confidence=1.0,
                    outputs={"linter_report": linter_report_json, "score": score}
                )
            }
        except json.JSONDecodeError:
            summary = f"Pylint ran on '{directory}' but produced invalid JSON output."
            return {
                "error": "Failed to parse pylint JSON output.",
                "raw_output": raw_report,
                "reflection": create_reflection(
                    action_name="run_code_linter",
                    status=ExecutionStatus.FAILURE,
                    message=summary,
                    confidence=0.5,
                    potential_issues=["Pylint output was not valid JSON. This can happen with fatal errors."],
                    outputs={"raw_output": raw_report}
                )
            }

    except FileNotFoundError:
        return {
            "error": "pylint command not found. Please ensure it is installed and in the system's PATH.",
            "reflection": create_reflection(
                action_name="run_code_linter",
                status=ExecutionStatus.CRITICAL_FAILURE,
                message="Pylint executable not found.",
                confidence=0.0
            )
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "reflection": create_reflection(
                action_name="run_code_linter",
                status=ExecutionStatus.CRITICAL_FAILURE,
                message=f"An unexpected error occurred while running pylint: {str(e)}",
                confidence=0.0
            )
        }

def run_workflow_suite(workflow_files: list, **kwargs) -> Dict[str, Any]:
    """
    Runs a suite of workflows and generates a comprehensive report.
    
    Args:
        workflow_files: List of paths to workflow JSON files to execute
        **kwargs: Additional arguments passed by the workflow engine
    
    Returns:
        Dict containing:
        - suite_report: Detailed report of all workflow executions
        - summary: Brief summary of the suite execution
        - reflection: IAR-compliant reflection object
    """
    from .workflow_engine import IARCompliantWorkflowEngine
    from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
    
    if not workflow_files:
        return {
            "error": "No workflow files specified",
            "reflection": create_reflection(
                action_name="run_workflow_suite",
                status=ExecutionStatus.FAILURE,
                message="No workflow files provided for testing",
                confidence=0.0
            )
        }
    
    suite_results = []
    total_workflows = len(workflow_files)
    successful_workflows = 0
    failed_workflows = 0
    
    for workflow_file in workflow_files:
        try:
            # Create a new engine instance for each workflow
            engine = IARCompliantWorkflowEngine()
            
            # Load and validate the workflow
            workflow = engine.load_workflow(workflow_file)
            if not workflow:
                raise ValueError(f"Failed to load workflow: {workflow_file}")
            
            # Execute the workflow
            start_time = datetime.now()
            result = engine.execute_workflow(workflow)
            end_time = datetime.now()
            
            # Add timing information
            execution_time = (end_time - start_time).total_seconds()
            result["execution_time_seconds"] = execution_time
            result["start_time"] = start_time.isoformat()
            result["end_time"] = end_time.isoformat()
            
            # Track success/failure
            if result.get("workflow_status") == "Completed Successfully":
                successful_workflows += 1
            else:
                failed_workflows += 1
            
            suite_results.append({
                "workflow_file": workflow_file,
                "result": result
            })
            
        except Exception as e:
            failed_workflows += 1
            suite_results.append({
                "workflow_file": workflow_file,
                "error": str(e),
                "status": "Failed"
            })
    
    # Generate summary
    summary = (
        f"Workflow Suite Results:\n"
        f"Total Workflows: {total_workflows}\n"
        f"Successful: {successful_workflows}\n"
        f"Failed: {failed_workflows}\n"
        f"Success Rate: {(successful_workflows/total_workflows)*100:.1f}%"
    )
    
    # Create detailed report
    suite_report = {
        "timestamp": now_iso(),
        "total_workflows": total_workflows,
        "successful_workflows": successful_workflows,
        "failed_workflows": failed_workflows,
        "success_rate": (successful_workflows/total_workflows)*100,
        "workflow_results": suite_results
    }
    
    return {
        "suite_report": suite_report,
        "summary": summary,
        "reflection": create_reflection(
            action_name="run_workflow_suite",
            status=ExecutionStatus.SUCCESS if failed_workflows == 0 else ExecutionStatus.WARNING,
            message=summary,
            confidence=1.0 if failed_workflows == 0 else 0.8,
            outputs={"suite_report": suite_report}
        )
    } 