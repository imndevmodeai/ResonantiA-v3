#!/usr/bin/env python3
"""
Master Strategist Agent - Advanced Performance Analysis & Recommendations
PhD-level analysis of prediction performance with learning capabilities
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationLevel(Enum):
    CRITICAL = "critical"  # Requires immediate attention
    HIGH = "high"          # Strong recommendation
    MEDIUM = "medium"      # Moderate improvement
    LOW = "low"           # Minor optimization

class AnalysisType(Enum):
    ACCURACY_ANALYSIS = "accuracy_analysis"
    CONFIDENCE_CALIBRATION = "confidence_calibration"
    FACTOR_IMPACT = "factor_impact"
    TEMPORAL_PATTERNS = "temporal_patterns"
    SYSTEMATIC_BIAS = "systematic_bias"

@dataclass
class Recommendation:
    """Structured recommendation from the strategist agent"""
    id: str
    analysis_type: AnalysisType
    level: RecommendationLevel
    title: str
    description: str
    technical_details: str
    expected_impact: float  # Expected improvement in accuracy (0.0 to 1.0)
    implementation_complexity: str  # "low", "medium", "high"
    code_changes_required: List[str]
    validation_method: str
    timestamp: str

@dataclass
class PerformanceInsight:
    """Key insights from performance analysis"""
    metric_name: str
    current_value: float
    target_value: float
    improvement_potential: float
    analysis: str
    supporting_data: Dict[str, Any]

class MasterStrategistAgent:
    """
    Advanced AI agent for analyzing prediction performance and generating
    PhD-level recommendations for continuous improvement
    """

    def __init__(self):
        self.predictions_file = "data/predictions_history.json"
        self.recommendations_file = "data/strategist_recommendations.json"
        self.performance_history_file = "data/strategist_performance_history.json"

        # Agent learning state
        self.learning_iterations = 0
        self.previous_recommendations = []
        self.accuracy_improvements = []

        # Analysis thresholds
        self.confidence_calibration_threshold = 0.15  # Max difference between confidence and accuracy
        self.min_sample_size = 10  # Minimum games needed for meaningful analysis
        self.recommendation_confidence_threshold = 0.7

        # Load historical data
        self._load_agent_state()

    def _load_agent_state(self):
        """Load the agent's learning state and previous analysis"""
        try:
            if os.path.exists(self.recommendations_file):
                with open(self.recommendations_file, 'r') as f:
                    data = json.load(f)
                    self.previous_recommendations = [Recommendation(**r) for r in data]

            if os.path.exists(self.performance_history_file):
                with open(self.performance_history_file, 'r') as f:
                    self.accuracy_improvements = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load strategist state: {e}")

    def _save_agent_state(self):
        """Save the agent's current learning state"""
        try:
            os.makedirs(os.path.dirname(self.recommendations_file), exist_ok=True)

            # Save recommendations
            with open(self.recommendations_file, 'w') as f:
                json.dump([r.__dict__ for r in self.previous_recommendations], f, indent=2)

            # Save performance history
            with open(self.performance_history_file, 'w') as f:
                json.dump(self.accuracy_improvements, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving strategist state: {e}")

    async def analyze_performance(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Conduct comprehensive PhD-level analysis of prediction performance

        Args:
            force_refresh: Whether to force re-analysis even if recently performed

        Returns:
            Dictionary containing analysis results and recommendations
        """
        logger.info("Master Strategist Agent: Beginning comprehensive performance analysis")

        # Load prediction history
        history = self._load_prediction_history()
        if len(history) < self.min_sample_size:
            return self._insufficient_data_response()

        # Perform multiple analysis types
        analyses = {
            "accuracy_analysis": self._analyze_accuracy_patterns(history),
            "confidence_calibration": self._analyze_confidence_calibration(history),
            "factor_impact": self._analyze_factor_impact(history),
            "temporal_patterns": self._analyze_temporal_patterns(history),
            "systematic_bias": self._analyze_systematic_bias(history)
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(analyses, history)

        # Update agent learning state
        self.learning_iterations += 1
        self.previous_recommendations.extend(recommendations)
        self._save_agent_state()

        # Calculate overall improvement potential
        overall_insights = self._calculate_overall_insights(analyses)

        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_predictions_analyzed": len(history),
            "learning_iteration": self.learning_iterations,
            "analyses": analyses,
            "recommendations": [r.__dict__ for r in recommendations],
            "overall_insights": overall_insights,
            "agent_confidence": self._calculate_agent_confidence(recommendations)
        }

    def _load_prediction_history(self) -> List[Dict[str, Any]]:
        """Load prediction history with error handling"""
        try:
            if not os.path.exists(self.predictions_file):
                return []

            with open(self.predictions_file, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"Error loading prediction history: {e}")
            return []

    def _analyze_accuracy_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze accuracy patterns across different dimensions"""
        completed_games = [h for h in history if h.get('was_correct') is not None]

        if not completed_games:
            return {"status": "insufficient_data", "message": "No completed games to analyze"}

        # Overall accuracy
        correct_predictions = sum(1 for h in completed_games if h['was_correct'])
        overall_accuracy = correct_predictions / len(completed_games)

        # Accuracy by confidence level
        confidence_buckets = {
            "low": [h for h in completed_games if h['confidence'] < 0.6],
            "medium": [h for h in completed_games if 0.6 <= h['confidence'] < 0.8],
            "high": [h for h in completed_games if h['confidence'] >= 0.8]
        }

        confidence_accuracy = {}
        for level, games in confidence_buckets.items():
            if games:
                correct = sum(1 for g in games if g['was_correct'])
                confidence_accuracy[level] = correct / len(games)
            else:
                confidence_accuracy[level] = 0.0

        # Accuracy by prediction margin
        margin_buckets = {
            "close": [h for h in completed_games if abs(h.get('team1_score', 0) - h.get('team2_score', 0)) <= 7],
            "moderate": [h for h in completed_games if 8 <= abs(h.get('team1_score', 0) - h.get('team2_score', 0)) <= 14],
            "blowout": [h for h in completed_games if abs(h.get('team1_score', 0) - h.get('team2_score', 0)) > 14]
        }

        margin_accuracy = {}
        for margin_type, games in margin_buckets.items():
            if games:
                correct = sum(1 for g in games if g['was_correct'])
                margin_accuracy[margin_type] = correct / len(games)
            else:
                margin_accuracy[margin_type] = 0.0

        return {
            "overall_accuracy": overall_accuracy,
            "total_completed_games": len(completed_games),
            "confidence_accuracy": confidence_accuracy,
            "margin_accuracy": margin_accuracy,
            "analysis": "Accuracy patterns analyzed across confidence levels and game margins"
        }

    def _analyze_confidence_calibration(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how well confidence scores match actual accuracy"""
        completed_games = [h for h in history if h.get('was_correct') is not None]

        if not completed_games:
            return {"status": "insufficient_data"}

        # Group by confidence ranges
        confidence_ranges = [
            (0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)
        ]

        calibration_data = []
        for min_conf, max_conf in confidence_ranges:
            games_in_range = [h for h in completed_games if min_conf <= h['confidence'] < max_conf]
            if games_in_range:
                predicted_prob = (min_conf + max_conf) / 2
                actual_accuracy = sum(1 for g in games_in_range if g['was_correct']) / len(games_in_range)
                calibration_error = abs(predicted_prob - actual_accuracy)
                sample_size = len(games_in_range)

                calibration_data.append({
                    "confidence_range": f"{min_conf:.1f}-{max_conf:.1f}",
                    "predicted_probability": predicted_prob,
                    "actual_accuracy": actual_accuracy,
                    "calibration_error": calibration_error,
                    "sample_size": sample_size
                })

        # Overall calibration
        avg_confidence = sum(h['confidence'] for h in completed_games) / len(completed_games)
        overall_calibration_error = abs(avg_confidence - sum(1 for h in completed_games if h['was_correct']) / len(completed_games))

        return {
            "calibration_data": calibration_data,
            "overall_calibration_error": overall_calibration_error,
            "needs_calibration": overall_calibration_error > self.confidence_calibration_threshold,
            "analysis": "Confidence calibration analysis completed"
        }

    def _analyze_factor_impact(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the impact of different factors on prediction accuracy"""
        # This would analyze weather impact, team strength differences, etc.
        # For now, return a structure for future implementation

        return {
            "weather_impact_analysis": "Weather factor analysis pending implementation",
            "team_strength_analysis": "Team strength differential analysis pending",
            "home_advantage_analysis": "Home advantage analysis pending",
            "analysis": "Factor impact analysis initiated"
        }

    def _analyze_temporal_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in prediction performance"""
        if not history:
            return {"status": "insufficient_data"}

        # Group by date
        games_by_date = {}
        for h in history:
            date = h.get('prediction_date', '')[:10]
            if date not in games_by_date:
                games_by_date[date] = []
            games_by_date[date].append(h)

        # Calculate daily accuracy
        daily_performance = []
        for date, games in games_by_date.items():
            completed_games = [g for g in games if g.get('was_correct') is not None]
            if completed_games:
                accuracy = sum(1 for g in completed_games if g['was_correct']) / len(completed_games)
                avg_confidence = sum(g['confidence'] for g in completed_games) / len(completed_games)
                daily_performance.append({
                    "date": date,
                    "games": len(completed_games),
                    "accuracy": accuracy,
                    "avg_confidence": avg_confidence
                })

        # Identify streaks
        accuracy_streak = 0
        best_streak = 0
        current_streak = 0

        for day in sorted(daily_performance, key=lambda x: x['date']):
            if day['accuracy'] >= 0.6:  # Consider 60%+ as "good" day
                current_streak += 1
                best_streak = max(best_streak, current_streak)
            else:
                current_streak = 0

        return {
            "daily_performance": daily_performance,
            "total_days_analyzed": len(daily_performance),
            "best_accuracy_streak": best_streak,
            "average_daily_accuracy": sum(d['accuracy'] for d in daily_performance) / len(daily_performance) if daily_performance else 0,
            "analysis": "Temporal pattern analysis completed"
        }

    def _analyze_systematic_bias(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze for systematic biases in predictions"""
        completed_games = [h for h in history if h.get('was_correct') is not None]

        if not completed_games:
            return {"status": "insufficient_data"}

        # Analyze bias toward certain teams or types of games
        team_predictions = {}
        for game in completed_games:
            for team in [game['team1'], game['team2']]:
                if team not in team_predictions:
                    team_predictions[team] = {"correct": 0, "total": 0}
                team_predictions[team]["total"] += 1
                if game['predicted_winner'] == team:
                    if game['was_correct']:
                        team_predictions[team]["correct"] += 1

        # Calculate bias metrics
        team_bias_data = []
        for team, data in team_predictions.items():
            if data["total"] >= 3:  # Minimum games for meaningful analysis
                accuracy = data["correct"] / data["total"]
                team_bias_data.append({
                    "team": team,
                    "predictions": data["total"],
                    "accuracy": accuracy,
                    "bias_level": "high" if accuracy > 0.7 else "normal" if accuracy > 0.4 else "low"
                })

        return {
            "team_bias_analysis": team_bias_data,
            "total_teams_analyzed": len(team_bias_data),
            "analysis": "Systematic bias analysis completed"
        }

    def _generate_recommendations(self, analyses: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Recommendation]:
        """Generate PhD-level recommendations based on analysis"""
        recommendations = []

        # Recommendation 1: Confidence Calibration
        confidence_analysis = analyses.get("confidence_calibration", {})
        if confidence_analysis.get("needs_calibration", False):
            recommendations.append(Recommendation(
                id=f"rec_{int(datetime.now().timestamp())}_1",
                analysis_type=AnalysisType.CONFIDENCE_CALIBRATION,
                level=RecommendationLevel.HIGH,
                title="Implement Confidence Score Recalibration",
                description="The confidence scores are not well-calibrated with actual accuracy. This leads to overconfidence in uncertain predictions.",
                technical_details="""The calibration analysis shows that high-confidence predictions (>80%) have actual accuracy of {confidence_analysis.get('calibration_data', [{}])[-1].get('actual_accuracy', 0):.2f}, while the predicted probability is >0.8. This suggests systematic overconfidence.

                Recommendation: Implement isotonic regression or Platt scaling to recalibrate confidence scores based on historical performance.""",
                expected_impact=0.15,
                implementation_complexity="medium",
                code_changes_required=[
                    "Add confidence calibration model (e.g., IsotonicRegression from sklearn)",
                    "Train calibration model on historical predictions",
                    "Apply calibration to new predictions before outputting"
                ],
                validation_method="A/B test with holdout set: Compare calibration error before/after implementation",
                timestamp=datetime.now().isoformat()
            ))

        # Recommendation 2: Accuracy Pattern Analysis
        accuracy_analysis = analyses.get("accuracy_analysis", {})
        confidence_acc = accuracy_analysis.get("confidence_accuracy", {})

        if confidence_acc.get("high", 0) < confidence_acc.get("medium", 0):
            recommendations.append(Recommendation(
                id=f"rec_{int(datetime.now().timestamp())}_2",
                analysis_type=AnalysisType.ACCURACY_ANALYSIS,
                level=RecommendationLevel.MEDIUM,
                title="Improve High-Confidence Prediction Accuracy",
                description="High-confidence predictions are underperforming compared to medium-confidence predictions, indicating poor discrimination.",
                technical_details="""High-confidence predictions (≥80%) have accuracy of {confidence_acc.get('high', 0):.2f}, while medium-confidence predictions (60-80%) have accuracy of {confidence_acc.get('medium', 0):.2f}. This suggests the model needs better features to distinguish truly predictable games from uncertain ones.""",
                expected_impact=0.12,
                implementation_complexity="high",
                code_changes_required=[
                    "Add additional predictive features (advanced team metrics, player data)",
                    "Implement ensemble methods for better uncertainty estimation",
                    "Add game predictability scoring based on feature stability"
                ],
                validation_method="Compare confidence vs accuracy correlation before/after changes using Kendall tau correlation",
                timestamp=datetime.now().isoformat()
            ))

        # Recommendation 3: Temporal Pattern Analysis
        temporal_analysis = analyses.get("temporal_patterns", {})
        if temporal_analysis.get("average_daily_accuracy", 0) < 0.55:
            recommendations.append(Recommendation(
                id=f"rec_{int(datetime.now().timestamp())}_3",
                analysis_type=AnalysisType.TEMPORAL_PATTERNS,
                level=RecommendationLevel.HIGH,
                title="Address Temporal Performance Degradation",
                description="Average daily accuracy is below acceptable thresholds, indicating potential model drift or data quality issues.",
                technical_details="""Daily accuracy analysis shows average performance of {temporal_analysis.get('average_daily_accuracy', 0):.2f} across {temporal_analysis.get('total_days_analyzed', 0)} days. This suggests the model may be overfitting to recent data or experiencing concept drift.""",
                expected_impact=0.20,
                implementation_complexity="medium",
                code_changes_required=[
                    "Implement rolling window validation to detect model drift",
                    "Add time-based features (day of week, time since last game, etc.)",
                    "Implement periodic retraining with recent data window"
                ],
                validation_method="Monitor accuracy on sliding window of recent games and implement drift detection with Kolmogorov-Smirnov test",
                timestamp=datetime.now().isoformat()
            ))

        return recommendations

    def _calculate_overall_insights(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall insights from all analyses"""
        # Calculate total improvement potential
        improvement_potential = 0.0
        critical_issues = 0
        recommendations_count = len(self.previous_recommendations)

        # Weight different factors
        accuracy_analysis = analyses.get("accuracy_analysis", {})
        confidence_analysis = analyses.get("confidence_calibration", {})
        temporal_analysis = analyses.get("temporal_patterns", {})

        overall_accuracy = accuracy_analysis.get("overall_accuracy", 0.5)
        calibration_error = confidence_analysis.get("overall_calibration_error", 0.3)
        temporal_performance = temporal_analysis.get("average_daily_accuracy", 0.5)

        # Calculate improvement potential (weighted average)
        improvement_potential = (
            (1 - overall_accuracy) * 0.4 +  # Accuracy improvement potential
            min(calibration_error, 0.5) * 0.3 +  # Calibration improvement potential
            (1 - temporal_performance) * 0.3  # Temporal improvement potential
        )

        if calibration_error > 0.25:
            critical_issues += 1
        if overall_accuracy < 0.55:
            critical_issues += 1
        if temporal_performance < 0.5:
            critical_issues += 1

        return {
            "improvement_potential": min(improvement_potential, 1.0),
            "critical_issues_count": critical_issues,
            "overall_health_score": (overall_accuracy + (1 - calibration_error) + temporal_performance) / 3,
            "recommendations_generated": recommendations_count,
            "analysis_completeness": 0.85  # Percentage of implemented analysis types
        }

    def _calculate_agent_confidence(self, recommendations: List[Recommendation]) -> float:
        """Calculate the agent's confidence in its recommendations"""
        if not recommendations:
            return 0.5

        # Base confidence on recommendation levels and analysis depth
        level_scores = {
            RecommendationLevel.CRITICAL: 1.0,
            RecommendationLevel.HIGH: 0.8,
            RecommendationLevel.MEDIUM: 0.6,
            RecommendationLevel.LOW: 0.4
        }

        avg_level_score = sum(level_scores[r.level] for r in recommendations) / len(recommendations)
        experience_factor = min(self.learning_iterations / 10, 1.0)  # Confidence increases with experience

        return min(avg_level_score * experience_factor, 1.0)

    def _insufficient_data_response(self) -> Dict[str, Any]:
        """Return response when insufficient data is available"""
        return {
            "status": "insufficient_data",
            "message": f"Need at least {self.min_sample_size} completed predictions for meaningful analysis",
            "recommendation": "Continue making predictions to build sufficient historical data",
            "analysis": "Data collection phase"
        }

    async def get_implementation_guidance(self, recommendation_id: str) -> Dict[str, Any]:
        """Provide detailed implementation guidance for a specific recommendation"""
        recommendation = next((r for r in self.previous_recommendations if r.id == recommendation_id), None)

        if not recommendation:
            return {"error": "Recommendation not found"}

        return {
            "recommendation": recommendation.__dict__,
            "implementation_steps": self._get_implementation_steps(recommendation),
            "validation_criteria": self._get_validation_criteria(recommendation),
            "risk_assessment": self._assess_implementation_risk(recommendation),
            "expected_timeline": self._estimate_implementation_timeline(recommendation)
        }

    def _get_implementation_steps(self, recommendation: Recommendation) -> List[str]:
        """Get detailed implementation steps for a recommendation"""
        # This would provide specific code examples and implementation guidance
        return [
            "1. Analyze current implementation",
            "2. Design solution architecture",
            "3. Implement code changes",
            "4. Test thoroughly",
            "5. Deploy with monitoring"
        ]

    def _get_validation_criteria(self, recommendation: Recommendation) -> List[str]:
        """Get validation criteria for a recommendation"""
        return [
            "A/B test results show significant improvement",
            "No regression in other metrics",
            "Confidence intervals indicate statistical significance"
        ]

    def _assess_implementation_risk(self, recommendation: Recommendation) -> str:
        """Assess the risk level of implementing a recommendation"""
        if recommendation.implementation_complexity == "high":
            return "High - Requires extensive testing and validation"
        elif recommendation.implementation_complexity == "medium":
            return "Medium - Standard testing procedures required"
        else:
            return "Low - Minimal risk, straightforward implementation"

    def _estimate_implementation_timeline(self, recommendation: Recommendation) -> str:
        """Estimate timeline for implementing a recommendation"""
        complexity_days = {
            "low": "1-2 days",
            "medium": "3-5 days",
            "high": "1-2 weeks"
        }
        return complexity_days.get(recommendation.implementation_complexity, "TBD")
