# --- START OF FILE ArchE/synergy_analysis_tool.py ---
# ResonantiA Protocol v3.0 - synergy_analysis_tool.py
# Implements the Synergy Analysis Tool for assessing "1+1=3" effects.
# Relies on LLM for qualitative assessment and generates IAR.

import logging
import json
from typing import Dict, Any, Optional, List
# Use relative imports for internal modules
try:
    from . import config
    from .tools import invoke_llm # To call the LLM
    from .llm_providers import LLMProviderError # To handle LLM errors
except ImportError:
    # Fallback for standalone or testing if needed
    class FallbackConfig: pass
    config = FallbackConfig()
    def invoke_llm(inputs: Dict[str, Any]) -> Dict[str, Any]: # Dummy invoke_llm
        return {"response_text": "{ \"achieved_level\": \"Moderate (Simulated)\", \"assessment_summary\": \"Simulated synergy assessment.\", \"supporting_evidence_points\": [\"Simulated point 1\"] }", "error": None, "reflection": {"status": "Success", "confidence": 0.5}}
    class LLMProviderError(Exception): pass
    logging.warning("config.py or tools.py not found via relative import for synergy_analysis_tool, using fallbacks.")

logger = logging.getLogger(__name__)

# --- IAR Helper Function ---
def _create_reflection(status: str, summary: str, confidence: Optional[float], alignment: Optional[str], issues: Optional[List[str]], preview: Any) -> Dict[str, Any]:
    """Helper function to create the standardized IAR reflection dictionary."""
    if confidence is not None: confidence = max(0.0, min(1.0, confidence))
    issues_list = issues if issues else None
    try:
        preview_str = json.dumps(preview, default=str) if isinstance(preview, (dict, list)) else str(preview)
        if preview_str and len(preview_str) > 150: preview_str = preview_str[:150] + "..."
    except Exception:
        try: preview_str = str(preview); preview_str = preview_str[:150] + "..." if len(preview_str) > 150 else preview_str
        except Exception: preview_str = "[Preview Error]"
    return {"status": status, "summary": summary, "confidence": confidence, "alignment_check": alignment if alignment else "N/A", "potential_issues": issues_list, "raw_output_preview": preview_str}

