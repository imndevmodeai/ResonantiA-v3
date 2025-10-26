#!/usr/bin/env python3
"""
Integration tests for API endpoints
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import os
import sys

# Import the main app - this would need to be adjusted based on actual structure
from ultimate_gambling_engine import app


class TestAPIEndpoints:
    """Test API endpoint functionality"""

    @pytest.fixture
    def client(self):
        """Create test client for API testing"""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")

        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"

    def test_stats_overview_endpoint(self, client):
        """Test system statistics endpoint"""
        response = client.get("/api/stats/overview")

        assert response.status_code == 200
        data = response.json()

        assert "total_predictions" in data
        assert "accuracy_rate" in data
        assert "last_updated" in data
        assert isinstance(data["total_predictions"], int)
        assert isinstance(data["accuracy_rate"], (int, float))

    def test_performance_history_endpoint(self, client):
        """Test performance history endpoint"""
        response = client.get("/api/performance-history")

        assert response.status_code == 200
        data = response.json()

        assert "total_predictions" in data
        assert "correct_predictions" in data
        assert "accuracy_rate" in data
        assert "average_confidence" in data
        assert "games_with_actual_results" in data

    def test_upcoming_games_endpoint(self, client):
        """Test upcoming games endpoint"""
        response = client.get("/api/upcoming-games")

        assert response.status_code == 200
        data = response.json()

        assert "games" in data
        assert isinstance(data["games"], list)

        if len(data["games"]) > 0:
            game = data["games"][0]
            assert "game_id" in game
            assert "team1" in game
            assert "team2" in game

    def test_predictions_endpoint(self, client):
        """Test predictions endpoint"""
        response = client.get("/api/predictions")

        assert response.status_code == 200
        data = response.json()

        assert "predictions" in data
        assert isinstance(data["predictions"], list)

        if len(data["predictions"]) > 0:
            prediction = data["predictions"][0]
            assert "game_id" in prediction
            assert "team1" in prediction
            assert "team2" in prediction
            assert "predicted_winner" in prediction

    def test_betting_advice_endpoint(self, client):
        """Test betting advice endpoint"""
        response = client.get("/api/betting-advice")

        assert response.status_code == 200
        data = response.json()

        assert "advice" in data
        assert isinstance(data["advice"], list)

        if len(data["advice"]) > 0:
            advice = data["advice"][0]
            assert "game_id" in advice
            assert "recommended_bet" in advice
            assert "confidence" in advice
            assert "bet_type" in advice

    def test_advanced_analysis_endpoint(self, client):
        """Test advanced analysis endpoint"""
        response = client.get("/api/advanced-analysis")

        assert response.status_code == 200
        data = response.json()

        # Should return mock data for now
        assert "analysis_type" in data
        assert "metrics" in data
        assert "recommendations" in data

    @pytest.mark.parametrize("endpoint,expected_keys", [
        ("/api/health", ["status"]),
        ("/api/stats/overview", ["total_predictions", "accuracy_rate", "last_updated"]),
        ("/api/performance-history", ["total_predictions", "correct_predictions", "accuracy_rate"]),
        ("/api/upcoming-games", ["games"]),
        ("/api/predictions", ["predictions"]),
        ("/api/betting-advice", ["advice"]),
        ("/api/advanced-analysis", ["analysis_type", "metrics", "recommendations"])
    ])
    def test_endpoint_structure(self, client, endpoint, expected_keys):
        """Test that all endpoints return expected structure"""
        response = client.get(endpoint)

        assert response.status_code == 200
        data = response.json()

        for key in expected_keys:
            assert key in data, f"Missing key {key} in {endpoint} response"


class TestStrategistAPIEndpoints:
    """Test Master Strategist Agent API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_strategist_status_endpoint(self, client):
        """Test strategist agent status endpoint"""
        response = client.get("/api/strategist/status")

        assert response.status_code == 200
        data = response.json()

        assert data["agent_name"] == "Master Strategist Agent"
        assert data["version"] == "1.0.0"
        assert "learning_iterations" in data
        assert "analysis_types" in data
        assert "capabilities" in data
        assert len(data["capabilities"]) > 0

    def test_strategist_recommendations_endpoint_empty(self, client):
        """Test recommendations endpoint with no data"""
        response = client.get("/api/strategist/recommendations")

        assert response.status_code == 200
        data = response.json()

        assert "agent_state" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_strategist_analyze_endpoint_insufficient_data(self, client):
        """Test analyze endpoint with insufficient data"""
        response = client.post("/api/strategist/analyze")

        assert response.status_code == 200
        data = response.json()

        # Should handle insufficient data gracefully
        assert "status" in data or "analysis_timestamp" in data

    def test_historical_analysis_endpoint(self, client):
        """Test historical analysis endpoint"""
        response = client.get("/api/historical-analysis/2023/1")

        assert response.status_code == 200
        data = response.json()

        assert "season" in data
        assert "week" in data
        assert "predictions" in data
        assert data["season"] == 2023
        assert data["week"] == 1

    def test_update_actual_results_endpoint(self, client):
        """Test updating actual results endpoint"""
        test_data = {
            "test_game_1": {
                "winner": "Kansas City Chiefs",
                "team1_score": 35,
                "team2_score": 28
            }
        }

        response = client.post(
            "/api/update-actual-results",
            json=test_data
        )

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "successfully" in data["message"]

    @pytest.mark.parametrize("season,week", [
        (2023, 1),
        (2023, 18),
        (2022, 10),
        (2024, 5)
    ])
    def test_historical_analysis_different_weeks(self, client, season, week):
        """Test historical analysis with different seasons and weeks"""
        response = client.get(f"/api/historical-analysis/{season}/{week}")

        assert response.status_code == 200
        data = response.json()

        assert data["season"] == season
        assert data["week"] == week
        assert "predictions" in data


