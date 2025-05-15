# --- START OF FILE tests/integration/test_iar_validation.py ---
import pytest
from unittest.mock import patch, MagicMock
from typing import Dict # Import Dict

# Attempt to import necessary modules with error handling
try:
    from ResonantiA.ArchE.action_registry import execute_action, register_action, ACTION_REGISTRY
    from ResonantiA.ArchE.tools import _create_reflection # Import helper for creating valid reflections
except ImportError:
    try:
        from ...ArchE.action_registry import execute_action, register_action, ACTION_REGISTRY
        from ...ArchE.tools import _create_reflection
    except ImportError:
        try:
            from ArchE.action_registry import execute_action, register_action, ACTION_REGISTRY
            from ArchE.tools import _create_reflection
        except ImportError:
            try:
                from ..ArchE.action_registry import execute_action, register_action, ACTION_REGISTRY
                from ..ArchE.tools import _create_reflection
            except ImportError:
                print("Failed to import action_registry or _create_reflection. Ensure PYTHONPATH is set or tests run correctly relative to the project structure.")
                execute_action, register_action, ACTION_REGISTRY, _create_reflection = None, None, None, None

# --- Mock Action Functions for Testing IAR Validation ---

@pytest.mark.skipif(_create_reflection is None, reason="_create_reflection helper not imported.")
def mock_action_returns_correct_iar(inputs: Dict) -> Dict:
    """Simulates an action that correctly returns primary result + IAR reflection."""
    primary = {"data": "some result", "value": 123}
    reflection = _create_reflection("Success", "Action completed fine.", 0.9, "Aligned", None, primary)
    return {**primary, "reflection": reflection}

def mock_action_returns_no_reflection(inputs: Dict) -> Dict:
    """Simulates an action that forgets the reflection key."""
    return {"data": "result without reflection"}

def mock_action_returns_non_dict(inputs: Dict) -> str:
    """Simulates an action that returns the wrong type."""
    return "just a string"

def mock_action_returns_bad_reflection_type(inputs: Dict) -> Dict:
    """Simulates an action with a non-dict reflection."""
    return {"data": "result", "reflection": "this is not a dict"}

@pytest.mark.skipif(_create_reflection is None, reason="_create_reflection helper not imported.")
def mock_action_returns_error_with_reflection(inputs: Dict) -> Dict:
    """Simulates an action returning an error correctly with IAR."""
    error_msg = "Something went wrong internally."
    reflection = _create_reflection("Failure", error_msg, 0.1, "Failed", [error_msg], None)
    return {"error": error_msg, "reflection": reflection}

# --- Test Setup ---
# Register mock actions before tests run
@pytest.fixture(autouse=True)
def register_mock_actions_fixture():
    """Fixture to register/unregister mock actions for tests in this module."""
    if not all([register_action, ACTION_REGISTRY]):
        pytest.skip("Action registry components not imported.")

    actions_to_register = {
        "correct_iar": mock_action_returns_correct_iar,
        "no_reflection": mock_action_returns_no_reflection,
        "non_dict_return": mock_action_returns_non_dict,
        "bad_reflection_type": mock_action_returns_bad_reflection_type,
        "error_with_reflection": mock_action_returns_error_with_reflection,
    }
    original_registry = ACTION_REGISTRY.copy() # Backup original
    for name, func in actions_to_register.items():
        # Check if function exists before registering (handles skipped functions)
        if callable(func):
             register_action(name, func, force=True) # Use force=True in tests is okay
    yield # Run the tests
    # Teardown: Restore original registry
    ACTION_REGISTRY.clear()
    ACTION_REGISTRY.update(original_registry)

# --- Tests for execute_action's IAR Validation ---

@pytest.mark.skipif(execute_action is None, reason="execute_action not imported.")
def test_execute_action_correct_iar():
    """Test execute_action with a function returning correct IAR format."""
    # Check if the mock function itself was skipped
    if not callable(mock_action_returns_correct_iar):
        pytest.skip("Dependent mock function was skipped.")

    result = execute_action("correct_iar", {})
    assert isinstance(result, dict)
    assert "reflection" in result
    assert isinstance(result["reflection"], dict)
    assert result["reflection"]["status"] == "Success"
    assert result.get("error") is None
    assert result["data"] == "some result"

@pytest.mark.skipif(execute_action is None, reason="execute_action not imported.")
def test_execute_action_no_reflection():
    """Test execute_action when action returns dict without reflection key."""
    result = execute_action("no_reflection", {})
    assert isinstance(result, dict)
    assert "reflection" in result # execute_action should add a default error reflection
    assert isinstance(result["reflection"], dict)
    assert result["reflection"]["status"] == "Failure" # Status should indicate failure due to missing reflection
    assert result["reflection"]["summary"] == "Action implementation error: Missing 'reflection' key."
    assert "Action needs code update" in result["reflection"]["potential_issues"][0]
    assert result.get("error") is not None # Error should be added
    assert result["data"] == "result without reflection" # Original data preserved

@pytest.mark.skipif(execute_action is None, reason="execute_action not imported.")
def test_execute_action_non_dict_return():
    """Test execute_action when action returns a non-dictionary type."""
    result = execute_action("non_dict_return", {})
    assert isinstance(result, dict) # execute_action should wrap it in a dict
    assert "reflection" in result
    assert isinstance(result["reflection"], dict)
    assert result["reflection"]["status"] == "Failure"
    assert result["reflection"]["summary"] == "Action implementation error: Returned non-dict."
    assert "Action needs code update" in result["reflection"]["potential_issues"][0]
    assert result.get("error") is not None
    assert result["original_result"] == "just a string" # Original result included

@pytest.mark.skipif(execute_action is None, reason="execute_action not imported.")
def test_execute_action_bad_reflection_type():
    """Test execute_action when action returns 'reflection' but it's not a dict."""
    result = execute_action("bad_reflection_type", {})
    assert isinstance(result, dict)
    assert "reflection" in result
    assert isinstance(result["reflection"], dict) # execute_action replaces the bad one
    assert result["reflection"]["status"] == "Failure"
    assert result["reflection"]["summary"] == "Action implementation error: Invalid 'reflection' format (not a dict)."
    assert "Action needs code update" in result["reflection"]["potential_issues"][0]
    assert result.get("error") is not None
    assert result["data"] == "result" # Original data preserved

@pytest.mark.skipif(execute_action is None, reason="execute_action not imported.")
def test_execute_action_error_with_reflection():
    """Test execute_action when action correctly returns an error and reflection."""
    # Check if the mock function itself was skipped
    if not callable(mock_action_returns_error_with_reflection):
        pytest.skip("Dependent mock function was skipped.")

    result = execute_action("error_with_reflection", {})
    assert isinstance(result, dict)
    assert "reflection" in result
    assert isinstance(result["reflection"], dict)
    assert result["reflection"]["status"] == "Failure"
    assert result.get("error") == "Something went wrong internally."
    # execute_action should pass through the valid reflection provided by the action
    assert result["reflection"]["summary"] == "Something went wrong internally."

# --- END OF FILE tests/integration/test_iar_validation.py --- 