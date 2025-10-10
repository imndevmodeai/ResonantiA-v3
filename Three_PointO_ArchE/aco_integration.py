"""
ACO Integration: Pattern Detection from ThoughtTrail
====================================================

This module integrates the Adaptive Cognitive Orchestrator (ACO) with the ThoughtTrail
to enable automatic pattern detection and instinct formation based on system behavior.

The ACO listens to ThoughtTrail triggers and analyzes patterns to propose new
controllers and optimizations for ArchE's cognitive architecture.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque

from Three_PointO_ArchE.nexus_interface import NexusInterface
from Three_PointO_ArchE.thought_trail import thought_trail

logger = logging.getLogger(__name__)

class PatternEvolutionEngine:
    """
    Engine for detecting emergent patterns and creating new domain controllers.
    Implements meta-learning capabilities for cognitive architecture evolution.
    """
    
    def __init__(self):
        self.query_history = deque(maxlen=1000)  # Rolling window of queries
        self.pattern_signatures = {}  # Pattern hash -> metadata
        self.emergent_domains = {}  # Potential new domains detected
        self.learning_threshold = 5  # Minimum occurrences to consider pattern
        self.confidence_threshold = 0.7  # Minimum confidence for domain creation
        
        logger.info("[PatternEngine] Initialized with learning capabilities")
    
    def analyze_query_pattern(self, query: str, success: bool, active_domain: str) -> Dict[str, Any]:
        """
        Analyze query for emergent patterns and learning opportunities
        
        Args:
            query: The user query
            success: Whether the query was successfully processed
            active_domain: Which domain controller was activated
            
        Returns:
            Dict containing pattern analysis results
        """
        # Create pattern signature
        pattern_signature = self._create_pattern_signature(query)
        
        # Record query in history
        query_record = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'pattern_signature': pattern_signature,
            'success': success,
            'active_domain': active_domain,
            'query_length': len(query),
            'word_count': len(query.split())
        }
        
        self.query_history.append(query_record)
        
        # Update pattern tracking
        if pattern_signature not in self.pattern_signatures:
            self.pattern_signatures[pattern_signature] = {
                'first_seen': datetime.now().isoformat(),
                'occurrences': 0,
                'success_count': 0,
                'failure_count': 0,
                'domains_activated': set(),
                'sample_queries': []
            }
        
        pattern_data = self.pattern_signatures[pattern_signature]
        pattern_data['occurrences'] += 1
        pattern_data['domains_activated'].add(active_domain)
        
        if success:
            pattern_data['success_count'] += 1
        else:
            pattern_data['failure_count'] += 1
            
        # Store a few sample queries for analysis
        if len(pattern_data['sample_queries']) < 3:
            pattern_data['sample_queries'].append(query)
        
        # Check for emergent domain potential
        emergent_analysis = self._analyze_emergent_potential(pattern_signature, pattern_data)
        
        return {
            'pattern_signature': pattern_signature,
            'occurrences': pattern_data['occurrences'],
            'success_rate': pattern_data['success_count'] / pattern_data['occurrences'],
            'emergent_potential': emergent_analysis,
            'domains_used': list(pattern_data['domains_activated'])
        }
    
    def _create_pattern_signature(self, query: str) -> str:
        """Create a unique signature for a query pattern."""
        import hashlib
        import re
        
        # Normalize query
        normalized = query.lower().strip()
        
        # Extract key features
        features = {
            'length': len(normalized),
            'word_count': len(normalized.split()),
            'has_numbers': bool(re.search(r'\d', normalized)),
            'has_special_chars': bool(re.search(r'[^\w\s]', normalized)),
            'question_words': len([w for w in normalized.split() if w in ['what', 'how', 'why', 'when', 'where', 'who']]),
            'action_words': len([w for w in normalized.split() if w in ['analyze', 'compare', 'create', 'generate', 'solve', 'optimize']])
        }
        
        # Create hash from features
        import json
        feature_string = json.dumps(features, sort_keys=True)
        pattern_hash = hashlib.md5(feature_string.encode()).hexdigest()[:16]
        
        return pattern_hash
    
    def _analyze_emergent_potential(self, pattern_signature: str, pattern_data: Dict) -> Dict[str, Any]:
        """Analyze emergent potential with error handling."""
        try:
            # Calculate success rate
            success_rate = pattern_data['success_count'] / pattern_data['occurrences']
            
            # Check for evolution potential
            evolution_potential = {
                'high_frequency': pattern_data['occurrences'] >= self.learning_threshold,
                'consistent_success': success_rate > 0.8,
                'domain_diversity': len(pattern_data['domains_activated']) > 1,
                'recent_activity': True  # Simplified check
            }
            
            # Calculate overall potential
            potential_score = sum(evolution_potential.values()) / len(evolution_potential)
            
            return {
                'potential_score': potential_score,
                'evolution_potential': evolution_potential,
                'recommendation': 'create_controller' if potential_score > 0.7 else 'monitor'
            }
        except Exception as e:
            logger.error(f"Error analyzing emergent potential: {e}")
            return {
                'potential_score': 0.0,
                'evolution_potential': {},
                'recommendation': 'error'
            }

class AdaptiveCognitiveOrchestrator:
    """
    Main orchestrator for adaptive cognitive evolution.
    Integrates with ThoughtTrail to detect patterns and propose optimizations.
    """
    
    def __init__(self):
        self.pattern_engine = PatternEvolutionEngine()
        self.nexus = None
        self.learning_metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'evolution_opportunities': 0,
            'controllers_created': 0
        }
        
        logger.info("[ACO] Initialized with evolution capabilities")
    
    def inject_nexus(self, nexus_instance: NexusInterface) -> None:
        """Inject NexusInterface for event communication."""
        self.nexus = nexus_instance
        logger.info("[ACO] NexusInterface injected")
    
    def on_thoughttrail_trigger(self, trigger_data: Dict[str, Any]) -> None:
        """
        Handle ThoughtTrail trigger events.
        
        This is called when ThoughtTrail detects significant patterns
        that warrant ACO analysis.
        """
        try:
            triggers = trigger_data.get('triggers', [])
            entry = trigger_data.get('entry', {})
            
            logger.info(f"[ACO] Received ThoughtTrail trigger: {triggers}")
            
            # Analyze the trigger
            if 'low_confidence' in triggers:
                self._analyze_low_confidence_pattern(entry)
            elif 'error_detected' in triggers:
                self._analyze_error_pattern(entry)
            elif 'novel_success' in triggers:
                self._analyze_success_pattern(entry)
            elif 'cross_domain_correlation' in triggers:
                self._analyze_cross_domain_pattern(entry)
            
            # Update metrics
            self.learning_metrics['evolution_opportunities'] += 1
            
        except Exception as e:
            logger.error(f"[ACO] Error handling ThoughtTrail trigger: {e}")
    
    def _analyze_low_confidence_pattern(self, entry: Dict[str, Any]) -> None:
        """Analyze patterns in low-confidence actions."""
        action_type = entry.get('action_type', 'unknown')
        reflection = entry.get('iar', {}).get('reflection', '')
        
        logger.info(f"[ACO] Analyzing low-confidence pattern for {action_type}")
        
        # Check if this is a recurring pattern
        recent_entries = thought_trail.get_recent_entries(minutes=60)
        similar_entries = [
            e for e in recent_entries 
            if e.action_type == action_type and e.confidence < 0.7
        ]
        
        if len(similar_entries) >= 3:  # Threshold for pattern detection
            self._propose_optimization(action_type, "low_confidence", similar_entries)
    
    def _analyze_error_pattern(self, entry: Dict[str, Any]) -> None:
        """Analyze patterns in error conditions."""
        action_type = entry.get('action_type', 'unknown')
        reflection = entry.get('iar', {}).get('reflection', '')
        
        logger.info(f"[ACO] Analyzing error pattern for {action_type}")
        
        # Look for recurring error patterns
        recent_entries = thought_trail.get_recent_entries(minutes=120)
        error_entries = [
            e for e in recent_entries 
            if e.action_type == action_type and 'error' in e.iar.get('reflection', '').lower()
        ]
        
        if len(error_entries) >= 2:  # Lower threshold for errors
            self._propose_error_handling(action_type, error_entries)
    
    def _analyze_success_pattern(self, entry: Dict[str, Any]) -> None:
        """Analyze patterns in successful actions."""
        action_type = entry.get('action_type', 'unknown')
        
        logger.info(f"[ACO] Analyzing success pattern for {action_type}")
        
        # Look for high-confidence patterns that could be optimized
        recent_entries = thought_trail.get_recent_entries(minutes=60)
        success_entries = [
            e for e in recent_entries 
            if e.action_type == action_type and e.confidence > 0.9
        ]
        
        if len(success_entries) >= 5:  # High threshold for success patterns
            self._propose_optimization(action_type, "high_success", success_entries)
    
    def _analyze_cross_domain_pattern(self, entry: Dict[str, Any]) -> None:
        """Analyze cross-domain correlation patterns."""
        logger.info("[ACO] Analyzing cross-domain correlation pattern")
        
        # This is where we'd implement more sophisticated cross-domain analysis
        # For now, just log the pattern
        self._propose_cross_domain_analysis()
    
    def _propose_optimization(self, action_type: str, pattern_type: str, entries: List[Any]) -> None:
        """Propose an optimization based on detected patterns."""
        proposal = {
            'type': 'optimization_proposal',
            'action_type': action_type,
            'pattern_type': pattern_type,
            'entries_analyzed': len(entries),
            'confidence': 0.8,
            'timestamp': datetime.now().isoformat(),
            'recommendation': f"Consider optimizing {action_type} for {pattern_type} pattern"
        }
        
        logger.info(f"[ACO] Optimization proposal: {proposal['recommendation']}")
        
        # Publish to Nexus for other components
        if self.nexus:
            self.nexus.publish("aco_optimization_proposal", proposal)
    
    def _propose_error_handling(self, action_type: str, entries: List[Any]) -> None:
        """Propose error handling improvements."""
        proposal = {
            'type': 'error_handling_proposal',
            'action_type': action_type,
            'entries_analyzed': len(entries),
            'confidence': 0.9,
            'timestamp': datetime.now().isoformat(),
            'recommendation': f"Implement better error handling for {action_type}"
        }
        
        logger.info(f"[ACO] Error handling proposal: {proposal['recommendation']}")
        
        if self.nexus:
            self.nexus.publish("aco_error_handling_proposal", proposal)
    
    def _propose_cross_domain_analysis(self) -> None:
        """Propose cross-domain analysis."""
        proposal = {
            'type': 'cross_domain_proposal',
            'confidence': 0.7,
            'timestamp': datetime.now().isoformat(),
            'recommendation': "Cross-domain correlation detected - consider deeper analysis"
        }
        
        logger.info("[ACO] Cross-domain analysis proposal")
        
        if self.nexus:
            self.nexus.publish("aco_cross_domain_proposal", proposal)
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get current learning metrics."""
        return {
            'learning_metrics': self.learning_metrics,
            'pattern_analytics': {
                'total_patterns': len(self.pattern_engine.pattern_signatures),
                'active_patterns': sum(1 for p in self.pattern_engine.pattern_signatures.values() if p['occurrences'] > 5),
                'success_rate': sum(p['success_count'] / p['occurrences'] for p in self.pattern_engine.pattern_signatures.values() if p['occurrences'] > 0) / max(len(self.pattern_engine.pattern_signatures), 1)
            }
        }

# Global ACO instance
aco = AdaptiveCognitiveOrchestrator()

def initialize_aco_integration(nexus_instance: NexusInterface) -> None:
    """
    Initialize ACO integration with ThoughtTrail and Nexus.
    
    Args:
        nexus_instance: The NexusInterface instance
    """
    # Inject dependencies
    aco.inject_nexus(nexus_instance)
    
    # Subscribe to ThoughtTrail triggers
    thought_trail.add_trigger_callback(aco.on_thoughttrail_trigger)
    
    logger.info("[ACO] Integration initialized with ThoughtTrail and Nexus")

__all__ = [
    'PatternEvolutionEngine',
    'AdaptiveCognitiveOrchestrator',
    'aco',
    'initialize_aco_integration'
]

