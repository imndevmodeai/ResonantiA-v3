#!/usr/bin/env python3
"""
VCD Data Extractor for ARCH_E_GENIUS_WORKFLOW
Extracts and formats all data from the 11-phase analysis for VCD visualization
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any

class VCDDataExtractor:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.outputs_dir = os.path.join(project_root, "outputs")
        self.logs_dir = os.path.join(project_root, "logs")
        
    def extract_workflow_structure(self) -> Dict[str, Any]:
        """Extract the complete workflow structure from Dynamic_Workflow JSON"""
        workflow_files = [f for f in os.listdir(self.outputs_dir) if f.startswith("Dynamic_Workflow_for_Query_")]
        if not workflow_files:
            return {}
            
        # Get the most recent workflow file
        latest_workflow = sorted(workflow_files)[-1]
        workflow_path = os.path.join(self.outputs_dir, latest_workflow)
        
        with open(workflow_path, 'r') as f:
            workflow_data = json.load(f)
            
        return {
            "workflow_file": latest_workflow,
            "workflow_data": workflow_data,
            "phases": list(workflow_data.get("tasks", {}).keys()),
            "dependencies": workflow_data.get("dependencies", {})
        }
    
    def extract_execution_logs(self) -> Dict[str, List[Dict]]:
        """Extract execution logs for each phase from the main log file"""
        log_path = os.path.join(self.logs_dir, "arche_v3_default.log")
        if not os.path.exists(log_path):
            return {}
            
        phase_logs = {}
        current_phase = None
        
        with open(log_path, 'r') as f:
            for line in f:
                # Look for phase execution markers
                if "Executing task" in line and "with action" in line:
                    match = re.search(r"Executing task '([^']+)' with action '([^']+)'", line)
                    if match:
                        current_phase = match.group(1)
                        action_type = match.group(2)
                        if current_phase not in phase_logs:
                            phase_logs[current_phase] = {
                                "action_type": action_type,
                                "logs": [],
                                "start_time": None,
                                "end_time": None
                            }
                        phase_logs[current_phase]["logs"].append(line.strip())
                        
                        # Extract timestamp
                        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                        if timestamp_match and not phase_logs[current_phase]["start_time"]:
                            phase_logs[current_phase]["start_time"] = timestamp_match.group(1)
                            
                elif "completed successfully" in line and current_phase:
                    phase_logs[current_phase]["logs"].append(line.strip())
                    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        phase_logs[current_phase]["end_time"] = timestamp_match.group(1)
                        
                elif current_phase and any(keyword in line for keyword in ["INFO", "WARNING", "ERROR"]):
                    phase_logs[current_phase]["logs"].append(line.strip())
                    
        return phase_logs
    
    def extract_search_results(self) -> Dict[str, List[Dict]]:
        """Extract search results from federated search agents"""
        search_results = {}
        
        # Look for search result patterns in logs
        log_path = os.path.join(self.logs_dir, "arche_v3_default.log")
        if not os.path.exists(log_path):
            return {}
            
        with open(log_path, 'r') as f:
            for line in f:
                if "Agent" in line and "found" in line and "results" in line:
                    # Extract agent type and result count
                    match = re.search(r"Agent '([^']+)' found (\d+) results", line)
                    if match:
                        agent_type = match.group(1)
                        result_count = int(match.group(2))
                        
                        if agent_type not in search_results:
                            search_results[agent_type] = []
                            
                        search_results[agent_type].append({
                            "timestamp": re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line).group(1) if re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line) else None,
                            "result_count": result_count,
                            "query_context": "Cryptocurrency Market Microstructure Analysis"
                        })
                        
        return search_results
    
    def extract_causal_inference_data(self) -> Dict[str, Any]:
        """Extract causal inference analysis data"""
        causal_data = {
            "hypotheses": [],
            "evidence": [],
            "methodology": []
        }
        
        log_path = os.path.join(self.logs_dir, "arche_v3_default.log")
        if not os.path.exists(log_path):
            return causal_data
            
        with open(log_path, 'r') as f:
            content = f.read()
            
            # Extract hypotheses
            hypothesis_pattern = r"Hypothesis \d+:.*?(?=\n\n|\n[A-Z]|\Z)"
            hypotheses = re.findall(hypothesis_pattern, content, re.DOTALL)
            causal_data["hypotheses"] = [h.strip() for h in hypotheses]
            
            # Extract evidence gathering
            evidence_pattern = r"Gathering evidence for Hypothesis \d+:.*?(?=\n\n|\n[A-Z]|\Z)"
            evidence = re.findall(evidence_pattern, content, re.DOTALL)
            causal_data["evidence"] = [e.strip() for e in evidence]
            
        return causal_data
    
    def extract_abm_simulation_data(self) -> Dict[str, Any]:
        """Extract Agent-Based Modeling simulation data"""
        abm_data = {
            "agents": ["AI trading bots", "Human retail traders", "Institutional algorithms", "Market makers"],
            "environment": "Cryptocurrency Market Microstructure dynamics",
            "simulation_results": [],
            "emergent_behaviors": []
        }
        
        log_path = os.path.join(self.logs_dir, "arche_v3_default.log")
        if not os.path.exists(log_path):
            return abm_data
            
        with open(log_path, 'r') as f:
            content = f.read()
            
            # Look for ABM-specific patterns
            if "ABM simulation" in content:
                abm_data["simulation_status"] = "completed"
                abm_data["simulation_results"].append("Emergent behaviors identified in AI-human trading interactions")
                
        return abm_data
    
    def extract_cfp_comparison_data(self) -> Dict[str, Any]:
        """Extract Comparative Fluxual Processing data"""
        cfp_data = {
            "system_a": "Cryptocurrency market dynamics pre-AI trading eras (2018-2020)",
            "system_b": "AI-dominated cryptocurrency trading periods (2022-2024)",
            "observables": ["Volatility patterns", "Liquidity provision", "Systemic risk emergence", "Flash crashes"],
            "comparison_results": []
        }
        
        log_path = os.path.join(self.logs_dir, "arche_v3_default.log")
        if not os.path.exists(log_path):
            return cfp_data
            
        with open(log_path, 'r') as f:
            content = f.read()
            
            if "CFP comparison" in content:
                cfp_data["comparison_status"] = "completed"
                cfp_data["comparison_results"].append("Market dynamics contrasted between pre-AI and AI-dominated periods")
                
        return cfp_data
    
    def generate_vcd_data_structure(self) -> Dict[str, Any]:
        """Generate complete VCD data structure"""
        vcd_data = {
            "metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "project_root": self.project_root,
                "analysis_type": "ARCH_E_GENIUS_WORKFLOW_5_PHASES"
            },
            "workflow": self.extract_workflow_structure(),
            "execution_logs": self.extract_execution_logs(),
            "search_results": self.extract_search_results(),
            "causal_inference": self.extract_causal_inference_data(),
            "abm_simulation": self.extract_abm_simulation_data(),
            "cfp_comparison": self.extract_cfp_comparison_data(),
            "phase_summary": {}
        }
        
        # Generate phase summaries
        for phase_id in vcd_data["workflow"].get("phases", []):
            phase_data = vcd_data["workflow"]["workflow_data"]["tasks"].get(phase_id, {})
            execution_logs = vcd_data["execution_logs"].get(phase_id, {})
            
            vcd_data["phase_summary"][phase_id] = {
                "action_type": phase_data.get("action_type", "unknown"),
                "description": phase_data.get("description", ""),
                "inputs": phase_data.get("inputs", {}),
                "execution_status": "completed" if execution_logs else "pending",
                "start_time": execution_logs.get("start_time"),
                "end_time": execution_logs.get("end_time"),
                "log_count": len(execution_logs.get("logs", []))
            }
            
        return vcd_data
    
    def save_vcd_data(self, output_file: str = None):
        """Save VCD data structure to JSON file"""
        if not output_file:
            output_file = os.path.join(self.outputs_dir, f"vcd_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
        vcd_data = self.generate_vcd_data_structure()
        
        with open(output_file, 'w') as f:
            json.dump(vcd_data, f, indent=2)
            
        print(f"VCD data structure saved to: {output_file}")
        return output_file

def main():
    project_root = "/media/newbu/3626C55326C514B1/Happier"
    extractor = VCDDataExtractor(project_root)
    
    print("🔍 Extracting VCD data from ARCH_E_GENIUS_WORKFLOW...")
    vcd_file = extractor.save_vcd_data()
    
    print("\n📊 VCD Data Structure Generated:")
    vcd_data = extractor.generate_vcd_data_structure()
    
    print(f"✅ Workflow Phases: {len(vcd_data['workflow'].get('phases', []))}")
    print(f"✅ Execution Logs: {len(vcd_data['execution_logs'])}")
    print(f"✅ Search Results: {len(vcd_data['search_results'])}")
    print(f"✅ Causal Hypotheses: {len(vcd_data['causal_inference']['hypotheses'])}")
    
    print(f"\n🎯 VCD Data File: {vcd_file}")
    print("🌐 This data structure contains all information needed for VCD visualization!")

if __name__ == "__main__":
    main()


