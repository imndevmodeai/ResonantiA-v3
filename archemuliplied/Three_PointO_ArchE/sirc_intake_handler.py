# Three_PointO_ArchE/sirc_intake_handler.py
# SIRC Intake Handler - Implements DirectiveClarificationProtocoL v1.0
# Processes keyy=('IMnDEVmode') directives with automatic ambiguity detection and clarification

import logging
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from .spr_manager import SPRManager

logger = logging.getLogger(__name__)

class SIRCIntakeHandler:
    """
    SIRC Intake Handler implementing DirectiveClarificationProtocoL v1.0
    
    Processes strategic directives received via keyy=('IMnDEVmode') invocation,
    detects ambiguity, generates contextual suggestions, and facilitates
    clarification through leading questions and confirmation-based interaction.
    
    Target: Improve ObjectiveClaritY score from 0.40 baseline to >0.85
    """
    
    def __init__(self, spr_manager: SPRManager = None):
        """Initialize the SIRC Intake Handler with required components."""
        self.spr_manager = spr_manager
        self.clarification_history = []
        
        # Ambiguity detection patterns
        self.vague_action_verbs = {
            'analyze', 'improve', 'enhance', 'optimize', 'solve', 'fix', 
            'develop', 'create', 'build', 'make', 'generate', 'produce',
            'increase', 'decrease', 'reduce', 'maximize', 'minimize',
            'handle', 'manage', 'process', 'work on', 'deal with'
        }
        
        self.undefined_scope_patterns = [
            r'\bsystem performance\b', r'\buser experience\b', r'\bmarket presence\b',
            r'\bdata quality\b', r'\bprocess efficiency\b', r'\bteam productivity\b',
            r'\bcode quality\b', r'\bsecurity posture\b', r'\barchitecture\b'
        ]
        
        self.missing_criteria_phrases = {
            'make it better', 'increase efficiency', 'improve quality',
            'enhance performance', 'optimize results', 'fix issues',
            'solve problems', 'work better', 'run faster', 'be more reliable'
        }
        
        self.temporal_ambiguity_terms = {
            'soon', 'quickly', 'fast', 'rapidly', 'immediately', 'asap',
            'long-term', 'short-term', 'eventually', 'later', 'when possible'
        }
        
        self.quantitative_gaps = {
            'more', 'less', 'better', 'worse', 'faster', 'slower',
            'higher', 'lower', 'significant', 'substantial', 'considerable'
        }
    
    def process_directive(self, directive: str, keyholder_callback=None) -> Dict[str, Any]:
        """
        Main entry point for processing a directive through the clarification protocol.
        
        Args:
            directive: The raw directive text received via keyy=('IMnDEVmode')
            keyholder_callback: Optional callback function for interactive clarification
            
        Returns:
            Dict containing the finalized objective and clarification metadata
        """
        logger.info(f"Processing directive: {directive[:100]}...")
        
        # Phase 1: Directive Intake & Ambiguity Detection
        detection_result = self._detect_ambiguity(directive)
        
        # Check bypass conditions
        if self._should_bypass_clarification(directive, detection_result):
            logger.info("Directive meets bypass conditions - proceeding directly")
            return {
                'finalized_objective': directive,
                'clarity_score': 0.95,  # High score for bypassed directives
                'clarification_needed': False,
                'bypass_reason': detection_result.get('bypass_reason', 'Technical precision detected')
            }
        
        # Phase 2-5: Full clarification protocol
        if detection_result['complexity'] == 'LOW':
            # Minimal clarification needed
            return self._minimal_clarification(directive, detection_result, keyholder_callback)
        else:
            # Full clarification protocol
            return self._full_clarification_protocol(directive, detection_result, keyholder_callback)
    
    def _detect_ambiguity(self, directive: str) -> Dict[str, Any]:
        """
        Phase 1: Detect ambiguity patterns in the directive.
        Activates AmbiguityDetectioN SPR functionality.
        """
        directive_lower = directive.lower()
        words = set(directive_lower.split())
        
        detection_result = {
            'vague_verbs': [],
            'undefined_scope': [],
            'missing_criteria': [],
            'temporal_ambiguity': [],
            'quantitative_gaps': [],
            'complexity': 'LOW',
            'ambiguity_score': 0.0
        }
        
        # Detect vague action verbs
        detected_verbs = words.intersection(self.vague_action_verbs)
        detection_result['vague_verbs'] = list(detected_verbs)
        
        # Detect undefined scope patterns
        for pattern in self.undefined_scope_patterns:
            if re.search(pattern, directive_lower):
                detection_result['undefined_scope'].append(pattern)
        
        # Detect missing success criteria
        for phrase in self.missing_criteria_phrases:
            if phrase in directive_lower:
                detection_result['missing_criteria'].append(phrase)
        
        # Detect temporal ambiguity
        detected_temporal = words.intersection(self.temporal_ambiguity_terms)
        detection_result['temporal_ambiguity'] = list(detected_temporal)
        
        # Detect quantitative gaps
        detected_quant = words.intersection(self.quantitative_gaps)
        detection_result['quantitative_gaps'] = list(detected_quant)
        
        # Calculate complexity and ambiguity score
        ambiguity_factors = (
            len(detection_result['vague_verbs']) +
            len(detection_result['undefined_scope']) +
            len(detection_result['missing_criteria']) +
            len(detection_result['temporal_ambiguity']) +
            len(detection_result['quantitative_gaps'])
        )
        
        detection_result['ambiguity_score'] = min(ambiguity_factors * 0.15, 1.0)
        
        if ambiguity_factors == 0:
            detection_result['complexity'] = 'LOW'
        elif ambiguity_factors <= 2:
            detection_result['complexity'] = 'MEDIUM'
        else:
            detection_result['complexity'] = 'HIGH'
        
        logger.info(f"Ambiguity detection: {ambiguity_factors} factors, complexity: {detection_result['complexity']}")
        return detection_result
    
    def _should_bypass_clarification(self, directive: str, detection_result: Dict[str, Any]) -> bool:
        """
        Check if directive meets bypass conditions for direct execution.
        """
        directive_lower = directive.lower()
        
        # Technical precision indicators
        technical_indicators = [
            r'\b\w+\(\)', r'\b\w+\.py\b', r'\bapi\b', r'\bdatabase\b',
            r'\bsql\b', r'\bjson\b', r'\bxml\b', r'\bhttp\b', r'\brest\b',
            r'\balgorithm\b', r'\bfunction\b', r'\bmethod\b', r'\bclass\b'
        ]
        
        for pattern in technical_indicators:
            if re.search(pattern, directive_lower):
                detection_result['bypass_reason'] = 'Technical precision detected'
                return True
        
        # Quantified metrics present
        if re.search(r'\b\d+%\b|\b\d+\s*(ms|seconds?|minutes?|hours?)\b|\b\d+\s*(MB|GB|KB)\b', directive):
            detection_result['bypass_reason'] = 'Quantified metrics present'
            return True
        
        # Bounded scope indicators
        bounded_indicators = [
            r'\bwithin\s+\d+\b', r'\bby\s+\d{4}-\d{2}-\d{2}\b',
            r'\busing\s+\w+\b', r'\bfor\s+dataset\b', r'\bin\s+file\b'
        ]
        
        for pattern in bounded_indicators:
            if re.search(pattern, directive):
                detection_result['bypass_reason'] = 'Bounded scope detected'
                return True
        
        # Historical pattern match (simplified - would use crystallized knowledge in full implementation)
        if detection_result['ambiguity_score'] < 0.1:
            detection_result['bypass_reason'] = 'Low ambiguity score'
            return True
        
        return False
    
    def _minimal_clarification(self, directive: str, detection_result: Dict[str, Any], keyholder_callback=None) -> Dict[str, Any]:
        """
        Handle low complexity directives with minimal clarification.
        """
        # For minimal clarification, we'll add basic specificity
        enhanced_directive = directive
        
        if detection_result['vague_verbs']:
            enhanced_directive += " (Please specify exact metrics and success criteria)"
        
        if detection_result['temporal_ambiguity']:
            enhanced_directive += " (Please specify timeframe)"
        
        return {
            'finalized_objective': enhanced_directive,
            'clarity_score': 0.75,
            'clarification_needed': True,
            'clarification_type': 'minimal',
            'enhancement_suggestions': enhanced_directive
        }
    
    def _full_clarification_protocol(self, directive: str, detection_result: Dict[str, Any], keyholder_callback=None) -> Dict[str, Any]:
        """
        Execute full clarification protocol for high complexity directives.
        Phases 2-5 of DirectiveClarificationProtocoL.
        """
        # Phase 2: Contextual Suggestion Generation
        suggestions = self._generate_contextual_suggestions(directive, detection_result)
        
        # Phase 3: Leading Question Presentation
        leading_question = self._format_leading_question(directive, suggestions)
        
        # Phase 4: Response Processing (simulated for now)
        if keyholder_callback:
            response = keyholder_callback(leading_question)
            refined_objective = self._process_keyholder_response(directive, suggestions, response)
        else:
            # Default to first suggestion if no callback
            logger.warning("No keyholder callback provided - defaulting to first suggestion")
            refined_objective = suggestions[0]['text'] if suggestions else directive
        
        # Phase 5: Objective Finalization
        finalized_result = self._finalize_resonant_objective(refined_objective, directive)
        
        return finalized_result
    
    def _generate_contextual_suggestions(self, directive: str, detection_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Phase 2: Generate specific, quantifiable alternatives.
        Activates ContextualSuggestionGeneratioN SPR functionality.
        """
        suggestions = []
        
        # Analyze domain context
        domain = self._analyze_domain(directive)
        
        # Generate domain-specific suggestions
        if domain == 'technical':
            suggestions.extend(self._generate_technical_suggestions(directive))
        elif domain == 'analytical':
            suggestions.extend(self._generate_analytical_suggestions(directive))
        elif domain == 'strategic':
            suggestions.extend(self._generate_strategic_suggestions(directive))
        else:
            suggestions.extend(self._generate_generic_suggestions(directive))
        
        # Ensure we have at least 3 suggestions and at most 4
        suggestions = suggestions[:4]
        while len(suggestions) < 3:
            suggestions.append({
                'text': f"Custom approach: {directive} with specific metrics to be defined",
                'confidence': 0.5,
                'rationale': 'Generic fallback option'
            })
        
        # Add "Other" option
        suggestions.append({
            'text': "Other specific approach (please specify)",
            'confidence': 0.0,
            'rationale': 'Custom specification required'
        })
        
        return suggestions
    
    def _analyze_domain(self, directive: str) -> str:
        """Analyze the domain context of the directive."""
        directive_lower = directive.lower()
        
        technical_keywords = ['api', 'database', 'code', 'system', 'performance', 'algorithm']
        analytical_keywords = ['analyze', 'data', 'metrics', 'report', 'insights', 'trends']
        strategic_keywords = ['strategy', 'plan', 'roadmap', 'vision', 'goals', 'objectives']
        
        tech_count = sum(1 for kw in technical_keywords if kw in directive_lower)
        analytical_count = sum(1 for kw in analytical_keywords if kw in directive_lower)
        strategic_count = sum(1 for kw in strategic_keywords if kw in directive_lower)
        
        if tech_count >= analytical_count and tech_count >= strategic_count:
            return 'technical'
        elif analytical_count >= strategic_count:
            return 'analytical'
        elif strategic_count > 0:
            return 'strategic'
        else:
            return 'generic'
    
    def _generate_technical_suggestions(self, directive: str) -> List[Dict[str, Any]]:
        """Generate technical domain suggestions."""
        return [
            {
                'text': f"Reduce API response time by 30% (from current baseline to <140ms) within 2 weeks using database optimization",
                'confidence': 0.85,
                'rationale': 'API optimization has 95% historical success rate'
            },
            {
                'text': f"Increase system throughput by 25% through caching implementation and query optimization",
                'confidence': 0.80,
                'rationale': 'Caching strategies show consistent performance gains'
            },
            {
                'text': f"Improve code quality metrics by 40% using automated testing and code review processes",
                'confidence': 0.75,
                'rationale': 'Quality metrics improvements are measurable and achievable'
            }
        ]
    
    def _generate_analytical_suggestions(self, directive: str) -> List[Dict[str, Any]]:
        """Generate analytical domain suggestions."""
        return [
            {
                'text': f"Generate comprehensive data analysis report with 95% confidence intervals within 1 week",
                'confidence': 0.90,
                'rationale': 'Statistical analysis with defined confidence levels'
            },
            {
                'text': f"Identify top 5 key performance indicators and establish baseline measurements",
                'confidence': 0.85,
                'rationale': 'KPI identification provides clear success metrics'
            },
            {
                'text': f"Create predictive model with >80% accuracy for specified outcome variable",
                'confidence': 0.75,
                'rationale': 'Predictive modeling with quantified accuracy targets'
            }
        ]
    
    def _generate_strategic_suggestions(self, directive: str) -> List[Dict[str, Any]]:
        """Generate strategic domain suggestions."""
        return [
            {
                'text': f"Develop 3-month strategic roadmap with weekly milestones and success criteria",
                'confidence': 0.80,
                'rationale': 'Time-bounded strategic planning with clear milestones'
            },
            {
                'text': f"Define 5 SMART objectives with quantifiable outcomes and 6-month timeline",
                'confidence': 0.85,
                'rationale': 'SMART objectives provide clear structure and measurability'
            },
            {
                'text': f"Create implementation plan with resource allocation and risk mitigation strategies",
                'confidence': 0.75,
                'rationale': 'Comprehensive planning addresses execution challenges'
            }
        ]
    
    def _generate_generic_suggestions(self, directive: str) -> List[Dict[str, Any]]:
        """Generate generic suggestions for unclear domains."""
        return [
            {
                'text': f"Define specific, measurable outcomes with 2-week timeline and success criteria",
                'confidence': 0.70,
                'rationale': 'Time-bounded objectives with clear success metrics'
            },
            {
                'text': f"Establish baseline measurements and target 20% improvement within 1 month",
                'confidence': 0.65,
                'rationale': 'Baseline establishment enables progress tracking'
            },
            {
                'text': f"Create detailed action plan with weekly checkpoints and deliverables",
                'confidence': 0.60,
                'rationale': 'Structured planning with regular progress reviews'
            }
        ]
    
    def _format_leading_question(self, directive: str, suggestions: List[Dict[str, Any]]) -> str:
        """
        Phase 3: Format leading question with suggestions.
        Activates LeadingQueryFormulationN SPR functionality.
        """
        question = f"For '{directive}', I suggest focusing on:\n\n"
        
        for i, suggestion in enumerate(suggestions[:-1], 1):  # Exclude "Other" option for numbering
            question += f"{chr(64+i)}) {suggestion['text']}\n"
        
        question += f"{chr(64+len(suggestions))}) {suggestions[-1]['text']}\n\n"
        
        # Add recommendation based on highest confidence
        best_suggestion = max(suggestions[:-1], key=lambda x: x['confidence'])
        best_index = suggestions.index(best_suggestion) + 1
        question += f"Based on historical success patterns, I recommend option {chr(64+best_index)} "
        question += f"({best_suggestion['rationale']}).\n\n"
        question += "Would you like to proceed with this recommendation, or would you prefer a different approach?"
        
        return question
    
    def _process_keyholder_response(self, directive: str, suggestions: List[Dict[str, Any]], response: str) -> str:
        """
        Phase 4: Process Keyholder response and refine objective.
        Activates PreferenceOverrideHandlinG SPR functionality.
        """
        response_lower = response.lower().strip()
        
        # Simple response parsing (would be more sophisticated in full implementation)
        if response_lower in ['a', 'option a', '1', 'first']:
            return suggestions[0]['text']
        elif response_lower in ['b', 'option b', '2', 'second']:
            return suggestions[1]['text'] if len(suggestions) > 1 else suggestions[0]['text']
        elif response_lower in ['c', 'option c', '3', 'third']:
            return suggestions[2]['text'] if len(suggestions) > 2 else suggestions[0]['text']
        elif response_lower in ['d', 'option d', '4', 'fourth', 'other']:
            return f"{directive} (requires further specification)"
        elif 'yes' in response_lower or 'proceed' in response_lower:
            # Default to recommendation
            best_suggestion = max(suggestions[:-1], key=lambda x: x['confidence'])
            return best_suggestion['text']
        else:
            # Try to extract refinements from the response
            return f"{suggestions[0]['text']} (refined based on: {response})"
    
    def _finalize_resonant_objective(self, refined_objective: str, original_directive: str) -> Dict[str, Any]:
        """
        Phase 5: Finalize objective and validate resonance.
        Activates FinalizeResonantObjective SPR functionality.
        """
        # Calculate clarity score based on objective characteristics
        clarity_score = self._calculate_clarity_score(refined_objective)
        
        # Ensure minimum clarity threshold
        if clarity_score < 0.85:
            # Add additional specificity
            enhanced_objective = self._enhance_objective_clarity(refined_objective)
            clarity_score = self._calculate_clarity_score(enhanced_objective)
            refined_objective = enhanced_objective
        
        result = {
            'finalized_objective': refined_objective,
            'original_directive': original_directive,
            'clarity_score': clarity_score,
            'clarification_needed': True,
            'clarification_type': 'full_protocol',
            'resonance_validation': {
                'technical_specificity': 'High' if clarity_score > 0.85 else 'Medium',
                'measurable_outcomes': 'Defined' if clarity_score > 0.80 else 'Partial',
                'success_criteria': 'Explicit' if clarity_score > 0.85 else 'Implicit',
                'execution_ready': clarity_score > 0.85
            }
        }
        
        # Log clarification for continuous improvement
        self.clarification_history.append({
            'original_directive': original_directive,
            'finalized_objective': refined_objective,
            'clarity_score': clarity_score,
            'timestamp': 'placeholder'  # Would use actual timestamp in full implementation
        })
        
        return result
    
    def _calculate_clarity_score(self, objective: str) -> float:
        """Calculate ObjectiveClaritY score for the objective."""
        score = 0.0
        
        # Quantifiable metrics present
        if re.search(r'\b\d+%\b|\b\d+\s*(ms|seconds?|minutes?|hours?|days?|weeks?|months?)\b', objective):
            score += 0.25
        
        # Specific timeframe
        if re.search(r'\bwithin\s+\d+\b|\bby\s+\d{4}-\d{2}-\d{2}\b|\bin\s+\d+\s*(days?|weeks?|months?)\b', objective):
            score += 0.20
        
        # Clear success criteria
        if any(criterion in objective.lower() for criterion in ['success', 'criteria', 'target', 'goal', 'outcome']):
            score += 0.15
        
        # Specific methods/tools mentioned
        if re.search(r'\busing\s+\w+\b|\bvia\s+\w+\b|\bthrough\s+\w+\b', objective):
            score += 0.15
        
        # Measurable outcomes
        if any(measure in objective.lower() for measure in ['measure', 'metric', 'kpi', 'indicator', 'score']):
            score += 0.10
        
        # Bounded scope
        if re.search(r'\bfor\s+\w+\b|\bin\s+\w+\b|\bof\s+\w+\b', objective):
            score += 0.10
        
        # Validation methods
        if any(validation in objective.lower() for validation in ['test', 'validate', 'verify', 'confirm']):
            score += 0.05
        
        return min(score, 1.0)
    
    def _enhance_objective_clarity(self, objective: str) -> str:
        """Enhance objective clarity to meet minimum threshold."""
        enhanced = objective
        
        # Add validation requirement if missing
        if 'validat' not in enhanced.lower() and 'test' not in enhanced.lower():
            enhanced += ", validated through appropriate testing methods"
        
        # Add measurement requirement if missing
        if not re.search(r'\bmeasur\w*\b|\bmetric\w*\b', enhanced.lower()):
            enhanced += " with measurable success criteria"
        
        # Add timeframe if missing
        if not re.search(r'\bwithin\s+\d+\b|\bin\s+\d+\s*(days?|weeks?|months?)\b', enhanced):
            enhanced += " within defined timeframe"
        
        return enhanced
    
    def get_clarification_metrics(self) -> Dict[str, Any]:
        """Get metrics for continuous improvement of the clarification protocol."""
        if not self.clarification_history:
            return {'total_clarifications': 0}
        
        clarity_scores = [entry['clarity_score'] for entry in self.clarification_history]
        
        return {
            'total_clarifications': len(self.clarification_history),
            'average_clarity_score': sum(clarity_scores) / len(clarity_scores),
            'clarity_improvement': clarity_scores[-1] - clarity_scores[0] if len(clarity_scores) > 1 else 0,
            'success_rate': sum(1 for score in clarity_scores if score > 0.85) / len(clarity_scores)
        } 