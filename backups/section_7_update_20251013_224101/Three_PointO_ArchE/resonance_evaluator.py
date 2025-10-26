#!/usr/bin/env python3
"""
Resonance Evaluator - Implementation of CognitiveresonancE Assessment
Operationalizes the "As Above, So Below" principle for dynamic alignment evaluation

This module implements the core CognitiveresonancE SPR capability, providing
quantitative assessment of alignment between:
- Incoming data streams
- Deep internal analysis
- Strategic objectives
- Probabilistic outcomes
- Temporal dimensions

Part of ResonantiA Protocol v3.1-CA Implementation Resonance initiative.
"""

import json
import numpy as np
from datetime import datetime, timedelta

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ResonanceMetrics:
    """Container for resonance assessment results."""
    data_alignment: float
    analysis_coherence: float
    objective_clarity: float
    outcome_probability: float
    temporal_consistency: float
    overall_resonance: float
    confidence: float
    assessment_timestamp: str
    dissonance_factors: List[str]
    enhancement_recommendations: List[str]

@dataclass
class ResonanceContext:
    """Input context for resonance evaluation."""
    data_sources: List[Dict[str, Any]]
    analysis_results: List[Dict[str, Any]]
    strategic_objectives: List[str]
    predicted_outcomes: List[Dict[str, Any]]
    temporal_scope: Dict[str, Any]
    iar_history: List[Dict[str, Any]]

