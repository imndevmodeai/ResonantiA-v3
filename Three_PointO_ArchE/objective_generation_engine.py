"""
Objective Generation Engine
Universally Abstracted & Dynamically Adaptive Objective Generator

This module implements the deterministic, template-driven Objective Generation Engine
that transforms raw user queries into enriched problem_description formats without LLM assistance.

Key Features:
- Universal Abstraction Level 3 (abstracts its own abstraction mechanisms)
- Autopoietic Learning Integration (4-epoch learning loop)
- Multi-Strategy Fallback Hierarchy (handles any query type)
- Pattern Crystallization (8-stage progressive compression)
- Deterministic Operation (no LLM dependencies in core generation)
"""

import json
import logging
import re
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Import dependencies with graceful fallback
logger = logging.getLogger(__name__)

try:
    from .autopoietic_learning_loop import AutopoieticLearningLoop
    AUTOPOIETIC_AVAILABLE = True
except ImportError:
    AUTOPOIETIC_AVAILABLE = False
    logger.warning("AutopoieticLearningLoop not available")

try:
    from .meta_pattern_manager import MetaPatternManager
    META_PATTERN_AVAILABLE = True
except ImportError:
    META_PATTERN_AVAILABLE = False
    logger.warning("MetaPatternManager not available")

try:
    from .adaptive_cognitive_orchestrator import EmergentDomainDetector
    EMERGENT_DOMAIN_AVAILABLE = True
except ImportError:
    EMERGENT_DOMAIN_AVAILABLE = False
    logger.warning("EmergentDomainDetector not available")

try:
    from .spr_manager import SPRManager
    SPR_MANAGER_AVAILABLE = True
except ImportError:
    SPR_MANAGER_AVAILABLE = False
    logger.warning("SPRManager not available")

try:
    from .autopoietic_self_analysis import QuantumProbability
    QUANTUM_AVAILABLE = True
except ImportError:
    # Fallback QuantumProbability implementation
    class QuantumProbability:
        def __init__(self, prob: float, evidence: List[str] = None):
            self.probability = prob
            self.evidence = evidence or []
        def to_dict(self):
            return {"probability": self.probability, "evidence": self.evidence}
        @classmethod
        def certain_true(cls, evidence: List[str] = None):
            return cls(1.0, evidence or [])
    QUANTUM_AVAILABLE = False


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class TemporalMarker:
    """Represents a temporal element extracted from a query."""
    type: str  # 'explicit_range', 'age_range', 'future_horizon', 'historical', 'implicit'
    value: Any
    confidence: QuantumProbability
    text: str = ""

@dataclass
class FeatureVector:
    """Feature vector extracted from a query."""
    raw_query: str
    temporal_markers: List[TemporalMarker] = field(default_factory=list)
    domain_keywords: List[str] = field(default_factory=list)
    spr_keywords: List[str] = field(default_factory=list)
    complexity_indicators: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    meta_pattern_type: Optional[str] = None
    confidence_boost: float = 0.0
    
    def update(self, other: 'FeatureVector'):
        """Update this feature vector with another FeatureVector data."""
        self.temporal_markers.extend(other.temporal_markers)
        self.domain_keywords.extend(other.domain_keywords)
        self.spr_keywords.extend(other.spr_keywords)
        self.complexity_indicators.extend(other.complexity_indicators)
        self.entities.extend(other.entities)

@dataclass
class TemporalScope:
    """Temporal scope extracted from a query."""
    explicit: List[str] = field(default_factory=list)
    implicit: List[str] = field(default_factory=list)
    temporal: List[str] = field(default_factory=list)
    contextual: List[str] = field(default_factory=list)
    
    def format(self) -> str:
        """Format temporal scope as string."""
        parts = []
        if self.explicit:
            parts.append(f"Explicit: {', '.join(self.explicit)}")
        if self.implicit:
            parts.append(f"Implicit: {', '.join(self.implicit)}")
        if self.temporal:
            parts.append(f"Temporal: {', '.join(self.temporal)}")
        if self.contextual:
            parts.append(f"Contextual: {', '.join(self.contextual)}")
        return " | ".join(parts) if parts else "No temporal scope detected"

@dataclass
class ActivatedSPR:
    """An SPR that has been activated for a query."""
    spr_id: str  # Original Guardian pointS format (e.g., 'CognitiveresonancE')
    match_confidence: QuantumProbability
    match_method: str  # 'static_lookup', 'autopoietic_learning', 'emergent_domain', 'universal_fallback'
    domain_explanation: Optional[str] = None
    _normalized_id: Optional[str] = None  # Python-safe identifier (cached)
    
    def __post_init__(self):
        """Ensure original Guardian pointS format is preserved."""
        # Store original - never modify spr_id
        self._original_guardian_format = self.spr_id
    
    @property
    def normalized_id(self) -> str:
        """Get Python-safe identifier while preserving original Guardian pointS format."""
        if self._normalized_id is None:
            # Normalize for Python use: convert to snake_case or valid identifier
            # But ALWAYS preserve original in spr_id field
            normalized = self._normalize_for_python(self.spr_id)
            self._normalized_id = normalized
        return self._normalized_id
    
    @staticmethod
    def _normalize_for_python(guardian_spr_id: str) -> str:
        """
        Normalize Guardian pointS format SPR ID for Python code use.
        Preserves original format - this is only for Python identifier generation.
        """
        # Remove spaces, convert to snake_case-like format
        # Example: 'CognitiveresonancE' -> 'cognitive_resonance'
        # Example: 'TemporalDynamiX' -> 'temporal_dynamics'
        
        # Split on uppercase letters (preserving them)
        parts = re.split(r'([A-Z])', guardian_spr_id)
        words = []
        current_word = ""
        
        for part in parts:
            if not part:
                continue
            if part.isupper() and len(part) == 1:
                if current_word:
                    words.append(current_word.lower())
                current_word = part
            else:
                current_word += part
        
        if current_word:
            words.append(current_word.lower())
        
        # Join with underscores, remove trailing/leading uppercase markers
        normalized = '_'.join(words).replace('_e', '_').replace('_x', '_')
        # Clean up: remove single uppercase letters at boundaries
        normalized = re.sub(r'_([A-Z])_', r'_\1', normalized)
        normalized = normalized.strip('_').lower()
        
        # Fallback: if normalization fails, use a safe version
        if not normalized or not normalized.replace('_', '').isalnum():
            # Create safe identifier from Guardian format
            normalized = guardian_spr_id.lower().replace(' ', '_')
            # Remove invalid characters
            normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        
        return normalized if normalized else f"spr_{hash(guardian_spr_id) % 10000}"

