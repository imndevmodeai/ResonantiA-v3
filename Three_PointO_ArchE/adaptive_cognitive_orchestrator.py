"""
Adaptive Cognitive Orchestrator (ACO)
Meta-learning system that builds upon the Cognitive Resonant Controller System
to dynamically learn new domains, optimize control parameters, and evolve 
the cognitive architecture through experience.

Implements hierarchical meta-control, predictive domain detection, and
collective intelligence patterns for distributed ArchE systems.
"""

import logging
import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import time
from abc import ABC, abstractmethod

from .cognitive_resonant_controller import (
    CognitiveResonantControllerSystem, 
    FrequencyDomainController,
    DomainControllerConfig,
    ControllerPerformanceMetrics
)

logger = logging.getLogger("ACO")

@dataclass
class MetaLearningEvent:
    """Record of a learning event for pattern analysis"""
    timestamp: float
    query: str
    domain_detected: Optional[str]
    success: bool
    response_time: float
    confidence: float
    context_patterns: List[str] = field(default_factory=list)
    error_type: Optional[str] = None
    correction_applied: Optional[str] = None

@dataclass
class EmergentDomain:
    """A newly discovered query domain through pattern analysis"""
    name: str
    frequency_patterns: List[str]
    sample_queries: List[str]
    success_examples: List[str]  # Successful context extractions
    confidence_score: float
    occurrence_count: int = 0
    validation_status: str = "candidate"  # candidate, validated, production

class PatternEvolutionEngine:
    """
    Analyzes query patterns over time to discover new domains and optimize existing ones
    Implements evolutionary algorithms for controller parameter optimization
    """
    
    def __init__(self, learning_window: int = 100):
        self.learning_window = learning_window
        self.event_history: deque = deque(maxlen=learning_window)
        self.pattern_clusters: Dict[str, List[str]] = defaultdict(list)
        self.emergent_domains: Dict[str, EmergentDomain] = {}
        self.evolution_metrics = {
            'domains_discovered': 0,
            'controllers_optimized': 0,
            'false_positive_domains': 0,
            'successful_adaptations': 0
        }
    
    def analyze_event(self, event: MetaLearningEvent):
        """Analyze a single learning event for patterns"""
        self.event_history.append(event)
        
        # Extract n-grams from query for pattern analysis
        query_patterns = self._extract_query_patterns(event.query)
        event.context_patterns = query_patterns
        
        # If event failed and no domain was detected, it's a candidate for new domain
        if not event.success and not event.domain_detected:
            self._analyze_potential_new_domain(event)
        
        # Analyze for parameter optimization opportunities
        if event.domain_detected:
            self._analyze_optimization_opportunity(event)
    
    def _extract_query_patterns(self, query: str) -> List[str]:
        """Extract meaningful patterns from query text"""
        query_lower = query.lower()
        words = query_lower.replace('?', '').split()
        
        patterns = []
        
        # Unigrams (meaningful words)
        meaningful_words = [w for w in words if len(w) > 3 and w not in ['what', 'how', 'the', 'this', 'that']]
        patterns.extend(meaningful_words)
        
        # Bigrams
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if len(bigram) > 6:
                patterns.append(bigram)
        
        # Trigrams
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(trigram) > 10:
                patterns.append(trigram)
        
        return patterns
    
    def _analyze_potential_new_domain(self, event: MetaLearningEvent):
        """Analyze failed queries for potential new domain discovery"""
        # Look for similar failed queries in recent history
        similar_failures = []
        for hist_event in list(self.event_history)[-20:]:  # Look at last 20 events
            if (not hist_event.success and 
                not hist_event.domain_detected and
                self._calculate_query_similarity(event.query, hist_event.query) > 0.6):
                similar_failures.append(hist_event)
        
        if len(similar_failures) >= 3:  # Threshold for considering new domain
            domain_name = self._generate_domain_name(event.query, similar_failures)
            common_patterns = self._extract_common_patterns([event] + similar_failures)
            
            if domain_name not in self.emergent_domains:
                self.emergent_domains[domain_name] = EmergentDomain(
                    name=domain_name,
                    frequency_patterns=common_patterns,
                    sample_queries=[e.query for e in [event] + similar_failures],
                    success_examples=[],
                    confidence_score=len(similar_failures) / 10.0,  # Basic confidence
                    occurrence_count=len(similar_failures) + 1
                )
                self.evolution_metrics['domains_discovered'] += 1
                logger.info(f"Discovered potential new domain: {domain_name} with {len(common_patterns)} patterns")
    
    def _calculate_query_similarity(self, query1: str, query2: str) -> float:
        """Calculate semantic similarity between queries (simple implementation)"""
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _generate_domain_name(self, primary_query: str, similar_queries: List[MetaLearningEvent]) -> str:
        """Generate a meaningful domain name from query patterns"""
        all_queries = [primary_query] + [e.query for e in similar_queries]
        all_words = []
        for query in all_queries:
            all_words.extend(query.lower().replace('?', '').split())
        
        # Find most common meaningful words
        word_freq = defaultdict(int)
        for word in all_words:
            if len(word) > 3 and word not in ['what', 'how', 'the', 'this', 'that', 'does', 'will']:
                word_freq[word] += 1
        
        if word_freq:
            most_common = max(word_freq.items(), key=lambda x: x[1])
            return f"{most_common[0].title()}DomaiN"
        else:
            return f"UnknownDomain{len(self.emergent_domains)}"
    
    def _extract_common_patterns(self, events: List[MetaLearningEvent]) -> List[str]:
        """Extract patterns common across multiple events"""
        all_patterns = []
        for event in events:
            all_patterns.extend(event.context_patterns)
        
        pattern_freq = defaultdict(int)
        for pattern in all_patterns:
            pattern_freq[pattern] += 1
        
        # Return patterns that appear in at least 2 events
        common_patterns = [pattern for pattern, freq in pattern_freq.items() if freq >= 2]
        return common_patterns[:10]  # Limit to top 10
    
    def _analyze_optimization_opportunity(self, event: MetaLearningEvent):
        """Analyze successful events for parameter optimization opportunities"""
        # This would implement more sophisticated optimization logic
        # For now, just track that we're analyzing
        self.evolution_metrics['controllers_optimized'] += 1
    
    def get_validated_emergent_domains(self) -> List[EmergentDomain]:
        """Get domains that have enough evidence to be considered for controller creation"""
        return [domain for domain in self.emergent_domains.values() 
                if domain.occurrence_count >= 5 and domain.confidence_score > 0.3]

