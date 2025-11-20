"""
Universal Query Enhancement Engine
Dynamically discovers ArchE capabilities and generates optimized queries
that maximize effectiveness and robustness.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Capability:
    """Represents a single ArchE capability."""
    name: str
    type: str  # 'spr', 'action', 'workflow', 'tool'
    description: str
    category: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryAnalysis:
    """Analysis of a user query."""
    original_query: str
    intent: str
    complexity: str  # 'simple', 'medium', 'complex', 'very_complex'
    required_capabilities: List[str] = field(default_factory=list)
    detected_sprs: List[str] = field(default_factory=list)
    temporal_scope: Optional[str] = None
    analysis_type: List[str] = field(default_factory=list)  # 'causal', 'predictive', 'simulation', etc.
    missing_capabilities: List[str] = field(default_factory=list)
    confidence: float = 0.0


class CapabilityDiscoveryEngine:
    """Discovers all available ArchE capabilities dynamically."""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.capabilities: Dict[str, Capability] = {}
        self.spr_manager = None
        self.action_registry = None
        
    def discover_all_capabilities(self) -> Dict[str, Capability]:
        """Discover all capabilities from SPRs, actions, workflows, and tools."""
        logger.info("Starting comprehensive capability discovery...")
        
        # Discover SPRs
        spr_capabilities = self._discover_sprs()
        
        # Discover Actions
        action_capabilities = self._discover_actions()
        
        # Discover Workflows
        workflow_capabilities = self._discover_workflows()
        
        # Discover Tools
        tool_capabilities = self._discover_tools()
        
        # Merge all capabilities
        all_capabilities = {
            **spr_capabilities,
            **action_capabilities,
            **workflow_capabilities,
            **tool_capabilities
        }
        
        self.capabilities = all_capabilities
        logger.info(f"Discovered {len(all_capabilities)} total capabilities")
        
        return all_capabilities
    
    def _discover_sprs(self) -> Dict[str, Capability]:
        """Discover SPRs from the knowledge graph."""
        spr_capabilities = {}
        
        try:
            spr_file = self.project_root / "knowledge_graph" / "spr_definitions_tv.json"
            if spr_file.exists():
                with open(spr_file, 'r', encoding='utf-8') as f:
                    spr_data = json.load(f)
                
                # Handle both dict and list formats
                if isinstance(spr_data, dict):
                    sprs = spr_data
                elif isinstance(spr_data, list):
                    sprs = {spr['spr_id']: spr for spr in spr_data if isinstance(spr, dict) and 'spr_id' in spr}
                else:
                    sprs = {}
                
                for spr_id, spr_def in sprs.items():
                    if isinstance(spr_def, dict):
                        capability = Capability(
                            name=spr_id,
                            type='spr',
                            description=spr_def.get('definition', ''),
                            category=spr_def.get('category', ''),
                            keywords=self._extract_keywords(spr_def.get('definition', '')),
                            metadata={
                                'relationships': spr_def.get('relationships', {}),
                                'blueprint_details': spr_def.get('blueprint_details', '')
                            }
                        )
                        spr_capabilities[spr_id] = capability
                
                logger.info(f"Discovered {len(spr_capabilities)} SPR capabilities")
        except Exception as e:
            logger.warning(f"Failed to discover SPRs: {e}")
        
        return spr_capabilities
    
    def _discover_actions(self) -> Dict[str, Capability]:
        """Discover actions from the action registry."""
        action_capabilities = {}
        
        try:
            # Try to import and access the action registry
            import sys
            sys.path.insert(0, str(self.project_root))
            
            from Three_PointO_ArchE.action_registry import main_action_registry
            
            if hasattr(main_action_registry, 'actions'):
                for action_name, action_func in main_action_registry.actions.items():
                    # Try to get docstring for description
                    description = action_func.__doc__ or f"Action: {action_name}"
                    
                    capability = Capability(
                        name=action_name,
                        type='action',
                        description=description,
                        category=self._categorize_action(action_name),
                        keywords=self._extract_keywords(description),
                        metadata={
                            'function': str(action_func),
                            'module': getattr(action_func, '__module__', 'unknown')
                        }
                    )
                    action_capabilities[action_name] = capability
                
                logger.info(f"Discovered {len(action_capabilities)} action capabilities")
        except Exception as e:
            logger.warning(f"Failed to discover actions: {e}")
        
        return action_capabilities
    
    def _discover_workflows(self) -> Dict[str, Capability]:
        """Discover workflows from the workflows directory."""
        workflow_capabilities = {}
        
        try:
            workflows_dir = self.project_root / "workflows"
            if workflows_dir.exists():
                for workflow_file in workflows_dir.glob("*.json"):
                    try:
                        with open(workflow_file, 'r', encoding='utf-8') as f:
                            workflow_data = json.load(f)
                        
                        workflow_name = workflow_file.stem
                        description = workflow_data.get('description', f"Workflow: {workflow_name}")
                        
                        # Extract task types to understand capabilities
                        tasks = workflow_data.get('tasks', [])
                        task_types = [task.get('action_type', '') for task in tasks if isinstance(task, dict)]
                        
                        capability = Capability(
                            name=workflow_name,
                            type='workflow',
                            description=description,
                            category='workflow',
                            keywords=self._extract_keywords(description) + task_types,
                            metadata={
                                'task_count': len(tasks),
                                'task_types': task_types,
                                'file': str(workflow_file)
                            }
                        )
                        workflow_capabilities[workflow_name] = capability
                    except Exception as e:
                        logger.warning(f"Failed to load workflow {workflow_file}: {e}")
                
                logger.info(f"Discovered {len(workflow_capabilities)} workflow capabilities")
        except Exception as e:
            logger.warning(f"Failed to discover workflows: {e}")
        
        return workflow_capabilities
    
    def _discover_tools(self) -> Dict[str, Capability]:
        """Discover tools from various tool modules."""
        tool_capabilities = {}
        
        # Known tool patterns
        tool_patterns = [
            ('causal_inference', 'Causal InferencE', 'causal analysis'),
            ('predictive_modeling', 'PredictivE ModelinG TooL', 'predictive analysis'),
            ('agent_based_modeling', 'Agent Based ModelinG', 'simulation'),
            ('cfp_framework', 'ComparativE FluxuaL ProcessinG', 'comparative analysis'),
            ('rise_orchestrator', 'RISE Engine', 'synthesis'),
            ('enhanced_search', 'Enhanced Perception Engine', 'web search'),
        ]
        
        for tool_id, tool_name, category in tool_patterns:
            capability = Capability(
                name=tool_name,
                type='tool',
                description=f"Tool: {tool_name}",
                category=category,
                keywords=[tool_id, tool_name.lower()],
                metadata={'tool_id': tool_id}
            )
            tool_capabilities[tool_id] = capability
        
        return tool_capabilities
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        if not text:
            return []
        
        # Simple keyword extraction (can be enhanced with NLP)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        # Remove common stop words
        stop_words = {'this', 'that', 'with', 'from', 'have', 'will', 'would', 'could', 'should'}
        keywords = [w for w in words if w not in stop_words]
        return list(set(keywords[:10]))  # Limit to top 10
    
    def _categorize_action(self, action_name: str) -> str:
        """Categorize an action based on its name."""
        name_lower = action_name.lower()
        
        if 'search' in name_lower or 'web' in name_lower:
            return 'data_collection'
        elif 'predict' in name_lower or 'forecast' in name_lower:
            return 'predictive'
        elif 'causal' in name_lower or 'inference' in name_lower:
            return 'causal'
        elif 'abm' in name_lower or 'agent' in name_lower or 'simulate' in name_lower:
            return 'simulation'
        elif 'cfp' in name_lower or 'flux' in name_lower or 'compare' in name_lower:
            return 'comparative'
        elif 'generate' in name_lower or 'synthesize' in name_lower:
            return 'generation'
        else:
            return 'general'


class QueryAnalyzer:
    """Analyzes user queries to understand intent and requirements."""
    
    def __init__(self, capability_engine: CapabilityDiscoveryEngine):
        self.capability_engine = capability_engine
        self.capabilities = capability_engine.capabilities
        
    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze a query to understand its requirements."""
        logger.info(f"Analyzing query: {query[:100]}...")
        
        # Detect SPRs in query
        detected_sprs = self._detect_sprs(query)
        
        # Determine complexity
        complexity = self._assess_complexity(query)
        
        # Determine intent
        intent = self._determine_intent(query)
        
        # Detect temporal scope
        temporal_scope = self._detect_temporal_scope(query)
        
        # Determine analysis types needed
        analysis_types = self._detect_analysis_types(query)
        
        # Find required capabilities
        required_capabilities = self._find_required_capabilities(query, detected_sprs, analysis_types)
        
        # Find missing capabilities
        missing_capabilities = self._find_missing_capabilities(required_capabilities)
        
        # Calculate confidence
        confidence = self._calculate_confidence(query, required_capabilities, missing_capabilities)
        
        analysis = QueryAnalysis(
            original_query=query,
            intent=intent,
            complexity=complexity,
            required_capabilities=required_capabilities,
            detected_sprs=detected_sprs,
            temporal_scope=temporal_scope,
            analysis_type=analysis_types,
            missing_capabilities=missing_capabilities,
            confidence=confidence
        )
        
        logger.info(f"Query analysis complete: {complexity} complexity, {len(required_capabilities)} capabilities required")
        
        return analysis
    
    def _detect_sprs(self, query: str) -> List[str]:
        """Detect SPRs mentioned in the query."""
        detected = []
        query_lower = query.lower()
        
        for spr_id, capability in self.capabilities.items():
            if capability.type == 'spr':
                # Check if SPR name or keywords appear in query
                if spr_id.lower() in query_lower:
                    detected.append(spr_id)
                elif any(kw in query_lower for kw in capability.keywords):
                    detected.append(spr_id)
        
        return detected
    
    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity."""
        query_lower = query.lower()
        
        # Count indicators of complexity
        complexity_indicators = {
            'very_complex': [
                'comprehensive', 'multi-dimensional', 'full spectrum', 'complete',
                'all capabilities', 'leveraging', 'integrate', 'synthesize'
            ],
            'complex': [
                'analyze', 'simulate', 'model', 'forecast', 'predict', 'compare',
                'strategic', 'blueprint', 'plan'
            ],
            'medium': [
                'how', 'what', 'explain', 'describe', 'identify', 'find'
            ]
        }
        
        score = 0
        for level, indicators in complexity_indicators.items():
            matches = sum(1 for ind in indicators if ind in query_lower)
            if level == 'very_complex':
                score += matches * 3
            elif level == 'complex':
                score += matches * 2
            else:
                score += matches
        
        # Check query length
        if len(query.split()) > 200:
            score += 5
        elif len(query.split()) > 100:
            score += 3
        elif len(query.split()) > 50:
            score += 1
        
        # INTENT-BASED COMPLEXITY BOOST
        # Certain intents inherently require complex analysis
        intent_complexity_boost = {
            'monetiz': 5,  # Monetization questions need comprehensive analysis (matches "monetize", "monetization", "monitize", etc.)
            'monitiz': 5,  # Handle typo "monitize"
            'market': 4,  # Market analysis requires multiple tools
            'strategy': 4,  # Strategic questions need deep analysis
            'strategic': 4,  # Strategic analysis
            'business': 3,  # Business questions often complex
            'revenue': 3,  # Revenue questions need modeling
            'go-to-market': 5,  # Go-to-market needs full analysis
            'commercial': 4,  # Commercial questions need comprehensive approach
            'pricing': 3,  # Pricing strategy needs analysis
            'business model': 4,  # Business model questions
            'best way': 3,  # "Best way" questions need analysis
            'make money': 5,  # Making money questions need comprehensive analysis
        }
        
        # Apply highest matching boost
        max_boost = 0
        for intent_keyword, boost in intent_complexity_boost.items():
            if intent_keyword in query_lower:
                max_boost = max(max_boost, boost)
        
        if max_boost > 0:
            score += max_boost
        
        # CAPABILITY-BASED COMPLEXITY BOOST
        # If query mentions specific complex capabilities, boost complexity
        complex_capability_keywords = [
            'causal inference', 'predictive modeling', 'agent-based modeling',
            'abm', 'cfp', 'comparative fluxual', 'complex system visioning',
            'rise engine', 'temporal resonance', '4d thinking'
        ]
        
        for capability in complex_capability_keywords:
            if capability in query_lower:
                score += 2
        
        if score >= 10:
            return 'very_complex'
        elif score >= 5:
            return 'complex'
        elif score >= 2:
            return 'medium'
        else:
            return 'simple'
    
    def _determine_intent(self, query: str) -> str:
        """Determine the primary intent of the query."""
        query_lower = query.lower()
        
        # Check for monetization (including common typos)
        monetization_keywords = ['monetize', 'monitize', 'monetiz', 'monitiz', 'monetization', 'monitization',
                                'market', 'revenue', 'business', 'commercial', 'pricing', 'business model',
                                'go-to-market', 'bring to market', 'make money', 'earn revenue']
        if any(keyword in query_lower for keyword in monetization_keywords):
            return 'monetization'
        elif any(word in query_lower for word in ['analyze', 'analysis', 'study', 'examine']):
            return 'analysis'
        elif any(word in query_lower for word in ['predict', 'forecast', 'project']):
            return 'prediction'
        elif any(word in query_lower for word in ['simulate', 'model', 'abm']):
            return 'simulation'
        elif any(word in query_lower for word in ['compare', 'difference', 'versus']):
            return 'comparison'
        elif any(word in query_lower for word in ['how', 'process', 'work']):
            return 'explanation'
        elif any(word in query_lower for word in ['what', 'define', 'is']) and 'best way' not in query_lower:
            # "what is the best way" is not a definition question, it's a strategy question
            return 'definition'
        else:
            return 'general'
    
    def _detect_temporal_scope(self, query: str) -> Optional[str]:
        """Detect temporal scope in query."""
        query_lower = query.lower()
        
        temporal_patterns = {
            'historical': ['historical', 'past', 'previous', 'prior', 'ago'],
            'current': ['current', 'now', 'present', 'today'],
            'future': ['future', 'forecast', 'predict', 'project', 'years', 'months'],
            'temporal': ['temporal', 'time', 'evolution', 'over time', 'trajectory']
        }
        
        for scope, patterns in temporal_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return scope
        
        return None
    
    def _detect_analysis_types(self, query: str) -> List[str]:
        """Detect what types of analysis are needed."""
        query_lower = query.lower()
        analysis_types = []
        
        if any(word in query_lower for word in ['causal', 'cause', 'effect', 'relationship']):
            analysis_types.append('causal')
        
        if any(word in query_lower for word in ['predict', 'forecast', 'project', 'future']):
            analysis_types.append('predictive')
        
        if any(word in query_lower for word in ['simulate', 'abm', 'agent', 'model']):
            analysis_types.append('simulation')
        
        if any(word in query_lower for word in ['compare', 'difference', 'versus', 'alternative']):
            analysis_types.append('comparative')
        
        if any(word in query_lower for word in ['complex', 'emergent', 'system', 'ecosystem']):
            analysis_types.append('complex_system')
        
        if any(word in query_lower for word in ['synthesize', 'integrate', 'combine']):
            analysis_types.append('synthesis')
        
        return analysis_types if analysis_types else ['general']
    
    def _find_required_capabilities(self, query: str, detected_sprs: List[str], analysis_types: List[str]) -> List[str]:
        """Find capabilities required to answer the query."""
        required = set()
        
        # Add detected SPRs
        required.update(detected_sprs)
        
        # Map analysis types to capabilities
        type_to_capabilities = {
            'causal': ['Causal InferencE', 'CausalLagDetectioN', 'causal_inference'],
            'predictive': ['PredictivE ModelinG TooL', 'FutureStateAnalysiS', 'predictive_modeling'],
            'simulation': ['Agent Based ModelinG', 'EmergenceOverTimE', 'agent_based_modeling'],
            'comparative': ['ComparativE FluxuaL ProcessinG', 'TrajectoryComparisoN', 'cfp_framework'],
            'complex_system': ['ComplexSystemVisioninG', 'HumanFactorModelinG'],
            'synthesis': ['RISE Engine', 'rise_orchestrator'],
            'temporal': ['Temporal resonancE', '4D Thinking', 'HistoricalContextualizatioN']
        }
        
        for analysis_type in analysis_types:
            if analysis_type in type_to_capabilities:
                required.update(type_to_capabilities[analysis_type])
        
        # Search query for capability keywords
        query_lower = query.lower()
        for cap_id, capability in self.capabilities.items():
            if any(kw in query_lower for kw in capability.keywords):
                required.add(cap_id)
        
        return list(required)
    
    def _find_missing_capabilities(self, required: List[str]) -> List[str]:
        """Find capabilities that are required but not available."""
        missing = []
        available_names = {cap.name.lower() for cap in self.capabilities.values()}
        available_ids = set(self.capabilities.keys())
        
        for req in required:
            req_lower = req.lower()
            if req not in available_ids and req_lower not in available_names:
                # Check if similar capability exists
                found = False
                for cap_id, capability in self.capabilities.items():
                    if req_lower in capability.name.lower() or any(req_lower in kw for kw in capability.keywords):
                        found = True
                        break
                
                if not found:
                    missing.append(req)
        
        return missing
    
    def _calculate_confidence(self, query: str, required: List[str], missing: List[str]) -> float:
        """Calculate confidence in ability to answer the query."""
        if not required:
            return 0.5  # Medium confidence if no specific requirements
        
        coverage = 1.0 - (len(missing) / len(required)) if required else 1.0
        
        # Adjust based on query clarity
        clarity_score = 0.8 if len(query.split()) > 20 else 0.6
        
        confidence = (coverage * 0.7) + (clarity_score * 0.3)
        return min(1.0, max(0.0, confidence))


class QueryEnhancementEngine:
    """Generates enhanced queries that maximize effectiveness."""
    
    def __init__(self, capability_engine: CapabilityDiscoveryEngine, query_analyzer: QueryAnalyzer):
        self.capability_engine = capability_engine
        self.query_analyzer = query_analyzer
        self.capabilities = capability_engine.capabilities
    
    def enhance_query(self, original_query: str, enhancement_level: str = 'auto') -> Dict[str, Any]:
        """
        Enhance a query to maximize effectiveness.
        
        Args:
            original_query: The original user query
            enhancement_level: 'minimal', 'moderate', 'comprehensive', 'auto'
        
        Returns:
            Dictionary with enhanced query and metadata
        """
        logger.info(f"Enhancing query with level: {enhancement_level}")
        
        # Analyze the original query
        analysis = self.query_analyzer.analyze_query(original_query)
        
        # Determine enhancement level if auto
        if enhancement_level == 'auto':
            enhancement_level = self._determine_enhancement_level(analysis)
        
        # Generate enhanced query
        enhanced_query = self._generate_enhanced_query(original_query, analysis, enhancement_level)
        
        # Generate query structure
        query_structure = self._generate_query_structure(analysis, enhancement_level)
        
        # Calculate enhanced complexity (complexity after enhancement)
        enhanced_complexity = self._calculate_enhanced_complexity(analysis, enhancement_level)
        
        return {
            'original_query': original_query,
            'enhanced_query': enhanced_query,
            'query_structure': query_structure,
            'analysis': {
                'intent': analysis.intent,
                'complexity': analysis.complexity,  # Original complexity
                'enhanced_complexity': enhanced_complexity,  # Complexity after enhancement
                'required_capabilities': analysis.required_capabilities,
                'detected_sprs': analysis.detected_sprs,
                'temporal_scope': analysis.temporal_scope,
                'analysis_types': analysis.analysis_type,
                'missing_capabilities': analysis.missing_capabilities,
                'confidence': analysis.confidence
            },
            'enhancement_metadata': {
                'level': enhancement_level,
                'capabilities_used': len(analysis.required_capabilities),
                'sprs_activated': len(analysis.detected_sprs),
                'improvement_estimate': self._estimate_improvement(analysis),
                'complexity_increase': self._calculate_complexity_increase(analysis.complexity, enhanced_complexity)
            }
        }
    
    def _determine_enhancement_level(self, analysis: QueryAnalysis) -> str:
        """Determine appropriate enhancement level based on analysis."""
        # Certain intents should always get comprehensive enhancement
        comprehensive_intents = ['monetization', 'strategy', 'market', 'business']
        if analysis.intent in comprehensive_intents:
            return 'comprehensive'
        
        if analysis.complexity == 'very_complex':
            return 'comprehensive'
        elif analysis.complexity == 'complex':
            return 'moderate'
        elif analysis.complexity == 'medium':
            return 'moderate'
        else:
            return 'minimal'
    
    def _generate_enhanced_query(self, original_query: str, analysis: QueryAnalysis, level: str) -> str:
        """Generate the enhanced query text."""
        if level == 'minimal':
            return self._minimal_enhancement(original_query, analysis)
        elif level == 'moderate':
            return self._moderate_enhancement(original_query, analysis)
        else:  # comprehensive
            return self._comprehensive_enhancement(original_query, analysis)
    
    def _minimal_enhancement(self, query: str, analysis: QueryAnalysis) -> str:
        """Minimal enhancement - just add protocol reference."""
        enhanced = f"Apply ResonantiA Protocol v3.5-GP capabilities to: {query}"
        return enhanced
    
    def _moderate_enhancement(self, query: str, analysis: QueryAnalysis) -> str:
        """Moderate enhancement - add relevant capabilities."""
        # Build capability preamble
        capabilities_text = ", ".join(analysis.required_capabilities[:5])
        
        enhanced = f"""Apply ResonantiA Protocol v3.5-GP (Genesis Protocol) capabilities including {capabilities_text} to achieve Cognitive Resonance and Temporal Resonance on this query.

