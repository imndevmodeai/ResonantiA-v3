#!/usr/bin/env python3
# ResonantiA Protocol v3.5-GP - Web Dashboard
# Web-based dashboard showing all available tools and their status

import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Flask, render_template_string, jsonify, request
import psutil

# Add sandbox to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.enhanced_workflow_engine import create_sandbox_workflow_engine
from validation.sandbox_validator import run_sandbox_validation
from monitoring.sandbox_monitor import create_sandbox_monitor


app = Flask(__name__)

# Dashboard data
tools_data = {}
monitoring_data = {}
validation_data = {}
engine = None
monitor = None


def load_tools_data():
    """Load tools data and check availability"""
    global tools_data, engine
    
    try:
        # Initialize engine
        engine = create_sandbox_workflow_engine()
        
        # Check tool availability
        tools_data = {
            "Core Components": {
                "Enhanced Workflow Engine": check_tool_availability("EnhancedWorkflowEngine"),
                "Enhanced IAR Validator": check_tool_availability("EnhancedIARValidator"),
                "Enhanced Resonance Tracker": check_tool_availability("EnhancedResonanceTracker"),
                "Genesis Protocol": True,  # Always available in v3.5-GP
                "Resonant Corrective Loop": True,  # Always available in v3.5-GP
                "Autonomous Orchestration": True  # Always available in v3.5-GP
            },
            "Analysis Tools": {
                "Causal Inference Tool (DoWhy)": check_import("dowhy"),
                "Agent-Based Modeling (Mesa)": check_import("mesa"),
                "Predictive Modeling": check_import("sklearn"),
                "TSP Solver": check_import("networkx"),
                "Combat ABM": check_import("mesa")
            },
            "Web & Search": {
                "Web Search Tool": check_import("requests"),
                "Enhanced Perception Engine": check_import("selenium"),
                "Google Maps Integration": check_import("googlemaps"),
                "Selenium WebDriver": check_import("selenium"),
                "WebSocket Bridge": check_import("websocket")
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
                "Scalable Framework": check_import("numpy"),
                "Mastermind": True,  # Built-in
                "Vetting Agent": True  # Built-in
            }
        }
        
    except Exception as e:
        print(f"Error loading tools data: {e}")


def check_tool_availability(tool_name):
    """Check if a specific tool is available"""
    try:
        if tool_name == "EnhancedWorkflowEngine":
            return hasattr(engine, 'get_enhanced_dashboard')
        elif tool_name == "EnhancedIARValidator":
            return hasattr(engine, 'iar_validator') and hasattr(engine.iar_validator, 'validate_enhanced_structure')
        elif tool_name == "EnhancedResonanceTracker":
            return hasattr(engine, 'resonance_tracker') and hasattr(engine.resonance_tracker, 'get_enhanced_resonance_report')
        return False
    except:
        return False


def check_import(module_name):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def get_system_metrics():
    """Get current system metrics"""
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available': memory.available / 1024 / 1024 / 1024,  # GB
            'disk_usage': disk.percent,
            'disk_free': disk.free / 1024 / 1024 / 1024  # GB
        }
    except Exception as e:
        return {'error': str(e)}


# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ResonantiA Protocol v3.5-GP - Tools Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(90deg, #00ff88 0%, #0088ff 100%);
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
        }
        
        .header h1 {
            font-size: 2.5em;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .header p {
            font-size: 1.2em;
            margin-top: 10px;
            opacity: 0.9;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(45, 45, 45, 0.8);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .card h2 {
            color: #00ff88;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 10px;
        }
        
        .tool-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .tool-item:last-child {
            border-bottom: none;
        }
        
        .tool-name {
            font-size: 1.1em;
            color: #ffffff;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-left: 10px;
        }
        
        .status-available {
            background: #00ff88;
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        
        .status-unavailable {
            background: #ff4444;
            box-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .metric {
            text-align: center;
            padding: 15px;
            background: rgba(0, 255, 136, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 136, 0.3);
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #00ff88;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #cccccc;
            margin-top: 5px;
        }
        
        .control-panel {
            background: rgba(45, 45, 45, 0.8);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            text-align: center;
        }
        
        .btn {
            background: linear-gradient(45deg, #00ff88, #0088ff);
            color: white;
            border: none;
            padding: 12px 24px;
            margin: 5px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 255, 136, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .status-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.8);
            padding: 10px;
            text-align: center;
            border-top: 1px solid rgba(0, 255, 136, 0.3);
        }
        
        .refresh-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff88;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .validation-results {
            background: rgba(45, 45, 45, 0.8);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .validation-score {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        
        .score-excellent { color: #00ff88; }
        .score-good { color: #0088ff; }
        .score-warning { color: #ffaa00; }
        .score-critical { color: #ff4444; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ResonantiA Protocol v3.5-GP</h1>
        <p>Tools Dashboard - Real-time Monitoring & Validation</p>
    </div>
    
    <div class="container">
        <div class="dashboard-grid">
            <!-- Tools Status -->
            <div class="card">
                <h2>🔧 Core Components</h2>
                <div id="core-tools"></div>
            </div>
            
            <div class="card">
                <h2>📊 Analysis Tools</h2>
                <div id="analysis-tools"></div>
            </div>
            
            <div class="card">
                <h2>🌐 Web & Search</h2>
                <div id="web-tools"></div>
            </div>
            
            <div class="card">
                <h2>🤖 AI & ML</h2>
                <div id="ai-tools"></div>
            </div>
            
            <div class="card">
                <h2>⚙️ System Tools</h2>
                <div id="system-tools"></div>
            </div>
            
            <!-- System Metrics -->
            <div class="card">
                <h2>📈 System Metrics</h2>
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-value" id="cpu-usage">0%</div>
                        <div class="metric-label">CPU Usage</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="memory-usage">0%</div>
                        <div class="metric-label">Memory Usage</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="disk-usage">0%</div>
                        <div class="metric-label">Disk Usage</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Validation Results -->
        <div class="validation-results">
            <h2>✅ Validation Results</h2>
            <div class="validation-score" id="validation-score">0.00</div>
            <div id="validation-details"></div>
        </div>
        
        <!-- Control Panel -->
        <div class="control-panel">
            <h2>🎮 Control Panel</h2>
            <button class="btn" onclick="runValidation()">Run Validation</button>
            <button class="btn" onclick="refreshTools()">Refresh Tools</button>
            <button class="btn" onclick="exportReport()">Export Report</button>
            <button class="btn" onclick="deployToProduction()">Deploy to Production</button>
        </div>
    </div>
    
    <div class="status-bar">
        <span class="refresh-indicator"></span>
        <span id="status-text">Dashboard Active - Last Updated: <span id="last-updated"></span></span>
    </div>
    
    <script>
        // Update tools display
        function updateToolsDisplay(toolsData) {
            const categories = {
                'core-tools': 'Core Components',
                'analysis-tools': 'Analysis Tools',
                'web-tools': 'Web & Search',
                'ai-tools': 'AI & ML',
                'system-tools': 'System Tools'
            };
            
            for (const [containerId, categoryName] of Object.entries(categories)) {
                const container = document.getElementById(containerId);
                container.innerHTML = '';
                
                if (toolsData[categoryName]) {
                    for (const [toolName, isAvailable] of Object.entries(toolsData[categoryName])) {
                        const toolItem = document.createElement('div');
                        toolItem.className = 'tool-item';
                        
                        toolItem.innerHTML = `
                            <span class="tool-name">${toolName}</span>
                            <span class="status-indicator ${isAvailable ? 'status-available' : 'status-unavailable'}"></span>
                        `;
                        
                        container.appendChild(toolItem);
                    }
                }
            }
        }
        
        // Update system metrics
        function updateSystemMetrics(metrics) {
            document.getElementById('cpu-usage').textContent = metrics.cpu_usage.toFixed(1) + '%';
            document.getElementById('memory-usage').textContent = metrics.memory_usage.toFixed(1) + '%';
            document.getElementById('disk-usage').textContent = metrics.disk_usage.toFixed(1) + '%';
        }
        
        // Update validation results
        function updateValidationResults(validationData) {
            const score = validationData.overall_score || 0;
            const scoreElement = document.getElementById('validation-score');
            scoreElement.textContent = score.toFixed(2);
            
            // Set score color
            scoreElement.className = 'validation-score';
            if (score >= 0.9) scoreElement.classList.add('score-excellent');
            else if (score >= 0.7) scoreElement.classList.add('score-good');
            else if (score >= 0.5) scoreElement.classList.add('score-warning');
            else scoreElement.classList.add('score-critical');
            
            // Update validation details
            const detailsElement = document.getElementById('validation-details');
            detailsElement.innerHTML = `
                <p><strong>Status:</strong> ${validationData.validation_status || 'Unknown'}</p>
                <p><strong>Deployment Ready:</strong> ${validationData.deployment_ready ? 'Yes' : 'No'}</p>
            `;
        }
        
        // Update last updated time
        function updateLastUpdated() {
            document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
        }
        
        // Fetch data from server
        async function fetchData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                updateToolsDisplay(data.tools_data);
                updateSystemMetrics(data.system_metrics);
                updateValidationResults(data.validation_data);
                updateLastUpdated();
                
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        
        // Control panel functions
        async function runValidation() {
            try {
                const response = await fetch('/api/validate', { method: 'POST' });
                const result = await response.json();
                alert(`Validation completed! Score: ${result.overall_score.toFixed(2)}`);
                fetchData(); // Refresh data
            } catch (error) {
                alert('Validation failed: ' + error.message);
            }
        }
        
        async function refreshTools() {
            await fetchData();
            alert('Tools refreshed!');
        }
        
        async function exportReport() {
            try {
                const response = await fetch('/api/export');
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'dashboard_report.json';
                a.click();
                window.URL.revokeObjectURL(url);
            } catch (error) {
                alert('Export failed: ' + error.message);
            }
        }
        
        async function deployToProduction() {
            if (confirm('Are you sure you want to deploy to production?')) {
                try {
                    const response = await fetch('/api/deploy', { method: 'POST' });
                    const result = await response.json();
                    alert(`Deployment ${result.deployment_status}!`);
                    fetchData(); // Refresh data
                } catch (error) {
                    alert('Deployment failed: ' + error.message);
                }
            }
        }
        
        // Auto-refresh every 5 seconds
        setInterval(fetchData, 5000);
        
        // Initial load
        fetchData();
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/data')
def api_data():
    """API endpoint for dashboard data"""
    try:
        system_metrics = get_system_metrics()
        
        return jsonify({
            'tools_data': tools_data,
            'system_metrics': system_metrics,
            'validation_data': validation_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/validate', methods=['POST'])
def api_validate():
    """API endpoint for running validation"""
    try:
        validation_results = run_sandbox_validation()
        validation_data.update(validation_results)
        
        return jsonify(validation_results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export')
def api_export():
    """API endpoint for exporting report"""
    try:
        report = {
            'timestamp': datetime.now().isoformat(),
            'tools_data': tools_data,
            'validation_data': validation_data,
            'system_metrics': get_system_metrics()
        }
        
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/deploy', methods=['POST'])
def api_deploy():
    """API endpoint for deployment"""
    try:
        from deployment.safe_deployer import run_safe_deployment
        deployment_results = run_safe_deployment()
        
        return jsonify(deployment_results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main():
    """Main entry point"""
    try:
        # Load initial data
        load_tools_data()
        
        # Start monitoring
        global monitor
        monitor = create_sandbox_monitor()
        monitor.start_monitoring()
        
        print("🌐 ResonantiA Protocol v3.5-GP Web Dashboard")
        print("=" * 60)
        print("Dashboard available at: http://localhost:5000")
        print("Press Ctrl+C to stop")
        
        # Run Flask app on available port
        import socket
        
        def find_free_port():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', 0))
                s.listen(1)
                port = s.getsockname()[1]
            return port
        
        port = find_free_port()
        print(f"🌐 Starting dashboard on port: {port}")
        print(f"📊 Dashboard available at: http://localhost:{port}")
        
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"Dashboard error: {e}")


if __name__ == "__main__":
    main()
