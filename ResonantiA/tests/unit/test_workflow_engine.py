# ResonantiA Protocol v3.0 - Unit Test for Workflow Engine
# Tests the core functionality of the IARCompliantWorkflowEngine class.

import os
import json
import pytest
from unittest.mock import MagicMock, patch, mock_open
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE import config # For config.WORKFLOW_DIR

# Minimal valid reflection for mocked actions
MOCK_REFLECTION = {"status": "Success", "summary": "Mocked action executed.", "confidence": 0.99, "alignment_check": "N/A", "potential_issues": None, "raw_output_preview": "mock"}

@pytest.fixture
def workflow_engine():
    """Provides a IARCompliantWorkflowEngine instance."""
    return IARCompliantWorkflowEngine()

@pytest.fixture
def sample_workflow_abs_path():
    """Returns the absolute path to sample_workflow.json for direct loading."""
    # Path for fixture to load the file directly, relative to project root
    path = os.path.join(config.WORKFLOW_DIR, 'sample_workflow.json')
    if not os.path.exists(path):
        pytest.fail(f"sample_workflow.json not found at {path}. Ensure WORKFLOW_DIR is correct and file exists.")
    return path

@pytest.fixture
def sample_workflow_data(sample_workflow_abs_path):
    """Loads sample_workflow.json content for comparison."""
    with open(sample_workflow_abs_path, 'r') as f:
        return json.load(f)

def test_load_workflow(workflow_engine, sample_workflow_data, sample_workflow_abs_path):
    # Pass only the filename to load_workflow, as it uses config.WORKFLOW_DIR
    workflow_filename = os.path.basename(sample_workflow_abs_path)
    result = workflow_engine.load_workflow(workflow_filename)
    # The load_workflow method returns the workflow dictionary directly.
    # Check for a known key within the workflow structure itself.
    assert result is not None
    assert "name" in result # 'name' is a top-level key in sample_workflow.json
    assert "tasks" in result
    assert isinstance(result["tasks"], dict)

@patch('ResonantiA.ArchE.workflow_engine.execute_action')
def test_run_workflow_simple(mock_execute_action, workflow_engine, sample_workflow_abs_path):
    mock_execute_action.return_value = {"output_data": "mocked_output", "reflection": MOCK_REFLECTION}
    
    workflow_filename = os.path.basename(sample_workflow_abs_path)
    initial_context = {"input_key": "input_value"}
    final_results = workflow_engine.run_workflow(workflow_filename, initial_context)

    assert final_results is not None
    assert final_results["workflow_status"] == "Completed Successfully"
    # Task results are stored directly under their task_id in the final_results dictionary
    assert "start_task" in final_results 
    assert "end_task" in final_results
    assert final_results["start_task"]["output_data"] == "mocked_output"
    mock_execute_action.assert_any_call('display_output', {'content': 'Sample workflow started.'}) # Check first call

# Test for execute_workflow attribute error - this test should now fail or be removed
# as execute_workflow is not the primary method to run workflows.
# Keeping it to see if it triggers an AttributeError, then we'll remove it.
def test_has_no_execute_workflow_method(workflow_engine):
    # This test is expected to pass as execute_workflow was removed/renamed in favor of run_workflow
    with pytest.raises(AttributeError):
        workflow_engine.execute_workflow({}) # Pass a dummy dict 