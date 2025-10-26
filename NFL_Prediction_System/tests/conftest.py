#!/usr/bin/env python3
"""
Pytest fixtures for NFL Prediction System testing
"""

import pytest
import asyncio
from typing import Dict, Any, List
from faker import Faker
import json
import os
from datetime import datetime, timedelta

# Mock team data for testing
MOCK_TEAM_DATA = {
    "Kansas City Chiefs": {
        "offensive_efficiency": 0.85,
        "defensive_efficiency": 0.78,
        "special_teams_efficiency": 0.82,
        "home_advantage": 0.15,
        "current_form": 0.88,
        "injuries": 0.05
    },
    "Buffalo Bills": {
        "offensive_efficiency": 0.82,
        "defensive_efficiency": 0.75,
        "special_teams_efficiency": 0.79,
        "home_advantage": 0.12,
        "current_form": 0.85,
        "injuries": 0.08
    },
    "San Francisco 49ers": {
        "offensive_efficiency": 0.88,
        "defensive_efficiency": 0.82,
        "special_teams_efficiency": 0.85,
        "home_advantage": 0.18,
        "current_form": 0.90,
        "injuries": 0.03
    },
    "Dallas Cowboys": {
        "offensive_efficiency": 0.80,
        "defensive_efficiency": 0.77,
        "special_teams_efficiency": 0.78,
        "home_advantage": 0.14,
        "current_form": 0.83,
        "injuries": 0.10
    }
}

MOCK_WEATHER_DATA = {
    "temperature": 72,
    "wind_speed": 8,
    "condition": "clear",
    "precipitation": 0.0,
    "humidity": 45,
    "game_impact": "Ideal conditions for offensive play"
}

MOCK_GAME_DATA = {
    "game_id": "test_game_2023_1_1",
    "team1": "Kansas City Chiefs",
    "team2": "Buffalo Bills",
    "game_date": "2023-09-15",
    "home_team": "Chiefs",
    "team1_score": 35,
    "team2_score": 28
}

MOCK_PREDICTION_RECORD = {
    "game_id": "test_game_2023_1_1",
    "team1": "Kansas City Chiefs",
    "team2": "Buffalo Bills",
    "predicted_winner": "Kansas City Chiefs",
    "predicted_score_team1": 35,
    "predicted_score_team2": 28,
    "confidence": 0.78,
    "actual_winner": "Kansas City Chiefs",
    "actual_score_team1": 35,
    "actual_score_team2": 28,
    "prediction_date": "2023-09-15T10:00:00",
    "game_date": "2023-09-15",
    "was_correct": True
}

@pytest.fixture
def sample_team_data():
    """Provide sample team data for testing"""
    return MOCK_TEAM_DATA.copy()

@pytest.fixture
def sample_weather_data():
    """Provide sample weather data for testing"""
    return MOCK_WEATHER_DATA.copy()

@pytest.fixture
def sample_game_data():
    """Provide sample game data for testing"""
    return MOCK_GAME_DATA.copy()

@pytest.fixture
def sample_prediction_record():
    """Provide sample prediction record for testing"""
    return MOCK_PREDICTION_RECORD.copy()

@pytest.fixture
def mock_prediction_history():
    """Provide a mock prediction history for testing"""
    return [
        {
            "game_id": f"test_game_2023_1_{i}",
            "team1": "Kansas City Chiefs",
            "team2": "Buffalo Bills",
            "predicted_winner": "Kansas City Chiefs",
            "predicted_score_team1": 35,
            "predicted_score_team2": 28,
            "confidence": 0.78,
            "actual_winner": "Kansas City Chiefs",
            "actual_score_team1": 35,
            "actual_score_team2": 28,
            "prediction_date": "2023-09-15T10:00:00",
            "game_date": "2023-09-15",
            "was_correct": True
        }
        for i in range(1, 21)  # 20 games of mock data
    ]

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after each test"""
    yield
    # Clean up any test-generated files
    test_files = [
        "tests/data/predictions_history.json",
        "tests/data/strategist_recommendations.json",
        "tests/data/strategist_performance_history.json"
    ]
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)

@pytest.fixture
def test_data_directory():
    """Ensure test data directory exists"""
    test_data_dir = "tests/data"
    os.makedirs(test_data_dir, exist_ok=True)
    return test_data_dir
