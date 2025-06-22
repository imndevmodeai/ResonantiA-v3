"""
Cognitive Resonant Controller System (CRCS)
A generalized implementation of Proportional Resonant Controller principles 
for cognitive architecture error elimination across multiple frequency domains.

Based on successful Implementation Resonance controller demonstration.
"""

import logging
import json
import math
import re
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

logger = logging.getLogger("CRCS")

@dataclass
class ControllerPerformanceMetrics:
    """Track performance metrics for each controller domain"""
    domain: str
    queries_processed: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    average_response_time: float = 0.0
    error_magnitude_reduction: float = 0.0
    confidence_scores: List[float] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        if self.queries_processed == 0:
            return 0.0
        return self.successful_extractions / self.queries_processed
    
    @property
    def average_confidence(self) -> float:
        if not self.confidence_scores:
            return 0.0
        return sum(self.confidence_scores) / len(self.confidence_scores)

@dataclass
class DomainControllerConfig:
    """Configuration for a specific frequency domain controller"""
    domain_name: str
    frequency_patterns: List[str]  # Trigger patterns for this domain
    resonant_gain: float = 500.0   # Ki - specialized extraction gain
    proportional_gain: float = 10.0  # Kp - general error correction
    damping_factor: float = 0.1    # wc - operational flexibility
    extraction_strategy: str = "chunk_aggregation"  # How to extract for this domain
    context_window: int = 3        # Number of surrounding chunks to include
    confidence_threshold: float = 0.7  # Minimum confidence for success
    auto_tune: bool = True         # Whether to automatically adjust gains

class FrequencyDomainController(ABC):
    """Abstract base class for domain-specific controllers"""
    
    def __init__(self, config: DomainControllerConfig):
        self.config = config
        self.metrics = ControllerPerformanceMetrics(domain=config.domain_name)
        
    @abstractmethod
    def detect_frequency_domain(self, query: str) -> bool:
        """Detect if query belongs to this frequency domain"""
        pass
    
    @abstractmethod
    def extract_specialized_context(self, chunks: List[str], query: str) -> Optional[str]:
        """Apply specialized extraction for this domain"""
        pass
    
    def update_performance(self, success: bool, confidence: float, response_time: float):
        """Update performance metrics and auto-tune if enabled"""
        self.metrics.queries_processed += 1
        if success:
            self.metrics.successful_extractions += 1
        else:
            self.metrics.failed_extractions += 1
        
        self.metrics.confidence_scores.append(confidence)
        self.metrics.average_response_time = (
            (self.metrics.average_response_time * (self.metrics.queries_processed - 1) + response_time) 
            / self.metrics.queries_processed
        )
        
        # Auto-tuning logic
        if self.config.auto_tune and self.metrics.queries_processed % 10 == 0:
            self._auto_tune_parameters()
    
    def _auto_tune_parameters(self):
        """Automatically adjust controller parameters based on performance"""
        success_rate = self.metrics.success_rate
        avg_confidence = self.metrics.average_confidence
        
        # Increase resonant gain if success rate is low but confidence is high
        if success_rate < 0.7 and avg_confidence > 0.6:
            self.config.resonant_gain *= 1.1
            logger.info(f"Auto-tuned {self.config.domain_name}: Increased resonant gain to {self.config.resonant_gain}")
        
        # Decrease damping if success rate is high (allow more precision)
        elif success_rate > 0.9:
            self.config.damping_factor *= 0.95
            logger.info(f"Auto-tuned {self.config.domain_name}: Decreased damping to {self.config.damping_factor}")

class ImplementationResonanceController(FrequencyDomainController):
    """Specialized controller for Implementation Resonance queries"""
    
    def detect_frequency_domain(self, query: str) -> bool:
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in self.config.frequency_patterns)
    
    def extract_specialized_context(self, chunks: List[str], query: str) -> Optional[str]:
        """High-gain extraction for Implementation Resonance domain"""
        relevant_chunks = []
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            if any(pattern in chunk_lower for pattern in [
                'implementation resonance', 'jedi principle 6', 'bridge the worlds', 
                'as above so below'
            ]):
                relevant_chunks.append(chunk)
        
        if relevant_chunks:
            combined_context = "\n\n".join(relevant_chunks)
            logger.info(f"Implementation Resonance Controller: Found {len(relevant_chunks)} relevant chunks")
            return combined_context
        
        return None

