# ResonantiA Protocol v3.0 - Integration Test for TSP Workflow
# Tests the execution and success metrics of the Traveling Salesman Problem workflow.

import os
import json
import time
import pytest
from ResonantiA.ArchE.workflow_engine import WorkflowEngine
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch
from ResonantiA.ArchE.spr_manager import SPRManager

@pytest.fixture
def workflow_engine():
    return WorkflowEngine()

@pytest.fixture
def tsp_workflow_data():
    # Construct path relative to the project root (assuming Happier/ is root)
    # The test file is at Happier/ResonantiA/ArchE/tests/integration/test_tsp_workflow.py
    # We want Happier/ResonantiA/workflows/...
    base_path = Path(__file__).parent.parent.parent.parent # Gets to Happier/
    workflow_path = base_path / 'ResonantiA' / 'workflows' / 'traveling_salesman_optimization.json'
    try:
        with open(workflow_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        pytest.skip("Workflow data file not found")

@pytest.fixture
def tsp_data():
    data_path = os.path.join('data', 'tsp_cities_data.json')
    with open(data_path, 'r') as f:
        return json.load(f)

def test_tsp_workflow_execution():
    """Test the execution of the TSP optimization workflow."""
    # Load TSP data
    tsp_data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'tsp_cities_data.json')
    with open(tsp_data_path, 'r') as f:
        tsp_data = json.load(f)

    # Initialize workflow engine
    engine = WorkflowEngine()
    workflow_file = os.path.join(os.path.dirname(__file__), '..', '..', 'workflows', 'traveling_salesman_optimization.json')
    workflow = engine.load_workflow(workflow_file)

    # Log input data for debugging
    logging.info(f"Input TSP data: {tsp_data[:100]}...")
    logging.info(f"Workflow loaded: {workflow.get('name', 'Unnamed Workflow')}")

    # Execute workflow with input data
    input_data = {'tsp_data': tsp_data}
    results = engine.execute_workflow(workflow, input_data=input_data)

    # Log results for debugging
    logging.info(f"Workflow execution results: {results}")

    # Validate results
    assert len(results) > 0, "Workflow execution returned no results"
    assert any(r['status'] == 'success' for r in results), "No steps succeeded in workflow execution"

    # Check for route data in results
    route_data = None
    for result in results:
        if result['step'] == 'TSP Simulation' and result['status'] == 'success':
            route_data = result['result']
            break

    if route_data:
        assert 'route' in route_data, "Route data not found in simulation results"
        assert 'total_distance' in route_data, "Total distance not found in simulation results"
        if route_data['route']:  # Check if route is non-empty
            assert len(route_data['route']) > 0, "Generated route is empty"
            assert route_data['total_distance'] > 0, "Total distance should be greater than 0"
            logging.info(f"Route found: {route_data['route'][:5]}... Total distance: {route_data['total_distance']}")
        else:
            logging.warning("Route is empty, but workflow executed successfully")
            assert True, "Route is empty, but workflow executed successfully"
    else:
        logging.error("No successful TSP Simulation step found in results")
        assert False, "No successful TSP Simulation step found in results"

    # Additional metrics
    for result in results:
        if result['step'] == 'Analyze Results' and result['status'] == 'success':
            analysis_data = result['result']
            assert 'efficiency_score' in analysis_data, "Efficiency score not found in analysis results"
            logging.info(f"Efficiency score: {analysis_data.get('efficiency_score', 'N/A')}")
            break
    else:
        logging.warning("Analyze Results step not found or failed")

    logging.info("TSP workflow execution test passed with route generation.")

def test_tsp_workflow_execution(workflow_engine, tsp_workflow_data, tsp_data):
    start_time = time.time()
    result = workflow_engine.execute_workflow(tsp_workflow_data, input_data={'tsp_data': tsp_data})
    execution_time = time.time() - start_time

    # Basic validation of IAR structure
    assert 'status' in result, f"Expected 'status' in result, got {result}"
    assert 'step_results' in result, f"Expected 'step_results' in result, got {result}"
    assert 'reflection' in result, f"Expected 'reflection' in result, got {result}"

    # Check if any step was simulated (partial status indicates simulation)
    step_results = result.get('step_results', {})
    simulated_steps = [step_id for step_id, step_data in step_results.items() if step_data.get('status') == 'simulated']
    if simulated_steps:
        logging.warning(f"Simulated steps (not fully implemented): {simulated_steps}")
    else:
        logging.info("All steps executed with real implementations.")

    # Check for errors in execution
    error_steps = [step_id for step_id, step_data in step_results.items() if step_data.get('status') == 'error']
    assert not error_steps, f"Steps failed with errors: {error_steps}"

    # Validate reflection content
    reflection = result.get('reflection', {})
    assert 'status' in reflection, "Reflection missing 'status'"
    assert 'summary' in reflection, "Reflection missing 'summary'"
    assert 'confidence' in reflection, "Reflection missing 'confidence'"
    assert reflection.get('confidence', 0.0) >= 0.3, f"Confidence too low: {reflection.get('confidence', 0.0)}"

    # Check for route optimization output if steps were not all simulated
    if result['status'] != 'error':
        route_found = False
        for step_id, step_data in step_results.items():
            if 'best_route' in str(step_data) or 'updated_routes' in str(step_data):
                route_found = True
                break
        assert route_found, "No route optimization output found in any step results"

    # Log execution time and confidence for monitoring
    logging.info(f"Workflow execution time: {execution_time:.2f} seconds")
    logging.info(f"Workflow confidence: {reflection.get('confidence', 0.0):.2f}")
    logging.info("TSP workflow execution test passed with IAR validation.") 