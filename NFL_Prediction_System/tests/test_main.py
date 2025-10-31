#!/usr/bin/env python3
"""
Unit tests for core prediction functionality
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import os

# Import the functions to test (we'll need to extract them or test through the main module)
from ultimate_gambling_engine import (
    calculate_team_strength,
    generate_key_factors,
    calculate_weather_impact,
    perform_cfp_analysis,
    load_predictions_history,
    save_prediction_record,
    calculate_performance_metrics
)


class TestCorePredictionFunctions:
    """Test core prediction calculation functions"""

    def test_calculate_team_strength_with_valid_data(self, sample_team_data):
        """Test team strength calculation with valid team data"""
        team_data = sample_team_data["Kansas City Chiefs"]

        strength = calculate_team_strength(team_data)

        assert isinstance(strength, float)
        assert 0.0 <= strength <= 1.0
        # Chiefs should have high strength due to good stats
        assert strength > 0.7

    def test_calculate_team_strength_with_empty_data(self):
        """Test team strength calculation with empty data"""
        strength = calculate_team_strength({})
        assert strength == 0.5  # Default fallback

    def test_calculate_team_strength_with_none_data(self):
        """Test team strength calculation with None data"""
        strength = calculate_team_strength(None)
        assert strength == 0.5  # Default fallback

    def test_calculate_weather_impact_clear_conditions(self, sample_weather_data):
        """Test weather impact calculation for clear conditions"""
        impact = calculate_weather_impact(sample_weather_data)

        assert isinstance(impact, float)
        assert 0.0 <= impact <= 2.0
        # Clear conditions should have minimal impact
        assert 0.8 <= impact <= 1.2

    def test_calculate_weather_impact_bad_conditions(self):
        """Test weather impact calculation for bad weather"""
        bad_weather = {
            "temperature": 25,  # Very cold
            "wind_speed": 25,   # High wind
            "condition": "rain",
            "precipitation": 1.0,
            "humidity": 90
        }

        impact = calculate_weather_impact(bad_weather)

        assert isinstance(impact, float)
        assert impact < 0.8  # Should penalize bad weather

    def test_generate_key_factors(self, sample_team_data, sample_weather_data):
        """Test key factors generation"""
        team1_data = sample_team_data["Kansas City Chiefs"]
        team2_data = sample_team_data["Buffalo Bills"]
        weather = sample_weather_data
        margin_strength = 0.15

        factors = generate_key_factors(team1_data, team2_data, weather, margin_strength)

        assert isinstance(factors, list)
        assert len(factors) > 0
        # Should include weather and team-related factors
        weather_factors = [f for f in factors if "weather" in f.lower() or "condition" in f.lower()]
        assert len(weather_factors) > 0

    @pytest.mark.asyncio
    async def test_perform_cfp_analysis(self, sample_team_data):
        """Test CFP analysis with mock team data"""
        team1_data = sample_team_data["Kansas City Chiefs"]
        team2_data = sample_team_data["Buffalo Bills"]

        result = await perform_cfp_analysis("Chiefs", "Bills", team1_data, team2_data)

        assert isinstance(result, dict)
        assert "quantum_flux_difference" in result or "status" in result

    def test_load_predictions_history_nonexistent_file(self):
        """Test loading predictions from non-existent file"""
        if os.path.exists("tests/data/predictions_history.json"):
            os.remove("tests/data/predictions_history.json")

        history = load_predictions_history("tests/data/predictions_history.json")

        assert isinstance(history, list)
        assert len(history) == 0

    def test_save_and_load_prediction_record(self, sample_prediction_record, test_data_directory):
        """Test saving and loading prediction records"""
        record = sample_prediction_record.copy()
        record["game_id"] = "test_unique_game_id"

        # Save record
        save_prediction_record(record, "tests/data/predictions_history.json")

        # Load and verify
        history = load_predictions_history("tests/data/predictions_history.json")

        assert isinstance(history, list)
        assert len(history) == 1
        assert history[0]["game_id"] == "test_unique_game_id"

    def test_calculate_performance_metrics_empty_history(self):
        """Test performance metrics calculation with empty history"""
        metrics = calculate_performance_metrics("tests/data/empty_history.json")

        assert metrics.total_predictions == 0
        assert metrics.correct_predictions == 0
        assert metrics.accuracy == 0.0
        assert metrics.average_confidence == 0.0
        assert metrics.games_with_actual_results == 0

    def test_calculate_performance_metrics_with_data(self, mock_prediction_history):
        """Test performance metrics calculation with mock data"""
        # Save mock data to file
        os.makedirs("tests/data", exist_ok=True)
        with open("tests/data/test_history.json", 'w') as f:
            json.dump(mock_prediction_history, f)

        metrics = calculate_performance_metrics("tests/data/test_history.json")

        assert metrics.total_predictions == 20
        assert metrics.correct_predictions == 20  # All mock predictions are correct
        assert metrics.accuracy == 1.0
        assert metrics.games_with_actual_results == 20
        assert 0.75 <= metrics.average_confidence <= 0.85  # Based on mock confidence values

    @pytest.mark.parametrize("team_data,expected_range", [
        ({"offensive_efficiency": 0.9, "defensive_efficiency": 0.8, "special_teams_efficiency": 0.85}, (0.8, 1.0)),
        ({"offensive_efficiency": 0.5, "defensive_efficiency": 0.5, "special_teams_efficiency": 0.5}, (0.4, 0.6)),
        ({"offensive_efficiency": 0.0, "defensive_efficiency": 0.0, "special_teams_efficiency": 0.0}, (0.0, 0.2)),
    ])
    def test_calculate_team_strength_parametrized(self, team_data, expected_range):
        """Test team strength calculation with different efficiency levels"""
        strength = calculate_team_strength(team_data)

        assert isinstance(strength, float)
        assert expected_range[0] <= strength <= expected_range[1]


class TestPredictionIntegration:
    """Integration tests for prediction pipeline"""

    @pytest.mark.asyncio
    async def test_prediction_pipeline_integration(self, sample_game_data, sample_team_data, sample_weather_data):
        """Test the complete prediction pipeline"""
        game = sample_game_data.copy()

        # Mock the database responses
        with patch('ultimate_gambling_engine.team_database') as mock_db:
            mock_db.get_all_teams.return_value = sample_team_data

            # Mock weather function
            with patch('ultimate_gambling_engine.get_weather_forecast', return_value=sample_weather_data):
                # Note: We can't easily test the full pipeline without the main app context
                # This would require either extracting functions or using a test client
                pass

    def test_key_factors_generation_comprehensive(self, sample_team_data, sample_weather_data):
        """Test comprehensive key factors generation"""
        team1_data = sample_team_data["Kansas City Chiefs"]
        team2_data = sample_team_data["San Francisco 49ers"]  # Stronger team
        weather = sample_weather_data
        margin_strength = 0.05  # Close game

        factors = generate_key_factors(team1_data, team2_data, weather, margin_strength)

        assert isinstance(factors, list)
        assert len(factors) >= 3  # Should have multiple factors

        # Check for specific types of factors
        strength_factors = [f for f in factors if "strength" in f.lower() or "advantage" in f.lower()]
        weather_factors = [f for f in factors if "weather" in f.lower() or "condition" in f.lower()]

        assert len(strength_factors) > 0
        assert len(weather_factors) > 0


class TestErrorHandling:
    """Test error handling in core functions"""

    def test_calculate_team_strength_invalid_data(self):
        """Test team strength calculation with invalid data types"""
        invalid_data = {
            "offensive_efficiency": "invalid",
            "defensive_efficiency": None,
            "special_teams_efficiency": [0.8]
        }

        # Should handle invalid data gracefully
        strength = calculate_team_strength(invalid_data)
        assert isinstance(strength, float)
        assert 0.0 <= strength <= 1.0

    def test_calculate_weather_impact_missing_data(self):
        """Test weather impact calculation with missing data"""
        incomplete_weather = {"temperature": 72}  # Missing other fields

        impact = calculate_weather_impact(incomplete_weather)
        assert isinstance(impact, float)
        assert 0.0 <= impact <= 2.0

    def test_generate_key_factors_edge_cases(self, sample_team_data):
        """Test key factors generation with edge cases"""
        team1_data = {"offensive_efficiency": 1.0, "defensive_efficiency": 1.0}
        team2_data = {"offensive_efficiency": 0.0, "defensive_efficiency": 0.0}
        weather = {}
        margin_strength = 0.0

        factors = generate_key_factors(team1_data, team2_data, weather, margin_strength)

        assert isinstance(factors, list)
        assert len(factors) > 0  # Should still generate some factors
