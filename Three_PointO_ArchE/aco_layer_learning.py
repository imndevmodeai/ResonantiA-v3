"""
ACO Layer Selection Learning System
ResonantiA Protocol v3.5-GP - Automatic Layer Orchestration & Learning

The ACO learns optimal layer selections from successful conversations,
streamlining knowledge gains and improving efficiency over time.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

# ============================================================================
# TEMPORAL CORE INTEGRATION
# ============================================================================
try:
    from .temporal_core import now_iso
except ImportError:
    def now_iso():
        return datetime.utcnow().isoformat() + "Z"


class ACOLayerLearningSystem:
    """
    Learning system for ACO to optimize Russian Doll layer selection.
    
    Tracks successful conversations and learns optimal layer selections,
    enabling streamlined knowledge gains over time.
    """
    
    def __init__(self, learning_data_path: Optional[Path] = None):
        """
        Initialize the learning system.
        
        Args:
            learning_data_path: Optional path to persist learning data
        """
        self.learning_data_path = learning_data_path or Path("Three_PointO_ArchE/ledgers/aco_layer_learning.json")
        self.learning_data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Learning data structures
        self.query_patterns: Dict[str, Dict[str, Any]] = {}  # query_signature → pattern data
        self.layer_success_rates: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))  # query_type → layer → success_rate
        self.reinforced_patterns: Dict[str, str] = {}  # query_signature → optimal_layer
        self.conversation_history: deque = deque(maxlen=1000)  # Recent conversations
        
        # Load existing learning data
        self._load_learning_data()
        
        logger.info(f"ACO Layer Learning System initialized with {len(self.reinforced_patterns)} learned patterns")
    
    def _create_query_signature(self, query: str) -> str:
        """
        Create a normalized signature for a query pattern.
        
        Normalizes query to capture intent while ignoring specific SPR names.
        """
        query_lower = query.lower().strip()
        
        # Extract query structure (normalize SPR names)
        import re
        # Replace SPR IDs with placeholder
        normalized = re.sub(r'\b[A-Z][a-z]+[A-Z][a-z]*\b', '[SPR]', query_lower)
        
        # Extract key intent words
        intent_words = []
        intent_patterns = [
            r'\b(what|who|when|where|why|how)\b',
            r'\b(show|tell|explain|describe|define)\b',
            r'\b(code|implementation|spec|specification)\b',
            r'\b(use|workflow|example|how to)\b',
            r'\b(summary|overview|brief)\b',
            r'\b(analyze|detailed|full|complete)\b'
        ]
        
        for pattern in intent_patterns:
            matches = re.findall(pattern, normalized)
            intent_words.extend(matches)
        
        # Create signature from structure + intent
        signature_parts = [normalized[:50]] + sorted(set(intent_words))
        signature = '|'.join(signature_parts)
        
        # Hash for consistent storage
        return hashlib.md5(signature.encode()).hexdigest()[:16]
    
    def select_optimal_layer(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Select optimal layer using learned patterns + heuristics.
        
        Args:
            query: User query
            context: Optional context (task_type, token_budget, etc.)
            
        Returns:
            Tuple of (selected_layer, selection_source)
            selection_source: "learned", "heuristic", or "default"
        """
        query_signature = self._create_query_signature(query)
        
        # Priority 1: Use learned successful pattern
        if query_signature in self.reinforced_patterns:
            optimal_layer = self.reinforced_patterns[query_signature]
            pattern_data = self.query_patterns.get(query_signature, {})
            success_rate = pattern_data.get('success_rate', 0.0)
            
            if success_rate > 0.8:  # High confidence learned pattern
                logger.debug(f"Using learned pattern: {query_signature} → {optimal_layer} (success: {success_rate:.1%})")
                return optimal_layer, "learned"
        
        # Priority 2: Use adaptive heuristics
        try:
            from .russian_doll_retrieval import select_layer_from_query
            heuristic_layer = select_layer_from_query(query, context)
            logger.debug(f"Using heuristic selection: {heuristic_layer}")
            return heuristic_layer, "heuristic"
        except Exception as e:
            logger.warning(f"Heuristic selection failed: {e}")
        
        # Priority 3: Default fallback
        return "Micro", "default"
    
    def track_conversation(
        self,
        query: str,
        selected_layer: str,
        success: bool,
        user_satisfaction: Optional[float] = None,
        response_quality: Optional[float] = None
    ):
        """
        Track a conversation for learning.
        
        Args:
            query: User query
            selected_layer: Layer that was selected
            success: Whether conversation was successful
            user_satisfaction: Optional user satisfaction score (0.0-1.0)
            response_quality: Optional response quality metric
        """
        query_signature = self._create_query_signature(query)
        timestamp = now_iso()
        
        # Record conversation
        conversation_record = {
            'query': query,
            'query_signature': query_signature,
            'selected_layer': selected_layer,
            'success': success,
            'user_satisfaction': user_satisfaction,
            'response_quality': response_quality,
            'timestamp': timestamp
        }
        
        self.conversation_history.append(conversation_record)
        
        # Update pattern tracking
        if query_signature not in self.query_patterns:
            self.query_patterns[query_signature] = {
                'first_seen': timestamp,
                'total_attempts': 0,
                'success_count': 0,
                'layer_attempts': defaultdict(int),
                'layer_successes': defaultdict(int),
                'optimal_layer': None,
                'success_rate': 0.0
            }
        
        pattern = self.query_patterns[query_signature]
        pattern['total_attempts'] += 1
        pattern['layer_attempts'][selected_layer] += 1
        
        if success:
            pattern['success_count'] += 1
            pattern['layer_successes'][selected_layer] += 1
        
        # Calculate success rate for this layer
        layer_attempts = pattern['layer_attempts'][selected_layer]
        layer_successes = pattern['layer_successes'][selected_layer]
        
        if layer_attempts > 0:
            layer_success_rate = layer_successes / layer_attempts
            pattern['success_rate'] = pattern['success_count'] / pattern['total_attempts']
            
            # Update optimal layer if this one is better
            current_optimal = pattern.get('optimal_layer')
            if current_optimal is None:
                pattern['optimal_layer'] = selected_layer
                self.reinforced_patterns[query_signature] = selected_layer
            else:
                current_optimal_rate = pattern['layer_successes'][current_optimal] / max(
                    pattern['layer_attempts'][current_optimal], 1
                )
                if layer_success_rate > current_optimal_rate + 0.1:  # 10% improvement threshold
                    pattern['optimal_layer'] = selected_layer
                    self.reinforced_patterns[query_signature] = selected_layer
                    logger.info(
                        f"ACO learned new optimal: {query_signature[:8]}... → {selected_layer} "
                        f"(success: {layer_success_rate:.1%} vs {current_optimal_rate:.1%})"
                    )
        
        # Auto-save periodically
        if len(self.conversation_history) % 10 == 0:
            self._save_learning_data()
    
    def reinforce_successful_pattern(
        self,
        query_signature: str,
        layer: str,
        success_rate: float
    ):
        """
        Explicitly reinforce a successful pattern.
        
        Called when a conversation proves successful.
        """
        if success_rate > 0.8:  # High success threshold
            self.reinforced_patterns[query_signature] = layer
            
            if query_signature in self.query_patterns:
                self.query_patterns[query_signature]['optimal_layer'] = layer
                self.query_patterns[query_signature]['success_rate'] = success_rate
            
            logger.info(
                f"ACO reinforced pattern: {query_signature[:8]}... → {layer} "
                f"(success rate: {success_rate:.1%})"
            )
            
            self._save_learning_data()
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about learning progress."""
        total_patterns = len(self.query_patterns)
        learned_patterns = len(self.reinforced_patterns)
        total_conversations = len(self.conversation_history)
        
        # Calculate average success rate
        avg_success_rate = 0.0
        if self.query_patterns:
            total_success_rate = sum(p.get('success_rate', 0.0) for p in self.query_patterns.values())
            avg_success_rate = total_success_rate / len(self.query_patterns)
        
        return {
            'total_patterns': total_patterns,
            'learned_patterns': learned_patterns,
            'learning_coverage': learned_patterns / max(total_patterns, 1),
            'total_conversations': total_conversations,
            'average_success_rate': avg_success_rate,
            'reinforced_patterns': dict(list(self.reinforced_patterns.items())[:10])  # Sample
        }
    
    def _load_learning_data(self):
        """Load learning data from persistent storage."""
        if not self.learning_data_path.exists():
            logger.debug(f"Learning data file not found: {self.learning_data_path}")
            return
        
        try:
            with open(self.learning_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.query_patterns = data.get('query_patterns', {})
            self.reinforced_patterns = data.get('reinforced_patterns', {})
            
            # Convert defaultdict data back
            for pattern in self.query_patterns.values():
                if 'layer_attempts' in pattern:
                    pattern['layer_attempts'] = defaultdict(int, pattern['layer_attempts'])
                if 'layer_successes' in pattern:
                    pattern['layer_successes'] = defaultdict(int, pattern['layer_successes'])
            
            logger.info(f"Loaded {len(self.query_patterns)} patterns, {len(self.reinforced_patterns)} reinforced")
        except Exception as e:
            logger.warning(f"Failed to load learning data: {e}")
    
    def _save_learning_data(self):
        """Save learning data to persistent storage."""
        try:
            # Convert defaultdicts to regular dicts for JSON
            serializable_patterns = {}
            for sig, pattern in self.query_patterns.items():
                serializable_patterns[sig] = {
                    **pattern,
                    'layer_attempts': dict(pattern.get('layer_attempts', {})),
                    'layer_successes': dict(pattern.get('layer_successes', {}))
                }
            
            data = {
                'query_patterns': serializable_patterns,
                'reinforced_patterns': self.reinforced_patterns,
                'last_updated': now_iso()
            }
            
            with open(self.learning_data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved learning data: {len(self.query_patterns)} patterns")
        except Exception as e:
            logger.warning(f"Failed to save learning data: {e}")

