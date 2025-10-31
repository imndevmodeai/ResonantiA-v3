# ResonantiA Protocol v3.5-GP - Enhanced Components Test Suite
# Comprehensive testing for sandbox environment

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

# Add sandbox to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.enhanced_workflow_engine import (
    EnhancedIARValidator, 
    EnhancedResonanceTracker, 
    EnhancedWorkflowEngine,
    validate_sandbox_environment,
    create_sandbox_workflow_engine
)


class TestEnhancedIARValidator(unittest.TestCase):
    """Test enhanced IAR validation capabilities"""
    
    def setUp(self):
        self.validator = EnhancedIARValidator()
    
    def test_standard_iar_validation(self):
        """Test standard IAR validation still works"""
        valid_iar = {
            'status': 'Success',
            'summary': 'Task completed successfully',
            'confidence': 0.95,
            'alignment_check': True,
            'potential_issues': [],
            'raw_output_preview': 'Output preview'
        }
        
        is_valid, issues = self.validator.validate_structure(valid_iar)
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
    
    def test_enhanced_iar_validation(self):
        """Test enhanced IAR validation with v3.5-GP fields"""
        enhanced_iar = {
            'status': 'Success',
            'summary': 'Task completed successfully',
            'confidence': 0.95,
            'alignment_check': True,
            'potential_issues': [],
            'raw_output_preview': 'Output preview',
            'genesis_protocol_compliance': {
                'objective_clarity': 0.90,
                'implementation_resonance': 0.95,
                'overall_score': 0.925
            },
            'resonant_corrective_loop': {
                'iterations': 3,
                'correction_time': 25
            },
            'autonomous_orchestration_score': 0.92
        }
        
        is_valid, issues = self.validator.validate_enhanced_structure(enhanced_iar)
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
    
    def test_enhanced_iar_validation_failures(self):
        """Test enhanced IAR validation with missing components"""
        incomplete_iar = {
            'status': 'Success',
            'summary': 'Task completed successfully',
            'confidence': 0.95,
            'alignment_check': True,
            'potential_issues': [],
            'raw_output_preview': 'Output preview',
            'genesis_protocol_compliance': {
                'objective_clarity': 0.90
                # Missing 'implementation_resonance'
            }
        }
        
        is_valid, issues = self.validator.validate_enhanced_structure(incomplete_iar)
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertIn('Missing required component', str(issues))


class TestEnhancedResonanceTracker(unittest.TestCase):
    """Test enhanced resonance tracking capabilities"""
    
    def setUp(self):
        self.tracker = EnhancedResonanceTracker()
    
    def test_enhanced_execution_recording(self):
        """Test enhanced execution recording"""
        task_id = "test_task"
        iar_data = {
            'status': 'Success',
            'confidence': 0.95,
            'tactical_resonance': 0.90,
            'crystallization_potential': 0.85,
            'genesis_protocol_compliance': {
                'overall_score': 0.92
            },
            'autonomous_orchestration_score': 0.88
        }
        context = {}
        
        record = self.tracker.record_enhanced_execution(task_id, iar_data, context)
        
        self.assertEqual(record['task_id'], task_id)
        self.assertEqual(record['status'], 'Success')
        self.assertEqual(record['confidence'], 0.95)
        self.assertEqual(record['genesis_protocol_compliance']['overall_score'], 0.92)
        self.assertEqual(record['autonomous_orchestration_score'], 0.88)
    
    def test_enhanced_metrics_calculation(self):
        """Test enhanced metrics calculation"""
        # Record multiple executions
        for i in range(5):
            iar_data = {
                'status': 'Success',
                'confidence': 0.90 + (i * 0.01),
                'tactical_resonance': 0.85 + (i * 0.02),
                'crystallization_potential': 0.80 + (i * 0.03),
                'genesis_protocol_compliance': {
                    'overall_score': 0.88 + (i * 0.02)
                },
                'autonomous_orchestration_score': 0.82 + (i * 0.03)
            }
            self.tracker.record_enhanced_execution(f"task_{i}", iar_data, {})
        
        # Check enhanced metrics
        self.assertGreater(self.tracker.resonance_metrics['avg_genesis_protocol_compliance'], 0.0)
        self.assertGreater(self.tracker.resonance_metrics['avg_autonomous_orchestration_score'], 0.0)
        self.assertIn('genesis_protocol_status', self.tracker.resonance_metrics)
        self.assertIn('resonant_corrective_loop_status', self.tracker.resonance_metrics)
        self.assertIn('autonomous_orchestration_status', self.tracker.resonance_metrics)
    
    def test_enhanced_resonance_report(self):
        """Test enhanced resonance report generation"""
        # Record some executions
        for i in range(3):
            iar_data = {
                'status': 'Success',
                'confidence': 0.90,
                'tactical_resonance': 0.85,
                'crystallization_potential': 0.80,
                'genesis_protocol_compliance': {
                    'overall_score': 0.88
                },
                'autonomous_orchestration_score': 0.82
            }
            self.tracker.record_enhanced_execution(f"task_{i}", iar_data, {})
        
        report = self.tracker.get_enhanced_resonance_report()
        
        # Check report structure
        self.assertIn('current_metrics', report)
        self.assertIn('genesis_protocol_status', report)
        self.assertIn('resonant_corrective_loop_status', report)
        self.assertIn('autonomous_orchestration_status', report)
        self.assertIn('enhanced_compliance_score', report)
        
        # Check status values
        self.assertIn(report['genesis_protocol_status'], ['excellent', 'good', 'needs_improvement', 'critical', 'no_data'])
        self.assertIn(report['autonomous_orchestration_status'], ['highly_autonomous', 'moderately_autonomous', 'limited_autonomy', 'manual_intervention_required', 'no_data'])


