"""
Universal Dynamic Causal Parameter Extraction Module

This module provides a query-relative, domain-agnostic abstraction for extracting
treatment and outcome variables from natural language queries. It implements the
DynamicCausalParameterExtractioN pattern, which crystallizes the insight that
causal inference parameters must be dynamically derived from query context rather
than hardcoded or heuristically determined.

This abstraction enables:
- Query-relative treatment/outcome identification
- Domain-agnostic causal relationship extraction
- Multi-mechanism extraction (LLM-based, pattern-based, data-driven)
- Fallback hierarchies for robustness
- Integration with RISE analysis and other cognitive tools

Author: ArchE (ResonantiA Protocol v3.1-CA)
Pattern: DynamicCausalParameterExtractioN
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List, Tuple
# REMOVED: LLM dependency - following Universal Abstraction principles
# Pattern matching and deterministic rules replace semantic understanding

logger = logging.getLogger(__name__)


class DynamicCausalParameterExtractor:
    """
    Universal abstraction for dynamically extracting treatment and outcome variables
    from natural language queries, RISE analysis, or data structures.
    
    This class implements the DynamicCausalParameterExtractioN pattern, providing
    multiple extraction strategies with fallback hierarchies to ensure robust
    parameter identification across diverse query types and domains.
    """
    
    # Meta-conceptual definitions for Treatment and Outcome roles
    # Treatment (CAUSE role): The independent variable, intervention, agent of change, driver
    # Outcome (EFFECT role): The dependent variable, result, target of analysis, consequence
    
    # Semantic role patterns for CAUSE/TREATMENT identification
    # These identify entities acting as agents, drivers, or sources of change
    CAUSE_ROLE_PATTERNS = [
        # Direct agency: "X does Y", "X changes Y"
        r'(\w+(?:\s+\w+){0,5})\s+(?:causes?|drives?|triggers?|initiates?|produces?|generates?|creates?|induces?|brings?\s+about)',
        # Intervention patterns: "implementing X", "adopting X", "transitioning from X"
        r'(?:implementing|adopting|introducing|establishing|transitioning\s+(?:from|away\s+from)|shifting\s+(?:from|to))\s+([^,\.]+)',
        # Subject of change verbs: "X transforms", "X alters", "X modifies"
        r'(\w+(?:\s+\w+){0,5})\s+(?:transforms?|alters?|modifies?|changes?|shifts?|evolves?)',
        # Prepositional patterns: "through X", "via X", "by means of X"
        r'(?:through|via|by\s+means\s+of|using|with|via)\s+([^,\.]+)',
    ]
    
    # Semantic role patterns for EFFECT/OUTCOME identification
    # These identify entities that are targets, results, or consequences
    EFFECT_ROLE_PATTERNS = [
        # Direct effect: "results in Y", "leads to Y", "produces Y"
        r'(?:results?\s+in|leads?\s+to|produces?|generates?|creates?|yields?|brings?\s+about)\s+([^,\.]+)',
        # Target patterns: "toward Y", "to Y", "for Y"
        r'(?:toward|to|for|into|achieving|attaining|reaching)\s+([^,\.]+)',
        # Object of change: "Y changes", "Y is transformed", "Y evolves"
        r'([^,\.]+)\s+(?:changes?|is\s+transformed|evolves?|emerges?|develops?|arises?)',
        # Measured/observed outcomes: "impact on Y", "effect on Y", "influence on Y"
        r'(?:impact|effect|influence|consequence|outcome|result)\s+(?:on|of|for)\s+([^,\.]+)',
    ]
    
    # Causal relationship indicator patterns (connectors between cause and effect)
    CAUSAL_INDICATORS = [
        r'impact\s+on',
        r'effect\s+of',
        r'influence\s+on',
        r'causes?\s+',
        r'leads?\s+to',
        r'results?\s+in',
        r'contributes?\s+to',
        r'correlates?\s+with',
        r'affects?',
        r'drives?',
        r'triggers?',
        r'produces?',
        r'generates?',
        r'creates?',
        r'transforms?\s+(?:into|to)',
        r'shifts?\s+(?:from|to)',
        r'transitions?\s+(?:from|to|away\s+from)',
    ]
    
    # Temporal causal indicators
    TEMPORAL_CAUSAL_INDICATORS = [
        r'after\s+',
        r'before\s+',
        r'following\s+',
        r'preceding\s+',
        r'lagged\s+effect',
        r'temporal\s+relationship',
    ]
    
    # Linguistic structures that indicate semantic roles
    # Subject-Verb-Object patterns where Subject = CAUSE, Object = EFFECT
    SVO_PATTERNS = [
        r'(\w+(?:\s+\w+){0,8})\s+(?:causes?|drives?|triggers?|produces?|generates?)\s+(\w+(?:\s+\w+){0,8})',
        r'(\w+(?:\s+\w+){0,8})\s+(?:affects?|influences?|impacts?)\s+(\w+(?:\s+\w+){0,8})',
    ]
    
    def __init__(self, llm_provider=None):
        """
        Initialize the extractor.
        
        Args:
            llm_provider: Optional LLM provider for advanced extraction.
                         If None, will use default from synthesis_tool.
        """
        self.llm_provider = llm_provider
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        self.causal_pattern = re.compile(
            '|'.join(self.CAUSAL_INDICATORS),
            re.IGNORECASE
        )
        self.temporal_pattern = re.compile(
            '|'.join(self.TEMPORAL_CAUSAL_INDICATORS),
            re.IGNORECASE
        )
        # Compile meta-conceptual role patterns
        self.cause_role_patterns = [re.compile(p, re.IGNORECASE) for p in self.CAUSE_ROLE_PATTERNS]
        self.effect_role_patterns = [re.compile(p, re.IGNORECASE) for p in self.EFFECT_ROLE_PATTERNS]
        self.svo_patterns = [re.compile(p, re.IGNORECASE) for p in self.SVO_PATTERNS]
    
    def extract_from_query(
        self,
        query: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        strategy: str = 'auto'
    ) -> Dict[str, Any]:
        """
        Extract treatment and outcome parameters from a natural language query.
        
        This is the primary entry point for query-relative causal parameter extraction.
        It employs a multi-strategy approach with intelligent fallback.
        
        Args:
            query: The natural language query containing causal relationships.
            domain: Optional domain context (e.g., 'economics', 'sociology', 'technology').
            context: Optional additional context (e.g., RISE analysis, previous extractions).
            strategy: Extraction strategy ('auto', 'llm', 'pattern', 'hybrid').
                    'auto' uses intelligent strategy selection.
        
        Returns:
            Dictionary with:
            - treatment: The cause/factor being analyzed
            - outcome: The effect/result being measured
            - confounders: List of potential confounders (if identified)
            - causal_mechanisms: List of identified causal mechanisms
            - confidence: Confidence score (0.0-1.0)
            - extraction_method: Method used ('llm', 'pattern', 'hybrid', 'fallback')
            - metadata: Additional extraction metadata
        """
        if not query or not isinstance(query, str):
            logger.warning("Empty or invalid query provided to extract_from_query")
            return self._fallback_result("Empty query")
        
        # PRIORITY 1: Transformation patterns (highest confidence, explicit "from X to Y")
        # Check transformation patterns FIRST before other strategies
        transform_result = self._extract_transformation_pattern(query, domain)
        if transform_result.get('treatment') and transform_result.get('outcome') and \
           transform_result.get('treatment') != 'unknown_treatment' and \
           transform_result.get('outcome') != 'unknown_outcome':
            logger.debug(f"Transformation pattern matched: '{transform_result['treatment']}' -> '{transform_result['outcome']}'")
            return transform_result
        
        # Strategy selection (Universal Abstraction: all strategies are pattern-based)
        if strategy == 'auto':
            strategy = self._select_strategy(query, domain, context)
        
        # Execute extraction based on strategy (all use pattern matching)
        if strategy == 'pattern':
            result = self._extract_via_enhanced_patterns(query, domain, context)
        elif strategy == 'hybrid':
            # Hybrid now means multiple pattern strategies combined
            result = self._extract_hybrid_patterns(query, domain, context)
        else:
            # Default to enhanced pattern matching (Universal Abstraction)
            result = self._extract_via_enhanced_patterns(query, domain, context)
        
        # Enhance with context if available
        if context:
            result = self._enhance_with_context(result, context)
        
        return result
    
    def extract_from_rise_analysis(
        self,
        rise_analysis: Dict[str, Any],
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract causal parameters from a RISE analysis structure.
        
        Args:
            rise_analysis: RISE analysis dictionary containing structured insights.
            query: Optional original query for context.
        
        Returns:
            Dictionary with treatment, outcome, and related parameters.
        """
        try:
            # Extract from RISE structure
            causal_relationships = rise_analysis.get('causal_relationships', [])
            strategic_requirements = rise_analysis.get('strategic_requirements', [])
            key_findings = rise_analysis.get('key_findings', [])
            
            # Try to extract treatment/outcome from causal relationships
            if causal_relationships:
                # Look for structured causal pairs
                for rel in causal_relationships:
                    if isinstance(rel, dict):
                        if 'treatment' in rel and 'outcome' in rel:
                            return {
                                'treatment': rel['treatment'],
                                'outcome': rel['outcome'],
                                'confounders': rel.get('confounders', []),
                                'causal_mechanisms': rel.get('mechanisms', []),
                                'confidence': 0.8,
                                'extraction_method': 'rise_structured',
                                'metadata': {'source': 'rise_analysis'}
                            }
                    elif isinstance(rel, str) and len(causal_relationships) >= 2:
                        # Use first as treatment, second as outcome
                        return {
                            'treatment': causal_relationships[0],
                            'outcome': causal_relationships[1] if len(causal_relationships) > 1 else strategic_requirements[0] if strategic_requirements else 'unknown_outcome',
                            'confounders': [],
                            'causal_mechanisms': key_findings[:3] if key_findings else [],
                            'confidence': 0.6,
                            'extraction_method': 'rise_heuristic',
                            'metadata': {'source': 'rise_analysis'}
                        }
            
            # Fallback: use strategic requirements
            if strategic_requirements:
                return {
                    'treatment': strategic_requirements[0] if strategic_requirements else 'unknown_treatment',
                    'outcome': strategic_requirements[-1] if len(strategic_requirements) > 1 else 'unknown_outcome',
                    'confounders': [],
                    'causal_mechanisms': key_findings[:3] if key_findings else [],
                    'confidence': 0.5,
                    'extraction_method': 'rise_fallback',
                    'metadata': {'source': 'rise_analysis'}
                }
            
            # If RISE analysis doesn't provide clear structure, fall back to query extraction
            if query:
                logger.info("RISE analysis lacks clear causal structure, falling back to query extraction")
                return self.extract_from_query(query)
            
            return self._fallback_result("RISE analysis lacks causal structure")
            
        except Exception as e:
            logger.error(f"Error extracting from RISE analysis: {e}", exc_info=True)
            if query:
                return self.extract_from_query(query)
            return self._fallback_result(f"RISE extraction error: {e}")
    
    def extract_from_data_structure(
        self,
        data: Any,
        query: Optional[str] = None,
        prefer_named: bool = True
    ) -> Dict[str, Any]:
        """
        Extract causal parameters from data structure (e.g., DataFrame columns).
        
        This method provides a data-driven approach when numerical keys or
        column names suggest causal relationships.
        
        Args:
            data: Data structure (dict, list, DataFrame, etc.)
            query: Optional query for context
            prefer_named: If True, prefer named columns over numeric indices
        
        Returns:
            Dictionary with treatment, outcome, and related parameters.
        """
        try:
            # Handle different data structures
            if isinstance(data, dict):
                keys = list(data.keys())
            elif hasattr(data, 'columns'):  # DataFrame-like
                keys = list(data.columns)
            elif isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    keys = list(data[0].keys())
                else:
                    keys = [f"Var{i}" for i in range(len(data[0]))]
            else:
                return self._fallback_result("Unsupported data structure")
            
            # Filter out non-relevant keys
            numeric_keys = [k for k in keys if k != 'iar_confidence' and not str(k).startswith('_')]
            
            if len(numeric_keys) < 2:
                # Not enough variables for causal analysis
                if query:
                    return self.extract_from_query(query)
                return self._fallback_result("Insufficient variables in data")
            
            # Heuristic: first two keys as treatment/outcome
            # This is a fallback; should be enhanced with query context
            treatment = numeric_keys[0]
            outcome = numeric_keys[1]
            confounders = numeric_keys[2:5] if len(numeric_keys) > 2 else []
            
            # If query available, try to match names to query concepts
            if query:
                query_result = self.extract_from_query(query)
                if query_result.get('confidence', 0) > 0.5:
                    # Try to map query concepts to data keys
                    treatment_name = query_result.get('treatment', '')
                    outcome_name = query_result.get('outcome', '')
                    
                    # Find closest matching keys
                    treatment_match = self._find_closest_key(treatment_name, numeric_keys)
                    outcome_match = self._find_closest_key(outcome_name, numeric_keys)
                    
                    if treatment_match and outcome_match:
                        treatment = treatment_match
                        outcome = outcome_match
                        confounders = [k for k in numeric_keys if k not in [treatment, outcome]]
            
            return {
                'treatment': treatment,
                'outcome': outcome,
                'confounders': confounders,
                'causal_mechanisms': [],
                'confidence': 0.6 if query else 0.4,
                'extraction_method': 'data_driven',
                'metadata': {
                    'data_keys': numeric_keys,
                    'query_enhanced': query is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting from data structure: {e}", exc_info=True)
            if query:
                return self.extract_from_query(query)
            return self._fallback_result(f"Data extraction error: {e}")
    
    def _select_strategy(
        self,
        query: str,
        domain: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Select optimal extraction strategy based on query characteristics.
        
        UNIVERSAL ABSTRACTION: No LLM dependency - all strategies use pattern matching.
        Strategy selection is deterministic rule-based, not LLM inference.
        """
        # Check for explicit causal indicators (pattern matching)
        has_causal_indicators = bool(self.causal_pattern.search(query))
        has_temporal_indicators = bool(self.temporal_pattern.search(query))
        
        # Check query complexity (structural analysis, not semantic)
        query_length = len(query.split())
        has_transformation_patterns = bool(re.search(
            r'(?:transitioning|shifting|moving|changing|transforming)\s+(?:from|away\s+from)',
            query, re.IGNORECASE
        ))
        
        # Deterministic strategy selection (rule-based, not LLM)
        if has_transformation_patterns:
            return 'pattern'  # Transformation patterns are most reliable
        elif has_causal_indicators:
            return 'pattern'  # Causal indicators enable pattern extraction
        elif query_length > 30:
            return 'pattern'  # Complex queries still use enhanced pattern matching
        else:
            return 'pattern'  # All queries use pattern matching (Universal Abstraction)
    
    def _extract_via_enhanced_patterns(
        self,
        query: str,
        domain: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enhanced pattern-based extraction using Universal Abstraction principles.
        
        REMOVED LLM DEPENDENCY: This method uses deterministic pattern matching,
        rule-based entity extraction, and structural analysis - no semantic understanding required.
        
        Following Objective Generation Engine principles:
        - Pattern matching replaces semantic understanding
        - Deterministic rules replace LLM inference
        - Quantum probability states replace LLM confidence
        """
        # Start with standard pattern extraction
        base_result = self._extract_via_patterns(query, domain)
        
        # If base extraction succeeded, enhance it
        if base_result.get('confidence', 0) > 0.5:
            # Enhance with additional deterministic analysis
            enhanced = self._enhance_pattern_result(base_result, query, domain, context)
            return enhanced
        
        # If base extraction failed, try advanced pattern strategies
        return self._extract_via_advanced_patterns(query, domain, context)
    
    def _extract_via_patterns(
        self,
        query: str,
        domain: Optional[str]
    ) -> Dict[str, Any]:
        """Extract causal parameters using meta-conceptual pattern matching."""
        try:
            treatment = None
            outcome = None
            cause_role_type = None
            effect_role_type = None
            
            # Strategy 1: Subject-Verb-Object patterns (SVO = CAUSE -> EFFECT)
            for svo_pattern in self.svo_patterns:
                match = svo_pattern.search(query)
                if match:
                    potential_cause = match.group(1).strip()
                    potential_effect = match.group(2).strip()
                    if potential_cause and potential_effect:
                        treatment = potential_cause
                        outcome = potential_effect
                        cause_role_type = "AGENT"
                        effect_role_type = "PATIENT"
                        break
            
            # Strategy 2: CAUSE role patterns (identify entities acting as agents)
            if not treatment:
                for cause_pattern in self.cause_role_patterns:
                    match = cause_pattern.search(query)
                    if match:
                        # Extract the captured group (the entity serving CAUSE role)
                        if match.lastindex and match.lastindex >= 1:
                            treatment = match.group(1).strip()
                            cause_role_type = "DRIVER"
                        elif match.group(0):
                            # Fallback: use full match
                            treatment = match.group(0).strip()
                            cause_role_type = "INTERVENTION"
                        break
            
            # Strategy 3: EFFECT role patterns (identify entities being affected)
            if not outcome:
                for effect_pattern in self.effect_role_patterns:
                    match = effect_pattern.search(query)
                    if match:
                        # Extract the captured group (the entity serving EFFECT role)
                        if match.lastindex and match.lastindex >= 1:
                            outcome = match.group(1).strip()
                            effect_role_type = "RESULT"
                        elif match.group(0):
                            # Fallback: use full match
                            outcome = match.group(0).strip()
                            effect_role_type = "TARGET"
                        break
            
            # Strategy 4: Transformation patterns (FROM X TO Y) - Highest priority
            # Pattern: "transitioning from X to Y", "shifting from X toward Y", "away from X toward Y"
            transform_pattern = re.compile(
                r'(?:transitioning|shifting|moving|changing|transforming)\s+(?:away\s+from|from)\s+([^,\.]+?)\s+(?:toward|to|into)\s+([^,\.]+)',
                re.IGNORECASE
            )
            match = transform_pattern.search(query)
            if match:
                treatment = self._clean_extracted_entity(match.group(1).strip())
                outcome = self._clean_extracted_entity(match.group(2).strip())
                cause_role_type = "SOURCE"
                effect_role_type = "TARGET"
                # Transformation patterns override other strategies (highest confidence)
                if treatment and outcome:
                    return {
                        'treatment': treatment,
                        'outcome': outcome,
                        'confounders': [],
                        'causal_mechanisms': [],
                        'confidence': 0.9,  # High confidence: explicit transformation
                        'extraction_method': 'transformation_pattern',
                        'metadata': {
                            'domain': domain,
                            'semantic_roles': {
                                'cause_role_type': cause_role_type,
                                'effect_role_type': effect_role_type
                            },
                            'pattern_type': 'transformation'
                        }
                    }
            
            # Strategy 5: Fallback to causal indicator patterns
            if not treatment or not outcome:
                matches = list(self.causal_pattern.finditer(query))
                if matches:
                    for match in matches:
                        start = match.start()
                        end = match.end()
                        before_text = query[:start].strip()
                        after_text = query[end:].strip()
                        
                        if not treatment and before_text:
                            words = before_text.split()
                            if len(words) > 0:
                                treatment = ' '.join(words[-3:]) if len(words) >= 3 else before_text
                                cause_role_type = "DRIVER"
                        
                        if not outcome and after_text:
                            words = after_text.split()
                            if len(words) > 0:
                                outcome = ' '.join(words[:3]) if len(words) >= 3 else after_text
                                effect_role_type = "RESULT"
                        
                        if treatment and outcome:
                            break
            
            if treatment and outcome:
                # Clean up extracted entities
                treatment = self._clean_extracted_entity(treatment)
                outcome = self._clean_extracted_entity(outcome)
                
                return {
                    'treatment': treatment,
                    'outcome': outcome,
                    'confounders': [],
                    'causal_mechanisms': [],
                    'confidence': 0.7 if cause_role_type and effect_role_type else 0.6,
                    'extraction_method': 'meta_pattern',
                    'metadata': {
                        'domain': domain,
                        'semantic_roles': {
                            'cause_role_type': cause_role_type or 'UNKNOWN',
                            'effect_role_type': effect_role_type or 'UNKNOWN'
                        }
                    }
                }
            
            return self._fallback_result("Meta-pattern extraction incomplete")
            
        except Exception as e:
            logger.error(f"Meta-pattern extraction error: {e}", exc_info=True)
            return self._fallback_result(f"Meta-pattern extraction error: {e}")
    
    def _clean_extracted_entity(self, entity: str) -> str:
        """Clean and normalize extracted entity text."""
        if not entity:
            return entity
        
        # Remove common stop words and connectors
        stop_connectors = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with']
        
        # Remove leading/trailing stop words
        words = entity.split()
        if words and words[0].lower() in stop_connectors:
            words = words[1:]
        if words and words[-1].lower() in stop_connectors:
            words = words[:-1]
        
        cleaned = ' '.join(words).strip()
        
        # Remove trailing punctuation
        cleaned = cleaned.rstrip('.,;:')
        
        return cleaned
    
    def _extract_hybrid_patterns(
        self,
        query: str,
        domain: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract using multiple pattern strategies combined (Universal Abstraction).
        
        REMOVED LLM DEPENDENCY: Hybrid now means combining multiple pattern-based
        strategies, not LLM + patterns. All strategies are deterministic pattern matching.
        """
        # Strategy 1: Enhanced pattern matching
        pattern_result = self._extract_via_patterns(query, domain)
        
        # Strategy 2: Advanced pattern strategies
        advanced_result = self._extract_via_advanced_patterns(query, domain, context)
        
        # Strategy 3: Transformation pattern priority
        transform_result = self._extract_transformation_pattern(query, domain)
        
        # Merge results using deterministic rules (not LLM inference)
        results = [
            (transform_result, 0.9),  # Highest priority: transformation patterns
            (advanced_result, 0.7),   # Medium priority: advanced patterns
            (pattern_result, 0.6),    # Base priority: standard patterns
        ]
        
        # Select best result based on confidence and completeness
        best_result = None
        best_score = 0.0
        
        for result, priority in results:
            if result.get('treatment') and result.get('outcome'):
                confidence = result.get('confidence', 0) * priority
                if confidence > best_score:
                    best_score = confidence
                    best_result = result
        
        if best_result:
            best_result['extraction_method'] = 'hybrid_patterns'
            best_result['confidence'] = min(0.95, best_score)
            best_result['metadata']['hybrid_components'] = len([r for r, _ in results if r.get('treatment')])
            return best_result
        
        # Fallback to best available
        return pattern_result if pattern_result.get('treatment') else advanced_result
    
    def _extract_transformation_pattern(
        self,
        query: str,
        domain: Optional[str]
    ) -> Dict[str, Any]:
        """Extract from transformation patterns (highest confidence pattern type)."""
        # Pattern: "transitioning from X to Y", "shifting from X toward Y"
        transform_pattern = re.compile(
            r'(?:transitioning|shifting|moving|changing|transforming|evolving)\s+(?:from|away\s+from)\s+([^,\.]+?)\s+(?:to|toward|into)\s+([^,\.]+)',
            re.IGNORECASE
        )
        match = transform_pattern.search(query)
        if match:
            treatment = self._clean_extracted_entity(match.group(1).strip())
            outcome = self._clean_extracted_entity(match.group(2).strip())
            return {
                'treatment': treatment,
                'outcome': outcome,
                'confounders': [],
                'causal_mechanisms': [],
                'confidence': 0.9,  # High confidence: explicit transformation
                'extraction_method': 'transformation_pattern',
                'metadata': {
                    'domain': domain,
                    'semantic_roles': {
                        'cause_role_type': 'SOURCE',
                        'effect_role_type': 'TARGET'
                    },
                    'pattern_type': 'transformation'
                }
            }
        return self._fallback_result("No transformation pattern found")
    
    def _extract_via_advanced_patterns(
        self,
        query: str,
        domain: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Advanced pattern strategies using Universal Abstraction principles.
        
        Uses deterministic rule-based entity extraction, no LLM required.
        """
        treatment = None
        outcome = None
        cause_role_type = None
        effect_role_type = None
        
        # Advanced Strategy 1: Noun phrase extraction with dependency patterns
        # Pattern: "effect of X on Y" structure
        effect_of_pattern = re.compile(
            r'effect\s+of\s+([^,\.]+?)\s+on\s+([^,\.]+)',
            re.IGNORECASE
        )
        match = effect_of_pattern.search(query)
        if match:
            treatment = self._clean_extracted_entity(match.group(1).strip())
            outcome = self._clean_extracted_entity(match.group(2).strip())
            cause_role_type = "AGENT"
            effect_role_type = "PATIENT"
        
        # Advanced Strategy 2: "X's impact on Y"
        if not treatment or not outcome:
            impact_pattern = re.compile(
                r"([^,\.]+?)(?:'s)?\s+impact\s+on\s+([^,\.]+)",
                re.IGNORECASE
            )
            match = impact_pattern.search(query)
            if match:
                treatment = self._clean_extracted_entity(match.group(1).strip())
                outcome = self._clean_extracted_entity(match.group(2).strip())
                cause_role_type = "DRIVER"
                effect_role_type = "TARGET"
        
        # Advanced Strategy 3: "How X affects Y"
        if not treatment or not outcome:
            how_affects_pattern = re.compile(
                r'how\s+([^,\.]+?)\s+affects?\s+([^,\.]+)',
                re.IGNORECASE
            )
            match = how_affects_pattern.search(query)
            if match:
                treatment = self._clean_extracted_entity(match.group(1).strip())
                outcome = self._clean_extracted_entity(match.group(2).strip())
                cause_role_type = "CAUSER"
                effect_role_type = "RECIPIENT"
        
        if treatment and outcome:
            return {
                'treatment': treatment,
                'outcome': outcome,
                'confounders': [],
                'causal_mechanisms': [],
                'confidence': 0.75,
                'extraction_method': 'advanced_patterns',
                'metadata': {
                    'domain': domain,
                    'semantic_roles': {
                        'cause_role_type': cause_role_type or 'UNKNOWN',
                        'effect_role_type': effect_role_type or 'UNKNOWN'
                    }
                }
            }
        
        return self._fallback_result("Advanced patterns incomplete")
    
    def _enhance_pattern_result(
        self,
        base_result: Dict[str, Any],
        query: str,
        domain: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enhance pattern-based result with additional deterministic analysis.
        
        Universal Abstraction: Uses rule-based enhancement, not LLM inference.
        """
        enhanced = base_result.copy()
        
        # Enhance confidence based on pattern quality
        treatment = enhanced.get('treatment', '')
        outcome = enhanced.get('outcome', '')
        
        # Quality indicators (deterministic rules)
        treatment_length = len(treatment.split()) if treatment else 0
        outcome_length = len(outcome.split()) if outcome else 0
        
        # Rule: Longer, more specific phrases indicate better extraction
        if treatment_length >= 2 and outcome_length >= 2:
            enhanced['confidence'] = min(0.95, enhanced.get('confidence', 0.6) + 0.1)
        
        # Rule: Semantic role types increase confidence
        if enhanced.get('metadata', {}).get('semantic_roles', {}).get('cause_role_type'):
            enhanced['confidence'] = min(0.95, enhanced.get('confidence', 0.6) + 0.05)
        
        # Add extraction quality metadata
        enhanced['metadata'] = enhanced.get('metadata', {})
        enhanced['metadata']['extraction_quality'] = {
            'treatment_length': treatment_length,
            'outcome_length': outcome_length,
            'enhanced': True
        }
        
        return enhanced
    
    def _parse_json_response(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response, handling code fences and whitespace."""
        if not content:
            return None
        
        # Remove code fences
        content = content.replace('```json', '').replace('```', '').strip()
        
        # Try to find JSON object
        first_brace = content.find('{')
        if first_brace == -1:
            return None
        
        # Extract complete JSON object
        brace_count = 0
        in_string = False
        escape_next = False
        json_end = -1
        
        for i, char in enumerate(content[first_brace:], start=first_brace):
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
            json_str = content[first_brace:json_end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _enhance_with_context(
        self,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance extraction result with additional context."""
        enhanced = result.copy()
        
        # Add context-derived confounders if available
        if 'confounders' in context:
            existing = enhanced.get('confounders', [])
            new_confounders = [c for c in context['confounders'] if c not in existing]
            enhanced['confounders'] = existing + new_confounders
        
        # Add context-derived mechanisms if available
        if 'causal_mechanisms' in context:
            existing = enhanced.get('causal_mechanisms', [])
            new_mechanisms = [m for m in context['causal_mechanisms'] if m not in existing]
            enhanced['causal_mechanisms'] = existing + new_mechanisms
        
        # Update metadata
        enhanced['metadata'] = enhanced.get('metadata', {})
        enhanced['metadata']['context_enhanced'] = True
        
        return enhanced
    
    def _check_alignment(self, text1: str, text2: str) -> bool:
        """Check if two texts are semantically aligned (simple word overlap)."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        overlap = len(words1 & words2)
        total_unique = len(words1 | words2)
        return overlap / total_unique > 0.3 if total_unique > 0 else False
    
    def _find_closest_key(self, concept: str, keys: List[str]) -> Optional[str]:
        """Find the data key that most closely matches a concept."""
        concept_words = set(concept.lower().split())
        best_match = None
        best_score = 0.0
        
        for key in keys:
            key_words = set(str(key).lower().split())
            overlap = len(concept_words & key_words)
            total = len(concept_words | key_words)
            score = overlap / total if total > 0 else 0.0
            
            if score > best_score and score > 0.2:
                best_score = score
                best_match = key
        
        return best_match
    
    def _fallback_result(self, reason: str) -> Dict[str, Any]:
        """Generate a fallback result when extraction fails."""
        return {
            'treatment': 'unknown_treatment',
            'outcome': 'unknown_outcome',
            'confounders': [],
            'causal_mechanisms': [],
            'confidence': 0.1,
            'extraction_method': 'fallback',
            'metadata': {'fallback_reason': reason}
        }


# Convenience function for backward compatibility and easy access
def extract_causal_parameters(
    query: Optional[str] = None,
    rise_analysis: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    domain: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    strategy: str = 'auto'
) -> Dict[str, Any]:
    """
    Universal convenience function for extracting causal parameters.
    
    This function provides a single entry point that automatically selects
    the appropriate extraction method based on available inputs.
    
    Args:
        query: Natural language query
        rise_analysis: RISE analysis dictionary
        data: Data structure (dict, DataFrame, etc.)
        domain: Domain context
        context: Additional context
        strategy: Extraction strategy ('auto', 'llm', 'pattern', 'hybrid')
    
    Returns:
        Dictionary with treatment, outcome, confounders, and metadata.
    """
    extractor = DynamicCausalParameterExtractor()
    
    # Priority: RISE analysis > query > data
    if rise_analysis:
        return extractor.extract_from_rise_analysis(rise_analysis, query)
    elif query:
        return extractor.extract_from_query(query, domain, context, strategy)
    elif data is not None:
        return extractor.extract_from_data_structure(data, query)
    else:
        return extractor._fallback_result("No input provided")


# Export for use across the codebase
__all__ = [
    'DynamicCausalParameterExtractor',
    'extract_causal_parameters'
]