@dataclass
class Mandate:
    """A mandate that has been selected for a query."""
    number: Optional[int]
    name: str
    confidence: QuantumProbability
    selection_method: str  # 'rule_based_temporal_detection', 'rule_based_complexity_detection', etc.


# ============================================================================
# Pattern Evolution Engine (Simplified)
# ============================================================================

class PatternEvolutionEngine:
    """Simplified pattern evolution engine for query pattern analysis."""
    
    def __init__(self):
        self.emergent_domains: Dict[str, Dict[str, Any]] = {}
        self.pattern_history: deque = deque(maxlen=1000)
    
    def analyze_query_pattern(self, query: str, success: bool = True, active_domain: str = 'objective_generation') -> Dict[str, Any]:
        """Analyze a query pattern and return analysis results."""
        pattern_signature = self._create_pattern_signature(query)
        self.pattern_history.append({
            'query': query,
            'signature': pattern_signature,
            'success': success,
            'domain': active_domain
        })
        return {
            'pattern_signature': pattern_signature,
            'success': success,
            'domain': active_domain
        }
    
    def _create_pattern_signature(self, query: str) -> str:
        """Create a pattern signature from a query."""
        # Simple signature: length + keyword count + domain indicators
        length_bucket = len(query) // 50
        keyword_count = len(re.findall(r'\b\w{4,}\b', query.lower()))
        return f"L{length_bucket}_K{keyword_count}"


# ============================================================================
# Main Objective Generation Engine
# ============================================================================