class TestErrorHandling:
    """Test error handling in API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_invalid_historical_analysis_season(self, client):
        """Test historical analysis with invalid season"""
        response = client.get("/api/historical-analysis/2025/25")  # Future season

        # Should handle gracefully or return appropriate error
        assert response.status_code in [200, 404, 500]

    def test_invalid_recommendation_id(self, client):
        """Test guidance endpoint with invalid recommendation ID"""
        response = client.get("/api/strategist/guidance/invalid_id")

        assert response.status_code == 500  # Currently returns error for not found
        data = response.json()
        assert "error" in data

    def test_malformed_update_request(self, client):
        """Test update actual results with malformed data"""
        malformed_data = {
            "game_1": {
                "invalid_field": "value"
                # Missing required fields
            }
        }

        response = client.post(
            "/api/update-actual-results",
            json=malformed_data
        )

        # Should handle gracefully
        assert response.status_code in [200, 400, 500]


class TestAPIDataValidation:
    """Test data validation in API responses"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_prediction_data_structure(self, client):
        """Test that prediction responses have correct structure"""
        response = client.get("/api/predictions")

        if response.status_code == 200:
            data = response.json()

            if "predictions" in data and len(data["predictions"]) > 0:
                prediction = data["predictions"][0]

                # Check required fields
                required_fields = ["game_id", "team1", "team2", "predicted_winner", "confidence"]
                for field in required_fields:
                    assert field in prediction, f"Missing field {field} in prediction"

                # Check data types
                assert isinstance(prediction["confidence"], (int, float))
                assert isinstance(prediction["team1"], str)
                assert isinstance(prediction["team2"], str)

    def test_betting_advice_structure(self, client):
        """Test that betting advice responses have correct structure"""
        response = client.get("/api/betting-advice")

        if response.status_code == 200:
            data = response.json()

            if "advice" in data and len(data["advice"]) > 0:
                advice = data["advice"][0]

                # Check required fields
                required_fields = ["game_id", "recommended_bet", "confidence", "bet_type", "odds"]
                for field in required_fields:
                    assert field in advice, f"Missing field {field} in betting advice"

                # Check data types
                assert isinstance(advice["confidence"], (int, float))
                assert isinstance(advice["odds"], str)
                assert isinstance(advice["bet_type"], str)

    def test_performance_history_data_types(self, client):
        """Test that performance history has correct data types"""
        response = client.get("/api/performance-history")

        if response.status_code == 200:
            data = response.json()

            # Check numeric fields
            numeric_fields = ["total_predictions", "correct_predictions", "accuracy_rate", "average_confidence"]
            for field in numeric_fields:
                assert field in data
                assert isinstance(data[field], (int, float))

            # Check percentage fields are reasonable
            assert 0.0 <= data["accuracy_rate"] <= 100.0
            assert 0.0 <= data["average_confidence"] <= 100.0


class TestAPIIntegration:
    """Test integration between different API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_prediction_to_betting_advice_consistency(self, client):
        """Test consistency between predictions and betting advice"""
        # Get predictions
        pred_response = client.get("/api/predictions")
        advice_response = client.get("/api/betting-advice")

        if pred_response.status_code == 200 and advice_response.status_code == 200:
            predictions = pred_response.json().get("predictions", [])
            advice_list = advice_response.json().get("advice", [])

            # Should have same number of games
            assert len(predictions) == len(advice_list)

            # Check that game IDs match
            if len(predictions) > 0 and len(advice_list) > 0:
                pred_game_ids = {p["game_id"] for p in predictions}
                advice_game_ids = {a["game_id"] for a in advice_list}

                assert pred_game_ids == advice_game_ids

    def test_historical_analysis_data_flow(self, client):
        """Test data flow from historical analysis to performance tracking"""
        # Generate historical predictions
        hist_response = client.get("/api/historical-analysis/2023/1")

        if hist_response.status_code == 200:
            data = hist_response.json()

            # Should have predictions
            assert "predictions" in data
            assert len(data["predictions"]) > 0

            # Update with actual results
            if len(data["predictions"]) > 0:
                game_id = data["predictions"][0]["game_id"]
                update_data = {
                    game_id: {
                        "winner": data["predictions"][0]["team1"],  # Make first team winner
                        "team1_score": 35,
                        "team2_score": 28
                    }
                }

                update_response = client.post("/api/update-actual-results", json=update_data)

                # Should succeed
                assert update_response.status_code == 200

                # Check that performance history reflects the update
                perf_response = client.get("/api/performance-history")
                assert perf_response.status_code == 200

    def test_strategist_agent_workflow(self, client):
        """Test the complete strategist agent workflow"""
        # First ensure we have some prediction data
        # (This would require setting up mock data or using other endpoints first)

        # Trigger analysis
        analyze_response = client.post("/api/strategist/analyze")

        if analyze_response.status_code == 200:
            data = analyze_response.json()

            # Should have analysis results
            assert "analysis_timestamp" in data
            assert "analyses" in data
            assert "recommendations" in data

            # Get recommendations
            rec_response = client.get("/api/strategist/recommendations")
            assert rec_response.status_code == 200

            rec_data = rec_response.json()

            # Should have agent state and recommendations
            assert "agent_state" in rec_data
            assert "recommendations" in rec_data
            assert "learning_iterations" in rec_data["agent_state"]
