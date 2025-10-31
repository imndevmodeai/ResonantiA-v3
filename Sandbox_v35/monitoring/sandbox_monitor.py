# ResonantiA Protocol v3.5-GP - Sandbox Monitor
# Real-time monitoring for sandbox environment

import os
import json
import time
import logging
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import sys

logger = logging.getLogger(__name__)


class SandboxMonitor:
    """Real-time monitoring for sandbox environment"""
    
    def __init__(self, sandbox_path: str = None, monitoring_interval: int = 5):
        self.sandbox_path = sandbox_path or os.path.dirname(os.path.dirname(__file__))
        self.monitoring_interval = monitoring_interval
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.monitoring_data = []
        
        # Monitoring thresholds
        self.thresholds = {
            'cpu_usage': 80.0,      # 80% CPU usage
            'memory_usage': 80.0,    # 80% memory usage
            'disk_usage': 90.0,      # 90% disk usage
            'response_time': 5.0,    # 5 seconds response time
            'error_rate': 0.05       # 5% error rate
        }
        
        # Monitoring callbacks
        self.callbacks = {
            'threshold_exceeded': [],
            'performance_degradation': [],
            'error_detected': [],
            'system_health': []
        }
        
        # Performance baselines
        self.baselines = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'response_time': 0.0,
            'error_rate': 0.0
        }
        
        # Initialize baselines
        self._initialize_baselines()
    
    def _initialize_baselines(self):
        """Initialize performance baselines"""
        logger.info("Initializing performance baselines")
        
        try:
            # Get initial system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            self.baselines = {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'response_time': 0.0,  # Will be updated during monitoring
                'error_rate': 0.0      # Will be updated during monitoring
            }
            
            logger.info(f"Baselines initialized: CPU={cpu_usage:.1f}%, Memory={memory_usage:.1f}%")
            
        except Exception as e:
            logger.error(f"Failed to initialize baselines: {e}")
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already running")
            return
        
        logger.info("Starting sandbox monitoring")
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if not self.is_monitoring:
            logger.warning("Monitoring not running")
            return
        
        logger.info("Stopping sandbox monitoring")
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Monitoring loop started")
        
        while self.is_monitoring:
            try:
                # Collect monitoring data
                monitoring_data = self._collect_monitoring_data()
                
                # Store monitoring data
                self.monitoring_data.append(monitoring_data)
                
                # Keep only last 1000 entries
                if len(self.monitoring_data) > 1000:
                    self.monitoring_data = self.monitoring_data[-1000:]
                
                # Check thresholds
                self._check_thresholds(monitoring_data)
                
                # Check performance degradation
                self._check_performance_degradation(monitoring_data)
                
                # Save monitoring data
                self._save_monitoring_data()
                
                # Sleep until next monitoring cycle
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)
        
        logger.info("Monitoring loop stopped")
    
    def _collect_monitoring_data(self) -> Dict[str, Any]:
        """Collect current monitoring data"""
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            process_cpu = process.cpu_percent()
            
            # Sandbox-specific metrics
            sandbox_metrics = self._collect_sandbox_metrics()
            
            monitoring_data = {
                'timestamp': timestamp,
                'system': {
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory.percent,
                    'memory_available': memory.available / 1024 / 1024 / 1024,  # GB
                    'disk_usage': disk.percent,
                    'disk_free': disk.free / 1024 / 1024 / 1024  # GB
                },
                'process': {
                    'memory_mb': process_memory,
                    'cpu_percent': process_cpu,
                    'threads': process.num_threads(),
                    'open_files': len(process.open_files())
                },
                'sandbox': sandbox_metrics
            }
            
            return monitoring_data
            
        except Exception as e:
            logger.error(f"Failed to collect monitoring data: {e}")
            return {
                'timestamp': timestamp,
                'error': str(e)
            }
    
    def _collect_sandbox_metrics(self) -> Dict[str, Any]:
        """Collect sandbox-specific metrics"""
        sandbox_metrics = {
            'files_count': 0,
            'total_size_mb': 0,
            'last_modified': None,
            'validation_status': 'unknown',
            'deployment_status': 'unknown'
        }
        
        try:
            # Count files and calculate size
            file_count = 0
            total_size = 0
            last_modified = None
            
            for root, dirs, files in os.walk(self.sandbox_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        file_count += 1
                        total_size += os.path.getsize(file_path)
                        
                        file_mtime = os.path.getmtime(file_path)
                        if last_modified is None or file_mtime > last_modified:
                            last_modified = file_mtime
            
            sandbox_metrics['files_count'] = file_count
            sandbox_metrics['total_size_mb'] = total_size / 1024 / 1024
            sandbox_metrics['last_modified'] = datetime.fromtimestamp(last_modified).isoformat() if last_modified else None
            
            # Check validation status
            validation_file = os.path.join(self.sandbox_path, 'validation', 'validation_history.json')
            if os.path.exists(validation_file):
                try:
                    with open(validation_file, 'r') as f:
                        validation_history = json.load(f)
                    
                    if validation_history:
                        latest_validation = validation_history[-1]
                        sandbox_metrics['validation_status'] = latest_validation.get('validation_status', 'unknown')
                        sandbox_metrics['validation_score'] = latest_validation.get('overall_score', 0.0)
                except Exception:
                    pass
            
            # Check deployment status
            deployment_file = os.path.join(self.sandbox_path, 'deployment', 'deployment_history.json')
            if os.path.exists(deployment_file):
                try:
                    with open(deployment_file, 'r') as f:
                        deployment_history = json.load(f)
                    
                    if deployment_history:
                        latest_deployment = deployment_history[-1]
                        sandbox_metrics['deployment_status'] = latest_deployment.get('deployment_status', 'unknown')
                except Exception:
                    pass
            
        except Exception as e:
            logger.error(f"Failed to collect sandbox metrics: {e}")
            sandbox_metrics['error'] = str(e)
        
        return sandbox_metrics
    
    def _check_thresholds(self, monitoring_data: Dict[str, Any]):
        """Check if any thresholds are exceeded"""
        if 'error' in monitoring_data:
            return
        
        system = monitoring_data.get('system', {})
        process = monitoring_data.get('process', {})
        
        # Check CPU usage
        cpu_usage = system.get('cpu_usage', 0)
        if cpu_usage > self.thresholds['cpu_usage']:
            self._trigger_callback('threshold_exceeded', {
                'metric': 'cpu_usage',
                'value': cpu_usage,
                'threshold': self.thresholds['cpu_usage'],
                'timestamp': monitoring_data['timestamp']
            })
        
        # Check memory usage
        memory_usage = system.get('memory_usage', 0)
        if memory_usage > self.thresholds['memory_usage']:
            self._trigger_callback('threshold_exceeded', {
                'metric': 'memory_usage',
                'value': memory_usage,
                'threshold': self.thresholds['memory_usage'],
                'timestamp': monitoring_data['timestamp']
            })
        
        # Check disk usage
        disk_usage = system.get('disk_usage', 0)
        if disk_usage > self.thresholds['disk_usage']:
            self._trigger_callback('threshold_exceeded', {
                'metric': 'disk_usage',
                'value': disk_usage,
                'threshold': self.thresholds['disk_usage'],
                'timestamp': monitoring_data['timestamp']
            })
    
    def _check_performance_degradation(self, monitoring_data: Dict[str, Any]):
        """Check for performance degradation"""
        if 'error' in monitoring_data:
            return
        
        system = monitoring_data.get('system', {})
        
        # Check CPU degradation
        cpu_usage = system.get('cpu_usage', 0)
        cpu_degradation = cpu_usage - self.baselines['cpu_usage']
        if cpu_degradation > 20.0:  # 20% increase from baseline
            self._trigger_callback('performance_degradation', {
                'metric': 'cpu_usage',
                'current': cpu_usage,
                'baseline': self.baselines['cpu_usage'],
                'degradation': cpu_degradation,
                'timestamp': monitoring_data['timestamp']
            })
        
        # Check memory degradation
        memory_usage = system.get('memory_usage', 0)
        memory_degradation = memory_usage - self.baselines['memory_usage']
        if memory_degradation > 20.0:  # 20% increase from baseline
            self._trigger_callback('performance_degradation', {
                'metric': 'memory_usage',
                'current': memory_usage,
                'baseline': self.baselines['memory_usage'],
                'degradation': memory_degradation,
                'timestamp': monitoring_data['timestamp']
            })
    
    def _trigger_callback(self, callback_type: str, data: Dict[str, Any]):
        """Trigger monitoring callbacks"""
        callbacks = self.callbacks.get(callback_type, [])
        
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def add_callback(self, callback_type: str, callback: Callable):
        """Add monitoring callback"""
        if callback_type not in self.callbacks:
            self.callbacks[callback_type] = []
        
        self.callbacks[callback_type].append(callback)
    
    def remove_callback(self, callback_type: str, callback: Callable):
        """Remove monitoring callback"""
        if callback_type in self.callbacks:
            try:
                self.callbacks[callback_type].remove(callback)
            except ValueError:
                pass
    
    def _save_monitoring_data(self):
        """Save monitoring data to file"""
        try:
            monitoring_file = os.path.join(self.sandbox_path, 'monitoring', 'monitoring_data.json')
            os.makedirs(os.path.dirname(monitoring_file), exist_ok=True)
            
            # Save last 100 entries
            recent_data = self.monitoring_data[-100:] if self.monitoring_data else []
            
            with open(monitoring_file, 'w') as f:
                json.dump(recent_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to save monitoring data: {e}")
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get monitoring summary"""
        if not self.monitoring_data:
            return {'status': 'no_data'}
        
        # Get recent data (last 10 minutes)
        recent_data = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=10)
        
        for data in self.monitoring_data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                if timestamp > cutoff_time:
                    recent_data.append(data)
            except Exception:
                continue
        
        if not recent_data:
            return {'status': 'no_recent_data'}
        
        # Calculate summary statistics
        cpu_values = [d['system']['cpu_usage'] for d in recent_data if 'system' in d]
        memory_values = [d['system']['memory_usage'] for d in recent_data if 'system' in d]
        
        summary = {
            'status': 'active',
            'monitoring_duration': len(self.monitoring_data),
            'recent_entries': len(recent_data),
            'system_health': {
                'avg_cpu_usage': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'max_cpu_usage': max(cpu_values) if cpu_values else 0,
                'avg_memory_usage': sum(memory_values) / len(memory_values) if memory_values else 0,
                'max_memory_usage': max(memory_values) if memory_values else 0
            },
            'thresholds_exceeded': self._count_threshold_exceeded(recent_data),
            'performance_degradation': self._count_performance_degradation(recent_data)
        }
        
        return summary
    
    def _count_threshold_exceeded(self, data: List[Dict[str, Any]]) -> int:
        """Count threshold exceeded events"""
        count = 0
        for entry in data:
            if 'system' in entry:
                system = entry['system']
                if (system.get('cpu_usage', 0) > self.thresholds['cpu_usage'] or
                    system.get('memory_usage', 0) > self.thresholds['memory_usage'] or
                    system.get('disk_usage', 0) > self.thresholds['disk_usage']):
                    count += 1
        return count
    
    def _count_performance_degradation(self, data: List[Dict[str, Any]]) -> int:
        """Count performance degradation events"""
        count = 0
        for entry in data:
            if 'system' in entry:
                system = entry['system']
                cpu_degradation = system.get('cpu_usage', 0) - self.baselines['cpu_usage']
                memory_degradation = system.get('memory_usage', 0) - self.baselines['memory_usage']
                
                if cpu_degradation > 20.0 or memory_degradation > 20.0:
                    count += 1
        return count
    
    def get_health_status(self) -> str:
        """Get overall health status"""
        summary = self.get_monitoring_summary()
        
        if summary['status'] != 'active':
            return 'unknown'
        
        system_health = summary['system_health']
        
        # Determine health status
        if (system_health['avg_cpu_usage'] > 90 or 
            system_health['avg_memory_usage'] > 90 or
            summary['thresholds_exceeded'] > 5):
            return 'critical'
        elif (system_health['avg_cpu_usage'] > 70 or 
              system_health['avg_memory_usage'] > 70 or
              summary['thresholds_exceeded'] > 2):
            return 'warning'
        else:
            return 'healthy'


def create_sandbox_monitor(sandbox_path: str = None, monitoring_interval: int = 5) -> SandboxMonitor:
    """Create sandbox monitor instance"""
    monitor = SandboxMonitor(sandbox_path, monitoring_interval)
    return monitor


if __name__ == "__main__":
    # Test sandbox monitor
    print("📊 ResonantiA Protocol v3.5-GP Sandbox Monitor")
    print("=" * 60)
    
    monitor = create_sandbox_monitor()
    
    # Add test callback
    def threshold_callback(data):
        print(f"⚠️  Threshold exceeded: {data['metric']} = {data['value']:.1f}%")
    
    monitor.add_callback('threshold_exceeded', threshold_callback)
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Monitor for 30 seconds
        for i in range(6):
            time.sleep(5)
            summary = monitor.get_monitoring_summary()
            health = monitor.get_health_status()
            print(f"Health Status: {health}")
            print(f"Recent Entries: {summary.get('recent_entries', 0)}")
            print(f"Avg CPU: {summary.get('system_health', {}).get('avg_cpu_usage', 0):.1f}%")
            print(f"Avg Memory: {summary.get('system_health', {}).get('avg_memory_usage', 0):.1f}%")
            print("-" * 40)
    
    finally:
        monitor.stop_monitoring()
        print("Monitoring stopped")
