"""
Proactive Truth Resonance Framework (PTRF) Implementation
Based on Keyholder directive and Tesla visioning methodology

This module implements the revolutionary approach to truth-seeking that solves
the "Oracle's Paradox" by proactively identifying uncertainty and targeting
verification efforts at the weakest points in our knowledge model.

Inspired by Tesla's method of mental simulation, stress testing, and selective
physical validation.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
from urllib.parse import urlparse

# Import ArchE components
from .workflow_engine import IARCompliantWorkflowEngine
from .llm_providers import LLMProviderError, BaseLLMProvider
from .tools.search_tool import SearchTool
from .spr_manager import SPRManager

logger = logging.getLogger(__name__)

class ConsensusLevel(Enum):
    """Levels of consensus among sources"""
    HIGH = "high"           # 80%+ sources agree
    MODERATE = "moderate"   # 60-79% sources agree  
    LOW = "low"            # 40-59% sources agree
    DISPUTED = "disputed"   # <40% sources agree or major conflicts

class SourceCredibility(Enum):
    """Source credibility rankings"""
    AUTHORITATIVE = 5      # .gov, .edu, official statistics
    ESTABLISHED = 4        # Major news, established organizations
    RELIABLE = 3          # Reputable sources with track record
    QUESTIONABLE = 2      # Limited credibility indicators
    UNRELIABLE = 1        # Known issues or bias

@dataclass
class HypotheticalAnswerModel:
    """Tesla's mental blueprint - our internal model of the probable answer"""
    primary_assertion: str
    supporting_facts: List[str]
    related_entities: List[str]
    confidence_breakdown: Dict[str, float]
    overall_confidence: float
    knowledge_sources: List[str] = field(default_factory=list)
    
    def get_lowest_confidence_component(self) -> Tuple[str, float]:
        """Identify the weakest link in our knowledge chain"""
        if not self.confidence_breakdown:
            return self.primary_assertion, self.overall_confidence
            
        min_component = min(self.confidence_breakdown.items(), key=lambda x: x[1])
        return min_component

@dataclass 
class LowestConfidenceVector:
    """The 3% doubt that requires external validation"""
    statement: str
    confidence: float
    importance_to_answer: float
    verification_queries: List[str]
    expected_source_types: List[str]

@dataclass
class SourceAnalysis:
    """Analysis of a verification source"""
    url: str
    domain: str
    credibility_score: SourceCredibility
    content_relevance: float
    supports_lcv: bool
    extracted_fact: str
    confidence_in_extraction: float

@dataclass
class SolidifiedTruthPacket:
    """The final, verified and crystallized answer"""
    final_answer: str
    confidence_score: float
    verification_trail: List[str]
    source_consensus: ConsensusLevel
    conflicting_information: Optional[str]
    transparency_note: str
    crystallization_ready: bool