class CognitiveResonanceEvaluator:
    """
    Implements CognitiveresonancE SPR - Dynamic alignment assessment across time.
    
    This class operationalizes the core principle that ArchE's success is measured
    by achieving profound, dynamic alignment between all cognitive components
    evaluated across the dimension of time (Temporal resonancE).
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the resonance evaluator with configuration."""
        self.config = config or self._get_default_config()
        self.assessment_history: List[ResonanceMetrics] = []
        self.dissonance_threshold = self.config.get('dissonance_threshold', 0.7)
        self.temporal_weight = self.config.get('temporal_weight', 0.3)
        
        logger.info("CognitiveResonanceEvaluator initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for resonance evaluation."""
        return {
            'dissonance_threshold': 0.7,
            'temporal_weight': 0.3,
            'confidence_threshold': 0.8,
            'alignment_weights': {
                'data_alignment': 0.25,
                'analysis_coherence': 0.25,
                'objective_clarity': 0.20,
                'outcome_probability': 0.20,
                'temporal_consistency': 0.10
            }
        }
    
    def evaluate_cognitive_resonance(self, context: ResonanceContext) -> ResonanceMetrics:
        """
        Main entry point for CognitiveresonancE assessment.
        
        Evaluates dynamic alignment across all cognitive dimensions with
        temporal awareness, returning quantified resonance metrics.
        
        Args:
            context: ResonanceContext containing all input data
            
        Returns:
            ResonanceMetrics with comprehensive assessment results
        """
        logger.info("Starting CognitiveresonancE evaluation")
        
        try:
            # Calculate individual alignment dimensions
            data_alignment = self._assess_data_alignment(context.data_sources)
            analysis_coherence = self._assess_analysis_coherence(context.analysis_results)
            objective_clarity = self._assess_objective_clarity(context.strategic_objectives)
            outcome_probability = self._assess_outcome_probability(context.predicted_outcomes)
            temporal_consistency = self._assess_temporal_consistency(context.temporal_scope, context.iar_history)
            
            # Calculate overall resonance using weighted average
            weights = self.config['alignment_weights']
            overall_resonance = (
                data_alignment * weights['data_alignment'] +
                analysis_coherence * weights['analysis_coherence'] +
                objective_clarity * weights['objective_clarity'] +
                outcome_probability * weights['outcome_probability'] +
                temporal_consistency * weights['temporal_consistency']
            )
            
            # Assess confidence in the evaluation
            confidence = self._calculate_assessment_confidence(context)
            
            # Identify dissonance factors and recommendations
            dissonance_factors = self._identify_dissonance_factors(
                data_alignment, analysis_coherence, objective_clarity,
                outcome_probability, temporal_consistency
            )
            enhancement_recommendations = self._generate_enhancement_recommendations(
                data_alignment, analysis_coherence, objective_clarity,
                outcome_probability, temporal_consistency
            )
            
            # Create comprehensive metrics
            metrics = ResonanceMetrics(
                data_alignment=data_alignment,
                analysis_coherence=analysis_coherence,
                objective_clarity=objective_clarity,
                outcome_probability=outcome_probability,
                temporal_consistency=temporal_consistency,
                overall_resonance=overall_resonance,
                confidence=confidence,
                assessment_timestamp=now_iso(),
                dissonance_factors=dissonance_factors,
                enhancement_recommendations=enhancement_recommendations
            )
            
            # Store in history for temporal analysis
            self.assessment_history.append(metrics)
            
            logger.info(f"CognitiveresonancE evaluation complete: {overall_resonance:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error in resonance evaluation: {e}")
            raise
    
    def _assess_data_alignment(self, data_sources: List[Dict[str, Any]]) -> float:
        """
        Assess alignment quality of incoming data streams.
        
        Evaluates consistency, reliability, and relevance of data sources.
        """
        if not data_sources:
            return 0.0
        
        alignment_scores = []
        
        for source in data_sources:
            score = 0.0
            
            # Data quality indicators
            if source.get('confidence', 0) > 0.8:
                score += 0.3
            if source.get('recency_hours', 24) < 12:
                score += 0.2
            if source.get('reliability_score', 0.5) > 0.7:
                score += 0.3
            if source.get('relevance_score', 0.5) > 0.7:
                score += 0.2
            
            alignment_scores.append(score)
        
        return np.mean(alignment_scores)
    
    def _assess_analysis_coherence(self, analysis_results: List[Dict[str, Any]]) -> float:
        """
        Assess coherence of internal analysis via tools and SPR-activated knowledge.
        
        Evaluates consistency across different analytical approaches.
        """
        if not analysis_results:
            return 0.0
        
        coherence_scores = []
        
        for result in analysis_results:
            score = 0.0
            
            # Analysis quality indicators
            if result.get('confidence', 0) > 0.8:
                score += 0.4
            if result.get('method_reliability', 0.5) > 0.7:
                score += 0.3
            if result.get('cross_validation', False):
                score += 0.3
            
            coherence_scores.append(score)
        
        # Check for consistency across analyses
        if len(coherence_scores) > 1:
            consistency_bonus = 1.0 - np.std(coherence_scores)
            avg_score = np.mean(coherence_scores)
            return min(1.0, avg_score * consistency_bonus)
        
        return np.mean(coherence_scores) if coherence_scores else 0.0
    
    def _assess_objective_clarity(self, strategic_objectives: List[str]) -> float:
        """
        Assess clarity and consistency of strategic objectives.
        
        Evaluates whether objectives are well-defined and achievable.
        """
        if not strategic_objectives:
            return 0.0
        
        clarity_score = 0.0
        
        # Objective quality indicators
        if len(strategic_objectives) <= 5:  # Not too many objectives
            clarity_score += 0.3
        
        for objective in strategic_objectives:
            if len(objective) > 10:  # Sufficient detail
                clarity_score += 0.1
            if any(word in objective.lower() for word in ['measure', 'quantify', 'achieve', 'improve']):
                clarity_score += 0.1  # Action-oriented
        
        return min(1.0, clarity_score)
    
    def _assess_outcome_probability(self, predicted_outcomes: List[Dict[str, Any]]) -> float:
        """
        Assess the probabilistic landscape of potential outcomes.
        
        Evaluates confidence and consistency in outcome predictions.
        """
        if not predicted_outcomes:
            return 0.0
        
        probability_scores = []
        
        for outcome in predicted_outcomes:
            score = 0.0
            
            # Outcome prediction quality
            confidence = outcome.get('confidence', 0.5)
            probability = outcome.get('probability', 0.5)
            
            # Higher confidence in predictions is better
            score += confidence * 0.5
            
            # Reasonable probability ranges (not too extreme)
            if 0.2 <= probability <= 0.8:
                score += 0.3
            elif 0.1 <= probability <= 0.9:
                score += 0.2
            
            # Evidence support
            if outcome.get('evidence_support', 0) > 3:
                score += 0.2
            
            probability_scores.append(score)
        
        return np.mean(probability_scores)
    
    def _assess_temporal_consistency(self, temporal_scope: Dict[str, Any], 
                                   iar_history: List[Dict[str, Any]]) -> float:
        """
        Assess temporal consistency and 4D thinking integration.
        
        Evaluates how well the analysis considers time dimensions.
        """
        temporal_score = 0.0
        
        # Temporal scope evaluation
        if temporal_scope.get('historical_context'):
            temporal_score += 0.3
        if temporal_scope.get('future_projections'):
            temporal_score += 0.3
        if temporal_scope.get('time_horizon_defined'):
            temporal_score += 0.2
        
        # IAR history consistency
        if iar_history:
            recent_confidences = [iar.get('confidence', 0.5) for iar in iar_history[-5:]]
            if recent_confidences:
                confidence_trend = np.mean(recent_confidences)
                stability = 1.0 - np.std(recent_confidences)
                temporal_score += (confidence_trend * stability) * 0.2
        
        return min(1.0, temporal_score)
    
    def _calculate_assessment_confidence(self, context: ResonanceContext) -> float:
        """Calculate confidence in the resonance assessment itself."""
        confidence_factors = []
        
        # Data availability
        if len(context.data_sources) >= 2:
            confidence_factors.append(0.8)
        elif len(context.data_sources) >= 1:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.2)
        
        # Analysis depth
        if len(context.analysis_results) >= 3:
            confidence_factors.append(0.9)
        elif len(context.analysis_results) >= 1:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.3)
        
        # Temporal context
        if context.temporal_scope and context.iar_history:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        return np.mean(confidence_factors)
    
    def _identify_dissonance_factors(self, data_alignment: float, analysis_coherence: float,
                                   objective_clarity: float, outcome_probability: float,
                                   temporal_consistency: float) -> List[str]:
        """Identify specific factors causing dissonance."""
        dissonance_factors = []
        threshold = self.dissonance_threshold
        
        if data_alignment < threshold:
            dissonance_factors.append("data_quality_issues")
        if analysis_coherence < threshold:
            dissonance_factors.append("analysis_inconsistency")
        if objective_clarity < threshold:
            dissonance_factors.append("unclear_objectives")
        if outcome_probability < threshold:
            dissonance_factors.append("uncertain_predictions")
        if temporal_consistency < threshold:
            dissonance_factors.append("temporal_misalignment")
        
        return dissonance_factors
    
    def _generate_enhancement_recommendations(self, data_alignment: float, analysis_coherence: float,
                                            objective_clarity: float, outcome_probability: float,
                                            temporal_consistency: float) -> List[str]:
        """Generate specific recommendations for enhancing resonance."""
        recommendations = []
        threshold = 0.8  # High standard for recommendations
        
        if data_alignment < threshold:
            recommendations.append("improve_data_source_reliability")
        if analysis_coherence < threshold:
            recommendations.append("cross_validate_analysis_methods")
        if objective_clarity < threshold:
            recommendations.append("refine_strategic_objectives")
        if outcome_probability < threshold:
            recommendations.append("gather_additional_evidence")
        if temporal_consistency < threshold:
            recommendations.append("enhance_temporal_analysis")
        
        return recommendations
    
    def get_resonance_trend(self, lookback_periods: int = 10) -> Dict[str, Any]:
        """
        Analyze resonance trends over recent assessments.
        
        Returns trend analysis for meta-cognitive monitoring.
        """
        if len(self.assessment_history) < 2:
            return {"trend": "insufficient_data", "periods": len(self.assessment_history)}
        
        recent_assessments = self.assessment_history[-lookback_periods:]
        resonance_scores = [assessment.overall_resonance for assessment in recent_assessments]
        
        # Calculate trend
        if len(resonance_scores) >= 3:
            trend_slope = np.polyfit(range(len(resonance_scores)), resonance_scores, 1)[0]
            if trend_slope > 0.02:
                trend = "improving"
            elif trend_slope < -0.02:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "current_score": resonance_scores[-1],
            "average_score": np.mean(resonance_scores),
            "score_variance": np.var(resonance_scores),
            "periods_analyzed": len(resonance_scores)
        }
    
    def generate_iar_reflection(self, metrics: ResonanceMetrics) -> Dict[str, Any]:
        """
        Generate IAR reflection for the resonance evaluation itself.
        
        This implements the self-awareness requirement that every action
        must generate reflection data.
        """
        return {
            "status": "completed",
            "confidence": metrics.confidence,
            "potential_issues": metrics.dissonance_factors,
            "alignment_check": "high" if metrics.overall_resonance > 0.8 else "medium" if metrics.overall_resonance > 0.6 else "low",
            "tactical_resonance": metrics.overall_resonance,
            "crystallization_potential": "high" if metrics.confidence > 0.8 and metrics.overall_resonance > 0.8 else "medium",
            "timestamp": metrics.assessment_timestamp,
            "enhancement_recommendations": metrics.enhancement_recommendations
        }

