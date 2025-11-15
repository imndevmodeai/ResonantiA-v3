#!/usr/bin/env python3
"""
Comprehensive SPR Mapping Script
Maps all workflows, actions, agents, and orchestrators to SPRs
Creates missing SPRs and documents all connections
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.spr_manager import SPRManager
from Three_PointO_ArchE.pattern_crystallization_engine import PatternCrystallizationEngine

class SPRComponentMapper:
    """Maps all system components to SPRs and creates missing ones"""
    
    def __init__(self):
        self.project_root = project_root
        spr_filepath = self.project_root / "knowledge_graph" / "spr_definitions_tv.json"
        self.spr_manager = SPRManager(str(spr_filepath))
        
        # Initialize crystallization engine (may fail if dependencies missing)
        try:
            self.crystallization_engine = PatternCrystallizationEngine()
        except Exception as e:
            print(f"  ⚠️  PatternCrystallizationEngine not available: {e}")
            self.crystallization_engine = None
        
        # Component collections
        self.workflows: List[Dict[str, Any]] = []
        self.actions: Set[str] = set()
        self.agents: List[Dict[str, Any]] = []
        self.orchestrators: List[Dict[str, Any]] = []
        self.engines: List[Dict[str, Any]] = []
        
        # Mapping results
        self.workflow_spr_map: Dict[str, str] = {}
        self.action_spr_map: Dict[str, str] = {}
        self.agent_spr_map: Dict[str, str] = {}
        self.orchestrator_spr_map: Dict[str, str] = {}
        self.engine_spr_map: Dict[str, str] = {}
        
        # Missing SPRs to create
        self.missing_sprs: List[Dict[str, Any]] = []
        
    def convert_to_guardian_points(self, name: str) -> str:
        """Convert a name to Guardian pointS format"""
        if not name:
            return ""
        
        # Remove special characters, keep alphanumeric and spaces
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        words = cleaned.split()
        
        if not words:
            return ""
        
        # First word: first char uppercase, rest lowercase
        # Last word: first char uppercase, rest lowercase
        # Middle words: all lowercase
        if len(words) == 1:
            word = words[0]
            return word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper()
        
        result = []
        for i, word in enumerate(words):
            if i == 0 or i == len(words) - 1:
                # First and last: capitalize first letter
                result.append(word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper())
            else:
                # Middle: all lowercase
                result.append(word.lower())
        
        return ''.join(result)
    
    def scan_workflows(self):
        """Scan all workflow files"""
        print("📋 Scanning workflows...")
        workflows_dir = self.project_root / "workflows"
        
        if not workflows_dir.exists():
            print(f"  ⚠️  Workflows directory not found: {workflows_dir}")
            return
        
        workflow_files = list(workflows_dir.glob("*.json"))
        print(f"  Found {len(workflow_files)} workflow files")
        
        for wf_file in workflow_files:
            try:
                with open(wf_file, 'r', encoding='utf-8') as f:
                    wf_data = json.load(f)
                    
                wf_name = wf_file.stem
                wf_id = wf_data.get('workflow_id', wf_name) if isinstance(wf_data, dict) else wf_name
                wf_description = wf_data.get('description', '') if isinstance(wf_data, dict) else ''
                
                self.workflows.append({
                    'file': str(wf_file.relative_to(self.project_root)),
                    'name': wf_name,
                    'id': wf_id,
                    'description': wf_description,
                    'data': wf_data if isinstance(wf_data, dict) else {}
                })
            except json.JSONDecodeError as e:
                print(f"  ⚠️  JSON error in {wf_file.name}: {e}")
                # Still add workflow with minimal info
                self.workflows.append({
                    'file': str(wf_file.relative_to(self.project_root)),
                    'name': wf_file.stem,
                    'id': wf_file.stem,
                    'description': f'[JSON Error: {str(e)[:50]}]',
                    'data': {}
                })
            except Exception as e:
                print(f"  ⚠️  Error reading {wf_file.name}: {e}")
    
    def scan_actions(self):
        """Scan all registered actions"""
        print("🔧 Scanning actions...")
        
        # Read action registry
        action_registry_file = self.project_root / "Three_PointO_ArchE" / "action_registry.py"
        
        if action_registry_file.exists():
            with open(action_registry_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all register_action calls
            pattern = r'register_action\(["\']([^"\']+)["\']'
            matches = re.findall(pattern, content)
            self.actions.update(matches)
            
            # Also find action_type in workflow tasks
            for workflow in self.workflows:
                tasks = workflow.get('data', {}).get('tasks', [])
                for task in tasks:
                    if isinstance(task, dict):
                        action_type = task.get('action_type')
                        if action_type:
                            self.actions.add(action_type)
                    elif isinstance(task, str):
                        # Task might be a string reference
                        self.actions.add(task)
        
        print(f"  Found {len(self.actions)} unique actions")
    
    def scan_agents(self):
        """Scan all agent classes"""
        print("🤖 Scanning agents...")
        
        agents_dir = self.project_root / "Three_PointO_ArchE"
        
        # Find all Python files with Agent classes
        for py_file in agents_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find class definitions with Agent in name
                pattern = r'class\s+(\w*Agent\w*)\s*[\(:]'
                matches = re.findall(pattern, content)
                
                for match in matches:
                    if 'Agent' in match:
                        # Try to find docstring or description
                        class_pattern = rf'class\s+{match}\s*[\(:](.*?)(?=class|\Z)'
                        class_match = re.search(class_pattern, content, re.DOTALL)
                        description = ""
                        if class_match:
                            docstring_match = re.search(r'"""(.*?)"""', class_match.group(1), re.DOTALL)
                            if docstring_match:
                                description = docstring_match.group(1).strip()
                        
                        self.agents.append({
                            'name': match,
                            'file': str(py_file.relative_to(self.project_root)),
                            'description': description
                        })
            except Exception as e:
                pass  # Skip files that can't be read
    
    def scan_orchestrators(self):
        """Scan all orchestrator classes"""
        print("🎼 Scanning orchestrators...")
        
        orchestrators_dir = self.project_root / "Three_PointO_ArchE"
        
        for py_file in orchestrators_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find class definitions with Orchestrator in name
                pattern = r'class\s+(\w*Orchestrator\w*)\s*[\(:]'
                matches = re.findall(pattern, content)
                
                for match in matches:
                    if 'Orchestrator' in match:
                        class_pattern = rf'class\s+{match}\s*[\(:](.*?)(?=class|\Z)'
                        class_match = re.search(class_pattern, content, re.DOTALL)
                        description = ""
                        if class_match:
                            docstring_match = re.search(r'"""(.*?)"""', class_match.group(1), re.DOTALL)
                            if docstring_match:
                                description = docstring_match.group(1).strip()
                        
                        self.orchestrators.append({
                            'name': match,
                            'file': str(py_file.relative_to(self.project_root)),
                            'description': description
                        })
            except Exception as e:
                pass
    
    def scan_engines(self):
        """Scan all engine classes"""
        print("⚙️  Scanning engines...")
        
        engines_dir = self.project_root / "Three_PointO_ArchE"
        
        for py_file in engines_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find class definitions with Engine in name
                pattern = r'class\s+(\w*Engine\w*)\s*[\(:]'
                matches = re.findall(pattern, content)
                
                for match in matches:
                    if 'Engine' in match:
                        class_pattern = rf'class\s+{match}\s*[\(:](.*?)(?=class|\Z)'
                        class_match = re.search(class_pattern, content, re.DOTALL)
                        description = ""
                        if class_match:
                            docstring_match = re.search(r'"""(.*?)"""', class_match.group(1), re.DOTALL)
                            if docstring_match:
                                description = docstring_match.group(1).strip()
                        
                        self.engines.append({
                            'name': match,
                            'file': str(py_file.relative_to(self.project_root)),
                            'description': description
                        })
            except Exception as e:
                pass
    
    def map_to_existing_sprs(self):
        """Map components to existing SPRs"""
        print("\n🔗 Mapping components to existing SPRs...")
        
        # Load existing SPRs
        spr_definitions = list(self.spr_manager.sprs.values())
        spr_terms = {spr.get('term', '').lower(): spr.get('spr_id') for spr in spr_definitions if spr.get('term')}
        spr_ids = {spr.get('spr_id'): spr for spr in spr_definitions}
        
        # Map workflows
        for workflow in self.workflows:
            wf_name = workflow['name']
            wf_id = workflow['id']
            
            # Try to find matching SPR
            spr_id = None
            for term, sid in spr_terms.items():
                if term in wf_name.lower() or wf_name.lower() in term:
                    spr_id = sid
                    break
            
            if spr_id:
                self.workflow_spr_map[wf_id] = spr_id
            else:
                # Create new SPR ID
                new_spr_id = self.convert_to_guardian_points(wf_name)
                self.workflow_spr_map[wf_id] = new_spr_id
                self.missing_sprs.append({
                    'type': 'workflow',
                    'component': wf_id,
                    'spr_id': new_spr_id,
                    'name': wf_name,
                    'description': workflow.get('description', '')
                })
        
        # Map actions
        for action in self.actions:
            # Try to find matching SPR
            spr_id = None
            for term, sid in spr_terms.items():
                if term in action.lower() or action.lower() in term:
                    spr_id = sid
                    break
            
            if spr_id:
                self.action_spr_map[action] = spr_id
            else:
                new_spr_id = self.convert_to_guardian_points(action)
                self.action_spr_map[action] = new_spr_id
                self.missing_sprs.append({
                    'type': 'action',
                    'component': action,
                    'spr_id': new_spr_id,
                    'name': action,
                    'description': f"Action: {action}"
                })
        
        # Map agents
        for agent in self.agents:
            agent_name = agent['name']
            spr_id = None
            for term, sid in spr_terms.items():
                if term in agent_name.lower() or agent_name.lower() in term:
                    spr_id = sid
                    break
            
            if spr_id:
                self.agent_spr_map[agent_name] = spr_id
            else:
                new_spr_id = self.convert_to_guardian_points(agent_name)
                self.agent_spr_map[agent_name] = new_spr_id
                self.missing_sprs.append({
                    'type': 'agent',
                    'component': agent_name,
                    'spr_id': new_spr_id,
                    'name': agent_name,
                    'description': agent.get('description', '')
                })
        
        # Map orchestrators
        for orchestrator in self.orchestrators:
            orch_name = orchestrator['name']
            spr_id = None
            for term, sid in spr_terms.items():
                if term in orch_name.lower() or orch_name.lower() in term:
                    spr_id = sid
                    break
            
            if spr_id:
                self.orchestrator_spr_map[orch_name] = spr_id
            else:
                new_spr_id = self.convert_to_guardian_points(orch_name)
                self.orchestrator_spr_map[orch_name] = new_spr_id
                self.missing_sprs.append({
                    'type': 'orchestrator',
                    'component': orch_name,
                    'spr_id': new_spr_id,
                    'name': orch_name,
                    'description': orchestrator.get('description', '')
                })
        
        # Map engines
        for engine in self.engines:
            engine_name = engine['name']
            spr_id = None
            for term, sid in spr_terms.items():
                if term in engine_name.lower() or engine_name.lower() in term:
                    spr_id = sid
                    break
            
            if spr_id:
                self.engine_spr_map[engine_name] = spr_id
            else:
                new_spr_id = self.convert_to_guardian_points(engine_name)
                self.engine_spr_map[engine_name] = new_spr_id
                self.missing_sprs.append({
                    'type': 'engine',
                    'component': engine_name,
                    'spr_id': new_spr_id,
                    'name': engine_name,
                    'description': engine.get('description', '')
                })
    
    def create_missing_sprs(self):
        """Create SPRs for missing components"""
        print(f"\n✨ Creating {len(self.missing_sprs)} missing SPRs...")
        
        created_count = 0
        for missing in self.missing_sprs:
            spr_id = missing['spr_id']
            
            # Check if SPR already exists
            existing = self.spr_manager.sprs.get(spr_id)
            if existing:
                print(f"  ✓ SPR {spr_id} already exists for {missing['component']}")
                continue
            
            # Create SPR definition
            category_map = {
                'workflow': 'ProcessBlueprint',
                'action': 'CognitiveTool',
                'agent': 'Agent',
                'orchestrator': 'Orchestrator',
                'engine': 'Engine'
            }
            
            spr_def = {
                'spr_id': spr_id,
                'term': missing['name'],
                'definition': missing.get('description', f"{missing['type'].title()}: {missing['name']}"),
                'category': category_map.get(missing['type'], 'SystemComponent'),
                'relationships': {
                    'type': missing['type'].title(),
                    'component': missing['component'],
                    'confidence': 'high'
                },
                'blueprint_details': f"Component: {missing['component']}",
                'example_application': f"Used in {missing['type']} operations"
            }
            
            # Generate Zepto compression
            if self.crystallization_engine:
                try:
                    zepto_result = self.crystallization_engine.compress_to_zepto(
                        narrative=missing.get('description', missing['name']),
                        target_compression_ratio=0.1
                    )
                    spr_def['zepto_spr'] = zepto_result.zepto_spr
                    spr_def['symbol_codex'] = {
                        symbol: {
                            'meaning': entry.meaning,
                            'context': entry.context
                        }
                        for symbol, entry in zepto_result.symbol_codex.items()
                    }
                except Exception as e:
                    print(f"  ⚠️  Zepto compression failed for {spr_id}: {e}")
                    spr_def['zepto_spr'] = "Ξ"
                    spr_def['symbol_codex'] = {"Ξ": {"meaning": missing['name'], "context": "Default"}}
            else:
                spr_def['zepto_spr'] = "Ξ"
                spr_def['symbol_codex'] = {"Ξ": {"meaning": missing['name'], "context": "Default"}}
            
            # Add to SPR manager
            success = self.spr_manager.add_spr(spr_def, save_to_file=False)
            if success:
                created_count += 1
                print(f"  ✓ Created SPR {spr_id} for {missing['component']}")
            else:
                print(f"  ⚠️  Failed to create SPR {spr_id} for {missing['component']}")
        
        # Save all SPR definitions at once
        spr_filepath = self.project_root / "knowledge_graph" / "spr_definitions_tv.json"
        with open(spr_filepath, 'w', encoding='utf-8') as f:
            json.dump(list(self.spr_manager.sprs.values()), f, indent=2, ensure_ascii=False)
        print(f"\n  ✅ Created {created_count} new SPRs")
    
    def generate_mapping_report(self):
        """Generate comprehensive mapping report"""
        print("\n📊 Generating mapping report...")
        
        report = {
            'summary': {
                'total_workflows': len(self.workflows),
                'total_actions': len(self.actions),
                'total_agents': len(self.agents),
                'total_orchestrators': len(self.orchestrators),
                'total_engines': len(self.engines),
                'mapped_workflows': len(self.workflow_spr_map),
                'mapped_actions': len(self.action_spr_map),
                'mapped_agents': len(self.agent_spr_map),
                'mapped_orchestrators': len(self.orchestrator_spr_map),
                'mapped_engines': len(self.engine_spr_map)
            },
            'workflow_mappings': self.workflow_spr_map,
            'action_mappings': self.action_spr_map,
            'agent_mappings': self.agent_spr_map,
            'orchestrator_mappings': self.orchestrator_spr_map,
            'engine_mappings': self.engine_spr_map,
            'component_details': {
                'workflows': self.workflows,
                'actions': list(self.actions),
                'agents': self.agents,
                'orchestrators': self.orchestrators,
                'engines': self.engines
            }
        }
        
        # Save report
        report_file = self.project_root / "knowledge_graph" / "spr_component_mapping.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Report saved to {report_file}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 MAPPING SUMMARY")
        print("=" * 70)
        print(f"Workflows:  {len(self.workflows)} total, {len(self.workflow_spr_map)} mapped")
        print(f"Actions:    {len(self.actions)} total, {len(self.action_spr_map)} mapped")
        print(f"Agents:     {len(self.agents)} total, {len(self.agent_spr_map)} mapped")
        print(f"Orchestrators: {len(self.orchestrators)} total, {len(self.orchestrator_spr_map)} mapped")
        print(f"Engines:    {len(self.engines)} total, {len(self.engine_spr_map)} mapped")
        print(f"Missing SPRs created: {len(self.missing_sprs)}")
        print("=" * 70)
    
    def run(self):
        """Execute full mapping process"""
        print("🚀 Starting SPR Component Mapping")
        print("=" * 70)
        
        # Scan all components
        self.scan_workflows()
        self.scan_actions()
        self.scan_agents()
        self.scan_orchestrators()
        self.scan_engines()
        
        # Map to SPRs
        self.map_to_existing_sprs()
        
        # Create missing SPRs
        self.create_missing_sprs()
        
        # Generate report
        self.generate_mapping_report()
        
        print("\n✅ SPR Component Mapping Complete!")

if __name__ == "__main__":
    mapper = SPRComponentMapper()
    mapper.run()