def perform_synergy_analysis(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    [IAR Enabled] Performs a meta-analysis on a list of task results to assess synergistic outcomes.

    Args:
        inputs (Dict[str, Any]): Dictionary containing:
            task_results_list (List[Dict]): A list of result dictionaries from
                                            previously executed tasks. Each dict in the
                                            list should contain its own 'outputs' and
                                            'reflection' (IAR).
            synergy_postulate (str): A textual description of the expected synergistic
                                     effect or the "1+1=3" goal for this set of tasks.
            synergy_metrics_description (str, optional): A textual description of
                                                        conceptual metrics or indicators
                                                        that would signify synergy.
            llm_provider (str, optional): Specific LLM provider to use.
            llm_model (str, optional): Specific LLM model to use.

    Returns:
        Dict[str, Any]: Dictionary containing:
            synergy_assessment (Dict):
                postulate_analyzed (str): The input synergy_postulate.
                achieved_level (str): Qualitative assessment (e.g., High, Moderate, Low, Interference).
                assessment_summary (str): Narrative from LLM explaining the assessment.
                supporting_evidence_points (List[str]): Points highlighted by LLM.
                confidence_in_assessment (float): This tool's confidence in its own assessment.
            error (Optional[str]): Error message if analysis failed.
            reflection (Dict[str, Any]): Standardized IAR dictionary for this tool's execution.
    """
    # --- Initialize Results & Reflection ---
    primary_result = {
        "synergy_assessment": {
            "postulate_analyzed": inputs.get("synergy_postulate", "N/A"),
            "achieved_level": "Undetermined",
            "assessment_summary": "Analysis not performed or failed.",
            "supporting_evidence_points": [],
            "confidence_in_assessment": 0.0
        },
        "error": None
    }
    reflection_status = "Failure"
    reflection_summary = "Synergy analysis initialization failed."
    confidence = 0.0
    alignment = "N/A"
    issues: List[str] = ["Initialization error."]
    preview = None

    try:
        # --- Extract & Validate Inputs ---
        task_results_list = inputs.get("task_results_list")
        synergy_postulate = inputs.get("synergy_postulate")
        synergy_metrics_desc = inputs.get("synergy_metrics_description", "Not specified.")

        if not isinstance(task_results_list, list) or not task_results_list:
            raise ValueError("Input 'task_results_list' must be a non-empty list of task result dictionaries.")
        if not synergy_postulate or not isinstance(synergy_postulate, str):
            raise ValueError("Input 'synergy_postulate' (string) is required.")

        # --- Aggregate Data from Task Results for LLM Prompt ---
        aggregated_inputs_summary = []
        overall_input_confidence_sum = 0
        num_valid_inputs = 0
        for i, task_res in enumerate(task_results_list):
            if isinstance(task_res, dict):
                task_id = task_res.get("task_id", f"InputTask_{i+1}") # Use task_id if available
                # Try to get primary output summary; fallback to reflection summary
                output_summary = "Output not directly summarized."
                # Check common primary output keys
                if "response_text" in task_res: output_summary = str(task_res["response_text"])[:200] + "..."
                elif "results" in task_res: output_summary = str(task_res["results"])[:200] + "..."
                elif "analysis_results" in task_res: output_summary = str(task_res["analysis_results"])[:200] + "..."
                elif "stdout" in task_res: output_summary = str(task_res["stdout"])[:200] + "..."


                iar = task_res.get("reflection", {})
                if isinstance(iar, dict):
                    status = iar.get("status", "N/A")
                    conf = iar.get("confidence")
                    iss = iar.get("potential_issues", [])
                    summary_text = iar.get("summary", output_summary) # Use IAR summary or output summary

                    aggregated_inputs_summary.append(
                        f"Input Task '{task_id}':\n"
                        f"  Status: {status}\n"
                        f"  Confidence: {conf if conf is not None else 'N/A'}\n"
                        f"  Summary/Output Snippet: {summary_text}\n"
                        f"  Potential Issues Noted: {iss if iss else 'None'}"
                    )
                    if conf is not None:
                        overall_input_confidence_sum += conf
                        num_valid_inputs += 1
                else:
                    aggregated_inputs_summary.append(f"Input Task '{task_id}': Reflection data missing or invalid.")
            else:
                 aggregated_inputs_summary.append(f"Input Task_{i+1}: Invalid format (not a dictionary).")

        avg_input_confidence = (overall_input_confidence_sum / num_valid_inputs) if num_valid_inputs > 0 else 0.0
        inputs_summary_str = "\n\n".join(aggregated_inputs_summary)

        # --- Craft LLM Prompt for Synergy Assessment ---
        prompt = f"""You are a Meta-Analyst for the ResonantiA AI system. Your task is to assess the synergistic ("1+1=3") outcome from a series of preceding analytical steps.

        **Synergy Postulate (Expected Emergent Value):**
        {synergy_postulate}

        **Conceptual Synergy Metrics/Indicators (How synergy might manifest):**
        {synergy_metrics_desc}

        **Summary of Inputs from Preceding Tasks (Outputs & IARs):**
        ---
        {inputs_summary_str}
        ---

        **Assessment Instructions:**
        Based on the Synergy Postulate, the Conceptual Metrics, and the aggregated inputs:
        1.  **Emergent Insights:** Did the combination of inputs lead to novel insights, conclusions, or capabilities that were NOT explicitly present in any single input? Describe them.
        2.  **Consistency & Coherence:** Are the combined results internally consistent? Do they form a more coherent or comprehensive picture than individual parts?
        3.  **Confidence/Uncertainty Modification:** Did the combination of inputs lead to a significant increase in overall confidence for a key finding, or a significant reduction in previously noted uncertainties/issues?
        4.  **Alignment with Postulate:** How well do the observed outcomes align with the stated Synergy Postulate?
        5.  **Overall Synergy Level:** Based on the above, assess the overall level of synergy achieved.

        **Output STRICTLY in the following JSON format:**
        ```json
        {{
            "achieved_level": "High | Moderate | Low | Interference | Undetermined",
            "assessment_summary": "Provide a detailed narrative explaining your synergy assessment, referencing specific points from the inputs, postulate, and metrics. Explain WHY you chose the achieved_level.",
            "supporting_evidence_points": [
                "List specific observations from the inputs that support your assessment (e.g., 'Novel connection found between Task A output and Task B output leading to new hypothesis X.').",
                "Point out if confidence in a key finding was demonstrably increased by combining results.",
                "Note if prior issues were resolved or new ones emerged from the combination."
            ],
            "limitations_of_assessment": [
                "State any limitations in your ability to assess synergy based on the provided information (e.g., 'Postulate was vague', 'Metrics were hard to quantify from inputs')."
            ]
        }}
        ```
        """

        # --- Invoke LLM ---
        logger.info("Invoking LLM for synergy assessment...")
        llm_inputs = {
            "prompt": prompt,
            "provider": inputs.get("llm_provider"), # Pass through if specified
            "model": inputs.get("llm_model")
        }
        llm_result = invoke_llm(llm_inputs)

        if llm_result.get("error"):
            raise LLMProviderError(f"LLM call failed during synergy assessment: {llm_result['error']}")
        if not llm_result.get("response_text"):
            raise ValueError("LLM provided no response text for synergy assessment.")

        # --- Parse LLM Response & Populate Results ---
        try:
            synergy_eval = json.loads(llm_result["response_text"])
            primary_result["synergy_assessment"]["achieved_level"] = synergy_eval.get("achieved_level", "Undetermined")
            primary_result["synergy_assessment"]["assessment_summary"] = synergy_eval.get("assessment_summary", "LLM did not provide a narrative summary.")
            primary_result["synergy_assessment"]["supporting_evidence_points"] = synergy_eval.get("supporting_evidence_points", [])
            # This tool's confidence in its *own* assessment
            # Could be based on LLM's IAR confidence, or a heuristic
            llm_iar_confidence = llm_result.get("reflection", {}).get("confidence", 0.7) # Default if LLM IAR missing
            # If LLM response is clear and structured, higher confidence in this tool's assessment
            clarity_factor = 0.9 if all(k in synergy_eval for k in ["achieved_level", "assessment_summary"]) else 0.5
            primary_result["synergy_assessment"]["confidence_in_assessment"] = round(llm_iar_confidence * clarity_factor, 2)

            reflection_status = "Success"
            summary = f"Synergy assessment completed. Level: {primary_result['synergy_assessment']['achieved_level']}."
            confidence = primary_result["synergy_assessment"]["confidence_in_assessment"]
            alignment = "Aligned with meta-analytical goal of assessing synergy."
            issues = synergy_eval.get("limitations_of_assessment", [])
            if not LLM_AVAILABLE: issues.append("Synergy assessment relied on simulated LLM call.") # If invoke_llm was dummy
            preview = primary_result["synergy_assessment"]

        except json.JSONDecodeError as e_json:
            error_msg = f"Failed to parse LLM JSON response for synergy assessment: {e_json}. Response: {llm_result['response_text'][:200]}..."
            logger.error(error_msg)
            primary_result["error"] = error_msg
            issues.append(error_msg)
            summary = "Synergy assessment failed: LLM response parsing error."
            confidence = 0.1
        except Exception as e_parse:
            error_msg = f"Error processing LLM response for synergy: {e_parse}"
            logger.error(error_msg, exc_info=True)
            primary_result["error"] = error_msg
            issues.append(error_msg)
            summary = f"Synergy assessment failed: LLM response processing error."
            confidence = 0.1


    except (ValueError, TypeError, ImportError, LLMProviderError) as e_val:
        primary_result["error"] = f"Input/Validation/LLM Error: {e_val}"
        issues = [str(e_val)]; summary = f"Synergy analysis failed: {e_val}"; confidence = 0.0
    except Exception as e_synergy:
        primary_result["error"] = f"Unexpected synergy analysis error: {e_synergy}"
        logger.error(f"Unexpected error during synergy analysis: {e_synergy}", exc_info=True)
        issues = [f"Unexpected Error: {e_synergy}"]; summary = f"Synergy analysis failed unexpectedly: {e_synergy}"; confidence = 0.0

    # Final status check
    if primary_result["error"]: reflection_status = "Failure"

    return {**primary_result, "reflection": _create_reflection(reflection_status, summary, confidence, alignment, issues, preview)}

# --- END OF FILE ArchE/synergy_analysis_tool.py ---