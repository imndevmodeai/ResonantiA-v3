# ResonantiA Protocol v3.5-GP - Safe Deployer
# Safe deployment mechanism for validated sandbox components

import os
import json
import shutil
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import sys

logger = logging.getLogger(__name__)


class SafeDeployer:
    """Safe deployment mechanism for validated sandbox components"""
    
    def __init__(self, sandbox_path: str = None, production_path: str = None):
        self.sandbox_path = sandbox_path or os.path.join(os.path.dirname(__file__), '..')
        self.production_path = production_path or os.path.join(os.path.dirname(self.sandbox_path), 'Three_PointO_ArchE')
        
        # Deployment configuration
        self.deployment_config = {
            'backup_enabled': True,
            'rollback_enabled': True,
            'validation_required': True,
            'staged_deployment': True
        }
        
        # Deployment history
        self.deployment_history = []
        
        # Component mapping
        self.component_mapping = {
            'enhanced_workflow_engine.py': 'workflow_engine.py',
            'enhanced_iar_validator.py': 'workflow_engine.py',  # Integrated
            'enhanced_resonance_tracker.py': 'workflow_engine.py'  # Integrated
        }
    
    def validate_deployment_readiness(self) -> Dict[str, Any]:
        """Validate that sandbox is ready for deployment"""
        logger.info("Validating deployment readiness")
        
        validation_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'deployment_ready': False,
            'validation_tests': {},
            'overall_score': 0.0
        }
        
        try:
            # Import sandbox validator
            sys.path.insert(0, os.path.join(self.sandbox_path, 'validation'))
            from sandbox_validator import SandboxValidator
            
            validator = SandboxValidator(self.sandbox_path)
            validation_results = validator.validate_sandbox_environment()
            
        except Exception as e:
            logger.error(f"Deployment validation failed: {e}")
            validation_results['error'] = str(e)
        
        return validation_results
    
    def create_backup(self) -> str:
        """Create backup of production system"""
        logger.info("Creating production system backup")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(os.path.dirname(self.production_path), f"backup_Three_PointO_ArchE_{timestamp}")
        
        try:
            # Copy production directory
            shutil.copytree(self.production_path, backup_path)
            
            # Create backup metadata
            backup_metadata = {
                'timestamp': timestamp,
                'backup_path': backup_path,
                'production_path': self.production_path,
                'backup_size': self._get_directory_size(backup_path),
                'files_backed_up': self._count_files(backup_path)
            }
            
            metadata_file = os.path.join(backup_path, 'backup_metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(backup_metadata, f, indent=2)
            
            logger.info(f"Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise
    
    def stage_deployment(self) -> Dict[str, Any]:
        """Stage deployment components"""
        logger.info("Staging deployment components")
        
        staging_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'staged_components': [],
            'staging_errors': []
        }
        
        try:
            # Create staging directory
            staging_path = os.path.join(self.sandbox_path, 'deployment', 'staging')
            os.makedirs(staging_path, exist_ok=True)
            
            # Stage enhanced components
            for sandbox_file, production_file in self.component_mapping.items():
                source_path = os.path.join(self.sandbox_path, 'core', sandbox_file)
                target_path = os.path.join(staging_path, production_file)
                
                if os.path.exists(source_path):
                    # Copy file to staging
                    shutil.copy2(source_path, target_path)
                    
                    # Validate staged file
                    if self._validate_staged_file(target_path):
                        staging_results['staged_components'].append({
                            'source': sandbox_file,
                            'target': production_file,
                            'staged_path': target_path,
                            'size': os.path.getsize(target_path)
                        })
                    else:
                        staging_results['staging_errors'].append(f"Validation failed for {sandbox_file}")
                else:
                    staging_results['staging_errors'].append(f"Source file not found: {sandbox_file}")
            
            # Create staging metadata
            staging_metadata = {
                'timestamp': datetime.utcnow().isoformat(),
                'staged_components': staging_results['staged_components'],
                'staging_errors': staging_results['staging_errors'],
                'staging_path': staging_path
            }
            
            metadata_file = os.path.join(staging_path, 'staging_metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(staging_metadata, f, indent=2)
            
            logger.info(f"Staging completed: {len(staging_results['staged_components'])} components staged")
            
        except Exception as e:
            logger.error(f"Staging failed: {e}")
            staging_results['staging_errors'].append(str(e))
        
        return staging_results
    
    def deploy_components(self, staging_results: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy staged components to production"""
        logger.info("Deploying staged components to production")
        
        deployment_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'deployed_components': [],
            'deployment_errors': [],
            'rollback_info': {}
        }
        
        try:
            staging_path = os.path.join(self.sandbox_path, 'deployment', 'staging')
            
            # Deploy each staged component
            for component in staging_results['staged_components']:
                source_path = component['staged_path']
                target_path = os.path.join(self.production_path, component['target'])
                
                # Create rollback info
                rollback_info = {
                    'original_file': target_path,
                    'backup_file': f"{target_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
                
                try:
                    # Backup original file
                    if os.path.exists(target_path):
                        shutil.copy2(target_path, rollback_info['backup_file'])
                    
                    # Deploy new file
                    shutil.copy2(source_path, target_path)
                    
                    # Validate deployment
                    if self._validate_deployed_file(target_path):
                        deployment_results['deployed_components'].append({
                            'component': component['target'],
                            'deployed_path': target_path,
                            'rollback_file': rollback_info['backup_file']
                        })
                        deployment_results['rollback_info'][component['target']] = rollback_info
                    else:
                        deployment_results['deployment_errors'].append(f"Deployment validation failed for {component['target']}")
                        
                        # Rollback this component
                        if os.path.exists(rollback_info['backup_file']):
                            shutil.copy2(rollback_info['backup_file'], target_path)
                            os.remove(rollback_info['backup_file'])
                
                except Exception as e:
                    deployment_results['deployment_errors'].append(f"Failed to deploy {component['target']}: {e}")
            
            # Create deployment metadata
            deployment_metadata = {
                'timestamp': datetime.utcnow().isoformat(),
                'deployed_components': deployment_results['deployed_components'],
                'deployment_errors': deployment_results['deployment_errors'],
                'rollback_info': deployment_results['rollback_info']
            }
            
            metadata_file = os.path.join(self.production_path, 'deployment_metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(deployment_metadata, f, indent=2)
            
            logger.info(f"Deployment completed: {len(deployment_results['deployed_components'])} components deployed")
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            deployment_results['deployment_errors'].append(str(e))
        
        return deployment_results
    
    def rollback_deployment(self, deployment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback deployment to previous state"""
        logger.info("Rolling back deployment")
        
        rollback_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'rolled_back_components': [],
            'rollback_errors': []
        }
        
        try:
            rollback_info = deployment_results.get('rollback_info', {})
            
            for component, info in rollback_info.items():
                try:
                    original_file = info['original_file']
                    backup_file = info['backup_file']
                    
                    if os.path.exists(backup_file):
                        # Restore original file
                        shutil.copy2(backup_file, original_file)
                        
                        # Remove backup file
                        os.remove(backup_file)
                        
                        rollback_results['rolled_back_components'].append(component)
                    else:
                        rollback_results['rollback_errors'].append(f"Backup file not found for {component}")
                
                except Exception as e:
                    rollback_results['rollback_errors'].append(f"Failed to rollback {component}: {e}")
            
            # Remove deployment metadata
            metadata_file = os.path.join(self.production_path, 'deployment_metadata.json')
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
            
            logger.info(f"Rollback completed: {len(rollback_results['rolled_back_components'])} components rolled back")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            rollback_results['rollback_errors'].append(str(e))
        
        return rollback_results
    
    def validate_deployment(self) -> Dict[str, Any]:
        """Validate deployed components"""
        logger.info("Validating deployed components")
        
        validation_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'validation_passed': False,
            'validation_errors': []
        }
        
        try:
            # Test production system functionality
            sys.path.insert(0, self.production_path)
            
            # Test basic imports
            try:
                from workflow_engine import IARCompliantWorkflowEngine
                validation_results['basic_import'] = True
            except Exception as e:
                validation_results['basic_import'] = False
                validation_results['validation_errors'].append(f"Basic import failed: {e}")
            
            # Test enhanced functionality
            try:
                # Check if enhanced components are available
                engine = IARCompliantWorkflowEngine()
                
                # Test enhanced dashboard if available
                if hasattr(engine, 'get_enhanced_dashboard'):
                    dashboard = engine.get_enhanced_dashboard()
                    validation_results['enhanced_dashboard'] = True
                else:
                    validation_results['enhanced_dashboard'] = False
                    validation_results['validation_errors'].append("Enhanced dashboard not available")
                
                # Test enhanced resonance report if available
                if hasattr(engine.resonance_tracker, 'get_enhanced_resonance_report'):
                    report = engine.resonance_tracker.get_enhanced_resonance_report()
                    validation_results['enhanced_resonance_report'] = True
                else:
                    validation_results['enhanced_resonance_report'] = False
                    validation_results['validation_errors'].append("Enhanced resonance report not available")
                
            except Exception as e:
                validation_results['enhanced_functionality'] = False
                validation_results['validation_errors'].append(f"Enhanced functionality test failed: {e}")
            
            # Determine overall validation result
            validation_results['validation_passed'] = (
                validation_results.get('basic_import', False) and
                validation_results.get('enhanced_dashboard', False) and
                validation_results.get('enhanced_resonance_report', False)
            )
            
        except Exception as e:
            logger.error(f"Deployment validation failed: {e}")
            validation_results['validation_errors'].append(str(e))
        
        return validation_results
    
    def _validate_staged_file(self, file_path: str) -> bool:
        """Validate staged file"""
        try:
            # Check file exists and is readable
            if not os.path.exists(file_path) or not os.access(file_path, os.R_OK):
                return False
            
            # Check file size
            if os.path.getsize(file_path) == 0:
                return False
            
            # Check Python syntax
            with open(file_path, 'r') as f:
                content = f.read()
            
            compile(content, file_path, 'exec')
            return True
            
        except Exception:
            return False
    
    def _validate_deployed_file(self, file_path: str) -> bool:
        """Validate deployed file"""
        return self._validate_staged_file(file_path)
    
    def _get_directory_size(self, directory: str) -> int:
        """Get directory size in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def _count_files(self, directory: str) -> int:
        """Count files in directory"""
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            file_count += len(filenames)
        return file_count
    
    def full_deployment(self) -> Dict[str, Any]:
        """Perform full deployment process"""
        logger.info("Starting full deployment process")
        
        deployment_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'deployment_status': 'running',
            'steps': {}
        }
        
        try:
            # Step 1: Validate deployment readiness
            logger.info("Step 1: Validating deployment readiness")
            validation_results = self.validate_deployment_readiness()
            deployment_results['steps']['validation'] = validation_results
            
            if not validation_results.get('deployment_ready', False):
                deployment_results['deployment_status'] = 'failed'
                deployment_results['error'] = 'Deployment validation failed'
                return deployment_results
            
            # Step 2: Create backup
            logger.info("Step 2: Creating production backup")
            backup_path = self.create_backup()
            deployment_results['steps']['backup'] = {'backup_path': backup_path}
            
            # Step 3: Stage deployment
            logger.info("Step 3: Staging deployment components")
            staging_results = self.stage_deployment()
            deployment_results['steps']['staging'] = staging_results
            
            if staging_results['staging_errors']:
                deployment_results['deployment_status'] = 'failed'
                deployment_results['error'] = 'Staging failed'
                return deployment_results
            
            # Step 4: Deploy components
            logger.info("Step 4: Deploying components")
            deployment_results['steps']['deployment'] = self.deploy_components(staging_results)
            
            # Step 5: Validate deployment
            logger.info("Step 5: Validating deployment")
            validation_results = self.validate_deployment()
            deployment_results['steps']['post_deployment_validation'] = validation_results
            
            if not validation_results['validation_passed']:
                # Rollback deployment
                logger.info("Deployment validation failed, rolling back")
                rollback_results = self.rollback_deployment(deployment_results['steps']['deployment'])
                deployment_results['steps']['rollback'] = rollback_results
                deployment_results['deployment_status'] = 'failed'
                deployment_results['error'] = 'Post-deployment validation failed'
            else:
                deployment_results['deployment_status'] = 'success'
            
        except Exception as e:
            logger.error(f"Full deployment failed: {e}")
            deployment_results['deployment_status'] = 'failed'
            deployment_results['error'] = str(e)
        
        # Store deployment history
        self.deployment_history.append(deployment_results)
        self._save_deployment_history()
        
        return deployment_results
    
    def _save_deployment_history(self):
        """Save deployment history"""
        history_file = os.path.join(self.sandbox_path, 'deployment', 'deployment_history.json')
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        with open(history_file, 'w') as f:
            json.dump(self.deployment_history, f, indent=2)


def run_safe_deployment(sandbox_path: str = None, production_path: str = None) -> Dict[str, Any]:
    """Run safe deployment process"""
    deployer = SafeDeployer(sandbox_path, production_path)
    return deployer.full_deployment()


if __name__ == "__main__":
    # Run safe deployment
    print("🚀 ResonantiA Protocol v3.5-GP Safe Deployment")
    print("=" * 60)
    
    deployment_results = run_safe_deployment()
    
    print(f"Deployment Status: {deployment_results['deployment_status']}")
    
    if deployment_results['deployment_status'] == 'success':
        print("✅ Deployment completed successfully!")
        print(f"Deployed Components: {len(deployment_results['steps']['deployment']['deployed_components'])}")
    else:
        print("❌ Deployment failed")
        print(f"Error: {deployment_results.get('error', 'Unknown error')}")
        
        if 'rollback' in deployment_results['steps']:
            print("🔄 Rollback completed")
    
    print(f"\nDeployment Steps:")
    for step_name, step_result in deployment_results['steps'].items():
        print(f"  {step_name}: {'✅' if 'error' not in step_result else '❌'}")
