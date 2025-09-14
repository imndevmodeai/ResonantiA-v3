"""
Tests for the workflow chaining functionality
"""
import unittest
import asyncio
from typing import Dict, Any
from Three_PointO_ArchE.workflow_chaining_engine import WorkflowChainingEngine
from Three_PointO_ArchE.iar_components import IARValidator, ResonanceTracker

class TestWorkflowChaining(unittest.TestCase):
    """Test cases for workflow chaining functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = WorkflowChainingEngine()
        self.validator = IARValidator()
        self.resonance_tracker = ResonanceTracker()
    
    def test_workflow_initialization(self):
        """Test workflow initialization."""
        workflow = {
            "name": "Test Workflow",
            "description": "Test workflow for chaining",
            "version": "3.0",
            "tasks": {
                "task1": {
                    "description": "First task",
                    "action_type": "test_action",
                    "inputs": {"param": "value"},
                    "dependencies": []
                }
            }
        }
        
        # Test workflow validation
        self.assertTrue(self.engine._validate_workflow(workflow))
    
    def test_dependency_resolution(self):
        """Test dependency resolution in workflow."""
        workflow = {
            "name": "Dependency Test",
            "tasks": {
                "task1": {
                    "description": "First task",
                    "action_type": "test_action",
                    "inputs": {},
                    "dependencies": []
                },
                "task2": {
                    "description": "Second task",
                    "action_type": "test_action",
                    "inputs": {},
                    "dependencies": ["task1"]
                }
            }
        }
        
        # Build execution graph
        self.engine._build_execution_graph(workflow)
        
        # Test dependency check
        self.assertTrue(self.engine._check_dependencies("task1", set()))
        self.assertFalse(self.engine._check_dependencies("task2", set()))
        self.assertTrue(self.engine._check_dependencies("task2", {"task1"}))
    
    def test_input_resolution(self):
        """Test input resolution from context and results."""
        inputs = {
            "param1": "{{task1.result.value}}",
            "param2": "{{context.value}}",
            "param3": "static_value"
        }
        
        context = {"value": "context_value"}
        results = {
            "task1": {
                "result": {
                    "value": "result_value"
                }
            }
        }
        
        resolved = self.engine._resolve_inputs(inputs, context, results)
        
        self.assertEqual(resolved["param1"], "result_value")
        self.assertEqual(resolved["param2"], "context_value")
        self.assertEqual(resolved["param3"], "static_value")
    
    def test_condition_evaluation(self):
        """Test condition evaluation."""
        results = {
            "task1": {
                "result": {
                    "confidence": 0.9
                }
            }
        }
        
        condition = "{{task1.result.confidence}} > 0.8"
        self.assertTrue(self.engine._evaluate_condition(condition, results))
        
        condition = "{{task1.result.confidence}} < 0.8"
        self.assertFalse(self.engine._evaluate_condition(condition, results))
    
    def test_iar_validation(self):
        """Test IAR validation."""
        iar_data = {
            "status": "Success",
            "confidence": 0.9,
            "summary": "Test execution",
            "potential_issues": [],
            "alignment_check": {
                "alignment1": 0.9,
                "alignment2": 0.8
            }
        }
        
        is_valid, issues = self.validator.validate_structure(iar_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
        
        # Test invalid IAR
        invalid_iar = {
            "status": "Invalid",
            "confidence": 1.5
        }
        
        is_valid, issues = self.validator.validate_structure(invalid_iar)
        self.assertFalse(is_valid)
        self.assertTrue(len(issues) > 0)
    
    def test_resonance_tracking(self):
        """Test resonance tracking."""
        iar_data = {
            "status": "Success",
            "confidence": 0.9,
            "summary": "Test execution",
            "potential_issues": [],
            "alignment_check": {
                "alignment1": 0.9,
                "alignment2": 0.8
            }
        }
        
        context = {"test": "context"}
        
        # Record execution
        self.resonance_tracker.record_execution("task1", iar_data, context)
        
        # Test resonance trend
        trend = self.resonance_tracker.get_resonance_trend()
        self.assertEqual(len(trend), 1)
        self.assertTrue(0 <= trend[0] <= 1)
        
        # Test issue detection
        issues = self.resonance_tracker.detect_resonance_issues()
        self.assertEqual(len(issues), 0)
    
    async def test_parallel_processing(self):
        """Test parallel processing functionality."""
        workflow = {
            "name": "Parallel Test",
            "tasks": {
                "parallel_task": {
                    "description": "Parallel processing task",
                    "action_type": "perform_parallel_action",
                    "inputs": {
                        "tasks": [
                            {
                                "name": "task1",
                                "action": "test_action",
                                "data": {"param": "value1"}
                            },
                            {
                                "name": "task2",
                                "action": "test_action",
                                "data": {"param": "value2"}
                            }
                        ]
                    },
                    "dependencies": []
                }
            }
        }
        
        # Execute workflow
        results = await self.engine.execute_workflow(workflow)
        
        # Verify parallel results
        self.assertIn("parallel_task", results)
        parallel_results = results["parallel_task"]["parallel_results"]
        self.assertIn("task1", parallel_results)
        self.assertIn("task2", parallel_results)
    
    async def test_metacognitive_shift(self):
        """Test metacognitive shift functionality."""
        workflow = {
            "name": "Metacognitive Test",
            "tasks": {
                "shift_task": {
                    "description": "Metacognitive shift task",
                    "action_type": "perform_metacognitive_shift",
                    "inputs": {
                        "context": {"test": "context"},
                        "threshold": 0.7
                    },
                    "dependencies": []
                }
            }
        }
        
        # Execute workflow
        results = await self.engine.execute_workflow(workflow)
        
        # Verify shift results
        self.assertIn("shift_task", results)
        shift_result = results["shift_task"]["shift_result"]
        self.assertIsNotNone(shift_result)

if __name__ == '__main__':
    unittest.main() 