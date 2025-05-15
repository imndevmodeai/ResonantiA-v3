# --- START OF FILE tests/integration/test_workflow_engine_integration.py ---
import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock # Requires pytest-mock
from typing import Dict # Import Dict

# Attempt to import necessary modules with error handling
try:
    from ResonantiA.ArchE.workflow_engine import WorkflowEngine
    from ResonantiA.ArchE.spr_manager import SPRManager
    # Import config to potentially override paths for testing
    from ResonantiA.ArchE import config
    # Assume execute_action is needed and imported by WorkflowEngine or patch it there
    # from ResonantiA.ArchE.action_registry import execute_action
except ImportError:
    try:
        from ...ArchE.workflow_engine import WorkflowEngine
        from ...ArchE.spr_manager import SPRManager
        from ...ArchE import config
        # from ...ArchE.action_registry import execute_action
    except ImportError:
         try:
             from ArchE.workflow_engine import WorkflowEngine
             from ArchE.spr_manager import SPRManager
             from ArchE import config
             # from ArchE.action_registry import execute_action
         except ImportError:
             try:
                 from ..ArchE.workflow_engine import WorkflowEngine
                 from ..ArchE.spr_manager import SPRManager
                 from ..ArchE import config
                 # from ..ArchE.action_registry import execute_action
             except ImportError:
                 print("Failed to import WorkflowEngine, SPRManager, or config. Ensure PYTHONPATH is set or tests run correctly relative to the project structure.")
                 WorkflowEngine, SPRManager, config = None, None, None

# Fixture for a WorkflowEngine instance
@pytest.fixture
def engine(tmp_path: Path, monkeypatch) -> WorkflowEngine: # Added monkeypatch
    """Provides a WorkflowEngine instance with temp dirs."""
    if not all([WorkflowEngine, SPRManager, config]):
        pytest.skip("Required modules (WorkflowEngine, SPRManager, config) not imported.")

    # Create dummy workflow/kg dirs for isolated testing
    workflow_dir = tmp_path / "workflows"
    kg_dir = tmp_path / "knowledge_graph"
    workflow_dir.mkdir()
    kg_dir.mkdir()
    # Create dummy SPR file
    spr_file = kg_dir / "spr_definitions_tv.json"
    with open(spr_file, "w") as f: json.dump([], f)

    # Use monkeypatch fixture to temporarily override config paths
    monkeypatch.setattr(config, 'WORKFLOW_DIR', str(workflow_dir))
    monkeypatch.setattr(config, 'KNOWLEDGE_GRAPH_DIR', str(kg_dir))
    monkeypatch.setattr(config, 'SPR_JSON_FILE', str(spr_file))

    spr_manager = SPRManager() # Uses patched config path
    return WorkflowEngine(spr_manager=spr_manager)

# Fixture for a simple valid workflow definition
@pytest.fixture
def simple_workflow_def() -> Dict:
    return {
    "name": "Simple Test Workflow",
    "description": "A basic workflow for testing.",
    "tasks": {
        "task_a": {
        "description": "First task",
        "action_type": "mock_action_a",
        "inputs": { "in_a": "{{initial_context.input_val}}" },
        "outputs": { "out_a": "string", "reflection": "dict"},
        "dependencies": []
        },
        "task_b": {
        "description": "Second task, depends on A",
        "action_type": "mock_action_b",
        "inputs": { "in_b": "{{task_a.out_a}}", "in_b_reflect_status": "{{task_a.reflection.status}}" },
        "outputs": { "out_b": "string", "reflection": "dict"},
        "dependencies": ["task_a"]
        },
        "task_c_conditional": {
            "description": "Conditional task based on A's reflection",
            "action_type": "mock_action_c",
            "inputs": {},
            "outputs": {"out_c": "string", "reflection": "dict"},
            "dependencies": ["task_a"],
            "condition": "{{ task_a.reflection.confidence > 0.8 }}"
        }
    },
    "start_tasks": ["task_a"] # Explicitly define start task(s) if needed by engine logic
    }

# Fixture to write workflow def to a file
@pytest.fixture
def simple_workflow_file(engine: WorkflowEngine, simple_workflow_def: Dict) -> str:
    """Writes the simple workflow definition to a file in the engine's dir."""
    if engine is None:
        pytest.skip("WorkflowEngine not initialized.")
    filepath = Path(engine.workflows_dir) / "simple_test.json"
    with open(filepath, 'w') as f:
        json.dump(simple_workflow_def, f)
    return "simple_test.json" # Return relative name

