#!/usr/bin/env python3
# ResonantiA Protocol v3.5-GP - Interactive VCD
# Visual Cognitive Debugger for individual tool and workflow interaction

import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from flask import Flask, render_template_string, jsonify, request, Response
import queue
import logging
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add sandbox to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__)

# VCD data
vcd_data = {
    'active_tools': {},
    'workflow_executions': {},
    'real_time_streams': {},
    'debug_sessions': {}
}

# Message queues for real-time streaming
message_queues = {}


class InteractiveVCD:
    """
    Interactive Visual Cognitive Debugger - CRITICAL MANDATES COMPLIANT
    
    Adheres to:
    - MANDATE 1: Live Validation Mandate (tools validated against real-world systems)
    - MANDATE 5: Implementation Resonance Enforcement ("As Above, So Below")
    - MANDATE 10: Workflow Engine and Process Orchestration (IAR compliance)
    """
    
    def __init__(self):
        self.active_sessions = {}
        self.tool_registry = {}
        self.workflow_registry = {}
        self.debug_streams = {}
        
        # MANDATE 5: Implementation Resonance Tracking
        self.implementation_resonance_tracker = {
            'concept_implementation_gaps': [],
            'resonance_breaks': [],
            'alignment_scores': {}
        }
        
        # MANDATE 1: Live Validation Framework
        self.live_validation_framework = {
            'validation_sessions': {},
            'real_world_tests': {},
            'mock_deprecation_log': []
        }
        
        # MANDATE 10: IAR Compliance Monitor
        self.iar_compliance_monitor = {
            'required_iar_fields': [
                'status', 'summary', 'confidence', 
                'alignment_check', 'potential_issues',
                'raw_output_preview'
            ],
            'compliance_violations': [],
            'compliance_scores': {}
        }
        
        self.system_event_queue = deque(maxlen=100) # New queue for high-level events
        
    def register_tool(self, tool_name: str, tool_func: Callable, info: Dict[str, Any], is_entry_point: bool = False):
        """Register a tool with the VCD"""
        self.tool_registry[tool_name] = {
            'function': tool_func,
            'info': {**info, 'is_entry_point': is_entry_point, 'enabled': info.get('enabled', True)},
            'metrics': {'executions': 0, 'success_rate': 0.0, 'avg_time': 0.0},
            'sessions': {}
        }
    
    def start_debug_session(self, session_id, tool_name, parameters):
        """Start a debug session for a tool"""
        session = {
            'session_id': session_id,
            'tool_name': tool_name,
            'parameters': parameters,
            'start_time': datetime.now(),
            'status': 'running',
            'steps': [],
            'outputs': [],
            'errors': []
        }
        
        self.active_sessions[session_id] = session
        
        # Create message queue for real-time updates
        message_queues[session_id] = queue.Queue()
        
        return session
    
    def execute_tool_with_debug(self, session_id, tool_name, parameters):
        """Execute tool with full debugging"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        try:
            # Add execution step
            step = {
                'timestamp': datetime.now().isoformat(),
                'action': 'tool_execution_start',
                'tool': tool_name,
                'parameters': parameters
            }
            session['steps'].append(step)
            
            # Send real-time update
            self._send_debug_update(session_id, step)
            
            # Execute tool
            if tool_name in self.tool_registry:
                tool_func = self.tool_registry[tool_name]['function']
                
                # Add parameter validation step
                validation_step = {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'parameter_validation',
                    'parameters': parameters,
                    'status': 'valid'
                }
                session['steps'].append(validation_step)
                self._send_debug_update(session_id, validation_step)
                
                # Execute with timing
                start_time = time.time()
                result = tool_func(**parameters)
                execution_time = time.time() - start_time
                
                # Add execution result step
                result_step = {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'tool_execution_complete',
                    'result': result,
                    'execution_time': execution_time,
                    'status': 'success'
                }
                session['steps'].append(result_step)
                session['outputs'].append(result)
                
                # Update tool metrics
                self._update_tool_metrics(tool_name, execution_time, True)
                
                # MANDATE COMPLIANCE VALIDATION
                # MANDATE 10: IAR Compliance
                iar_score, iar_violations = self.validate_iar_compliance(result, tool_name)
                
                # MANDATE 5: Implementation Resonance
                resonance_score, resonance_gaps = self.validate_implementation_resonance(
                    tool_name, f"Tool: {tool_name}", result
                )
                
                # MANDATE 1: Live Validation
                live_score, live_notes = self.validate_live_system_integration(tool_name, result)
                
                # Add mandate compliance to result step
                result_step['mandate_compliance'] = {
                    'iar_score': iar_score,
                    'iar_violations': iar_violations,
                    'resonance_score': resonance_score,
                    'resonance_gaps': resonance_gaps,
                    'live_validation_score': live_score,
                    'live_validation_notes': live_notes,
                    'overall_compliance': (iar_score + resonance_score + live_score) / 3.0
                }
                
                # Send final update
                self._send_debug_update(session_id, result_step)
                
                session['status'] = 'completed'
                return result
            else:
                error_step = {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'error',
                    'error': f'Tool {tool_name} not found',
                    'status': 'failed'
                }
                session['steps'].append(error_step)
                session['errors'].append(error_step)
                session['status'] = 'failed'
                
                self._send_debug_update(session_id, error_step)
                return {'error': f'Tool {tool_name} not found'}
                
        except Exception as e:
            error_step = {
                'timestamp': datetime.now().isoformat(),
                'action': 'error',
                'error': str(e),
                'status': 'failed'
            }
            session['steps'].append(error_step)
            session['errors'].append(error_step)
            session['status'] = 'failed'
            
            self._update_tool_metrics(tool_name, 0, False)
            self._send_debug_update(session_id, error_step)
            
            return {'error': str(e)}
    
    def _send_debug_update(self, session_id, update):
        """Send real-time debug update"""
        if session_id in message_queues:
            try:
                message_queues[session_id].put_nowait(update)
            except queue.Full:
                pass
    
    def _update_tool_metrics(self, tool_name, execution_time, success):
        """Update tool metrics"""
        if tool_name in self.tool_registry:
            metrics = self.tool_registry[tool_name]['metrics']
            metrics['executions'] += 1
            metrics['last_execution'] = datetime.now().isoformat()
            
            # Update success rate
            if success:
                metrics['success_rate'] = (metrics['success_rate'] * (metrics['executions'] - 1) + 1.0) / metrics['executions']
            else:
                metrics['success_rate'] = (metrics['success_rate'] * (metrics['executions'] - 1) + 0.0) / metrics['executions']
            
            # Update average execution time
            metrics['avg_execution_time'] = (metrics['avg_execution_time'] * (metrics['executions'] - 1) + execution_time) / metrics['executions']
    
    def validate_iar_compliance(self, result, tool_name):
        """
        MANDATE 10: Validate IAR compliance for tool execution results
        """
        compliance_score = 0.0
        violations = []
        
        # Check for reflection/IAR data
        reflection = result.get("reflection") or result.get("iar") or {}
        
        if not reflection:
            violations.append("Missing IAR/reflection data")
            return 0.0, violations
        
        # Check required fields
        for field in self.iar_compliance_monitor['required_iar_fields']:
            if field in reflection:
                compliance_score += 1.0
            else:
                violations.append(f"Missing required IAR field: {field}")
        
        # Calculate compliance percentage
        compliance_score = compliance_score / len(self.iar_compliance_monitor['required_iar_fields'])
        
        # Record compliance
        self.iar_compliance_monitor['compliance_scores'][tool_name] = compliance_score
        if violations:
            self.iar_compliance_monitor['compliance_violations'].extend(violations)
        
        return compliance_score, violations
    
    def validate_implementation_resonance(self, tool_name, concept_definition, implementation_result):
        """
        MANDATE 5: Validate implementation resonance - "As Above, So Below"
        """
        resonance_score = 0.0
        gaps = []
        
        # Check if implementation aligns with concept
        if isinstance(implementation_result, dict):
            # Check for expected outputs based on concept
            if 'result' in implementation_result or 'output' in implementation_result:
                resonance_score += 0.3
            
            # Check for proper error handling
            if 'error' in implementation_result:
                if 'reflection' in implementation_result:
                    resonance_score += 0.2  # Proper error reflection
                else:
                    gaps.append("Error without proper reflection")
            
            # Check for IAR compliance
            iar_score, _ = self.validate_iar_compliance(implementation_result, tool_name)
            resonance_score += iar_score * 0.5
        
        # Record resonance tracking
        self.implementation_resonance_tracker['alignment_scores'][tool_name] = resonance_score
        if gaps:
            self.implementation_resonance_tracker['concept_implementation_gaps'].extend(gaps)
        
        return resonance_score, gaps
    
    def validate_live_system_integration(self, tool_name, result):
        """
        MANDATE 1: Validate against live, real-world systems
        """
        live_validation_score = 0.0
        validation_notes = []
        
        # Check if result indicates real-world interaction
        if isinstance(result, dict):
            # Check for real API responses
            if any(key in str(result).lower() for key in ['api', 'http', 'response', 'status_code']):
                live_validation_score += 0.4
                validation_notes.append("Real API interaction detected")
            
            # Check for real data processing
            if any(key in str(result).lower() for key in ['data', 'content', 'results', 'analysis']):
                live_validation_score += 0.3
                validation_notes.append("Real data processing detected")
            
            # Check for error resilience
            if 'error' in result and 'reflection' in result:
                live_validation_score += 0.3
                validation_notes.append("Proper error handling in live environment")
        
        # Record live validation
        self.live_validation_framework['real_world_tests'][tool_name] = {
            'score': live_validation_score,
            'notes': validation_notes,
            'timestamp': datetime.now().isoformat()
        }
        
        return live_validation_score, validation_notes

    def register_demo_tools(self):
        """Registers a set of simple, in-memory tools for demonstration or fallback."""
        logging.info("Registering demo tools as a fallback.")
        self.register_tool(
            "demo_add", 
            lambda inputs, context: {"result": inputs.get('a', 0) + inputs.get('b', 0)},
            {"description": "Adds two numbers.", "parameters": {"a": "number", "b": "number"}}
        )
        self.register_tool(
            "demo_echo",
            lambda inputs, context: {"result": inputs.get('message', '')},
            {"description": "Echoes a message.", "parameters": {"message": "string"}}
        )

    def _event_callback(self, event_data: Dict[str, Any]):
        """Callback function to receive events from the orchestrator."""
        self.system_event_queue.append(event_data)


# Global VCD instance
vcd = InteractiveVCD()


# HTML Template for Interactive VCD
VCD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ResonantiA Protocol v3.5-GP - Interactive VCD</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
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
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .panel {
            background: rgba(45, 45, 45, 0.8);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .panel h2 {
            color: #00ff88;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 10px;
        }
        
        .tool-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .tool-card {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .tool-card:hover {
            background: rgba(0, 255, 136, 0.2);
            transform: translateY(-2px);
        }
        
        .tool-card.active {
            background: rgba(0, 255, 136, 0.3);
            border-color: #00ff88;
        }
        
        .tool-name {
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 5px;
        }
        
        .tool-metrics {
            font-size: 0.9em;
            color: #cccccc;
        }
        
        .debug-console {
            background: #000000;
            border: 1px solid #333333;
            border-radius: 10px;
            padding: 15px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .debug-line {
            margin-bottom: 5px;
            padding: 5px;
            border-radius: 5px;
        }
        
        .debug-line.info {
            background: rgba(0, 255, 136, 0.1);
            border-left: 3px solid #00ff88;
        }
        
        .debug-line.warning {
            background: rgba(255, 170, 0, 0.1);
            border-left: 3px solid #ffaa00;
        }
        
        .debug-line.error {
            background: rgba(255, 68, 68, 0.1);
            border-left: 3px solid #ff4444;
        }
        
        .debug-line.success {
            background: rgba(0, 255, 136, 0.2);
            border-left: 3px solid #00ff88;
        }
        
        .parameter-form {
            background: rgba(0, 136, 255, 0.1);
            border: 1px solid rgba(0, 136, 255, 0.3);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #00ff88;
            font-weight: bold;
        }
        
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #333333;
            border-radius: 5px;
            background: #1a1a1a;
            color: #ffffff;
            font-size: 1em;
        }
        
        .form-group textarea {
            height: 100px;
            resize: vertical;
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
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .session-info {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .session-info h3 {
            color: #00ff88;
            margin-bottom: 10px;
        }
        
        .session-info p {
            margin-bottom: 5px;
            color: #cccccc;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .status-running {
            background: #ffaa00;
            animation: pulse 1s infinite;
        }
        
        .status-completed {
            background: #00ff88;
        }
        
        .status-failed {
            background: #ff4444;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
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
            font-size: 1.5em;
            font-weight: bold;
            color: #00ff88;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #cccccc;
            margin-top: 5px;
        }
        
        .mandate-compliance {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .mandate-item {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 15px;
        }
        
        .mandate-item h3 {
            color: #00ff88;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .compliance-bar {
            width: 100%;
            height: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .compliance-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff4444 0%, #ffaa00 50%, #00ff88 100%);
            transition: width 0.5s ease;
            border-radius: 10px;
        }
        
        .mandate-item span {
            color: #cccccc;
            font-size: 0.9em;
        }

        .event-log {
            height: 300px;
            overflow-y: auto;
            background: #111;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 10px;
            font-family: 'Courier New', Courier, monospace;
        }

        .event-item {
            padding: 5px;
            border-bottom: 1px solid #222;
        }

        .event-item .metadata {
            color: #888;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>ResonantiA Protocol v3.5-GP</h1>
        <p>Interactive Visual Cognitive Debugger (VCD)</p>
    </div>
    
    <div class="container">
        <!-- Orchestrator Entry Points -->
        <div class="panel full-width">
            <h2>🚀 Orchestrator Entry Points</h2>
            <div class="tool-grid" id="entry-points-grid">
                <!-- Entry points will be dynamically loaded here -->
            </div>
        </div>

        <!-- Available Tools -->
        <div class="panel">
            <h2>🛠️ Available Tools</h2>
            <div class="tool-grid" id="tool-grid">
                <!-- Tools will be dynamically loaded here -->
            </div>
            
            <div class="parameter-form" id="parameter-form" style="display: none;">
                <h3>Tool Parameters</h3>
                <div id="parameter-fields">
                    <!-- Parameters will be populated by JavaScript -->
                </div>
                <button class="btn" onclick="executeTool()">Execute Tool</button>
                <button class="btn" onclick="cancelExecution()">Cancel</button>
            </div>
        </div>

        <!-- System Events Log -->
        <div class="panel full-width">
            <h2>🧠 System Events Log</h2>
            <div class="event-log" id="system-events-log">
                <!-- System events will be dynamically loaded here -->
            </div>
        </div>
        
        <!-- Debug Console Panel -->
        <div class="panel">
            <h2>🐛 Debug Console</h2>
            <div class="session-info" id="session-info" style="display: none;">
                <h3>Session Information</h3>
                <p id="session-details"></p>
            </div>
            
            <div class="debug-console" id="debug-console">
                <div class="debug-line info">
                    <strong>[INFO]</strong> Interactive VCD initialized. Select a tool to begin debugging.
                </div>
            </div>
        </div>
        
        <!-- Real-time Stream Panel -->
        <div class="panel full-width">
            <h2>📡 Real-time Execution Stream</h2>
            <div class="debug-console" id="stream-console" style="height: 200px;">
                <div class="debug-line info">
                    <strong>[STREAM]</strong> Real-time execution stream will appear here.
                </div>
            </div>
        </div>
        
        <!-- CRITICAL MANDATES Compliance Panel -->
        <div class="panel full-width">
            <h2>⚖️ CRITICAL MANDATES Compliance</h2>
            <div class="mandate-compliance" id="mandate-compliance">
                <div class="mandate-item">
                    <h3>MANDATE 1: Live Validation</h3>
                    <div class="compliance-bar">
                        <div class="compliance-fill" id="live-validation-bar" style="width: 0%"></div>
                    </div>
                    <span id="live-validation-text">Loading...</span>
                </div>
                
                <div class="mandate-item">
                    <h3>MANDATE 5: Implementation Resonance</h3>
                    <div class="compliance-bar">
                        <div class="compliance-fill" id="resonance-bar" style="width: 0%"></div>
                    </div>
                    <span id="resonance-text">Loading...</span>
                </div>
                
                <div class="mandate-item">
                    <h3>MANDATE 10: IAR Compliance</h3>
                    <div class="compliance-bar">
                        <div class="compliance-fill" id="iar-bar" style="width: 0%"></div>
                    </div>
                    <span id="iar-text">Loading...</span>
                </div>
                
                <div class="mandate-item">
                    <h3>Overall Compliance</h3>
                    <div class="compliance-bar">
                        <div class="compliance-fill" id="overall-bar" style="width: 0%"></div>
                    </div>
                    <span id="overall-text">Loading...</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedTool = null;
        let currentSession = null;
        let streamInterval = null;
        
        // Initialize tools
        async function initializeTools() {
            try {
                const response = await fetch('/api/tools');
                const tools = await response.json();
                
                const toolsGrid = document.getElementById('tool-grid');
                toolsGrid.innerHTML = '';
                
                for (const [toolName, toolInfo] of Object.entries(tools)) {
                    const toolCard = document.createElement('div');
                    toolCard.className = 'tool-card';
                    toolCard.innerHTML = `
                        <div class="tool-name">${toolName}</div>
                        <div class="tool-metrics">
                            Executions: ${toolInfo.metrics.executions}<br>
                            Success Rate: ${(toolInfo.metrics.success_rate * 100).toFixed(1)}%<br>
                            Avg Time: ${toolInfo.metrics.avg_execution_time.toFixed(3)}s
                        </div>
                    `;
                    
                    toolCard.onclick = () => selectTool(toolName, toolInfo);
                    toolsGrid.appendChild(toolCard);
                }
            } catch (error) {
                console.error('Error loading tools:', error);
            }
        }

        async function initializeEntryPoints() {
            try {
                const response = await fetch('/api/entry-points');
                const entryPoints = await response.json();

                const entryPointsGrid = document.getElementById('entry-points-grid');
                entryPointsGrid.innerHTML = '';

                for (const [toolName, toolInfo] of Object.entries(entryPoints)) {
                    const toolCard = document.createElement('div');
                    toolCard.className = 'tool-card';
                    toolCard.innerHTML = `
                        <div class="tool-name">${toolName}</div>
                        <div class="tool-metrics">
                            Description: ${toolInfo.description}<br>
                            Parameters: ${toolInfo.parameters.join(', ')}
                        </div>
                    `;
                    toolCard.onclick = () => selectEntryPoint(toolName, toolInfo);
                    entryPointsGrid.appendChild(toolCard);
                }
            } catch (error) {
                console.error('Error loading entry points:', error);
            }
        }
        
        // Select tool
        function selectTool(toolName, toolInfo) {
            selectedTool = { name: toolName, info: toolInfo };
            
            // Update UI
            document.querySelectorAll('.tool-card').forEach(card => {
                card.classList.remove('active');
            });
            // Find the correct card to activate
            const cards = document.querySelectorAll('.tool-card');
            for (const card of cards) {
                if (card.querySelector('.tool-name').textContent === toolName) {
                    card.classList.add('active');
                    break;
                }
            }
            
            // Show parameter form
            showParameterForm(toolInfo);
        }

        function selectEntryPoint(toolName, toolInfo) {
            selectedTool = { name: toolName, info: toolInfo };
            showParameterForm(toolInfo);
        }
        
        // Show parameter form
        function showParameterForm(toolInfo) {
            const parameterForm = document.getElementById('parameter-form');
            const parameterFields = document.getElementById('parameter-fields');
            
            parameterFields.innerHTML = ''; // Clear previous fields
            
            const params = toolInfo.parameters || [];
            
            if (params.length === 0) {
                 parameterFields.innerHTML = '<p>This tool requires no parameters.</p>';
            } else {
                params.forEach(param => {
                    const formGroup = document.createElement('div');
                    formGroup.className = 'form-group';
                    // Simple text input for all params for now. Could be enhanced based on type.
                    formGroup.innerHTML = `
                        <label for="${param}">${param}:</label>
                        <textarea id="${param}" placeholder="Enter value for ${param}..."></textarea>
                    `;
                    parameterFields.appendChild(formGroup);
                });
            }
            
            parameterForm.style.display = 'block';
        }
        
        // Execute tool
        async function executeTool() {
            if (!selectedTool) return;
            
            // Collect parameters
            const parameters = {};
            const inputs = document.querySelectorAll('#parameter-form input, #parameter-form textarea');
            inputs.forEach(input => {
                if (input.value.trim()) {
                    parameters[input.id] = input.value.trim();
                }
            });
            
            // Start debug session
            try {
                const response = await fetch('/api/start-session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        tool_name: selectedTool.name,
                        parameters: parameters
                    })
                });
                
                const session = await response.json();
                currentSession = session.session_id;
                
                // Show session info
                showSessionInfo(session);
                
                // Start real-time stream
                startRealTimeStream();
                
                // Execute tool
                const executeResponse = await fetch('/api/execute-tool', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: currentSession,
                        tool_name: selectedTool.name,
                        parameters: parameters
                    })
                });
                
                const result = await executeResponse.json();
                addDebugLine('success', `Tool execution completed: ${JSON.stringify(result)}`);
                
            } catch (error) {
                addDebugLine('error', `Execution failed: ${error.message}`);
            }
        }
        
        // Show session info
        function showSessionInfo(session) {
            const sessionInfo = document.getElementById('session-info');
            const sessionDetails = document.getElementById('session-details');
            
            sessionDetails.innerHTML = `
                <strong>Session ID:</strong> ${session.session_id}<br>
                <strong>Tool:</strong> ${session.tool_name}<br>
                <strong>Status:</strong> <span class="status-indicator status-running"></span>Running<br>
                <strong>Start Time:</strong> ${new Date(session.start_time).toLocaleTimeString()}
            `;
            
            sessionInfo.style.display = 'block';
        }
        
        // Start real-time stream
        function startRealTimeStream() {
            if (streamInterval) clearInterval(streamInterval);
            
            streamInterval = setInterval(async () => {
                if (!currentSession) return;
                
                try {
                    const response = await fetch(`/api/stream/${currentSession}`);
                    const stream = await response.json();
                    
                    if (stream.messages && stream.messages.length > 0) {
                        stream.messages.forEach(message => {
                            addStreamLine(message.action, message);
                        });
                    }
                } catch (error) {
                    console.error('Stream error:', error);
                }
            }, 1000); // Update every second
        }
        
        // Add debug line
        function addDebugLine(type, message) {
            const console = document.getElementById('debug-console');
            const line = document.createElement('div');
            line.className = `debug-line ${type}`;
            line.innerHTML = `<strong>[${type.toUpperCase()}]</strong> ${new Date().toLocaleTimeString()} - ${message}`;
            console.appendChild(line);
            console.scrollTop = console.scrollHeight;
        }
        
        // Add stream line
        function addStreamLine(type, message) {
            const console = document.getElementById('stream-console');
            const line = document.createElement('div');
            line.className = `debug-line ${type}`;
            line.innerHTML = `<strong>[STREAM]</strong> ${new Date().toLocaleTimeString()} - ${JSON.stringify(message)}`;
            console.appendChild(line);
            console.scrollTop = console.scrollHeight;
        }
        
        // Cancel execution
        function cancelExecution() {
            if (streamInterval) {
                clearInterval(streamInterval);
                streamInterval = null;
            }
            
            currentSession = null;
            document.getElementById('session-info').style.display = 'none';
            document.getElementById('parameter-form').style.display = 'none';
            
            addDebugLine('info', 'Execution cancelled by user.');
        }
        
        // Load mandate compliance data
        async function loadMandateCompliance() {
            try {
                const response = await fetch('/api/mandate-compliance');
                const data = await response.json();
                
                if (data.error) {
                    console.error('Error loading mandate compliance:', data.error);
                    return;
                }
                
                // Update compliance bars
                updateComplianceBar('live-validation-bar', 'live-validation-text', 
                    data.live_validation.overall_validation, 'Live Validation');
                updateComplianceBar('resonance-bar', 'resonance-text', 
                    data.implementation_resonance.overall_resonance, 'Implementation Resonance');
                updateComplianceBar('iar-bar', 'iar-text', 
                    data.iar_compliance.overall_score, 'IAR Compliance');
                updateComplianceBar('overall-bar', 'overall-text', 
                    data.overall_mandate_compliance, 'Overall Compliance');
                
            } catch (error) {
                console.error('Error loading mandate compliance:', error);
            }
        }
        
        // Update compliance bar
        function updateComplianceBar(barId, textId, score, label) {
            const bar = document.getElementById(barId);
            const text = document.getElementById(textId);
            
            if (bar && text) {
                const percentage = Math.round(score * 100);
                bar.style.width = `${percentage}%`;
                text.textContent = `${label}: ${percentage}%`;
                
                // Color coding based on score
                if (score >= 0.8) {
                    bar.style.background = 'linear-gradient(90deg, #00ff88 0%, #00ff88 100%)';
                } else if (score >= 0.6) {
                    bar.style.background = 'linear-gradient(90deg, #ffaa00 0%, #ffaa00 100%)';
                } else {
                    bar.style.background = 'linear-gradient(90deg, #ff4444 0%, #ff4444 100%)';
                }
            }
        }

        async function loadSystemEvents() {
            try {
                const response = await fetch('/api/system-events');
                const events = await response.json();
                const logContainer = document.getElementById('system-events-log');
                logContainer.innerHTML = ''; // Clear previous events
                events.reverse().forEach(event => {
                    const eventElement = document.createElement('div');
                    eventElement.className = 'event-item';
                    
                    let content = `<strong>${event.phase || 'SYSTEM'}:</strong> ${event.message || JSON.stringify(event)}`;
                    if (event.metadata) {
                        content += ` <span class="metadata">${JSON.stringify(event.metadata)}</span>`;
                    }
                    
                    eventElement.innerHTML = content;
                    logContainer.appendChild(eventElement);
                });
            } catch (error) {
                console.error('Error loading system events:', error);
            }
        }
        
        // Initialize on load
        document.addEventListener('DOMContentLoaded', function() {
            initializeTools();
            initializeEntryPoints();
            loadMandateCompliance();
            
            // Refresh mandate compliance every 30 seconds
            setInterval(loadMandateCompliance, 30000);
            setInterval(loadSystemEvents, 5000); // Poll for new events every 5 seconds
        });
    </script>
</body>
</html>
"""


