# ResonantiA Protocol v3.0 - iar_analyzer.py
# Module for Proactive IAR Anomaly Detection and Analysis.
# Implements core logic for the IARAnomalyDetectoR SPR.

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
# Potential future import: from .predictive_modeling_tool import run_prediction

logger = logging.getLogger(__name__)

# --- Configuration (Potentially move to config.py or load from SPRManager) ---
DEFAULT_BASELINE_WINDOW = 100  # Number of IAR records to establish an initial baseline
DEFAULT_METRIC_THRESHOLDS = {
    "confidence_drop_std_devs": 2.5, # Number of std devs below mean to flag confidence drop
    "new_issue_frequency_threshold": 3 # Number of times a new issue type appears to be flagged
}

class IARAnalyzer:
    """
    Provides functionalities to analyze streams of Integrated Action Reflection (IAR)
    data to detect anomalies, learn baselines, and support predictive system health.
    Corresponds to the conceptual `IARAnomalyDetectoR`.
    """
    def __init__(self, predictive_modeling_tool_func: Optional[callable] = None):
        """
        Initializes the IARAnalyzer.

        Args:
            predictive_modeling_tool_func (Optional[callable]): A function reference
                to the `run_prediction` method of the PredictiveModelingTool,
                if available and to be used for advanced forecasting-based anomaly detection.
        """
        self.baselines: Dict[str, Dict[str, Any]] = {} # Stores learned baselines for various metrics/contexts
                                                       # Will also store 'issue_baseline': {'known_issue_types': set(), 
                                                       #                              'new_issue_candidates': {issue_str: streak_count}}
        self.iar_history: Dict[str, List[Dict[str, Any]]] = {} # Stores recent IAR data for context-specific analysis
        # self.predictive_tool = predictive_modeling_tool_func # Store for later use
        logger.info("IARAnalyzer initialized.")

    def update_iar_history(self, context_key: str, iar_record: Dict[str, Any], max_history_len: int = 200) -> None:
        """
        Updates the IAR history for a given context (e.g., a specific tool or workflow step).
        
        Args:
            context_key (str): A unique key identifying the source/context of the IAR (e.g., "ToolName_ActionType").
            iar_record (Dict[str, Any]): The IAR dictionary.
            max_history_len (int): Maximum number of IAR records to keep for this context.
        """
        if context_key not in self.iar_history:
            self.iar_history[context_key] = []
        self.iar_history[context_key].append(iar_record)
        # Keep history to a manageable size
        if len(self.iar_history[context_key]) > max_history_len:
            self.iar_history[context_key].pop(0)

    def calculate_basic_iar_metrics(self, iar_stream: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates basic summary metrics from a list/stream of IAR records.

        Args:
            iar_stream (List[Dict[str, Any]]): A list of IAR data dictionaries.
                                              Each dictionary is expected to conform to IAR structure,
                                              e.g., {"status": "Success", "confidence": 0.9, "potential_issues": []}.

        Returns:
            Dict[str, Any]: A dictionary of calculated metrics.
                            Example: {"average_confidence": 0.85, "failure_rate": 0.1, 
                                      "critical_issue_count": 2, "unique_issue_types": set("type1", "type2")}
        """
        if not iar_stream:
            return {
                "average_confidence": None,
                "failure_rate": None,
                "critical_issue_count": 0,
                "unique_issue_types": set(),
                "total_records": 0
            }

        confidences = [r["confidence"] for r in iar_stream if isinstance(r.get("confidence"), (int, float))]
        statuses = [r.get("status", "Unknown").lower() for r in iar_stream]
        potential_issues_lists = [r.get("potential_issues", []) for r in iar_stream]

        avg_confidence = np.mean(confidences) if confidences else None
        failure_count = sum(1 for s in statuses if s == "failure")
        failure_rate = failure_count / len(iar_stream) if iar_stream else None
        
        all_issues = []
        for issues_list in potential_issues_lists:
            if isinstance(issues_list, list):
                all_issues.extend(issues_list)
        
        # This is a simplified view of "critical". A more robust system might have severity levels in issues.
        critical_issue_count = sum(1 for issue in all_issues if isinstance(issue, str) and "critical" in issue.lower())
        unique_issue_types = set(issue for issue in all_issues if isinstance(issue, str))


        return {
            "average_confidence": avg_confidence,
            "failure_rate": failure_rate,
            "critical_issue_count": critical_issue_count,
            "unique_issue_types": unique_issue_types,
            "total_records": len(iar_stream)
        }

    def update_metric_baseline(self, context_key: str, metric_name: str, value: Any, window_size: int = DEFAULT_BASELINE_WINDOW) -> None:
        """
        Updates the baseline for a specific metric within a given context using a moving window approach.
        For simplicity, this example uses a simple moving average and standard deviation for numeric values.
        More sophisticated baseline models can be implemented.

        Args:
            context_key (str): Context identifier (e.g., "ToolName_ActionType").
            metric_name (str): Name of the metric (e.g., "average_confidence").
            value (Any): The new value of the metric.
            window_size (int): The number of recent values to consider for the baseline.
        """
        if context_key not in self.baselines:
            self.baselines[context_key] = {}
        
        if metric_name not in self.baselines[context_key]:
            self.baselines[context_key][metric_name] = {"values": [], "mean": None, "std_dev": None, "count": 0}

        baseline_data = self.baselines[context_key][metric_name]
        
        if isinstance(value, (int, float)): # Only calculate mean/std for numeric
            baseline_data["values"].append(value)
            if len(baseline_data["values"]) > window_size:
                baseline_data["values"].pop(0)
            
            if baseline_data["values"]:
                baseline_data["mean"] = np.mean(baseline_data["values"])
                baseline_data["std_dev"] = np.std(baseline_data["values"])
            else: # Should not happen if value is appended
                baseline_data["mean"] = None
                baseline_data["std_dev"] = None
        
        baseline_data["count"] += 1
        # For non-numeric types or if specific baseline logic is needed, extend here.
        # For example, for 'unique_issue_types' (a set), the baseline might be a historical set of common issues.

    def update_issue_type_baselines(self, context_key: str, current_issue_types: set) -> None:
        """
        Updates the baseline for issue types within a given context.
        Manages known issue types and tracks new issue candidates with their appearance streaks.

        Args:
            context_key (str): Context identifier (e.g., "ToolName_ActionType").
            current_issue_types (set): A set of unique issue strings observed in the current IAR stream.
        """
        if context_key not in self.baselines:
            self.baselines[context_key] = {}
        
        if "issue_baseline" not in self.baselines[context_key]:
            self.baselines[context_key]["issue_baseline"] = {
                "known_issue_types": set(),
                "new_issue_candidates": {} # issue_str: streak_count
            }

        issue_baseline = self.baselines[context_key]["issue_baseline"]
        known_issues = issue_baseline["known_issue_types"]
        new_candidates = issue_baseline["new_issue_candidates"]

        # Issues that were candidates but are not in the current stream have their streak broken
        # and are moved to known issues (if not already there) and removed from candidates.
        disappeared_candidates = set(new_candidates.keys()) - current_issue_types
        for issue in disappeared_candidates:
            known_issues.add(issue) # Add to known as it's no longer consistently new
            del new_candidates[issue]

        # Process current issues
        for issue in current_issue_types:
            if issue in known_issues:
                continue # Already known, nothing to do

            if issue in new_candidates:
                new_candidates[issue] += 1 # Increment streak
            else:
                # This is a brand new issue, not known and not a candidate yet
                new_candidates[issue] = 1 # Start streak

    def detect_confidence_drop(self, context_key: str, current_confidence: float) -> Optional[Dict[str, Any]]:
        """
        Detects a significant drop in confidence for a given context based on its baseline.

        Args:
            context_key (str): Context identifier.
            current_confidence (float): The current confidence score.

        Returns:
            Optional[Dict[str, Any]]: An anomaly dictionary if a drop is detected, else None.
        """
        baseline_metric_data = self.baselines.get(context_key, {}).get("average_confidence")
        if not baseline_metric_data or baseline_metric_data["mean"] is None or baseline_metric_data["std_dev"] is None:
            logger.debug(f"No baseline or insufficient data for confidence in context '{context_key}'.")
            return None

        mean_confidence = baseline_metric_data["mean"]
        std_dev_confidence = baseline_metric_data["std_dev"]
        threshold_multiplier = DEFAULT_METRIC_THRESHOLDS.get("confidence_drop_std_devs", 2.5)
        
        # Handle near-zero std_dev to avoid overly sensitive detection on stable metrics
        effective_std_dev = max(std_dev_confidence, 0.01) # Minimum std_dev to consider

        lower_bound = mean_confidence - (threshold_multiplier * effective_std_dev)

        if current_confidence < lower_bound:
            anomaly_details = {
                "anomaly_type": "SignificantConfidenceDrop",
                "context_key": context_key,
                "current_value": current_confidence,
                "baseline_mean": mean_confidence,
                "baseline_std_dev": std_dev_confidence,
                "threshold_bound": lower_bound,
                "message": f"Confidence {current_confidence:.2f} in '{context_key}' is significantly below baseline mean {mean_confidence:.2f} (lower bound {lower_bound:.2f})."
            }
            logger.warning(anomaly_details["message"])
            return anomaly_details
        return None

    def detect_new_frequent_issue_types(self, context_key: str, current_issue_types: set) -> List[Dict[str, Any]]:
        """
        Detects new issue types that appear frequently compared to a baseline of known/common issues.
        This method relies on `update_issue_type_baselines` having been called first for the same `current_issue_types`.

        Args:
            context_key (str): Context identifier.
            current_issue_types (set): A set of unique issue strings observed currently (should match the set used in the last call to `update_issue_type_baselines`).
        
        Returns:
            List[Dict[str, Any]]: A list of anomaly dictionaries for new frequent issues.
        """
        anomalies = []
        if context_key not in self.baselines or "issue_baseline" not in self.baselines[context_key]:
            logger.debug(f"No issue baseline found for context '{context_key}'. Cannot detect new frequent issues.")
            return anomalies

        issue_baseline = self.baselines[context_key]["issue_baseline"]
        known_issues = issue_baseline["known_issue_types"]
        new_candidates = issue_baseline["new_issue_candidates"]
        
        frequency_threshold = DEFAULT_METRIC_THRESHOLDS.get("new_issue_frequency_threshold", 3)

        issues_to_make_known_after_detection = set()
        logger.debug(f"Detecting new frequent issues in '{context_key}'. Candidates: {new_candidates}, Known: {known_issues}, Threshold: {frequency_threshold}")

        for issue, streak in list(new_candidates.items()): # Iterate over a copy for safe modification
            if issue in known_issues: # Should ideally not happen if logic in update is correct
                continue

            if streak >= frequency_threshold:
                anomaly_details = {
                    "anomaly_type": "NewFrequentIssue",
                    "context_key": context_key,
                    "issue_type": issue,
                    "appearance_streak": streak,
                    "threshold": frequency_threshold,
                    "message": f"New issue type '{issue}' in '{context_key}' has appeared {streak} consecutive times, meeting threshold {frequency_threshold}."
                }
                logger.warning(anomaly_details["message"])
                anomalies.append(anomaly_details)
                
                # Mark for transition to known_issues after detection to avoid re-flagging immediately
                issues_to_make_known_after_detection.add(issue)

        # Transition flagged issues from candidates to known
        if issues_to_make_known_after_detection:
            for issue in issues_to_make_known_after_detection:
                if issue in new_candidates: # Check if still a candidate (it should be)
                    del new_candidates[issue]
                known_issues.add(issue)
                logger.info(f"Issue type '{issue}' in context '{context_key}' transitioned to known after being flagged as a new frequent issue.")

        return anomalies

    def analyze_iar_stream_for_anomalies(self, context_key: str, iar_stream: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Main analysis function for a stream of IARs from a specific context.
        Calculates metrics, updates baselines, and detects anomalies.

        Args:
            context_key (str): Context identifier (e.g., "ToolName_ActionType").
            iar_stream (List[Dict[str, Any]]): A list of IAR data dictionaries for this context.
        
        Returns:
            List[Dict[str, Any]]: A list of detected anomaly dictionaries.
        """
        if not iar_stream:
            return []
            
        logger.info(f"Analyzing IAR stream for context '{context_key}' ({len(iar_stream)} records).")
        
        # 1. Store raw IARs in history (optional, if needed for more complex context)
        # for iar_record in iar_stream:
        #    self.update_iar_history(context_key, iar_record)

        # 2. Calculate current metrics from the provided stream
        current_metrics = self.calculate_basic_iar_metrics(iar_stream)
        logger.debug(f"Current metrics for '{context_key}': {current_metrics}")

        # 3. Update baselines with current metrics
        if current_metrics.get("average_confidence") is not None:
            self.update_metric_baseline(context_key, "average_confidence", current_metrics["average_confidence"])
        if current_metrics.get("failure_rate") is not None:
            self.update_metric_baseline(context_key, "failure_rate", current_metrics["failure_rate"])
        # Add baseline updates for other relevant metrics (e.g., issue counts/types)
        
        # Update issue type baselines based on the current stream's unique issues
        self.update_issue_type_baselines(context_key, current_metrics["unique_issue_types"])

        # 4. Detect anomalies based on current metrics and updated baselines
        detected_anomalies = []
        
        # Confidence drop detection
        if current_metrics.get("average_confidence") is not None:
            confidence_anomaly = self.detect_confidence_drop(context_key, current_metrics["average_confidence"])
            if confidence_anomaly:
                detected_anomalies.append(confidence_anomaly)
        
        # New frequent issue types detection
        new_issue_anomalies = self.detect_new_frequent_issue_types(context_key, current_metrics["unique_issue_types"])
        detected_anomalies.extend(new_issue_anomalies)

        # Add other anomaly detection calls here (e.g., failure rate spikes)

        if detected_anomalies:
            logger.warning(f"Detected {len(detected_anomalies)} anomalies in context '{context_key}'.")
        else:
            logger.info(f"No anomalies detected in context '{context_key}' based on current checks.")
            
        return detected_anomalies

# Example Usage (Conceptual - would be part of a workflow or monitoring service)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) # Changed to INFO for cleaner default output
    analyzer = IARAnalyzer()

    # Simulate some IAR data for a specific tool/action
    context = "MyTool_ProcessData"
    # Baseline stream has one recurring minor issue
    sample_iars_normal_baseline_stream = [
        {"status": "Success", "confidence": 0.9, "potential_issues": ["minor_hiccup"]},
        {"status": "Success", "confidence": 0.95, "potential_issues": []},
        {"status": "Success", "confidence": 0.88, "potential_issues": ["minor_hiccup"]},
        {"status": "Success", "confidence": 0.92, "potential_issues": []},
        {"status": "Success", "confidence": 0.85, "potential_issues": ["minor_hiccup"]},
    ] * 20 # Multiply for a larger baseline stream (DEFAULT_BASELINE_WINDOW is 100)

    # Establish a baseline by processing the normal stream
    logger.info(f"--- Establishing baseline for context '{context}' ---")
    analyzer.analyze_iar_stream_for_anomalies(context, sample_iars_normal_baseline_stream)
    
    baseline_info = analyzer.baselines.get(context, {}).get('average_confidence')
    if baseline_info and baseline_info.get('mean') is not None:
        logger.info(f"Baseline for '{context}' (average_confidence): Mean={baseline_info['mean']:.2f}, StdDev={baseline_info['std_dev']:.2f}, Count={baseline_info['count']}")
    else:
        logger.info(f"Baseline for '{context}' (average_confidence) not fully established or metric missing.")
    
    issue_baseline_info = analyzer.baselines.get(context, {}).get('issue_baseline')
    if issue_baseline_info:
        logger.info(f"Issue Baseline for '{context}': Known={issue_baseline_info['known_issue_types']}, Candidates={issue_baseline_info['new_issue_candidates']}")


    # Simulate a new batch of IARs with a potential anomaly (confidence drop + new issues)
    logger.info("\\n--- Simulating new IAR batch with potential anomalies (confidence drop & new issues) ---")
    sample_iars_anomaly_1 = [
        {"status": "Success", "confidence": 0.5, "potential_issues": ["new_critical_issue_A"]}, # Lower confidence, new issue
        {"status": "Success", "confidence": 0.6, "potential_issues": ["new_critical_issue_A", "another_new_issue_X"]},
        {"status": "Success", "confidence": 0.45, "potential_issues": ["new_critical_issue_A"]},
        {"status": "Failure", "confidence": 0.3, "potential_issues": ["investigate_ASAP", "new_critical_issue_A"]},
        {"status": "Success", "confidence": 0.55, "potential_issues": ["new_critical_issue_A"]},
    ] # new_critical_issue_A appears 5 times, another_new_issue_X appears 1 time
    
    anomalies_found_1 = analyzer.analyze_iar_stream_for_anomalies(context, sample_iars_anomaly_1)
    
    if anomalies_found_1:
        logger.info(f"\\n--- Anomalies Detected (Batch 1) ({context}) ---")
        for anomaly in anomalies_found_1:
            logger.info(f"  {anomaly}")
    else:
        logger.info(f"\\n--- No Anomalies Detected in Batch 1 ({context}) ---")
    
    logger.info(f"Issue Baseline after Batch 1: Known={analyzer.baselines[context]['issue_baseline']['known_issue_types']}, Candidates={analyzer.baselines[context]['issue_baseline']['new_issue_candidates']}")

    # Simulate another batch - new_critical_issue_A should be known now (or will be after this run if not flagged).
    # another_new_issue_X streak continues. A new issue_B appears.
    logger.info("\\n--- Simulating Batch 2: new_critical_issue_A should be known, another_new_issue_X continues, new_issue_B appears ---")
    sample_iars_anomaly_2 = [
        {"status": "Success", "confidence": 0.8, "potential_issues": ["new_critical_issue_A", "another_new_issue_X", "new_issue_B"]},
        {"status": "Success", "confidence": 0.85, "potential_issues": ["another_new_issue_X"]},
        {"status": "Success", "confidence": 0.75, "potential_issues": ["new_critical_issue_A", "new_issue_B"]},
        {"status": "Success", "confidence": 0.82, "potential_issues": ["another_new_issue_X"]},
        {"status": "Success", "confidence": 0.78, "potential_issues": ["new_critical_issue_A", "another_new_issue_X", "new_issue_B"]},
    ] # new_critical_issue_A appears 3 times (should be known)
      # another_new_issue_X appears 4 times (streak = 1+4 = 5 or 1+3=4 if prev stream reset it) -> should be anomaly
      # new_issue_B appears 3 times (streak = 3) -> should be anomaly
      
    anomalies_found_2 = analyzer.analyze_iar_stream_for_anomalies(context, sample_iars_anomaly_2)

    if anomalies_found_2:
        logger.info(f"\\n--- Anomalies Detected (Batch 2) ({context}) ---")
        for anomaly in anomalies_found_2:
            logger.info(f"  {anomaly}")
    else:
        logger.info(f"\\n--- No Anomalies Detected in Batch 2 ({context}) ---")
        
    logger.info(f"Issue Baseline after Batch 2: Known={analyzer.baselines[context]['issue_baseline']['known_issue_types']}, Candidates={analyzer.baselines[context]['issue_baseline']['new_issue_candidates']}")

    # Simulate a batch where 'another_new_issue_X' and 'new_issue_B' might disappear, breaking their streak
    # and moving them to known if they were candidates.
    logger.info("\\n--- Simulating Batch 3: Previously new issues disappear, should move to known if candidates ---")
    sample_iars_normalizing = [
        {"status": "Success", "confidence": 0.9, "potential_issues": ["minor_hiccup"]}, # Original known issue
        {"status": "Success", "confidence": 0.92, "potential_issues": []},
        {"status": "Success", "confidence": 0.88, "potential_issues": ["newly_known_issue_C"]}, # A completely different issue
    ] * 2 # 'newly_known_issue_C' will appear twice, not hitting threshold
    
    anomalies_found_3 = analyzer.analyze_iar_stream_for_anomalies(context, sample_iars_normalizing)
    
    if anomalies_found_3:
        logger.info(f"\\n--- Anomalies Detected (Batch 3) ({context}) ---") # Should ideally be none from new issues
        for anomaly in anomalies_found_3:
            logger.info(f"  {anomaly}")
    else:
        logger.info(f"\\n--- No Anomalies Detected in Batch 3 ({context}) ---")

    logger.info(f"Issue Baseline after Batch 3: Known={analyzer.baselines[context]['issue_baseline']['known_issue_types']}, Candidates={analyzer.baselines[context]['issue_baseline']['new_issue_candidates']}")
    
    baseline_info_final = analyzer.baselines.get(context, {}).get('average_confidence')
    if baseline_info_final and baseline_info_final.get('mean') is not None:
        logger.info(f"Final baseline for '{context}' (average_confidence): Mean={baseline_info_final['mean']:.2f}, StdDev={baseline_info_final['std_dev']:.2f}, Count={baseline_info_final['count']}") 