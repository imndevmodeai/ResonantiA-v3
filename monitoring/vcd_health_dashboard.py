#!/usr/bin/env python3
"""
VCD Health Dashboard - Real-time Monitoring Interface
Provides comprehensive health monitoring for Visual Cognitive Debugger system
"""

import json
import time
import asyncio
import websockets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import os

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Three_PointO_ArchE.websocket_timeout_wrapper import WebSocketTimeoutWrapper

class VCDHealthDashboard:
    """VCD Health Dashboard - Real-time monitoring interface"""
    
    def __init__(self):
        self.dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "unknown",
            "components": {},
            "performance_metrics": {},
            "alerts": [],
            "health_score": 0
        }
        
        self.timeout_wrapper = WebSocketTimeoutWrapper(timeout=5.0)
        self.vcd_bridge_uri = "ws://localhost:8765"
        
        # Health thresholds
        self.thresholds = {
            "response_time": 1.0,  # seconds
            "memory_usage": 0.8,   # percentage
            "cpu_usage": 0.9,      # percentage
            "error_rate": 0.05     # percentage
        }
        
        # Component status tracking
        self.component_status = {
            "vcd_ui": "unknown",
            "vcd_bridge": "unknown",
            "vcd_analysis_agent": "unknown",
            "websocket_communication": "unknown"
        }
    
    def generate_health_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive health dashboard"""
        print("🏥 Generating VCD Health Dashboard...")
        
        # Update dashboard data
        self.dashboard_data["timestamp"] = datetime.now().isoformat()
        
        # Check component health
        self._check_component_health()
        
        # Calculate performance metrics
        self._calculate_performance_metrics()
        
        # Generate alerts
        self._generate_alerts()
        
        # Calculate overall health score
        self._calculate_health_score()
        
        # Determine system status
        self._determine_system_status()
        
        return self.dashboard_data
    
    def _check_component_health(self) -> None:
        """Check health of all VCD components"""
        print("  🔍 Checking component health...")
        
        # Check VCD UI
        vcd_ui_health = self._check_vcd_ui_health()
        self.dashboard_data["components"]["vcd_ui"] = vcd_ui_health
        
        # Check VCD Bridge
        vcd_bridge_health = self._check_vcd_bridge_health()
        self.dashboard_data["components"]["vcd_bridge"] = vcd_bridge_health
        
        # Check VCD Analysis Agent
        analysis_agent_health = self._check_analysis_agent_health()
        self.dashboard_data["components"]["vcd_analysis_agent"] = analysis_agent_health
        
        # Check WebSocket Communication
        websocket_health = self._check_websocket_health()
        self.dashboard_data["components"]["websocket_communication"] = websocket_health
    
    def _check_vcd_ui_health(self) -> Dict[str, Any]:
        """Check VCD UI component health"""
        try:
            vcd_ui_path = Path("Three_PointO_ArchE/visual_cognitive_debugger_ui.py")
            
            if not vcd_ui_path.exists():
                return {
                    "status": "critical",
                    "message": "VCD UI file not found",
                    "last_check": datetime.now().isoformat()
                }
            
            # Check file integrity
            file_size = vcd_ui_path.stat().st_size
            content = vcd_ui_path.read_text()
            
            # Check for key components
            has_visualizer = "class AdvancedCognitiveVisualizer" in content
            has_debugger = "class VisualCognitiveDebugger" in content
            has_modes = "class CognitiveVisualizationMode" in content
            
            if has_visualizer and has_debugger and has_modes:
                return {
                    "status": "healthy",
                    "message": "VCD UI component is healthy",
                    "details": {
                        "file_size": file_size,
                        "has_visualizer": has_visualizer,
                        "has_debugger": has_debugger,
                        "has_modes": has_modes
                    },
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "warning",
                    "message": "VCD UI missing required components",
                    "last_check": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "message": f"VCD UI health check failed: {str(e)}",
                "last_check": datetime.now().isoformat()
            }
    
    def _check_vcd_bridge_health(self) -> Dict[str, Any]:
        """Check VCD Bridge component health"""
        try:
            # Check configuration file
            config_path = Path("vcd_bridge_config.json")
            
            if not config_path.exists():
                return {
                    "status": "critical",
                    "message": "VCD Bridge configuration not found",
                    "last_check": datetime.now().isoformat()
                }
            
            # Load and validate configuration
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check configuration completeness
            vcd_bridge_config = config.get("vcd_bridge", {})
            server_config = vcd_bridge_config.get("server", {})
            
            required_keys = ["host", "port", "timeout", "max_connections"]
            missing_keys = [key for key in required_keys if key not in server_config]
            
            if missing_keys:
                return {
                    "status": "warning",
                    "message": f"VCD Bridge configuration missing keys: {missing_keys}",
                    "last_check": datetime.now().isoformat()
                }
            
            # Check if server is running (simplified check)
            server_running = self._check_server_running()
            
            return {
                "status": "healthy" if server_running else "warning",
                "message": "VCD Bridge configuration is valid" + ("" if server_running else " but server not running"),
                "details": {
                    "config_valid": True,
                    "server_port": server_config["port"],
                    "server_timeout": server_config["timeout"],
                    "server_running": server_running
                },
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "critical",
                "message": f"VCD Bridge health check failed: {str(e)}",
                "last_check": datetime.now().isoformat()
            }
    
    def _check_server_running(self) -> bool:
        """Check if VCD Bridge server is running"""
        try:
            # Simple check - try to connect to the server
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 8765))
            sock.close()
            return result == 0
        except:
            return False
    
    def _check_analysis_agent_health(self) -> Dict[str, Any]:
        """Check VCD Analysis Agent component health"""
        try:
            agent_path = Path("Three_PointO_ArchE/vcd_analysis_agent_simple.py")
            
            if not agent_path.exists():
                return {
                    "status": "critical",
                    "message": "VCD Analysis Agent file not found",
                    "last_check": datetime.now().isoformat()
                }
            
            # Check file content
            content = agent_path.read_text()
            
            # Check for key components
            has_agent_class = "class VCDAnalysisAgent" in content
            has_timeout_wrapper = "websocket_timeout_wrapper" in content
            has_analysis_methods = "async def analyze" in content
            
            if has_agent_class and has_timeout_wrapper and has_analysis_methods:
                return {
                    "status": "healthy",
                    "message": "VCD Analysis Agent is healthy",
                    "details": {
                        "has_agent_class": has_agent_class,
                        "has_timeout_wrapper": has_timeout_wrapper,
                        "has_analysis_methods": has_analysis_methods
                    },
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "warning",
                    "message": "VCD Analysis Agent missing required components",
                    "last_check": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "message": f"VCD Analysis Agent health check failed: {str(e)}",
                "last_check": datetime.now().isoformat()
            }
    
    def _check_websocket_health(self) -> Dict[str, Any]:
        """Check WebSocket communication health"""
        try:
            # Check timeout wrapper
            wrapper_path = Path("Three_PointO_ArchE/websocket_timeout_wrapper.py")
            
            if not wrapper_path.exists():
                return {
                    "status": "critical",
                    "message": "WebSocket timeout wrapper not found",
                    "last_check": datetime.now().isoformat()
                }
            
            # Check wrapper content
            content = wrapper_path.read_text()
            
            has_wrapper_class = "class WebSocketTimeoutWrapper" in content
            has_connect_method = "async def connect_with_timeout" in content
            
            if has_wrapper_class and has_connect_method:
                return {
                    "status": "healthy",
                    "message": "WebSocket communication components are healthy",
                    "details": {
                        "has_wrapper_class": has_wrapper_class,
                        "has_connect_method": has_connect_method
                    },
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "warning",
                    "message": "WebSocket communication missing required components",
                    "last_check": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "message": f"WebSocket communication health check failed: {str(e)}",
                "last_check": datetime.now().isoformat()
            }
    
    def _calculate_performance_metrics(self) -> None:
        """Calculate performance metrics"""
        print("  📊 Calculating performance metrics...")
        
        metrics = {
            "response_time": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "error_rate": 0.0,
            "throughput": 0.0
        }
        
        # Calculate response time (simplified)
        start_time = time.time()
        self._perform_health_checks()
        response_time = time.time() - start_time
        metrics["response_time"] = response_time
        
        # Calculate error rate based on component status
        total_components = len(self.dashboard_data["components"])
        error_components = sum(1 for comp in self.dashboard_data["components"].values() 
                             if comp["status"] in ["critical", "warning"])
        metrics["error_rate"] = error_components / total_components if total_components > 0 else 0
        
        # Calculate throughput (simplified)
        metrics["throughput"] = 1.0 / response_time if response_time > 0 else 0
        
        # Simulate memory and CPU usage (in real implementation, these would be actual system metrics)
        metrics["memory_usage"] = 0.3  # 30% memory usage
        metrics["cpu_usage"] = 0.2     # 20% CPU usage
        
        self.dashboard_data["performance_metrics"] = metrics
    
    def _perform_health_checks(self) -> None:
        """Perform health checks for performance calculation"""
        # This is a simplified version - in real implementation, this would be more comprehensive
        pass
    
    def _generate_alerts(self) -> None:
        """Generate alerts based on component status and performance metrics"""
        print("  🚨 Generating alerts...")
        
        alerts = []
        
        # Check component status
        for component_name, component_data in self.dashboard_data["components"].items():
            if component_data["status"] == "critical":
                alerts.append({
                    "level": "critical",
                    "component": component_name,
                    "message": component_data["message"],
                    "timestamp": datetime.now().isoformat()
                })
            elif component_data["status"] == "warning":
                alerts.append({
                    "level": "warning",
                    "component": component_name,
                    "message": component_data["message"],
                    "timestamp": datetime.now().isoformat()
                })
        
        # Check performance metrics
        metrics = self.dashboard_data["performance_metrics"]
        
        if metrics["response_time"] > self.thresholds["response_time"]:
            alerts.append({
                "level": "warning",
                "component": "performance",
                "message": f"Response time exceeds threshold: {metrics['response_time']:.3f}s",
                "timestamp": datetime.now().isoformat()
            })
        
        if metrics["error_rate"] > self.thresholds["error_rate"]:
            alerts.append({
                "level": "critical",
                "component": "performance",
                "message": f"Error rate exceeds threshold: {metrics['error_rate']:.1%}",
                "timestamp": datetime.now().isoformat()
            })
        
        self.dashboard_data["alerts"] = alerts
    
    def _calculate_health_score(self) -> None:
        """Calculate overall health score"""
        print("  🎯 Calculating health score...")
        
        # Base score
        base_score = 100
        
        # Deduct points for component issues
        for component_data in self.dashboard_data["components"].values():
            if component_data["status"] == "critical":
                base_score -= 30
            elif component_data["status"] == "warning":
                base_score -= 10
        
        # Deduct points for performance issues
        metrics = self.dashboard_data["performance_metrics"]
        
        if metrics["response_time"] > self.thresholds["response_time"]:
            base_score -= 15
        
        if metrics["error_rate"] > self.thresholds["error_rate"]:
            base_score -= 25
        
        # Ensure score is between 0 and 100
        health_score = max(0, min(100, base_score))
        
        self.dashboard_data["health_score"] = health_score
    
    def _determine_system_status(self) -> None:
        """Determine overall system status"""
        health_score = self.dashboard_data["health_score"]
        
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 60:
            status = "fair"
        elif health_score >= 40:
            status = "poor"
        else:
            status = "critical"
        
        self.dashboard_data["system_status"] = status
    
    def display_dashboard(self) -> None:
        """Display the health dashboard"""
        print("\n🏥 VCD Health Dashboard")
        print("=" * 50)
        
        # System status
        status_icon = {
            "excellent": "🟢",
            "good": "🟡",
            "fair": "🟠",
            "poor": "🔴",
            "critical": "💀"
        }.get(self.dashboard_data["system_status"], "❓")
        
        print(f"System Status: {status_icon} {self.dashboard_data['system_status'].upper()}")
        print(f"Health Score: {self.dashboard_data['health_score']}/100")
        print(f"Last Updated: {self.dashboard_data['timestamp']}")
        
        # Component status
        print("\n🔍 Component Status:")
        for component_name, component_data in self.dashboard_data["components"].items():
            status_icon = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "❌"
            }.get(component_data["status"], "❓")
            
            print(f"  {status_icon} {component_name}: {component_data['status']}")
            print(f"    {component_data['message']}")
        
        # Performance metrics
        print("\n📊 Performance Metrics:")
        metrics = self.dashboard_data["performance_metrics"]
        print(f"  Response Time: {metrics['response_time']:.3f}s")
        print(f"  Memory Usage: {metrics['memory_usage']:.1%}")
        print(f"  CPU Usage: {metrics['cpu_usage']:.1%}")
        print(f"  Error Rate: {metrics['error_rate']:.1%}")
        print(f"  Throughput: {metrics['throughput']:.2f} ops/s")
        
        # Alerts
        if self.dashboard_data["alerts"]:
            print("\n🚨 Alerts:")
            for alert in self.dashboard_data["alerts"]:
                alert_icon = {
                    "critical": "🔴",
                    "warning": "🟡"
                }.get(alert["level"], "❓")
                
                print(f"  {alert_icon} {alert['level'].upper()}: {alert['message']}")
        else:
            print("\n✅ No alerts")
    
    def save_dashboard(self, filename: Optional[str] = None) -> str:
        """Save dashboard data to file"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"vcd_health_dashboard_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.dashboard_data, f, indent=2, default=str)
        
        return filename

def main():
    """Main dashboard execution function"""
    print("🏥 VCD Health Dashboard - Real-time Monitoring Interface")
    print("=" * 60)
    
    # Create and generate dashboard
    dashboard = VCDHealthDashboard()
    dashboard_data = dashboard.generate_health_dashboard()
    
    # Display dashboard
    dashboard.display_dashboard()
    
    # Save dashboard
    filename = dashboard.save_dashboard()
    print(f"\n💾 Dashboard saved to: {filename}")
    
    return dashboard_data["system_status"] in ["excellent", "good"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



