# ResonantiA Protocol v3.0 - Unit Test for Workflow Engine
# Tests the core functionality of the WorkflowEngine class.

import os
import json
import pytest
from workflow_engine import WorkflowEngine

@pytest.fixture
def workflow_engine():
    return WorkflowEngine()

@pytest.fixture
def sample_workflow_data():
    workflow_path = os.path.join('workflows', 'sample_workflow.json')
    with open(workflow_path, 'r') as f:
        return json.load(f)

def test_load_workflow(workflow_engine, sample_workflow_data):
    workflow_path = os.path.join('workflows', 'sample_workflow.json')
    result = workflow_engine.load_workflow(workflow_path)
    assert result['workflow_data'] == sample_workflow_data
    assert result['reflection']['status'] == 'success'
    assert result['reflection']['confidence'] > 0.9

def test_execute_workflow(workflow_engine, sample_workflow_data):
    result = workflow_engine.execute_workflow(sample_workflow_data)
    assert 'step_results' in result
    assert result['reflection']['status'] == 'partial'
    assert result['reflection']['confidence'] > 0.0 