@pytest.mark.skipif(WorkflowEngine is None, reason="WorkflowEngine class not imported.")
def test_workflow_engine_load_valid(engine: WorkflowEngine, simple_workflow_file: str):
    """Test loading a valid workflow file."""
    workflow = engine.load_workflow(simple_workflow_file)
    assert workflow is not None
    assert workflow["name"] == "Simple Test Workflow"
    assert "task_a" in workflow["tasks"]

@pytest.mark.skipif(WorkflowEngine is None, reason="WorkflowEngine class not imported.")
def test_workflow_engine_load_invalid_path(engine: WorkflowEngine):
    """Test loading a non-existent workflow file."""
    with pytest.raises(FileNotFoundError):
        engine.load_workflow("non_existent_workflow.json")

@pytest.mark.skipif(WorkflowEngine is None, reason="WorkflowEngine class not imported.")
def test_workflow_engine_resolve_context(engine: WorkflowEngine):
    """Test resolving inputs using context, including IAR data."""
    context = {
        "initial_context": {"input_val": "initial"},
        "task_a": { # Simulate result of task_a including IAR
            "out_a": "output_from_a",
            "some_other_key": 123,
            "reflection": {
                "status": "Success", "summary": "Task A done",
                "confidence": 0.95, "alignment_check": "Aligned",
                "potential_issues": None, "raw_output_preview": "output..."
            }
        },
        "workflow_run_id": "test_run_123"
    }
    inputs_to_resolve = {
        "val1": "{{initial_context.input_val}}",
        "val2": "{{task_a.out_a}}",
        "val3_status": "{{task_a.reflection.status}}",
        "val4_confidence": "{{task_a.reflection.confidence}}",
        "val5_nonexistent": "{{task_a.reflection.non_key}}", # Test non-existent key
        "val6_run_id": "{{workflow_run_id}}"
    }
    resolved = engine._resolve_inputs(inputs_to_resolve, context)
    assert resolved["val1"] == "initial"
    assert resolved["val2"] == "output_from_a"
    assert resolved["val3_status"] == "Success"
    assert resolved["val4_confidence"] == 0.95
    assert resolved["val5_nonexistent"] is None # Non-existent keys resolve to None
    assert resolved["val6_run_id"] == "test_run_123"

@pytest.mark.skipif(WorkflowEngine is None, reason="WorkflowEngine class not imported.")
def test_workflow_engine_evaluate_condition_iar(engine: WorkflowEngine):
    """Test evaluating conditions based on IAR data."""
    context = {
        "task_a": {"reflection": {"confidence": 0.9, "status": "Success", "potential_issues": ["Minor issue"]}},
        "task_b": {"reflection": {"confidence": 0.5, "status": "Failure"}}
    }
    assert engine._evaluate_condition("{{ task_a.reflection.confidence > 0.8 }}", context) is True
    assert engine._evaluate_condition("{{ task_a.reflection.confidence < 0.8 }}", context) is False
    assert engine._evaluate_condition("{{ task_b.reflection.confidence <= 0.5 }}", context) is True
    assert engine._evaluate_condition("{{ task_a.reflection.status == 'Success' }}", context) is True
    assert engine._evaluate_condition("{{ task_b.reflection.status != 'Success' }}", context) is True
    # Adjusted condition string format for 'in' check
    assert engine._evaluate_condition("'Minor issue' in task_a.reflection.potential_issues", context) is True
    assert engine._evaluate_condition("'Critical issue' not in task_a.reflection.potential_issues", context) is True
    assert engine._evaluate_condition("task_b.reflection.confidence * 2 == 1.0", context) is True # Math expression

# Mock the execute_action function from action_registry
MOCK_REFLECTION_SUCCESS = {
    "status": "Success", "summary": "Mocked action successful.", "confidence": 0.9,
    "alignment_check": "Aligned", "potential_issues": None, "raw_output_preview": "mock output"
}
MOCK_REFLECTION_LOW_CONF = {
    "status": "Success", "summary": "Mocked action successful but low confidence.", "confidence": 0.4,
    "alignment_check": "Aligned", "potential_issues": ["Uncertainty in result."], "raw_output_preview": "mock output low conf"
}

