"""
Test harness for the Creative Synthesis Triptych workflow.

This test ensures that the creative_synthesis.json workflow functions correctly
and maintains compatibility with the IARCompliantWorkflowEngine.
"""

import pytest
import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.action_registry import ActionRegistry


class TestCreativeSynthesisWorkflow:
    """Test suite for the Creative Synthesis Triptych workflow."""
    
    @pytest.fixture
    def workflow_engine(self):
        """Initialize the IARCompliantWorkflowEngine with test configuration."""
        engine = IARCompliantWorkflowEngine()
        # Register the required action types
        registry = ActionRegistry()
        registry.register_action("generate_text_llm", self._mock_llm_action)
        engine.action_registry = registry
        return engine
    
    @pytest.fixture
    def sample_problem(self):
        """Sample problem with conflicting constraints for testing."""
        return {
            "problem_description": """
            A pharmaceutical company has developed a life-saving drug that costs $2 to manufacture 
            but could save thousands of lives. The company needs to price it to recoup R&D costs 
            ($500M) and fund future research, but must balance this against accessibility for 
            patients who cannot afford expensive treatments. Regulatory bodies require safety 
            testing that costs $100M, and insurance companies are pressuring for lower prices 
            while patient advocacy groups demand immediate access. How should the company proceed?
            """
        }
    
    def _mock_llm_action(self, prompt, **kwargs):
        """Mock LLM action for testing purposes."""
        # Simulate different response types based on prompt content
        if "logical" in prompt.lower():
            return {
                "status": "Success",
                "confidence": 0.9,
                "response_text": "Logical solution: Implement tiered pricing with government subsidies and insurance partnerships.",
                "metadata": {"approach": "analytical"}
            }
        elif "ethical" in prompt.lower():
            return {
                "status": "Success", 
                "confidence": 0.85,
                "response_text": "Ethical solution: Establish a not-for-profit foundation to distribute the drug at cost.",
                "metadata": {"approach": "humanitarian"}
            }
        elif "bizarre" in prompt.lower():
            return {
                "status": "Success",
                "confidence": 0.8,
                "response_text": "Bizarre solution: Create a blockchain-based 'life token' system where healthy people can donate their unused medical budget.",
                "metadata": {"approach": "innovative"}
            }
        else:
            return {
                "status": "Success",
                "confidence": 0.9,
                "response_text": "Synthesis: The three approaches can be combined into a hybrid model.",
                "metadata": {"approach": "synthetic"}
            }
    
    def test_workflow_file_exists(self):
        """Test that the workflow file exists and is valid JSON."""
        workflow_path = project_root / "workflows" / "system" / "creative_synthesis.json"
        assert workflow_path.exists(), f"Workflow file not found at {workflow_path}"
        
        with open(workflow_path, 'r') as f:
            workflow_data = json.load(f)
        
        # Validate basic structure
        assert "name" in workflow_data
        assert "description" in workflow_data
        assert "version" in workflow_data
        assert "tasks" in workflow_data
        assert workflow_data["name"] == "Creative Synthesis Triptych"
    
    def test_workflow_execution(self, workflow_engine, sample_problem):
        """Test that the workflow executes successfully with valid input."""
        workflow_path = project_root / "workflows" / "system" / "creative_synthesis.json"
        
        # Execute the workflow
        result = workflow_engine.run_workflow(
            str(workflow_path),
            sample_problem
        )
        
        # Validate execution success
        assert result["status"] == "Success", f"Workflow execution failed: {result.get('error', 'Unknown error')}"
        
        # Validate that all tasks completed
        task_results = result.get("task_results", {})
        expected_tasks = [
            "generate_logical_solution",
            "generate_ethical_solution", 
            "generate_bizarre_solution",
            "synthesize_triptych"
        ]
        
        for task_name in expected_tasks:
            assert task_name in task_results, f"Task {task_name} not found in results"
            task_result = task_results[task_name]
            assert task_result["status"] == "Success", f"Task {task_name} failed: {task_result.get('error', 'Unknown error')}"
    
    def test_final_output_quality(self, workflow_engine, sample_problem):
        """Test that the final synthesize_triptych output meets quality standards."""
        workflow_path = project_root / "workflows" / "system" / "creative_synthesis.json"
        
        result = workflow_engine.run_workflow(
            str(workflow_path),
            sample_problem
        )
        
        # Get the final synthesis output
        final_task = result["task_results"]["synthesize_triptych"]
        final_output = final_task["response_text"]
        
        # Validate output quality
        assert final_output is not None, "Final output is None"
        assert len(final_output.strip()) > 0, "Final output is empty"
        assert len(final_output) > 100, "Final output is too short for meaningful synthesis"
        
        # Validate IAR compliance
        assert final_task["status"] == "Success"
        assert final_task["confidence"] > 0.8, f"Confidence too low: {final_task['confidence']}"
    
    def test_workflow_dependencies(self, workflow_engine, sample_problem):
        """Test that task dependencies are properly enforced."""
        workflow_path = project_root / "workflows" / "system" / "creative_synthesis.json"
        
        result = workflow_engine.run_workflow(
            str(workflow_path),
            sample_problem
        )
        
        task_results = result["task_results"]
        
        # Verify that individual solution tasks completed before synthesis
        synthesis_task = task_results["synthesize_triptych"]
        assert synthesis_task["status"] == "Success"
        
        # Verify that synthesis task has access to all three solution outputs
        synthesis_inputs = synthesis_task.get("inputs", {})
        assert "generate_logical_solution.response_text" in synthesis_inputs
        assert "generate_ethical_solution.response_text" in synthesis_inputs  
        assert "generate_bizarre_solution.response_text" in synthesis_inputs
    
    def test_error_handling(self, workflow_engine):
        """Test that the workflow handles invalid input gracefully."""
        workflow_path = project_root / "workflows" / "system" / "creative_synthesis.json"
        
        # Test with missing problem description
        invalid_context = {}
        
        result = workflow_engine.run_workflow(
            str(workflow_path),
            invalid_context
        )
        
        # Should handle gracefully, not crash
        assert "status" in result
        # May fail due to missing input, but should provide meaningful error


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"]) 