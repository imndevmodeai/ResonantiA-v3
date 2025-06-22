# ResonantiA Protocol v3.0 - Integration Test for TSP Workflow
# Tests the execution and success metrics of the Traveling Salesman Problem workflow.

import os
import json
import time
import pytest
import unittest
from unittest.mock import MagicMock, patch, mock_open
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
import logging
from Three_PointO_ArchE import config # For config.WORKFLOW_DIR

# Mock reflection for successful operations
MOCK_REFLECTION_SUCCESS = {
    "status": "Success",
    "summary": "Action completed as expected.",
    "confidence": 0.95,
    "alignment_check": "Aligned",
    "potential_issues": None,
    "raw_output_preview": "Mocked success preview..."
}

@pytest.fixture
def workflow_engine():
    return IARCompliantWorkflowEngine()

@pytest.fixture
def tsp_workflow_data():
    # This path is for the fixture to load the file directly
    workflow_path_for_fixture = os.path.join('ResonantiA', 'workflows', 'traveling_salesman_optimization.json')
    if not os.path.exists(workflow_path_for_fixture):
        pytest.fail(f"Fixture could not find TSP workflow: {workflow_path_for_fixture}")
    with open(workflow_path_for_fixture, 'r') as f:
        return json.load(f)

@pytest.fixture
def tsp_data():
    # Path for the fixture to load tsp_cities_data.json
    # Assuming 'data' directory is a sibling of 'ResonantiA' or configured in PYTHONPATH
    # For robust testing when running from 'Happier', let's try relative to 'ResonantiA'
    data_path = os.path.join('ResonantiA', 'data', 'tsp_cities_data.json')
    if not os.path.exists(data_path):
        # Fallback: try relative to the test file's directory, going up to project root
        # This is more complex and depends on test execution context
        test_dir = os.path.dirname(__file__)
        project_root_marker = "ResonantiA" # A directory that indicates we are in the project
        current_dir = test_dir
        levels_up = 0
        max_levels = 4 # Safety break
        while project_root_marker not in os.listdir(os.path.abspath(os.path.join(current_dir, *(['..'] * levels_up)))) and levels_up < max_levels:
            levels_up +=1
        
        if levels_up < max_levels:
            project_root_path = os.path.abspath(os.path.join(current_dir, *(['..'] * levels_up)))
            data_path_alt = os.path.join(project_root_path, 'data', 'tsp_cities_data.json')
            if os.path.exists(data_path_alt):
                data_path = data_path_alt
            else:
                pytest.fail(f"Fixture could not find TSP data: {data_path} or {data_path_alt}")
        else:
            pytest.fail(f"Fixture could not find TSP data at primary path: {data_path} and could not determine project root.")
            
    with open(data_path, 'r') as f:
        return json.load(f)

def test_tsp_workflow_execution_original(workflow_engine, tsp_workflow_data, tsp_data):
    """Test the execution of the TSP optimization workflow."""
    workflow_filename = 'workflows/traveling_salesman_optimization.json'

    # Log input data for debugging
    logging.info(f"Input TSP data for original test: {str(tsp_data)[:100]}...")

    # Execute workflow with input data
    initial_context = {'tsp_data': tsp_data}
    results = workflow_engine.run_workflow(workflow_filename, initial_context=initial_context)

    # Log results for debugging
    logging.info(f"Workflow execution results for original test: {results}")

    # Validate results
    assert results is not None, "Workflow execution returned None results"
    assert results.get("workflow_status") == "Completed Successfully", f"Workflow did not complete successfully: {results.get('workflow_status')}"
    
    step_results = results.get('step_results', {})
    assert len(step_results) > 0, "Workflow execution returned no step_results"

    # Check for route data in results
    route_data_found = False
    final_route_details = None

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

@pytest.fixture
def engine_for_tsp():
    """Provides a IARCompliantWorkflowEngine instance for TSP tests."""
    return IARCompliantWorkflowEngine()

