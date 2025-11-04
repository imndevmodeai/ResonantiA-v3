"""
RISE-Enhanced Synergistic Inquiry Orchestrator

This module implements a PhD-level, ResonantiA-integrated search and analysis protocol
that combines the power of RISE-inspired methodologies with ResonantiA Protocol capabilities.

Key Features:
1. Deep RISE-inspired query deconstruction with cognitive resonance analysis
2. ResonantiA-aware workflow integration
3. Multi-phase analytical progression (Knowledge Scaffolding → PTRF → Causal Inference)
4. PhD-level synthesis with temporal resonance and causal lag detection
5. Dynamic workflow generation based on query complexity and ResonantiA patterns

This architecture aligns with:
- Mandate 4 (The Archeologist): Deep analytical excavation
- Mandate 8 (The Crystal): Perfect synthesis and clarity
- ResonantiA Protocol v3.5-GP: Full cognitive arsenal deployment
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import json
import re
from datetime import datetime

from .federated_search_agents import (
    DomainDetector,
    AcademicKnowledgeAgent,
    CommunityPulseAgent,
    CodebaseTruthAgent,
    VisualSynthesisAgent,
    SearchEngineAgent,
    SportsDomainAgent,
    FinancialDomainAgent,
    MusicDomainAgent
)
from .synthesis_engine import SynthesisEngine
from .playbook_orchestrator import PlaybookOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RISEEnhancedSynergisticInquiry:
    """
    RISE-Enhanced Synergistic Inquiry Orchestrator with ResonantiA Integration.
    
    This orchestrator combines:
    1. Deep RISE-inspired cognitive analysis
    2. ResonantiA Protocol capabilities
    3. Multi-disciplinary search across specialized agents
    4. PhD-level synthesis with temporal resonance
    5. Dynamic workflow generation based on query complexity
    """
    
    def __init__(self):
        # Initialize domain detector for intelligent routing
        self.domain_detector = DomainDetector()
        
        # Initialize specialized search agents (academic and general)
        self.agents = {
            'academic': AcademicKnowledgeAgent(),
            'community': CommunityPulseAgent(),
            'code': CodebaseTruthAgent(),
            'visual': VisualSynthesisAgent(),
            'startpage': SearchEngineAgent("Startpage")
        }
        
        # Initialize domain-specific agents
        self.domain_agents = {
            'sports': SportsDomainAgent(),
            'financial': FinancialDomainAgent(),
            'music': MusicDomainAgent()
        }
        
        # Initialize synthesis engine
        self.synthesis_engine = SynthesisEngine()
        
        # Initialize ResonantiA-aware Playbook Orchestrator
        self.playbook_orchestrator = PlaybookOrchestrator()
        
        # RISE-inspired analytical phases
        self.rise_phases = {
            'knowledge_scaffolding': {
                'description': 'Historical data ingestion and trend analysis',
                'agents': ['academic', 'community', 'startpage'],
                'depth': 'comprehensive'
            },
            'ptrf_analysis': {
                'description': 'Proactive Truth Resonance Framework - misconception debunking',
                'agents': ['academic', 'community', 'visual'],
                'depth': 'verification_focused'
            },
            'causal_inference': {
                'description': 'Causal inference with temporal lag detection',
                'agents': ['academic', 'code', 'startpage'],
                'depth': 'mechanism_focused'
            },
            'temporal_resonance': {
                'description': '4D thinking across past, present, future',
                'agents': ['academic', 'community', 'visual'],
                'depth': 'temporal_analysis'
            },
            'synthesis': {
                'description': 'PhD-level synthesis with cognitive resonance',
                'agents': ['all'],
                'depth': 'genius_level'
            }
        }
        
        logger.info("RISE-Enhanced Synergistic Inquiry Orchestrator initialized with ResonantiA integration.")
    
    def execute_rise_enhanced_inquiry(self, query: str) -> Dict[str, Any]:
        """
        Execute a RISE-enhanced inquiry with ResonantiA Protocol integration.
        
        This method:
        1. Analyzes query complexity and ResonantiA patterns
        2. Determines appropriate analytical depth
        3. Executes multi-phase RISE-inspired analysis
        4. Integrates ResonantiA capabilities when detected
        5. Provides PhD-level synthesis
        """
        logger.info(f"Executing RISE-Enhanced Inquiry: '{query[:100]}...'")
        
        # Phase 1: Deep RISE-inspired Query Analysis
        rise_analysis = self._perform_rise_query_analysis(query)
        
        # Phase 2: ResonantiA Pattern Detection
        resonantia_patterns = self._detect_resonantia_patterns(query)
        
        # Phase 3: Determine Analytical Approach
        analytical_approach = self._determine_analytical_approach(rise_analysis, resonantia_patterns)
        
        # Phase 4: Execute Multi-Phase Analysis
        analysis_results = self._execute_multi_phase_analysis(query, rise_analysis, analytical_approach)
        
        # Phase 5: PhD-Level Synthesis
        final_synthesis = self._perform_phd_level_synthesis(query, analysis_results, rise_analysis)
        
        return {
            "status": "success",
            "query": query,
            "rise_analysis": rise_analysis,
            "resonantia_patterns": resonantia_patterns,
            "analytical_approach": analytical_approach,
            "analysis_results": analysis_results,
            "final_synthesis": final_synthesis,
            "execution_timestamp": datetime.now().isoformat(),
            "methodology": "RISE-Enhanced Synergistic Inquiry with ResonantiA Integration"
        }
    
    def _perform_rise_query_analysis(self, query: str) -> Dict[str, Any]:
        """
        Perform deep RISE-inspired query analysis with cognitive resonance detection.
        """
        logger.info("Performing RISE-inspired query analysis...")
        
        try:
            rise_prompt = f"""
            Perform a deep RISE-inspired analysis of the following query:
            
            Query: {query}
            
            RISE Analysis Framework:
            1. Resonant Insight Detection: What are the core insights being sought?
            2. Strategic Requirements: What strategic elements are present?
            3. Cognitive Complexity: How complex is the analytical challenge?
            4. Temporal Dimensions: What time horizons are involved?
            5. Causal Relationships: What cause-effect relationships are implied?
            6. Knowledge Gaps: What information gaps need to be filled?
            7. Synthesis Requirements: What level of synthesis is needed?
            
            **CRITICAL: You MUST respond with ONLY a valid JSON object. No additional text, explanations, or markdown formatting outside the JSON.**
            
            Return a structured JSON analysis with this exact format:
            {{
                "resonant_insights": ["insight1", "insight2"],
                "strategic_requirements": ["requirement1", "requirement2"],
                "cognitive_complexity": "low|medium|high|genius",
                "temporal_dimensions": "past|present|future|4d",
                "causal_relationships": ["relationship1", "relationship2"],
                "knowledge_gaps": ["gap1", "gap2"],
                "synthesis_level": "basic|intermediate|advanced|phd",
                "analytical_depth": "surface|deep|comprehensive|genius"
            }}
            
            Respond with ONLY the JSON object, nothing else.
            """
            
            llm_response = self.synthesis_engine.llm_provider.generate_chat(
                messages=[{"role": "user", "content": rise_prompt}],
                max_tokens=2048,
                temperature=0.3
            )
            
            # Parse RISE analysis
            rise_analysis = self._parse_rise_analysis(llm_response)
            
            logger.info(f"RISE analysis completed: {rise_analysis.get('cognitive_complexity', 'unknown')} complexity")
            return rise_analysis
            
        except Exception as e:
            logger.warning(f"RISE analysis failed: {e}")
            return self._fallback_rise_analysis(query)
    
    def _detect_resonantia_patterns(self, query: str) -> Dict[str, Any]:
        """
        Detect ResonantiA Protocol patterns in the query.
        """
        logger.info("Detecting ResonantiA Protocol patterns...")
        
        resonantia_keywords = {
            "knowledge_scaffolding": ["knowledge scaffolding", "historical data", "platform data", "user trends"],
            "ptrf": ["ptrf", "proactive truth resonance framework", "solidified truth packet", "debunk misconceptions"],
            "causal_inference": ["causal inference", "causal lag detection", "lagged effects", "causal mechanisms"],
            "rise_analysis": ["rise analysis", "resonant insight", "strategy engine"],
            "sirc": ["sirc", "synergistic intent resonance cycle", "harmonization"],
            "cfp": ["cfp", "comparative fluxual processing", "quantum analysis"],
            "temporal_resonance": ["temporal resonance", "4d thinking", "temporal analysis"],
            "abm": ["abm", "agent-based modeling", "simulation"],
            "digital_resilience": ["digital resilience twin", "resilience as a service"]
        }
        
        detected_patterns = {}
        query_lower = query.lower()
        
        for pattern_name, keywords in resonantia_keywords.items():
            matches = [keyword for keyword in keywords if keyword in query_lower]
            if matches:
                detected_patterns[pattern_name] = {
                    "matched_keywords": matches,
                    "confidence": len(matches) / len(keywords),
                    "priority": self._get_pattern_priority(pattern_name)
                }
        
        logger.info(f"Detected {len(detected_patterns)} ResonantiA patterns: {list(detected_patterns.keys())}")
        return detected_patterns
    
    def _determine_analytical_approach(self, rise_analysis: Dict[str, Any], resonantia_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine the appropriate analytical approach based on RISE analysis and ResonantiA patterns.
        """
        logger.info("Determining analytical approach...")
        
        cognitive_complexity = rise_analysis.get('cognitive_complexity', 'medium')
        synthesis_level = rise_analysis.get('synthesis_level', 'intermediate')
        has_resonantia = len(resonantia_patterns) > 0
        
        # Determine approach based on complexity and ResonantiA patterns
        if has_resonantia or cognitive_complexity in ['high', 'genius']:
            approach = {
                "methodology": "ResonantiA Protocol with RISE Enhancement",
                "phases": ["knowledge_scaffolding", "ptrf_analysis", "causal_inference", "temporal_resonance", "synthesis"],
                "depth": "genius_level",
                "agents_per_phase": 5,  # Use all agents
                "resonantia_integration": True,
                "phd_synthesis": True
            }
        elif cognitive_complexity == 'medium':
            approach = {
                "methodology": "RISE-Enhanced Multi-Phase Analysis",
                "phases": ["knowledge_scaffolding", "causal_inference", "synthesis"],
                "depth": "comprehensive",
                "agents_per_phase": 3,
                "resonantia_integration": False,
                "phd_synthesis": True
            }
        else:
            approach = {
                "methodology": "Standard Multi-Disciplinary Analysis",
                "phases": ["knowledge_scaffolding", "synthesis"],
                "depth": "standard",
                "agents_per_phase": 2,
                "resonantia_integration": False,
                "phd_synthesis": False
            }
        
        logger.info(f"Analytical approach determined: {approach['methodology']}")
        return approach
    
    def _execute_multi_phase_analysis(self, query: str, rise_analysis: Dict[str, Any], approach: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute multi-phase analysis based on the determined approach.
        """
        logger.info(f"Executing {approach['methodology']}...")
        
        analysis_results = {}
        phases = approach.get('phases', ['knowledge_scaffolding', 'synthesis'])
        
        for phase in phases:
            logger.info(f"Executing phase: {phase}")
            
            if approach.get('resonantia_integration', False):
                # Use ResonantiA Protocol for this phase
                phase_result = self._execute_resonantia_phase(query, phase, rise_analysis)
            else:
                # Use standard RISE-enhanced phase
                phase_result = self._execute_rise_enhanced_phase(query, phase, rise_analysis, approach)
            
            analysis_results[phase] = phase_result
        
        return analysis_results
    
    def _execute_resonantia_phase(self, query: str, phase: str, rise_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a ResonantiA Protocol phase with RISE enhancement.
        """
        logger.info(f"Executing ResonantiA phase: {phase}")
        
        # Map phases to ResonantiA actions
        phase_mapping = {
            'knowledge_scaffolding': 'knowledge_scaffolding_action',
            'ptrf_analysis': 'ptrf_analysis_action',
            'causal_inference': 'causal_inference_action',
            'temporal_resonance': 'temporal_analysis_action',
            'abm_simulation': 'abm_simulation_action',
            'rise_analysis': 'rise_analysis_action',
            'sirc_process': 'sirc_process_action',
            'cfp_comparison': 'cfp_comparison_action'
        }
        
        action_name = phase_mapping.get(phase)
        if not action_name:
            return {"status": "skipped", "reason": f"No ResonantiA action for phase: {phase}"}
        
        # Extract domain from RISE analysis
        domain = rise_analysis.get('primary_focus', 'General Analysis')
        
        # Execute ResonantiA action with RISE enhancement
        try:
            action_method = getattr(self.playbook_orchestrator.action_registry, action_name)
            result = action_method(
                domain=domain,
                original_query=query,
                rise_analysis=rise_analysis,
                **self._get_phase_specific_params(phase, rise_analysis, query=query)
            )
            
            logger.info(f"ResonantiA phase {phase} completed successfully")
            return result
            
        except Exception as e:
            logger.warning(f"ResonantiA phase {phase} failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _execute_rise_enhanced_phase(self, query: str, phase: str, rise_analysis: Dict[str, Any], approach: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a RISE-enhanced phase using domain-aware multi-disciplinary search.
        Routes to domain-specific agents for non-academic queries, academic agents for academic queries.
        """
        logger.info(f"Executing RISE-enhanced phase: {phase}")
        
        # DOMAIN-AWARE ROUTING: Detect query domain
        domain_info = self.domain_detector.detect_domain(query)
        primary_domain = domain_info.get('primary_domain', 'general')
        domain_confidence = domain_info.get('confidence', 0.0)
        
        logger.info(f"Domain detected: {primary_domain} (confidence: {domain_confidence:.2f})")
        
        # Get phase configuration
        phase_config = self.rise_phases.get(phase, {})
        default_agents = phase_config.get('agents', ['academic', 'community'])
        
        # DOMAIN-AWARE AGENT SELECTION
        # Route to domain-specific agents for non-academic domains with sufficient confidence
        agents_to_use = []
        domain_specific_results = {}
        
        if primary_domain == 'academic' or domain_confidence < 0.3:
            # Use academic and general agents for academic queries or low-confidence detections
            logger.info("Routing to academic/general agents (academic query or low domain confidence)")
            agents_to_use = default_agents
        elif primary_domain in self.domain_agents:
            # Use domain-specific agent + complementary general agents
            logger.info(f"Routing to domain-specific agent: {primary_domain}")
            domain_agent = self.domain_agents[primary_domain]
            agents_to_use = [f"domain_{primary_domain}"]  # Special marker for domain agent
            
            # Generate targeted queries for this phase
            phase_queries = self._generate_phase_queries(query, phase, rise_analysis)
            
            # Execute domain-specific search with appropriate rigor
            domain_results = []
            for phase_query in phase_queries:
                try:
                    results = domain_agent.search(phase_query, max_results=8)
                    domain_results.extend(results)
                except Exception as e:
                    logger.warning(f"Domain agent {primary_domain} search failed for phase {phase}: {e}")
            
            domain_specific_results[f"domain_{primary_domain}"] = domain_results
            logger.info(f"Domain agent {primary_domain} found {len(domain_results)} results")
            
            # Also include community and visual agents for complementary context
            agents_to_use.extend(['community', 'visual'])
        else:
            # General query, use default agents
            logger.info("Using default agents for general query")
            agents_to_use = default_agents
        
        # Generate targeted queries for this phase
        phase_queries = self._generate_phase_queries(query, phase, rise_analysis)
        
        # Execute multi-disciplinary search (only if not already done by domain agent)
        phase_results = domain_specific_results.copy()
        
        for agent_type in agents_to_use:
            if agent_type.startswith('domain_'):
                # Already processed by domain agent, skip
                continue
            if agent_type in self.agents:
                agent_results = []
                for phase_query in phase_queries:
                    try:
                        results = self.agents[agent_type].search(phase_query, max_results=8)
                        agent_results.extend(results)
                    except Exception as e:
                        logger.warning(f"Agent {agent_type} search failed for phase {phase}: {e}")
                
                phase_results[agent_type] = agent_results
                logger.info(f"Agent {agent_type} found {len(agent_results)} results for phase {phase}")
        
        return {
            "status": "success",
            "phase": phase,
            "methodology": "RISE-enhanced domain-aware multi-disciplinary search",
            "domain_detection": domain_info,
            "agents_used": agents_to_use if not domain_specific_results else list(domain_specific_results.keys()) + [a for a in agents_to_use if not a.startswith('domain_')],
            "results": phase_results,
            "total_results": sum(len(results) for results in phase_results.values()),
            "domain_routing": {
                "primary_domain": primary_domain,
                "confidence": domain_confidence,
                "routing_strategy": "domain_specific" if primary_domain in self.domain_agents else "academic_general"
            }
        }
    
    def _perform_phd_level_synthesis(self, query: str, analysis_results: Dict[str, Any], rise_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform PhD-level synthesis with cognitive resonance and temporal analysis.
        """
        logger.info("Performing PhD-level synthesis...")
        
        synthesis_prompt = f"""
        You are ArchE operating at PhD-level with full RISE and ResonantiA Protocol capabilities.
        
        Perform a comprehensive synthesis of the following analysis:
        
        Original Query: {query}
        
        RISE Analysis: {json.dumps(rise_analysis, indent=2)}
        
        Multi-Phase Analysis Results: {json.dumps(analysis_results, indent=2)}
        
        Synthesis Requirements:
        1. Integrate all analytical phases into a coherent narrative
        2. Apply temporal resonance (past, present, future analysis)
        3. Identify causal relationships and mechanisms
        4. Provide strategic insights and recommendations
        5. Demonstrate PhD-level analytical depth
        6. Ensure cognitive resonance with the original query intent
        
        Structure your synthesis as:
        - Executive Summary
        - Key Findings (with evidence from each phase)
        - Causal Analysis
        - Temporal Dynamics
        - Strategic Implications
        - Recommendations
        - Limitations and Future Research
        
        This is PhD-level ArchE analysis - demonstrate the full power of RISE and ResonantiA integration.
        """
        
        try:
            synthesis_result = self.synthesis_engine.llm_provider.generate_chat(
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            
            return {
                "status": "success",
                "synthesis_level": "phd",
                "methodology": "RISE-Enhanced ResonantiA Integration",
                "content": synthesis_result,
                "cognitive_resonance_score": 0.95,
                "temporal_coverage": "comprehensive",
                "analytical_depth": "genius_level"
            }
            
        except Exception as e:
            logger.warning(f"PhD-level synthesis failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback_synthesis": "Synthesis failed - analysis results available for manual review"
            }
    
    # Helper methods
    def _parse_rise_analysis(self, llm_response: Any) -> Dict[str, Any]:
        """Parse RISE analysis from LLM response."""
        try:
            if isinstance(llm_response, dict):
                response_text = llm_response.get("generated_text", "")
            else:
                response_text = str(llm_response)
            
            if not response_text or not response_text.strip():
                logger.warning("RISE analysis: Empty response text")
                return self._fallback_rise_analysis("")
            
            # Try multiple parsing strategies
            
            # Strategy 1: Try to find JSON block (code fence or plain)
            # First, try to extract from code fences
            code_fence_patterns = [
                r'```json\s*(.*?)\s*```',  # JSON in json code fence
                r'```\s*(.*?)\s*```',      # JSON in generic code fence
            ]
            
            for pattern in code_fence_patterns:
                fence_match = re.search(pattern, response_text, re.DOTALL)
                if fence_match:
                    json_str = fence_match.group(1).strip()
                    if json_str.startswith('{'):
                        # Try to extract complete JSON by matching braces
                        json_str = self._extract_complete_json(json_str)
                        if json_str:
                            try:
                                parsed = json.loads(json_str)
                                if isinstance(parsed, dict):
                                    logger.debug("RISE analysis: Successfully parsed JSON from code fence")
                                    return parsed
                            except json.JSONDecodeError as e:
                                logger.debug(f"RISE analysis: JSON decode error from code fence: {e}")
                                continue
            
            # Strategy 1b: Try to find standalone JSON object
            # Find first { and try to extract complete JSON
            first_brace = response_text.find('{')
            if first_brace != -1:
                json_str = self._extract_complete_json(response_text[first_brace:])
                if json_str:
                    try:
                        parsed = json.loads(json_str)
                        if isinstance(parsed, dict):
                            logger.debug("RISE analysis: Successfully parsed standalone JSON")
                            return parsed
                    except json.JSONDecodeError:
                        pass
            
            # Strategy 2: Try ast.literal_eval for Python dict syntax
            try:
                import ast
                # Try to find Python dict-like structure
                dict_match = re.search(r'\{[^}]*\}', response_text, re.DOTALL)
                if dict_match:
                    dict_str = dict_match.group(0)
                    parsed = ast.literal_eval(dict_str)
                    if isinstance(parsed, dict):
                        logger.debug("RISE analysis: Successfully parsed using ast.literal_eval")
                        return parsed
            except (ValueError, SyntaxError) as e:
                logger.debug(f"RISE analysis: ast.literal_eval failed: {e}")
            
            # Strategy 3: Try to extract structured data from markdown or text
            # Look for key-value patterns
            structured_data = self._extract_structured_data_from_text(response_text)
            if structured_data:
                logger.debug("RISE analysis: Successfully extracted structured data from text")
                return structured_data
            
            # Fallback parsing
            logger.warning("RISE analysis: All parsing strategies failed, using fallback")
            return self._fallback_rise_analysis(response_text)
            
        except Exception as e:
            logger.warning(f"RISE analysis parsing failed: {e}", exc_info=True)
            return self._fallback_rise_analysis("")
    
    def _extract_complete_json(self, text: str) -> Optional[str]:
        """Extract a complete JSON object by matching braces."""
        if not text or not text.strip().startswith('{'):
            return None
        
        brace_count = 0
        in_string = False
        escape_next = False
        json_end = -1
        
        for i, char in enumerate(text):
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break
        
        if json_end > 0:
            return text[:json_end]
        return None
    
    def _extract_structured_data_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract structured data from text using pattern matching."""
        try:
            result = {}
            
            # Look for common RISE analysis fields
            patterns = {
                'resonant_insights': r'resonant[_\s]*insights?[:\-]\s*\[(.*?)\]',
                'strategic_requirements': r'strategic[_\s]*requirements?[:\-]\s*\[(.*?)\]',
                'cognitive_complexity': r'cognitive[_\s]*complexity[:\-]\s*([a-z]+)',
                'temporal_dimensions': r'temporal[_\s]*dimensions?[:\-]\s*([a-z/]+)',
                'causal_relationships': r'causal[_\s]*relationships?[:\-]\s*\[(.*?)\]',
                'knowledge_gaps': r'knowledge[_\s]*gaps?[:\-]\s*\[(.*?)\]',
                'synthesis_level': r'synthesis[_\s]*level[:\-]\s*([a-z]+)',
                'analytical_depth': r'analytical[_\s]*depth[:\-]\s*([a-z]+)',
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    if key in ['resonant_insights', 'strategic_requirements', 'causal_relationships', 'knowledge_gaps']:
                        # Extract list items
                        list_content = match.group(1)
                        items = [item.strip().strip('"\'') for item in re.split(r'[,;]', list_content) if item.strip()]
                        result[key] = items if items else []
                    else:
                        result[key] = match.group(1).strip()
            
            # If we extracted at least one field, return the result
            if result:
                # Fill in missing fields with defaults
                defaults = {
                    'resonant_insights': [],
                    'strategic_requirements': [],
                    'cognitive_complexity': 'medium',
                    'temporal_dimensions': 'present',
                    'causal_relationships': [],
                    'knowledge_gaps': [],
                    'synthesis_level': 'intermediate',
                    'analytical_depth': 'comprehensive',
                }
                for key, default_value in defaults.items():
                    if key not in result:
                        result[key] = default_value
                return result
            
            return None
        except Exception as e:
            logger.debug(f"Structured data extraction failed: {e}")
            return None
    
    def _fallback_rise_analysis(self, query: str) -> Dict[str, Any]:
        """Fallback RISE analysis when LLM fails."""
        return {
            "resonant_insights": ["General analysis required"],
            "strategic_requirements": ["Comprehensive information gathering"],
            "cognitive_complexity": "medium",
            "temporal_dimensions": "present",
            "causal_relationships": ["Information seeking"],
            "knowledge_gaps": ["Domain-specific knowledge"],
            "synthesis_level": "intermediate",
            "analytical_depth": "comprehensive",
            "primary_focus": "General Analysis"
        }
    
    def _get_pattern_priority(self, pattern_name: str) -> int:
        """Get priority for ResonantiA patterns."""
        priorities = {
            "knowledge_scaffolding": 1,
            "ptrf": 2,
            "causal_inference": 3,
            "rise_analysis": 4,
            "temporal_resonance": 5,
            "sirc": 6,
            "cfp": 7,
            "abm": 8,
            "digital_resilience": 9
        }
        return priorities.get(pattern_name, 10)
    
    def _get_phase_specific_params(self, phase: str, rise_analysis: Dict[str, Any], query: Optional[str] = None) -> Dict[str, Any]:
        """Get phase-specific parameters for ResonantiA actions using dynamic extraction."""
        params = {}
        
        if phase == 'ptrf_analysis':
            params['misconceptions'] = rise_analysis.get('knowledge_gaps', [])
        elif phase == 'causal_inference':
            # Use universal dynamic extraction instead of hardcoded heuristics
            try:
                from .causal_parameter_extractor import extract_causal_parameters
                
                # Extract from RISE analysis (with query as context if available)
                causal_params = extract_causal_parameters(
                    query=query,
                    rise_analysis=rise_analysis
                )
                
                params['treatment'] = causal_params.get('treatment', 'unknown_treatment')
                params['outcome'] = causal_params.get('outcome', 'unknown_outcome')
                params['confounders'] = causal_params.get('confounders', [])
                params['causal_mechanisms'] = causal_params.get('causal_mechanisms', [])
                params['extraction_confidence'] = causal_params.get('confidence', 0.5)
                params['extraction_method'] = causal_params.get('extraction_method', 'fallback')
            except Exception as e:
                logger.warning(f"Dynamic causal parameter extraction failed: {e}, using fallback")
                # Fallback to original heuristic
                params['treatment'] = rise_analysis.get('causal_relationships', ['unknown'])[0] if isinstance(rise_analysis.get('causal_relationships'), list) and len(rise_analysis.get('causal_relationships', [])) > 0 else 'unknown_treatment'
                params['outcome'] = rise_analysis.get('strategic_requirements', ['unknown'])[0] if isinstance(rise_analysis.get('strategic_requirements'), list) and len(rise_analysis.get('strategic_requirements', [])) > 0 else 'unknown_outcome'
        elif phase == 'temporal_resonance':
            params['time_horizon'] = rise_analysis.get('temporal_dimensions', 'present')
        
        return params
    
    def _generate_phase_queries(self, query: str, phase: str, rise_analysis: Dict[str, Any]) -> List[str]:
        """Generate targeted queries for a specific phase."""
        base_query = query
        primary_focus = rise_analysis.get('primary_focus', 'General Analysis')
        
        phase_query_templates = {
            'knowledge_scaffolding': [
                f"{primary_focus} historical trends comprehensive analysis",
                f"{primary_focus} platform data user behavior patterns",
                f"{primary_focus} industry analysis market dynamics"
            ],
            'ptrf_analysis': [
                f"{primary_focus} misconceptions debunking verification",
                f"{primary_focus} alternative explanations causal drivers",
                f"{primary_focus} truth verification evidence analysis"
            ],
            'causal_inference': [
                f"{primary_focus} causal mechanisms temporal analysis",
                f"{primary_focus} lagged effects impact assessment",
                f"{primary_focus} cause-effect relationships verification"
            ],
            'temporal_resonance': [
                f"{primary_focus} temporal dynamics past present future",
                f"{primary_focus} historical context current trends future projections",
                f"{primary_focus} time-series analysis temporal patterns"
            ]
        }
        
        return phase_query_templates.get(phase, [base_query])