# Factory function for easy integration
def create_resonance_evaluator(config: Optional[Dict[str, Any]] = None) -> CognitiveResonanceEvaluator:
    """Factory function to create a configured resonance evaluator."""
    return CognitiveResonanceEvaluator(config)

def evaluate_workflow_resonance(workflow_context: Dict[str, Any], 
                               evaluation_criteria: Optional[Dict[str, str]] = None,
                               evaluation_mode: str = "comprehensive",
                               include_recommendations: bool = True,
                               **kwargs) -> Dict[str, Any]:
    """
    SPR Bridge compatible function for evaluating workflow resonance.
    
    This function converts workflow context into ResonanceContext format
    and returns IAR-compliant results for CognitiveresonancE SPR.
    
    Args:
        workflow_context: Dictionary containing workflow execution details
        evaluation_criteria: Optional criteria for evaluation
        evaluation_mode: Mode of evaluation (comprehensive, basic, etc.)
        include_recommendations: Whether to include enhancement recommendations
        **kwargs: Additional parameters
        
    Returns:
        IAR-compliant dictionary with resonance evaluation results
    """
    try:
        # Create resonance evaluator
        evaluator = create_resonance_evaluator()
        
        # Convert workflow context to ResonanceContext
        resonance_context = _convert_workflow_to_resonance_context(workflow_context)
        
        # Perform evaluation
        metrics = evaluator.evaluate_cognitive_resonance(resonance_context)
        
        # Generate IAR reflection
        iar_reflection = evaluator.generate_iar_reflection(metrics)
        
        # Create comprehensive result
        result = {
            "status": "success",
            "confidence": metrics.confidence,
            "potential_issues": metrics.dissonance_factors,
            "alignment_check": "aligned" if metrics.overall_resonance > 0.7 else "misaligned",
            "tactical_resonance": metrics.overall_resonance,
            "crystallization_potential": metrics.confidence * metrics.overall_resonance,
            
            # Detailed resonance results
            "resonance_scores": {
                "data_alignment": metrics.data_alignment,
                "analysis_coherence": metrics.analysis_coherence,
                "objective_clarity": metrics.objective_clarity,
                "outcome_probability": metrics.outcome_probability,
                "temporal_consistency": metrics.temporal_consistency
            },
            "overall_resonance": f"{metrics.overall_resonance:.3f}",
            "assessment_timestamp": metrics.assessment_timestamp,
            
            # Recommendations if requested
            "recommendations": metrics.enhancement_recommendations if include_recommendations else [],
            
            # Evaluation metadata
            "evaluation_mode": evaluation_mode,
            "criteria_applied": evaluation_criteria or "default_comprehensive",
            "workflow_complexity": workflow_context.get("workflow_complexity", "unknown"),
            "execution_time": workflow_context.get("execution_time_seconds", 0)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error in evaluate_workflow_resonance: {e}")
        return {
            "status": "error",
            "confidence": 0.0,
            "potential_issues": [f"Evaluation failed: {str(e)}"],
            "alignment_check": "failed",
            "tactical_resonance": 0.0,
            "crystallization_potential": 0.0,
            "error_details": str(e)
        }

def _convert_workflow_to_resonance_context(workflow_context: Dict[str, Any]) -> ResonanceContext:
    """
    Convert workflow context to ResonanceContext format.
    
    Maps workflow execution details to the structured format expected
    by the CognitiveResonanceEvaluator.
    """
    # Extract data sources from workflow
    data_sources = []
    if "data_sources_used" in workflow_context:
        for source in workflow_context["data_sources_used"]:
            data_sources.append({
                "confidence": 0.8,  # Default confidence
                "recency_hours": 1,  # Assume recent
                "reliability_score": 0.8,  # Default reliability
                "relevance_score": 0.9,  # Assume relevant
                "source_name": source
            })
    
    # Extract analysis results from thought trail
    analysis_results = []
    if "thought_trail_summary" in workflow_context:
        for step in workflow_context["thought_trail_summary"]:
            analysis_results.append({
                "confidence": step.get("confidence", 0.7),
                "method_reliability": 0.8,
                "cross_validation": True,
                "action": step.get("action", "unknown"),
                "findings": step.get("key_findings", "")
            })
    
    # Extract strategic objectives
    strategic_objectives = [workflow_context.get("objective", "Unknown objective")]
    
    # Extract predicted outcomes
    predicted_outcomes = [{
        "confidence": 0.8,
        "probability": 0.7,
        "evidence_support": len(data_sources),
        "outcome": workflow_context.get("final_output", "No output specified")
    }]
    
    # Create temporal scope
    temporal_scope = {
        "historical_context": True,  # Assume some historical context
        "future_projections": "final_output" in workflow_context,
        "time_horizon_defined": "execution_time_seconds" in workflow_context
    }
    
    # Create IAR history from confidence trajectory
    iar_history = []
    if "confidence_trajectory" in workflow_context:
        for conf in workflow_context["confidence_trajectory"]:
            iar_history.append({"confidence": conf})
    
    return ResonanceContext(
        data_sources=data_sources,
        analysis_results=analysis_results,
        strategic_objectives=strategic_objectives,
        predicted_outcomes=predicted_outcomes,
        temporal_scope=temporal_scope,
        iar_history=iar_history
    )

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    evaluator = create_resonance_evaluator()
    
    # Sample context for testing
    sample_context = ResonanceContext(
        data_sources=[
            {"confidence": 0.9, "recency_hours": 2, "reliability_score": 0.8, "relevance_score": 0.9},
            {"confidence": 0.7, "recency_hours": 8, "reliability_score": 0.9, "relevance_score": 0.8}
        ],
        analysis_results=[
            {"confidence": 0.85, "method_reliability": 0.8, "cross_validation": True},
            {"confidence": 0.82, "method_reliability": 0.9, "cross_validation": True}
        ],
        strategic_objectives=["Improve system performance by 20%", "Reduce response time"],
        predicted_outcomes=[
            {"confidence": 0.8, "probability": 0.7, "evidence_support": 5},
            {"confidence": 0.75, "probability": 0.6, "evidence_support": 4}
        ],
        temporal_scope={
            "historical_context": True,
            "future_projections": True,
            "time_horizon_defined": True
        },
        iar_history=[
            {"confidence": 0.8}, {"confidence": 0.82}, {"confidence": 0.85}
        ]
    )
    
    # Evaluate resonance
    metrics = evaluator.evaluate_cognitive_resonance(sample_context)
    iar_reflection = evaluator.generate_iar_reflection(metrics)
    
    print("CognitiveresonancE Evaluation Results:")
    print(f"Overall Resonance: {metrics.overall_resonance:.3f}")
    print(f"Confidence: {metrics.confidence:.3f}")
    print(f"Dissonance Factors: {metrics.dissonance_factors}")
    print(f"Recommendations: {metrics.enhancement_recommendations}")
    print(f"IAR Reflection: {iar_reflection}") 