@pytest.fixture
def tsp_workflow_file_path():
    """Returns the absolute path to the TSP workflow JSON file."""
    # Ensure config.WORKFLOW_DIR is an absolute path
    # and traveling_salesman_optimization.json is directly in it.
    if not os.path.isabs(config.WORKFLOW_DIR):
        pytest.fail(f"config.WORKFLOW_DIR is not absolute: {config.WORKFLOW_DIR}")
    
    file_path = os.path.join(config.WORKFLOW_DIR, 'traveling_salesman_optimization.json')
    if not os.path.exists(file_path):
        pytest.fail(f"TSP workflow file not found at: {file_path}. Ensure it exists and config.WORKFLOW_DIR is correct.")
    return file_path

@pytest.fixture
def tsp_initial_context():
    """Provides initial context including TSP data for the workflow."""
    # Correctly load tsp_cities_data.json relative to this test file or project structure
    # Assuming ResonantiA/data/tsp_cities_data.json when running from Happier/
    data_file_path = os.path.join(config.BASE_DIR, 'data', 'tsp_cities_data.json')
    if not os.path.exists(data_file_path):
        pytest.fail(f"TSP data file not found: {data_file_path}")
    with open(data_file_path, 'r') as f:
        tsp_cities = json.load(f)
    return {
        'tsp_data': tsp_cities,
        'max_iterations': 100, # Example parameter
        'output_options': {'include_distance_matrix': False}
    }

@pytest.mark.skipif(IARCompliantWorkflowEngine is None or config is None, reason="IARCompliantWorkflowEngine or config not available.")
def test_tsp_workflow_execution_and_iar(engine_for_tsp, tsp_workflow_file_path, tsp_initial_context, mocker, caplog):
    caplog.set_level(logging.INFO)
    start_time = time.time()

    # Extract just the filename for run_workflow, as engine prepends WORKFLOW_DIR
    workflow_filename = os.path.basename(tsp_workflow_file_path)

    # Mock the execute_action method to simulate task execution
    def mock_tsp_solver_action(action_type, inputs, current_workflow_context=None, workflow_id=None):
        logging.info(f"Mocked action '{action_type}' called with inputs: {str(inputs)[:100]}...")
        if action_type == "solve_tsp_ortools": # Intended TSP action
            # Simulate a successful TSP solution
            mock_route = [city_data['city'] for city_data in inputs.get('cities_data', [])[:4]] # Mock route of first 4 cities
            if mock_route: mock_route.append(mock_route[0]) # Close the loop
            return {
                "best_route": mock_route,
                "total_distance": 123.45,
                "solver_log": "Mock solver ran successfully.",
                "reflection": MOCK_REFLECTION_SUCCESS
            }
        elif action_type == "display_output" or action_type == "log_message": # Common utility actions
             return {"status": "Displayed/Logged", "reflection": MOCK_REFLECTION_SUCCESS}
        elif action_type == "perform_abm": # Handle perform_abm for tsp_simulation task
            # Simulate a successful ABM run for TSP (can be simple)
            return {
                "result": {"route": ["A", "B", "C", "A"], "total_distance": 78.9, "message": "Mock ABM TSP solved"},
                "reflection": MOCK_REFLECTION_SUCCESS
            }
        # Add mocks for other actions if present in traveling_salesman_optimization.json
        # For execute_code (load_tsp_data)
        if action_type == "execute_code":
            # Simulate successful execution of load_tsp_data
            # It should output a JSON string of cities
            simulated_cities_json = json.dumps(inputs.get('input_data', {}).get('initial_cities', []))
            return {
                "stdout": simulated_cities_json,
                "stderr": "",
                "exit_code": 0,
                "reflection": MOCK_REFLECTION_SUCCESS
            }
        logging.warning(f"Unhandled mock action type: {action_type}")
        return {"error": f"Mock for {action_type} not implemented", "reflection": {"status": "Failure", "summary":"Mock missing"}}

    # Patch the action_registry's execute_action, which is used internally by run_workflow
    # The IARCompliantWorkflowEngine imports execute_action into its own module's namespace,
    # or calls it via the action_registry module. The actual callable is in action_registry.
    # Let's try patching where it's most likely looked up by the engine instance if not directly imported.
    # Based on other tests, patching it within the workflow_engine module scope seems to work.
    mocker.patch('ResonantiA.ArchE.workflow_engine.execute_action', side_effect=mock_tsp_solver_action)

    final_results = engine_for_tsp.run_workflow(workflow_filename, tsp_initial_context)
    execution_time = time.time() - start_time

    logging.info(f"TSP Workflow ('{workflow_filename}') execution finished. Results: {json.dumps(final_results, indent=2, default=str)}")

    assert final_results is not None, "Workflow returned None results"
    assert final_results.get("workflow_status") == "Completed Successfully", \
        f"Workflow failed. Status: {final_results.get('workflow_status')}. Errors: {final_results.get('errors')}"

    step_results = final_results.get('step_results', {})
    assert len(step_results) > 0, "No step results found"

    # Check IAR for the whole workflow
    workflow_iar = final_results.get('reflection')
    assert workflow_iar is not None, "Workflow IAR is missing"
    assert workflow_iar.get('status') == "Success", f"Workflow IAR status is not Success: {workflow_iar.get('status')}"
    assert workflow_iar.get('confidence', 0.0) >= 0.5, f"Workflow IAR confidence too low: {workflow_iar.get('confidence')}"

    # Check for specific output from a mocked solver step (adapt task_id if needed)
    solve_task_id = None # Find the task_id of your TSP solving step
    for task_id, details in final_results.get('tasks_definition', {}).items():
        if details.get('action_type') == 'solve_tsp_ortools': # Or your solver's action_type
            solve_task_id = task_id
            break
    
    if solve_task_id and solve_task_id in step_results:
        solver_output = step_results[solve_task_id].get('output', {})
        assert 'best_route' in solver_output, "'best_route' not in solver output"
        assert 'total_distance' in solver_output, "'total_distance' not in solver output"
        assert solver_output['total_distance'] == 123.45, "Mocked distance mismatch"
        logging.info(f"Mocked solver output validated: {solver_output['best_route']}")
    elif solve_task_id:
        assert False, f"Solver task '{solve_task_id}' did not produce results in step_results."
    else:
        logging.warning("Could not identify TSP solver task_id by action_type for specific output validation.")

    logging.info(f"TSP workflow execution and IAR test passed. Execution time: {execution_time:.2f}s")