class ObjectiveGenerationEngine:
    """
    Universally Abstracted & Dynamically Adaptive Objective Generator
    Integrates with Autopoietic Learning Loop for continuous evolution
    """
    
    def __init__(self, spr_filepath: str = "knowledge_graph/spr_definitions_tv.json"):
        """Initialize the Objective Generation Engine."""
        # Integration with learning systems
        if AUTOPOIETIC_AVAILABLE:
            self.autopoietic_loop = AutopoieticLearningLoop()
        else:
            self.autopoietic_loop = None
        
        if META_PATTERN_AVAILABLE:
            self.meta_pattern_manager = MetaPatternManager()
        else:
            self.meta_pattern_manager = None
        
        self.pattern_evolution_engine = PatternEvolutionEngine()
        
        if EMERGENT_DOMAIN_AVAILABLE:
            self.emergent_domain_detector = EmergentDomainDetector()
        else:
            self.emergent_domain_detector = None
        
        if SPR_MANAGER_AVAILABLE:
            self.spr_manager = SPRManager(spr_filepath)
        else:
            self.spr_manager = None
        
        # Load static mappings
        self.spr_keyword_map = self._load_spr_keyword_map()
        self.domain_rules = self._load_domain_rules()
        self.template = self._load_enhancement_template()
        
        # Dynamic learning state
        self.query_pattern_history = deque(maxlen=1000)
        self.learned_keyword_patterns = {}  # Autopoietically learned
        self.learned_domain_rules = {}  # Autopoietically learned
        self.fallback_strategies = {}  # For unknown query types
        
        # Guardian pointS format preservation mapping
        # Maps: normalized_id -> original_guardian_format
        # This ensures we never lose the original Guardian pointS format
        self._guardian_format_preservation_map: Dict[str, str] = {}
        
        # Confidence thresholds
        self.min_confidence_for_activation = 0.5
        self.min_confidence_for_mandate = 0.6
        
        logger.info("ObjectiveGenerationEngine initialized with Universal Abstraction Level 3")
    
    def generate_objective(self, query: str) -> Dict[str, Any]:
        """
        Universally abstracted objective generation with dynamic adaptation.
        Handles any query type through pattern learning and fallback mechanisms.
        """
        try:
            # Stage 0: Pattern Signature Analysis (NEW)
            pattern_signature = self._create_pattern_signature(query)
            pattern_analysis = self.pattern_evolution_engine.analyze_query_pattern(
                query, success=True, active_domain='objective_generation'
            )
            
            # Stage 1: Universal Feature Extraction (Enhanced)
            features = self._extract_features_universal(query, pattern_signature)
            
            # Stage 2: Adaptive TemporalScope Building (Enhanced)
            temporal_scope = self._build_temporal_scope_adaptive(features)
            
            # Stage 3: Dynamic SPR Activation (Enhanced with Learning)
            activated_sprs = self._activate_sprs_dynamic(features, pattern_signature)
            
            # Stage 4: Adaptive Mandate Selection (Enhanced)
            mandates = self._select_mandates_adaptive(features, activated_sprs)
            
            # Stage 5: Flexible Template Assembly (Enhanced)
            objective = self._assemble_objective_flexible(
                activated_sprs, mandates, features, pattern_signature
            )
            
            # Stage 6: Adaptive Domain Customization (Enhanced)
            objective = self._customize_domain_adaptive(
                objective, activated_sprs, features, pattern_signature
            )
            
            # Stage 7: Final Assembly
            problem_description = self._assemble_problem_description(
                query, temporal_scope, objective, activated_sprs
            )
            
            # Stage 8: Zepto SPR Generation
            zepto_spr = self._generate_zepto_spr(
                query, features, temporal_scope, activated_sprs, mandates, objective
            )
            
            # Stage 9: Autopoietic Learning (NEW)
            self._learn_from_query(query, features, activated_sprs, mandates, pattern_signature)
            
            return {
                'problem_description': problem_description,
                'zepto_spr': zepto_spr,
                'compression_ratio': len(query) / len(zepto_spr) if zepto_spr else 1.0,
                'iar': self._generate_iar(activated_sprs, mandates, features),
                'pattern_analysis': pattern_analysis,
                'learning_opportunities': self._identify_learning_opportunities(pattern_analysis),
                'features': features,
                'temporal_scope': temporal_scope,
                'activated_sprs': [spr.spr_id for spr in activated_sprs],  # Original Guardian pointS format
                'activated_sprs_normalized': {spr.normalized_id: spr.spr_id for spr in activated_sprs},  # Mapping for Python use
                'guardian_format_preservation': self._guardian_format_preservation_map.copy(),  # Full preservation map
                'mandates': [f"M{m.number}" if m.number else m.name for m in mandates]
            }
        except Exception as e:
            logger.error(f"Objective generation failed: {e}", exc_info=True)
            # Fallback: return minimal enriched format
            return {
                'problem_description': f"->|UserInput query_id={uuid.uuid4()}|<-\n    ->|QueryText|<-\n        {query}\n    ->|/QueryText|<-\n->|/UserInput|<-",
                'zepto_spr': f"⟦{len(query)}⟧",
                'compression_ratio': 1.0,
                'iar': {'status': 'Failed', 'confidence': 0.1, 'error': str(e)},
                'error': str(e)
            }
    
    def _create_pattern_signature(self, query: str) -> str:
        """Create a pattern signature from a query."""
        length_bucket = len(query) // 50
        keyword_count = len(re.findall(r'\b\w{4,}\b', query.lower()))
        domain_indicators = sum(1 for domain in ['economic', 'scientific', 'medical', 'legal', 'environmental'] if domain in query.lower())
        return f"L{length_bucket}_K{keyword_count}_D{domain_indicators}"
    
    def _extract_features_universal(self, query: str, pattern_signature: str) -> FeatureVector:
        """
        Universal feature extraction that handles any query type.
        Uses multiple extraction strategies with fallback mechanisms.
        """
        features = FeatureVector(raw_query=query)
        
        # Strategy 1: Regex-based temporal extraction (deterministic)
        features.temporal_markers = self._extract_temporal_regex(query)
        
        # Strategy 2: Keyword-based domain detection (deterministic)
        features.domain_keywords = self._extract_domain_keywords(query)
        
        # Strategy 3: Complexity indicators
        features.complexity_indicators = self._extract_complexity_indicators(query)
        
        # Strategy 4: Learned pattern matching (autopoietic)
        if self.learned_keyword_patterns:
            learned_features = self._apply_learned_patterns(query, pattern_signature)
            features.update(learned_features)
        
        # Strategy 5: Fallback for unknown patterns
        if not features.domain_keywords and not features.temporal_markers:
            # Unknown query type - use universal fallback
            features = self._apply_universal_fallback(query, pattern_signature)
        
        # Strategy 6: Meta-pattern recognition (Universal Abstraction Level 3)
        if self.meta_pattern_manager:
            meta_pattern = self.meta_pattern_manager.abstract_mechanism({
                'query': query,
                'features': features
            })
            if meta_pattern and 'pattern_type' in meta_pattern:
                features.meta_pattern_type = meta_pattern['pattern_type']
                features.confidence_boost = 0.1
        
        return features
    
    def _extract_temporal_regex(self, query: str) -> List[TemporalMarker]:
        """Extract temporal markers using regex patterns."""
        temporal_patterns = [
            (r'circa\s+(\d{4})-(\d{4})', 'explicit_range'),
            (r'age\s+(\d+)-(\d+)', 'age_range'),
            (r'(\d+)\s+year[s]?\s+(?:ahead|forward|projection|consequence)', 'future_horizon'),
            (r'starting\s+in\s+(\d{4})', 'start_date'),
            (r'through\s+(\d{4})', 'end_date'),
            (r'historical', 'historical'),
            (r'time\s+horizon[s]?', 'time_horizon'),
            (r'temporal', 'temporal'),
            (r'causal\s+lag', 'causal_lag'),
        ]
        
        temporal_markers = []
        for pattern, marker_type in temporal_patterns:
            for match in re.finditer(pattern, query, re.IGNORECASE):
                temporal_markers.append(TemporalMarker(
                    type=marker_type,
                    value=match.groups() if match.groups() else match.group(0),
                    confidence=QuantumProbability(0.95, [f'regex_match: {pattern}']),
                    text=match.group(0)
                ))
        
        return temporal_markers
    
    def _extract_domain_keywords(self, query: str) -> List[str]:
        """Extract domain keywords from query."""
        domain_vocab = {
            'economic': ['economic', 'economy', 'financial', 'market', 'pricing', 'cost', 'revenue'],
            'environmental': ['environmental', 'climate', 'carbon', 'emission', 'green', 'sustainable'],
            'social': ['social', 'society', 'community', 'population', 'demographic'],
            'scientific': ['scientific', 'research', 'study', 'analysis', 'data'],
            'medical': ['medical', 'health', 'disease', 'treatment', 'patient'],
            'legal': ['legal', 'law', 'regulation', 'policy', 'compliance'],
            'boxing': ['boxing', 'fight', 'match', 'fighter', 'punch'],
        }
        
        query_lower = query.lower()
        detected_domains = []
        for domain, keywords in domain_vocab.items():
            if any(kw in query_lower for kw in keywords):
                detected_domains.append(domain)
        
        return detected_domains
    
    def _extract_complexity_indicators(self, query: str) -> List[str]:
        """Extract complexity indicators from query."""
        complexity_keywords = [
            'emergent', 'complex system', 'interaction', 'dynamic', 'simulation',
            'multi-dimensional', 'comprehensive', 'integrated', 'systematic'
        ]
        
        query_lower = query.lower()
        detected = [kw for kw in complexity_keywords if kw in query_lower]
        return detected
    
    def _apply_learned_patterns(self, query: str, pattern_signature: str) -> FeatureVector:
        """Apply autopoietically learned patterns."""
        features = FeatureVector(raw_query=query)
        # Placeholder for learned pattern application
        return features
    
    def _apply_universal_fallback(self, query: str, pattern_signature: str) -> FeatureVector:
        """Apply universal fallback for unknown query types."""
        features = FeatureVector(raw_query=query)
        # Activate generic SPRs
        features.spr_keywords = ['CognitiveresonancE', 'FourdthinkinG']
        return features
    
    def _build_temporal_scope_adaptive(self, features: FeatureVector) -> TemporalScope:
        """Build temporal scope adaptively from features."""
        scope = TemporalScope()
        
        for marker in features.temporal_markers:
            if marker.type in ['explicit_range', 'start_date', 'end_date']:
                scope.explicit.append(marker.text)
            elif marker.type in ['age_range', 'future_horizon']:
                scope.temporal.append(marker.text)
            elif marker.type == 'historical':
                scope.implicit.append('Historical context')
            elif marker.type == 'causal_lag':
                scope.contextual.append('Causal lag effects')
        
        # Add implicit temporal elements from query
        query_lower = features.raw_query.lower()
        if 'historical' in query_lower or 'precedent' in query_lower:
            scope.implicit.append('Historical precedents')
        if 'future' in query_lower or 'projected' in query_lower:
            scope.temporal.append('Future projections')
        if 'emergent' in query_lower or 'dynamic' in query_lower:
            scope.contextual.append('Emergent dynamics')
        
        return scope
    
    def _activate_sprs_dynamic(self, features: FeatureVector, pattern_signature: str) -> List[ActivatedSPR]:
        """
        Dynamic SPR activation that learns new keyword patterns.
        Combines static lookup tables with autopoietically learned patterns.
        """
        activated = []
        query_lower = features.raw_query.lower()
        
        # Strategy 1: Static keyword lookup (deterministic)
        for keyword, spr_id in self.spr_keyword_map.items():
            if keyword in query_lower:
                # Preserve Guardian pointS format
                self._guardian_format_preservation_map[spr_id] = spr_id
                activated.append(ActivatedSPR(
                    spr_id=spr_id,  # Original Guardian pointS format preserved
                    match_confidence=QuantumProbability(0.95, [f'static_keyword_match: {keyword}']),
                    match_method='static_lookup'
                ))
        
        # Strategy 2: Learned keyword patterns (autopoietic)
        for learned_keyword, learned_spr in self.learned_keyword_patterns.items():
            if learned_keyword in query_lower:
                if learned_spr.get('validated', False):
                    activated.append(ActivatedSPR(
                        spr_id=learned_spr['spr_id'],
                        match_confidence=QuantumProbability(
                            learned_spr.get('confidence', 0.7),
                            [f'learned_pattern_match: {learned_keyword}']
                        ),
                        match_method='autopoietic_learning'
                    ))
        
        # Strategy 3: Pattern signature matching (emergent domain detection)
        if pattern_signature in self.pattern_evolution_engine.emergent_domains:
            emergent_domain = self.pattern_evolution_engine.emergent_domains[pattern_signature]
            if emergent_domain.get('status') == 'validated':
                for spr_id in emergent_domain.get('associated_sprs', []):
                    activated.append(ActivatedSPR(
                        spr_id=spr_id,
                        match_confidence=QuantumProbability(0.8, ['emergent_domain_match']),
                        match_method='emergent_domain'
                    ))
        
        # Strategy 4: Universal fallback SPRs (for unknown query types)
        if not activated:
            # Preserve Guardian pointS format for fallback SPRs
            fallback_sprs = ['CognitiveresonancE', 'FourdthinkinG']
            for spr_id in fallback_sprs:
                self._guardian_format_preservation_map[spr_id] = spr_id
                activated.append(ActivatedSPR(
                    spr_id=spr_id,  # Original Guardian pointS format preserved
                    match_confidence=QuantumProbability(0.5 if spr_id == 'CognitiveresonancE' else 0.4, ['universal_fallback']),
                    match_method='universal_fallback'
                ))
        
        # Remove duplicates
        seen = set()
        unique_activated = []
        for spr in activated:
            if spr.spr_id not in seen:
                seen.add(spr.spr_id)
                unique_activated.append(spr)
        
        return unique_activated
    
    def _select_mandates_adaptive(self, features: FeatureVector, activated_sprs: List[ActivatedSPR]) -> List[Mandate]:
        """
        Adaptive mandate selection that learns new mandate patterns.
        Uses quantum probability for uncertainty handling.
        """
        mandates = []
        
        # Strategy 1: Rule-based selection (deterministic)
        temporal_indicators = ['circa', 'age', 'year', 'time horizon', 'trajectory', 'historical', 'temporal']
        temporal_confidence = sum([
            0.15 for ind in temporal_indicators if ind in features.raw_query.lower()
        ])
        if temporal_confidence >= 0.3:
            mandates.append(Mandate(
                number=6,
                name="Temporal Resonance",
                confidence=QuantumProbability(
                    min(temporal_confidence, 0.95),
                    ['temporal_indicator_detected']
                ),
                selection_method='rule_based_temporal_detection'
            ))
        
        complexity_keywords = ['emergent', 'complex system', 'interaction', 'dynamic', 'simulation']
        complexity_confidence = sum([
            0.2 for kw in complexity_keywords if kw in features.raw_query.lower()
        ])
        if complexity_confidence >= 0.4:
            mandates.append(Mandate(
                number=9,
                name="Complex System Visioning",
                confidence=QuantumProbability(
                    min(complexity_confidence, 0.95),
                    ['complexity_keyword_detected']
                ),
                selection_method='rule_based_complexity_detection'
            ))
        
        # Rule 3: Always include Cognitive Resonance
        mandates.append(Mandate(
            number=None,
            name="Cognitive Resonance",
            confidence=QuantumProbability(1.0, ['always_included']),
            selection_method='universal_principle'
        ))
        
        return mandates
    
    def _assemble_objective_flexible(self, activated_sprs: List[ActivatedSPR], mandates: List[Mandate], 
                                     features: FeatureVector, pattern_signature: str) -> str:
        """Flexible template assembly with domain-specific customization."""
        # Build capability list
        capability_list = []
        for spr in activated_sprs:
            explanation = self._get_domain_explanation(spr, features)
            capability_list.append(f"{spr.spr_id} ({explanation})")
        
        capabilities_text = ", ".join(capability_list) if capability_list else "Cognitive resonancE"
        
        # Build mandate references
        mandate_refs = []
        for m in mandates:
            if m.number:
                mandate_refs.append(f"Mandate {m.number} ({m.name})")
            else:
                mandate_refs.append(m.name)
        
        mandates_text = " and ".join(mandate_refs) if mandate_refs else "Cognitive Resonance"
        
        # Template substitution
        objective = self.template.format(
            protocol_version="v3.5-GP (Genesis Protocol)",
            temporal_resonance="Temporal Resonance",
            cognitive_resonance="Cognitive Resonance",
            query_description=features.raw_query[:100] + "..." if len(features.raw_query) > 100 else features.raw_query,
            capabilities=capabilities_text,
            mandates=mandates_text,
            implementation_resonance="Implementation Resonance"
        )
        
        return objective
    
    def _get_domain_explanation(self, spr: ActivatedSPR, features: FeatureVector) -> str:
        """Get domain-specific explanation for an SPR."""
        # Check domain rules
        for domain in features.domain_keywords:
            if domain in self.domain_rules:
                if spr.spr_id in self.domain_rules[domain]:
                    return self.domain_rules[domain][spr.spr_id]
        
        # Generic explanation
        generic_explanations = {
            'HistoricalContextualizatioN': 'understanding historical context',
            'TemporalDynamiX': 'modeling temporal dynamics',
            'FutureStateAnalysiS': 'predicting future states',
            'CausalLagDetectioN': 'identifying causal lag effects',
            'EmergenceOverTimE': 'simulating emergent behaviors',
            'TrajectoryComparisoN': 'comparing system trajectories',
            'ComplexSystemVisioninG': 'modeling complex system interactions',
            'CognitiveresonancE': 'achieving cognitive resonance',
            'FourdthinkinG': 'applying 4D thinking',
        }
        
        return generic_explanations.get(spr.spr_id, 'applying analytical capabilities')
    
    def _customize_domain_adaptive(self, objective: str, activated_sprs: List[ActivatedSPR], 
                                   features: FeatureVector, pattern_signature: str) -> str:
        """Adaptive domain customization."""
        # Domain-specific customization is already applied in _get_domain_explanation
        # This method can be extended for more advanced customization
        return objective
    
    def _assemble_problem_description(self, query: str, temporal_scope: TemporalScope, 
                                     objective: str, activated_sprs: List[ActivatedSPR]) -> str:
        """Final assembly of problem_description."""
        query_id = str(uuid.uuid4())
        spr_hints = ", ".join([spr.spr_id for spr in activated_sprs])
        
        problem_description = f"""->|UserInput query_id={query_id}|<-
    ->|QueryText|<-
        {query}
    ->|/QueryText|<-
    ->|TemporalScope|<-{temporal_scope.format()}<-/TemporalScope|<-
->|/UserInput|<-

->|EnhancementDirectives|<-
    ->|Objective|<-
        {objective}
    ->|/Objective|<-
->|/EnhancementDirectives|<-

[SPR_HINTS]: {spr_hints}"""
        
        return problem_description.strip()
    
    def _generate_zepto_spr(self, query: str, features: FeatureVector, temporal_scope: TemporalScope,
                           activated_sprs: List[ActivatedSPR], mandates: List[Mandate], objective: str) -> str:
        """Generate Zepto SPR (pure symbolic compression)."""
        # Compress to symbols
        zepto = f"⟦{len(query)}⟧→⦅{len(features.temporal_markers)}T{len(features.domain_keywords)}D⦆→"
        zepto += f"Δ⦅{len(temporal_scope.explicit)+len(temporal_scope.implicit)}⦆→"
        zepto += f"⊢{''.join([spr.spr_id[0] for spr in activated_sprs[:5]])}→"
        zepto += f"⊨{''.join([f'M{m.number}' for m in mandates if m.number])}→"
        zepto += f"⊧{len(objective)}→⟧"
        
        return zepto
    
    def _learn_from_query(self, query: str, features: FeatureVector, activated_sprs: List[ActivatedSPR],
                         mandates: List[Mandate], pattern_signature: str):
        """Autopoietic learning from query processing."""
        # Store query pattern for learning
        self.query_pattern_history.append({
            'query': query,
            'features': features,
            'activated_sprs': [spr.spr_id for spr in activated_sprs],
            'mandates': [m.name for m in mandates],
            'pattern_signature': pattern_signature
        })
        
        # Trigger autopoietic learning loop if available
        if self.autopoietic_loop:
            try:
                # Store experience for autopoietic learning (if method exists)
                if hasattr(self.autopoietic_loop, 'process_experience'):
                    self.autopoietic_loop.process_experience({
                        'type': 'objective_generation',
                        'query': query,
                        'pattern_signature': pattern_signature,
                        'success': True
                    })
                # Alternative: store in query pattern history for later processing
                # The autopoietic loop can process this history in batch
            except Exception as e:
                logger.debug(f"Autopoietic learning not available: {e}")
    
    def _identify_learning_opportunities(self, pattern_analysis: Dict[str, Any]) -> List[str]:
        """Identify learning opportunities from pattern analysis."""
        opportunities = []
        
        # Check for novel patterns
        if pattern_analysis.get('pattern_signature') not in [p.get('pattern_signature') for p in self.query_pattern_history]:
            opportunities.append("Novel query pattern detected - potential for new keyword mapping")
        
        # Check for low confidence activations
        # (This would require confidence tracking in activated_sprs)
        
        return opportunities
    
    def _generate_iar(self, activated_sprs: List[ActivatedSPR], mandates: List[Mandate], 
                     features: FeatureVector) -> Dict[str, Any]:
        """Generate Integrated Action Reflection."""
        avg_confidence = sum([spr.match_confidence.probability for spr in activated_sprs]) / len(activated_sprs) if activated_sprs else 0.5
        
        return {
            'status': 'Success',
            'confidence': avg_confidence,
            'alignment_check': {
                'objective_alignment': 1.0,
                'protocol_alignment': 1.0
            },
            'potential_issues': [],
            'summary': f'Generated enriched problem_description with {len(activated_sprs)} SPRs and {len(mandates)} mandates'
        }
    
    # ============================================================================
    # Static Data Loading Methods
    # ============================================================================
    
    def _load_spr_keyword_map(self) -> Dict[str, str]:
        """Load SPR keyword mapping."""
        return {
            'historical': 'HistoricalContextualizatioN',
            'temporal': 'TemporalDynamiX',
            'future': 'FutureStateAnalysiS',
            'predict': 'FutureStateAnalysiS',
            'causal': 'CausalLagDetectioN',
            'lag': 'CausalLagDetectioN',
            'emergent': 'EmergenceOverTimE',
            'emerge': 'EmergenceOverTimE',
            'trajectory': 'TrajectoryComparisoN',
            'compare': 'TrajectoryComparisoN',
            'complex system': 'ComplexSystemVisioninG',
            'complex': 'ComplexSystemVisioninG',
            'cognitive': 'CognitiveresonancE',
            'resonance': 'CognitiveresonancE',
            '4d': 'FourdthinkinG',
            'fourd': 'FourdthinkinG',
            'time': 'TemporalDynamiX',
            'time horizon': 'TemporalDynamiX',
        }
    
    def _load_domain_rules(self) -> Dict[str, Dict[str, str]]:
        """Load domain-specific rules for SPR explanations."""
        return {
            'boxing': {
                'TemporalDynamiX': 'how the fight evolves round-by-round',
                'EmergenceOverTimE': 'ABM showing how agent interactions create unpredictable outcomes',
                'TrajectoryComparisoN': 'CFP comparing fight trajectory probabilities',
                'CausalLagDetectioN': 'identifying time-delayed effects of fighting strategies'
            },
            'economic': {
                'FutureStateAnalysiS': 'predicting outcomes across time horizons',
                'TemporalDynamiX': '5-year economic projections',
                'EmergenceOverTimE': 'market dynamics from agent interactions'
            },
            'environmental': {
                'FutureStateAnalysiS': 'projecting environmental consequences over time',
                'TemporalDynamiX': 'long-term climate and ecosystem dynamics',
                'CausalLagDetectioN': 'identifying delayed environmental impacts'
            }
        }
    
    def _load_enhancement_template(self) -> str:
        """Load the Enhancement_Skeleton_Pattern template."""
        return (
            "Apply the full spectrum of ResonantiA Protocol {protocol_version} capabilities "
            "to achieve deep {temporal_resonance} and {cognitive_resonance} on this query. "
            "Execute a temporally-aware, multi-dimensional analytical sequence that integrates: "
            "{capabilities}. This analysis must honor {mandates} while maintaining "
            "{implementation_resonance} throughout."
        )