class SPRController(FrequencyDomainController):
    """Specialized controller for SPR-related queries"""
    
    def detect_frequency_domain(self, query: str) -> bool:
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in self.config.frequency_patterns)
    
    def extract_specialized_context(self, chunks: List[str], query: str) -> Optional[str]:
        """Extract SPR definitions and Guardian Points patterns"""
        relevant_chunks = []
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            if any(pattern in chunk_lower for pattern in [
                'guardian points', 'sparse priming representation', 'spr', 
                'cognitive keys', 'resonant patterns'
            ]) or self._contains_guardian_points_pattern(chunk):
                relevant_chunks.append(chunk)
        
        if relevant_chunks:
            combined_context = "\n\n".join(relevant_chunks)
            logger.info(f"SPR Controller: Found {len(relevant_chunks)} SPR-related chunks")
            return combined_context
        
        return None
    
    def _contains_guardian_points_pattern(self, text: str) -> bool:
        """Detect Guardian Points pattern: CapitalLetter...lowercase...CapitalLetter"""
        pattern = r'\b[A-Z0-9][a-z]+(?:\s+[a-z]+)*\s+[A-Z0-9]\b'
        return bool(re.search(pattern, text))

class ProportionalResonantController(FrequencyDomainController):
    """Specialized controller for Proportional Resonant Control Pattern queries"""
    
    def detect_frequency_domain(self, query: str) -> bool:
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in self.config.frequency_patterns)
    
    def extract_specialized_context(self, chunks: List[str], query: str) -> Optional[str]:
        """Extract context related to Proportional Resonant Control patterns"""
        relevant_chunks = []
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            if any(pattern in chunk_lower for pattern in [
                'proportional resonant', 'pr controller', 'frequency domain', 'resonant gain',
                'oscillatory error', 'control pattern', 'proportionalresonantcontrolpattern'
            ]):
                relevant_chunks.append(chunk)
        
        if relevant_chunks:
            combined_context = "\n\n".join(relevant_chunks)
            logger.info(f"Proportional Resonant Controller: Found {len(relevant_chunks)} relevant chunks")
            return combined_context
        
        return None

