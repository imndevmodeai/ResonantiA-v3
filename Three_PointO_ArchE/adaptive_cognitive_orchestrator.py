#!/usr/bin/env python3
"""
Adaptive Cognitive Orchestrator (ACO) - Phase 2 Deployment
Building upon the Cognitive Resonant Controller System (CRCS) with meta-learning capabilities.

This module represents the evolution from static domain controllers to dynamic, 
learning-enabled cognitive orchestration with pattern evolution and emergent domain detection.

Key Features:
- Meta-learning from query patterns
- Emergent domain detection and controller creation
- Adaptive parameter tuning based on performance metrics
- Pattern evolution engine for continuous improvement
- Cross-instance learning capabilities (conceptual)
"""

import logging
import time
import json
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict, deque
from datetime import datetime
import hashlib
import re
import numpy as np

# Import the base CRCS system
from cognitive_resonant_controller import CognitiveResonantControllerSystem

logger = logging.getLogger("ACO")

class PatternEvolutionEngine:
    """
    Engine for detecting emergent patterns and creating new domain controllers
    Implements meta-learning capabilities for cognitive architecture evolution
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
            'pattern_occurrences': pattern_data['occurrences'],
            'success_rate': pattern_data['success_count'] / pattern_data['occurrences'],
            'emergent_potential': emergent_analysis,
            'learning_opportunity': not success and pattern_data['occurrences'] >= self.learning_threshold
        }
    
    def _create_pattern_signature(self, query: str) -> str:
        """Create a hash signature for query pattern recognition"""
        # Extract key features for pattern matching
        query_lower = query.lower()
        
        # Key terms that might indicate domain
        key_terms = []
        
        # Technical terms
        if any(term in query_lower for term in ['implementation', 'resonance', 'jedi', 'bridge']):
            key_terms.append('implementation_resonance')
        
        if any(term in query_lower for term in ['spr', 'sparse', 'priming', 'representation']):
            key_terms.append('spr_related')
            
        if any(term in query_lower for term in ['proportional', 'resonant', 'controller', 'cfp']):
            key_terms.append('control_theory')
            
        if any(term in query_lower for term in ['adaptive', 'cognitive', 'orchestrator', 'meta']):
            key_terms.append('adaptive_cognitive')
            
        if any(term in query_lower for term in ['temporal', 'time', '4d', 'dynamics']):
            key_terms.append('temporal_analysis')
            
        if any(term in query_lower for term in ['agent', 'abm', 'simulation', 'modeling']):
            key_terms.append('agent_modeling')
        
        # Question type
        question_type = 'unknown'
        if query_lower.startswith('what'):
            question_type = 'definition'
        elif query_lower.startswith('how'):
            question_type = 'process'
        elif query_lower.startswith('why'):
            question_type = 'reasoning'
        elif '?' not in query:
            question_type = 'statement'
        
        # Create signature
        signature_components = sorted(key_terms) + [question_type]
        signature_string = '|'.join(signature_components)
        
        return hashlib.md5(signature_string.encode()).hexdigest()[:12]
    
    def _analyze_emergent_potential(self, pattern_signature: str, pattern_data: Dict) -> Dict[str, Any]:
        """Analyze whether a pattern represents a potential new domain"""
        occurrences = pattern_data['occurrences']
        success_rate = pattern_data['success_count'] / occurrences
        
        # Criteria for emergent domain
        frequent_enough = occurrences >= self.learning_threshold
        low_success_rate = success_rate < 0.5  # Struggling with current controllers
        multiple_domains = len(pattern_data['domains_activated']) > 1  # Confusion between domains
        
        emergent_score = 0.0
        if frequent_enough:
            emergent_score += 0.4
        if low_success_rate:
            emergent_score += 0.4
        if multiple_domains:
            emergent_score += 0.2
            
        is_emergent = emergent_score >= self.confidence_threshold
        
        if is_emergent and pattern_signature not in self.emergent_domains:
            # Create emergent domain record
            self.emergent_domains[pattern_signature] = {
                'detected_at': datetime.now().isoformat(),
                'pattern_signature': pattern_signature,
                'sample_queries': pattern_data['sample_queries'].copy(),
                'occurrences': occurrences,
                'success_rate': success_rate,
                'emergent_score': emergent_score,
                'suggested_domain_name': self._suggest_domain_name(pattern_data['sample_queries']),
                'status': 'detected'
            }
            
            logger.info(f"[PatternEngine] 🧠 Emergent domain detected: {pattern_signature}")
            logger.info(f"[PatternEngine] Suggested name: {self.emergent_domains[pattern_signature]['suggested_domain_name']}")
        
        return {
            'is_emergent': is_emergent,
            'emergent_score': emergent_score,
            'occurrences': occurrences,
            'success_rate': success_rate,
            'criteria_met': {
                'frequent_enough': frequent_enough,
                'low_success_rate': low_success_rate,
                'multiple_domains': multiple_domains
            }
        }
    
    def _suggest_domain_name(self, sample_queries: List[str]) -> str:
        """Suggest a domain name based on sample queries"""
        # Extract common terms
        all_words = []
        for query in sample_queries:
            words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
            all_words.extend(words)
        
        # Count word frequency
        word_counts = defaultdict(int)
        for word in all_words:
            if len(word) > 3:  # Skip short words
                word_counts[word] += 1
        
        # Get most common meaningful words
        common_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if common_words:
            # Create domain name from common words
            domain_name = ''.join(word.capitalize() for word, _ in common_words)
            return f"{domain_name}Queries"
        else:
            return f"EmergentDomain{len(self.emergent_domains) + 1}"
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from the learning process"""
        total_queries = len(self.query_history)
        if total_queries == 0:
            return {'status': 'no_data'}
        
        # Calculate overall metrics
        recent_queries = list(self.query_history)[-50:]  # Last 50 queries
        success_rate = sum(1 for q in recent_queries if q['success']) / len(recent_queries)
        
        # Domain distribution
        domain_counts = defaultdict(int)
        for query in recent_queries:
            domain_counts[query['active_domain']] += 1
        
        return {
            'total_queries_analyzed': total_queries,
            'recent_success_rate': success_rate,
            'unique_patterns_detected': len(self.pattern_signatures),
            'emergent_domains_count': len(self.emergent_domains),
            'domain_distribution': dict(domain_counts),
            'emergent_domains': {
                sig: {
                    'suggested_name': data['suggested_domain_name'],
                    'occurrences': data['occurrences'],
                    'emergent_score': data['emergent_score'],
                    'status': data['status']
                }
                for sig, data in self.emergent_domains.items()
            }
        }

