#!/usr/bin/env python3
# ResonantiA Protocol v3.5-GP - Sandbox Runner
# Main entry point for sandbox environment

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

# Add sandbox to path
sys.path.insert(0, os.path.dirname(__file__))

from core.enhanced_workflow_engine import create_sandbox_workflow_engine
from validation.sandbox_validator import run_sandbox_validation
from deployment.safe_deployer import run_safe_deployment
from monitoring.sandbox_monitor import create_sandbox_monitor


def setup_logging(config: Dict[str, Any]):
    """Setup logging configuration"""
    log_config = config.get('logging', {})
    
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler() if log_config.get('console_logging', True) else logging.NullHandler(),
            logging.FileHandler(log_config.get('log_file', 'sandbox.log')) if log_config.get('file_logging', True) else logging.NullHandler()
        ]
    )


def load_config() -> Dict[str, Any]:
    """Load sandbox configuration"""
    config_file = os.path.join(os.path.dirname(__file__), 'config', 'sandbox_config.json')
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Failed to load config: {e}")
        return {}


def run_validation_mode(config: Dict[str, Any]) -> bool:
    """Run validation mode"""
    print("🧪 Running Sandbox Validation")
    print("=" * 50)
    
    validation_results = run_sandbox_validation()
    
    print(f"Validation Status: {validation_results['validation_status']}")
    print(f"Overall Score: {validation_results.get('overall_score', 0.0):.2f}")
    print(f"Deployment Ready: {validation_results.get('deployment_ready', False)}")
    
    print("\nTest Results:")
    for test_name, test_result in validation_results['tests'].items():
        status = test_result.get('status', 'unknown')
        score = test_result.get('score', 0.0)
        print(f"  {test_name}: {status} (score: {score:.2f})")
    
    return validation_results.get('deployment_ready', False)


def run_deployment_mode(config: Dict[str, Any]) -> bool:
    """Run deployment mode"""
    print("🚀 Running Safe Deployment")
    print("=" * 50)
    
    deployment_results = run_safe_deployment()
    
    print(f"Deployment Status: {deployment_results['deployment_status']}")
    
    if deployment_results['deployment_status'] == 'success':
        print("✅ Deployment completed successfully!")
        print(f"Deployed Components: {len(deployment_results['steps']['deployment']['deployed_components'])}")
        return True
    else:
        print("❌ Deployment failed")
        print(f"Error: {deployment_results.get('error', 'Unknown error')}")
        
        if 'rollback' in deployment_results['steps']:
            print("🔄 Rollback completed")
        return False


def run_monitoring_mode(config: Dict[str, Any]):
    """Run monitoring mode"""
    print("📊 Starting Sandbox Monitoring")
    print("=" * 50)
    
    monitor = create_sandbox_monitor()
    
    # Add monitoring callbacks
    def threshold_callback(data):
        print(f"⚠️  Threshold exceeded: {data['metric']} = {data['value']:.1f}%")
    
    def performance_callback(data):
        print(f"📉 Performance degradation: {data['metric']} degraded by {data['degradation']:.1f}%")
    
    monitor.add_callback('threshold_exceeded', threshold_callback)
    monitor.add_callback('performance_degradation', performance_callback)
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        print("Monitoring started. Press Ctrl+C to stop.")
        while True:
            import time
            time.sleep(10)
            
            summary = monitor.get_monitoring_summary()
            health = monitor.get_health_status()
            
            print(f"\nHealth Status: {health}")
            print(f"Recent Entries: {summary.get('recent_entries', 0)}")
            print(f"Avg CPU: {summary.get('system_health', {}).get('avg_cpu_usage', 0):.1f}%")
            print(f"Avg Memory: {summary.get('system_health', {}).get('avg_memory_usage', 0):.1f}%")
            print(f"Thresholds Exceeded: {summary.get('thresholds_exceeded', 0)}")
            print("-" * 40)
    
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
    finally:
        monitor.stop_monitoring()
        print("Monitoring stopped")


def run_test_mode(config: Dict[str, Any]):
    """Run test mode"""
    print("🧪 Running Sandbox Tests")
    print("=" * 50)
    
    try:
        # Import test suite
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
        import unittest
        
        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = os.path.join(os.path.dirname(__file__), 'tests')
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("✅ All tests passed!")
            return True
        else:
            print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
            return False
    
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def run_development_mode(config: Dict[str, Any]):
    """Run development mode"""
    print("🛠️  Sandbox Development Mode")
    print("=" * 50)
    
    try:
        # Create enhanced workflow engine
        engine = create_sandbox_workflow_engine()
        
        print("✅ Enhanced Workflow Engine created")
        
        # Test enhanced dashboard
        dashboard = engine.get_enhanced_dashboard()
        print(f"✅ Enhanced Dashboard: {len(dashboard)} metrics")
        
        # Test enhanced resonance report
        report = engine.resonance_tracker.get_enhanced_resonance_report()
        print(f"✅ Enhanced Resonance Report: {len(report)} metrics")
        
        # Show v3.5-GP features
        v35_features = dashboard.get('v35_features', {})
        print(f"\nv3.5-GP Features:")
        for feature, enabled in v35_features.items():
            status = "✅ Enabled" if enabled else "❌ Disabled"
            print(f"  {feature}: {status}")
        
        print("\nSandbox is ready for development!")
        return True
    
    except Exception as e:
        print(f"❌ Development mode failed: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ResonantiA Protocol v3.5-GP Sandbox')
    parser.add_argument('mode', choices=['validate', 'deploy', 'monitor', 'test', 'dev'], 
                       help='Sandbox mode to run')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Setup logging
    setup_logging(config)
    
    # Run selected mode
    success = False
    
    if args.mode == 'validate':
        success = run_validation_mode(config)
    elif args.mode == 'deploy':
        success = run_deployment_mode(config)
    elif args.mode == 'monitor':
        run_monitoring_mode(config)
        success = True
    elif args.mode == 'test':
        success = run_test_mode(config)
    elif args.mode == 'dev':
        success = run_development_mode(config)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
