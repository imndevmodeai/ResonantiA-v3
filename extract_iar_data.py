#!/usr/bin/env python3
"""
ArchE IAR Data Extractor - Comprehensive extraction of all Integrated Action Reflection data
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path

def extract_iar_from_logs():
    """Extract all IAR data from ArchE execution logs"""
    
    print("🔍 ARCH E IAR DATA EXTRACTION")
    print("=" * 50)
    print(f"Extraction started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check all log files
    log_files = [
        "outputs/arche_system.log",
        "logs/arche_system.log",
        "outputs/arche_system.log"
    ]
    
    all_iar_data = {}
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📋 Processing: {log_file}")
            print("-" * 40)
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract IAR patterns
                iar_patterns = [
                    r'IAR[:\s]*({[^}]+})',
                    r'iar[:\s]*({[^}]+})',
                    r'reflection[:\s]*({[^}]+})',
                    r'confidence[:\s]*(\d+\.?\d*)',
                    r'alignment[:\s]*([^,\n]+)',
                    r'status[:\s]*([^,\n]+)',
                    r'summary[:\s]*([^,\n]+)'
                ]
                
                iar_matches = []
                for pattern in iar_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    iar_matches.extend(matches)
                
                if iar_matches:
                    print(f"✅ Found {len(iar_matches)} IAR-related entries")
                    all_iar_data[log_file] = iar_matches
                else:
                    print("❌ No IAR data found")
                    
            except Exception as e:
                print(f"❌ Error reading {log_file}: {e}")
    
    return all_iar_data

def extract_task_details():
    """Extract detailed task execution information"""
    
    print("\n🔧 TASK EXECUTION DETAILS")
    print("=" * 50)
    
    task_details = {}
    
    # Check outputs log for task details
    log_file = "outputs/arche_system.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_task = None
            task_info = {}
            
            for i, line in enumerate(lines):
                # Look for task execution patterns
                if "Executing task" in line:
                    task_match = re.search(r"Executing task '([^']+)'", line)
                    if task_match:
                        current_task = task_match.group(1)
                        task_info = {
                            'start_time': re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line).group(1) if re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line) else 'Unknown',
                            'action_type': 'Unknown',
                            'status': 'Unknown',
                            'duration': 'Unknown',
                            'details': []
                        }
                
                elif "completed successfully" in line and current_task:
                    task_info['status'] = 'Success'
                    task_info['end_time'] = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line).group(1) if re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line) else 'Unknown'
                    task_details[current_task] = task_info
                    current_task = None
                
                elif "ERROR" in line and current_task:
                    task_info['status'] = 'Error'
                    task_info['error'] = line.strip()
                
                elif current_task and line.strip():
                    task_info['details'].append(line.strip())
            
            print(f"✅ Extracted {len(task_details)} task executions")
            
        except Exception as e:
            print(f"❌ Error extracting task details: {e}")
    
    return task_details

def extract_tool_usage():
    """Extract tool usage and performance data"""
    
    print("\n🛠️ TOOL USAGE AND PERFORMANCE")
    print("=" * 50)
    
    tool_data = {}
    
    log_file = "outputs/arche_system.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract tool usage patterns
            tool_patterns = [
                r'(predictive_modeling_tool|PredictiveModelingTool)',
                r'(causal_inference_tool|CausalInferenceTool)',
                r'(knowledge_graph_manager|KnowledgeGraphManager)',
                r'(llm_providers|LLMProvider)',
                r'(code_executor|CodeExecutor)',
                r'(synthesis_tool|SynthesisTool)',
                r'(playbook_orchestrator|PlaybookOrchestrator)'
            ]
            
            for pattern in tool_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    tool_name = pattern.replace('|', '_').replace('(', '').replace(')', '')
                    tool_data[tool_name] = {
                        'usage_count': len(matches),
                        'instances': matches[:5]  # First 5 instances
                    }
            
            print(f"✅ Found {len(tool_data)} tool types")
            
        except Exception as e:
            print(f"❌ Error extracting tool data: {e}")
    
    return tool_data

def extract_workflow_data():
    """Extract workflow execution data"""
    
    print("\n🔄 WORKFLOW EXECUTION DATA")
    print("=" * 50)
    
    workflow_data = {}
    
    log_file = "outputs/arche_system.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract workflow patterns
            workflow_patterns = [
                r'Orchestrating playbook: ([^\s]+)',
                r'Playbook \'([^\']+)\' orchestrated successfully',
                r'Distributed Resonant Corrective Loop',
                r'RISE.*[Mm]ethodology',
                r'protocol_priming',
                r'conceptual_map',
                r'rise_blueprint'
            ]
            
            for pattern in workflow_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    workflow_data[pattern] = {
                        'matches': len(matches),
                        'instances': matches[:3]  # First 3 instances
                    }
            
            print(f"✅ Found {len(workflow_data)} workflow patterns")
            
        except Exception as e:
            print(f"❌ Error extracting workflow data: {e}")
    
    return workflow_data

def main():
    """Main extraction function"""
    
    # Extract all data
    iar_data = extract_iar_from_logs()
    task_details = extract_task_details()
    tool_data = extract_tool_usage()
    workflow_data = extract_workflow_data()
    
    # Display results
    print("\n" + "=" * 50)
    print("📊 COMPREHENSIVE ARCH E DATA SUMMARY")
    print("=" * 50)
    
    print(f"\n🧠 IAR Data Sources: {len(iar_data)}")
    for source, data in iar_data.items():
        print(f"   • {source}: {len(data)} entries")
    
    print(f"\n🔧 Task Executions: {len(task_details)}")
    for task, details in task_details.items():
        print(f"   • {task}: {details['status']} at {details.get('start_time', 'Unknown')}")
    
    print(f"\n🛠️ Tools Used: {len(tool_data)}")
    for tool, data in tool_data.items():
        print(f"   • {tool}: {data['usage_count']} uses")
    
    print(f"\n🔄 Workflow Patterns: {len(workflow_data)}")
    for pattern, data in workflow_data.items():
        print(f"   • {pattern}: {data['matches']} matches")
    
    # Save detailed data
    detailed_data = {
        'iar_data': iar_data,
        'task_details': task_details,
        'tool_data': tool_data,
        'workflow_data': workflow_data,
        'extraction_time': datetime.now().isoformat()
    }
    
    with open('arche_detailed_data.json', 'w') as f:
        json.dump(detailed_data, f, indent=2)
    
    print(f"\n💾 Detailed data saved to: arche_detailed_data.json")
    print("\n🎯 EXTRACTION COMPLETE!")

if __name__ == "__main__":
    main()
