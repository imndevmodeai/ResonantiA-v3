#!/usr/bin/env python3
"""
Specialized Agent with ResonantiA Protocol Expertise
Creates detailed action plans describing which capabilities to use and how
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# Import workflow and action discovery
try:
    from .workflow_action_discovery import WorkflowActionDiscovery
    DISCOVERY_AVAILABLE = True
except ImportError:
    WorkflowActionDiscovery = None
    DISCOVERY_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class SpecializedAgent:
    """Domain expert + ResonantiA Protocol expert that designs action plans"""
    
    domain_expertise: str
    resonantia_capabilities: List[str]
    
    def __init__(self, domain_expertise: str, resonantia_capabilities: List[str], 
                 workflows_dir: str = None, action_registry=None):
        """Initialize with optional workflow and action discovery"""
        self.domain_expertise = domain_expertise
        self.resonantia_capabilities = resonantia_capabilities
        self.discovery = None
        
        if DISCOVERY_AVAILABLE:
            try:
                self.discovery = WorkflowActionDiscovery(
                    workflows_dir=workflows_dir,
                    action_registry=action_registry
                )
                logger.info("Workflow and action discovery enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize discovery: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def generate_action_plan(self, problem: str, available_capabilities: Dict, protocol_knowledge: Dict) -> Dict[str, Any]:
        """
        Generate detailed action plan describing HOW to solve the problem
        using available ResonantiA capabilities
        """
        logger.info(f"Agent generating action plan for: {problem[:100]}...")
        
        # Step 0: Discover relevant workflows and actions
        discovery_results = {}
        if self.discovery:
            discovery_results = self.discover_relevant_workflows_and_actions(problem)
            logger.info(f"Discovery found {len(discovery_results.get('recommended_workflows', []))} workflows and "
                       f"{len(discovery_results.get('recommended_actions', []))} actions")
        
        # Step 1: Analyze problem requirements
        problem_analysis = self._analyze_problem_requirements(problem)
        
        # Step 2: Select optimal capabilities
        selected_capabilities = self._select_capabilities(
            problem_analysis,
            available_capabilities
        )
        
        # Step 3: Design action sequence
        action_sequence = self._design_action_sequence(
            problem_analysis,
            selected_capabilities
        )
        
        # Step 4: Identify parallelization opportunities
        parallel_groups = self._identify_parallel_actions(action_sequence)
        
        # Step 5: Generate custom tool specs if needed
        custom_tools = self._identify_custom_tool_needs(
            problem_analysis,
            available_capabilities
        )
        
        action_plan = {
            'problem_analysis': problem_analysis,
            'selected_capabilities': selected_capabilities,
            'action_sequence': action_sequence,
            'parallel_groups': parallel_groups,
            'custom_tools': custom_tools,
            'discovered_workflows_and_actions': discovery_results,  # NEW: Include discovered items
            'success_criteria': self._define_success_criteria(problem_analysis),
            'reassessment_gates': self._define_reassessment_gates(action_sequence),
            'agent_rationale': self._generate_rationale(
                problem_analysis,
                selected_capabilities,
                action_sequence
            )
        }
        
        logger.info(f"Action plan generated with {len(action_sequence)} phases")
        return action_plan
        
    def _analyze_problem_requirements(self, problem: str) -> Dict[str, Any]:
        """Analyze what the problem requires"""
        problem_lower = problem.lower()
        
        return {
            'domain': self._identify_domain(problem),
            'complexity': self._assess_complexity(problem),
            'key_questions': self._extract_key_questions(problem),
            'required_analyses': self._identify_required_analyses(problem),
            'data_requirements': self._identify_data_requirements(problem),
            'success_metrics': self._define_success_metrics(problem)
        }
        
    def _identify_domain(self, problem: str) -> str:
        """Identify the problem domain"""
        problem_lower = problem.lower()
        
        if any(term in problem_lower for term in ['combat', 'fight', 'battle', 'survival']):
            return 'combat_modeling'
        elif any(term in problem_lower for term in ['truth', 'verify', 'fact', 'claim']):
            return 'truth_verification'
        elif any(term in problem_lower for term in ['strategic', 'planning', 'business']):
            return 'strategic_planning'
        elif any(term in problem_lower for term in ['complex system', 'emergent', 'multi-agent']):
            return 'complex_systems'
        elif any(term in problem_lower for term in ['causal', 'cause', 'effect', 'why']):
            return 'causal_analysis'
        else:
            return 'general_analysis'
            
    def _assess_complexity(self, problem: str) -> float:
        """Assess problem complexity 0-1"""
        indicators = ['multiple', 'complex', 'dynamic', 'emergent', 'simulation', 'modeling']
        complexity_score = sum(1 for ind in indicators if ind in problem.lower()) / len(indicators)
        return min(1.0, 0.3 + complexity_score)
        
    def _extract_key_questions(self, problem: str) -> List[str]:
        """Extract key questions from problem"""
        # Simple extraction - can be enhanced
        questions = []
        for sentence in problem.split('.'):
            if '?' in sentence or 'how' in sentence.lower() or 'what' in sentence.lower():
                questions.append(sentence.strip())
        return questions[:3]  # Limit to 3
        
    def _identify_required_analyses(self, problem: str) -> List[str]:
        """Identify required types of analysis"""
        analyses = []
        problem_lower = problem.lower()
        
        if 'simulation' in problem_lower or 'emergent' in problem_lower or 'agent' in problem_lower:
            analyses.append('ABM')
        if 'compare' in problem_lower or 'trajectory' in problem_lower or 'evolution' in problem_lower:
            analyses.append('CFP')
        if 'causal' in problem_lower or 'cause' in problem_lower or 'effect' in problem_lower:
            analyses.append('CausalInference')
        if 'predict' in problem_lower or 'forecast' in problem_lower or 'future' in problem_lower:
            analyses.append('PredictiveModeling')
        if 'search' in problem_lower or 'find' in problem_lower or 'research' in problem_lower:
            analyses.append('FederatedSearch')
            
        return analyses if analyses else ['general_analysis']
        
    def _identify_data_requirements(self, problem: str) -> List[str]:
        """Identify data requirements"""
        requirements = []
        problem_lower = problem.lower()
        
        if 'historical' in problem_lower or 'time series' in problem_lower:
            requirements.append('historical_data')
        if 'agent' in problem_lower or 'simulation' in problem_lower:
            requirements.append('agent_definitions')
        if 'compare' in problem_lower or 'scenario' in problem_lower:
            requirements.append('state_definitions')
            
        return requirements
        
    def _define_success_metrics(self, problem: str) -> Dict[str, Any]:
        """Define success metrics"""
        return {
            'confidence_threshold': 0.75,
            'completeness_threshold': 0.8,
            'accuracy_threshold': 0.7,
            'requires_validation': True
        }
        
    def _select_capabilities(self, problem_analysis: Dict, available_capabilities: Dict) -> List[Dict]:
        """Select which ResonantiA capabilities to use and WHY"""
        selections = []
        required_analyses = problem_analysis.get('required_analyses', [])
        
        for capability_name, capability_info in available_capabilities.items():
            # Check if this capability is in required analyses
            if any(req.lower() in capability_name.lower() for req in required_analyses):
                relevance_score = 0.9  # High relevance if explicitly required
            else:
                # Assess relevance
                relevance_score = self._assess_capability_relevance(
                    capability_info,
                    problem_analysis
                )
            
            if relevance_score > 0.6:
                selections.append({
                    'capability': capability_name,
                    'tool': capability_info['tool'],
                    'relevance_score': relevance_score,
                    'rationale': self._explain_capability_selection(
                        capability_info,
                        problem_analysis
                    ),
                    'expected_contribution': self._describe_expected_contribution(
                        capability_info,
                        problem_analysis
                    )
                })
        
        return sorted(selections, key=lambda x: x['relevance_score'], reverse=True)
        
    def _assess_capability_relevance(self, capability_info: Dict, problem_analysis: Dict) -> float:
        """Assess how relevant a capability is to the problem"""
        domain = problem_analysis.get('domain', '')
        use_for = capability_info.get('use_for', '').lower()
        
        relevance = 0.0
        
        # Domain-specific matching
        if domain == 'combat_modeling' and 'agent' in use_for:
            relevance = 0.8
        elif domain == 'truth_verification' and 'verification' in use_for:
            relevance = 0.8
        elif domain == 'causal_analysis' and 'causal' in use_for:
            relevance = 0.8
        elif domain == 'complex_systems' and 'emergent' in use_for:
            relevance = 0.8
        else:
            # Generic relevance
            relevance = 0.5
            
        return relevance
        
    def _explain_capability_selection(self, capability_info: Dict, problem_analysis: Dict) -> str:
        """Explain why this capability was selected"""
        use_for = capability_info.get('use_for', '')
        domain = problem_analysis.get('domain', '')
        
        return f"{capability_info.get('name', 'Tool')} is suitable for {domain} because it {use_for}"
        
    def _describe_expected_contribution(self, capability_info: Dict, problem_analysis: Dict) -> str:
        """Describe what this capability will contribute"""
        outputs = capability_info.get('outputs', [])
        return f"Will provide: {', '.join(outputs)}"
        
    def _design_action_sequence(self, problem_analysis: Dict, selected_capabilities: List[Dict]) -> List[Dict]:
        """Design optimal sequence of actions"""
        sequence = []
        
        # Phase 1: Data Collection & Preparation
        sequence.append({
            'phase': 'data_collection',
            'actions': self._plan_data_collection(problem_analysis),
            'dependencies': [],
            'outputs': ['collected_data', 'data_quality_report'],
            'parallel': False
        })
        
        # Phase 2: Core Analysis (may be parallel)
        analysis_actions = []
        for capability in selected_capabilities:
            if capability['capability'] in ['ABM', 'CFP', 'CausalInference', 'PredictiveModeling']:
                analysis_actions.append({
                    'action': f"run_{capability['capability'].lower()}",
                    'tool': capability['tool'],
                    'rationale': capability['rationale'],
                    'inputs': self._define_action_inputs(capability, problem_analysis),
                    'outputs': self._define_action_outputs(capability),
                    'can_parallelize': self._can_parallelize(capability),
                    'reassessment_gate': {
                        'confidence_threshold': 0.75,
                        'on_failure': 'modify_parameters'
                    }
                })
        
        if analysis_actions:
            sequence.append({
                'phase': 'core_analysis',
                'actions': analysis_actions,
                'dependencies': ['data_collection'],
                'parallel': True
            })
        
        # Phase 3: Synthesis & Integration
        sequence.append({
            'phase': 'synthesis',
            'actions': [{
                'action': 'synthesize_results',
                'tool': 'SynthesisEngine',
                'inputs': ['core_analysis_results'],
                'outputs': ['integrated_insights', 'final_answer']
            }],
            'dependencies': ['core_analysis'],
            'parallel': False
        })
        
        return sequence
        
    def _plan_data_collection(self, problem_analysis: Dict) -> List[Dict]:
        """Plan data collection actions"""
        return [{
            'action': 'federated_search',
            'tool': 'SynergisticInquiryOrchestrator',
            'inputs': {'query': problem_analysis.get('key_questions', [])},
            'outputs': ['search_results']
        }]
        
    def _identify_parallel_actions(self, action_sequence: List[Dict]) -> List[List[str]]:
        """Identify which actions can run in parallel"""
        parallel_groups = []
        
        for phase in action_sequence:
            if phase.get('parallel', False):
                action_ids = [action['action'] for action in phase.get('actions', [])]
                if len(action_ids) > 1:
                    parallel_groups.append(action_ids)
                    
        return parallel_groups
        
    def _identify_custom_tool_needs(self, problem_analysis: Dict, available_capabilities: Dict) -> List[Dict]:
        """Identify if custom tools are needed"""
        custom_tools = []
        
        # Placeholder - can be enhanced to detect gaps
        if problem_analysis.get('complexity', 0) > 0.8:
            custom_tools.append({
                'name': 'custom_analysis_tool',
                'description': 'High complexity problem may need custom tool',
                'required': False
            })
            
        return custom_tools
        
    def _define_success_criteria(self, problem_analysis: Dict) -> Dict[str, Any]:
        """Define success criteria for this problem"""
        return {
            'confidence_threshold': 0.75,
            'completeness_threshold': 0.8,
            'validation_required': True,
            'metrics': problem_analysis.get('success_metrics', {})
        }
        
    def _define_reassessment_gates(self, action_sequence: List[Dict]) -> List[Dict]:
        """Define where reassessment gates should be placed"""
        gates = []
        
        for i, phase in enumerate(action_sequence):
            if i > 0:  # Don't gate the first phase
                gates.append({
                    'phase': phase['phase'],
                    'confidence_threshold': 0.75,
                    'action_on_failure': 'modify_parameters'
                })
                
        return gates
        
    def _generate_rationale(self, problem_analysis: Dict, selected_capabilities: List[Dict], action_sequence: List[Dict]) -> Dict[str, Any]:
        """Generate human-readable explanation of the action plan"""
        capability_names = [cap['capability'] for cap in selected_capabilities]
        
        return {
            'problem_understanding': f"This problem requires {problem_analysis['domain']} expertise with complexity {problem_analysis['complexity']:.2f}",
            'capability_justification': f"Selected {len(selected_capabilities)} capabilities: {', '.join(capability_names)}",
            'sequence_rationale': f"Designed {len(action_sequence)}-phase execution: {', '.join([p['phase'] for p in action_sequence])}",
            'expected_outcome': f"Comprehensive analysis providing integrated insights with >{problem_analysis.get('success_metrics', {}).get('confidence_threshold', 0.75)} confidence"
        }
        
    def _define_action_inputs(self, capability: Dict, problem_analysis: Dict) -> Dict[str, Any]:
        """Define inputs for an action"""
        inputs = capability.get('inputs', [])
        return {'inputs': inputs, 'problem_context': problem_analysis}
        
    def _define_action_outputs(self, capability: Dict) -> List[str]:
        """Define outputs for an action"""
        return capability.get('outputs', [])
        
    def _can_parallelize(self, capability: Dict) -> bool:
        """Check if this action can be parallelized"""
        # Analysis tools can typically be parallelized
        if capability['capability'] in ['ABM', 'CFP', 'CausalInference']:
            return True
        return False
    
    def discover_relevant_workflows_and_actions(self, problem_description: str) -> Dict[str, Any]:
        """Discover and recommend relevant workflows and actions for the problem"""
        if not self.discovery:
            return {
                'recommended_workflows': [],
                'recommended_actions': [],
                'discovery_enabled': False
            }
        
        # Get workflow recommendations
        workflow_recommendations = self.discovery.recommend_workflows_for_problem(problem_description)
        
        # Search for relevant actions
        problem_lower = problem_description.lower()
        
        relevant_actions = []
        if 'search' in problem_lower or 'find' in problem_lower or 'research' in problem_lower:
            actions = self.discovery.search_actions('search')
            relevant_actions.extend(actions[:3])
        if 'causal' in problem_lower or 'cause' in problem_lower:
            actions = self.discovery.search_actions('causal')
            relevant_actions.extend(actions[:2])
        if 'simulate' in problem_lower or 'abm' in problem_lower:
            actions = self.discovery.search_actions('abm')
            relevant_actions.extend(actions[:2])
        if 'compare' in problem_lower or 'cfp' in problem_lower:
            actions = self.discovery.search_actions('cfp')
            relevant_actions.extend(actions[:2])
        
        return {
            'recommended_workflows': workflow_recommendations,
            'recommended_actions': relevant_actions,
            'discovery_enabled': True,
            'total_available_workflows': len(self.discovery.workflows_catalog),
            'total_available_actions': len(self.discovery.actions_catalog)
        }
    
    def generate_dynamic_workflow_from_discovered_items(self, problem_description: str, 
                                                         discovery_results: Dict) -> Dict[str, Any]:
        """Generate a workflow using discovered workflows and actions"""
        workflow_steps = []
        
        # Add workflow recommendations
        for rec in discovery_results.get('recommended_workflows', [])[:2]:
            workflow = rec.get('workflow', {})
            workflow_steps.append({
                'step_type': 'workflow',
                'workflow_name': workflow.get('name'),
                'description': f"Execute {workflow.get('name')} workflow",
                'rationale': rec.get('match_reason', ''),
                'file_path': workflow.get('path')
            })
        
        # Add action recommendations
        for action in discovery_results.get('recommended_actions', [])[:5]:
            workflow_steps.append({
                'step_type': 'action',
                'action_name': action.get('name'),
                'description': action.get('description'),
                'parameters': action.get('parameters', {})
            })
        
        return {
            'workflow_name': f"Dynamic Workflow for {problem_description[:50]}",
            'description': "Auto-generated workflow using discovered items",
            'steps': workflow_steps,
            'total_steps': len(workflow_steps),
            'includes_workflows': any(s['step_type'] == 'workflow' for s in workflow_steps),
            'includes_actions': any(s['step_type'] == 'action' for s in workflow_steps)
        }