class EmergentDomainDetector:
    """
    Autonomous evolution module for the Adaptive Cognitive Orchestrator.
    Analyzes General_Fallback patterns to identify emergent cognitive domains.
    """
    
    def __init__(self, confidence_threshold: float = 0.8, min_cluster_size: int = 5):
        self.confidence_threshold = confidence_threshold
        self.min_cluster_size = min_cluster_size
        self.fallback_queries = []
        self.pattern_clusters = {}
        self.domain_candidates = {}
        self.evolution_history = []
        
    def analyze_fallback_query(self, query: str, context: str, timestamp: str) -> Dict[str, Any]:
        """
        Analyze a query that activated General_Fallback controller.
        
        Args:
            query: The original query
            context: Retrieved context from fallback
            timestamp: When the query was processed
            
        Returns:
            Analysis results including clustering and evolution potential
        """
        # Store the fallback query
        fallback_entry = {
            'query': query,
            'context': context or "",  # Handle None context
            'timestamp': timestamp,
            'query_vector': self._vectorize_query(query),
            'context_features': self._extract_context_features(context or "")
        }
        
        self.fallback_queries.append(fallback_entry)
        
        # Perform clustering analysis
        cluster_analysis = self._perform_clustering_analysis()
        
        # Check for evolution opportunities
        evolution_opportunity = self._check_evolution_opportunity(cluster_analysis)
        
        return {
            'fallback_entry_id': len(self.fallback_queries) - 1,
            'cluster_analysis': cluster_analysis,
            'evolution_opportunity': evolution_opportunity,
            'total_fallback_queries': len(self.fallback_queries)
        }
    
    def _vectorize_query(self, query: str) -> np.ndarray:
        """Create a vector representation of the query for clustering."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Simple TF-IDF vectorization (in production, use more sophisticated methods)
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
        # If this is the first query, initialize with it
        if len(self.fallback_queries) == 0:
            self.vectorizer = vectorizer
            vector = vectorizer.fit_transform([query]).toarray()[0]
        else:
            # Use existing vectorizer or refit if needed
            all_queries = [entry['query'] for entry in self.fallback_queries] + [query]
            if len(all_queries) % 10 == 0:  # Refit every 10 queries
                self.vectorizer = vectorizer
                vectors = vectorizer.fit_transform(all_queries)
                vector = vectors[-1].toarray()[0]
                
                # Update existing vectors
                for i, entry in enumerate(self.fallback_queries):
                    entry['query_vector'] = vectors[i].toarray()[0]
            else:
                try:
                    vector = self.vectorizer.transform([query]).toarray()[0]
                except:
                    # Fallback to refit if transform fails
                    all_queries = [entry['query'] for entry in self.fallback_queries] + [query]
                    vectors = self.vectorizer.fit_transform(all_queries)
                    vector = vectors[-1].toarray()[0]
        
        return vector
    
    def _extract_context_features(self, context: str) -> Dict[str, Any]:
        """Extract features from the retrieved context."""
        features = {
            'length': len(context),
            'word_count': len(context.split()),
            'has_code': 'def ' in context or 'class ' in context or 'import ' in context,
            'has_protocol_refs': 'SPR' in context or 'IAR' in context or 'resonance' in context.lower(),
            'technical_density': len([w for w in context.split() if w.isupper() and len(w) > 2]) / max(len(context.split()), 1)
        }
        return features
    
    def _perform_clustering_analysis(self) -> Dict[str, Any]:
        """Perform clustering analysis on fallback queries."""
        if len(self.fallback_queries) < 3:
            return {'status': 'insufficient_data', 'clusters': []}
        
        from sklearn.cluster import DBSCAN
        from sklearn.metrics import silhouette_score
        
        # Get query vectors
        vectors = np.array([entry['query_vector'] for entry in self.fallback_queries])
        
        # Perform DBSCAN clustering
        clustering = DBSCAN(eps=0.3, min_samples=2)
        cluster_labels = clustering.fit_predict(vectors)
        
        # Analyze clusters
        unique_labels = set(cluster_labels)
        clusters = []
        
        for label in unique_labels:
            if label == -1:  # Noise points
                continue
                
            cluster_indices = [i for i, l in enumerate(cluster_labels) if l == label]
            cluster_queries = [self.fallback_queries[i]['query'] for i in cluster_indices]
            
            cluster_info = {
                'cluster_id': label,
                'size': len(cluster_indices),
                'queries': cluster_queries,
                'representative_query': cluster_queries[0],  # Could be improved with centroid
                'evolution_potential': len(cluster_indices) >= self.min_cluster_size
            }
            
            clusters.append(cluster_info)
        
        # Calculate silhouette score if possible
        silhouette = None
        if len(unique_labels) > 1 and len(vectors) > 2:
            try:
                silhouette = silhouette_score(vectors, cluster_labels)
            except:
                silhouette = None
        
        return {
            'status': 'complete',
            'clusters': clusters,
            'total_clusters': len(clusters),
            'silhouette_score': silhouette,
            'noise_points': list(cluster_labels).count(-1)
        }
    
    def _check_evolution_opportunity(self, cluster_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Check if any clusters meet the criteria for domain evolution."""
        if cluster_analysis['status'] != 'complete':
            return {'evolution_ready': False, 'reason': 'insufficient_clustering'}
        
        evolution_candidates = []
        
        for cluster in cluster_analysis['clusters']:
            if cluster['evolution_potential']:
                # Generate domain candidate
                domain_candidate = self._generate_domain_candidate(cluster)
                evolution_candidates.append(domain_candidate)
        
        return {
            'evolution_ready': len(evolution_candidates) > 0,
            'candidates': evolution_candidates,
            'total_candidates': len(evolution_candidates)
        }
    
    def _generate_domain_candidate(self, cluster: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a domain candidate configuration."""
        cluster_id = cluster['cluster_id']
        
        # Analyze query patterns to generate domain name
        queries = cluster['queries']
        common_terms = self._extract_common_terms(queries)
        
        # Generate domain name
        domain_name = self._generate_domain_name(common_terms)
        
        # Create domain controller config
        controller_config = {
            'domain_name': domain_name,
            'controller_class': f'{domain_name}Controller',
            'detection_patterns': common_terms,
            'confidence_threshold': self.confidence_threshold,
            'cluster_source': {
                'cluster_id': cluster_id,
                'sample_queries': queries[:3],
                'cluster_size': cluster['size']
            }
        }
        
        # Store for Keyholder review
        candidate_id = f"domain_candidate_{len(self.domain_candidates)}"
        self.domain_candidates[candidate_id] = controller_config
        
        return {
            'candidate_id': candidate_id,
            'domain_name': domain_name,
            'controller_config': controller_config,
            'evolution_confidence': min(cluster['size'] / self.min_cluster_size, 1.0)
        }
    
    def _extract_common_terms(self, queries: List[str]) -> List[str]:
        """Extract common terms from a cluster of queries."""
        from collections import Counter
        
        # Simple term extraction (could be enhanced with NLP)
        all_terms = []
        for query in queries:
            terms = [word.lower().strip('.,!?') for word in query.split() 
                    if len(word) > 3 and word.lower() not in ['what', 'how', 'when', 'where', 'why', 'the', 'and', 'or']]
            all_terms.extend(terms)
        
        # Get most common terms
        term_counts = Counter(all_terms)
        common_terms = [term for term, count in term_counts.most_common(5) if count >= 2]
        
        return common_terms
    
    def _generate_domain_name(self, common_terms: List[str]) -> str:
        """Generate a domain name from common terms."""
        if not common_terms:
            return f"EmergentDomain{len(self.domain_candidates)}"
        
        # Create a domain name from the most common term
        primary_term = common_terms[0].title()
        
        # Add contextual suffix
        if any(term in ['control', 'system', 'process'] for term in common_terms):
            domain_name = f"{primary_term}SystemQueries"
        elif any(term in ['analysis', 'data', 'pattern'] for term in common_terms):
            domain_name = f"{primary_term}AnalysisQueries"
        else:
            domain_name = f"{primary_term}Queries"
        
        return domain_name
    
    def generate_controller_draft(self, candidate_id: str) -> str:
        """Generate a draft controller class for Keyholder review."""
        if candidate_id not in self.domain_candidates:
            raise ValueError(f"Unknown candidate ID: {candidate_id}")
        
        config = self.domain_candidates[candidate_id]
        
        controller_draft = f'''
class {config['controller_class']}(FrequencyDomainController):
    """
    Emergent domain controller for {config['domain_name']}.
    Auto-generated by EmergentDomainDetector.
    
    Cluster Analysis:
    - Cluster ID: {config['cluster_source']['cluster_id']}
    - Cluster Size: {config['cluster_source']['cluster_size']}
    - Sample Queries: {config['cluster_source']['sample_queries']}
    """
    
    def __init__(self):
        super().__init__(
            domain_name="{config['domain_name']}",
            resonant_frequency=0.7,  # Initial frequency - requires tuning
            quality_factor=2.0,      # Initial Q-factor - requires tuning
            damping_ratio=0.5        # Initial damping - requires tuning
        )
        
        # Detection patterns identified from clustering
        self.detection_patterns = {config['detection_patterns']}
        
    def detect_domain(self, query: str) -> float:
        """Detect if query belongs to this domain."""
        query_lower = query.lower()
        
        # Pattern matching based on cluster analysis
        matches = 0
        for pattern in self.detection_patterns:
            if pattern in query_lower:
                matches += 1
        
        # Calculate confidence based on pattern matches
        confidence = min(matches / len(self.detection_patterns), 1.0)
        
        return confidence
        
    def process_query(self, query: str, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Process query using domain-specific logic."""
        # TODO: Implement domain-specific processing logic
        # This is a placeholder that needs Keyholder refinement
        
        extracted_context = "EMERGENT_DOMAIN_PROCESSING: " + str(context.get('fallback_context', ''))
        
        metrics = {{
            'domain_confidence': self.detect_domain(query),
            'processing_method': 'emergent_auto_generated',
            'requires_refinement': True
        }}
        
        return extracted_context, metrics
'''
        
        return controller_draft
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status and recommendations."""
        return {
            'total_fallback_queries': len(self.fallback_queries),
            'domain_candidates': len(self.domain_candidates),
            'evolution_history': self.evolution_history,
            'next_evolution_threshold': self.min_cluster_size,
            'current_confidence_threshold': self.confidence_threshold,
            'ready_for_evolution': len(self.domain_candidates) > 0
        }

class AdaptiveCognitiveOrchestrator:
    """
    Phase 2 Deployment: Adaptive Cognitive Orchestrator
    
    Builds upon CRCS with meta-learning capabilities:
    - Pattern evolution engine for emergent domain detection
    - Adaptive parameter tuning based on performance
    - Meta-learning from query patterns
    - Foundation for collective intelligence (Phase 3)
    """
    
    def __init__(self, protocol_chunks: List[str]):
        """
        Initialize the Adaptive Cognitive Orchestrator
        
        Args:
            protocol_chunks: List of protocol text chunks for domain controllers
        """
        # Initialize base CRCS system
        self.crcs = CognitiveResonantControllerSystem(protocol_chunks)
        
        # Initialize meta-learning components
        self.pattern_engine = PatternEvolutionEngine()
        
        # Adaptation metrics
        self.adaptation_metrics = {
            'total_adaptations': 0,
            'successful_adaptations': 0,
            'failed_adaptations': 0,
            'new_controllers_created': 0,
            'parameter_adjustments': 0,
            'last_adaptation': None
        }
        
        # Meta-learning configuration
        self.meta_learning_active = True
        self.auto_tuning_enabled = True
        self.emergent_domain_detection = True
        
        # Performance tracking for adaptive tuning
        self.performance_history = deque(maxlen=100)
        
        # Initialize Phase 4 Self-Evolution capability
        self.emergent_domain_detector = EmergentDomainDetector(
            confidence_threshold=0.8,
            min_cluster_size=5
        )
        
        # Evolution tracking
        self.autonomous_evolution_active = True
        self.evolution_log = []
        
        logger.info("[ACO] Adaptive Cognitive Orchestrator initialized with autonomous evolution")
        logger.info(f"[ACO] Base CRCS has {len(self.crcs.domain_controllers)} domain controllers")
        logger.info(f"[ACO] Meta-learning active: {self.meta_learning_active}")
        logger.info(f"[ACO] Emergent Domain Detector active: threshold={self.emergent_domain_detector.confidence_threshold}")
    
    def process_query_with_evolution(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process query with full evolution capabilities including emergent domain detection.
        
        Args:
            query: User query to process
            
        Returns:
            Tuple of (context, enhanced_metrics)
        """
        start_time = time.time()
        
        # Process query using base CRCS
        context, base_metrics = self.crcs.process_query(query)
        
        processing_time = time.time() - start_time
        success = bool(context)
        active_domain = base_metrics.get('active_domain', 'None')
        
        # Enhanced metrics for ACO with evolution
        enhanced_metrics = base_metrics.copy()
        enhanced_metrics.update({
            'meta_learning_active': self.meta_learning_active,
            'autonomous_evolution_active': self.autonomous_evolution_active,
            'processing_time': processing_time,
            'aco_version': 'Phase_4_Self_Evolution'
        })
        
                # Phase 4 Self-Evolution: Emergent Domain Detection
        # Trigger evolution detection for General domain (fallback) or low-confidence specialized domains
        should_analyze_for_evolution = (
            self.autonomous_evolution_active and 
            (active_domain == 'General_Fallback' or 
             active_domain == 'General' or
             (active_domain and base_metrics.get('domain_confidence', 1.0) < 0.5))
        )
        
        if should_analyze_for_evolution:
            logger.info(f"[ACO-EVOLUTION] Analyzing query for evolution: domain={active_domain}, query='{query[:50]}...'")
            
            evolution_analysis = self.emergent_domain_detector.analyze_fallback_query(
                query=query,
                context=context,
                timestamp=datetime.now().isoformat()
            )
            
            enhanced_metrics['evolution_analysis'] = evolution_analysis
            
            logger.info(f"[ACO-EVOLUTION] Analysis complete: {evolution_analysis['total_fallback_queries']} total queries analyzed")
            
            # Check for autonomous evolution opportunities
            if evolution_analysis['evolution_opportunity']['evolution_ready']:
                logger.info(f"[ACO-EVOLUTION] Evolution opportunity detected for query: '{query[:50]}...'")
                logger.info(f"[ACO-EVOLUTION] Domain candidates ready: {evolution_analysis['evolution_opportunity']['total_candidates']}")
                self._handle_evolution_opportunity(evolution_analysis['evolution_opportunity'])
            else:
                logger.info(f"[ACO-EVOLUTION] No evolution opportunity yet: {evolution_analysis['evolution_opportunity'].get('reason', 'insufficient data')}")
        
        # Meta-learning analysis if enabled
        if self.meta_learning_active:
            pattern_analysis = self.pattern_engine.analyze_query_pattern(
                query, success, active_domain
            )
            
            enhanced_metrics.update({
                'pattern_analysis': pattern_analysis,
                'emergent_domains_count': len(self.pattern_engine.emergent_domains),
                'evolution_status': self.emergent_domain_detector.get_evolution_status()
            })
            
            # Check for adaptation opportunities
            if pattern_analysis.get('learning_opportunity'):
                adaptation_result = self._attempt_adaptation(query, pattern_analysis)
                enhanced_metrics['adaptation_attempted'] = adaptation_result
        
        # Record performance for adaptive tuning
        performance_record = {
            'timestamp': datetime.now().isoformat(),
            'query': query[:50] + '...' if len(query) > 50 else query,
            'success': success,
            'active_domain': active_domain,
            'processing_time': processing_time,
            'context_length': len(context) if context else 0,
            'evolution_active': self.autonomous_evolution_active
        }
        
        self.performance_history.append(performance_record)
        
        return context, enhanced_metrics
    
    def _attempt_adaptation(self, query: str, pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to adapt the system based on learning opportunity
        
        Args:
            query: The query that triggered the learning opportunity
            pattern_analysis: Analysis results from pattern engine
            
        Returns:
            Dict describing the adaptation attempt
        """
        self.adaptation_metrics['total_adaptations'] += 1
        
        emergent_potential = pattern_analysis.get('emergent_potential', {})
        
        if emergent_potential.get('is_emergent'):
            # Potential new domain detected
            pattern_sig = pattern_analysis['pattern_signature']
            emergent_domain = self.pattern_engine.emergent_domains.get(pattern_sig)
            
            if emergent_domain and emergent_domain['status'] == 'detected':
                # Mark as under consideration
                emergent_domain['status'] = 'under_consideration'
                emergent_domain['consideration_started'] = datetime.now().isoformat()
                
                logger.info(f"[ACO] 🔄 Adaptation: Emergent domain under consideration")
                logger.info(f"[ACO] Domain: {emergent_domain['suggested_domain_name']}")
                
                self.adaptation_metrics['successful_adaptations'] += 1
                self.adaptation_metrics['last_adaptation'] = datetime.now().isoformat()
                
                return {
                    'type': 'emergent_domain_detection',
                    'status': 'successful',
                    'domain_name': emergent_domain['suggested_domain_name'],
                    'emergent_score': emergent_domain['emergent_score']
                }
        
        # Other adaptation strategies could be implemented here
        # For now, log the failed adaptation
        self.adaptation_metrics['failed_adaptations'] += 1
        
        return {
            'type': 'pattern_learning',
            'status': 'logged_for_future_analysis',
            'pattern_signature': pattern_analysis['pattern_signature']
        }
    
    def _auto_tune_parameters(self):
        """Auto-tune system parameters based on performance history"""
        if len(self.performance_history) < 10:
            return
        
        recent_performance = list(self.performance_history)[-10:]
        
        # Calculate performance metrics
        success_rate = sum(1 for p in recent_performance if p['success']) / len(recent_performance)
        avg_processing_time = sum(p['processing_time'] for p in recent_performance) / len(recent_performance)
        
        # Simple adaptive tuning logic
        tuning_applied = False
        
        # If success rate is low, consider adjusting thresholds
        if success_rate < 0.6:
            # Lower the pattern learning threshold to be more aggressive
            if self.pattern_engine.learning_threshold > 3:
                self.pattern_engine.learning_threshold -= 1
                tuning_applied = True
                logger.info(f"[ACO] 🔧 Auto-tuning: Lowered learning threshold to {self.pattern_engine.learning_threshold}")
        
        # If processing time is too high, consider optimizations
        elif avg_processing_time > 0.05:  # 50ms threshold
            # Could implement caching or other optimizations
            logger.info(f"[ACO] 📊 Performance note: Average processing time {avg_processing_time:.3f}s")
        
        if tuning_applied:
            self.adaptation_metrics['parameter_adjustments'] += 1
    
    def get_system_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive system diagnostics including ACO-specific metrics"""
        # Get base CRCS diagnostics
        base_diagnostics = self.crcs.get_system_diagnostics()
        
        # Add ACO-specific diagnostics
        learning_insights = self.pattern_engine.get_learning_insights()
        
        aco_diagnostics = {
            'aco_version': 'Phase_2_Deployment',
            'meta_learning_active': self.meta_learning_active,
            'auto_tuning_enabled': self.auto_tuning_enabled,
            'emergent_domain_detection': self.emergent_domain_detection,
            'adaptation_metrics': self.adaptation_metrics.copy(),
            'learning_insights': learning_insights,
            'performance_history_size': len(self.performance_history),
            'pattern_engine_status': {
                'query_history_size': len(self.pattern_engine.query_history),
                'unique_patterns': len(self.pattern_engine.pattern_signatures),
                'emergent_domains': len(self.pattern_engine.emergent_domains),
                'learning_threshold': self.pattern_engine.learning_threshold,
                'confidence_threshold': self.pattern_engine.confidence_threshold
            },
            'evolution_status': self.emergent_domain_detector.get_evolution_status()
        }
        
        # Combine diagnostics
        combined_diagnostics = base_diagnostics.copy()
        combined_diagnostics['aco_diagnostics'] = aco_diagnostics
        
        return combined_diagnostics
    
    def _handle_evolution_opportunity(self, evolution_opportunity: Dict[str, Any]) -> None:
        """Handle detected evolution opportunities."""
        for candidate in evolution_opportunity['candidates']:
            candidate_id = candidate['candidate_id']
            domain_name = candidate['domain_name']
            confidence = candidate['evolution_confidence']
            
            # Log evolution event
            evolution_event = {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'domain_candidate_detected',
                'candidate_id': candidate_id,
                'domain_name': domain_name,
                'confidence': confidence,
                'status': 'awaiting_keyholder_review'
            }
            
            self.evolution_log.append(evolution_event)
            
            logger.info(f"[ACO-EVOLUTION] New domain candidate detected: {domain_name} (confidence: {confidence:.2f})")
            logger.info(f"[ACO-EVOLUTION] Candidate ID: {candidate_id} - Awaiting Keyholder review")
    
    def get_evolution_candidates_for_review(self) -> Dict[str, Any]:
        """Get evolution candidates ready for Keyholder review."""
        candidates = {}
        
        for candidate_id, config in self.emergent_domain_detector.domain_candidates.items():
            # Generate controller draft
            controller_draft = self.emergent_domain_detector.generate_controller_draft(candidate_id)
            
            candidates[candidate_id] = {
                'config': config,
                'controller_draft': controller_draft,
                'status': 'ready_for_review'
            }
        
        return {
            'total_candidates': len(candidates),
            'candidates': candidates,
            'evolution_log': self.evolution_log,
            'evolution_status': self.emergent_domain_detector.get_evolution_status()
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the ACO system
    logging.basicConfig(level=logging.INFO)
    
    # Mock protocol chunks for testing
    mock_protocol = [
        "Implementation Resonance refers to the alignment between conceptual understanding and operational implementation.",
        "The ProportionalResonantControlPatterN eliminates oscillatory errors through resonant gain amplification.",
        "Adaptive Cognitive Orchestrator enables meta-learning and pattern evolution in cognitive architectures.",
        "Sparse Priming Representations (SPRs) activate internal cognitive pathways within the Knowledge Network Oneness.",
        "Temporal Dynamics and 4D Thinking enable analysis across the dimension of time for strategic foresight."
    ]
    
    # Initialize ACO
    aco = AdaptiveCognitiveOrchestrator(mock_protocol)
    
    # Test queries
    test_queries = [
        "What is Implementation Resonance?",
        "How does the ProportionalResonantControlPatterN work?",
        "What is the Adaptive Cognitive Orchestrator?",
        "Explain SPRs and their function",
        "What is temporal dynamics?",
        "How do cognitive architectures learn?",  # Should trigger learning
        "What is meta-learning in AI?",  # Should trigger learning
        "Explain pattern evolution",  # Should trigger learning
    ]
    
    print("🧠 Testing Adaptive Cognitive Orchestrator")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        context, metrics = aco.process_query_with_evolution(query)
        
        if context:
            print(f"✅ Success - Domain: {metrics.get('active_domain', 'Unknown')}")
            print(f"Context length: {len(context)} chars")
        else:
            print(f"❌ No context - Domain: {metrics.get('active_domain', 'None')}")
        
        if metrics.get('pattern_analysis'):
            pattern = metrics['pattern_analysis']
            print(f"Pattern occurrences: {pattern.get('pattern_occurrences', 0)}")
            if pattern.get('emergent_potential', {}).get('is_emergent'):
                print("🧠 EMERGENT DOMAIN DETECTED!")
        
        print(f"Processing time: {metrics.get('processing_time', 0):.3f}s")
    
    # Show final diagnostics
    print("\n" + "=" * 60)
    print("FINAL SYSTEM DIAGNOSTICS")
    print("=" * 60)
    
    diagnostics = aco.get_system_diagnostics()
    aco_diag = diagnostics.get('aco_diagnostics', {})
    
    print(f"Adaptation Metrics:")
    for key, value in aco_diag.get('adaptation_metrics', {}).items():
        print(f"  {key}: {value}")
    
    print(f"\nLearning Insights:")
    learning = aco_diag.get('learning_insights', {})
    print(f"  Total queries analyzed: {learning.get('total_queries_analyzed', 0)}")
    print(f"  Unique patterns detected: {learning.get('unique_patterns_detected', 0)}")
    print(f"  Emergent domains count: {learning.get('emergent_domains_count', 0)}")
    
    if learning.get('emergent_domains'):
        print(f"\nEmergent Domains:")
        for sig, domain in learning['emergent_domains'].items():
            print(f"  {domain['suggested_name']}: {domain['occurrences']} occurrences, "
                  f"score {domain['emergent_score']:.2f}") 