class TrustedSourceRegistry:
    """Registry for tracking source credibility and historical accuracy"""
    
    def __init__(self):
        self.domain_patterns = {
            # Authoritative sources
            r'.*\.gov$': SourceCredibility.AUTHORITATIVE,
            r'.*\.edu$': SourceCredibility.AUTHORITATIVE,
            r'.*\.mil$': SourceCredibility.AUTHORITATIVE,
            
            # Established organizations
            r'.*wikipedia\.org$': SourceCredibility.RELIABLE,
            r'.*britannica\.com$': SourceCredibility.ESTABLISHED,
            r'.*reuters\.com$': SourceCredibility.ESTABLISHED,
            r'.*bbc\.(com|co\.uk)$': SourceCredibility.ESTABLISHED,
            r'.*npr\.org$': SourceCredibility.ESTABLISHED,
            
            # Scientific and academic
            r'.*nature\.com$': SourceCredibility.AUTHORITATIVE,
            r'.*science\.org$': SourceCredibility.AUTHORITATIVE,
            r'.*pubmed\.ncbi\.nlm\.nih\.gov$': SourceCredibility.AUTHORITATIVE,
        }
        
        # Track historical accuracy (would be populated over time)
        self.domain_accuracy_history: Dict[str, List[float]] = {}
        
    def assess_source_credibility(self, url: str) -> SourceCredibility:
        """Assess the credibility of a source URL"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Check against known patterns
            for pattern, credibility in self.domain_patterns.items():
                if re.match(pattern, domain):
                    return credibility
                    
            # Check historical accuracy if available
            if domain in self.domain_accuracy_history:
                avg_accuracy = sum(self.domain_accuracy_history[domain]) / len(self.domain_accuracy_history[domain])
                if avg_accuracy >= 0.9:
                    return SourceCredibility.RELIABLE
                elif avg_accuracy >= 0.7:
                    return SourceCredibility.QUESTIONABLE
                else:
                    return SourceCredibility.UNRELIABLE
                    
            # Default for unknown sources
            return SourceCredibility.QUESTIONABLE
            
        except Exception as e:
            logger.warning(f"Error assessing source credibility for {url}: {e}")
            return SourceCredibility.UNRELIABLE

class ProactiveTruthSystem:
    """
    The Proactive Truth Resonance Framework Implementation
    
    Solves the Oracle's Paradox by:
    1. Building internal mental models (Tesla's visualization)
    2. Identifying uncertainty points (stress testing)
    3. Targeted verification (selective validation)
    4. Truth crystallization (refined integration)
    """
    
    def __init__(self, workflow_engine: IARCompliantWorkflowEngine, llm_provider: BaseLLMProvider, 
                 web_search_tool: SearchTool, spr_manager: SPRManager):
        self.workflow_engine = workflow_engine
        self.llm_provider = llm_provider
        self.web_search_tool = web_search_tool
        self.spr_manager = spr_manager
        self.source_registry = TrustedSourceRegistry()
        
    def seek_truth(self, query: str, accuracy_threshold: float = 0.95) -> SolidifiedTruthPacket:
        """
        Main entry point for proactive truth seeking
        
        Args:
            query: The factual question requiring high accuracy
            accuracy_threshold: Minimum confidence required (default 95%)
            
        Returns:
            SolidifiedTruthPacket with verified answer and trail
        """
        logger.info(f"Initiating Proactive Truth Resonance Framework for: {query}")
        
        try:
            # Phase 1: Inception - Generate Hypothetical Answer Model
            ham = self._generate_hypothetical_answer_model(query)
            logger.info(f"Generated HAM with overall confidence: {ham.overall_confidence}")
            
            # Check if we need verification
            if ham.overall_confidence >= accuracy_threshold:
                logger.info("Internal confidence sufficient, proceeding with internal answer")
                return self._create_stp_from_ham(ham, verified=False)
            
            # Phase 2: Conception - Identify Lowest Confidence Vector
            lcv = self._identify_lowest_confidence_vector(ham)
            logger.info(f"Identified LCV: {lcv.statement} (confidence: {lcv.confidence})")
            
            # Phase 3: Actualization - Targeted Verification
            verification_results = self._execute_targeted_verification(lcv)
            logger.info(f"Completed verification with {len(verification_results)} sources")
            
            # Phase 4: Realization - Synthesize Solidified Truth Packet
            stp = self._synthesize_solidified_truth_packet(ham, lcv, verification_results)
            logger.info(f"Created STP with final confidence: {stp.confidence_score}")
            
            return stp
            
        except Exception as e:
            logger.error(f"Error in proactive truth seeking: {e}")
            # Fallback to basic response with uncertainty note
            return SolidifiedTruthPacket(
                final_answer=f"Unable to verify with high confidence. Error: {str(e)}",
                confidence_score=0.5,
                verification_trail=[f"Error occurred: {str(e)}"],
                source_consensus=ConsensusLevel.DISPUTED,
                conflicting_information=None,
                transparency_note="Verification process failed, treat answer with caution",
                crystallization_ready=False
            )
    
    def _generate_hypothetical_answer_model(self, query: str) -> HypotheticalAnswerModel:
        """Phase 1: Tesla's mental blueprint generation"""
        
        prompt = f"""
        Generate a comprehensive Hypothetical Answer Model for this query: {query}
        
        Provide:
        1. Primary assertion (the main answer)
        2. Supporting facts (3-5 key supporting points)
        3. Related entities (people, places, concepts involved)
        4. Confidence breakdown (estimate confidence 0-1 for each component)
        5. Overall confidence assessment
        
        Be honest about uncertainty. The goal is to identify what we're most/least sure about.
        
        Format as JSON with keys: primary_assertion, supporting_facts, related_entities, confidence_breakdown, overall_confidence
        """
        
        try:
            response = self.llm_provider.generate(prompt, max_tokens=1000)
            
            # Parse the JSON response
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                data = self._extract_ham_from_text(response)
            
            ham = HypotheticalAnswerModel(
                primary_assertion=data.get('primary_assertion', 'Unable to determine'),
                supporting_facts=data.get('supporting_facts', []),
                related_entities=data.get('related_entities', []),
                confidence_breakdown=data.get('confidence_breakdown', {}),
                overall_confidence=data.get('overall_confidence', 0.5),
                knowledge_sources=['internal_kno']
            )
            
            return ham
            
        except Exception as e:
            logger.error(f"Error generating HAM: {e}")
            # Create minimal HAM
            return HypotheticalAnswerModel(
                primary_assertion=f"Unable to generate reliable answer for: {query}",
                supporting_facts=[],
                related_entities=[],
                confidence_breakdown={},
                overall_confidence=0.3,
                knowledge_sources=[]
            )
    
    def _identify_lowest_confidence_vector(self, ham: HypotheticalAnswerModel) -> LowestConfidenceVector:
        """Phase 2: Tesla's stress point identification"""
        
        # Find the component with lowest confidence
        lcv_component, lcv_confidence = ham.get_lowest_confidence_component()
        
        prompt = f"""
        Analyze this Hypothetical Answer Model to identify the Lowest Confidence Vector (LCV):
        
        Primary Assertion: {ham.primary_assertion}
        Supporting Facts: {ham.supporting_facts}
        Confidence Breakdown: {ham.confidence_breakdown}
        
        The component with lowest confidence appears to be: {lcv_component} (confidence: {lcv_confidence})
        
        Generate:
        1. A clear statement of what needs verification
        2. Its importance to the overall answer (0-1 scale)
        3. 2-3 targeted search queries to verify this specific point
        4. Expected types of authoritative sources that could verify this
        
        Format as JSON with keys: statement, importance_to_answer, verification_queries, expected_source_types
        """
        
        try:
            response = self.llm_provider.generate(prompt, max_tokens=500)
            data = json.loads(response)
            
            return LowestConfidenceVector(
                statement=data.get('statement', lcv_component),
                confidence=lcv_confidence,
                importance_to_answer=data.get('importance_to_answer', 0.8),
                verification_queries=data.get('verification_queries', [lcv_component]),
                expected_source_types=data.get('expected_source_types', ['authoritative'])
            )
            
        except Exception as e:
            logger.error(f"Error identifying LCV: {e}")
            return LowestConfidenceVector(
                statement=lcv_component,
                confidence=lcv_confidence,
                importance_to_answer=0.5,
                verification_queries=[lcv_component],
                expected_source_types=['any']
            )
    
    def _execute_targeted_verification(self, lcv: LowestConfidenceVector) -> List[SourceAnalysis]:
        """Phase 3: Tesla's selective validation"""
        
        all_results = []
        
        for query in lcv.verification_queries:
            try:
                # Execute web search
                search_results = self.web_search_tool.search(query, num_results=8)
                
                # Analyze each result
                for result in search_results.get('results', []):
                    analysis = self._analyze_source(result, lcv)
                    if analysis:
                        all_results.append(analysis)
                        
            except Exception as e:
                logger.error(f"Error in verification search for '{query}': {e}")
                continue
        
        # Sort by credibility and relevance
        all_results.sort(key=lambda x: (x.credibility_score.value, x.content_relevance), reverse=True)
        
        return all_results[:10]  # Top 10 most credible and relevant
    
    def _analyze_source(self, search_result: Dict, lcv: LowestConfidenceVector) -> Optional[SourceAnalysis]:
        """Analyze a single source for credibility and relevance"""
        
        try:
            url = search_result.get('url', '')
            title = search_result.get('title', '')
            snippet = search_result.get('snippet', '')
            
            if not url:
                return None
            
            # Assess credibility
            credibility = self.source_registry.assess_source_credibility(url)
            
            # Assess relevance and extract fact
            relevance_prompt = f"""
            Analyze this search result for relevance to our verification target:
            
            Target to verify: {lcv.statement}
            
            Source URL: {url}
            Title: {title}
            Snippet: {snippet}
            
            Provide:
            1. Relevance score (0-1) - how relevant is this to our verification target?
            2. Does this support our target statement? (true/false)
            3. What specific fact does this source provide about our target?
            4. Confidence in the fact extraction (0-1)
            
            Format as JSON: {{"relevance": 0.8, "supports_lcv": true, "extracted_fact": "...", "extraction_confidence": 0.9}}
            """
            
            response = self.llm_provider.generate(relevance_prompt, max_tokens=300)
            analysis_data = json.loads(response)
            
            return SourceAnalysis(
                url=url,
                domain=urlparse(url).netloc,
                credibility_score=credibility,
                content_relevance=analysis_data.get('relevance', 0.5),
                supports_lcv=analysis_data.get('supports_lcv', False),
                extracted_fact=analysis_data.get('extracted_fact', snippet),
                confidence_in_extraction=analysis_data.get('extraction_confidence', 0.5)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing source {search_result.get('url', 'unknown')}: {e}")
            return None
    
    def _synthesize_solidified_truth_packet(self, ham: HypotheticalAnswerModel, 
                                          lcv: LowestConfidenceVector, 
                                          verification_results: List[SourceAnalysis]) -> SolidifiedTruthPacket:
        """Phase 4: Tesla's refined design integration"""
        
        # Analyze consensus
        supporting_sources = [r for r in verification_results if r.supports_lcv]
        conflicting_sources = [r for r in verification_results if not r.supports_lcv]
        
        # Weight by credibility
        total_credibility_weight = sum(r.credibility_score.value for r in verification_results)
        supporting_weight = sum(r.credibility_score.value for r in supporting_sources)
        
        consensus_ratio = supporting_weight / total_credibility_weight if total_credibility_weight > 0 else 0.5
        
        # Determine consensus level
        if consensus_ratio >= 0.8:
            consensus = ConsensusLevel.HIGH
        elif consensus_ratio >= 0.6:
            consensus = ConsensusLevel.MODERATE
        elif consensus_ratio >= 0.4:
            consensus = ConsensusLevel.LOW
        else:
            consensus = ConsensusLevel.DISPUTED
        
        # Create synthesis prompt
        synthesis_prompt = f"""
        Synthesize the final answer by integrating verified information:
        
        Original Answer Model: {ham.primary_assertion}
        Supporting Facts: {ham.supporting_facts}
        
        Verification Target: {lcv.statement}
        
        Verification Results:
        - Supporting sources: {len(supporting_sources)}
        - Conflicting sources: {len(conflicting_sources)}
        - Consensus level: {consensus.value}
        - Top supporting facts: {[r.extracted_fact for r in supporting_sources[:3]]}
        
        Create the final, integrated answer that:
        1. Incorporates the verified information
        2. Acknowledges any conflicts or uncertainties
        3. Provides appropriate confidence level
        
        Format as JSON: {{"final_answer": "...", "confidence_score": 0.95, "key_verification_points": ["..."]}}
        """
        
        try:
            response = self.llm_provider.generate(synthesis_prompt, max_tokens=800)
            synthesis_data = json.loads(response)
            
            # Build verification trail
            verification_trail = [
                f"Original internal confidence: {ham.overall_confidence:.2f}",
                f"Verification target: {lcv.statement}",
                f"Sources analyzed: {len(verification_results)}",
                f"Consensus level: {consensus.value}",
                f"Top sources: {[r.domain for r in verification_results[:3]]}"
            ]
            
            # Handle conflicts
            conflicting_info = None
            if conflicting_sources:
                conflicting_info = f"Conflicting information found in {len(conflicting_sources)} sources"
            
            # Create transparency note
            transparency_note = f"Answer verified through {len(verification_results)} sources with {consensus.value} consensus"
            
            return SolidifiedTruthPacket(
                final_answer=synthesis_data.get('final_answer', ham.primary_assertion),
                confidence_score=min(synthesis_data.get('confidence_score', 0.8), 0.99),  # Cap at 99%
                verification_trail=verification_trail,
                source_consensus=consensus,
                conflicting_information=conflicting_info,
                transparency_note=transparency_note,
                crystallization_ready=consensus in [ConsensusLevel.HIGH, ConsensusLevel.MODERATE]
            )
            
        except Exception as e:
            logger.error(f"Error in synthesis: {e}")
            # Fallback synthesis
            return SolidifiedTruthPacket(
                final_answer=ham.primary_assertion,
                confidence_score=max(ham.overall_confidence, 0.6),
                verification_trail=[f"Synthesis error: {str(e)}"],
                source_consensus=ConsensusLevel.DISPUTED,
                conflicting_information="Synthesis process failed",
                transparency_note="Unable to complete full verification synthesis",
                crystallization_ready=False
            )
    
    def _create_stp_from_ham(self, ham: HypotheticalAnswerModel, verified: bool = False) -> SolidifiedTruthPacket:
        """Create STP directly from HAM when verification not needed"""
        
        return SolidifiedTruthPacket(
            final_answer=ham.primary_assertion,
            confidence_score=ham.overall_confidence,
            verification_trail=["High internal confidence, verification not required"],
            source_consensus=ConsensusLevel.HIGH if verified else ConsensusLevel.MODERATE,
            conflicting_information=None,
            transparency_note="Answer based on high-confidence internal knowledge",
            crystallization_ready=True
        )
    
    def _extract_ham_from_text(self, text: str) -> Dict[str, Any]:
        """Fallback method to extract HAM data from non-JSON text"""
        # Basic extraction logic for when JSON parsing fails
        return {
            'primary_assertion': 'Unable to parse structured response',
            'supporting_facts': [],
            'related_entities': [],
            'confidence_breakdown': {},
            'overall_confidence': 0.5
        }

# Integration with existing ArchE workflow system
def register_proactive_truth_workflow():
    """Register the PTRF workflow with the ArchE system"""
    
    workflow_definition = {
        "workflow_id": "proactive_truth_seeking_v1",
        "description": "Proactive Truth Resonance Framework - Tesla visioning approach to truth verification",
        "steps": [
            # Workflow steps would be defined here
            # This integrates with the JSON workflow definition created above
        ]
    }
    
    return workflow_definition

# Example usage and testing
if __name__ == "__main__":
    # This would be used for testing the system
    print("Proactive Truth Resonance Framework - Tesla visioning implementation")
    print("Solving the Oracle's Paradox through proactive uncertainty identification") 