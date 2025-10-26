#!/usr/bin/env python3
"""
Metacognitive Shift Processor - Implementation of MetacognitiveshifT SPR
Operationalizes reactive meta-cognitive error correction and adaptation

This module implements the MetacognitiveshifT SPR capability, providing:
- Dissonance detection from IAR data
- Root cause analysis of cognitive failures
- Corrective strategy formulation
- Adaptive learning and improvement
- Self-aware cognitive monitoring

Part of ResonantiA Protocol v3.1-CA Implementation Resonance initiative.
"""

import json
import numpy as np
from datetime import datetime, timedelta

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now, now_iso, ago, from_now, format_log, format_filename


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DissonanceType(Enum):
    """Types of cognitive dissonance that can trigger metacognitive shifts."""
    LOW_CONFIDENCE = "low_confidence"
    REPEATED_FAILURE = "repeated_failure"
    STRATEGY_MISALIGNMENT = "strategy_misalignment"
    INCONSISTENT_RESULTS = "inconsistent_results"
    EXTERNAL_CONTRADICTION = "external_contradiction"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"

class ShiftSeverity(Enum):
    """Severity levels for metacognitive shifts."""
    MINOR = "minor"           # Small adjustments
    MODERATE = "moderate"     # Strategy changes
    MAJOR = "major"          # Fundamental approach revision
    CRITICAL = "critical"    # Complete restart required

class CorrectionStrategy(Enum):
    """Types of corrective strategies available."""
    PARAMETER_ADJUSTMENT = "parameter_adjustment"
    METHOD_SUBSTITUTION = "method_substitution"
    APPROACH_REVISION = "approach_revision"
    KNOWLEDGE_UPDATE = "knowledge_update"
    RESOURCE_REALLOCATION = "resource_reallocation"
    OBJECTIVE_CLARIFICATION = "objective_clarification"
    TEMPORAL_REFRAMING = "temporal_reframing"

@dataclass
class DissonanceSignal:
    """Container for detected dissonance information."""
    dissonance_type: DissonanceType
    severity: ShiftSeverity
    confidence: float
    evidence: Dict[str, Any]
    affected_components: List[str]
    temporal_context: Dict[str, Any]
    detection_timestamp: str = field(default_factory=lambda: now_iso())

@dataclass
class CorrectionPlan:
    """Container for metacognitive correction strategy."""
    correction_strategy: CorrectionStrategy
    target_components: List[str]
    adjustments: Dict[str, Any]
    expected_outcomes: List[str]
    success_metrics: Dict[str, float]
    implementation_steps: List[str]
    rollback_plan: Optional[Dict[str, Any]] = None
    estimated_effectiveness: float = 0.0

@dataclass
class ShiftResult:
    """Container for metacognitive shift execution results."""
    shift_id: str
    original_dissonance: DissonanceSignal
    correction_plan: CorrectionPlan
    execution_status: str
    outcomes_achieved: List[str]
    performance_delta: Dict[str, float]
    lessons_learned: List[str]
    timestamp: str = field(default_factory=lambda: now_iso())
    success_score: float = 0.0

