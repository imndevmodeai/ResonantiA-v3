#!/usr/bin/env python3
"""
Unit tests for Master Strategist Agent functionality
"""

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from strategist_agent import (
    MasterStrategistAgent,
    Recommendation,
    RecommendationLevel,
    AnalysisType,
    PerformanceInsight
)


class TestMasterStrategistAgent:
    """Test the Master Strategist Agent functionality"""

    @pytest.fixture
    def strategist(self):
        """Create a strategist agent instance for testing"""
        agent = MasterStrategistAgent()
        # Use test-specific files
        agent.predictions_file = "tests/data/test_predictions.json"
        agent.recommendations_file = "tests/data/test_recommendations.json"
        agent.performance_history_file = "tests/data/test_performance_history.json"
        return agent

    def test_agent_initialization(self, strategist):
        """Test strategist agent initialization"""
        assert strategist.learning_iterations == 0
        assert len(strategist.previous_recommendations) == 0
        assert strategist.min_sample_size == 10
        assert strategist.confidence_calibration_threshold == 0.15

    @pytest.mark.asyncio
    async def test_analyze_performance_insufficient_data(self, strategist):
        """Test analysis with insufficient data"""
        result = await strategist.analyze_performance()

        assert result["status"] == "insufficient_data"
        assert "Need at least" in result["message"]
        assert result["analysis"] == "Data collection phase"

    @pytest.mark.asyncio
    async def test_analyze_performance_with_data(self, strategist, mock_prediction_history):
        """Test analysis with sufficient mock data"""
        # Save mock data to test file
        os.makedirs("tests/data", exist_ok=True)
        with open("tests/data/test_predictions.json", 'w') as f:
            json.dump(mock_prediction_history, f)

        result = await strategist.analyze_performance()

        assert "analysis_timestamp" in result
        assert "total_predictions_analyzed" in result
        assert result["total_predictions_analyzed"] == 20
        assert "analyses" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) >= 0

    def test_load_prediction_history(self, strategist, mock_prediction_history):
        """Test loading prediction history"""
        # Save mock data
        os.makedirs("tests/data", exist_ok=True)
        with open("tests/data/test_predictions.json", 'w') as f:
            json.dump(mock_prediction_history, f)

        history = strategist._load_prediction_history()

        assert isinstance(history, list)
        assert len(history) == 20
        assert all("game_id" in record for record in history)

    def test_calculate_performance_metrics_empty(self, strategist):
        """Test performance metrics with no data"""
        metrics = strategist._calculate_performance_metrics([])

        assert metrics.total_predictions == 0
        assert metrics.correct_predictions == 0
        assert metrics.accuracy == 0.0
        assert metrics.average_confidence == 0.0

    def test_calculate_performance_metrics_with_data(self, strategist, mock_prediction_history):
        """Test performance metrics calculation"""
        # Mock the load function to return our test data
        with patch.object(strategist, '_load_prediction_history', return_value=mock_prediction_history):
            metrics = strategist._calculate_performance_metrics(mock_prediction_history)

            assert metrics.total_predictions == 20
            assert metrics.correct_predictions == 20  # All mock data is correct
            assert metrics.accuracy == 1.0
            assert metrics.games_with_actual_results == 20

    def test_analyze_accuracy_patterns(self, strategist, mock_prediction_history):
        """Test accuracy pattern analysis"""
        analysis = strategist._analyze_accuracy_patterns(mock_prediction_history)

        assert "overall_accuracy" in analysis
        assert "total_completed_games" in analysis
        assert "confidence_accuracy" in analysis
        assert "margin_accuracy" in analysis
        assert analysis["total_completed_games"] == 20
        assert analysis["overall_accuracy"] == 1.0

    def test_analyze_confidence_calibration(self, strategist, mock_prediction_history):
        """Test confidence calibration analysis"""
        analysis = strategist._analyze_confidence_calibration(mock_prediction_history)

        assert "calibration_data" in analysis
        assert "overall_calibration_error" in analysis
        assert len(analysis["calibration_data"]) > 0

        # Check calibration data structure
        for data_point in analysis["calibration_data"]:
            assert "confidence_range" in data_point
            assert "predicted_probability" in data_point
            assert "actual_accuracy" in data_point
            assert "calibration_error" in data_point

    def test_analyze_temporal_patterns(self, strategist, mock_prediction_history):
        """Test temporal pattern analysis"""
        analysis = strategist._analyze_temporal_patterns(mock_prediction_history)

        assert "daily_performance" in analysis
        assert "total_days_analyzed" in analysis
        assert "best_accuracy_streak" in analysis
        assert "average_daily_accuracy" in analysis

        # Should have processed the mock data
        assert analysis["total_days_analyzed"] == 1  # All data is from same day in mock

    def test_analyze_systematic_bias(self, strategist, mock_prediction_history):
        """Test systematic bias analysis"""
        analysis = strategist._analyze_systematic_bias(mock_prediction_history)

        assert "team_bias_analysis" in analysis
        assert "total_teams_analyzed" in analysis
        assert isinstance(analysis["team_bias_analysis"], list)

    def test_generate_recommendations(self, strategist, mock_prediction_history):
        """Test recommendation generation"""
        # Create mock analyses
        analyses = {
            "accuracy_analysis": {"overall_accuracy": 0.8, "confidence_accuracy": {"high": 0.9, "medium": 0.7}},
            "confidence_calibration": {"overall_calibration_error": 0.2, "needs_calibration": True},
            "temporal_patterns": {"average_daily_accuracy": 0.75},
            "systematic_bias": {"team_bias_analysis": []}
        }

        recommendations = strategist._generate_recommendations(analyses, mock_prediction_history)

        assert isinstance(recommendations, list)
        # Should generate at least one recommendation based on calibration error
        assert len(recommendations) >= 1

        for rec in recommendations:
            assert isinstance(rec, Recommendation)
            assert rec.analysis_type in [t.value for t in AnalysisType]
            assert rec.level in [l.value for l in RecommendationLevel]
            assert rec.expected_impact >= 0.0
            assert rec.implementation_complexity in ["low", "medium", "high"]

    def test_calculate_overall_insights(self, strategist):
        """Test overall insights calculation"""
        analyses = {
            "accuracy_analysis": {"overall_accuracy": 0.85},
            "confidence_calibration": {"overall_calibration_error": 0.1},
            "temporal_patterns": {"average_daily_accuracy": 0.8}
        }

        insights = strategist._calculate_overall_insights(analyses)

        assert "improvement_potential" in insights
        assert "critical_issues_count" in insights
        assert "overall_health_score" in insights
        assert 0.0 <= insights["improvement_potential"] <= 1.0
        assert insights["overall_health_score"] >= 0.0

    def test_calculate_agent_confidence(self, strategist):
        """Test agent confidence calculation"""
        # Test with no recommendations
        confidence = strategist._calculate_agent_confidence([])
        assert confidence == 0.5  # Base confidence

        # Test with recommendations
        recommendations = [
            Recommendation(
                id="test_1",
                analysis_type=AnalysisType.ACCURACY_ANALYSIS,
                level=RecommendationLevel.HIGH,
                title="Test",
                description="Test",
                technical_details="Test",
                expected_impact=0.2,
                implementation_complexity="medium",
                code_changes_required=[],
                validation_method="Test",
                timestamp=datetime.now().isoformat()
            )
        ]

        confidence = strategist._calculate_agent_confidence(recommendations)
        assert 0.5 <= confidence <= 1.0

    def test_recommendation_creation(self):
        """Test recommendation object creation"""
        rec = Recommendation(
            id="test_rec_123",
            analysis_type=AnalysisType.CONFIDENCE_CALIBRATION,
            level=RecommendationLevel.HIGH,
            title="Implement Confidence Recalibration",
            description="Test description",
            technical_details="Technical details",
            expected_impact=0.15,
            implementation_complexity="medium",
            code_changes_required=["Change 1", "Change 2"],
            validation_method="A/B testing",
            timestamp=datetime.now().isoformat()
        )

        assert rec.id == "test_rec_123"
        assert rec.analysis_type == AnalysisType.CONFIDENCE_CALIBRATION
        assert rec.level == RecommendationLevel.HIGH
        assert rec.expected_impact == 0.15
        assert len(rec.code_changes_required) == 2

    @pytest.mark.asyncio
    async def test_get_implementation_guidance(self, strategist):
        """Test implementation guidance retrieval"""
        # Add a test recommendation
        test_rec = Recommendation(
            id="test_guidance_123",
            analysis_type=AnalysisType.ACCURACY_ANALYSIS,
            level=RecommendationLevel.MEDIUM,
            title="Test Guidance",
            description="Test",
            technical_details="Test",
            expected_impact=0.1,
            implementation_complexity="low",
            code_changes_required=["Step 1"],
            validation_method="Test validation",
            timestamp=datetime.now().isoformat()
        )
        strategist.previous_recommendations.append(test_rec)

        guidance = await strategist.get_implementation_guidance("test_guidance_123")

        assert "recommendation" in guidance
        assert "implementation_steps" in guidance
        assert "validation_criteria" in guidance
        assert "risk_assessment" in guidance
        assert "expected_timeline" in guidance

    @pytest.mark.asyncio
    async def test_get_implementation_guidance_not_found(self, strategist):
        """Test implementation guidance for non-existent recommendation"""
        guidance = await strategist.get_implementation_guidance("non_existent")

        assert guidance == {"error": "Recommendation not found"}

    def test_agent_state_persistence(self, strategist):
        """Test agent state save/load functionality"""
        # Add some test data
        strategist.learning_iterations = 5
        test_rec = Recommendation(
            id="persistence_test",
            analysis_type=AnalysisType.ACCURACY_ANALYSIS,
            level=RecommendationLevel.LOW,
            title="Persistence Test",
            description="Test",
            technical_details="Test",
            expected_impact=0.05,
            implementation_complexity="low",
            code_changes_required=[],
            validation_method="Test",
            timestamp=datetime.now().isoformat()
        )
        strategist.previous_recommendations.append(test_rec)

        # Save state
        strategist._save_agent_state()

        # Create new instance and load state
        new_strategist = MasterStrategistAgent()
        new_strategist.predictions_file = "tests/data/test_predictions.json"
        new_strategist.recommendations_file = "tests/data/test_recommendations.json"
        new_strategist.performance_history_file = "tests/data/test_performance_history.json"
        new_strategist._load_agent_state()

        assert new_strategist.learning_iterations == 5
        assert len(new_strategist.previous_recommendations) == 1
        assert new_strategist.previous_recommendations[0].id == "persistence_test"


