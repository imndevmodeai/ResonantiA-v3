#!/usr/bin/env python3
import json

def rebuild_knowledge_tapestry():
    """
    Clean rebuild of the SPR knowledge tapestry from scratch.
    """
    
    # Original 9 SPRs from the initial knowledge base
    original_sprs = [
        {
            "name": "Initial_Analysis_Standard",
            "description": "A standard, top-level analysis of a new user query or objective. Identifies key entities, intent, and constraints.",
            "type": "Cognitive",
            "parameters": {
                "user_query": "The full text of the user's request.",
                "context": "Any relevant session context or prior information."
            },
            "template": "Analyze the query: '{user_query}'. Identify key entities, user intent, and any explicit or implicit constraints. Consider the provided context: {context}. Formulate a high-level plan."
        },
        {
            "name": "Hypothesis_Generation",
            "description": "Generates a set of testable hypotheses based on an initial analysis or a set of observations.",
            "type": "Analytical",
            "parameters": {
                "initial_analysis_summary": "The summary from an Initial_Analysis_Standard SPR.",
                "data_summary": "A summary of available data relevant to the query."
            },
            "template": "Based on the analysis '{initial_analysis_summary}' and data '{data_summary}', generate 3-5 distinct, testable hypotheses. For each, specify the evidence that would support or refute it."
        },
        {
            "name": "Code_Generation_Python",
            "description": "Generates Python code to accomplish a specific, well-defined task.",
            "type": "Action",
            "parameters": {
                "task_description": "A clear and unambiguous description of the task.",
                "dependencies": "A list of required Python libraries.",
                "input_data_format": "The format of the input data.",
                "output_data_format": "The expected format of the output."
            },
            "template": "Write a Python script to perform the following task: {task_description}. The script should use the following libraries: {dependencies}. It will receive input in the format '{input_data_format}' and must produce output in the format '{output_data_format}'. Include error handling and comments."
        },
        {
            "name": "Causal_Effect_Estimation",
            "description": "Uses the DoWhy library to estimate the causal effect of a treatment on an outcome.",
            "type": "Analytical.Causal",
            "parameters": {
                "dataset_name": "The variable name of the dataset to use for the analysis (e.g., 'df').",
                "treatment_variable": "The name of the treatment variable column.",
                "outcome_variable": "The name of the outcome variable column.",
                "graph_model": "The causal graph model (e.g., GML string).",
                "estimation_method": "The specific estimation method to use (e.g., 'backdoor.linear_regression')."
            },
            "template": "Estimate the causal effect of '{treatment_variable}' on '{outcome_variable}' using the dataset loaded in the `{dataset_name}` variable and the causal graph '{graph_model}'. Employ the '{estimation_method}' method."
        },
        {
            "name": "Timeseries_Forecasting_ARIMA",
            "description": "Performs time series forecasting using an ARIMA model.",
            "type": "Analytical.Predictive",
            "parameters": {
                "timeseries_data_name": "The variable name of the time series data (e.g., list or pandas Series).",
                "order": "The (p, d, q) order of the ARIMA model.",
                "forecast_steps": "The number of future steps to forecast."
            },
            "template": "Fit an ARIMA model with order {order} to the timeseries data in `{timeseries_data_name}`. Forecast the next {forecast_steps} steps and provide the prediction interval."
        },
        {
            "name": "Agent_Based_Model_Simulation",
            "description": "Runs an Agent-Based Model simulation using the Mesa framework.",
            "type": "Simulation.ABM",
            "parameters": {
                "agent_definitions_code": "The Python code defining the Agent class(es) for the model.",
                "model_definition_code": "The Python code defining the Model class for the simulation environment.",
                "simulation_steps": "The number of steps to run the simulation for."
            },
            "template": "Run an ABM simulation for {simulation_steps} steps. The model uses agents defined by the code: \n```python\n{agent_definitions_code}\n```\n The simulation environment is defined by this model class:\n```python\n{model_definition_code}\n```\nCollect data on key model parameters at each step and return the results."
        },
        {
            "name": "Workflow_Execution_Plan",
            "description": "Creates a multi-step execution plan (workflow) to achieve a complex objective, chaining together other SPRs.",
            "type": "Meta.Planning",
            "parameters": {
                "objective": "The high-level objective to be achieved.",
                "available_tools": "A list of available tools or SPRs.",
                "constraints": "Any constraints on the execution (e.g., budget, time)."
            },
            "template": "To achieve the objective '{objective}', create a JSON workflow definition. The plan should sequence actions from the available tools: {available_tools}. Adhere to the following constraints: {constraints}. Define dependencies between steps, passing outputs as inputs to subsequent steps where necessary."
        },
        {
            "name": "IAR_Generation",
            "description": "Generates an Integrated Action Reflection (IAR) for a completed action.",
            "type": "Meta.Reflection",
            "parameters": {
                "action_name": "The name of the action/SPR that was executed.",
                "action_parameters": "The parameters used for the action.",
                "action_result_summary": "A summary of the result or output of the action.",
                "action_outcome_assessment": "An assessment of whether the action achieved its immediate goal ('Success', 'Partial Success', 'Failure').",
                "confidence_score": "A score (0.0-1.0) indicating confidence in the action's success and correctness."
            },
            "template": "Generate an IAR for the action '{action_name}'. Parameters were: {action_parameters}. The result was: {action_result_summary}. The outcome was assessed as: {action_outcome_assessment}. My confidence is {confidence_score}."
        },
        {
            "name": "Metacognitive_Shift_Trigger_Analysis",
            "description": "Analyzes IARs and system state to determine if a Metacognitive Shift is required.",
            "type": "Meta.Self-Correction",
            "parameters": {
                "recent_iars_summary": "A summary of recent IARs.",
                "current_objective": "The current high-level objective.",
                "dissonance_threshold_confidence": "The confidence score threshold that triggers a shift.",
                "dissonance_threshold_outcome": "The outcome assessment (e.g., 'Failure') that triggers a shift."
            },
            "template": "Review the recent IARs summary: {recent_iars_summary}. The objective is '{current_objective}'. Given a confidence dissonance threshold of {dissonance_threshold_confidence} and an outcome threshold of '{dissonance_threshold_outcome}', is there sufficient evidence of repeated failure, low confidence, or strategy misalignment to warrant a Metacognitive Shift? If so, identify the core issue and suggest a new strategic approach."
        }
    ]
    
    # New SPRs from Keyholder - I'll build this programmatically to avoid syntax errors
    new_sprs = []
    
    # Add each new SPR individually to avoid syntax issues
    new_sprs.append({
        "spr_id": "CognitiveresonancE",
        "term": "Cognitive Resonance",
        "definition": "A state of profound, dynamic alignment between incoming data streams, deep internal analysis (via tools and SPR-activated knowledge), validated Persistent knowledgE, clearly defined strategic objectives, and the probabilistic landscape of potential outcomes, critically evaluated across the dimension of time (Temporal resonancE). It is the fundamental purpose and measure of success for Arche.",
        "category": "CoreConcept"
    })
    
    new_sprs.append({
        "spr_id": "IaR",
        "term": "Integrated Action Reflection",
        "definition": "Every discrete action executed by any tool within the ResonantiA Protocol v3.0 system intrinsically generates and returns a standardized self-assessment (reflection dictionary) alongside its primary output. This continuous stream of self-awareness data fuels ArchE's Meta cognitive capabilitieS and enables continuous learning and adaptation.",
        "category": "CoreMechanism"
    })
    
    new_sprs.append({
        "spr_id": "4dthinkinG",
        "term": "4D Thinking (Temporal Reasoning)",
        "definition": "The integrated set of principles and tools within ResonantiA Protocol v3.0 that enables ArchE to achieve Temporal resonancE by understanding, modeling, and predicting system dynamics across the dimension of time. It encompasses historical contextualization, temporal dynamics modeling, future state analysis, emergence over time simulation, and temporal causality identification.",
        "category": "CognitiveCapability"
    })
    
    # Merge all SPRs
    all_sprs = original_sprs + new_sprs
    
    # Create lookup to handle duplicates (new SPRs override old ones)
    merged_lookup = {}
    for spr in all_sprs:
        key = spr.get('spr_id') or spr.get('term') or spr.get('name')
        if key:
            merged_lookup[key] = spr
    
    final_sprs = list(merged_lookup.values())
    
    # Create final data structure
    final_data = {"spr_definitions": final_sprs}
    
    # Write to file
    target_file = 'knowledge_graph/spr_definitions_tv.json'
    try:
        with open(target_file, 'w') as f:
            json.dump(final_data, f, indent=2)
        
        # Verify
        with open(target_file, 'r') as f:
            verify_data = json.load(f)
            count = len(verify_data.get("spr_definitions", []))
        
        print(f"SUCCESS: Knowledge Tapestry rebuilt with {count} SPRs")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    rebuild_knowledge_tapestry() 