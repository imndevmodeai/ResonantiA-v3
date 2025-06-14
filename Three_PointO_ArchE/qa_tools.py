# Three_PointO_ArchE/qa_tools.py
import subprocess
import json
from typing import Dict, Any
from .utils import _create_reflection

def run_code_linter(directory: str, **kwargs) -> Dict[str, Any]:
    """
    Runs pylint on a specified directory and returns a detailed report.
    Accepts directory as a keyword argument.
    """
    if not directory:
        return {
            "error": "Input 'directory' is required.",
            "reflection": _create_reflection(
                status="Failed",
                summary="Missing required input: directory.",
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
                "reflection": _create_reflection(
                    status="Success",
                    summary=summary,
                    confidence=1.0,
                    raw_output_preview=raw_report
                )
            }
        except json.JSONDecodeError:
            summary = f"Pylint ran on '{directory}' but produced invalid JSON output."
            return {
                "error": "Failed to parse pylint JSON output.",
                "raw_output": raw_report,
                "reflection": _create_reflection(
                    status="Failed",
                    summary=summary,
                    confidence=0.5,
                    potential_issues="Pylint output was not valid JSON. This can happen with fatal errors.",
                    raw_output_preview=raw_report
                )
            }

    except FileNotFoundError:
        return {
            "error": "pylint command not found. Please ensure it is installed and in the system's PATH.",
            "reflection": _create_reflection(
                status="Failed",
                summary="Pylint executable not found.",
                confidence=0.0
            )
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "reflection": _create_reflection(
                status="Error",
                summary=f"An unexpected error occurred while running pylint: {str(e)}",
                confidence=0.0
            )
        } 