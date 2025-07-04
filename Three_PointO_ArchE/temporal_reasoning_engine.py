#!/usr/bin/env python3
"""
Temporal Reasoning Engine - Implementation of 4dthinkinG SPR
Operationalizes temporal reasoning capabilities for ArchE

This module implements the 4dthinkinG SPR capability, providing:
- Historical contextualization
- Temporal dynamics modeling  
- Future state analysis
- Emergence over time simulation
- Temporal causality identification
- Trajectory comparison
- Time horizon awareness

Part of ResonantiA Protocol v3.1-CA Implementation Resonance initiative.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemporalScope(Enum):
    """Enumeration of temporal analysis scopes."""
    SHORT_TERM = "short_term"      # Minutes to hours
    MEDIUM_TERM = "medium_term"    # Days to weeks  
    LONG_TERM = "long_term"        # Months to years
    STRATEGIC = "strategic"        # Years to decades

class TemporalAnalysisType(Enum):
    """Types of temporal analysis supported."""
    TREND_ANALYSIS = "trend_analysis"
    CAUSAL_LAG = "causal_lag"
    PATTERN_EMERGENCE = "pattern_emergence"
    TRAJECTORY_PROJECTION = "trajectory_projection"
    SYSTEM_EVOLUTION = "system_evolution"

@dataclass
class TemporalContext:
    """Container for temporal analysis context."""
    historical_data: List[Dict[str, Any]]
    current_state: Dict[str, Any]
    time_horizon: TemporalScope
    analysis_type: TemporalAnalysisType
    key_variables: List[str]
    temporal_resolution: str = "daily"  # hourly, daily, weekly, monthly
    confidence_threshold: float = 0.7

@dataclass 
class TemporalInsight:
    """Container for temporal analysis results."""
    insight_type: TemporalAnalysisType
    temporal_scope: TemporalScope
    key_findings: List[str]
    confidence: float
    evidence: Dict[str, Any]
    projections: Optional[Dict[str, Any]] = None
    causal_relationships: Optional[List[Dict[str, Any]]] = None
    emergence_patterns: Optional[List[Dict[str, Any]]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class TemporalTrajectory:
    """Container for trajectory analysis results."""
    trajectory_id: str
    start_state: Dict[str, Any]
    projected_states: List[Dict[str, Any]]
    confidence_intervals: List[Dict[str, Any]]
    key_transition_points: List[Dict[str, Any]]
    uncertainty_factors: List[str]
    temporal_resolution: str
    projection_horizon: str

class TemporalAnalyzer(ABC):
    """Abstract base class for temporal analysis components."""
    
    @abstractmethod
    def analyze(self, context: TemporalContext) -> TemporalInsight:
        """Perform temporal analysis on the given context."""
        pass

class HistoricalContextualizer(TemporalAnalyzer):
    """Analyzes historical patterns and context."""
    
    def analyze(self, context: TemporalContext) -> TemporalInsight:
        """Analyze historical patterns and trends."""
        logger.info("Performing historical contextualization")
        
        try:
            findings = []
            evidence = {}
            confidence = 0.0
            
            if not context.historical_data:
                return TemporalInsight(
                    insight_type=TemporalAnalysisType.TREND_ANALYSIS,
                    temporal_scope=context.time_horizon,
                    key_findings=["No historical data available"],
                    confidence=0.0,
                    evidence={"data_points": 0}
                )
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(context.historical_data)
            
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                
                # Analyze trends for key variables
                for variable in context.key_variables:
                    if variable in df.columns:
                        trend_analysis = self._analyze_trend(df, variable)
                        findings.append(f"{variable}: {trend_analysis['description']}")
                        evidence[f"{variable}_trend"] = trend_analysis
                
                # Calculate overall confidence
                confidence = min(1.0, len(df) / 100.0)  # More data = higher confidence
                confidence *= 0.8 if len(context.key_variables) > 0 else 0.5
                
                # Identify patterns
                patterns = self._identify_patterns(df, context.key_variables)
                if patterns:
                    findings.extend([f"Pattern: {p}" for p in patterns])
                    evidence['patterns'] = patterns
                    confidence += 0.1
                
            return TemporalInsight(
                insight_type=TemporalAnalysisType.TREND_ANALYSIS,
                temporal_scope=context.time_horizon,
                key_findings=findings,
                confidence=min(1.0, confidence),
                evidence=evidence
            )
            
        except Exception as e:
            logger.error(f"Error in historical contextualization: {e}")
            return TemporalInsight(
                insight_type=TemporalAnalysisType.TREND_ANALYSIS,
                temporal_scope=context.time_horizon,
                key_findings=[f"Analysis failed: {str(e)}"],
                confidence=0.0,
                evidence={"error": str(e)}
            )
    
    def _analyze_trend(self, df: pd.DataFrame, variable: str) -> Dict[str, Any]:
        """Analyze trend for a specific variable."""
        try:
            values = df[variable].dropna()
            if len(values) < 2:
                return {"description": "insufficient_data", "direction": "unknown", "strength": 0.0}
            
            # Calculate trend using linear regression
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            
            # Determine trend direction and strength
            if abs(slope) < 0.01:
                direction = "stable"
            elif slope > 0:
                direction = "increasing"
            else:
                direction = "decreasing"
            
            # Calculate R-squared for trend strength
            y_pred = slope * x + intercept
            ss_res = np.sum((values - y_pred) ** 2)
            ss_tot = np.sum((values - np.mean(values)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            return {
                "description": f"{direction} trend (R²={r_squared:.3f})",
                "direction": direction,
                "strength": r_squared,
                "slope": slope,
                "recent_value": float(values.iloc[-1]),
                "change_rate": slope
            }
            
        except Exception as e:
            return {"description": f"trend_analysis_error: {str(e)}", "direction": "error", "strength": 0.0}
    
    def _identify_patterns(self, df: pd.DataFrame, variables: List[str]) -> List[str]:
        """Identify recurring patterns in the data."""
        patterns = []
        
        try:
            # Look for cyclical patterns
            for variable in variables:
                if variable in df.columns:
                    values = df[variable].dropna()
                    if len(values) > 10:
                        # Simple pattern detection using autocorrelation
                        autocorr = np.correlate(values, values, mode='full')
                        autocorr = autocorr[autocorr.size // 2:]
                        
                        # Find peaks in autocorrelation (indicating cycles)
                        if len(autocorr) > 3:
                            peaks = []
                            for i in range(1, len(autocorr) - 1):
                                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                                    if autocorr[i] > 0.3 * autocorr[0]:  # Significant correlation
                                        peaks.append(i)
                            
                            if peaks:
                                patterns.append(f"{variable} shows cyclical pattern (period ~{peaks[0]} units)")
            
        except Exception as e:
            logger.warning(f"Pattern identification failed: {e}")
        
        return patterns

class FutureStateAnalyzer(TemporalAnalyzer):
    """Projects future states based on current trends and patterns."""
    
    def analyze(self, context: TemporalContext) -> TemporalInsight:
        """Analyze potential future states."""
        logger.info("Performing future state analysis")
        
        try:
            findings = []
            evidence = {}
            projections = {}
            confidence = 0.0
            
            if not context.historical_data:
                return TemporalInsight(
                    insight_type=TemporalAnalysisType.TRAJECTORY_PROJECTION,
                    temporal_scope=context.time_horizon,
                    key_findings=["No historical data for projection"],
                    confidence=0.0,
                    evidence={"data_points": 0}
                )
            
            # Convert to DataFrame
            df = pd.DataFrame(context.historical_data)
            
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                
                # Project each key variable
                for variable in context.key_variables:
                    if variable in df.columns:
                        projection = self._project_variable(df, variable, context.time_horizon)
                        projections[variable] = projection
                        findings.append(f"{variable} projected: {projection['summary']}")
                
                # Calculate confidence based on data quality and trend stability
                confidence = self._calculate_projection_confidence(df, context.key_variables)
                evidence['projection_confidence_factors'] = {
                    'data_points': len(df),
                    'variables_projected': len(projections),
                    'time_horizon': context.time_horizon.value
                }
            
            return TemporalInsight(
                insight_type=TemporalAnalysisType.TRAJECTORY_PROJECTION,
                temporal_scope=context.time_horizon,
                key_findings=findings,
                confidence=confidence,
                evidence=evidence,
                projections=projections
            )
            
        except Exception as e:
            logger.error(f"Error in future state analysis: {e}")
            return TemporalInsight(
                insight_type=TemporalAnalysisType.TRAJECTORY_PROJECTION,
                temporal_scope=context.time_horizon,
                key_findings=[f"Projection failed: {str(e)}"],
                confidence=0.0,
                evidence={"error": str(e)}
            )
    
    def _project_variable(self, df: pd.DataFrame, variable: str, time_horizon: TemporalScope) -> Dict[str, Any]:
        """Project a single variable into the future."""
        try:
            values = df[variable].dropna()
            if len(values) < 3:
                return {"summary": "insufficient_data", "projection": None, "confidence": 0.0}
            
            # Determine projection steps based on time horizon
            steps_map = {
                TemporalScope.SHORT_TERM: 24,    # 24 time units
                TemporalScope.MEDIUM_TERM: 168,  # ~1 week in hours or ~6 months in days
                TemporalScope.LONG_TERM: 365,    # 1 year
                TemporalScope.STRATEGIC: 1825    # 5 years
            }
            
            steps = steps_map.get(time_horizon, 100)
            
            # Simple linear projection (can be enhanced with more sophisticated models)
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            
            # Project future values
            future_x = np.arange(len(values), len(values) + steps)
            projected_values = slope * future_x + intercept
            
            # Calculate confidence intervals (simple approach)
            residuals = values - (slope * x + intercept)
            std_error = np.std(residuals)
            confidence_interval = 1.96 * std_error  # 95% CI
            
            current_value = float(values.iloc[-1])
            final_projected = float(projected_values[-1])
            change_percent = ((final_projected - current_value) / current_value * 100) if current_value != 0 else 0
            
            return {
                "summary": f"Change from {current_value:.2f} to {final_projected:.2f} ({change_percent:+.1f}%)",
                "projection": {
                    "current_value": current_value,
                    "projected_value": final_projected,
                    "change_percent": change_percent,
                    "confidence_interval": confidence_interval,
                    "trend_slope": slope
                },
                "confidence": min(1.0, len(values) / 50.0)  # More data = higher confidence
            }
            
        except Exception as e:
            return {"summary": f"projection_error: {str(e)}", "projection": None, "confidence": 0.0}
    
    def _calculate_projection_confidence(self, df: pd.DataFrame, variables: List[str]) -> float:
        """Calculate overall confidence in projections."""
        factors = []
        
        # Data quantity factor
        data_factor = min(1.0, len(df) / 100.0)
        factors.append(data_factor)
        
        # Variable coverage factor
        available_vars = sum(1 for var in variables if var in df.columns)
        coverage_factor = available_vars / len(variables) if variables else 0
        factors.append(coverage_factor)
        
        # Temporal consistency factor (based on data regularity)
        if 'timestamp' in df.columns and len(df) > 1:
            time_diffs = df['timestamp'].diff().dropna()
            consistency = 1.0 - (time_diffs.std() / time_diffs.mean()) if time_diffs.mean() > timedelta(0) else 0.5
            factors.append(min(1.0, consistency))
        
        return np.mean(factors) if factors else 0.0

class EmergenceAnalyzer(TemporalAnalyzer):
    """Analyzes emergent patterns and behaviors over time."""
    
    def analyze(self, context: TemporalContext) -> TemporalInsight:
        """Analyze emergence patterns over time."""
        logger.info("Performing emergence analysis")
        
        try:
            findings = []
            evidence = {}
            emergence_patterns = []
            confidence = 0.0
            
            if not context.historical_data:
                return TemporalInsight(
                    insight_type=TemporalAnalysisType.PATTERN_EMERGENCE,
                    temporal_scope=context.time_horizon,
                    key_findings=["No data for emergence analysis"],
                    confidence=0.0,
                    evidence={"data_points": 0}
                )
            
            df = pd.DataFrame(context.historical_data)
            
            if 'timestamp' in df.columns and len(df) > 10:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                
                # Analyze emergence for each variable
                for variable in context.key_variables:
                    if variable in df.columns:
                        emergence = self._detect_emergence(df, variable)
                        if emergence:
                            emergence_patterns.append(emergence)
                            findings.append(f"{variable}: {emergence['description']}")
                
                # Look for cross-variable emergence
                if len(context.key_variables) > 1:
                    cross_emergence = self._detect_cross_variable_emergence(df, context.key_variables)
                    if cross_emergence:
                        emergence_patterns.extend(cross_emergence)
                        findings.extend([e['description'] for e in cross_emergence])
                
                confidence = min(1.0, len(emergence_patterns) / 3.0)  # More patterns = higher confidence
                evidence['emergence_detection_method'] = 'statistical_analysis'
                evidence['data_points'] = len(df)
                evidence['variables_analyzed'] = context.key_variables
            
            return TemporalInsight(
                insight_type=TemporalAnalysisType.PATTERN_EMERGENCE,
                temporal_scope=context.time_horizon,
                key_findings=findings if findings else ["No significant emergence patterns detected"],
                confidence=confidence,
                evidence=evidence,
                emergence_patterns=emergence_patterns
            )
            
        except Exception as e:
            logger.error(f"Error in emergence analysis: {e}")
            return TemporalInsight(
                insight_type=TemporalAnalysisType.PATTERN_EMERGENCE,
                temporal_scope=context.time_horizon,
                key_findings=[f"Emergence analysis failed: {str(e)}"],
                confidence=0.0,
                evidence={"error": str(e)}
            )
    
    def _detect_emergence(self, df: pd.DataFrame, variable: str) -> Optional[Dict[str, Any]]:
        """Detect emergence patterns in a single variable."""
        try:
            values = df[variable].dropna()
            if len(values) < 10:
                return None
            
            # Look for phase transitions (sudden changes in behavior)
            # Calculate rolling statistics to detect regime changes
            window = max(3, len(values) // 10)
            rolling_mean = values.rolling(window=window).mean()
            rolling_std = values.rolling(window=window).std()
            
            # Detect significant changes in variance (emergence indicator)
            std_changes = rolling_std.diff().abs()
            significant_changes = std_changes > (2 * std_changes.std())
            
            if significant_changes.any():
                change_points = df.loc[significant_changes[significant_changes].index, 'timestamp'].tolist()
                return {
                    'variable': variable,
                    'pattern_type': 'variance_shift',
                    'description': f"Emergence detected: variance shift at {len(change_points)} points",
                    'change_points': [t.isoformat() for t in change_points[:3]],  # Top 3
                    'confidence': min(1.0, len(change_points) / 5.0)
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Emergence detection failed for {variable}: {e}")
            return None
    
    def _detect_cross_variable_emergence(self, df: pd.DataFrame, variables: List[str]) -> List[Dict[str, Any]]:
        """Detect emergence patterns across multiple variables."""
        patterns = []
        
        try:
            # Look for correlation emergence (variables becoming more/less correlated over time)
            for i, var1 in enumerate(variables):
                for var2 in variables[i+1:]:
                    if var1 in df.columns and var2 in df.columns:
                        correlation_pattern = self._analyze_correlation_evolution(df, var1, var2)
                        if correlation_pattern:
                            patterns.append(correlation_pattern)
            
        except Exception as e:
            logger.warning(f"Cross-variable emergence detection failed: {e}")
        
        return patterns
    
    def _analyze_correlation_evolution(self, df: pd.DataFrame, var1: str, var2: str) -> Optional[Dict[str, Any]]:
        """Analyze how correlation between two variables evolves over time."""
        try:
            if len(df) < 20:
                return None
            
            # Calculate rolling correlation
            window = max(10, len(df) // 5)
            rolling_corr = df[var1].rolling(window=window).corr(df[var2])
            
            # Look for significant changes in correlation
            corr_changes = rolling_corr.diff().abs()
            if corr_changes.max() > 0.3:  # Significant correlation change
                return {
                    'pattern_type': 'correlation_emergence',
                    'description': f"Correlation between {var1} and {var2} evolved significantly",
                    'variables': [var1, var2],
                    'max_correlation_change': float(corr_changes.max()),
                    'final_correlation': float(rolling_corr.iloc[-1]) if not rolling_corr.isna().iloc[-1] else 0.0,
                    'confidence': min(1.0, corr_changes.max())
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Correlation evolution analysis failed: {e}")
            return None

class TemporalReasoningEngine:
    """
    Main engine implementing 4dthinkinG SPR capabilities.
    
    Integrates all temporal analysis components to provide comprehensive
    temporal reasoning for ArchE system.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the temporal reasoning engine."""
        self.config = config or self._get_default_config()
        self.analyzers = {
            'historical': HistoricalContextualizer(),
            'future': FutureStateAnalyzer(),
            'emergence': EmergenceAnalyzer()
        }
        self.analysis_history: List[TemporalInsight] = []
        
        logger.info("TemporalReasoningEngine initialized with 4dthinkinG capabilities")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for temporal reasoning."""
        return {
            'default_confidence_threshold': 0.7,
            'max_projection_horizon': 365,
            'analysis_timeout': 300,  # seconds
            'enable_caching': True
        }
    
    def perform_temporal_analysis(self, context: TemporalContext) -> Dict[str, TemporalInsight]:
        """
        Perform comprehensive temporal analysis using 4dthinkinG approach.
        
        Args:
            context: TemporalContext containing analysis parameters
            
        Returns:
            Dictionary of insights from different temporal analyzers
        """
        logger.info(f"Starting 4dthinkinG analysis: {context.analysis_type.value}")
        
        insights = {}
        
        try:
            # Historical contextualization
            insights['historical'] = self.analyzers['historical'].analyze(context)
            
            # Future state analysis
            insights['future'] = self.analyzers['future'].analyze(context)
            
            # Emergence analysis
            insights['emergence'] = self.analyzers['emergence'].analyze(context)
            
            # Store insights for temporal tracking
            for insight in insights.values():
                self.analysis_history.append(insight)
            
            logger.info("4dthinkinG analysis completed successfully")
            return insights
            
        except Exception as e:
            logger.error(f"Error in temporal analysis: {e}")
            raise
    
    def generate_temporal_trajectory(self, context: TemporalContext) -> TemporalTrajectory:
        """
        Generate a comprehensive temporal trajectory projection.
        
        Combines insights from all analyzers to create a unified trajectory.
        """
        logger.info("Generating temporal trajectory")
        
        try:
            # Perform comprehensive analysis
            insights = self.perform_temporal_analysis(context)
            
            # Extract projections from future analysis
            future_insight = insights.get('future')
            projections = future_insight.projections if future_insight and future_insight.projections else {}
            
            # Create trajectory states
            projected_states = []
            confidence_intervals = []
            
            if projections:
                # Create time series of projected states
                steps = 10  # Number of intermediate states
                for i in range(steps + 1):
                    state = {}
                    confidence = {}
                    
                    for variable, projection_data in projections.items():
                        if projection_data and projection_data.get('projection'):
                            current = projection_data['projection']['current_value']
                            final = projection_data['projection']['projected_value']
                            # Linear interpolation
                            value = current + (final - current) * (i / steps)
                            state[variable] = value
                            confidence[variable] = projection_data.get('confidence', 0.5)
                    
                    projected_states.append(state)
                    confidence_intervals.append(confidence)
            
            # Identify key transition points from emergence analysis
            emergence_insight = insights.get('emergence')
            transition_points = []
            if emergence_insight and emergence_insight.emergence_patterns:
                for pattern in emergence_insight.emergence_patterns:
                    if pattern.get('change_points'):
                        transition_points.extend([
                            {'timestamp': cp, 'pattern': pattern['pattern_type']}
                            for cp in pattern['change_points']
                        ])
            
            # Calculate overall uncertainty
            uncertainty_factors = []
            for insight in insights.values():
                if insight.confidence < context.confidence_threshold:
                    uncertainty_factors.append(f"low_confidence_{insight.insight_type.value}")
            
            trajectory = TemporalTrajectory(
                trajectory_id=f"traj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                start_state=context.current_state,
                projected_states=projected_states,
                confidence_intervals=confidence_intervals,
                key_transition_points=transition_points,
                uncertainty_factors=uncertainty_factors,
                temporal_resolution=context.temporal_resolution,
                projection_horizon=context.time_horizon.value
            )
            
            logger.info(f"Temporal trajectory generated: {len(projected_states)} states")
            return trajectory
            
        except Exception as e:
            logger.error(f"Error generating temporal trajectory: {e}")
            raise
    
    def generate_iar_reflection(self, insights: Dict[str, TemporalInsight]) -> Dict[str, Any]:
        """
        Generate IAR reflection for temporal reasoning analysis.
        
        Implements the self-awareness requirement for all ArchE actions.
        """
        overall_confidence = np.mean([insight.confidence for insight in insights.values()])
        
        potential_issues = []
        for name, insight in insights.items():
            if insight.confidence < 0.7:
                potential_issues.append(f"low_confidence_{name}_analysis")
            if "error" in insight.evidence:
                potential_issues.append(f"error_in_{name}_analysis")
        
        return {
            "status": "completed",
            "confidence": overall_confidence,
            "potential_issues": potential_issues,
            "alignment_check": "high" if overall_confidence > 0.8 else "medium" if overall_confidence > 0.6 else "low",
            "tactical_resonance": overall_confidence,
            "crystallization_potential": "high" if overall_confidence > 0.8 and len(potential_issues) == 0 else "medium",
            "timestamp": datetime.now().isoformat(),
            "analysis_types_completed": list(insights.keys()),
            "temporal_scope_analyzed": insights[list(insights.keys())[0]].temporal_scope.value if insights else "unknown"
        }