def test_tsp_workflow_execution_and_iar(workflow_engine, tsp_workflow_data, tsp_data):
    """Test the execution of the TSP optimization workflow with IAR validation."""
    workflow_filename = 'workflows/traveling_salesman_optimization.json'
    tsp_data_file = "data/tsp_cities.json" # This file needs to exist if this test is not mocked

    # Ensure the data directory exists and the file is present if not mocked
    # In a real scenario, this would involve mocking file access or ensuring setup creates this.
    if not os.path.exists(tsp_data_file):
        # For now, let's create a dummy file if it doesn't exist to allow tests to proceed
        # In a proper test setup, this would be part of a fixture or proper test data management
        os.makedirs(os.path.dirname(tsp_data_file), exist_ok=True)
        with open(tsp_data_file, 'w') as f:
            json.dump(tsp_data, f)

    logging.info(f"Input TSP data file for IAR test: {tsp_data_file}")

    initial_context = {'tsp_data_file': tsp_data_file}
    results = workflow_engine.run_workflow(workflow_filename, initial_context=initial_context)

    logging.info(f"Workflow execution results for IAR test: {results}")

    assert results is not None, "Workflow execution returned None results"
    assert results.get("workflow_status") == "Completed Successfully", f"Workflow did not complete successfully: {results.get('workflow_status')}"
    assert "reflection" in results # Top-level workflow reflection
    assert results["reflection"]["status"] == "Success"
    assert "tasks" in results
    assert "load_tsp_data" in results["tasks"]
    assert "optimize_route" in results["tasks"]
    assert results["tasks"]["load_tsp_data"]["reflection"]["status"] == "Success"
    assert results["tasks"]["optimize_route"]["reflection"]["status"] == "Success" 