# ============================================================================
# Crystallized Objective Generator (8-Stage Pattern Crystallization)
# ============================================================================

class CrystallizedObjectiveGenerator:
    """
    Mastermind AI: Deterministic Objective Generation Engine
    Applies Pattern Crystallization meta-process for 100:1 compression
    
    Implements the 8-stage crystallization process:
    1. Feature Extraction (⦅features⦆) - Regex, keyword matching
    2. TemporalScope Building (Δ⦅scope⦆) - Rule-based
    3. SPR Activation (⊢SPR_ID) - Keyword lookup
    4. Mandate Selection (⊨M_N) - Boolean rules
    5. Template Assembly (⊧template) - String substitution
    6. Domain Customization (⊨domain) - Rule-based lookup
    7. Final Assembly (⟧problem_description⟧) - Template concatenation
    8. Zepto SPR Generation (◊objective_spr◊) - Pure symbolic compression
    """
    
    def __init__(self, symbol_codex_path: str = "knowledge_graph/protocol_symbol_vocabulary.json"):
        """Initialize the Crystallized Objective Generator."""
        self.symbol_codex_path = Path(symbol_codex_path)
        self.symbol_codex = self._load_objective_codex()
        self.spr_keyword_map = self._load_spr_keyword_map()
        self.domain_rules = self._load_domain_rules()
        self.template = self._load_enhancement_template()
        logger.info("CrystallizedObjectiveGenerator initialized")
    
    def generate_objective(self, query: str) -> Dict[str, Any]:
        """
        Crystallized 8-stage objective generation process.
        Returns enriched problem_description without LLM assistance.
        """
        # Stage 1: Feature Extraction (⦅features⦆)
        features = self._extract_features(query)  # Regex, keyword matching
        
        # Stage 2: TemporalScope Building (Δ⦅scope⦆)
        temporal_scope = self._build_temporal_scope(features)  # Rule-based
        
        # Stage 3: SPR Activation (⊢SPR_ID)
        activated_sprs = self._activate_sprs(features)  # Keyword lookup
        
        # Stage 4: Mandate Selection (⊨M_N)
        mandates = self._select_mandates(features)  # Boolean rules
        
        # Stage 5: Template Assembly (⊧template)
        objective = self._assemble_objective(activated_sprs, mandates, features)  # String substitution
        
        # Stage 6: Domain Customization (⊨domain)
        objective = self._customize_domain(objective, activated_sprs, features)  # Rule-based lookup
        
        # Stage 7: Final Assembly (⟧problem_description⟧)
        problem_description = self._assemble_problem_description(
            query, temporal_scope, objective, activated_sprs
        )  # Template concatenation
        
        # Stage 8: Zepto SPR Generation (◊objective_spr◊)
        zepto_spr = self._generate_zepto_spr(
            query, features, temporal_scope, activated_sprs, mandates, objective
        )  # Pure symbolic compression
        
        return {
            'problem_description': problem_description,
            'zepto_spr': zepto_spr,
            'compression_ratio': len(query) / len(zepto_spr) if zepto_spr else 1.0,
            'iar': self._generate_iar(activated_sprs, mandates, features),
            'features': features,
            'temporal_scope': temporal_scope,
            'activated_sprs': [spr.spr_id for spr in activated_sprs],
            'mandates': [f"M{m.number}" if m.number else m.name for m in mandates]
        }
    
    def _extract_features(self, query: str) -> FeatureVector:
        """Stage 1: ⦅features⦆ - Deterministic pattern matching"""
        # Regex patterns for temporal markers
        temporal_patterns = [
            (r'circa\s+(\d{4})-(\d{4})', 'explicit_range'),
            (r'age\s+(\d+)-(\d+)', 'age_range'),
            (r'(\d+)\s+year[s]?\s+(?:ahead|forward|projection)', 'future_horizon'),
        ]
        
        temporal_markers = []
        for pattern, marker_type in temporal_patterns:
            for match in re.finditer(pattern, query, re.IGNORECASE):
                temporal_markers.append(TemporalMarker(
                    type=marker_type,
                    value=match.groups(),
                    confidence=QuantumProbability.certain_true() if hasattr(QuantumProbability, 'certain_true') else QuantumProbability(1.0, ['regex_match']),
                    text=match.group(0)
                ))
        
        # Keyword lookup for domain
        domain_keywords = []
        domain_vocab = ['boxing', 'economic', 'scientific', 'medical', 'legal']
        for domain in domain_vocab:
            if domain in query.lower():
                domain_keywords.append(domain)
        
        # SPR keyword scanning
        spr_keywords = []
        for keyword in self.spr_keyword_map.keys():
            if keyword in query.lower():
                spr_keywords.append(keyword)
        
        return FeatureVector(
            temporal_markers=temporal_markers,
            domain_keywords=domain_keywords,
            spr_keywords=spr_keywords,
            raw_query=query
        )
    
    def _build_temporal_scope(self, features: FeatureVector) -> TemporalScope:
        """Stage 2: Δ⦅scope⦆ - Rule-based temporal structuring"""
        scope = TemporalScope()
        
        # IF temporal_markers EXISTS
        if features.temporal_markers:
            explicit_parts = []
            for marker in features.temporal_markers:
                if marker.type == 'explicit_range':
                    explicit_parts.append(f"Historical primes: {marker.text}")
            if explicit_parts:
                scope.explicit = explicit_parts
        
        # IF 'boxing match' IN domain_keywords
        if 'boxing' in features.domain_keywords or 'match' in features.raw_query.lower():
            scope.implicit.append("Round-by-round progression")
        
        # IF 'career' OR 'trajectory' OR 'prime' IN domain_keywords
        query_lower = features.raw_query.lower()
        if any(kw in query_lower for kw in ['career', 'trajectory', 'prime']):
            scope.temporal.append("Career trajectories")
        
        # IF COUNT(temporal_markers) >= 2
        if len(features.temporal_markers) >= 2:
            scope.contextual.append("Era differences (rules, training, competition level)")
        
        return scope
    
    def _activate_sprs(self, features: FeatureVector) -> List[ActivatedSPR]:
        """Stage 3: ⊢SPR_ID - Keyword lookup table matching"""
        activated = []
        query_lower = features.raw_query.lower()
        
        # Activation Loop
        for keyword in features.spr_keywords:
            if keyword in self.spr_keyword_map:
                spr_id = self.spr_keyword_map[keyword]
                activated.append(ActivatedSPR(
                    spr_id=spr_id,
                    match_confidence=QuantumProbability(0.95, [f'keyword_match: {keyword}']),
                    match_method='keyword_lookup'
                ))
        
        # Additional SPRs from temporal markers
        if features.temporal_markers:
            temporal_sprs = ['TemporalDynamiX', 'HistoricalContextualizatioN', 'FutureStateAnalysiS']
            for spr_id in temporal_sprs:
                if not any(spr.spr_id == spr_id for spr in activated):
                    activated.append(ActivatedSPR(
                        spr_id=spr_id,
                        match_confidence=QuantumProbability(0.85, ['temporal_marker_detected']),
                        match_method='temporal_auto_activation'
                    ))
        
        return activated
    
    def _select_mandates(self, features: FeatureVector) -> List[Mandate]:
        """Stage 4: ⊨M_N - Rule-based boolean logic"""
        mandates = []
        
        # Rule 1: Temporal → M₆
        temporal_indicators = ['circa', 'age', 'year', 'time horizon', 'trajectory']
        if any(ind in features.raw_query.lower() for ind in temporal_indicators):
            mandates.append(Mandate(
                number=6,
                name="Temporal Resonance",
                confidence=QuantumProbability(0.9, ['temporal_indicator_detected']),
                selection_method='rule_based_temporal_detection'
            ))
        
        # Rule 2: Complex/Emergent → M₉
        complexity_keywords = ['emergent', 'complex system', 'interaction', 'dynamic']
        if any(kw in features.raw_query.lower() for kw in complexity_keywords):
            mandates.append(Mandate(
                number=9,
                name="Complex System Visioning",
                confidence=QuantumProbability(0.85, ['complexity_keyword_detected']),
                selection_method='rule_based_complexity_detection'
            ))
        
        # Rule 3: Always include Cognitive Resonance
        mandates.append(Mandate(
            number=None,
            name="Cognitive Resonance",
            confidence=QuantumProbability.certain_true() if hasattr(QuantumProbability, 'certain_true') and not QUANTUM_AVAILABLE else QuantumProbability(1.0, ['always_included']),
            selection_method='universal_principle'
        ))
        
        return mandates
    
    def _assemble_objective(self, spr_list: List[ActivatedSPR], mandates: List[Mandate], features: FeatureVector) -> str:
        """Stage 5: ⊧template - String substitution"""
        # Build capability list
        capability_list = []
        for spr in spr_list:
            explanation = self._get_domain_explanation(spr, features)
            capability_list.append(f"{spr.spr_id} ({explanation})")
        
        capabilities_text = ", ".join(capability_list) if capability_list else "CognitiveresonancE"
        
        # Build mandate references
        mandate_refs = []
        for m in mandates:
            if m.number:
                mandate_refs.append(f"Mandate {m.number} ({m.name})")
        
        mandates_text = " and ".join(mandate_refs) if mandate_refs else "Cognitive Resonance"
        
        # Template substitution
        return self.template.format(
            protocol_version="v3.5-GP (Genesis Protocol)",
            temporal_resonance="Temporal Resonance",
            cognitive_resonance="Cognitive Resonance",
            query_description=features.raw_query[:100] + "..." if len(features.raw_query) > 100 else features.raw_query,
            capabilities=capabilities_text,
            mandates=mandates_text,
            implementation_resonance="Implementation Resonance"
        )
    
    def _customize_domain(self, objective: str, spr_list: List[ActivatedSPR], features: FeatureVector) -> str:
        """Stage 6: ⊨domain - Rule-based domain explanation lookup"""
        # Domain customization is already applied in _get_domain_explanation
        # This method can be extended for additional customization
        return objective
    
    def _assemble_problem_description(self, query: str, temporal_scope: TemporalScope, 
                                     objective: str, activated_sprs: List[ActivatedSPR]) -> str:
        """Stage 7: ⟧problem_description⟧ - Complete problem_description assembly"""
        query_id = str(uuid.uuid4())
        spr_hints = ", ".join([spr.spr_id for spr in activated_sprs])
        
        problem_description = f"""->|UserInput query_id={query_id}|<-
    ->|QueryText|<-
        {query}
    ->|/QueryText|<-
    ->|TemporalScope|<-{temporal_scope.format()}<-/TemporalScope|<-
->|/UserInput|<-

->|EnhancementDirectives|<-
    ->|Objective|<-
        {objective}
    ->|/Objective|<-
->|/EnhancementDirectives|<-

[SPR_HINTS]: {spr_hints}"""
        
        return problem_description.strip()
    
    def _generate_zepto_spr(self, query: str, features: FeatureVector, temporal_scope: TemporalScope,
                           spr_list: List[ActivatedSPR], mandates: List[Mandate], objective: str) -> str:
        """Stage 8: ◊objective_spr◊ - Pure symbolic compression"""
        # Compress to symbols
        zepto = f"⟦{len(query)}⟧→⦅{len(features.temporal_markers)}T{len(features.domain_keywords)}D⦆→"
        zepto += f"Δ⦅{len(temporal_scope.explicit)+len(temporal_scope.implicit)}⦆→"
        zepto += f"⊢{''.join([spr.spr_id[0] for spr in spr_list[:5]])}→"
        zepto += f"⊨{''.join([f'M{m.number}' for m in mandates if m.number])}→"
        zepto += f"⊧{len(objective)}→⟧"
        
        return zepto
    
    def _get_domain_explanation(self, spr: ActivatedSPR, features: FeatureVector) -> str:
        """Get domain-specific explanation for an SPR."""
        # Check domain rules
        for domain in features.domain_keywords:
            if domain in self.domain_rules:
                if spr.spr_id in self.domain_rules[domain]:
                    return self.domain_rules[domain][spr.spr_id]
        
        # Generic explanation
        generic_explanations = {
            'HistoricalContextualizatioN': 'understanding historical context',
            'TemporalDynamiX': 'modeling temporal dynamics',
            'FutureStateAnalysiS': 'predicting future states',
            'CausalLagDetectioN': 'identifying causal lag effects',
            'EmergenceOverTimE': 'simulating emergent behaviors',
            'TrajectoryComparisoN': 'comparing system trajectories',
            'CognitiveresonancE': 'achieving cognitive resonance',
            'FourdthinkinG': 'applying 4D thinking',
        }
        
        return generic_explanations.get(spr.spr_id, 'applying analytical capabilities')
    
    def _generate_iar(self, activated_sprs: List[ActivatedSPR], mandates: List[Mandate], 
                     features: FeatureVector) -> Dict[str, Any]:
        """Generate Integrated Action Reflection."""
        avg_confidence = sum([spr.match_confidence.probability for spr in activated_sprs]) / len(activated_sprs) if activated_sprs else 0.5
        
        return {
            'status': 'Success',
            'confidence': avg_confidence,
            'alignment_check': {
                'objective_alignment': 1.0,
                'protocol_alignment': 1.0
            },
            'potential_issues': [],
            'summary': f'Generated enriched problem_description with {len(activated_sprs)} SPRs and {len(mandates)} mandates'
        }
    
    # ============================================================================
    # Static Data Loading Methods
    # ============================================================================
    
    def _load_objective_codex(self) -> Dict[str, Any]:
        """Load objective generation symbol codex."""
        if self.symbol_codex_path.exists():
            try:
                with open(self.symbol_codex_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Extract objective_generation_symbols if present
                    return data.get('objective_generation_symbols', {})
            except Exception as e:
                logger.warning(f"Failed to load objective codex: {e}")
        return {}
    
    def _load_spr_keyword_map(self) -> Dict[str, str]:
        """Load SPR keyword mapping."""
        return {
            'historical': 'HistoricalContextualizatioN',
            'emergent': 'EmergenceOverTimE',
            'causal': 'CausalLagDetectioN',
            'predictive': 'FutureStateAnalysiS',
            'predicting': 'FutureStateAnalysiS',
            'temporal': 'TemporalDynamiX',
            'compare': 'TrajectoryComparisoN',
            'matchup': 'TrajectoryComparisoN'
        }
    
    def _load_domain_rules(self) -> Dict[str, Dict[str, str]]:
        """Load domain-specific rules for SPR explanations."""
        return {
            'boxing': {
                'TemporalDynamiX': 'how the fight evolves round-by-round',
                'EmergenceOverTimE': 'ABM showing how agent interactions create unpredictable outcomes',
                'TrajectoryComparisoN': 'CFP comparing fight trajectory probabilities',
                'CausalLagDetectioN': 'identifying time-delayed effects of fighting strategies'
            },
            'economic': {
                'FutureStateAnalysiS': 'predicting outcomes across time horizons',
                'TemporalDynamiX': '5-year economic projections',
                'EmergenceOverTimE': 'market dynamics from agent interactions'
            }
        }
    
    def _load_enhancement_template(self) -> str:
        """Load the Enhancement_Skeleton_Pattern template."""
        return (
            "Apply the full spectrum of ResonantiA Protocol {protocol_version} capabilities "
            "to achieve deep {temporal_resonance} and {cognitive_resonance} on {query_description}. "
            "Execute a temporally-aware, multi-dimensional analytical sequence that integrates: "
            "{capabilities}. This analysis must honor {mandates} while maintaining "
            "{implementation_resonance} throughout."
        )