# Factory function for easy integration
def create_temporal_reasoning_engine(config: Optional[Dict[str, Any]] = None) -> TemporalReasoningEngine:
    """Factory function to create a configured temporal reasoning engine."""
    return TemporalReasoningEngine(config)

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    engine = create_temporal_reasoning_engine()
    
    # Sample temporal context for testing
    sample_data = [
        {"timestamp": "2024-01-01T00:00:00", "metric_a": 100, "metric_b": 50},
        {"timestamp": "2024-01-02T00:00:00", "metric_a": 105, "metric_b": 52},
        {"timestamp": "2024-01-03T00:00:00", "metric_a": 110, "metric_b": 55},
        {"timestamp": "2024-01-04T00:00:00", "metric_a": 108, "metric_b": 58},
        {"timestamp": "2024-01-05T00:00:00", "metric_a": 115, "metric_b": 60},
    ]
    
    context = TemporalContext(
        historical_data=sample_data,
        current_state={"metric_a": 115, "metric_b": 60},
        time_horizon=TemporalScope.MEDIUM_TERM,
        analysis_type=TemporalAnalysisType.TRAJECTORY_PROJECTION,
        key_variables=["metric_a", "metric_b"],
        temporal_resolution="daily"
    )
    
    # Perform temporal analysis
    insights = engine.perform_temporal_analysis(context)
    trajectory = engine.generate_temporal_trajectory(context)
    iar_reflection = engine.generate_iar_reflection(insights)
    
    print("4dthinkinG Temporal Analysis Results:")
    for name, insight in insights.items():
        print(f"\n{name.upper()} Analysis:")
        print(f"  Confidence: {insight.confidence:.3f}")
        print(f"  Key Findings: {insight.key_findings}")
    
    print(f"\nTemporal Trajectory:")
    print(f"  Trajectory ID: {trajectory.trajectory_id}")
    print(f"  Projected States: {len(trajectory.projected_states)}")
    print(f"  Uncertainty Factors: {trajectory.uncertainty_factors}")
    
    print(f"\nIAR Reflection: {iar_reflection}") 