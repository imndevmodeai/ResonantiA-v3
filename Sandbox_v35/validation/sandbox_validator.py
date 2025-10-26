# ResonantiA Protocol v3.5-GP - Sandbox Validator
# Comprehensive validation framework for safe development and deployment

import os
import json
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import sys

logger = logging.getLogger(__name__)


class SandboxValidator:
    """Comprehensive validator for sandbox environment"""
    
    def __init__(self, sandbox_path: str = None):
        self.sandbox_path = sandbox_path or os.path.dirname(os.path.dirname(__file__))
        self.validation_results = {}
        self.validation_history = []
        
        # Validation thresholds
        self.thresholds = {
            'performance_degradation': 0.05,  # 5% max degradation
            'memory_increase': 0.10,         # 10% max memory increase
            'error_rate': 0.01,              # 1% max error rate
            'compatibility_score': 0.95      # 95% min compatibility
        }
    
    def validate_sandbox_environment(self) -> Dict[str, Any]:
        """Comprehensive sandbox environment validation"""
        logger.info("Starting comprehensive sandbox validation")
        
        validation_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'sandbox_path': self.sandbox_path,
            'validation_status': 'running',
            'tests': {}
        }
        
        try:
            # Run all validation tests
            validation_results['tests']['environment_isolation'] = self._test_environment_isolation()
            validation_results['tests']['component_compatibility'] = self._test_component_compatibility()
            validation_results['tests']['performance_benchmarks'] = self._test_performance_benchmarks()
            validation_results['tests']['memory_usage'] = self._test_memory_usage()
            validation_results['tests']['error_handling'] = self._test_error_handling()
            validation_results['tests']['data_integrity'] = self._test_data_integrity()
            validation_results['tests']['security_isolation'] = self._test_security_isolation()
            
            # Calculate overall validation score
            validation_results['overall_score'] = self._calculate_overall_score(validation_results['tests'])
            validation_results['validation_status'] = 'completed'
            
            # Determine if sandbox is ready for deployment
            validation_results['deployment_ready'] = self._is_deployment_ready(validation_results)
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            validation_results['validation_status'] = 'failed'
            validation_results['error'] = str(e)
        
        # Store validation history
        self.validation_history.append(validation_results)
        self._save_validation_history()
        
        return validation_results
    
    def _test_environment_isolation(self) -> Dict[str, Any]:
        """Test that sandbox is properly isolated from production"""
        logger.info("Testing environment isolation")
        
        test_results = {
            'test_name': 'environment_isolation',
            'status': 'running',
            'details': {}
        }
        
        try:
            # Check Python path isolation
            python_path = sys.path.copy()
            production_paths = [p for p in python_path if 'Three_PointO_ArchE' in p and 'Sandbox_v35' not in p]
            
            test_results['details']['production_paths_found'] = len(production_paths)
            test_results['details']['production_paths'] = production_paths
            
            # Check import isolation
            try:
                import importlib
                # Try to import production components directly
                try:
                    import Three_PointO_ArchE.workflow_engine as prod_engine
                    test_results['details']['production_import_possible'] = True
                except ImportError:
                    test_results['details']['production_import_possible'] = False
                
                # Try to import sandbox components
                try:
                    from core.enhanced_workflow_engine import EnhancedWorkflowEngine
                    test_results['details']['sandbox_import_possible'] = True
                except ImportError as e:
                    test_results['details']['sandbox_import_possible'] = False
                    test_results['details']['sandbox_import_error'] = str(e)
                
            except Exception as e:
                test_results['details']['import_test_error'] = str(e)
            
            # Check file system isolation
            sandbox_files = []
            production_files = []
            
            for root, dirs, files in os.walk(self.sandbox_path):
                for file in files:
                    if file.endswith('.py'):
                        sandbox_files.append(os.path.join(root, file))
            
            # Check for production file access
            production_path = os.path.join(os.path.dirname(self.sandbox_path), 'Three_PointO_ArchE')
            if os.path.exists(production_path):
                for root, dirs, files in os.walk(production_path):
                    for file in files:
                        if file.endswith('.py'):
                            production_files.append(os.path.join(root, file))
            
            test_results['details']['sandbox_files_count'] = len(sandbox_files)
            test_results['details']['production_files_count'] = len(production_files)
            
            # Determine isolation status
            isolation_score = 0.0
            if test_results['details']['production_import_possible'] == False:
                isolation_score += 0.4
            if test_results['details']['sandbox_import_possible'] == True:
                isolation_score += 0.3
            if len(production_paths) == 0:
                isolation_score += 0.3
            
            test_results['isolation_score'] = isolation_score
            test_results['status'] = 'passed' if isolation_score >= 0.8 else 'failed'
            
        except Exception as e:
            test_results['status'] = 'error'
            test_results['error'] = str(e)
        
        return test_results
    
    def _test_component_compatibility(self) -> Dict[str, Any]:
        """Test compatibility between enhanced and base components"""
        logger.info("Testing component compatibility")
        
        test_results = {
            'test_name': 'component_compatibility',
            'status': 'running',
            'details': {}
        }
        
        try:
            # Test enhanced IAR validator compatibility
            try:
                from core.enhanced_workflow_engine import EnhancedIARValidator
                validator = EnhancedIARValidator()
                
                # Test standard IAR validation
                standard_iar = {
                    'status': 'Success',
                    'summary': 'Test',
                    'confidence': 0.95,
                    'alignment_check': True,
                    'potential_issues': [],
                    'raw_output_preview': 'Test'
                }
                
                is_valid, issues = validator.validate_structure(standard_iar)
                test_results['details']['standard_iar_validation'] = is_valid
                test_results['details']['standard_iar_issues'] = len(issues)
                
                # Test enhanced IAR validation
                enhanced_iar = {
                    **standard_iar,
                    'genesis_protocol_compliance': {
                        'objective_clarity': 0.90,
                        'implementation_resonance': 0.95,
                        'overall_score': 0.925
                    }
                }
                
                is_valid, issues = validator.validate_enhanced_structure(enhanced_iar)
                test_results['details']['enhanced_iar_validation'] = is_valid
                test_results['details']['enhanced_iar_issues'] = len(issues)
                
            except Exception as e:
                test_results['details']['iar_validator_error'] = str(e)
            
            # Test enhanced resonance tracker compatibility
            try:
                from core.enhanced_workflow_engine import EnhancedResonanceTracker
                tracker = EnhancedResonanceTracker()
                
                # Test standard recording
                iar_data = {
                    'status': 'Success',
                    'confidence': 0.95,
                    'tactical_resonance': 0.90,
                    'crystallization_potential': 0.85
                }
                
                record = tracker.record_execution('test_task', iar_data, {})
                test_results['details']['standard_recording'] = record is not None
                
                # Test enhanced recording
                enhanced_iar_data = {
                    **iar_data,
                    'genesis_protocol_compliance': {'overall_score': 0.92},
                    'autonomous_orchestration_score': 0.88
                }
                
                enhanced_record = tracker.record_enhanced_execution('test_task', enhanced_iar_data, {})
                test_results['details']['enhanced_recording'] = enhanced_record is not None
                
            except Exception as e:
                test_results['details']['resonance_tracker_error'] = str(e)
            
            # Calculate compatibility score
            compatibility_score = 0.0
            if test_results['details'].get('standard_iar_validation', False):
                compatibility_score += 0.25
            if test_results['details'].get('enhanced_iar_validation', False):
                compatibility_score += 0.25
            if test_results['details'].get('standard_recording', False):
                compatibility_score += 0.25
            if test_results['details'].get('enhanced_recording', False):
                compatibility_score += 0.25
            
            test_results['compatibility_score'] = compatibility_score
            test_results['status'] = 'passed' if compatibility_score >= 0.8 else 'failed'
            
        except Exception as e:
            test_results['status'] = 'error'
            test_results['error'] = str(e)
        
        return test_results
    
    def _test_performance_benchmarks(self) -> Dict[str, Any]:
        """Test performance benchmarks"""
        logger.info("Testing performance benchmarks")
        
        test_results = {
            'test_name': 'performance_benchmarks',
            'status': 'running',
            'details': {}
        }
        
        try:
            # Test enhanced workflow engine creation time
            start_time = time.time()
            from core.enhanced_workflow_engine import create_sandbox_workflow_engine
            engine = create_sandbox_workflow_engine()
            creation_time = time.time() - start_time
            
            test_results['details']['engine_creation_time'] = creation_time
            
            # Test enhanced dashboard generation time
            start_time = time.time()
            dashboard = engine.get_enhanced_dashboard()
            dashboard_time = time.time() - start_time
            
            test_results['details']['dashboard_generation_time'] = dashboard_time
            
            # Test enhanced resonance report generation time
            start_time = time.time()
            report = engine.resonance_tracker.get_enhanced_resonance_report()
            report_time = time.time() - start_time
            
            test_results['details']['report_generation_time'] = report_time
            
            # Performance thresholds
            performance_score = 1.0
            if creation_time > 1.0:  # 1 second threshold
                performance_score -= 0.3
            if dashboard_time > 0.5:  # 0.5 second threshold
                performance_score -= 0.3
            if report_time > 0.2:  # 0.2 second threshold
                performance_score -= 0.4
            
            test_results['performance_score'] = max(0.0, performance_score)
            test_results['status'] = 'passed' if performance_score >= 0.7 else 'failed'
            
        except Exception as e:
            test_results['status'] = 'error'
            test_results['error'] = str(e)
        
        return test_results
    
    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage"""
        logger.info("Testing memory usage")
        
        test_results = {
            'test_name': 'memory_usage',
            'status': 'running',
            'details': {}
        }
        
        try:
            import psutil
            import gc
            
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create enhanced components
            from core.enhanced_workflow_engine import create_sandbox_workflow_engine
            engine = create_sandbox_workflow_engine()
            
            # Get memory after creation
            after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Generate some reports
            for i in range(10):
                dashboard = engine.get_enhanced_dashboard()
                report = engine.resonance_tracker.get_enhanced_resonance_report()
            
            # Get memory after operations
            after_operations_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Cleanup
            del engine
            gc.collect()
            
            # Get memory after cleanup
            after_cleanup_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            test_results['details']['initial_memory_mb'] = initial_memory
            test_results['details']['after_creation_memory_mb'] = after_creation_memory
            test_results['details']['after_operations_memory_mb'] = after_operations_memory
            test_results['details']['after_cleanup_memory_mb'] = after_cleanup_memory
            
            # Calculate memory increase
            memory_increase = (after_creation_memory - initial_memory) / initial_memory
            test_results['details']['memory_increase_ratio'] = memory_increase
            
            # Memory score
            memory_score = 1.0
            if memory_increase > self.thresholds['memory_increase']:
                memory_score -= 0.5
            
            test_results['memory_score'] = max(0.0, memory_score)
            test_results['status'] = 'passed' if memory_score >= 0.5 else 'failed'
            
        except Exception as e:
            test_results['status'] = 'error'
            test_results['error'] = str(e)
        
        return test_results
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """Test error handling capabilities"""
        logger.info("Testing error handling")
        
        test_results = {
            'test_name': 'error_handling',
            'status': 'running',
            'details': {}
        }
        
        try:
            from core.enhanced_workflow_engine import EnhancedIARValidator, EnhancedResonanceTracker
            
            # Test IAR validator error handling
            validator = EnhancedIARValidator()
            
            # Test with invalid IAR data
            invalid_iar = {
                'status': 'Invalid',
                'confidence': 1.5,  # Invalid confidence
                'missing_field': 'test'
            }
            
            is_valid, issues = validator.validate_enhanced_structure(invalid_iar)
            test_results['details']['invalid_iar_handled'] = not is_valid
            test_results['details']['invalid_iar_issues_count'] = len(issues)
            
            # Test resonance tracker error handling
            tracker = EnhancedResonanceTracker()
            
            # Test with malformed data
            malformed_iar = {
                'status': 'Success',
                'confidence': 0.95,
                'genesis_protocol_compliance': 'invalid_type'  # Should be dict
            }
            
            try:
                record = tracker.record_enhanced_execution('test_task', malformed_iar, {})
                test_results['details']['malformed_data_handled'] = True
            except Exception:
                test_results['details']['malformed_data_handled'] = False
            
            # Error handling score
            error_score = 0.0
            if test_results['details']['invalid_iar_handled']:
                error_score += 0.5
            if test_results['details']['malformed_data_handled']:
                error_score += 0.5
            
            test_results['error_handling_score'] = error_score
            test_results['status'] = 'passed' if error_score >= 0.8 else 'failed'
            
        except Exception as e:
            test_results['status'] = 'error'
            test_results['error'] = str(e)
        
        return test_results
    
    def _test_data_integrity(self) -> Dict[str, Any]:
        """Test data integrity"""
        logger.info("Testing data integrity")
        
        test_results = {
            'test_name': 'data_integrity',
            'status': 'running',
            'details': {}
        }
        
        try:
            from core.enhanced_workflow_engine import EnhancedResonanceTracker
            
            tracker = EnhancedResonanceTracker()
            
            # Test data consistency
            test_data = {
                'status': 'Success',
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
            
            # Record multiple executions
            for i in range(5):
                record = tracker.record_enhanced_execution(f'task_{i}', test_data, {})
                
                # Verify data integrity
                if record['task_id'] != f'task_{i}':
                    test_results['details']['data_integrity_failed'] = True
                    break
                
                if record['confidence'] != 0.95:
                    test_results['details']['data_integrity_failed'] = True
                    break
                
                if record['genesis_protocol_compliance']['overall_score'] != 0.925:
                    test_results['details']['data_integrity_failed'] = True
                    break
            
            test_results['details']['data_integrity_failed'] = test_results['details'].get('data_integrity_failed', False)
            
            # Data integrity score
            integrity_score = 1.0 if not test_results['details']['data_integrity_failed'] else 0.0
            test_results['data_integrity_score'] = integrity_score
            test_results['status'] = 'passed' if integrity_score >= 0.8 else 'failed'
            
        except Exception as e:
            test_results['status'] = 'error'
            test_results['error'] = str(e)
        
        return test_results
    
    def _test_security_isolation(self) -> Dict[str, Any]:
        """Test security isolation"""
        logger.info("Testing security isolation")
        
        test_results = {
            'test_name': 'security_isolation',
            'status': 'running',
            'details': {}
        }
        
        try:
            # Test file system access
            test_results['details']['sandbox_readable'] = os.access(self.sandbox_path, os.R_OK)
            test_results['details']['sandbox_writable'] = os.access(self.sandbox_path, os.W_OK)
            
            # Test production path access
            production_path = os.path.join(os.path.dirname(self.sandbox_path), 'Three_PointO_ArchE')
            if os.path.exists(production_path):
                test_results['details']['production_readable'] = os.access(production_path, os.R_OK)
                test_results['details']['production_writable'] = os.access(production_path, os.W_OK)
            else:
                test_results['details']['production_readable'] = False
                test_results['details']['production_writable'] = False
            
            # Security score
            security_score = 0.0
            if test_results['details']['sandbox_readable']:
                security_score += 0.25
            if test_results['details']['sandbox_writable']:
                security_score += 0.25
            if not test_results['details']['production_writable']:
                security_score += 0.5
            
            test_results['security_score'] = security_score
            test_results['status'] = 'passed' if security_score >= 0.8 else 'failed'
            
        except Exception as e:
            test_results['status'] = 'error'
            test_results['error'] = str(e)
        
        return test_results
    
    def _calculate_overall_score(self, tests: Dict[str, Any]) -> float:
        """Calculate overall validation score"""
        scores = []
        
        for test_name, test_result in tests.items():
            if 'score' in test_result:
                scores.append(test_result['score'])
        
        if not scores:
            return 0.0
        
        return sum(scores) / len(scores)
    
    def _is_deployment_ready(self, validation_results: Dict[str, Any]) -> bool:
        """Determine if sandbox is ready for deployment"""
        overall_score = validation_results.get('overall_score', 0.0)
        
        # Check individual test statuses
        all_tests_passed = all(
            test_result.get('status') == 'passed' 
            for test_result in validation_results['tests'].values()
        )
        
        return overall_score >= self.thresholds['compatibility_score'] and all_tests_passed
    
    def _save_validation_history(self):
        """Save validation history"""
        history_file = os.path.join(self.sandbox_path, 'validation', 'validation_history.json')
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        with open(history_file, 'w') as f:
            json.dump(self.validation_history, f, indent=2)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        if not self.validation_history:
            return {'status': 'no_validations'}
        
        latest_validation = self.validation_history[-1]
        
        return {
            'timestamp': latest_validation['timestamp'],
            'overall_score': latest_validation.get('overall_score', 0.0),
            'deployment_ready': latest_validation.get('deployment_ready', False),
            'test_summary': {
                test_name: {
                    'status': test_result.get('status', 'unknown'),
                    'score': test_result.get('score', 0.0)
                }
                for test_name, test_result in latest_validation['tests'].items()
            }
        }


def run_sandbox_validation(sandbox_path: str = None) -> Dict[str, Any]:
    """Run comprehensive sandbox validation"""
    validator = SandboxValidator(sandbox_path)
    return validator.validate_sandbox_environment()


if __name__ == "__main__":
    # Run validation
    print("🧪 ResonantiA Protocol v3.5-GP Sandbox Validation")
    print("=" * 60)
    
    validation_results = run_sandbox_validation()
    
    print(f"Validation Status: {validation_results['validation_status']}")
    print(f"Overall Score: {validation_results.get('overall_score', 0.0):.2f}")
    print(f"Deployment Ready: {validation_results.get('deployment_ready', False)}")
    
    print("\nTest Results:")
    for test_name, test_result in validation_results['tests'].items():
        status = test_result.get('status', 'unknown')
        score = test_result.get('score', 0.0)
        print(f"  {test_name}: {status} (score: {score:.2f})")
    
    if validation_results.get('deployment_ready', False):
        print("\n✅ Sandbox is ready for deployment!")
    else:
        print("\n❌ Sandbox needs additional validation before deployment")