class DissonanceDetector:
    """Detects cognitive dissonance from IAR streams and system state."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize dissonance detector with configuration."""
        self.config = config or self._get_default_config()
        self.detection_history: List[DissonanceSignal] = []
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for dissonance detection."""
        return {
            'confidence_threshold': 0.7,
            'failure_count_threshold': 3,
            'consistency_threshold': 0.8,
            'temporal_window_hours': 24,
            'detection_sensitivity': 0.8
        }
    
    def detect_dissonance(self, iar_stream: List[Dict[str, Any]], 
                         system_state: Dict[str, Any]) -> List[DissonanceSignal]:
        """
        Detect cognitive dissonance from IAR data and system state.
        
        Args:
            iar_stream: Recent IAR reflection data
            system_state: Current system operational state
            
        Returns:
            List of detected dissonance signals
        """
        logger.info("Detecting cognitive dissonance from IAR stream")
        
        dissonance_signals = []
        
        try:
            # Low confidence detection
            low_confidence = self._detect_low_confidence(iar_stream)
            if low_confidence:
                dissonance_signals.append(low_confidence)
            
            # Repeated failure detection
            repeated_failures = self._detect_repeated_failures(iar_stream)
            if repeated_failures:
                dissonance_signals.append(repeated_failures)
            
            # Strategy misalignment detection
            strategy_misalignment = self._detect_strategy_misalignment(iar_stream, system_state)
            if strategy_misalignment:
                dissonance_signals.append(strategy_misalignment)
            
            # Inconsistent results detection
            inconsistent_results = self._detect_inconsistent_results(iar_stream)
            if inconsistent_results:
                dissonance_signals.append(inconsistent_results)
            
            # Temporal inconsistency detection
            temporal_inconsistency = self._detect_temporal_inconsistency(iar_stream)
            if temporal_inconsistency:
                dissonance_signals.append(temporal_inconsistency)
            
            # Store detection history
            self.detection_history.extend(dissonance_signals)
            
            logger.info(f"Detected {len(dissonance_signals)} dissonance signals")
            return dissonance_signals
            
        except Exception as e:
            logger.error(f"Error in dissonance detection: {e}")
            return []
    
    def _detect_low_confidence(self, iar_stream: List[Dict[str, Any]]) -> Optional[DissonanceSignal]:
        """Detect patterns of low confidence in IAR data."""
        if not iar_stream:
            return None
        
        recent_confidences = [
            iar.get('confidence', 0.5) for iar in iar_stream[-10:]  # Last 10 actions
        ]
        
        if not recent_confidences:
            return None
        
        avg_confidence = np.mean(recent_confidences)
        confidence_trend = np.polyfit(range(len(recent_confidences)), recent_confidences, 1)[0]
        
        threshold = self.config['confidence_threshold']
        
        if avg_confidence < threshold or confidence_trend < -0.1:
            severity = ShiftSeverity.MAJOR if avg_confidence < 0.5 else ShiftSeverity.MODERATE
            
            return DissonanceSignal(
                dissonance_type=DissonanceType.LOW_CONFIDENCE,
                severity=severity,
                confidence=0.9,  # High confidence in this detection
                evidence={
                    'average_confidence': avg_confidence,
                    'confidence_trend': confidence_trend,
                    'samples_analyzed': len(recent_confidences),
                    'threshold_used': threshold
                },
                affected_components=['cognitive_processing', 'decision_making'],
                temporal_context={'analysis_window': '10_recent_actions'}
            )
        
        return None
    
    def _detect_repeated_failures(self, iar_stream: List[Dict[str, Any]]) -> Optional[DissonanceSignal]:
        """Detect patterns of repeated failures."""
        if not iar_stream:
            return None
        
        recent_statuses = [
            iar.get('status', 'unknown') for iar in iar_stream[-10:]
        ]
        
        failure_count = sum(1 for status in recent_statuses if status in ['failed', 'error', 'timeout'])
        failure_rate = failure_count / len(recent_statuses) if recent_statuses else 0
        
        threshold = self.config['failure_count_threshold']
        
        if failure_count >= threshold or failure_rate > 0.3:
            severity = ShiftSeverity.CRITICAL if failure_rate > 0.5 else ShiftSeverity.MAJOR
            
            return DissonanceSignal(
                dissonance_type=DissonanceType.REPEATED_FAILURE,
                severity=severity,
                confidence=0.95,
                evidence={
                    'failure_count': failure_count,
                    'failure_rate': failure_rate,
                    'recent_statuses': recent_statuses,
                    'threshold_used': threshold
                },
                affected_components=['execution_engine', 'tool_integration'],
                temporal_context={'analysis_window': '10_recent_actions'}
            )
        
        return None
    
    def _detect_strategy_misalignment(self, iar_stream: List[Dict[str, Any]], 
                                    system_state: Dict[str, Any]) -> Optional[DissonanceSignal]:
        """Detect misalignment between strategy and outcomes."""
        if not iar_stream:
            return None
        
        alignment_checks = [
            iar.get('alignment_check', 'unknown') for iar in iar_stream[-10:]
        ]
        
        low_alignment_count = sum(1 for check in alignment_checks if check == 'low')
        misalignment_rate = low_alignment_count / len(alignment_checks) if alignment_checks else 0
        
        if misalignment_rate > 0.4:  # 40% misalignment threshold
            severity = ShiftSeverity.MAJOR if misalignment_rate > 0.6 else ShiftSeverity.MODERATE
            
            return DissonanceSignal(
                dissonance_type=DissonanceType.STRATEGY_MISALIGNMENT,
                severity=severity,
                confidence=0.8,
                evidence={
                    'misalignment_rate': misalignment_rate,
                    'low_alignment_count': low_alignment_count,
                    'alignment_checks': alignment_checks,
                    'current_objectives': system_state.get('current_objectives', [])
                },
                affected_components=['strategic_planning', 'objective_alignment'],
                temporal_context={'analysis_window': '10_recent_actions'}
            )
        
        return None
    
    def _detect_inconsistent_results(self, iar_stream: List[Dict[str, Any]]) -> Optional[DissonanceSignal]:
        """Detect inconsistent results from similar operations."""
        if len(iar_stream) < 5:
            return None
        
        # Group by operation type if available
        operation_groups = {}
        for iar in iar_stream[-20:]:  # Analyze last 20 actions
            op_type = iar.get('operation_type', 'unknown')
            if op_type not in operation_groups:
                operation_groups[op_type] = []
            operation_groups[op_type].append(iar)
        
        inconsistency_detected = False
        evidence = {}
        
        for op_type, iars in operation_groups.items():
            if len(iars) >= 3:  # Need at least 3 samples
                confidences = [iar.get('confidence', 0.5) for iar in iars]
                confidence_variance = np.var(confidences)
                
                if confidence_variance > 0.1:  # High variance threshold
                    inconsistency_detected = True
                    evidence[f'{op_type}_variance'] = confidence_variance
                    evidence[f'{op_type}_confidences'] = confidences
        
        if inconsistency_detected:
            return DissonanceSignal(
                dissonance_type=DissonanceType.INCONSISTENT_RESULTS,
                severity=ShiftSeverity.MODERATE,
                confidence=0.75,
                evidence=evidence,
                affected_components=['result_consistency', 'method_reliability'],
                temporal_context={'analysis_window': '20_recent_actions'}
            )
        
        return None
    
    def _detect_temporal_inconsistency(self, iar_stream: List[Dict[str, Any]]) -> Optional[DissonanceSignal]:
        """Detect temporal inconsistencies in cognitive processing."""
        if not iar_stream:
            return None
        
        # Check for temporal reasoning issues
        temporal_issues = []
        for iar in iar_stream[-10:]:
            potential_issues = iar.get('potential_issues', [])
            temporal_issues.extend([
                issue for issue in potential_issues 
                if 'temporal' in issue.lower() or 'time' in issue.lower()
            ])
        
        if len(temporal_issues) >= 3:  # Multiple temporal issues
            return DissonanceSignal(
                dissonance_type=DissonanceType.TEMPORAL_INCONSISTENCY,
                severity=ShiftSeverity.MODERATE,
                confidence=0.8,
                evidence={
                    'temporal_issues_count': len(temporal_issues),
                    'temporal_issues': temporal_issues[:5],  # Top 5
                    'affected_actions': len([iar for iar in iar_stream[-10:] 
                                           if any('temporal' in issue.lower() for issue in iar.get('potential_issues', []))])
                },
                affected_components=['temporal_reasoning', '4d_thinking'],
                temporal_context={'analysis_window': '10_recent_actions'}
            )
        
        return None

class CorrectionPlanner:
    """Plans corrective strategies for detected dissonance."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize correction planner."""
        self.config = config or self._get_default_config()
        self.strategy_history: List[CorrectionPlan] = []
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for correction planning."""
        return {
            'max_correction_attempts': 3,
            'effectiveness_threshold': 0.7,
            'rollback_threshold': 0.3,
            'learning_rate': 0.1
        }
    
    def plan_correction(self, dissonance: DissonanceSignal, 
                       system_state: Dict[str, Any]) -> CorrectionPlan:
        """
        Plan corrective strategy for detected dissonance.
        
        Args:
            dissonance: DissonanceSignal requiring correction
            system_state: Current system state
            
        Returns:
            CorrectionPlan with detailed correction strategy
        """
        logger.info(f"Planning correction for {dissonance.dissonance_type.value}")
        
        try:
            # Select correction strategy based on dissonance type
            strategy = self._select_correction_strategy(dissonance)
            
            # Determine target components
            target_components = dissonance.affected_components.copy()
            
            # Plan specific adjustments
            adjustments = self._plan_adjustments(dissonance, strategy, system_state)
            
            # Define expected outcomes
            expected_outcomes = self._define_expected_outcomes(dissonance, strategy)
            
            # Set success metrics
            success_metrics = self._define_success_metrics(dissonance, strategy)
            
            # Create implementation steps
            implementation_steps = self._create_implementation_steps(strategy, adjustments)
            
            # Plan rollback strategy
            rollback_plan = self._plan_rollback_strategy(system_state)
            
            # Estimate effectiveness
            effectiveness = self._estimate_effectiveness(dissonance, strategy)
            
            plan = CorrectionPlan(
                correction_strategy=strategy,
                target_components=target_components,
                adjustments=adjustments,
                expected_outcomes=expected_outcomes,
                success_metrics=success_metrics,
                implementation_steps=implementation_steps,
                rollback_plan=rollback_plan,
                estimated_effectiveness=effectiveness
            )
            
            self.strategy_history.append(plan)
            logger.info(f"Correction plan created: {strategy.value}")
            return plan
            
        except Exception as e:
            logger.error(f"Error in correction planning: {e}")
            # Return minimal safe plan
            return CorrectionPlan(
                correction_strategy=CorrectionStrategy.PARAMETER_ADJUSTMENT,
                target_components=['error_handling'],
                adjustments={'error_tolerance': 0.1},
                expected_outcomes=['improved_error_handling'],
                success_metrics={'error_rate': 0.1},
                implementation_steps=['adjust_error_tolerance'],
                estimated_effectiveness=0.5
            )
    
    def _select_correction_strategy(self, dissonance: DissonanceSignal) -> CorrectionStrategy:
        """Select appropriate correction strategy based on dissonance type."""
        strategy_map = {
            DissonanceType.LOW_CONFIDENCE: CorrectionStrategy.METHOD_SUBSTITUTION,
            DissonanceType.REPEATED_FAILURE: CorrectionStrategy.APPROACH_REVISION,
            DissonanceType.STRATEGY_MISALIGNMENT: CorrectionStrategy.OBJECTIVE_CLARIFICATION,
            DissonanceType.INCONSISTENT_RESULTS: CorrectionStrategy.PARAMETER_ADJUSTMENT,
            DissonanceType.TEMPORAL_INCONSISTENCY: CorrectionStrategy.TEMPORAL_REFRAMING,
            DissonanceType.RESOURCE_EXHAUSTION: CorrectionStrategy.RESOURCE_REALLOCATION,
            DissonanceType.EXTERNAL_CONTRADICTION: CorrectionStrategy.KNOWLEDGE_UPDATE
        }
        
        return strategy_map.get(dissonance.dissonance_type, CorrectionStrategy.PARAMETER_ADJUSTMENT)
    
    def _plan_adjustments(self, dissonance: DissonanceSignal, strategy: CorrectionStrategy, 
                         system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Plan specific adjustments based on strategy."""
        adjustments = {}
        
        if strategy == CorrectionStrategy.PARAMETER_ADJUSTMENT:
            if dissonance.dissonance_type == DissonanceType.LOW_CONFIDENCE:
                adjustments['confidence_threshold'] = max(0.5, self.config.get('confidence_threshold', 0.7) - 0.1)
                adjustments['validation_steps'] = system_state.get('validation_steps', 1) + 1
            elif dissonance.dissonance_type == DissonanceType.INCONSISTENT_RESULTS:
                adjustments['consistency_checks'] = True
                adjustments['result_validation'] = 'enhanced'
        
        elif strategy == CorrectionStrategy.METHOD_SUBSTITUTION:
            adjustments['alternative_methods'] = ['backup_analysis', 'simplified_approach']
            adjustments['method_selection_criteria'] = 'reliability_over_complexity'
        
        elif strategy == CorrectionStrategy.APPROACH_REVISION:
            adjustments['approach_change'] = 'fundamental_revision'
            adjustments['fallback_enabled'] = True
            adjustments['progressive_complexity'] = True
        
        elif strategy == CorrectionStrategy.TEMPORAL_REFRAMING:
            adjustments['temporal_scope'] = 'narrowed'
            adjustments['temporal_resolution'] = 'increased'
            adjustments['historical_weight'] = 'reduced'
        
        return adjustments
    
    def _define_expected_outcomes(self, dissonance: DissonanceSignal, 
                                strategy: CorrectionStrategy) -> List[str]:
        """Define expected outcomes from correction."""
        base_outcomes = [f"reduced_{dissonance.dissonance_type.value}"]
        
        strategy_outcomes = {
            CorrectionStrategy.PARAMETER_ADJUSTMENT: ['improved_stability', 'better_consistency'],
            CorrectionStrategy.METHOD_SUBSTITUTION: ['increased_reliability', 'reduced_variance'],
            CorrectionStrategy.APPROACH_REVISION: ['fundamental_improvement', 'strategic_realignment'],
            CorrectionStrategy.TEMPORAL_REFRAMING: ['temporal_consistency', 'improved_4d_thinking']
        }
        
        return base_outcomes + strategy_outcomes.get(strategy, ['general_improvement'])
    
    def _define_success_metrics(self, dissonance: DissonanceSignal, 
                              strategy: CorrectionStrategy) -> Dict[str, float]:
        """Define metrics for measuring correction success."""
        metrics = {}
        
        if dissonance.dissonance_type == DissonanceType.LOW_CONFIDENCE:
            metrics['average_confidence'] = 0.8
            metrics['confidence_variance'] = 0.05
        elif dissonance.dissonance_type == DissonanceType.REPEATED_FAILURE:
            metrics['failure_rate'] = 0.1
            metrics['success_rate'] = 0.9
        elif dissonance.dissonance_type == DissonanceType.INCONSISTENT_RESULTS:
            metrics['result_consistency'] = 0.9
            metrics['variance_reduction'] = 0.7
        
        return metrics
    
    def _create_implementation_steps(self, strategy: CorrectionStrategy, 
                                   adjustments: Dict[str, Any]) -> List[str]:
        """Create step-by-step implementation plan."""
        steps = ['backup_current_state', 'validate_correction_plan']
        
        if strategy == CorrectionStrategy.PARAMETER_ADJUSTMENT:
            steps.extend(['adjust_parameters', 'test_adjustments', 'validate_improvements'])
        elif strategy == CorrectionStrategy.METHOD_SUBSTITUTION:
            steps.extend(['identify_alternative_methods', 'implement_substitution', 'compare_results'])
        elif strategy == CorrectionStrategy.APPROACH_REVISION:
            steps.extend(['analyze_current_approach', 'design_new_approach', 'implement_revision', 'validate_improvement'])
        
        steps.append('monitor_results')
        return steps
    
    def _plan_rollback_strategy(self, system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Plan rollback strategy in case correction fails."""
        return {
            'rollback_trigger': 'performance_degradation',
            'rollback_threshold': self.config['rollback_threshold'],
            'restore_state': system_state.copy(),
            'rollback_steps': ['halt_correction', 'restore_previous_state', 'analyze_failure']
        }
    
    def _estimate_effectiveness(self, dissonance: DissonanceSignal, 
                              strategy: CorrectionStrategy) -> float:
        """Estimate the effectiveness of the correction strategy."""
        base_effectiveness = 0.7
        
        # Adjust based on dissonance severity
        severity_adjustments = {
            ShiftSeverity.MINOR: 0.9,
            ShiftSeverity.MODERATE: 0.8,
            ShiftSeverity.MAJOR: 0.6,
            ShiftSeverity.CRITICAL: 0.4
        }
        
        # Adjust based on strategy appropriateness
        strategy_confidence = {
            CorrectionStrategy.PARAMETER_ADJUSTMENT: 0.8,
            CorrectionStrategy.METHOD_SUBSTITUTION: 0.7,
            CorrectionStrategy.APPROACH_REVISION: 0.6,
            CorrectionStrategy.TEMPORAL_REFRAMING: 0.75
        }
        
        effectiveness = base_effectiveness
        effectiveness *= severity_adjustments.get(dissonance.severity, 0.7)
        effectiveness *= strategy_confidence.get(strategy, 0.7)
        
        return min(1.0, effectiveness)

class MetacognitiveShiftProcessor:
    """
    Main processor implementing MetacognitiveshifT SPR capabilities.
    
    Orchestrates dissonance detection, correction planning, and adaptive learning
    to enable reactive meta-cognitive error correction.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the metacognitive shift processor."""
        self.config = config or self._get_default_config()
        self.detector = DissonanceDetector(config)
        self.planner = CorrectionPlanner(config)
        self.shift_history: List[ShiftResult] = []
        self.active_shifts: Dict[str, CorrectionPlan] = {}
        
        logger.info("MetacognitiveShiftProcessor initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for metacognitive processing."""
        return {
            'auto_correction_enabled': True,
            'max_concurrent_shifts': 3,
            'shift_timeout_minutes': 30,
            'learning_enabled': True,
            'monitoring_interval_seconds': 60
        }
    
    def process_metacognitive_shift(self, iar_stream: List[Dict[str, Any]], 
                                  system_state: Dict[str, Any]) -> List[ShiftResult]:
        """
        Main entry point for metacognitive shift processing.
        
        Detects dissonance, plans corrections, and executes adaptive responses.
        
        Args:
            iar_stream: Recent IAR reflection data
            system_state: Current system operational state
            
        Returns:
            List of shift results from processing
        """
        logger.info("Processing metacognitive shift")
        
        try:
            # Detect dissonance
            dissonance_signals = self.detector.detect_dissonance(iar_stream, system_state)
            
            shift_results = []
            
            for dissonance in dissonance_signals:
                # Plan correction
                correction_plan = self.planner.plan_correction(dissonance, system_state)
                
                # Execute correction if auto-correction is enabled
                if self.config['auto_correction_enabled']:
                    shift_result = self._execute_correction(dissonance, correction_plan, system_state)
                    shift_results.append(shift_result)
                else:
                    # Store for manual execution
                    shift_id = f"shift_{format_filename()}_{dissonance.dissonance_type.value}"
                    self.active_shifts[shift_id] = correction_plan
                    logger.info(f"Correction plan stored for manual execution: {shift_id}")
            
            # Learn from shift results
            if self.config['learning_enabled'] and shift_results:
                self._learn_from_shifts(shift_results)
            
            logger.info(f"Metacognitive shift processing complete: {len(shift_results)} shifts executed")
            return shift_results
            
        except Exception as e:
            logger.error(f"Error in metacognitive shift processing: {e}")
            return []
    
    def _execute_correction(self, dissonance: DissonanceSignal, 
                          correction_plan: CorrectionPlan, 
                          system_state: Dict[str, Any]) -> ShiftResult:
        """Execute a correction plan and measure results."""
        shift_id = f"shift_{format_filename()}_{dissonance.dissonance_type.value}"
        
        logger.info(f"Executing correction: {shift_id}")
        
        try:
            # Simulate correction execution
            # In a real implementation, this would interface with actual system components
            execution_status = "completed"
            outcomes_achieved = []
            performance_delta = {}
            lessons_learned = []
            
            # Simulate implementation of correction plan
            for step in correction_plan.implementation_steps:
                logger.debug(f"Executing step: {step}")
                # Simulate step execution
                if step == "adjust_parameters":
                    outcomes_achieved.append("parameters_adjusted")
                elif step == "test_adjustments":
                    outcomes_achieved.append("adjustments_tested")
                elif step == "validate_improvements":
                    outcomes_achieved.append("improvements_validated")
            
            # Simulate performance measurement
            for metric, target in correction_plan.success_metrics.items():
                # Simulate improvement (in real implementation, would measure actual metrics)
                current_value = system_state.get(metric, 0.5)
                improvement = min(target, current_value + 0.1)  # Simulate 10% improvement
                performance_delta[metric] = improvement - current_value
            
            # Calculate success score
            success_score = np.mean([
                1.0 if outcome in outcomes_achieved else 0.0 
                for outcome in correction_plan.expected_outcomes
            ])
            
            # Generate lessons learned
            if success_score > 0.8:
                lessons_learned.append(f"Strategy {correction_plan.correction_strategy.value} effective for {dissonance.dissonance_type.value}")
            else:
                lessons_learned.append(f"Strategy {correction_plan.correction_strategy.value} needs refinement for {dissonance.dissonance_type.value}")
            
            shift_result = ShiftResult(
                shift_id=shift_id,
                original_dissonance=dissonance,
                correction_plan=correction_plan,
                execution_status=execution_status,
                outcomes_achieved=outcomes_achieved,
                performance_delta=performance_delta,
                lessons_learned=lessons_learned,
                success_score=success_score
            )
            
            self.shift_history.append(shift_result)
            logger.info(f"Correction executed successfully: {shift_id} (success: {success_score:.3f})")
            return shift_result
            
        except Exception as e:
            logger.error(f"Error executing correction {shift_id}: {e}")
            return ShiftResult(
                shift_id=shift_id,
                original_dissonance=dissonance,
                correction_plan=correction_plan,
                execution_status="failed",
                outcomes_achieved=[],
                performance_delta={},
                lessons_learned=[f"Execution failed: {str(e)}"],
                success_score=0.0
            )
    
    def _learn_from_shifts(self, shift_results: List[ShiftResult]) -> None:
        """Learn from shift execution results to improve future corrections."""
        logger.info("Learning from metacognitive shift results")
        
        try:
            # Analyze successful strategies
            successful_shifts = [shift for shift in shift_results if shift.success_score > 0.7]
            failed_shifts = [shift for shift in shift_results if shift.success_score < 0.3]
            
            # Update strategy effectiveness estimates
            strategy_performance = {}
            for shift in self.shift_history[-20:]:  # Last 20 shifts
                strategy = shift.correction_plan.correction_strategy
                if strategy not in strategy_performance:
                    strategy_performance[strategy] = []
                strategy_performance[strategy].append(shift.success_score)
            
            # Log learning insights
            for strategy, scores in strategy_performance.items():
                avg_score = np.mean(scores)
                logger.info(f"Strategy {strategy.value} average success: {avg_score:.3f}")
            
            # Update planner configuration based on learning
            if hasattr(self.planner, 'update_effectiveness_estimates'):
                self.planner.update_effectiveness_estimates(strategy_performance)
            
        except Exception as e:
            logger.warning(f"Learning from shifts failed: {e}")
    
    def get_shift_analytics(self) -> Dict[str, Any]:
        """Get analytics on metacognitive shift performance."""
        if not self.shift_history:
            return {"message": "No shift history available"}
        
        recent_shifts = self.shift_history[-10:]
        
        analytics = {
            "total_shifts": len(self.shift_history),
            "recent_shifts": len(recent_shifts),
            "average_success_score": np.mean([shift.success_score for shift in recent_shifts]),
            "most_common_dissonance": self._get_most_common_dissonance(),
            "most_effective_strategy": self._get_most_effective_strategy(),
            "improvement_trend": self._calculate_improvement_trend()
        }
        
        return analytics
    
    def _get_most_common_dissonance(self) -> str:
        """Get the most commonly detected dissonance type."""
        if not self.shift_history:
            return "none"
        
        dissonance_counts = {}
        for shift in self.shift_history:
            dissonance_type = shift.original_dissonance.dissonance_type
            dissonance_counts[dissonance_type] = dissonance_counts.get(dissonance_type, 0) + 1
        
        return max(dissonance_counts, key=dissonance_counts.get).value if dissonance_counts else "none"
    
    def _get_most_effective_strategy(self) -> str:
        """Get the most effective correction strategy."""
        if not self.shift_history:
            return "none"
        
        strategy_scores = {}
        for shift in self.shift_history:
            strategy = shift.correction_plan.correction_strategy
            if strategy not in strategy_scores:
                strategy_scores[strategy] = []
            strategy_scores[strategy].append(shift.success_score)
        
        strategy_averages = {
            strategy: np.mean(scores) for strategy, scores in strategy_scores.items()
        }
        
        return max(strategy_averages, key=strategy_averages.get).value if strategy_averages else "none"
    
    def _calculate_improvement_trend(self) -> str:
        """Calculate trend in metacognitive shift effectiveness."""
        if len(self.shift_history) < 5:
            return "insufficient_data"
        
        recent_scores = [shift.success_score for shift in self.shift_history[-10:]]
        trend_slope = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
        
        if trend_slope > 0.02:
            return "improving"
        elif trend_slope < -0.02:
            return "declining"
        else:
            return "stable"
    
    def generate_iar_reflection(self, shift_results: List[ShiftResult]) -> Dict[str, Any]:
        """
        Generate IAR reflection for metacognitive shift processing.
        
        Implements the self-awareness requirement for all ArchE actions.
        """
        if not shift_results:
            return {
                "status": "completed",
                "confidence": 0.5,
                "potential_issues": ["no_shifts_executed"],
                "alignment_check": "medium",
                "tactical_resonance": 0.5,
                "crystallization_potential": "low",
                "timestamp": now_iso()
            }
        
        avg_success = np.mean([shift.success_score for shift in shift_results])
        
        potential_issues = []
        if avg_success < 0.5:
            potential_issues.append("low_correction_effectiveness")
        if any(shift.execution_status == "failed" for shift in shift_results):
            potential_issues.append("correction_execution_failures")
        
        return {
            "status": "completed",
            "confidence": avg_success,
            "potential_issues": potential_issues,
            "alignment_check": "high" if avg_success > 0.8 else "medium" if avg_success > 0.6 else "low",
            "tactical_resonance": avg_success,
            "crystallization_potential": "high" if avg_success > 0.8 and len(potential_issues) == 0 else "medium",
            "timestamp": now_iso(),
            "shifts_processed": len(shift_results),
            "average_success_score": avg_success,
            "corrections_applied": [shift.correction_plan.correction_strategy.value for shift in shift_results]
        }

# Factory function for easy integration
def create_metacognitive_shift_processor(config: Optional[Dict[str, Any]] = None) -> MetacognitiveShiftProcessor:
    """Factory function to create a configured metacognitive shift processor."""
    return MetacognitiveShiftProcessor(config)

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    processor = create_metacognitive_shift_processor()
    
    # Sample IAR stream with dissonance indicators
    sample_iar_stream = [
        {"confidence": 0.4, "status": "completed", "alignment_check": "low", "potential_issues": ["data_quality"]},
        {"confidence": 0.3, "status": "failed", "alignment_check": "low", "potential_issues": ["method_failure"]},
        {"confidence": 0.5, "status": "completed", "alignment_check": "medium", "potential_issues": []},
        {"confidence": 0.2, "status": "failed", "alignment_check": "low", "potential_issues": ["temporal_inconsistency"]},
        {"confidence": 0.4, "status": "completed", "alignment_check": "low", "potential_issues": ["strategy_mismatch"]}
    ]
    
    sample_system_state = {
        "current_objectives": ["improve_performance", "reduce_errors"],
        "confidence_threshold": 0.7,
        "validation_steps": 2
    }
    
    # Process metacognitive shift
    shift_results = processor.process_metacognitive_shift(sample_iar_stream, sample_system_state)
    analytics = processor.get_shift_analytics()
    iar_reflection = processor.generate_iar_reflection(shift_results)
    
    print("MetacognitiveshifT Processing Results:")
    print(f"Shifts Executed: {len(shift_results)}")
    for shift in shift_results:
        print(f"  {shift.shift_id}: {shift.correction_plan.correction_strategy.value} (success: {shift.success_score:.3f})")
    
    print(f"\nAnalytics: {analytics}")
    print(f"\nIAR Reflection: {iar_reflection}") 