class AdaptiveCognitiveOrchestrator:
    """
    Meta-cognitive system that orchestrates multiple Cognitive Resonant Controller Systems
    and evolves the architecture through experience and learning
    """
    
    def __init__(self, protocol_chunks: List[str]):
        # Core controller system
        self.crcs = CognitiveResonantControllerSystem(protocol_chunks)
        
        # Meta-learning components
        self.pattern_engine = PatternEvolutionEngine()
        self.meta_learning_active = True
        
        # Predictive components
        self.query_prediction_cache: Dict[str, float] = {}
        self.domain_prediction_model = None  # Would be ML model in advanced implementation
        
        # Collective intelligence
        self.instance_knowledge: Dict[str, Any] = {}
        self.knowledge_sharing_active = False  # Would connect to ArchE registry
        
        # System evolution tracking
        self.evolution_history: List[Dict[str, Any]] = []
        self.adaptation_metrics = {
            'total_adaptations': 0,
            'successful_adaptations': 0,
            'failed_adaptations': 0,
            'new_controllers_created': 0,
            'controllers_optimized': 0
        }
        
        logger.info("Adaptive Cognitive Orchestrator initialized")
    
    def process_query_with_learning(self, query: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Process query with full learning and adaptation cycle
        """
        start_time = time.time()
        
        # Phase 1: Predictive Domain Detection
        predicted_domains = self._predict_likely_domains(query)
        
        # Phase 2: Standard processing through CRCS
        context, metrics = self.crcs.process_query(query)
        
        # Phase 3: Meta-learning event recording
        if self.meta_learning_active:
            learning_event = MetaLearningEvent(
                timestamp=time.time(),
                query=query,
                domain_detected=metrics.get('active_domain'),
                success=context is not None,
                response_time=metrics.get('response_time', 0),
                confidence=0.8 if context else 0.2,  # Simplified confidence
                error_type=None if context else "extraction_failed"
            )
            self.pattern_engine.analyze_event(learning_event)
        
        # Phase 4: Adaptive Response
        if not context:
            context = self._attempt_adaptive_extraction(query, predicted_domains)
            if context:
                metrics['extraction_method'] = 'adaptive_recovery'
                self.adaptation_metrics['successful_adaptations'] += 1
        
        # Phase 5: Evolution Check
        self._check_evolution_triggers()
        
        # Enhanced metrics
        enhanced_metrics = {
            **metrics,
            'predicted_domains': predicted_domains,
            'meta_learning_active': self.meta_learning_active,
            'emergent_domains_count': len(self.pattern_engine.emergent_domains),
            'adaptation_metrics': self.adaptation_metrics
        }
        
        return context, enhanced_metrics
    
    def _predict_likely_domains(self, query: str) -> List[str]:
        """Predict likely domains for a query based on patterns"""
        # Simple pattern matching for now - could be enhanced with ML
        query_lower = query.lower()
        predicted = []
        
        # Check against existing domain patterns
        for domain_name, controller in self.crcs.domain_controllers.items():
            for pattern in controller.config.frequency_patterns:
                if pattern in query_lower:
                    predicted.append(domain_name)
                    break
        
        # Check against emergent domains
        for domain_name, domain in self.pattern_engine.emergent_domains.items():
            for pattern in domain.frequency_patterns:
                if pattern in query_lower:
                    predicted.append(f"emergent_{domain_name}")
                    break
        
        return predicted
    
    def _attempt_adaptive_extraction(self, query: str, predicted_domains: List[str]) -> Optional[str]:
        """Attempt to extract context using adaptive strategies"""
        # Strategy 1: Try emergent domain patterns
        for domain_name in predicted_domains:
            if domain_name.startswith('emergent_'):
                actual_domain = domain_name[9:]  # Remove 'emergent_' prefix
                if actual_domain in self.pattern_engine.emergent_domains:
                    domain = self.pattern_engine.emergent_domains[actual_domain]
                    # Try pattern-based extraction
                    context = self._extract_using_emergent_patterns(query, domain)
                    if context:
                        logger.info(f"Adaptive extraction successful using emergent domain: {actual_domain}")
                        return context
        
        # Strategy 2: Expanded search with relaxed criteria
        return self._relaxed_criteria_extraction(query)
    
    def _extract_using_emergent_patterns(self, query: str, domain: EmergentDomain) -> Optional[str]:
        """Extract context using patterns from an emergent domain"""
        relevant_chunks = []
        
        for chunk in self.crcs.protocol_chunks:
            chunk_lower = chunk.lower()
            # Check if chunk contains any of the domain's patterns
            for pattern in domain.frequency_patterns:
                if pattern in chunk_lower:
                    relevant_chunks.append(chunk)
                    break
        
        if relevant_chunks:
            return "\n\n".join(relevant_chunks[:3])  # Limit to avoid overwhelming
        
        return None
    
    def _relaxed_criteria_extraction(self, query: str) -> Optional[str]:
        """Fallback extraction with relaxed matching criteria"""
        query_words = set(word.lower() for word in query.replace('?', '').split())
        
        best_chunks = []
        for chunk in self.crcs.protocol_chunks:
            chunk_words = set(chunk.lower().split())
            overlap = len(query_words.intersection(chunk_words))
            if overlap >= 2:  # Relaxed criteria - just need 2 word overlap
                best_chunks.append((chunk, overlap))
        
        if best_chunks:
            # Sort by overlap and take best
            best_chunks.sort(key=lambda x: x[1], reverse=True)
            return best_chunks[0][0]
        
        return None
    
    def _check_evolution_triggers(self):
        """Check if system should evolve by creating new controllers"""
        validated_domains = self.pattern_engine.get_validated_emergent_domains()
        
        for domain in validated_domains:
            if domain.validation_status == "candidate":
                # Create new controller for this domain
                self._create_emergent_domain_controller(domain)
                domain.validation_status = "production"
                self.adaptation_metrics['new_controllers_created'] += 1
                self.adaptation_metrics['total_adaptations'] += 1
                
                # Record evolution event
                evolution_event = {
                    'timestamp': time.time(),
                    'type': 'new_controller_created',
                    'domain_name': domain.name,
                    'patterns': domain.frequency_patterns,
                    'confidence': domain.confidence_score
                }
                self.evolution_history.append(evolution_event)
                logger.info(f"System evolved: Created new controller for domain {domain.name}")
    
    def _create_emergent_domain_controller(self, domain: EmergentDomain):
        """Create a new controller for an emergent domain"""
        # Create configuration based on domain analysis
        config = DomainControllerConfig(
            domain_name=domain.name,
            frequency_patterns=domain.frequency_patterns,
            resonant_gain=300.0,  # Start conservative
            proportional_gain=10.0,
            damping_factor=0.2,   # Start with more damping
            auto_tune=True        # Enable learning
        )
        
        # Create a generic controller (simplified for this example)
        class EmergentDomainController(FrequencyDomainController):
            def detect_frequency_domain(self, query: str) -> bool:
                query_lower = query.lower()
                return any(pattern in query_lower for pattern in self.config.frequency_patterns)
            
            def extract_specialized_context(self, chunks: List[str], query: str) -> Optional[str]:
                relevant_chunks = []
                for chunk in chunks:
                    chunk_lower = chunk.lower()
                    if any(pattern in chunk_lower for pattern in self.config.frequency_patterns):
                        relevant_chunks.append(chunk)
                
                if relevant_chunks:
                    return "\n\n".join(relevant_chunks)
                return None
        
        # Add to the controller system
        new_controller = EmergentDomainController(config)
        self.crcs.domain_controllers[domain.name] = new_controller
        logger.info(f"Created and registered new controller: {domain.name}")
    
    def get_orchestrator_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive diagnostics for the entire orchestrator system"""
        base_diagnostics = self.crcs.get_system_diagnostics()
        
        orchestrator_diagnostics = {
            **base_diagnostics,
            'orchestrator_metrics': {
                'meta_learning_active': self.meta_learning_active,
                'pattern_engine_metrics': self.pattern_engine.evolution_metrics,
                'adaptation_metrics': self.adaptation_metrics,
                'emergent_domains': {
                    name: {
                        'patterns': domain.frequency_patterns,
                        'confidence': domain.confidence_score,
                        'occurrence_count': domain.occurrence_count,
                        'status': domain.validation_status
                    }
                    for name, domain in self.pattern_engine.emergent_domains.items()
                },
                'evolution_events': len(self.evolution_history),
                'learning_window_utilization': len(self.pattern_engine.event_history)
            }
        }
        
        return orchestrator_diagnostics
    
    def enable_collective_intelligence(self, instance_registry=None):
        """Enable collective intelligence features (placeholder for distributed ArchE)"""
        self.knowledge_sharing_active = True
        # Would connect to ArchE instance registry for knowledge sharing
        logger.info("Collective intelligence capabilities enabled")
    
    def export_learned_patterns(self) -> Dict[str, Any]:
        """Export learned patterns for sharing with other ArchE instances"""
        return {
            'emergent_domains': {
                name: {
                    'patterns': domain.frequency_patterns,
                    'confidence': domain.confidence_score,
                    'sample_queries': domain.sample_queries
                }
                for name, domain in self.pattern_engine.emergent_domains.items()
                if domain.validation_status == "production"
            },
            'evolution_metrics': self.pattern_engine.evolution_metrics,
            'adaptation_success_rate': (
                self.adaptation_metrics['successful_adaptations'] / 
                max(1, self.adaptation_metrics['total_adaptations'])
            )
        }
    
    def import_learned_patterns(self, patterns: Dict[str, Any]):
        """Import learned patterns from other ArchE instances"""
        if 'emergent_domains' in patterns:
            for domain_name, domain_data in patterns['emergent_domains'].items():
                if domain_name not in self.pattern_engine.emergent_domains:
                    # Import as candidate domain
                    imported_domain = EmergentDomain(
                        name=domain_name,
                        frequency_patterns=domain_data['patterns'],
                        sample_queries=domain_data.get('sample_queries', []),
                        success_examples=[],
                        confidence_score=domain_data['confidence'] * 0.8,  # Slight discount for imported
                        validation_status="candidate"
                    )
                    self.pattern_engine.emergent_domains[domain_name] = imported_domain
                    logger.info(f"Imported emergent domain: {domain_name}") 