class TestAdvancedAnalysisFeatures:
    """Test advanced analysis features of the strategist agent"""

    @pytest.fixture
    def loaded_strategist(self, mock_prediction_history):
        """Create strategist with loaded mock data"""
        strategist = MasterStrategistAgent()
        strategist.predictions_file = "tests/data/test_predictions.json"

        # Save mock data
        os.makedirs("tests/data", exist_ok=True)
        with open("tests/data/test_predictions.json", 'w') as f:
            json.dump(mock_prediction_history, f)

        return strategist

    @pytest.mark.asyncio
    async def test_comprehensive_analysis_workflow(self, loaded_strategist):
        """Test the complete analysis workflow"""
        result = await loaded_strategist.analyze_performance()

        # Verify comprehensive analysis structure
        assert "analysis_timestamp" in result
        assert "learning_iteration" in result
        assert result["learning_iteration"] == 1
        assert "analyses" in result
        assert "recommendations" in result
        assert "overall_insights" in result
        assert "agent_confidence" in result

        # Check analyses completeness
        analyses = result["analyses"]
        assert "accuracy_analysis" in analyses
        assert "confidence_calibration" in analyses
        assert "temporal_patterns" in analyses
        assert "systematic_bias" in analyses

        # Check insights
        insights = result["overall_insights"]
        assert "improvement_potential" in insights
        assert "critical_issues_count" in insights
        assert "overall_health_score" in insights

    def test_confidence_calibration_detailed(self, mock_prediction_history):
        """Test detailed confidence calibration with varied data"""
        strategist = MasterStrategistAgent()

        # Create varied confidence data
        varied_history = []
        for i, game in enumerate(mock_prediction_history[:12]):  # Use subset
            game_copy = game.copy()
            game_copy["confidence"] = 0.5 + (i * 0.04)  # Vary confidence from 0.5 to 0.9
            if i % 4 == 0:  # Make some incorrect
                game_copy["was_correct"] = False
            varied_history.append(game_copy)

        analysis = strategist._analyze_confidence_calibration(varied_history)

        assert len(analysis["calibration_data"]) >= 3  # Should have multiple calibration points
        assert analysis["overall_calibration_error"] >= 0.0

        # Check that calibration errors are calculated
        for data_point in analysis["calibration_data"]:
            assert data_point["calibration_error"] >= 0.0
            assert data_point["sample_size"] > 0

    def test_systematic_bias_detection(self, mock_prediction_history):
        """Test systematic bias detection with varied team data"""
        strategist = MasterStrategistAgent()

        # Add team-specific bias to mock data
        biased_history = []
        for game in mock_prediction_history[:10]:
            game_copy = game.copy()
            # Simulate bias toward certain teams
            if "Chiefs" in game["team1"]:
                game_copy["was_correct"] = True  # Chiefs always correct
            elif "Bills" in game["team2"]:
                game_copy["was_correct"] = False  # Bills often incorrect
            biased_history.append(game_copy)

        analysis = strategist._analyze_systematic_bias(biased_history)

        assert len(analysis["team_bias_analysis"]) >= 2
        assert analysis["total_teams_analyzed"] >= 2

        # Should detect some level of bias
        biased_teams = [team for team in analysis["team_bias_analysis"] if team["bias_level"] != "normal"]
        assert len(biased_teams) > 0

    def test_temporal_pattern_analysis(self, mock_prediction_history):
        """Test temporal pattern analysis with varied dates"""
        strategist = MasterStrategistAgent()

        # Create data with different dates
        temporal_history = []
        base_date = datetime(2023, 9, 15)

        for i, game in enumerate(mock_prediction_history[:15]):
            game_copy = game.copy()
            # Spread across different days
            game_date = base_date + timedelta(days=i//3)
            game_copy["prediction_date"] = game_date.isoformat()
            # Vary accuracy over time
            game_copy["was_correct"] = i % 5 != 0  # 80% accuracy
            temporal_history.append(game_copy)

        analysis = strategist._analyze_temporal_patterns(temporal_history)

        assert analysis["total_days_analyzed"] >= 3  # Should span multiple days
        assert len(analysis["daily_performance"]) >= 3
        assert analysis["average_daily_accuracy"] >= 0.75  # Based on our test data

        # Check daily performance structure
        for day_perf in analysis["daily_performance"]:
            assert "date" in day_perf
            assert "games" in day_perf
            assert "accuracy" in day_perf
            assert 0.0 <= day_perf["accuracy"] <= 1.0
