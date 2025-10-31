#!/usr/bin/env python3
# ResonantiA Protocol v3.5-GP - Tools Dashboard
# Comprehensive dashboard showing all available tools and their status

import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
import tkinter as tk
from tkinter import ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import numpy as np

# Add sandbox to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.enhanced_workflow_engine import create_sandbox_workflow_engine
from validation.sandbox_validator import run_sandbox_validation
from monitoring.sandbox_monitor import create_sandbox_monitor


class ToolsDashboard:
    """Comprehensive tools dashboard with real-time monitoring"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ResonantiA Protocol v3.5-GP - Tools Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Dashboard data
        self.tools_data = {}
        self.monitoring_data = {}
        self.validation_data = {}
        self.engine = None
        self.monitor = None
        
        # Initialize dashboard
        self.setup_styles()
        self.create_widgets()
        self.load_tools_data()
        self.start_monitoring()
        
    def setup_styles(self):
        """Setup dashboard styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background='#1e1e1e', 
                       foreground='#00ff88', 
                       font=('Arial', 16, 'bold'))
        
        style.configure('Header.TLabel', 
                       background='#2d2d2d', 
                       foreground='#ffffff', 
                       font=('Arial', 12, 'bold'))
        
        style.configure('Status.TLabel', 
                       background='#2d2d2d', 
                       foreground='#00ff88', 
                       font=('Arial', 10))
        
        style.configure('Error.TLabel', 
                       background='#2d2d2d', 
                       foreground='#ff4444', 
                       font=('Arial', 10))
        
        style.configure('Warning.TLabel', 
                       background='#2d2d2d', 
                       foreground='#ffaa00', 
                       font=('Arial', 10))
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="ResonantiA Protocol v3.5-GP Tools Dashboard", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tools Status Tab
        self.tools_frame = ttk.Frame(notebook)
        notebook.add(self.tools_frame, text="Tools Status")
        self.create_tools_tab()
        
        # System Monitoring Tab
        self.monitoring_frame = ttk.Frame(notebook)
        notebook.add(self.monitoring_frame, text="System Monitoring")
        self.create_monitoring_tab()
        
        # Validation Tab
        self.validation_frame = ttk.Frame(notebook)
        notebook.add(self.validation_frame, text="Validation")
        self.create_validation_tab()
        
        # Performance Tab
        self.performance_frame = ttk.Frame(notebook)
        notebook.add(self.performance_frame, text="Performance")
        self.create_performance_tab()
        
        # Control Panel
        self.create_control_panel(main_frame)
    
    def create_tools_tab(self):
        """Create tools status tab"""
        # Tools grid
        tools_container = ttk.Frame(self.tools_frame)
        tools_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable frame
        canvas = tk.Canvas(tools_container, bg='#2d2d2d')
        scrollbar = ttk.Scrollbar(tools_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Tools categories
        self.create_tools_category(scrollable_frame, "Core Components", [
            "Enhanced Workflow Engine", "Enhanced IAR Validator", "Enhanced Resonance Tracker",
            "Genesis Protocol", "Resonant Corrective Loop", "Autonomous Orchestration"
        ])
        
        self.create_tools_category(scrollable_frame, "Analysis Tools", [
            "Causal Inference Tool (DoWhy)", "Agent-Based Modeling (Mesa)", 
            "Predictive Modeling", "TSP Solver", "Combat ABM"
        ])
        
        self.create_tools_category(scrollable_frame, "Web & Search", [
            "Web Search Tool", "Enhanced Perception Engine", "Google Maps Integration",
            "Selenium WebDriver", "WebSocket Bridge"
        ])
        
        self.create_tools_category(scrollable_frame, "AI & ML", [
            "Enhanced LLM Provider", "Prompt Manager", "Knowledge Graph Manager",
            "Insight Solidification Engine", "Temporal Reasoning Engine"
        ])
        
        self.create_tools_category(scrollable_frame, "System Tools", [
            "Code Executor", "Visual Cognitive Debugger", "Token Cache Manager",
            "Scalable Framework", "Mastermind", "Vetting Agent"
        ])
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_tools_category(self, parent, category_name, tools):
        """Create a tools category section"""
        # Category header
        category_frame = ttk.LabelFrame(parent, text=category_name, style='Header.TLabel')
        category_frame.pack(fill=tk.X, pady=5)
        
        # Tools grid
        for i, tool in enumerate(tools):
            tool_frame = ttk.Frame(category_frame)
            tool_frame.grid(row=i//2, column=i%2, sticky="ew", padx=5, pady=2)
            
            # Tool name
            tool_label = ttk.Label(tool_frame, text=tool, style='Status.TLabel')
            tool_label.pack(side=tk.LEFT)
            
            # Status indicator
            status_label = ttk.Label(tool_frame, text="●", style='Status.TLabel')
            status_label.pack(side=tk.RIGHT)
            
            # Store reference for updates
            if not hasattr(self, 'tool_status_labels'):
                self.tool_status_labels = {}
            self.tool_status_labels[tool] = status_label
    
    def create_monitoring_tab(self):
        """Create system monitoring tab"""
        # System metrics frame
        metrics_frame = ttk.LabelFrame(self.monitoring_frame, text="System Metrics")
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # CPU and Memory
        cpu_frame = ttk.Frame(metrics_frame)
        cpu_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(cpu_frame, text="CPU Usage:").pack(side=tk.LEFT)
        self.cpu_label = ttk.Label(cpu_frame, text="0%", style='Status.TLabel')
        self.cpu_label.pack(side=tk.RIGHT)
        
        memory_frame = ttk.Frame(metrics_frame)
        memory_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(memory_frame, text="Memory Usage:").pack(side=tk.LEFT)
        self.memory_label = ttk.Label(memory_frame, text="0%", style='Status.TLabel')
        self.memory_label.pack(side=tk.RIGHT)
        
        # Real-time chart
        chart_frame = ttk.LabelFrame(self.monitoring_frame, text="Real-time Performance")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 6))
        self.fig.patch.set_facecolor('#2d2d2d')
        
        # Configure axes
        self.ax1.set_facecolor('#2d2d2d')
        self.ax1.set_title('CPU Usage', color='white')
        self.ax1.set_ylabel('CPU %', color='white')
        self.ax1.tick_params(colors='white')
        
        self.ax2.set_facecolor('#2d2d2d')
        self.ax2.set_title('Memory Usage', color='white')
        self.ax2.set_ylabel('Memory %', color='white')
        self.ax2.tick_params(colors='white')
        
        # Embed chart
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize data
        self.cpu_data = []
        self.memory_data = []
        self.time_data = []
    
    def create_validation_tab(self):
        """Create validation tab"""
        # Validation results
        validation_frame = ttk.LabelFrame(self.validation_frame, text="Validation Results")
        validation_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Validation status
        status_frame = ttk.Frame(validation_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(status_frame, text="Overall Score:").pack(side=tk.LEFT)
        self.validation_score_label = ttk.Label(status_frame, text="0.00", style='Status.TLabel')
        self.validation_score_label.pack(side=tk.RIGHT)
        
        # Test results
        self.test_results_text = scrolledtext.ScrolledText(validation_frame, height=15, bg='#2d2d2d', fg='white')
        self.test_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_performance_tab(self):
        """Create performance tab"""
        # Performance metrics
        perf_frame = ttk.LabelFrame(self.performance_frame, text="Performance Metrics")
        perf_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create performance chart
        self.perf_fig, self.perf_ax = plt.subplots(figsize=(12, 8))
        self.perf_fig.patch.set_facecolor('#2d2d2d')
        self.perf_ax.set_facecolor('#2d2d2d')
        
        # Performance data
        self.performance_data = {
            'tactical_resonance': [],
            'crystallization_potential': [],
            'genesis_compliance': [],
            'autonomous_score': []
        }
        
        # Embed performance chart
        self.perf_canvas = FigureCanvasTkAgg(self.perf_fig, perf_frame)
        self.perf_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_control_panel(self, parent):
        """Create control panel"""
        control_frame = ttk.LabelFrame(parent, text="Control Panel")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Run Validation", command=self.run_validation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh Tools", command=self.refresh_tools).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Report", command=self.export_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deploy to Production", command=self.deploy_to_production).pack(side=tk.LEFT, padx=5)
    
    def load_tools_data(self):
        """Load tools data and check availability"""
        try:
            # Initialize engine
            self.engine = create_sandbox_workflow_engine()
            
            # Check tool availability
            self.tools_data = {
                "Core Components": {
                    "Enhanced Workflow Engine": self.check_tool_availability("EnhancedWorkflowEngine"),
                    "Enhanced IAR Validator": self.check_tool_availability("EnhancedIARValidator"),
                    "Enhanced Resonance Tracker": self.check_tool_availability("EnhancedResonanceTracker"),
                    "Genesis Protocol": True,  # Always available in v3.5-GP
                    "Resonant Corrective Loop": True,  # Always available in v3.5-GP
                    "Autonomous Orchestration": True  # Always available in v3.5-GP
                },
                "Analysis Tools": {
                    "Causal Inference Tool (DoWhy)": self.check_import("dowhy"),
                    "Agent-Based Modeling (Mesa)": self.check_import("mesa"),
                    "Predictive Modeling": self.check_import("sklearn"),
                    "TSP Solver": self.check_import("networkx"),
                    "Combat ABM": self.check_import("mesa")
                },
                "Web & Search": {
                    "Web Search Tool": self.check_import("requests"),
                    "Enhanced Perception Engine": self.check_import("selenium"),
                    "Google Maps Integration": self.check_import("googlemaps"),
                    "Selenium WebDriver": self.check_import("selenium"),
                    "WebSocket Bridge": self.check_import("websocket")
                },
                "AI & ML": {
                    "Enhanced LLM Provider": True,  # Built-in
                    "Prompt Manager": True,  # Built-in
                    "Knowledge Graph Manager": True,  # Built-in
                    "Insight Solidification Engine": True,  # Built-in
                    "Temporal Reasoning Engine": True  # Built-in
                },
                "System Tools": {
                    "Code Executor": True,  # Built-in
                    "Visual Cognitive Debugger": True,  # Built-in
                    "Token Cache Manager": True,  # Built-in
                    "Scalable Framework": self.check_import("numpy"),
                    "Mastermind": True,  # Built-in
                    "Vetting Agent": True  # Built-in
                }
            }
            
            self.update_tools_display()
            
        except Exception as e:
            print(f"Error loading tools data: {e}")
    
    def check_tool_availability(self, tool_name):
        """Check if a specific tool is available"""
        try:
            if tool_name == "EnhancedWorkflowEngine":
                return hasattr(self.engine, 'get_enhanced_dashboard')
            elif tool_name == "EnhancedIARValidator":
                return hasattr(self.engine, 'iar_validator') and hasattr(self.engine.iar_validator, 'validate_enhanced_structure')
            elif tool_name == "EnhancedResonanceTracker":
                return hasattr(self.engine, 'resonance_tracker') and hasattr(self.engine.resonance_tracker, 'get_enhanced_resonance_report')
            return False
        except:
            return False
    
    def check_import(self, module_name):
        """Check if a module can be imported"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def update_tools_display(self):
        """Update tools display with current status"""
        if hasattr(self, 'tool_status_labels'):
            for tool_name, status_label in self.tool_status_labels.items():
                # Find tool status
                status = False
                for category, tools in self.tools_data.items():
                    if tool_name in tools:
                        status = tools[tool_name]
                        break
                
                # Update status indicator
                if status:
                    status_label.configure(text="●", foreground='#00ff88')
                else:
                    status_label.configure(text="●", foreground='#ff4444')
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        try:
            self.monitor = create_sandbox_monitor()
            self.monitor.start_monitoring()
            
            # Start update thread
            self.update_thread = threading.Thread(target=self.update_monitoring, daemon=True)
            self.update_thread.start()
            
        except Exception as e:
            print(f"Error starting monitoring: {e}")
    
    def update_monitoring(self):
        """Update monitoring data"""
        while True:
            try:
                # Update system metrics
                import psutil
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                
                # Update labels
                self.root.after(0, lambda: self.cpu_label.configure(text=f"{cpu_percent:.1f}%"))
                self.root.after(0, lambda: self.memory_label.configure(text=f"{memory_percent:.1f}%"))
                
                # Update charts
                self.root.after(0, self.update_charts, cpu_percent, memory_percent)
                
                # Update performance data
                if self.engine:
                    dashboard = self.engine.get_enhanced_dashboard()
                    resonance_report = dashboard.get('enhanced_resonance_report', {})
                    
                    self.root.after(0, self.update_performance_chart, resonance_report)
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Monitoring update error: {e}")
                time.sleep(5)
    
    def update_charts(self, cpu_percent, memory_percent):
        """Update monitoring charts"""
        try:
            # Add new data
            self.cpu_data.append(cpu_percent)
            self.memory_data.append(memory_percent)
            self.time_data.append(datetime.now())
            
            # Keep only last 50 points
            if len(self.cpu_data) > 50:
                self.cpu_data = self.cpu_data[-50:]
                self.memory_data = self.memory_data[-50:]
                self.time_data = self.time_data[-50:]
            
            # Update charts
            self.ax1.clear()
            self.ax1.plot(self.time_data, self.cpu_data, color='#00ff88', linewidth=2)
            self.ax1.set_title('CPU Usage', color='white')
            self.ax1.set_ylabel('CPU %', color='white')
            self.ax1.tick_params(colors='white')
            self.ax1.set_facecolor('#2d2d2d')
            
            self.ax2.clear()
            self.ax2.plot(self.time_data, self.memory_data, color='#0088ff', linewidth=2)
            self.ax2.set_title('Memory Usage', color='white')
            self.ax2.set_ylabel('Memory %', color='white')
            self.ax2.tick_params(colors='white')
            self.ax2.set_facecolor('#2d2d2d')
            
            self.canvas.draw()
            
        except Exception as e:
            print(f"Chart update error: {e}")
    
    def update_performance_chart(self, resonance_report):
        """Update performance chart"""
        try:
            # Extract performance metrics
            current_metrics = resonance_report.get('current_metrics', {})
            
            tactical_resonance = current_metrics.get('avg_tactical_resonance', 0.0)
            crystallization_potential = current_metrics.get('avg_crystallization_potential', 0.0)
            genesis_compliance = current_metrics.get('avg_genesis_protocol_compliance', 0.0)
            autonomous_score = current_metrics.get('avg_autonomous_orchestration_score', 0.0)
            
            # Add to performance data
            self.performance_data['tactical_resonance'].append(tactical_resonance)
            self.performance_data['crystallization_potential'].append(crystallization_potential)
            self.performance_data['genesis_compliance'].append(genesis_compliance)
            self.performance_data['autonomous_score'].append(autonomous_score)
            
            # Keep only last 20 points
            for key in self.performance_data:
                if len(self.performance_data[key]) > 20:
                    self.performance_data[key] = self.performance_data[key][-20:]
            
            # Update performance chart
            self.perf_ax.clear()
            
            x = range(len(self.performance_data['tactical_resonance']))
            self.perf_ax.plot(x, self.performance_data['tactical_resonance'], label='Tactical Resonance', color='#00ff88')
            self.perf_ax.plot(x, self.performance_data['crystallization_potential'], label='Crystallization Potential', color='#0088ff')
            self.perf_ax.plot(x, self.performance_data['genesis_compliance'], label='Genesis Compliance', color='#ff8800')
            self.perf_ax.plot(x, self.performance_data['autonomous_score'], label='Autonomous Score', color='#ff0088')
            
            self.perf_ax.set_title('v3.5-GP Performance Metrics', color='white')
            self.perf_ax.set_ylabel('Score', color='white')
            self.perf_ax.set_xlabel('Time', color='white')
            self.perf_ax.legend()
            self.perf_ax.tick_params(colors='white')
            self.perf_ax.set_facecolor('#2d2d2d')
            
            self.perf_canvas.draw()
            
        except Exception as e:
            print(f"Performance chart update error: {e}")
    
    def run_validation(self):
        """Run validation"""
        try:
            self.test_results_text.delete(1.0, tk.END)
            self.test_results_text.insert(tk.END, "Running validation...\n")
            
            # Run validation in thread
            def validation_thread():
                try:
                    validation_results = run_sandbox_validation()
                    
                    # Update UI
                    self.root.after(0, self.update_validation_results, validation_results)
                    
                except Exception as e:
                    self.root.after(0, lambda: self.test_results_text.insert(tk.END, f"Validation error: {e}\n"))
            
            threading.Thread(target=validation_thread, daemon=True).start()
            
        except Exception as e:
            self.test_results_text.insert(tk.END, f"Error: {e}\n")
    
    def update_validation_results(self, validation_results):
        """Update validation results display"""
        try:
            # Update score
            overall_score = validation_results.get('overall_score', 0.0)
            self.validation_score_label.configure(text=f"{overall_score:.2f}")
            
            # Update test results
            self.test_results_text.delete(1.0, tk.END)
            self.test_results_text.insert(tk.END, f"Validation Status: {validation_results.get('validation_status', 'Unknown')}\n")
            self.test_results_text.insert(tk.END, f"Overall Score: {overall_score:.2f}\n")
            self.test_results_text.insert(tk.END, f"Deployment Ready: {validation_results.get('deployment_ready', False)}\n\n")
            
            # Test results
            self.test_results_text.insert(tk.END, "Test Results:\n")
            for test_name, test_result in validation_results.get('tests', {}).items():
                status = test_result.get('status', 'unknown')
                score = test_result.get('score', 0.0)
                self.test_results_text.insert(tk.END, f"  {test_name}: {status} (score: {score:.2f})\n")
            
        except Exception as e:
            self.test_results_text.insert(tk.END, f"Error updating validation results: {e}\n")
    
    def refresh_tools(self):
        """Refresh tools data"""
        self.load_tools_data()
    
    def export_report(self):
        """Export dashboard report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'tools_data': self.tools_data,
                'validation_data': self.validation_data,
                'monitoring_data': self.monitoring_data
            }
            
            report_file = f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.test_results_text.insert(tk.END, f"Report exported to: {report_file}\n")
            
        except Exception as e:
            self.test_results_text.insert(tk.END, f"Export error: {e}\n")
    
    def deploy_to_production(self):
        """Deploy to production"""
        try:
            self.test_results_text.insert(tk.END, "Starting deployment to production...\n")
            
            # Run deployment in thread
            def deployment_thread():
                try:
                    from deployment.safe_deployer import run_safe_deployment
                    deployment_results = run_safe_deployment()
                    
                    # Update UI
                    self.root.after(0, self.update_deployment_results, deployment_results)
                    
                except Exception as e:
                    self.root.after(0, lambda: self.test_results_text.insert(tk.END, f"Deployment error: {e}\n"))
            
            threading.Thread(target=deployment_thread, daemon=True).start()
            
        except Exception as e:
            self.test_results_text.insert(tk.END, f"Deployment error: {e}\n")
    
    def update_deployment_results(self, deployment_results):
        """Update deployment results"""
        try:
            status = deployment_results.get('deployment_status', 'unknown')
            self.test_results_text.insert(tk.END, f"Deployment Status: {status}\n")
            
            if status == 'success':
                self.test_results_text.insert(tk.END, "✅ Deployment completed successfully!\n")
            else:
                self.test_results_text.insert(tk.END, f"❌ Deployment failed: {deployment_results.get('error', 'Unknown error')}\n")
            
        except Exception as e:
            self.test_results_text.insert(tk.END, f"Error updating deployment results: {e}\n")
    
    def run(self):
        """Run the dashboard"""
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        dashboard = ToolsDashboard()
        dashboard.run()
    except Exception as e:
        print(f"Dashboard error: {e}")


if __name__ == "__main__":
    main()