# Determine the correct path for patching execute_action based on imports
if WorkflowEngine: # Only try to patch if WorkflowEngine was imported
    try:
        # Attempt standard import path structure
        patch_target = 'ResonantiA.ArchE.workflow_engine.execute_action'
        # Check if execute_action exists there before patching
        from ResonantiA.ArchE.workflow_engine import execute_action
    except (ImportError, AttributeError):
        try:
            # Attempt relative import path structure
            patch_target = '...ArchE.workflow_engine.execute_action'
            from ...ArchE.workflow_engine import execute_action
        except (ImportError, AttributeError):
            try:
                # Attempt direct import path structure
                patch_target = 'ArchE.workflow_engine.execute_action'
                from ArchE.workflow_engine import execute_action
            except (ImportError, AttributeError):
                 try:
                     # Attempt parent import path structure
                     patch_target = '..ArchE.workflow_engine.execute_action'
                     from ..ArchE.workflow_engine import execute_action
                 except (ImportError, AttributeError):
                      patch_target = None # Could not determine patch target
                      print(f"Warning: Could not determine correct patch target for execute_action in workflow_engine.")
else:
    patch_target = None # Cannot patch if WorkflowEngine wasn't imported

# Conditionally apply the patch decorator
if patch_target:
    workflow_run_patch = patch(patch_target)
else:
    # Create a dummy decorator if patching isn't possible
    def workflow_run_patch(func):
        @pytest.mark.skip(reason="Could not patch execute_action, skipping workflow run test.")
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

@pytest.mark.skipif(WorkflowEngine is None, reason="WorkflowEngine class not imported.")
@workflow_run_patch
def test_workflow_engine_run_simple_workflow(mock_execute_action: MagicMock, engine: WorkflowEngine, simple_workflow_file: str):
    """Test running a simple workflow with mocked actions and checking context/IAR."""
    # Configure mock return values for each action type
    def side_effect(action_type, inputs, context): # Add context argument
        if action_type == "mock_action_a":
            return {"out_a": f"output_a_for_{inputs.get('in_a')}", "reflection": MOCK_REFLECTION_LOW_CONF} # Task A returns low confidence
        elif action_type == "mock_action_b":
            # Check if inputs from task_a were resolved correctly
            assert inputs.get('in_b') == "output_a_for_initial"
            assert inputs.get('in_b_reflect_status') == "Success" # Status was success, even if conf was low
            return {"out_b": f"output_b_using_{inputs.get('in_b')}", "reflection": MOCK_REFLECTION_SUCCESS}
        elif action_type == "mock_action_c":
            # This action should be skipped because task_a confidence (0.4) is not > 0.8
            pytest.fail("Mock Action C should not have been called due to condition.")
            # return {"out_c": "output_c", "reflection": MOCK_REFLECTION_SUCCESS} # This line should not be reached
        else:
            return {"error": f"Unknown mock action type: {action_type}", "reflection": {"status":"Failure"}}

    if mock_execute_action is None: # If patch failed
         pytest.skip("execute_action patch failed.")

    mock_execute_action.side_effect = side_effect

    initial_context = {"input_val": "initial"}
    final_results = engine.run_workflow(simple_workflow_file, initial_context)

    # Assertions on final state
    assert final_results["workflow_status"] == "Completed Successfully"
    assert "task_a" in final_results
    assert final_results["task_a"]["out_a"] == "output_a_for_initial"
    assert final_results["task_a"]["reflection"]["confidence"] == 0.4 # Check IAR stored

    assert "task_b" in final_results
    assert final_results["task_b"]["out_b"] == "output_b_using_output_a_for_initial"
    assert final_results["task_b"]["reflection"]["status"] == "Success" # Check IAR stored

    assert "task_c_conditional" in final_results # Task exists in results
    assert "task_statuses" in final_results
    assert final_results["task_statuses"].get("task_c_conditional") == "skipped" # Check status map
    assert final_results["task_c_conditional"].get("status") == "skipped" # Check result dict
    assert final_results["task_c_conditional"].get("reflection", {}).get("status") == "Skipped" # Check IAR for skipped

    # Check that mock_action_a and mock_action_b were called once
    assert mock_execute_action.call_count == 2
    # Note: execute_action is called with context, so adjust assertion
    mock_execute_action.assert_any_call("mock_action_a", {"in_a": "initial"}, final_results) # Context passed
    mock_execute_action.assert_any_call("mock_action_b", {"in_b": "output_a_for_initial", "in_b_reflect_status": "Success"}, final_results) # Context passed

# --- END OF FILE tests/integration/test_workflow_engine_integration.py --- 