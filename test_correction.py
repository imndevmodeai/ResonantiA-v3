import json
from prompts.formulate_correction_prompt import PROMPT

# Hypothetical failure scenario
failure_scenario = {
    "failure_context": {
        "task_id": "task_1749426473362_0",
        "description": "Analyze user sentiment from logs",
        "required_capability": "data_analysis",
        "status": "failed",
        "error_type": "data_processing_error",
        "error_message": "Insufficient data points for reliable sentiment analysis",
        "context": {
            "data_source": "user_logs_2024",
            "timeframe": "last_24_hours",
            "data_points": 12,
            "minimum_required": 100,
            "analysis_method": "sentiment_classifier_v2"
        }
    }
}

# Format the prompt with our scenario
formatted_prompt = PROMPT.format(
    dissonance_analysis=json.dumps(failure_scenario, indent=2),
    original_context="Task was initiated to analyze user sentiment from recent logs to inform product decisions."
)

print("=== Correction Prompt Response ===")
print(formatted_prompt)
print("\n=== Expected Correction Plan ===")
print("""
{
    "correction_plan": {
        "root_cause": "Insufficient data volume for reliable sentiment analysis",
        "immediate_actions": [
            {
                "action": "Extend data collection timeframe",
                "justification": "Current 24-hour window yields only 12 data points, below minimum threshold of 100",
                "implementation": "Modify data collection parameters to include last 7 days of logs"
            },
            {
                "action": "Implement data quality check",
                "justification": "Prevent future failures by validating data volume before analysis",
                "implementation": "Add pre-analysis validation step in sentiment analysis workflow"
            }
        ],
        "preventive_measures": [
            {
                "measure": "Dynamic timeframe adjustment",
                "justification": "Automatically adjust collection window based on data density",
                "implementation": "Add adaptive timeframe logic to data collection module"
            },
            {
                "measure": "Data volume monitoring",
                "justification": "Early detection of potential data insufficiency",
                "implementation": "Implement real-time monitoring of data point accumulation"
            }
        ],
        "success_criteria": [
            "Minimum 100 data points collected",
            "Sentiment analysis confidence score > 0.85",
            "Data quality validation passed"
        ],
        "rollback_plan": {
            "trigger": "Data quality validation failure",
            "actions": [
                "Revert to previous timeframe settings",
                "Notify system administrator",
                "Log failure for analysis"
            ]
        }
    }
}
""") 