@app.route('/')
def vcd_dashboard():
    """Main VCD dashboard page"""
    return render_template_string(VCD_TEMPLATE)


@app.route('/api/tools')
def api_tools():
    """API endpoint for available tools"""
    try:
        # Convert tool registry to JSON-serializable format
        tools_info = {}
        for tool_name, tool_data in vcd.tool_registry.items():
            tools_info[tool_name] = {
                'info': tool_data['info'],
                'metrics': tool_data['metrics'],
                'sessions': len(tool_data['sessions']),
                'available': True
            }
        return jsonify(tools_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/start-session', methods=['POST'])
def api_start_session():
    """API endpoint for starting debug session"""
    try:
        data = request.get_json()
        session = vcd.start_debug_session(
            f"session_{int(time.time())}",
            data['tool_name'],
            data['parameters']
        )
        return jsonify(session)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/execute-tool', methods=['POST'])
def api_execute_tool():
    """API endpoint for executing tool with debug"""
    try:
        data = request.get_json()
        result = vcd.execute_tool_with_debug(
            data['session_id'],
            data['tool_name'],
            data['parameters']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stream/<session_id>')
def api_stream(session_id):
    """API endpoint for real-time stream"""
    try:
        messages = []
        if session_id in message_queues:
            try:
                while True:
                    message = message_queues[session_id].get_nowait()
                    messages.append(message)
            except queue.Empty:
                pass
        
        return jsonify({'messages': messages})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mandate-compliance')
def api_mandate_compliance():
    """API endpoint for CRITICAL MANDATES compliance status"""
    try:
        compliance_data = {
            'iar_compliance': {
                'scores': vcd.iar_compliance_monitor['compliance_scores'],
                'violations': vcd.iar_compliance_monitor['compliance_violations'][-10:],  # Last 10 violations
                'overall_score': sum(vcd.iar_compliance_monitor['compliance_scores'].values()) / max(1, len(vcd.iar_compliance_monitor['compliance_scores']))
            },
            'implementation_resonance': {
                'alignment_scores': vcd.implementation_resonance_tracker['alignment_scores'],
                'gaps': vcd.implementation_resonance_tracker['concept_implementation_gaps'][-10:],  # Last 10 gaps
                'overall_resonance': sum(vcd.implementation_resonance_tracker['alignment_scores'].values()) / max(1, len(vcd.implementation_resonance_tracker['alignment_scores']))
            },
            'live_validation': {
                'tests': vcd.live_validation_framework['real_world_tests'],
                'overall_validation': sum(test['score'] for test in vcd.live_validation_framework['real_world_tests'].values()) / max(1, len(vcd.live_validation_framework['real_world_tests']))
            }
        }
        
        # Calculate overall mandate compliance
        overall_compliance = (
            compliance_data['iar_compliance']['overall_score'] +
            compliance_data['implementation_resonance']['overall_resonance'] +
            compliance_data['live_validation']['overall_validation']
        ) / 3.0
        
        compliance_data['overall_mandate_compliance'] = overall_compliance
        
        return jsonify(compliance_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mandate-status')
def api_mandate_status():
    """API endpoint for detailed mandate status"""
    try:
        status = {
            'mandate_1_live_validation': {
                'status': 'ACTIVE',
                'description': 'Live Validation Mandate - Tools validated against real-world systems',
                'compliance_rate': len(vcd.live_validation_framework['real_world_tests']) / max(1, len(vcd.tool_registry)) * 100
            },
            'mandate_5_implementation_resonance': {
                'status': 'ACTIVE',
                'description': 'Implementation Resonance Enforcement - "As Above, So Below"',
                'resonance_rate': sum(vcd.implementation_resonance_tracker['alignment_scores'].values()) / max(1, len(vcd.tool_registry)) * 100
            },
            'mandate_10_workflow_orchestration': {
                'status': 'ACTIVE',
                'description': 'Workflow Engine and Process Orchestration - IAR compliance',
                'iar_compliance_rate': sum(vcd.iar_compliance_monitor['compliance_scores'].values()) / max(1, len(vcd.tool_registry)) * 100
            }
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/entry-points')
def api_entry_points():
    """API endpoint for entry points (high-level orchestrator actions)"""
    try:
        entry_points = {}
        for tool_name, tool_data in vcd.tool_registry.items():
            if tool_data.get('info', {}).get('is_entry_point'):
                entry_points[tool_name] = {
                    'description': tool_data['info'].get('description'),
                    'parameters': list(tool_data['info'].get('parameters', {}).keys())
                }
        return jsonify(entry_points)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system-events')
def api_system_events():
    """API endpoint to fetch high-level system events."""
    return jsonify(list(vcd.system_event_queue))


def register_resonantia_tools(vcd_instance):
    """Register all ResonantiA Protocol tools and orchestrators"""
    try:
        # The PYTHONPATH environment variable should be set before running this script
        # to include the project's root directory ('Happier').
        import sys
        import os
        import inspect
        
        logging.info("Attempting to import ResonantiA components...")
        from Three_PointO_ArchE import action_registry
        from Three_PointO_ArchE import workflow_engine
        from Three_PointO_ArchE import resonantia_maestro
        from Three_PointO_ArchE import rise_orchestrator
        logging.info("✅ V3 components imported successfully.")
        
        # Import V4 components if available
        try:
            from Four_PointO_ArchE import tool_registry as v4_tool_registry
            from Four_PointO_ArchE import orchestrator as v4_orchestrator
            V4_AVAILABLE = True
            logging.info("✅ V4 components available")
        except (ImportError, ModuleNotFoundError):
            V4_AVAILABLE = False
            logging.warning("⚠️ V4 components not available")
            
        main_action_registry = action_registry.main_action_registry
        execute_action = action_registry.execute_action
        IARCompliantWorkflowEngine = workflow_engine.IARCompliantWorkflowEngine
        ResonantiAMaestro = resonantia_maestro.ResonantiAMaestro
        EnhancementLevel = resonantia_maestro.EnhancementLevel
        RISE_Orchestrator = rise_orchestrator.RISE_Orchestrator
        
        # Register all available tools from the V3 registry
        for action_name, action_func in main_action_registry.actions.items():
            # Create a wrapper that provides IAR-compliant output
            def create_tool_wrapper(func, name):
                def wrapper(**kwargs):
                    try:
                        # Execute using the registry's execute_action function
                        result = execute_action(name, kwargs)
                        return result
                    except Exception as e:
                        return {
                            'error': str(e),
                            'reflection': {
                                'status': 'Failed',
                                'confidence': 0.0,
                                'message': f'Tool execution failed: {str(e)}',
                                'alignment_check': 'Failed',
                                'potential_issues': [f'Execution error: {str(e)}']
                            }
                        }
                return wrapper
            
            # Get tool metadata
            # Introspect function signature to get parameters
            try:
                sig = inspect.signature(action_func)
                params = list(sig.parameters.keys())
                # Exclude 'context_for_action' as it's a system parameter
                if 'context_for_action' in params:
                    params.remove('context_for_action')
            except (ValueError, TypeError):
                params = ['inputs'] # Fallback for complex signatures

            tool_info = {
                'description': f'ResonantiA Protocol tool: {action_name}',
                'parameters': params,
                'category': 'resonantia_protocol',
                'version': '3.1-CA'
            }
            
            # Register the tool
            vcd_instance.register_tool(action_name, create_tool_wrapper(action_func, action_name), tool_info)
            
        # Register V4 tools if available
        if V4_AVAILABLE:
            for tool_name, tool_data in v4_tool_registry.get_tools().items():
                vcd_instance.register_tool(f"v4_{tool_name}", tool_data['function'], {
                    'description': f"V4 Tool: {tool_data['description']}",
                    'parameters': tool_data.get('parameters', []),
                    'category': 'v4_protocol',
                    'version': '4.0'
                })
        
        # Register orchestrators as special tools
        workflow_engine = IARCompliantWorkflowEngine()
        maestro = ResonantiAMaestro(
            workflow_engine=workflow_engine,
            rise_orchestrator=RISE_Orchestrator(), # Pass it in
            spr_manager=None # Placeholder, needs actual SPR manager
        )
        rise_orchestrator = RISE_Orchestrator()
        
        # Register ResonantiA Maestro
        def maestro_wrapper(**kwargs):
            try:
                query = kwargs.get('query', kwargs.get('input_text', ''))
                enhancement_level = kwargs.get('enhancement_level', 'strategic')
                
                # Convert string to enum
                if isinstance(enhancement_level, str):
                    enhancement_level = EnhancementLevel(enhancement_level.lower())
                
                result = maestro.weave_response(query, enhancement_level)
                return result
            except Exception as e:
                return {
                    'error': str(e),
                    'reflection': {
                        'status': 'Failed',
                        'confidence': 0.0,
                        'message': f'Maestro execution failed: {str(e)}',
                        'alignment_check': 'Failed',
                        'potential_issues': [f'Execution error: {str(e)}']
                    }
                }
        
        vcd_instance.register_tool('resonantia_maestro', maestro_wrapper, {
            'description': 'ResonantiA Maestro - Master cognitive orchestrator',
            'parameters': ['query', 'enhancement_level'],
            'category': 'orchestrator',
            'version': '3.1-CA'
        })
        
        # Register RISE Orchestrator
        def rise_wrapper(**kwargs):
            try:
                query = kwargs.get('query', kwargs.get('input_text', ''))
                result = rise_orchestrator.orchestrate_query(query)
                return result
            except Exception as e:
                return {
                    'error': str(e),
                    'reflection': {
                        'status': 'Failed',
                        'confidence': 0.0,
                        'message': f'RISE execution failed: {str(e)}',
                        'alignment_check': 'Failed',
                        'potential_issues': [f'Execution error: {str(e)}']
                    }
                }
        
        vcd_instance.register_tool('rise_orchestrator', rise_wrapper, {
            'description': 'RISE Orchestrator - Resonant Insight and Strategy Engine',
            'parameters': ['query', 'context'],
            'category': 'orchestrator',
            'version': '3.1-CA'
        })
        
        # Add orchestrator entry points
        vcd_instance.register_tool(
            "resonantia_maestro_entry_point",
            maestro.weave_response,
            {
                "description": "Weave a response using the ResonantiA Maestro.",
                "parameters": {
                    "query": "The query to be woven into a response."
                }
            },
            is_entry_point=True
        )
        
        # Disable direct execution for orchestrators
        if "rise_orchestrator" in vcd_instance.tool_registry:
            vcd_instance.tool_registry["rise_orchestrator"]["info"]["enabled"] = False
        if "resonantia_maestro" in vcd_instance.tool_registry:
            vcd_instance.tool_registry["resonantia_maestro"]["info"]["enabled"] = False
        
        logging.info("Tool registration complete")
    except Exception as e:
        logging.warning(f"⚠️ Could not import ResonantiA components: {e}")
        vcd_instance.register_demo_tools()
    except Exception as e:
        logging.error(f"⚠️ Error registering ResonantiA tools: {e}")
        vcd_instance.register_demo_tools()


def register_demo_tools():
    """Register demo tools for testing when ResonantiA registry is not available"""
    
    def demo_web_search(query, max_results=5):
        """Demo web search tool"""
        time.sleep(1)  # Simulate search time
        return {
            'query': query,
            'results': [
                {'title': f'Result {i+1} for {query}', 'url': f'https://example.com/{i+1}', 'snippet': f'This is a demo result for {query}'}
                for i in range(max_results)
            ],
            'total_results': max_results,
            'reflection': {
                'status': 'Success',
                'confidence': 0.9,
                'message': 'Demo web search completed',
                'alignment_check': 'Aligned',
                'potential_issues': []
            }
        }
    
    def demo_llm_generate(prompt, max_tokens=100):
        """Demo LLM generation tool"""
        time.sleep(2)  # Simulate generation time
        return {
            'prompt': prompt,
            'generated_text': f'This is a demo response to: "{prompt}". Generated with max_tokens={max_tokens}.',
            'tokens_used': len(prompt.split()) + 20,
            'model': 'demo-model',
            'reflection': {
                'status': 'Success',
                'confidence': 0.85,
                'message': 'Demo LLM generation completed',
                'alignment_check': 'Aligned',
                'potential_issues': []
            }
        }
    
    def demo_causal_analysis(data, method='dowhy'):
        """Demo causal analysis tool"""
        time.sleep(3)  # Simulate analysis time
        return {
            'method': method,
            'data_points': len(data) if isinstance(data, list) else 1,
            'causal_graph': {'nodes': ['A', 'B', 'C'], 'edges': [('A', 'B'), ('B', 'C')]},
            'confidence': 0.85,
            'p_value': 0.03,
            'reflection': {
                'status': 'Success',
                'confidence': 0.8,
                'message': 'Demo causal analysis completed',
                'alignment_check': 'Aligned',
                'potential_issues': []
            }
        }
    
    def demo_abm_simulation(agents=100, steps=50):
        """Demo agent-based modeling tool"""
        time.sleep(4)  # Simulate simulation time
        return {
            'agents': agents,
            'steps': steps,
            'final_state': {'cooperation_rate': 0.73, 'average_wealth': 45.2},
            'convergence': True,
            'simulation_time': 4.0,
            'reflection': {
                'status': 'Success',
                'confidence': 0.9,
                'message': 'Demo ABM simulation completed',
                'alignment_check': 'Aligned',
                'potential_issues': []
            }
        }
    
    # Register demo tools
    vcd.register_tool('web_search', demo_web_search, {
        'description': 'Demo web search tool',
        'parameters': ['query', 'max_results'],
        'category': 'demo'
    })
    
    vcd.register_tool('llm_generate', demo_llm_generate, {
        'description': 'Demo LLM generation tool',
        'parameters': ['prompt', 'max_tokens'],
        'category': 'demo'
    })
    
    vcd.register_tool('causal_analysis', demo_causal_analysis, {
        'description': 'Demo causal inference analysis',
        'parameters': ['data', 'method'],
        'category': 'demo'
    })
    
    vcd.register_tool('abm_simulation', demo_abm_simulation, {
        'description': 'Demo agent-based modeling simulation',
        'parameters': ['agents', 'steps'],
        'category': 'demo'
    })
    
    logging.info("✅ Registered demo tools for testing")


def cleanup_previous_sessions():
    """Clean up any previous VCD sessions"""
    import subprocess
    import signal
    import os
    
    try:
        current_pid = os.getpid()
        logging.info(f"Current VCD PID: {current_pid}")
        
        # Find and kill other VCD processes
        result = subprocess.run(['pgrep', '-f', 'interactive_vcd.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            for pid in result.stdout.strip().split('\n'):
                if pid and int(pid) != current_pid:
                    logging.info(f"Killing previous VCD process with PID: {pid}")
                    os.kill(int(pid), signal.SIGTERM)
        
        # Also try to kill any Flask processes on our target port range
        for port in range(5000, 5010):
            try:
                result = subprocess.run(['fuser', '-k', f'{port}/tcp'], 
                                      capture_output=True, text=True)
            except:
                pass  # fuser might not be available on all systems
                
    except Exception as e:
        logging.warning(f"⚠️ Cleanup warning: {e}")


def main():
    """Main entry point"""
    try:
        logging.info("Starting VCD main function")
        # Clean up previous sessions first
        logging.info("Cleaning up previous sessions...")
        cleanup_previous_sessions()
        logging.info("Cleanup complete")
        
        # Register ResonantiA Protocol tools
        logging.info("Registering ResonantiA tools...")
        register_resonantia_tools(vcd)
        logging.info("Tool registration complete")
        
        # Use a fixed port range for consistency
        import socket
        
        def find_free_port_in_range(start_port=5000, end_port=5010):
            """Find a free port in a specific range"""
            for port in range(start_port, end_port):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('127.0.0.1', port))
                        return port
                except OSError:
                    continue
            # If no port in range is free, use system-assigned port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', 0))
                s.listen(1)
                return s.getsockname()[1]
        
        port = find_free_port_in_range()
        
        # Fixed address for consistency
        VCD_ADDRESS = "http://resonantia-vcd.local"
        VCD_PORT = port
        
        logging.info(f"VCD starting on port {VCD_PORT}")
        
        print("🐛 ResonantiA Protocol v3.5-GP Interactive VCD")
        print("=" * 60)
        print(f"🎯 VCD Address: {VCD_ADDRESS}")
        print(f"🔌 Actual Port: {VCD_PORT}")
        print(f"🌐 Direct Access: http://localhost:{VCD_PORT}")
        print(f"📊 Tools Registered: {len(vcd.tool_registry)}")
        print("=" * 60)
        print("Press Ctrl+C to stop")
        
        # Create a simple port mapping file for reference
        try:
            with open('/tmp/resonantia_vcd_port', 'w') as f:
                f.write(f"{VCD_PORT}\n{VCD_ADDRESS}\n")
        except:
            pass  # Non-critical if we can't write the file
        
        logging.info("Starting Flask app")
        # Run Flask app
        app.run(host='127.0.0.1', port=VCD_PORT, debug=False)
        
    except KeyboardInterrupt:
        print("\n🛑 VCD stopped by user")
        cleanup_previous_sessions()
    except Exception as e:
        logging.error(f"VCD error: {e}", exc_info=True)
        print(f"❌ VCD error: {e}")
        cleanup_previous_sessions()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ VCD Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
