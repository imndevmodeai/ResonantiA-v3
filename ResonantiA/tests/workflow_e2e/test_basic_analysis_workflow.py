# --- START OF FILE tests/workflow_e2e/test_basic_analysis_workflow.py ---
import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict # Import Dict
from functools import wraps

# Attempt to import necessary modules with error handling
try:
    from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
    from Three_PointO_ArchE.spr_manager import SPRManager
    from Three_PointO_ArchE import config
    # Specific tool functions to patch
    from Three_PointO_ArchE.tools import run_search, invoke_llm, display_output
    from Three_PointO_ArchE.code_executor import execute_code
except ImportError:
    try:
        from ...ArchE.workflow_engine import IARCompliantWorkflowEngine
        from ...ArchE.spr_manager import SPRManager
        from ...ArchE import config
        from ...ArchE.tools import run_search, invoke_llm, display_output
        from ...ArchE.code_executor import execute_code
    except ImportError:
        try:
            from ArchE.workflow_engine import IARCompliantWorkflowEngine
            from ArchE.spr_manager import SPRManager
            from ArchE import config
            from ArchE.tools import run_search, invoke_llm, display_output
            from ArchE.code_executor import execute_code
        except ImportError:
            try:
                from ..ArchE.workflow_engine import IARCompliantWorkflowEngine
                from ..ArchE.spr_manager import SPRManager
                from ..ArchE import config
                from ..ArchE.tools import run_search, invoke_llm, display_output
                from ..ArchE.code_executor import execute_code
            except ImportError:
                print("Failed to import IARCompliantWorkflowEngine, SPRManager, config or tool functions. Ensure PYTHONPATH is set or tests run correctly.")
                IARCompliantWorkflowEngine, SPRManager, config = None, None, None
                run_search, invoke_llm, execute_code, display_output = None, None, None, None


# Fixture for engine, similar to integration test but potentially using real config paths
@pytest.fixture
def e2e_engine(tmp_path: Path, monkeypatch) -> IARCompliantWorkflowEngine:
    """Provides engine configured for E2E tests (might use actual config paths)."""
    if not all([IARCompliantWorkflowEngine, SPRManager, config]):
        pytest.skip("Required modules (IARCompliantWorkflowEngine, SPRManager, config) not imported.")

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
    return IARCompliantWorkflowEngine(spr_manager=spr_manager)

# Mock data for successful tool calls with IAR reflection
MOCK_REFLECTION_SUCCESS = {"status": "Success", "summary": "Mocked tool executed successfully.", "confidence": 0.95, "alignment_check": "Aligned", "potential_issues": None, "raw_output_preview": "Mock success"}
MOCK_REFLECTION_SEARCH = {"status": "Success", "summary": "Search successful.", "confidence": 0.9, "alignment_check": "Aligned", "potential_issues": None, "raw_output_preview": "Search results preview"}

MOCK_SEARCH_RESULTS = [{"title": "Mock Result 1", "url": "http://mock.com/1", "snippet": "Mock snippet 1"}]
MOCK_LLM_SUMMARY = "This is a mock LLM summary of the search results."

# This test will use mocker fixture for patching directly
@pytest.mark.skipif(IARCompliantWorkflowEngine is None or config is None, reason="IARCompliantWorkflowEngine or config not imported.")
def test_basic_analysis_workflow_e2e(e2e_engine: IARCompliantWorkflowEngine, mocker):
    """
    Runs the basic_analysis.json workflow end-to-end with mocked external calls.
    Verifies final status and presence of key results and IAR data.
    """
    # Mock the individual tool functions that would be called via ActionRegistry
    mock_display = mocker.patch('ResonantiA.ArchE.tools.display_output', return_value={"status": "Displayed", "reflection": MOCK_REFLECTION_SUCCESS})
    mock_search = mocker.patch('ResonantiA.ArchE.tools.run_search', return_value={"results": MOCK_SEARCH_RESULTS, "error": None, "provider_used": "mock", "reflection": MOCK_REFLECTION_SEARCH})
    
    # Mock get_llm_provider from llm_providers.py (imported by tools.py)
    # to prevent real API key checks and client instantiation.
    mock_get_client_cached = mocker.patch('ResonantiA.ArchE.tools._get_llm_provider_client_cached', return_value=("mock_client_instance", "mock_provider_name_from_cache", MagicMock())) # return (client, provider_name, cfg_to_monitor)
    mock_llm_provider_getter = mocker.patch('ResonantiA.ArchE.llm_providers.get_llm_provider', return_value={"client": "mock_client_instance", "provider_name": "mock_provider"} )
    mock_llm = mocker.patch('ResonantiA.ArchE.tools.invoke_llm', return_value={"response_text": MOCK_LLM_SUMMARY, "error": None, "provider_used": "mock", "model_used": "mock_model", "reflection": MOCK_REFLECTION_SUCCESS})
    mock_execute = mocker.patch('ResonantiA.ArchE.code_executor.execute_code', return_value={"stdout": "Formatted Mock Report...", "stderr": "", "exit_code": 0, "error": None, "sandbox_method_used": "mock", "reflection": MOCK_REFLECTION_SUCCESS})

    workflow_file = "basic_analysis.json" 
    workflow_path = Path(config.WORKFLOW_DIR) / workflow_file
    if not workflow_path.is_file():
         pytest.skip(f"Workflow file not found: {workflow_path}")

    initial_context = {"user_query": "Test Query for basic analysis"}

    # Run the workflow
    final_results = e2e_engine.run_workflow(workflow_file, initial_context)

    assert final_results is not None, "Workflow execution returned None"
    assert final_results.get("workflow_status") == "Completed Successfully", \
        f"Workflow did not complete successfully. Status: {final_results.get('workflow_status')}. Errors: {final_results.get('errors')}"

    # Verify IAR reflection is present and indicates success
    workflow_iar = final_results.get('reflection')
    assert workflow_iar is not None, "Workflow IAR (reflection) is missing"
    assert workflow_iar.get('status') == "Success", f"Workflow IAR status is not Success: {workflow_iar}"

    # Check if key tasks were called (via their mocks)
    mock_display.assert_called()
    mock_search.assert_called_with(query="Test Query for basic analysis", num_results=3)
    mock_llm.assert_called()
    mock_execute.assert_called()

    # Check for specific data in the final context or step results if applicable
    # This depends on the 'basic_analysis.json' workflow structure
    # Example: Check if LLM summary is in the context or a step output
    assert "final_report_content" in final_results.get("final_context", {}), "Final report content not in final context"
    assert MOCK_LLM_SUMMARY in final_results["final_context"]["final_report_content"], "LLM summary missing from final report"

# --- END OF FILE tests/workflow_e2e/test_basic_analysis_workflow.py --- 