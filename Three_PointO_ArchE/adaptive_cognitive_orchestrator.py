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
import asyncio

# Optional Dependencies for advanced features
try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import silhouette_score
    ADVANCED_CLUSTERING_AVAILABLE = True
except ImportError:
    ADVANCED_CLUSTERING_AVAILABLE = False

# Import the base CRCS system - assuming it exists in a sibling file
try:
    from .cognitive_resonant_controller import CognitiveResonantControllerSystem
    from .llm_providers import BaseLLMProvider # Import for type hinting
    from .rise_orchestrator import RISE_Orchestrator
except ImportError:
    # Fallback for standalone execution
    CognitiveResonantControllerSystem = None


logger = logging.getLogger(__name__)

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
            'occurrences': pattern_data['occurrences'],
            'success_rate': pattern_data['success_count'] / pattern_data['occurrences'] if pattern_data['occurrences'] > 0 else 0,
            'emergent_potential': emergent_analysis,
            'domains_used': list(pattern_data['domains_activated'])
        }
    
    def _create_pattern_signature(self, query: str) -> str:
        """Create a unique signature for a query pattern based on its features."""
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
        feature_string = json.dumps(features, sort_keys=True)
        pattern_hash = hashlib.md5(feature_string.encode()).hexdigest()[:16]
        
        return pattern_hash
    
    def _analyze_emergent_potential(self, pattern_signature: str, pattern_data: Dict) -> Dict[str, Any]:
        """Analyze emergent potential with error handling."""
        try:
            occurrences = pattern_data.get('occurrences', 0)
            if occurrences == 0:
                return {'potential_score': 0.0, 'recommendation': 'monitor'}

            # Calculate success rate
            success_rate = pattern_data.get('success_count', 0) / occurrences
            
            # Check for evolution potential
            evolution_potential = {
                'high_frequency': occurrences >= self.learning_threshold,
                'consistent_success': success_rate > 0.8,
                'domain_diversity': len(pattern_data.get('domains_activated', set())) > 1,
                'recent_activity': True  # Simplified check
            }
            
            # Calculate overall potential
            potential_score = sum(evolution_potential.values()) / len(evolution_potential)
        
            try:
                return {
                    'potential_score': potential_score,
                    'evolution_potential': evolution_potential,
                    'recommendation': 'create_controller' if potential_score > 0.7 else 'monitor'
                }
            except Exception as e:
                logger.error(f"Error analyzing emergent potential for signature {pattern_signature}: {e}")
                return {
                    'potential_score': 0.0,
                    'evolution_potential': {},
                    'recommendation': 'error'
                }
        except Exception as e:
            logger.error(f"Error in _analyze_emergent_potential: {e}")
            return {
                'potential_score': 0.0,
                'evolution_potential': {},
                'recommendation': 'error'
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
    """Detects emergent domains and generates controller candidates."""
    
    def __init__(self, confidence_threshold: float = 0.8, min_cluster_size: int = 5):
        self.confidence_threshold = confidence_threshold
        self.min_cluster_size = min_cluster_size
        self.candidates = {}
        self.controller_templates = self._load_controller_templates()
        self.fallback_queries = [] # Added for clustering
        self.vectorizer = None # Added for vectorization
        
        logger.info("[DomainDetector] Initialized with detection capabilities")

    def _load_controller_templates(self) -> Dict[str, str]:
        """Load controller templates for different types."""
        return {
            'analytical': """
class {domain_name}Controller:
    \"\"\"
    {domain_name} Domain Controller
    Handles {domain_description}
    \"\"\"
    
    def __init__(self):
        self.domain_name = "{domain_name}"
        self.capabilities = {capabilities}
        self.learning_rate = 0.1
        
    def process_query(self, query: str) -> str:
        \"\"\"Process query in {domain_name} domain.\"\"\"
        # Implementation for {domain_name} processing
        return f"Processed {domain_name} query: {{query}}"
        
    def learn(self, feedback: Dict[str, Any]):
        \"\"\"Learn from feedback.\"\"\"
        # Learning implementation
        pass
""",
            'creative': """
class {domain_name}Controller:
    \"\"\"
    {domain_name} Creative Controller
    Handles {domain_description}
    \"\"\"
    
    def __init__(self):
        self.domain_name = "{domain_name}"
        self.creativity_level = 0.8
        self.capabilities = {capabilities}
        
    def generate_creative_response(self, query: str) -> str:
        \"\"\"Generate creative response for {domain_name}.\"\"\"
        # Creative generation implementation
        return f"Creative {domain_name} response: {{query}}"
""",
            'problem_solving': """
class {domain_name}Controller:
    \"\"\"
    {domain_name} Problem Solving Controller
    Handles {domain_description}
    \"\"\"
    
    def __init__(self):
        self.domain_name = "{domain_name}"
        self.solving_methods = {solving_methods}
        self.capabilities = {capabilities}
        
    def solve_problem(self, problem: str) -> str:
        \"\"\"Solve problem in {domain_name} domain.\"\"\"
        # Problem solving implementation
        return f"Solved {domain_name} problem: {{problem}}"
"""
        }

    def analyze_fallback_query(self, query: str, context: str, timestamp: str) -> Dict[str, Any]:
        """Analyze fallback queries for emergent domain patterns."""
        fallback_entry = {
            'query': query,
            'context': context or "",
            'timestamp': timestamp
        }
        self.fallback_queries.append(fallback_entry)
        
        analysis = {
            'query_features': self._extract_query_features(query),
            'context_features': self._extract_context_features(context or ""),
            'timestamp': timestamp,
            'potential_domain': None,
            'confidence': 0.0
        }
        
        if not ADVANCED_CLUSTERING_AVAILABLE:
            logger.warning("Scikit-learn not available. Skipping advanced clustering analysis.")
            return analysis

        # Vectorize query for clustering
        query_vector = self._vectorize_query(query)
        fallback_entry['query_vector'] = query_vector
        
        # Check existing candidates
        for candidate_id, candidate in self.candidates.items():
            similarity = self._calculate_similarity(query_vector, candidate['centroid'])
            if similarity > self.confidence_threshold:
                analysis['potential_domain'] = candidate_id
                analysis['confidence'] = similarity
                break
        
        # If no match, consider creating new candidate from clustering
        if not analysis['potential_domain']:
            cluster_analysis = self._perform_clustering_analysis()
            if cluster_analysis.get('evolution_opportunity'):
                 # For simplicity, we'll just consider the first opportunity
                candidate_info = self._check_evolution_opportunity({'status': 'complete', 'clusters': cluster_analysis['clusters']})
                if candidate_info.get('evolution_ready'):
                    new_candidate = candidate_info['candidates'][0]
                    analysis['potential_domain'] = new_candidate['candidate_id']
                    analysis['confidence'] = new_candidate['evolution_confidence']

        return analysis

    def _extract_query_features(self, query: str) -> Dict[str, Any]:
        """Extracts meaningful features from queries"""
        normalized = query.lower().strip()
        return {
            'length': len(normalized),
            'word_count': len(normalized.split()),
            'has_numbers': bool(re.search(r'\d', normalized)),
        }
    
    def _calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        from numpy.linalg import norm
        if not isinstance(vec1, np.ndarray): vec1 = np.array(vec1)
        if not isinstance(vec2, np.ndarray): vec2 = np.array(vec2)
        
        cosine_sim = np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))
        return cosine_sim if not np.isnan(cosine_sim) else 0.0

    def _perform_clustering_analysis(self) -> Dict[str, Any]:
        """Perform clustering analysis on query patterns."""
        if len(self.fallback_queries) < self.min_cluster_size:
            return {'clusters': [], 'evolution_opportunity': False}
        
        # Extract query vectors
        query_vectors = [rec['query_vector'] for rec in self.fallback_queries if 'query_vector' in rec]
        query_texts = [rec['query'] for rec in self.fallback_queries if 'query_vector' in rec]

        if not query_vectors:
             return {'clusters': [], 'evolution_opportunity': False}
        
        # Perform clustering (simplified K-means)
        if len(query_vectors) >= self.min_cluster_size:
            clusters = self._simple_clustering(query_vectors, query_texts)
            
            # Analyze clusters for evolution opportunities
            evolution_opportunity = self._check_evolution_opportunity({'status': 'complete', 'clusters': clusters})
            
            return {
                'clusters': clusters,
                'evolution_opportunity': evolution_opportunity['evolution_ready'],
                'cluster_count': len(clusters),
                'total_queries': len(query_vectors)
            }
        
        return {'clusters': [], 'evolution_opportunity': False}

    def _simple_clustering(self, vectors, texts):
        """A simple K-Means clustering implementation."""
        # Determine optimal k (e.g., using elbow method - simplified here)
        num_clusters = max(2, min(5, len(vectors) // self.min_cluster_size))
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(vectors)

        clusters = defaultdict(list)
        for i, label in enumerate(labels):
            clusters[label].append(texts[i])
        
        return [{'cluster_id': k, 'queries': v, 'size': len(v), 'evolution_potential': len(v) >= self.min_cluster_size} for k, v in clusters.items()]
    
    def _check_evolution_opportunity(self, cluster_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Check if any clusters meet the criteria for domain evolution."""
        if cluster_analysis.get('status') != 'complete':
            return {'evolution_ready': False, 'reason': 'insufficient_clustering'}
        
        evolution_candidates = []
        
        for cluster in cluster_analysis.get('clusters', []):
            if cluster.get('evolution_potential'):
                # Generate domain candidate
                domain_candidate = self._generate_domain_candidate(cluster)
                if domain_candidate:
                    evolution_candidates.append(domain_candidate)
        
        return {
            'evolution_ready': len(evolution_candidates) > 0,
            'candidates': evolution_candidates,
            'total_candidates': len(evolution_candidates)
        }
    
    def _generate_domain_candidate(self, cluster: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a domain candidate configuration."""
        try:
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
            candidate_id = f"candidate_{int(time.time())}"
            self.candidates[candidate_id] = controller_config
            
            return {
                'candidate_id': candidate_id,
                'domain_name': domain_name,
                'controller_config': controller_config,
                'evolution_confidence': min(cluster['size'] / self.min_cluster_size, 1.0)
            }
        except Exception as e:
            logger.error(f"Error generating domain candidate for cluster {cluster.get('cluster_id')}: {e}")
            return None
    
    def _extract_common_terms(self, queries: List[str]) -> List[str]:
        """Extract common terms from a list of queries."""
        if not queries: return []
        from collections import Counter
        
        # Simple term extraction (could be enhanced with NLP)
        all_terms = []
        for query in queries:
            terms = [word.lower().strip('.,!?') for word in query.split() 
                    if len(word) > 3 and word.lower() not in ['what', 'how', 'when', 'where', 'why', 'the', 'and', 'or', 'for', 'are', 'is']]
            all_terms.extend(terms)
        
        # Get most common terms
        term_counts = Counter(all_terms)
        common_terms = [term for term, count in term_counts.most_common(5) if count >= 2]
        
        return common_terms
    
    def _generate_domain_name(self, common_terms: List[str]) -> str:
        """Generate a domain name from common terms."""
        if not common_terms:
            return f"EmergentDomain{len(self.candidates) + 1}"
        
        # Create a domain name from the most common term
        primary_term = "".join(word.capitalize() for word in common_terms[0].split())
        
        # Add contextual suffix
        if any(term in ['control', 'system', 'process'] for term in common_terms):
            domain_name = f"{primary_term}System"
        elif any(term in ['analysis', 'data', 'pattern'] for term in common_terms):
            domain_name = f"{primary_term}Analysis"
        else:
            domain_name = f"{primary_term}Domain"
        
        return domain_name
    
    def generate_controller_draft(self, candidate_id: str) -> str:
        """Generate a draft controller class for Keyholder review."""
        if candidate_id not in self.candidates:
            raise ValueError(f"Unknown candidate ID: {candidate_id}")
        
        config = self.candidates[candidate_id]
        
        # Determine controller type
        controller_type = self._determine_controller_type(config)
        template = self.controller_templates.get(controller_type, self.controller_templates['analytical'])

        # Generate controller code
        controller_code = self._generate_controller_code(config, controller_type)
        return controller_code

    def _determine_controller_type(self, config: Dict[str, Any]) -> str:
        """Determine the type of controller to generate."""
        keywords = config.get('detection_patterns', [])
        if any(w in ['create', 'generate', 'design'] for w in keywords):
            return 'creative'
        elif any(w in ['solve', 'optimize', 'fix'] for w in keywords):
            return 'problem_solving'
        else:
            return 'analytical'

    def _generate_controller_code(self, config: Dict[str, Any], controller_type: str) -> str:
        """Generate controller code based on configuration and type."""
        template = self.controller_templates[controller_type]
        
        domain_name = config.get('domain_name', 'NewDomain')
        description = f"Handles queries related to {config.get('detection_patterns', [])}"
        capabilities = config.get('detection_patterns', []) # simple mapping
        
        return template.format(
            domain_name=domain_name,
            domain_description=description,
            capabilities=capabilities,
            solving_methods=capabilities # for problem solving template
        )
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status and recommendations."""
        return {
            'total_fallback_queries': len(self.fallback_queries),
            'domain_candidates_count': len(self.candidates),
            'domain_candidates': self.candidates,
            'evolution_history': [], # No history tracking in this simplified version
            'next_evolution_threshold': self.min_cluster_size,
            'current_confidence_threshold': self.confidence_threshold,
            'ready_for_evolution': len(self.candidates) > 0
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
    
    def __init__(self, protocol_chunks: List[str], llm_provider: Optional[BaseLLMProvider] = None, event_callback: Optional[callable] = None, loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        Initialize the Adaptive Cognitive Orchestrator
        
        Args:
            protocol_chunks: List of protocol text chunks for domain controllers
            llm_provider: An optional LLM provider for generative capabilities
            event_callback: An optional callable for emitting events to a listener (like the VCD)
            loop: The asyncio event loop to run callbacks on.
        """
        # Initialize base system if available
        if CognitiveResonantControllerSystem:
            self.base_system = CognitiveResonantControllerSystem(
                protocol_chunks=protocol_chunks,
                llm_provider=llm_provider # Pass the provider down to the CRCS
            )
        else:
            self.base_system = None
            logger.warning("CognitiveResonantControllerSystem not found. ACO running in standalone mode.")
        
        # Initialize meta-learning components
        self.pattern_engine = PatternEvolutionEngine()
        self.domain_detector = EmergentDomainDetector()
        self.evolution_candidates = {}
        
        # Add event callback for VCD integration
        self.event_callback = event_callback
        self.loop = loop
        
        # Instantiate RISE orchestrator for handling high-stakes queries
        self.rise_orchestrator = RISE_Orchestrator(
            event_callback=self.event_callback  # Pass the callback to RISE
        )
        # Hook the event callback into RISE as well
        if self.event_callback:
            self.rise_orchestrator.event_callback = self.event_callback
        
        # Meta-learning configuration
        self.meta_learning_active = True
        
        # Performance tracking for adaptive tuning
        self.performance_history = deque(maxlen=100)
        
        self.learning_metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'evolution_opportunities': 0,
            'controllers_created': 0
        }
        
        logger.info("[ACO] Initialized with evolution capabilities")
    
    def process_query_with_evolution(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Process query with potential evolution."""
        self.learning_metrics['total_queries'] += 1
        
        try:
            self.emit_aco_event("QueryReceived", f"ACO received query: {query[:80]}...", {"query": query})

            # --- High-Stakes Query Escalation to RISE ---
            high_stakes_keywords = ['strategy', 'strategic', 'plan', 'framework', 'protocol', 'pharmaceutical', 'ethical']
            if any(keyword in query.lower() for keyword in high_stakes_keywords):
                self.emit_aco_event("Escalation", "High-stakes query detected. Escalating to RISE Engine.", {"keywords": high_stakes_keywords})
                
                # RISE workflow is synchronous and long-running
                rise_result = self.rise_orchestrator.run_rise_workflow(query)
                
                self.emit_aco_event("RISEComplete", "RISE Engine workflow finished.", {"rise_result": rise_result})
                
                # The final result from RISE is the context
                context = json.dumps(rise_result.get('final_strategy', {'error': 'No strategy produced'}), indent=2)
                
                # For now, metrics are simple. In a real scenario, we'd parse the RISE IAR.
                response_metrics = {
                    'active_domain': 'RISE_Engine',
                    'escalated': True,
                    'rise_session_id': rise_result.get('session_id')
                }
                return context, response_metrics

            # --- Base System Processing (if available) ---
            if self.base_system:
                self.emit_aco_event("Routing", "Routing to Cognitive Resonant Controller System (CRCS).", {})
                context, base_metrics = self.base_system.process_query(query)
                success = bool(context)
                active_domain = base_metrics.get('active_domain', 'standalone')
            else:
                # Standalone processing
                context, base_metrics = f"Processed query (standalone): {query}", {}
                success = True
                active_domain = "standalone"
        
            # --- Pattern Analysis ---
            pattern_analysis = self.pattern_engine.analyze_query_pattern(
                query, success=success, active_domain=active_domain
            )
            
            # --- Adaptation and Evolution ---
            evolution_opportunity = self._attempt_adaptation(query, pattern_analysis)
            if evolution_opportunity.get('adaptation_type'):
                self.learning_metrics['evolution_opportunities'] += 1
                logger.info(f"[ACO] Evolution opportunity detected: {evolution_opportunity}")
            
            self.learning_metrics['successful_queries'] += 1
            
            # --- Final Response ---
            response_metrics = {
                'pattern_analysis': pattern_analysis,
                'evolution_opportunity': evolution_opportunity,
                'learning_metrics': self.learning_metrics.copy()
            }
            response_metrics.update(base_metrics)

            return context, response_metrics
            
        except Exception as e:
            self.emit_aco_event("Error", "An error occurred during ACO processing.", {"error": str(e)})
            logger.error(f"[ACO] Error processing query: {e}", exc_info=True)
            return f"Error processing query: {str(e)}", {
                'error': str(e),
                'learning_metrics': self.learning_metrics.copy()
            }
    
    def emit_aco_event(self, step_name: str, message: str, metadata: Dict[str, Any]) -> None:
        """Emits an event for the VCD or other listeners."""
        if not self.event_callback or not self.loop:
            return

        event = {
            "type": "thought_process_step",
            "source": "ACO",
            "step_id": f"aco_{step_name.lower()}_{int(time.time() * 1000)}",
            "step_name": step_name,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        try:
            # Schedule the async callback to run on the provided event loop
            self.loop.call_soon_threadsafe(asyncio.create_task, self.event_callback(event))
        except Exception as e:
            logger.error(f"Failed to emit ACO event: {e}")

    def _attempt_adaptation(self, query: str, pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to adapt the system based on pattern analysis."""
        adaptation_result = {
            'adaptation_type': None,
            'confidence': 0.0,
            'changes_made': [],
            'new_capabilities': []
        }
        
        occurrences = pattern_analysis.get('occurrences', 0)
        success_rate = pattern_analysis.get('success_rate', 1.0)
        
        # Check for high-frequency patterns to generate a controller
        if occurrences > 10 and pattern_analysis.get('emergent_potential', {}).get('recommendation') == 'create_controller':
            adaptation_result['adaptation_type'] = 'controller_creation'
            adaptation_result['confidence'] = min(0.9, occurrences / 20)
            
            # Generate controller candidate
            candidate = self._generate_controller_candidate(query, pattern_analysis)
            if candidate:
                self.evolution_candidates[candidate['id']] = candidate
                adaptation_result['changes_made'].append(f"Created controller candidate: {candidate['id']}")
                adaptation_result['new_capabilities'].append(candidate['capabilities'])
        
        # Check for low success rates to trigger tuning
        if success_rate < 0.5 and occurrences > 5:
            adaptation_result['adaptation_type'] = 'parameter_tuning'
            adaptation_result['confidence'] = 0.7
            adaptation_result['changes_made'].append("Triggered parameter tuning analysis")
            self._auto_tune_parameters()
    
        return adaptation_result

    def _generate_controller_candidate(self, query:str, pattern_analysis: Dict) -> Optional[Dict]:
        """Generates a new controller candidate."""
        try:
            # Simplified candidate generation
            candidate_id = f"candidate_{int(time.time())}"
            common_terms = self._extract_common_terms([q['query'] for q in self.pattern_engine.query_history if q['pattern_signature'] == pattern_analysis['pattern_signature']])
            domain_name = self._generate_domain_name(common_terms)
            
            candidate = {
                'id': candidate_id,
                'domain_name': domain_name,
                'description': f"Domain for queries like: {query[:50]}...",
                'keywords': common_terms,
                'confidence': 0.8,
                'capabilities': ['query_processing', 'pattern_recognition'],
                'config': { 'domain_name': domain_name, 'description': "...", 'keywords': common_terms, 'capabilities': []}
            }
            return candidate
        except Exception as e:
            logger.error(f"Error creating domain candidate: {e}")
            return None

    def _extract_common_terms(self, queries: List[str]) -> List[str]:
        """Extract common terms from a list of queries."""
        if not queries: return []
        from collections import Counter
        all_terms = []
        for query in queries:
            terms = [word.lower().strip('.,!?') for word in query.split() if len(word) > 4 and word.lower() not in ['what', 'how', 'when', 'where', 'why', 'the', 'and', 'or', 'for', 'are', 'is']]
            all_terms.extend(terms)
        term_counts = Counter(all_terms)
        return [term for term, count in term_counts.most_common(3)]

    def _generate_domain_name(self, common_terms: List[str]) -> str:
        """Generate a domain name from common terms."""
        if not common_terms:
            return f"EmergentDomain{len(self.evolution_candidates)}"
        return "".join(word.capitalize() for word in common_terms) + "Domain"
    
    def _auto_tune_parameters(self):
        """Auto-tune system parameters based on performance history"""
        # This is a placeholder for a more sophisticated tuning mechanism
        logger.info("[ACO] Auto-tuning analysis triggered. (Placeholder)")
        pass

    # --- ADVANCED FEATURES FROM SPEC ---

    def share_learning_across_instances(self, other_instance_data: Dict[str, Any]) -> bool:
        """Share learning data across ArchE instances."""
        try:
            # Import patterns from other instance
            if 'pattern_signatures' in other_instance_data:
                for signature, data in other_instance_data['pattern_signatures'].items():
                    if signature not in self.pattern_engine.pattern_signatures:
                        self.pattern_engine.pattern_signatures[signature] = data
            
            # Import evolution candidates
            if 'evolution_candidates' in other_instance_data:
                for candidate_id, candidate in other_instance_data['evolution_candidates'].items():
                    if candidate_id not in self.evolution_candidates:
                        self.evolution_candidates[candidate_id] = candidate
            
            logger.info("Successfully shared learning data across instances")
            return True
        except Exception as e:
            logger.error(f"Error sharing learning data: {e}")
            return False

    def predict_evolution_needs(self) -> Dict[str, Any]:
        """Predict future evolution needs based on current patterns."""
        # Placeholder for a predictive model
        logger.warning("Predictive evolution is not fully implemented.")
        return {
            'predicted_domains': [], 'confidence': 0.0, 'timeline': 'unknown', 'recommendations': []
        }

    def get_evolution_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics on evolution progress."""
        success_rates = [p['success_count'] / p['occurrences'] for p in self.pattern_engine.pattern_signatures.values() if p['occurrences'] > 0]
        return {
            'learning_metrics': self.learning_metrics,
            'pattern_analytics': {
                'total_patterns': len(self.pattern_engine.pattern_signatures),
                'active_patterns': sum(1 for p in self.pattern_engine.pattern_signatures.values() if p.get('occurrences', 0) > 5),
                'avg_success_rate': np.mean(success_rates) if success_rates else 0.0
            },
            'evolution_analytics': {
                'total_candidates': len(self.evolution_candidates),
                'candidates_approved': sum(1 for c in self.evolution_candidates.values() if c.get('status') == 'approved'),
                'controllers_created': self.learning_metrics['controllers_created']
            },
        }
    
    def get_system_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive system diagnostics including ACO-specific metrics"""
        # Get base diagnostics if system exists
        base_diagnostics = self.base_system.get_system_diagnostics() if self.base_system else {}
        
        # Add ACO-specific diagnostics
        aco_diagnostics = self.get_evolution_analytics()
        aco_diagnostics['meta_learning_active'] = self.meta_learning_active
        
        # Combine diagnostics
        base_diagnostics['aco_diagnostics'] = aco_diagnostics
        return base_diagnostics
    
    def _handle_evolution_opportunity(self, evolution_opportunity: Dict[str, Any]) -> None:
        """Handle detected evolution opportunities."""
        for candidate in evolution_opportunity.get('candidates', []):
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
            
            # self.evolution_log.append(evolution_event) # No history tracking in this simplified version
            
            logger.info(f"[ACO-EVOLUTION] New domain candidate detected: {domain_name} (confidence: {confidence:.2f})")
            logger.info(f"[ACO-EVOLUTION] Candidate ID: {candidate_id} - Awaiting Keyholder review")
    
    def get_evolution_candidates_for_review(self) -> Dict[str, Any]:
        """Get evolution candidates ready for Keyholder review."""
        candidates = {}
        
        for candidate_id, config in self.domain_detector.candidates.items():
            # Generate controller draft
            try:
                controller_draft = self.domain_detector.generate_controller_draft(candidate_id)
                candidates[candidate_id] = {
                    'config': config,
                    'controller_draft': controller_draft,
                    'status': 'ready_for_review'
                }
            except Exception as e:
                 logger.error(f"Failed to generate draft for {candidate_id}: {e}")
        
        return {
            'total_candidates': len(candidates),
            'candidates': candidates,
            'evolution_log': [], # No history tracking in this simplified version
            'evolution_status': self.domain_detector.get_evolution_status()
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
        "Analyze market trends for Q4 2024",
        "Analyze market trends for Q1 2025",
        "Compare market performance last year",
        "Generate a report on market trends",
        "Create a new marketing strategy based on trends",
        "How do cognitive architectures learn?",
        "What is meta-learning in AI?",
        "Explain pattern evolution in adaptive systems",
        "Can you create a new controller for me?",
        "Generate a creative solution for customer retention",
        "Solve the logistics optimization problem for our fleet",
        "Optimize our supply chain based on new data"
    ]
    
    print("🧠 Testing Adaptive Cognitive Orchestrator")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        context, metrics = aco.process_query_with_evolution(query)
        
        print(f"✅ Success - Domain: {metrics.get('active_domain', 'standalone')}")
        print(f"Context: {context[:100]}...")
        
        if metrics.get('pattern_analysis'):
            pattern = metrics['pattern_analysis']
            print(f"Pattern Signature: {pattern.get('pattern_signature')}")
            print(f"Occurrences: {pattern.get('occurrences', 0)}")
            if pattern.get('emergent_potential', {}).get('recommendation') == 'create_controller':
                print("🧠 EVOLUTION OPPORTUNITY: CREATE CONTROLLER")
        
        if metrics.get('evolution_opportunity',{}).get('adaptation_type'):
             print(f"⚡ ADAPTATION ATTEMPTED: {metrics['evolution_opportunity']['adaptation_type']}")

    
    # Show final diagnostics
    print("\n" + "=" * 60)
    print("FINAL SYSTEM DIAGNOSTICS")
    print("=" * 60)
    
    diagnostics = aco.get_system_diagnostics()
    aco_diag = diagnostics.get('aco_diagnostics', {})
    
    print(f"Evolution Analytics:")
    analytics = aco_diag.get('evolution_analytics', {})
    for key, value in analytics.items():
        print(f"  {key}: {value}")
    
    print(f"\nLearning Metrics:")
    learning = aco_diag.get('learning_metrics', {})
    for key, value in learning.items():
        print(f"  {key}: {value}")

    # Test controller generation
    if aco.evolution_candidates:
        print("\n" + "="*60)
        print("GENERATING CONTROLLER DRAFT")
        print("="*60)
        candidate_id = list(aco.evolution_candidates.keys())[0]
        candidate_config = aco.evolution_candidates[candidate_id]['config']
        
        # Manually add to detector for draft generation
        aco.domain_detector.candidates[candidate_id] = candidate_config
        
        draft = aco.domain_detector.generate_controller_draft(candidate_id)
        print(draft) 