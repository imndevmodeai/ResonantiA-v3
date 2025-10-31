#!/usr/bin/env python3
"""
VCD Visualization Generator for ARCH_E_GENIUS_WORKFLOW
Creates comprehensive visualization of all 11 phases and their data
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class VCDVisualizationGenerator:
    def __init__(self, vcd_data_file: str):
        self.vcd_data_file = vcd_data_file
        with open(vcd_data_file, 'r') as f:
            self.vcd_data = json.load(f)
    
    def generate_phase_overview(self) -> str:
        """Generate overview of all 11 phases"""
        phases = self.vcd_data["workflow"]["phases"]
        phase_summary = self.vcd_data["phase_summary"]
        
        overview = "🧠 ARCH_E_GENIUS_WORKFLOW - COMPLETE PHASE OVERVIEW\n"
        overview += "=" * 80 + "\n\n"
        
        for i, phase_id in enumerate(phases, 1):
            phase_info = phase_summary[phase_id]
            status_icon = "✅" if phase_info["execution_status"] == "completed" else "⏳"
            
            overview += f"{i:2d}. {status_icon} {phase_id}\n"
            overview += f"    Action: {phase_info['action_type']}\n"
            overview += f"    Description: {phase_info['description']}\n"
            overview += f"    Status: {phase_info['execution_status']}\n"
            overview += f"    Logs: {phase_info['log_count']} entries\n"
            if phase_info['start_time']:
                overview += f"    Started: {phase_info['start_time']}\n"
            if phase_info['end_time']:
                overview += f"    Completed: {phase_info['end_time']}\n"
            overview += "\n"
            
        return overview
    
    def generate_search_results_summary(self) -> str:
        """Generate summary of all search results"""
        search_results = self.vcd_data["search_results"]
        
        summary = "🔍 FEDERATED SEARCH RESULTS SUMMARY\n"
        summary += "=" * 50 + "\n\n"
        
        total_results = 0
        for agent_type, results in search_results.items():
            agent_total = sum(r["result_count"] for r in results)
            total_results += agent_total
            
            summary += f"📡 {agent_type.upper()} Agent:\n"
            summary += f"   Total Results: {agent_total}\n"
            summary += f"   Queries Executed: {len(results)}\n"
            for result in results:
                if result["timestamp"]:
                    summary += f"   - {result['timestamp']}: {result['result_count']} results\n"
            summary += "\n"
            
        summary += f"🎯 TOTAL SEARCH RESULTS ACROSS ALL AGENTS: {total_results}\n\n"
        return summary
    
    def generate_causal_inference_summary(self) -> str:
        """Generate summary of causal inference analysis"""
        causal_data = self.vcd_data["causal_inference"]
        
        summary = "🔬 CAUSAL INFERENCE ANALYSIS SUMMARY\n"
        summary += "=" * 50 + "\n\n"
        
        summary += f"📊 Hypotheses Generated: {len(causal_data['hypotheses'])}\n"
        summary += f"🔍 Evidence Gatherings: {len(causal_data['evidence'])}\n\n"
        
        if causal_data['hypotheses']:
            summary += "🎯 KEY HYPOTHESES:\n"
            for i, hypothesis in enumerate(causal_data['hypotheses'][:3], 1):
                summary += f"   {i}. {hypothesis[:100]}...\n"
            summary += "\n"
            
        return summary
    
    def generate_abm_simulation_summary(self) -> str:
        """Generate summary of ABM simulation"""
        abm_data = self.vcd_data["abm_simulation"]
        
        summary = "🤖 AGENT-BASED MODELING SIMULATION SUMMARY\n"
        summary += "=" * 50 + "\n\n"
        
        summary += f"👥 Agents Modeled: {len(abm_data['agents'])}\n"
        for agent in abm_data['agents']:
            summary += f"   - {agent}\n"
        summary += f"\n🌍 Environment: {abm_data['environment']}\n"
        summary += f"📈 Simulation Status: {abm_data.get('simulation_status', 'pending')}\n"
        
        if abm_data['simulation_results']:
            summary += "\n🎯 Key Results:\n"
            for result in abm_data['simulation_results']:
                summary += f"   - {result}\n"
                
        summary += "\n"
        return summary
    
    def generate_cfp_comparison_summary(self) -> str:
        """Generate summary of CFP comparison"""
        cfp_data = self.vcd_data["cfp_comparison"]
        
        summary = "⚡ COMPARATIVE FLUXUAL PROCESSING SUMMARY\n"
        summary += "=" * 50 + "\n\n"
        
        summary += f"📊 System A: {cfp_data['system_a']}\n"
        summary += f"📊 System B: {cfp_data['system_b']}\n\n"
        
        summary += "🔍 Observables Analyzed:\n"
        for observable in cfp_data['observables']:
            summary += f"   - {observable}\n"
            
        summary += f"\n📈 Comparison Status: {cfp_data.get('comparison_status', 'pending')}\n"
        
        if cfp_data['comparison_results']:
            summary += "\n🎯 Key Findings:\n"
            for result in cfp_data['comparison_results']:
                summary += f"   - {result}\n"
                
        summary += "\n"
        return summary
    
    def generate_execution_timeline(self) -> str:
        """Generate execution timeline"""
        execution_logs = self.vcd_data["execution_logs"]
        
        timeline = "⏰ EXECUTION TIMELINE\n"
        timeline += "=" * 30 + "\n\n"
        
        # Sort phases by start time
        phases_with_times = []
        for phase_id, logs in execution_logs.items():
            if logs.get("start_time"):
                phases_with_times.append((phase_id, logs["start_time"], logs.get("end_time")))
                
        phases_with_times.sort(key=lambda x: x[1])
        
        for phase_id, start_time, end_time in phases_with_times:
            timeline += f"🕐 {start_time} - {phase_id}\n"
            if end_time:
                timeline += f"   ✅ Completed: {end_time}\n"
            else:
                timeline += f"   ⏳ In Progress\n"
            timeline += "\n"
            
        return timeline
    
    def generate_complete_vcd_report(self) -> str:
        """Generate complete VCD visualization report"""
        report = ""
        report += self.generate_phase_overview()
        report += self.generate_search_results_summary()
        report += self.generate_causal_inference_summary()
        report += self.generate_abm_simulation_summary()
        report += self.generate_cfp_comparison_summary()
        report += self.generate_execution_timeline()
        
        # Add metadata
        metadata = self.vcd_data["metadata"]
        report += "📋 METADATA\n"
        report += "=" * 20 + "\n"
        report += f"Analysis Type: {metadata['analysis_type']}\n"
        report += f"Extraction Time: {metadata['extraction_timestamp']}\n"
        report += f"Project Root: {metadata['project_root']}\n"
        
        return report
    
    def save_vcd_report(self, output_file: str = None):
        """Save VCD report to file"""
        if not output_file:
            output_file = os.path.join(os.path.dirname(self.vcd_data_file), f"vcd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
        report = self.generate_complete_vcd_report()
        
        with open(output_file, 'w') as f:
            f.write(report)
            
        print(f"📊 VCD Report saved to: {output_file}")
        return output_file

def main():
    vcd_data_file = "/media/newbu/3626C55326C514B1/Happier/outputs/vcd_data_20251022_174826.json"
    
    if not os.path.exists(vcd_data_file):
        print(f"❌ VCD data file not found: {vcd_data_file}")
        return
        
    print("🎨 Generating VCD Visualization Report...")
    generator = VCDVisualizationGenerator(vcd_data_file)
    
    # Generate and display report
    report = generator.generate_complete_vcd_report()
    print("\n" + report)
    
    # Save report to file
    report_file = generator.save_vcd_report()
    
    print(f"\n🌐 VCD Visualization Complete!")
    print(f"📁 Data File: {vcd_data_file}")
    print(f"📊 Report File: {report_file}")
    print(f"🎯 All 11 phases of ARCH_E_GENIUS_WORKFLOW are now visible and documented!")

if __name__ == "__main__":
    main()


