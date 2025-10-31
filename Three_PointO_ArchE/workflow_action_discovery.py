#!/usr/bin/env python3
"""
Workflow and Action Discovery Module
Discovers available workflows and actions, allowing dynamic usage by agents
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class WorkflowActionDiscovery:
    """Discovers and catalogs all available workflows and actions for dynamic use"""
    
    def __init__(self, workflows_dir: str = None, action_registry=None):
        """
        Initialize workflow and action discovery
        
        Args:
            workflows_dir: Directory containing workflow JSON files
            action_registry: ActionRegistry instance to query for available actions
        """
        if workflows_dir is None:
            # Default to Three_PointO_ArchE/workflows
            base_dir = Path(__file__).parent
            workflows_dir = str(base_dir.parent / "workflows")
        
        self.workflows_dir = Path(workflows_dir)
        self.action_registry = action_registry
        self.workflows_catalog = {}
        self.actions_catalog = {}
        
        # Discover and load workflows and actions
        self._discover_workflows()
        self._discover_actions()
        
    def _discover_workflows(self):
        """Discover all available workflow JSON files"""
        logger.info(f"Discovering workflows in: {self.workflows_dir}")
        
        if not self.workflows_dir.exists():
            logger.warning(f"Workflows directory does not exist: {self.workflows_dir}")
            return
        
        for workflow_file in self.workflows_dir.glob("*.json"):
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = json.load(f)
                    
                workflow_name = workflow_data.get('workflow_name') or workflow_file.stem
                
                # Extract key information
                catalog_entry = {
                    'name': workflow_name,
                    'filename': workflow_file.name,
                    'path': str(workflow_file),
                    'description': workflow_data.get('description', ''),
                    'tasks': self._extract_workflow_tasks(workflow_data),
                    'input_parameters': workflow_data.get('input_parameters', {}),
                    'output': workflow_data.get('output', {}),
                    'tags': self._extract_tags(workflow_data)
                }
                
                self.workflows_catalog[workflow_name] = catalog_entry
                logger.debug(f"Discovered workflow: {workflow_name}")
                
            except Exception as e:
                logger.warning(f"Failed to load workflow {workflow_file.name}: {e}")
        
        logger.info(f"Discovered {len(self.workflows_catalog)} workflows")
        
    def _discover_actions(self):
        """Discover all available actions from action registry"""
        if not self.action_registry:
            logger.warning("No action registry provided, cannot discover actions")
            return
        
        try:
            # Get list of registered actions
            actions = self.action_registry.list_actions()
            
            # Get signatures for each action
            signatures = self.action_registry.get_action_signatures()
            
            for action_name in actions:
                signature_info = signatures.get(action_name, {})
                
                self.actions_catalog[action_name] = {
                    'name': action_name,
                    'description': signature_info.get('doc', ''),
                    'parameters': signature_info.get('params', {}),
                    'callable': True
                }
            
            logger.info(f"Discovered {len(self.actions_catalog)} registered actions")
            
        except Exception as e:
            logger.error(f"Failed to discover actions: {e}")
    
    def _extract_workflow_tasks(self, workflow_data: Dict) -> List[Dict[str, Any]]:
        """Extract task information from workflow"""
        tasks = []
        workflow_tasks = workflow_data.get('tasks', {})
        
        for task_name, task_def in workflow_tasks.items():
            tasks.append({
                'task_id': task_name,
                'action_type': task_def.get('action_type', 'unknown'),
                'description': task_def.get('description', ''),
                'inputs': task_def.get('inputs', {}),
                'outputs': task_def.get('outputs', {}),
                'dependencies': task_def.get('dependencies', [])
            })
        
        return tasks
    
    def _extract_tags(self, workflow_data: Dict) -> List[str]:
        """Extract tags from workflow data"""
        tags = []
        
        # Extract from description
        description = workflow_data.get('description', '').lower()
        
        if 'knowledge' in description or 'scaffolding' in description:
            tags.append('knowledge_scaffolding')
        if 'rise' in description or 'resonant' in description:
            tags.append('rise')
        if 'analysis' in description:
            tags.append('analysis')
        if 'search' in description:
            tags.append('search')
        if 'dynamic' in description:
            tags.append('dynamic')
        if 'genesis' in description or 'autopoietic' in description:
            tags.append('autopoietic')
        if 'metamorphosis' in description:
            tags.append('metamorphosis')
        if 'strategy' in description or 'fusion' in description:
            tags.append('strategy')
        if 'vetting' in description:
            tags.append('vetting')
        
        return tags
    
    def list_available_workflows(self) -> List[Dict[str, Any]]:
        """Return list of available workflows with metadata"""
        return list(self.workflows_catalog.values())
    
    def list_available_actions(self) -> List[Dict[str, Any]]:
        """Return list of available actions with metadata"""
        return list(self.actions_catalog.values())
    
    def get_workflow(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get workflow by name"""
        return self.workflows_catalog.get(workflow_name)
    
    def get_action(self, action_name: str) -> Optional[Dict[str, Any]]:
        """Get action by name"""
        return self.actions_catalog.get(action_name)
    
    def search_workflows(self, query: str) -> List[Dict[str, Any]]:
        """Search workflows by query string"""
        query_lower = query.lower()
        results = []
        
        for workflow_name, workflow in self.workflows_catalog.items():
            # Search in name, description, tags
            if (query_lower in workflow_name.lower() or
                query_lower in workflow.get('description', '').lower() or
                any(query_lower in tag for tag in workflow.get('tags', []))):
                results.append(workflow)
        
        return results
    
    def search_actions(self, query: str) -> List[Dict[str, Any]]:
        """Search actions by query string"""
        query_lower = query.lower()
        results = []
        
        for action_name, action in self.actions_catalog.items():
            if (query_lower in action_name.lower() or
                query_lower in action.get('description', '').lower()):
                results.append(action)
        
        return results
    
    def recommend_workflows_for_problem(self, problem_description: str) -> List[Dict[str, Any]]:
        """Recommend workflows based on problem description"""
        recommendations = []
        problem_lower = problem_description.lower()
        
        # Keyword-based recommendations
        keyword_mappings = {
            'knowledge': ['knowledge_scaffolding', 'robust_knowledge_gathering'],
            'research': ['enhanced_search', 'advanced_research_analysis'],
            'search': ['simple_search_test', 'enhanced_search'],
            'strategy': ['strategy_fusion', 'autonomous_spacecraft'],
            'analysis': ['dynamic_analysis', 'asymmetric_warfare_analysis'],
            'quantum': ['quantum_hybrid_ai', 'quantum_drug_discovery'],
            'rise': ['rise_v2_robust'],
            'autopoietic': ['autopoietic_genesis_protocol'],
            'metamorphosis': ['metamorphosis_protocol'],
            'vetting': ['high_stakes_vetting']
        }
        
        for keyword, workflow_keywords in keyword_mappings.items():
            if keyword in problem_lower:
                # Search for matching workflows
                matched = self.search_workflows(keyword)
                for workflow in matched:
                    if workflow not in recommendations:
                        recommendations.append({
                            'workflow': workflow,
                            'match_reason': f"Problem mentions '{keyword}'"
                        })
        
        return recommendations[:5]  # Top 5 recommendations
    
    def get_complete_catalog(self) -> Dict[str, Any]:
        """Return complete catalog of workflows and actions"""
        return {
            'workflows': self.list_available_workflows(),
            'actions': self.list_available_actions(),
            'total_workflows': len(self.workflows_catalog),
            'total_actions': len(self.actions_catalog)
        }
    
    def export_catalog(self, output_path: str):
        """Export catalog to JSON file"""
        catalog = self.get_complete_catalog()
        
        with open(output_path, 'w') as f:
            json.dump(catalog, f, indent=2)
        
        logger.info(f"Catalog exported to: {output_path}")