{query}

Ensure the analysis leverages the identified capabilities and generates IAR reflections throughout."""
        
        return enhanced
    
    def _comprehensive_enhancement(self, query: str, analysis: QueryAnalysis) -> str:
        """Comprehensive enhancement - full structured query."""
        # Build comprehensive query structure
        preamble = "Apply the full spectrum of ResonantiA Protocol v3.5-GP (Genesis Protocol) capabilities to achieve deep Temporal Resonance and Cognitive Resonance on this query. Execute a temporally-aware, multi-dimensional analytical sequence that integrates all advanced capabilities while maintaining Implementation Resonance throughout.\n\n"
        
        # Add capability-specific directives
        directives = []
        
        if 'causal' in analysis.analysis_type:
            directives.append("(1) Use Causal InferencE with CausalLagDetectioN to identify causal relationships and temporal lags.")
        
        if 'predictive' in analysis.analysis_type:
            directives.append("(2) Apply PredictivE ModelinG TooL with FutureStateAnalysiS to forecast outcomes with confidence intervals.")
        
        if 'simulation' in analysis.analysis_type:
            directives.append("(3) Execute Agent Based ModelinG with HumanFactorModelinG and EmergenceOverTimE to simulate complex dynamics.")
        
        if 'comparative' in analysis.analysis_type:
            directives.append("(4) Utilize ComparativE FluxuaL ProcessinG (CFP) with TrajectoryComparisoN to compare alternative scenarios.")
        
        if 'complex_system' in analysis.analysis_type:
            directives.append("(5) Apply ComplexSystemVisioninG to model emergent behaviors and system interactions.")
        
        if 'synthesis' in analysis.analysis_type or analysis.complexity == 'very_complex':
            directives.append("(6) Synthesize all findings through the RISE engine to generate comprehensive, actionable recommendations.")
        
        if analysis.temporal_scope:
            directives.append(f"(7) Ensure Temporal resonancE by integrating {analysis.temporal_scope} context and validating temporal coherence.")
        
        # Add IAR requirement
        directives.append("(8) Generate comprehensive IAR (Integrated Action Reflection) reflections for each phase, assessing confidence, alignment, and potential issues.")
        
        # Add pattern crystallization
        if analysis.complexity in ['complex', 'very_complex']:
            directives.append("(9) Apply Pattern crystallizatioN to identify and solidify key insights for future use.")
        
        # Build final query
        enhanced = preamble
        enhanced += "PRIMARY OBJECTIVE:\n\n"
        enhanced += query + "\n\n"
        
        if directives:
            enhanced += "REQUIRED ANALYSIS COMPONENTS:\n\n"
            enhanced += "\n".join(directives) + "\n\n"
        
        enhanced += "FINAL OUTPUT REQUIREMENTS:\n\n"
        enhanced += "- Comprehensive analysis with all phase results\n"
        enhanced += "- IAR reflections for each major step\n"
        enhanced += "- Temporal coherence validation\n"
        enhanced += "- Implementation feasibility assessment\n"
        enhanced += "- Crystallized insights and patterns\n"
        
        return enhanced
    
    def _generate_query_structure(self, analysis: QueryAnalysis, level: str) -> Dict[str, Any]:
        """Generate structured query components."""
        structure = {
            'phases': [],
            'capabilities_per_phase': {},
            'expected_outputs': []
        }
        
        # Define phases based on analysis
        if 'causal' in analysis.analysis_type:
            structure['phases'].append({
                'name': 'Causal Analysis',
                'capabilities': ['Causal InferencE', 'CausalLagDetectioN'],
                'output': 'Causal relationships and temporal lags'
            })
        
        if 'predictive' in analysis.analysis_type:
            structure['phases'].append({
                'name': 'Predictive Modeling',
                'capabilities': ['PredictivE ModelinG TooL', 'FutureStateAnalysiS'],
                'output': 'Forecasts with confidence intervals'
            })
        
        if 'simulation' in analysis.analysis_type:
            structure['phases'].append({
                'name': 'Agent-Based Simulation',
                'capabilities': ['Agent Based ModelinG', 'HumanFactorModelinG'],
                'output': 'Simulation results and emergent patterns'
            })
        
        if 'comparative' in analysis.analysis_type:
            structure['phases'].append({
                'name': 'Comparative Analysis',
                'capabilities': ['ComparativE FluxuaL ProcessinG', 'TrajectoryComparisoN'],
                'output': 'Comparative metrics and trajectory differences'
            })
        
        if 'synthesis' in analysis.analysis_type:
            structure['phases'].append({
                'name': 'Synthesis',
                'capabilities': ['RISE Engine'],
                'output': 'Comprehensive strategy and recommendations'
            })
        
        return structure
    
    def _calculate_enhanced_complexity(self, analysis: QueryAnalysis, enhancement_level: str) -> str:
        """Calculate the complexity level after enhancement."""
        original = analysis.complexity
        
        # Enhancement level increases complexity
        if enhancement_level == 'comprehensive':
            if original == 'simple':
                return 'complex'
            elif original == 'medium':
                return 'very_complex'
            elif original == 'complex':
                return 'very_complex'
            else:
                return 'very_complex'
        elif enhancement_level == 'moderate':
            if original == 'simple':
                return 'medium'
            elif original == 'medium':
                return 'complex'
            else:
                return original
        else:  # minimal
            if original == 'simple':
                return 'medium'
            else:
                return original
    
    def _calculate_complexity_increase(self, original: str, enhanced: str) -> str:
        """Calculate how much complexity increased."""
        complexity_levels = {'simple': 1, 'medium': 2, 'complex': 3, 'very_complex': 4}
        original_level = complexity_levels.get(original, 1)
        enhanced_level = complexity_levels.get(enhanced, 1)
        increase = enhanced_level - original_level
        
        if increase >= 2:
            return "Significantly increased"
        elif increase == 1:
            return "Moderately increased"
        elif increase == 0:
            return "Maintained"
        else:
            return "Decreased"
    
    def _estimate_improvement(self, analysis: QueryAnalysis) -> str:
        """Estimate improvement from enhancement."""
        if analysis.complexity == 'very_complex':
            return "High - Query will leverage full ArchE capabilities"
        elif analysis.complexity == 'complex':
            return "Medium-High - Query will use multiple advanced capabilities"
        elif analysis.complexity == 'medium':
            return "Medium - Query will be enhanced with relevant capabilities"
        else:
            return "Low - Minimal enhancement needed"


def create_enhancement_engine(project_root: Optional[Path] = None) -> QueryEnhancementEngine:
    """Factory function to create a query enhancement engine."""
    if project_root is None:
        import os
        project_root = Path(os.getcwd())
    
    capability_engine = CapabilityDiscoveryEngine(project_root)
    capability_engine.discover_all_capabilities()
    
    query_analyzer = QueryAnalyzer(capability_engine)
    
    enhancement_engine = QueryEnhancementEngine(capability_engine, query_analyzer)
    
    return enhancement_engine


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "How can I monetize ArchE and bring it to market?"
    
    engine = create_enhancement_engine()
    result = engine.enhance_query(query, enhancement_level='auto')
    
    print("\n" + "="*80)
    print("QUERY ENHANCEMENT RESULT")
    print("="*80)
    print(f"\nOriginal Query:\n{result['original_query']}\n")
    print(f"\nEnhanced Query:\n{result['enhanced_query']}\n")
    print(f"\nAnalysis:\n{json.dumps(result['analysis'], indent=2)}\n")
    print("="*80)

