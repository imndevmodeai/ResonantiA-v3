# --- START OF FILE tests/workflow_e2e/test_basic_analysis_workflow.py ---
import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict # Import Dict

# Attempt to import necessary modules with error handling
try:
    from ResonantiA.ArchE.workflow_engine import WorkflowEngine
    from ResonantiA.ArchE.spr_manager import SPRManager
    from ResonantiA.ArchE import config
    # Specific tool functions to patch
    from ResonantiA.ArchE.tools import run_search, invoke_llm, display_output
    from ResonantiA.ArchE.code_executor import execute_code
except ImportError:
    try:
        from ...ArchE.workflow_engine import WorkflowEngine
        from ...ArchE.spr_manager import SPRManager
        from ...ArchE import config
        from ...ArchE.tools import run_search, invoke_llm, display_output
        from ...ArchE.code_executor import execute_code
    except ImportError:
        try:
            from ArchE.workflow_engine import WorkflowEngine
            from ArchE.spr_manager import SPRManager
            from ArchE import config
            from ArchE.tools import run_search, invoke_llm, display_output
            from ArchE.code_executor import execute_code
        except ImportError:
            try:
                from ..ArchE.workflow_engine import WorkflowEngine
                from ..ArchE.spr_manager import SPRManager
                from ..ArchE import config
                from ..ArchE.tools import run_search, invoke_llm, display_output
                from ..ArchE.code_executor import execute_code
            except ImportError:
                print("Failed to import WorkflowEngine, SPRManager, config or tool functions. Ensure PYTHONPATH is set or tests run correctly.")
                WorkflowEngine, SPRManager, config = None, None, None
                run_search, invoke_llm, execute_code, display_output = None, None, None, None


# Fixture for engine, similar to integration test but potentially using real config paths
@pytest.fixture
def e2e_engine(tmp_path: Path, monkeypatch) -> WorkflowEngine:
    """Provides engine configured for E2E tests (might use actual config paths)."""
    if not all([WorkflowEngine, SPRManager, config]):
        pytest.skip("Required modules (WorkflowEngine, SPRManager, config) not imported.")

    # For E2E, we might want to use the actual configured paths,
    # but ensure outputs/logs go to temp dir for cleanup.
    test_output_dir = tmp_path / "outputs"
    test_log_dir = tmp_path / "logs"
    test_output_dir.mkdir()
    test_log_dir.mkdir()
    test_log_file = test_log_dir / "e2e_test.log"

    # Patch output/log paths in config for the duration of the test
    # Use monkeypatch fixture from pytest
    monkeypatch.setattr(config, 'OUTPUT_DIR', str(test_output_dir))
    monkeypatch.setattr(config, 'LOG_DIR', str(test_log_dir))
    monkeypatch.setattr(config, 'LOG_FILE', str(test_log_file))

    # Assume config.WORKFLOW_DIR and config.SPR_JSON_FILE point to actual files
    # Ensure these actual files exist for E2E tests
    # Check if configured SPR file exists, otherwise skip
    spr_filepath = Path(config.SPR_JSON_FILE)
    if not spr_filepath.is_file():
        pytest.skip(f"SPR file not found at configured path: {spr_filepath}")

    spr_manager = SPRManager(config.SPR_JSON_FILE) # Use actual SPR file
    return WorkflowEngine(spr_manager=spr_manager)

# Define mock return values for external calls
MOCK_SEARCH_RESULTS = [{"title": "Mock Search Result", "link": "http://mock.com", "snippet": "This is a mock snippet."}]
MOCK_LLM_SUMMARY = "This is the mocked LLM summary of the search results."
MOCK_REFLECTION_SUCCESS = {
    "status": "Success", "summary": "Mocked action successful.", "confidence": 0.9,
    "alignment_check": "Aligned", "potential_issues": None, "raw_output_preview": "mock..."
}
MOCK_REFLECTION_SEARCH = {
    "status": "Success", "summary": "Simulated search completed.", "confidence": 0.6,
    "alignment_check": "Aligned", "potential_issues": ["Results are simulated."], "raw_output_preview": MOCK_SEARCH_RESULTS[0]['title'] if MOCK_SEARCH_RESULTS else ""
}

# Determine patch targets based on successful imports
patch_targets = {}
if run_search: patch_targets['run_search_patch'] = patch('ResonantiA.ArchE.tools.run_search')
if invoke_llm: patch_targets['invoke_llm_patch'] = patch('ResonantiA.ArchE.tools.invoke_llm')
if execute_code: patch_targets['execute_code_patch'] = patch('ResonantiA.ArchE.code_executor.execute_code')
if display_output: patch_targets['display_output_patch'] = patch('ResonantiA.ArchE.tools.display_output')

# Function to apply multiple patches - requires careful ordering in decorator stack
def apply_patches(func):
    wrapped = func
    # Apply patches in reverse order of definition for correct mock passing
    if 'display_output_patch' in patch_targets: wrapped = patch_targets['display_output_patch'](wrapped)
    if 'execute_code_patch' in patch_targets: wrapped = patch_targets['execute_code_patch'](wrapped)
    if 'invoke_llm_patch' in patch_targets: wrapped = patch_targets['invoke_llm_patch'](wrapped)
    if 'run_search_patch' in patch_targets: wrapped = patch_targets['run_search_patch'](wrapped)
    return wrapped