class TestEnhancedWorkflowEngine(unittest.TestCase):
    """Test enhanced workflow engine capabilities"""
    
    def setUp(self):
        self.engine = EnhancedWorkflowEngine()
    
    def test_enhanced_context_enhancement(self):
        """Test context enhancement for v3.5-GP"""
        original_context = {
            'user_query': 'Test query',
            'session_id': 'test_session'
        }
        
        enhanced_context = self.engine._enhance_context_for_v35(original_context)
        
        # Check original context preserved
        self.assertEqual(enhanced_context['user_query'], 'Test query')
        self.assertEqual(enhanced_context['session_id'], 'test_session')
        
        # Check v3.5-GP enhancements added
        self.assertIn('genesis_protocol', enhanced_context)
        self.assertIn('resonant_corrective_loop', enhanced_context)
        self.assertIn('autonomous_orchestration', enhanced_context)
        
        # Check Genesis Protocol structure
        self.assertEqual(enhanced_context['genesis_protocol']['version'], '3.5-GP')
        self.assertTrue(enhanced_context['genesis_protocol']['enabled'])
        self.assertEqual(enhanced_context['genesis_protocol']['objective_clarity_target'], 0.85)
    
    def test_enhanced_result_enhancement(self):
        """Test result enhancement for v3.5-GP"""
        original_result = {
            'workflow_name': 'test_workflow',
            'workflow_status': 'Completed Successfully',
            'task_statuses': {'task1': 'completed'}
        }
        
        enhanced_result = self.engine._enhance_result_for_v35(original_result)
        
        # Check original result preserved
        self.assertEqual(enhanced_result['workflow_name'], 'test_workflow')
        self.assertEqual(enhanced_result['workflow_status'], 'Completed Successfully')
        
        # Check v3.5-GP enhancements added
        self.assertIn('enhanced_resonance_report', enhanced_result)
        self.assertIn('v35_status', enhanced_result)
        
        # Check v3.5-GP status structure
        v35_status = enhanced_result['v35_status']
        self.assertTrue(v35_status['genesis_protocol_enabled'])
        self.assertTrue(v35_status['resonant_corrective_loop_enabled'])
        self.assertTrue(v35_status['autonomous_orchestration_enabled'])
        self.assertTrue(v35_status['sandbox_mode'])
    
    def test_enhanced_dashboard(self):
        """Test enhanced dashboard generation"""
        dashboard = self.engine.get_enhanced_dashboard()
        
        # Check base dashboard components
        self.assertIn('run_id', dashboard)
        self.assertIn('workflow', dashboard)
        self.assertIn('resonance_report', dashboard)
        
        # Check enhanced components
        self.assertIn('enhanced_resonance_report', dashboard)
        self.assertIn('v35_features', dashboard)
        
        # Check v3.5-GP features
        v35_features = dashboard['v35_features']
        self.assertTrue(v35_features['genesis_protocol'])
        self.assertTrue(v35_features['resonant_corrective_loop'])
        self.assertTrue(v35_features['autonomous_orchestration'])


class TestSandboxEnvironment(unittest.TestCase):
    """Test sandbox environment validation"""
    
    def test_sandbox_validation(self):
        """Test sandbox environment validation"""
        validation = validate_sandbox_environment()
        
        self.assertIn('sandbox_mode', validation)
        self.assertIn('production_isolation', validation)
        self.assertIn('enhanced_components', validation)
        self.assertIn('validation_tests', validation)
        
        # Check sandbox mode is enabled
        self.assertTrue(validation['sandbox_mode'])
    
    def test_sandbox_engine_creation(self):
        """Test sandbox engine creation"""
        engine = create_sandbox_workflow_engine()
        
        self.assertIsInstance(engine, EnhancedWorkflowEngine)
        self.assertTrue(engine.genesis_protocol_enabled)
        self.assertTrue(engine.resonant_corrective_loop_enabled)
        self.assertTrue(engine.autonomous_orchestration_enabled)


class TestIntegration(unittest.TestCase):
    """Test integration between enhanced components"""
    
    def test_full_workflow_simulation(self):
        """Test full workflow simulation with enhanced components"""
        engine = create_sandbox_workflow_engine()
        
        # Simulate workflow execution
        initial_context = {
            'user_query': 'Test enhanced workflow',
            'session_id': 'test_session'
        }
        
        # Mock workflow execution (since we don't have actual workflows in sandbox)
        with patch.object(engine, 'load_workflow') as mock_load:
            mock_load.return_value = {
                'name': 'test_workflow',
                'tasks': {
                    'task1': {
                        'action_type': 'test_action',
                        'description': 'Test task',
                        'inputs': {}
                    }
                }
            }
            
            # Mock action execution
            with patch('core.enhanced_workflow_engine.execute_action') as mock_execute:
                mock_execute.return_value = {
                    'status': 'Success',
                    'summary': 'Test task completed',
                    'confidence': 0.95,
                    'tactical_resonance': 0.90,
                    'crystallization_potential': 0.85,
                    'genesis_protocol_compliance': {
                        'objective_clarity': 0.90,
                        'implementation_resonance': 0.95,
                        'overall_score': 0.925
                    },
                    'autonomous_orchestration_score': 0.92
                }
                
                # Execute workflow
                result = engine.run_workflow('test_workflow', initial_context)
                
                # Check result structure
                self.assertIn('workflow_name', result)
                self.assertIn('enhanced_resonance_report', result)
                self.assertIn('v35_status', result)
                
                # Check v3.5-GP status
                v35_status = result['v35_status']
                self.assertTrue(v35_status['sandbox_mode'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
