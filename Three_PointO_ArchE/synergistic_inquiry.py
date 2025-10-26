"""
Synergistic Inquiry and Synthesis Protocol Orchestrator

This module implements the core logic for the PhD-level genius search protocol.
It deconstructs queries, dispatches tasks to federated agents, and prepares
the multi-modal results for final synthesis.

This architecture aligns with Mandate 4 (The Archeologist) and Mandate 8 (The Crystal).
"""

import logging
from typing import List, Dict, Any

from .federated_search_agents import (
    AcademicKnowledgeAgent,
    CommunityPulseAgent,
    CodebaseTruthAgent,
    VisualSynthesisAgent,
    SearchEngineAgent
)
from .synthesis_engine import SynthesisEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SynergisticInquiryOrchestrator:
    """Orchestrates the federated search and synthesis process."""
    def __init__(self):
        self.agents = {
            'academic': AcademicKnowledgeAgent(),
            'community': CommunityPulseAgent(),
            'code': CodebaseTruthAgent(),
            'visual': VisualSynthesisAgent(),
            'startpage': SearchEngineAgent("Startpage")
        }
        self.synthesis_engine = SynthesisEngine()
        logger.info("Synergistic Inquiry Orchestrator initialized with 5 specialized agents and a Synthesis Engine.")

    def deconstruct_query(self, query: str) -> Dict[str, str]:
        """
        Deconstructs a user query into targeted vectors for each agent using RISE-inspired methodology.
        
        This implementation follows the RISE Knowledge Scaffolding approach:
        1. Problem deconstruction using LLM
        2. Domain extraction and analysis
        3. Targeted query generation for each source type
        """
        logger.info(f"Deconstructing query using RISE-inspired methodology: '{query[:100]}...'")
        
        try:
            # Phase 1: Problem Deconstruction (RISE-inspired)
            deconstruction = self._deconstruct_problem_with_llm(query)
            
            # Phase 2: Domain Extraction
            primary_domain = self._extract_primary_domain(deconstruction)
            
            # Phase 3: Generate targeted vectors for each agent
            vectors = self._generate_targeted_vectors(query, deconstruction, primary_domain)
            
            logger.debug(f"Generated targeted query vectors: {vectors}")
            return vectors
            
        except Exception as e:
            logger.warning(f"LLM-based deconstruction failed: {e}. Falling back to simple approach.")
            # Fallback to simple approach
            vectors = {
                'academic': f"{query} academic review research",
                'community': f"{query} reddit discussion community",
                'code': f"{query} github implementation code",
                'visual': f"{query} youtube tutorial video",
                'startpage': f"{query} best practices latest trends"
            }
            return vectors

    def _deconstruct_problem_with_llm(self, query: str) -> Dict[str, Any]:
        """
        Deconstruct the problem using LLM analysis (RISE-inspired approach).
        """
        try:
            # Use the synthesis engine's LLM for deconstruction
            deconstruction_prompt = f"""
            Analyze the following query and deconstruct it into core components:

            Query: {query}

            IMPORTANT: Preserve the specific domain/topic area in your analysis. Do not focus only on action words like "analyze" or "generate".

            Identify:
            1. Core domain areas (the main subject matter/topic)
            2. Key variables and unknowns  
            3. Strategic requirements
            4. Risk factors
            5. Success criteria
            6. Search intent (what information is being sought)

            Output your analysis as a structured JSON object with these keys:
            - core_domains: [list of domain areas - be specific about the topic]
            - key_variables: [list of variables/unknowns]
            - strategic_requirements: [list of requirements]
            - risk_factors: [list of potential risks]
            - success_criteria: [list of success criteria]
            - search_intent: [description of what information is being sought]
            - primary_focus: [the main topic/domain being analyzed, not the action being performed]
            """
            
            # Use the synthesis engine's LLM provider
            llm_response = self.synthesis_engine.llm_provider.generate_chat(
                messages=[{"role": "user", "content": deconstruction_prompt}],
                max_tokens=2048,
                temperature=0.3
            )
            
            # Parse the response
            if isinstance(llm_response, dict):
                response_text = llm_response.get("generated_text", "")
            else:
                response_text = str(llm_response)
            
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Fallback: create structured response from text
            return {
                "core_domains": ["General Analysis"],
                "key_variables": ["information", "insights"],
                "strategic_requirements": ["comprehensive_analysis"],
                "risk_factors": ["information_gaps"],
                "success_criteria": ["actionable_insights"],
                "search_intent": "comprehensive information gathering",
                "primary_focus": "General Analysis",
                "raw_response": response_text
            }
            
        except Exception as e:
            logger.warning(f"LLM deconstruction failed: {e}")
            return {
                "core_domains": ["General Analysis"],
                "key_variables": ["information"],
                "strategic_requirements": ["analysis"],
                "risk_factors": ["unknown"],
                "success_criteria": ["insights"],
                "search_intent": "information gathering",
                "primary_focus": "General Analysis"
            }

    def _extract_primary_domain(self, deconstruction: Dict[str, Any]) -> str:
        """
        Extract the primary domain from the deconstruction analysis.
        """
        primary_focus = deconstruction.get("primary_focus", "")
        core_domains = deconstruction.get("core_domains", [])
        
        if primary_focus and primary_focus != "General Analysis":
            return primary_focus
        
        if core_domains and len(core_domains) > 0:
            return core_domains[0]
        
        return "General Analysis"

    def _generate_targeted_vectors(self, original_query: str, deconstruction: Dict[str, Any], primary_domain: str) -> Dict[str, str]:
        """
        Generate targeted search vectors for each agent based on deconstruction analysis.
        """
        search_intent = deconstruction.get("search_intent", "information gathering")
        key_variables = deconstruction.get("key_variables", [])
        
        # Create targeted vectors for each agent type
        vectors = {}
        
        # Academic Agent: Focus on research, papers, studies
        academic_terms = ["research", "study", "analysis", "academic", "paper", "journal"]
        if primary_domain != "General Analysis":
            academic_query = f"{primary_domain} {' '.join(academic_terms[:3])}"
        else:
            # Use much more of the original query for robust, accurate results
            academic_query = f"{original_query[:800]} {' '.join(academic_terms[:2])}"
        vectors['academic'] = academic_query
        
        # Community Agent: Focus on discussions, opinions, real-world experiences
        community_terms = ["discussion", "opinion", "experience", "community", "reddit", "forum"]
        if primary_domain != "General Analysis":
            community_query = f"{primary_domain} {' '.join(community_terms[:3])}"
        else:
            # Use much more of the original query for robust, accurate results
            community_query = f"{original_query[:800]} {' '.join(community_terms[:2])}"
        vectors['community'] = community_query
        
        # Code Agent: Focus on implementations, repositories, technical solutions
        code_terms = ["implementation", "code", "github", "repository", "technical", "solution"]
        if primary_domain != "General Analysis":
            code_query = f"{primary_domain} {' '.join(code_terms[:3])}"
        else:
            # Use much more of the original query for robust, accurate results
            code_query = f"{original_query[:800]} {' '.join(code_terms[:2])}"
        vectors['code'] = code_query
        
        # Visual Agent: Focus on tutorials, demonstrations, visual content
        visual_terms = ["tutorial", "demo", "video", "youtube", "explanation", "guide"]
        if primary_domain != "General Analysis":
            visual_query = f"{primary_domain} {' '.join(visual_terms[:3])}"
        else:
            # Use much more of the original query for robust, accurate results
            visual_query = f"{original_query[:800]} {' '.join(visual_terms[:2])}"
        vectors['visual'] = visual_query
        
        # Search Engine Agent: Use optimized query for Startpage (working)
        search_engine_query = self._optimize_for_search_engines(original_query, primary_domain, deconstruction)
        vectors['startpage'] = search_engine_query
        
        return vectors

    def _optimize_for_search_engines(self, original_query: str, primary_domain: str, deconstruction: Dict[str, Any]) -> str:
        """
        Optimize search queries specifically for search engines using platform-specific techniques.
        """
        # Get platform-specific search tips
        search_tips = self._get_platform_search_tips()
        
        # Build optimized query
        optimized_parts = []
        
        # Add primary domain if available
        if primary_domain != "General Analysis":
            optimized_parts.append(primary_domain)
        else:
            # For general analysis, use more of the original query to preserve context
            optimized_parts.append(original_query[:600])  # Use significant portion of original query
        
        # Add key terms from deconstruction
        key_variables = deconstruction.get("key_variables", [])
        if key_variables:
            optimized_parts.extend(key_variables[:4])  # Increased from 2 to 4 for more context
        
        # Add search optimization terms
        optimization_terms = search_tips.get("general_optimization", [])
        if optimization_terms:
            optimized_parts.extend(optimization_terms[:2])
        
        # Fallback to truncated original query
        if not optimized_parts:
            optimized_parts.append(original_query[:800])  # Increased significantly for robust results
        
        return " ".join(optimized_parts)

    def _get_platform_search_tips(self) -> Dict[str, List[str]]:
        """
        Get platform-specific search optimization tips and techniques.
        This could be enhanced by searching for current best practices.
        """
        return {
            "general_optimization": [
                "best practices",
                "latest trends",
                "comprehensive guide",
                "expert insights"
            ],
            "academic_optimization": [
                "research paper",
                "peer reviewed",
                "academic study",
                "scientific analysis"
            ],
            "community_optimization": [
                "real world experience",
                "community discussion",
                "user feedback",
                "practical advice"
            ],
            "code_optimization": [
                "open source",
                "implementation",
                "code example",
                "technical solution"
            ],
            "visual_optimization": [
                "step by step tutorial",
                "visual demonstration",
                "hands on guide",
                "practical example"
            ]
        }

    def execute_inquiry(self, query: str, max_results_per_agent: int = 5) -> List[Dict[str, Any]]:
        """
        Executes the full Synergistic Inquiry and Synthesis Protocol.
        
        Phase 1: Query Deconstruction
        Phase 2: Federated, Source-Aware Inquiry
        """
        # Phase 1: Deconstruct the query
        query_vectors = self.deconstruct_query(query)
        
        # Phase 2: Execute inquiry across federated agents in parallel (conceptually)
        all_results = []
        for agent_type, agent_query in query_vectors.items():
            agent = self.agents.get(agent_type)
            if agent:
                try:
                    results = agent.search(agent_query, max_results=max_results_per_agent)
                    logger.info(f"Agent '{agent.name}' found {len(results)} results.")
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Agent '{agent.name}' failed during search: {e}")
            else:
                logger.warning(f"No agent found for type: {agent_type}")
        
        logger.info(f"Synergistic inquiry complete. Total results gathered: {len(all_results)}")
        return all_results

    def synthesize_and_reflect(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Phase 3 & 4: Invokes the Synthesis Engine to perform deep synthesis and reflection.
        """
        logger.info("Handing off to Synthesis Engine for final processing.")
        return self.synthesis_engine.synthesize(query, results)