@pytest.mark.skipif(WorkflowEngine is None or config is None, reason="WorkflowEngine or config not imported.")
@apply_patches
def test_basic_analysis_workflow_e2e(
    mock_search: MagicMock = None, mock_llm: MagicMock = None, mock_execute: MagicMock = None, mock_display: MagicMock = None, # Mocks passed in order of patching (inner first)
    e2e_engine: WorkflowEngine = None):
    """
    Runs the basic_analysis.json workflow end-to-end with mocked external calls.
    Verifies final status and presence of key results and IAR data.
    """
    # Check if mocks were created (i.e., patching was successful)
    if not all ([mock_search, mock_llm, mock_execute, mock_display]):
         pytest.skip("One or more required tool functions could not be mocked.")

    # Configure mock return values (including IAR reflection)
    mock_display.return_value = {"status": "Displayed", "reflection": MOCK_REFLECTION_SUCCESS}
    mock_search.return_value = {"results": MOCK_SEARCH_RESULTS, "error": None, "provider_used": "mock", "reflection": MOCK_REFLECTION_SEARCH}
    mock_llm.return_value = {"response_text": MOCK_LLM_SUMMARY, "error": None, "provider_used": "mock", "model_used": "mock_model", "reflection": MOCK_REFLECTION_SUCCESS}
    # Mock the final execute_code step that formats the output
    mock_execute.return_value = {"stdout": "Formatted Mock Report...", "stderr": "", "exit_code": 0, "error": None, "sandbox_method_used": "mock", "reflection": MOCK_REFLECTION_SUCCESS}

    workflow_file = "basic_analysis.json" # Assumes this exists in configured WORKFLOW_DIR
    workflow_path = Path(config.WORKFLOW_DIR) / workflow_file
    if not workflow_path.is_file():
         pytest.skip(f"Workflow file not found: {workflow_path}")

    initial_context = {"user_query": "Test Query"}

    # Run the workflow
    final_results = e2e_engine.run_workflow(workflow_file, initial_context)

    # --- Assertions ---
    assert final_results is not None
    assert final_results.get("workflow_status") == "Completed Successfully"
    assert final_results.get("error") is None

    # Check if key tasks completed and their results/IAR are present
    assert final_results.get("task_statuses", {}).get("perform_search") == "completed"
    assert "perform_search" in final_results
    assert final_results["perform_search"]["results"] == MOCK_SEARCH_RESULTS
    assert "reflection" in final_results["perform_search"]
    assert final_results["perform_search"]["reflection"]["status"] == "Success"

    assert final_results.get("task_statuses", {}).get("summarize_results") == "completed"
    assert "summarize_results" in final_results
    assert final_results["summarize_results"]["response_text"] == MOCK_LLM_SUMMARY
    assert "reflection" in final_results["summarize_results"]
    assert final_results["summarize_results"]["reflection"]["confidence"] == 0.9 # Check specific IAR value

    # Assuming task name is 'format_and_display_summary' or similar based on workflow json
    display_task_name = "display_summary" # Use the actual task name from basic_analysis.json
    # Find the actual task name if necessary (e.g., based on action type)
    # TODO: Update display_task_name if different in basic_analysis.json
    found_display_task = False
    for task_id, task_details in final_results.get("task_statuses", {}).items():
        if task_details == "completed" and task_id in final_results and final_results[task_id].get("stdout") == "Formatted Mock Report...":
            display_task_name = task_id
            found_display_task = True
            break
    if not found_display_task:
        # Try finding based on action type if stdout check fails (mock might change)
         for task_id, task_info in e2e_engine.load_workflow(workflow_file)["tasks"].items():
             if task_info["action_type"] == "execute_code" or task_info["action_type"] == "display_output":
                 if final_results.get("task_statuses", {}).get(task_id) == "completed":
                     display_task_name = task_id
                     found_display_task = True
                     break

    assert found_display_task, f"Could not find completed display/execute task in results: {final_results.get('task_statuses')}"
    assert final_results.get("task_statuses", {}).get(display_task_name) == "completed"
    assert display_task_name in final_results
    assert final_results[display_task_name]["stdout"] == "Formatted Mock Report..."
    assert "reflection" in final_results[display_task_name]

    # Verify mocks were called
    mock_search.assert_called_once()
    mock_llm.assert_called_once()
    mock_execute.assert_called_once() # Assumes display uses execute_code
    # Check specific call arguments if needed
    search_call_args, _ = mock_search.call_args
    # Adjust if run_search input format is different (e.g., a single dict arg)
    assert search_call_args[0].get("query") == "Test Query"
    assert search_call_args[0].get("num_results", 5) == 5 # Check default or passed value

    # Check that the LLM prompt received the search results (or mock thereof)
    llm_call_args, _ = mock_llm.call_args
    # Adjust if invoke_llm input format is different
    prompt_input = llm_call_args[0].get('prompt', '') or llm_call_args[0].get('messages', '')
    assert "Test Query" in str(prompt_input)
    assert "Mock Search Result" in str(prompt_input)
    # Check if search IAR confidence was potentially resolved and passed
    # This depends heavily on how the workflow resolves and formats the prompt
    # assert "Confidence: 0.6" in str(prompt_input)

# --- END OF FILE tests/workflow_e2e/test_basic_analysis_workflow.py --- 