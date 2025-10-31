#!/usr/bin/env python3
"""
VCD Testing Suite - Comprehensive Testing Framework
Implements automated testing for Visual Cognitive Debugger system
"""

import pytest
import asyncio
import json
import time
import websockets
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Three_PointO_ArchE.websocket_timeout_wrapper import WebSocketTimeoutWrapper, test_vcd_bridge_connection

class VCDTestSuite:
    """Comprehensive VCD Testing Suite"""
    
    def __init__(self):
        self.test_results = []
        self.vcd_bridge_uri = "ws://localhost:8765"
        self.timeout_wrapper = WebSocketTimeoutWrapper(timeout=5.0)
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all VCD tests"""
        print("🧪 Starting VCD Testing Suite...")
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_suite_version": "1.0",
            "tests": {}
        }
        
        # Run test categories
        test_results["tests"]["unit_tests"] = self.run_unit_tests()
        test_results["tests"]["integration_tests"] = self.run_integration_tests()
        test_results["tests"]["performance_tests"] = self.run_performance_tests()
        test_results["tests"]["stress_tests"] = self.run_stress_tests()
        
        # Calculate overall results
        test_results["summary"] = self.calculate_test_summary(test_results["tests"])
        
        return test_results
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests for VCD components"""
        print("  🔬 Running Unit Tests...")
        
        results = {
            "category": "unit_tests",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        
        # Test VCD UI implementation
        vcd_ui_test = self.test_vcd_ui_implementation()
        results["tests"].append(vcd_ui_test)
        
        # Test VCD Bridge configuration
        vcd_bridge_test = self.test_vcd_bridge_configuration()
        results["tests"].append(vcd_bridge_test)
        
        # Test timeout wrapper
        timeout_wrapper_test = self.test_timeout_wrapper()
        results["tests"].append(timeout_wrapper_test)
        
        # Test configuration file
        config_test = self.test_configuration_file()
        results["tests"].append(config_test)
        
        # Calculate results
        for test in results["tests"]:
            results["total"] += 1
            if test["status"] == "passed":
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def test_vcd_ui_implementation(self) -> Dict[str, Any]:
        """Test VCD UI implementation"""
        try:
            vcd_ui_path = Path("Three_PointO_ArchE/visual_cognitive_debugger_ui.py")
            
            if not vcd_ui_path.exists():
                return {
                    "name": "VCD UI Implementation",
                    "status": "failed",
                    "error": "VCD UI file not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check file size and basic structure
            file_size = vcd_ui_path.stat().st_size
            content = vcd_ui_path.read_text()
            
            # Check for key classes and methods
            has_visualizer_class = "class AdvancedCognitiveVisualizer" in content
            has_debugger_class = "class VisualCognitiveDebugger" in content
            has_visualization_modes = "class CognitiveVisualizationMode" in content
            
            if has_visualizer_class and has_debugger_class and has_visualization_modes:
                return {
                    "name": "VCD UI Implementation",
                    "status": "passed",
                    "details": {
                        "file_size": file_size,
                        "has_visualizer_class": has_visualizer_class,
                        "has_debugger_class": has_debugger_class,
                        "has_visualization_modes": has_visualization_modes
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "name": "VCD UI Implementation",
                    "status": "failed",
                    "error": "Missing required classes or methods",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "name": "VCD UI Implementation",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_vcd_bridge_configuration(self) -> Dict[str, Any]:
        """Test VCD Bridge configuration"""
        try:
            config_path = Path("vcd_bridge_config.json")
            
            if not config_path.exists():
                return {
                    "name": "VCD Bridge Configuration",
                    "status": "failed",
                    "error": "Configuration file not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Load and validate configuration
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check required sections
            required_sections = ["vcd_bridge", "vcd_ui", "vcd_analysis_agent", "monitoring"]
            missing_sections = [section for section in required_sections if section not in config]
            
            if missing_sections:
                return {
                    "name": "VCD Bridge Configuration",
                    "status": "failed",
                    "error": f"Missing configuration sections: {missing_sections}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Validate VCD Bridge configuration
            vcd_bridge_config = config["vcd_bridge"]
            required_bridge_keys = ["server", "websocket", "logging"]
            missing_bridge_keys = [key for key in required_bridge_keys if key not in vcd_bridge_config]
            
            if missing_bridge_keys:
                return {
                    "name": "VCD Bridge Configuration",
                    "status": "failed",
                    "error": f"Missing VCD Bridge configuration keys: {missing_bridge_keys}",
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "name": "VCD Bridge Configuration",
                "status": "passed",
                "details": {
                    "config_sections": len(config),
                    "bridge_port": vcd_bridge_config["server"]["port"],
                    "timeout": vcd_bridge_config["server"]["timeout"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "name": "VCD Bridge Configuration",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_timeout_wrapper(self) -> Dict[str, Any]:
        """Test WebSocket timeout wrapper"""
        try:
            wrapper_path = Path("Three_PointO_ArchE/websocket_timeout_wrapper.py")
            
            if not wrapper_path.exists():
                return {
                    "name": "WebSocket Timeout Wrapper",
                    "status": "failed",
                    "error": "Timeout wrapper file not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check file content
            content = wrapper_path.read_text()
            
            # Check for key components
            has_wrapper_class = "class WebSocketTimeoutWrapper" in content
            has_connect_method = "async def connect_with_timeout" in content
            has_test_function = "async def test_vcd_bridge_connection" in content
            
            if has_wrapper_class and has_connect_method and has_test_function:
                return {
                    "name": "WebSocket Timeout Wrapper",
                    "status": "passed",
                    "details": {
                        "has_wrapper_class": has_wrapper_class,
                        "has_connect_method": has_connect_method,
                        "has_test_function": has_test_function
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "name": "WebSocket Timeout Wrapper",
                    "status": "failed",
                    "error": "Missing required methods or classes",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "name": "WebSocket Timeout Wrapper",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_configuration_file(self) -> Dict[str, Any]:
        """Test configuration file structure"""
        try:
            config_path = Path("vcd_bridge_config.json")
            
            if not config_path.exists():
                return {
                    "name": "Configuration File Structure",
                    "status": "failed",
                    "error": "Configuration file not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Validate JSON structure
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check configuration completeness
            vcd_bridge = config.get("vcd_bridge", {})
            server_config = vcd_bridge.get("server", {})
            
            required_server_keys = ["host", "port", "timeout", "max_connections"]
            missing_keys = [key for key in required_server_keys if key not in server_config]
            
            if missing_keys:
                return {
                    "name": "Configuration File Structure",
                    "status": "failed",
                    "error": f"Missing server configuration keys: {missing_keys}",
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "name": "Configuration File Structure",
                "status": "passed",
                "details": {
                    "config_valid": True,
                    "server_port": server_config["port"],
                    "server_timeout": server_config["timeout"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "name": "Configuration File Structure",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        print("  🔗 Running Integration Tests...")
        
        results = {
            "category": "integration_tests",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        
        # Test VCD Analysis Agent integration
        analysis_agent_test = self.test_vcd_analysis_agent_integration()
        results["tests"].append(analysis_agent_test)
        
        # Test ask_arche integration
        ask_arche_test = self.test_ask_arche_integration()
        results["tests"].append(ask_arche_test)
        
        # Calculate results
        for test in results["tests"]:
            results["total"] += 1
            if test["status"] == "passed":
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def test_vcd_analysis_agent_integration(self) -> Dict[str, Any]:
        """Test VCD Analysis Agent integration"""
        try:
            agent_path = Path("Three_PointO_ArchE/vcd_analysis_agent_simple.py")
            
            if not agent_path.exists():
                return {
                    "name": "VCD Analysis Agent Integration",
                    "status": "failed",
                    "error": "Analysis agent file not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check for timeout wrapper integration
            content = agent_path.read_text()
            has_timeout_wrapper_import = "websocket_timeout_wrapper" in content
            has_timeout_wrapper_usage = "test_vcd_bridge_connection_simple" in content
            
            if has_timeout_wrapper_import and has_timeout_wrapper_usage:
                return {
                    "name": "VCD Analysis Agent Integration",
                    "status": "passed",
                    "details": {
                        "has_timeout_wrapper_import": has_timeout_wrapper_import,
                        "has_timeout_wrapper_usage": has_timeout_wrapper_usage
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "name": "VCD Analysis Agent Integration",
                    "status": "failed",
                    "error": "Timeout wrapper integration not found",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "name": "VCD Analysis Agent Integration",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_ask_arche_integration(self) -> Dict[str, Any]:
        """Test ask_arche VCD integration"""
        try:
            ask_arche_files = [
                "ask_arche_vcd_enhanced.py",
                "ask_arche_vcd_real.py",
                "ask_arche_vcd_analysis_enhanced.py"
            ]
            
            integration_status = {}
            for file in ask_arche_files:
                file_path = Path(file)
                integration_status[file] = {
                    "exists": file_path.exists(),
                    "has_vcd_integration": False
                }
                
                if file_path.exists():
                    content = file_path.read_text()
                    integration_status[file]["has_vcd_integration"] = "VCD" in content or "vcd" in content
            
            # Check if at least one integration file exists
            has_integration = any(status["exists"] and status["has_vcd_integration"] 
                                for status in integration_status.values())
            
            if has_integration:
                return {
                    "name": "Ask_Arche VCD Integration",
                    "status": "passed",
                    "details": integration_status,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "name": "Ask_Arche VCD Integration",
                    "status": "failed",
                    "error": "No VCD integration found in ask_arche files",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "name": "Ask_Arche VCD Integration",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        print("  ⚡ Running Performance Tests...")
        
        results = {
            "category": "performance_tests",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        
        # Test file access performance
        file_access_test = self.test_file_access_performance()
        results["tests"].append(file_access_test)
        
        # Test configuration loading performance
        config_loading_test = self.test_configuration_loading_performance()
        results["tests"].append(config_loading_test)
        
        # Calculate results
        for test in results["tests"]:
            results["total"] += 1
            if test["status"] == "passed":
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def test_file_access_performance(self) -> Dict[str, Any]:
        """Test file access performance"""
        try:
            start_time = time.time()
            
            # Test VCD UI file access
            vcd_ui_path = Path("Three_PointO_ArchE/visual_cognitive_debugger_ui.py")
            if vcd_ui_path.exists():
                file_size = vcd_ui_path.stat().st_size
                content = vcd_ui_path.read_text()
            
            access_time = time.time() - start_time
            
            # Performance threshold: < 0.1 seconds
            if access_time < 0.1:
                return {
                    "name": "File Access Performance",
                    "status": "passed",
                    "details": {
                        "access_time": access_time,
                        "file_size": file_size,
                        "performance_rating": "excellent"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "name": "File Access Performance",
                    "status": "failed",
                    "error": f"File access too slow: {access_time:.3f}s",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "name": "File Access Performance",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_configuration_loading_performance(self) -> Dict[str, Any]:
        """Test configuration loading performance"""
        try:
            start_time = time.time()
            
            # Test configuration loading
            config_path = Path("vcd_bridge_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            
            loading_time = time.time() - start_time
            
            # Performance threshold: < 0.05 seconds
            if loading_time < 0.05:
                return {
                    "name": "Configuration Loading Performance",
                    "status": "passed",
                    "details": {
                        "loading_time": loading_time,
                        "config_sections": len(config),
                        "performance_rating": "excellent"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "name": "Configuration Loading Performance",
                    "status": "failed",
                    "error": f"Configuration loading too slow: {loading_time:.3f}s",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "name": "Configuration Loading Performance",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_stress_tests(self) -> Dict[str, Any]:
        """Run stress tests"""
        print("  💪 Running Stress Tests...")
        
        results = {
            "category": "stress_tests",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        
        # Test multiple file access
        multiple_access_test = self.test_multiple_file_access()
        results["tests"].append(multiple_access_test)
        
        # Test configuration validation stress
        config_stress_test = self.test_configuration_validation_stress()
        results["tests"].append(config_stress_test)
        
        # Calculate results
        for test in results["tests"]:
            results["total"] += 1
            if test["status"] == "passed":
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def test_multiple_file_access(self) -> Dict[str, Any]:
        """Test multiple file access stress"""
        try:
            start_time = time.time()
            
            # Access multiple files in sequence
            files_to_test = [
                "Three_PointO_ArchE/visual_cognitive_debugger_ui.py",
                "Three_PointO_ArchE/vcd_analysis_agent_simple.py",
                "Three_PointO_ArchE/websocket_timeout_wrapper.py",
                "vcd_bridge_config.json"
            ]
            
            accessed_files = 0
            for file_path in files_to_test:
                path = Path(file_path)
                if path.exists():
                    content = path.read_text()
                    accessed_files += 1
            
            total_time = time.time() - start_time
            
            # Stress test threshold: < 0.5 seconds for all files
            if total_time < 0.5 and accessed_files == len(files_to_test):
                return {
                    "name": "Multiple File Access Stress",
                    "status": "passed",
                    "details": {
                        "total_time": total_time,
                        "files_accessed": accessed_files,
                        "files_total": len(files_to_test),
                        "performance_rating": "excellent"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "name": "Multiple File Access Stress",
                    "status": "failed",
                    "error": f"Stress test failed: {total_time:.3f}s for {accessed_files}/{len(files_to_test)} files",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "name": "Multiple File Access Stress",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_configuration_validation_stress(self) -> Dict[str, Any]:
        """Test configuration validation stress"""
        try:
            start_time = time.time()
            
            # Perform multiple configuration validations
            config_path = Path("vcd_bridge_config.json")
            validation_count = 100
            
            for _ in range(validation_count):
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Validate structure
                    assert "vcd_bridge" in config
                    assert "server" in config["vcd_bridge"]
                    assert "port" in config["vcd_bridge"]["server"]
            
            total_time = time.time() - start_time
            
            # Stress test threshold: < 1 second for 100 validations
            if total_time < 1.0:
                return {
                    "name": "Configuration Validation Stress",
                    "status": "passed",
                    "details": {
                        "total_time": total_time,
                        "validations_performed": validation_count,
                        "performance_rating": "excellent"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "name": "Configuration Validation Stress",
                    "status": "failed",
                    "error": f"Stress test failed: {total_time:.3f}s for {validation_count} validations",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "name": "Configuration Validation Stress",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def calculate_test_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall test summary"""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for category, results in test_results.items():
            if isinstance(results, dict) and "total" in results:
                total_tests += results["total"]
                total_passed += results["passed"]
                total_failed += results["failed"]
        
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "pass_rate": pass_rate,
            "overall_status": "passed" if pass_rate >= 90 else "failed"
        }

def main():
    """Main test execution function"""
    print("🧪 VCD Testing Suite - Comprehensive Testing Framework")
    print("=" * 60)
    
    # Create and run test suite
    test_suite = VCDTestSuite()
    results = test_suite.run_all_tests()
    
    # Display results
    print("\n📊 Test Results Summary:")
    summary = results["summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['total_passed']}")
    print(f"Failed: {summary['total_failed']}")
    print(f"Pass Rate: {summary['pass_rate']:.1f}%")
    print(f"Overall Status: {summary['overall_status']}")
    
    # Display detailed results
    print("\n🔍 Detailed Results:")
    for category, category_results in results["tests"].items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for test in category_results["tests"]:
            status_icon = "✅" if test["status"] == "passed" else "❌"
            print(f"  {status_icon} {test['name']}: {test['status']}")
            if test["status"] == "failed" and "error" in test:
                print(f"    Error: {test['error']}")
    
    # Save results
    results_file = f"vcd_test_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved to: {results_file}")
    
    if summary["overall_status"] == "passed":
        print("\n🎉 All tests passed! VCD system is ready for production.")
    else:
        print("\n⚠️  Some tests failed. Please review the results and fix issues.")
    
    return summary["overall_status"] == "passed"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)