class CognitiveResonantControllerSystem:
    """
    Master controller system managing multiple frequency domain controllers
    Implements hierarchical control architecture with learning capabilities
    """
    
    def __init__(self, protocol_chunks: List[str]):
        self.protocol_chunks = protocol_chunks
        self.domain_controllers: Dict[str, FrequencyDomainController] = {}
        self.general_controller_params = {
            'proportional_gain': 10.0,
            'integration_time': 1.0,
            'damping': 0.1
        }
        self.system_metrics = {
            'total_queries': 0,
            'successful_domains': 0,
            'fallback_activations': 0,
            'learning_events': 0
        }
        
        self._initialize_default_controllers()
        logger.info("Cognitive Resonant Controller System initialized")
    
    def _initialize_default_controllers(self):
        """Initialize the proven domain controllers"""
        
        # Implementation Resonance Controller (proven successful)
        impl_config = DomainControllerConfig(
            domain_name="ImplementationResonance",
            frequency_patterns=['implementation resonance', 'jedi principle 6', 'bridge the worlds'],
            resonant_gain=500.0,
            proportional_gain=10.0,
            damping_factor=0.1
        )
        self.domain_controllers["ImplementationResonance"] = ImplementationResonanceController(impl_config)
        
        # SPR Controller 
        spr_config = DomainControllerConfig(
            domain_name="SPRQueries",
            frequency_patterns=['spr', 'sparse priming', 'guardian points', 'cognitive keys'],
            resonant_gain=400.0,
            proportional_gain=15.0,
            damping_factor=0.15
        )
        self.domain_controllers["SPRQueries"] = SPRController(spr_config)
        
        # Proportional Resonant Controller (NEW!)
        pr_config = DomainControllerConfig(
            domain_name="ProportionalResonantQueries",
            frequency_patterns=['proportional resonant', 'pr controller', 'proportionalresonantcontrolpattern'],
            resonant_gain=450.0,
            proportional_gain=12.0,
            damping_factor=0.12
        )
        self.domain_controllers["ProportionalResonantQueries"] = ProportionalResonantController(pr_config)
        
        logger.info(f"Initialized {len(self.domain_controllers)} domain controllers")
    
    def process_query(self, query: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Main query processing with multi-domain controller selection
        Returns: (extracted_context, control_metrics)
        """
        start_time = time.time()
        self.system_metrics['total_queries'] += 1
        
        # Phase 1: Domain Detection & Controller Selection
        active_controllers = []
        for domain_name, controller in self.domain_controllers.items():
            if controller.detect_frequency_domain(query):
                active_controllers.append((domain_name, controller))
                logger.info(f"Activated {domain_name} controller for query")
        
        # Phase 2: Specialized Extraction
        if active_controllers:
            self.system_metrics['successful_domains'] += 1
            
            for domain_name, controller in active_controllers:
                context = controller.extract_specialized_context(self.protocol_chunks, query)
                if context:
                    response_time = time.time() - start_time
                    controller.update_performance(True, 0.85, response_time)
                    
                    return context, {
                        'active_domain': domain_name,
                        'controller_used': controller.__class__.__name__,
                        'extraction_method': 'specialized_resonant',
                        'response_time': response_time,
                        'chunks_found': len(context.split('\n\n')),
                        'system_metrics': self.system_metrics
                    }
        
        # Phase 3: Fallback to General Proportional Control
        self.system_metrics['fallback_activations'] += 1
        logger.info("No specialized controller activated, using general proportional control")
        return self._general_proportional_extraction(query), {
            'active_domain': 'General',
            'controller_used': 'ProportionalControl',
            'extraction_method': 'tfidf_fallback',
            'response_time': time.time() - start_time,
            'system_metrics': self.system_metrics
        }
    
    def _general_proportional_extraction(self, query: str) -> Optional[str]:
        """Fallback TF-IDF based extraction for unrecognized domains"""
        query_words = set(word.lower() for word in query.replace('?', '').split())
        num_chunks = len(self.protocol_chunks)
        
        if num_chunks == 0:
            return None
        
        idf = {
            word: math.log(num_chunks / max(1, sum(1 for chunk in self.protocol_chunks if word in chunk.lower())))
            for word in query_words
        }
        
        best_chunk, max_score = None, 0
        for chunk in self.protocol_chunks:
            words_in_chunk = chunk.lower().split()
            chunk_word_count = len(words_in_chunk)
            if chunk_word_count == 0:
                continue
                
            tfidf_score = sum(
                (words_in_chunk.count(word) / chunk_word_count) * idf[word] 
                for word in query_words
            )
            
            if tfidf_score > max_score:
                max_score, best_chunk = tfidf_score, chunk
        
        if best_chunk and max_score > 0.01:
            logger.info(f"General controller: Found context (TF-IDF Score: {max_score:.4f})")
            return best_chunk
        
        return None
    
    def get_system_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive system diagnostics"""
        diagnostics = {
            'system_metrics': self.system_metrics,
            'domain_controllers': {}
        }
        
        for domain_name, controller in self.domain_controllers.items():
            diagnostics['domain_controllers'][domain_name] = {
                'performance': {
                    'domain': controller.metrics.domain,
                    'queries_processed': controller.metrics.queries_processed,
                    'successful_extractions': controller.metrics.successful_extractions,
                    'failed_extractions': controller.metrics.failed_extractions,
                    'success_rate': controller.metrics.success_rate,
                    'average_confidence': controller.metrics.average_confidence,
                    'average_response_time': controller.metrics.average_response_time
                },
                'config': {
                    'domain_name': controller.config.domain_name,
                    'frequency_patterns': controller.config.frequency_patterns,
                    'resonant_gain': controller.config.resonant_gain,
                    'proportional_gain': controller.config.proportional_gain,
                    'damping_factor': controller.config.damping_factor
                }
            }
        
        return diagnostics

# Import time for timing measurements
import time 