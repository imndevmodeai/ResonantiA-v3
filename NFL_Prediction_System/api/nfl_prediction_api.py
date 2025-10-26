#!/usr/bin/env python3
"""
NFL Prediction System - FastAPI Backend
World-class NFL prediction API with real-time stats and CFP analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime
import logging

# Import our components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.nfl_prediction_core import NFLPredictionSystem, GamePrediction
from data.nfl_team_database import NFLTeamDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NFL Prediction System",
    description="World-class NFL predictions with quantum-inspired CFP analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
nfl_system = NFLPredictionSystem()
team_database = NFLTeamDatabase()

# Pydantic models
class GamePredictionRequest(BaseModel):
    team1: str
    team2: str
    game_context: Optional[Dict[str, Any]] = None

class TeamStatsResponse(BaseModel):
    team_name: str
    offensive_efficiency: float
    defensive_efficiency: float
    special_teams: float
    coaching: float
    injuries: float
    home_advantage: float
    momentum: float
    experience: float
    depth: float
    clutch_performance: float
    playoff_experience: float
    quarterback_rating: float
    running_game: float
    passing_game: float
    defense_rating: float
    turnover_margin: float
    red_zone_efficiency: float
    third_down_conversion: float
    time_of_possession: float
    penalty_discipline: float
    current_record: str
    recent_form: List[str]
    key_injuries: List[str]

class GamePredictionResponse(BaseModel):
    game_id: str
    team1: str
    team2: str
    predicted_winner: str
    predicted_score: str
    confidence: float
    margin: str
    total_points: int
    over_under: int
    key_factors: List[str]
    weather_impact: str
    injury_impact: str
    momentum_factor: str
    clutch_performance: str
    prediction_timestamp: datetime

class WeeklyPredictionsResponse(BaseModel):
    week: int
    predictions: List[GamePredictionResponse]
    total_games: int
    generated_at: datetime

# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NFL Prediction System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: white; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #00ff00; font-size: 2.5em; margin: 0; }
            .header p { color: #ccc; font-size: 1.2em; }
            .prediction-form { background: #2a2a2a; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            .form-group label { display: block; margin-bottom: 5px; color: #00ff00; font-weight: bold; }
            .form-group select, .form-group input { width: 100%; padding: 10px; border: 1px solid #555; border-radius: 5px; background: #333; color: white; }
            .form-group button { background: #00ff00; color: black; padding: 15px 30px; border: none; border-radius: 5px; font-size: 1.1em; cursor: pointer; font-weight: bold; }
            .form-group button:hover { background: #00cc00; }
            .results { background: #2a2a2a; padding: 30px; border-radius: 10px; margin-top: 20px; }
            .prediction-card { background: #333; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #00ff00; }
            .prediction-card h3 { color: #00ff00; margin-top: 0; }
            .prediction-card .score { font-size: 1.5em; font-weight: bold; color: #fff; }
            .prediction-card .confidence { color: #00ff00; font-weight: bold; }
            .prediction-card .factors { color: #ccc; }
            .loading { text-align: center; color: #00ff00; font-size: 1.2em; }
            .error { color: #ff4444; background: #2a1111; padding: 15px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏈 NFL Prediction System</h1>
                <p>World-class predictions with quantum-inspired CFP analysis</p>
            </div>
            
            <div class="prediction-form">
                <h2>Game Prediction</h2>
                <form id="predictionForm">
                    <div class="form-group">
                        <label for="team1">Team 1:</label>
                        <select id="team1" name="team1" required>
                            <option value="">Select Team 1</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="team2">Team 2:</label>
                        <select id="team2" name="team2" required>
                            <option value="">Select Team 2</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="weather">Weather Conditions:</label>
                        <select id="weather" name="weather">
                            <option value="normal">Normal</option>
                            <option value="cold">Cold</option>
                            <option value="windy">Windy</option>
                            <option value="rainy">Rainy</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="homeTeam">Home Team:</label>
                        <select id="homeTeam" name="homeTeam">
                            <option value="">Neutral</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <button type="submit">Generate Prediction</button>
                    </div>
                </form>
            </div>
            
            <div id="results" class="results" style="display: none;">
                <h2>Prediction Results</h2>
                <div id="predictionContent"></div>
            </div>
        </div>

        <script>
            // Load teams
            async function loadTeams() {
                try {
                    const response = await fetch('/api/teams');
                    const teams = await response.json();
                    
                    const team1Select = document.getElementById('team1');
                    const team2Select = document.getElementById('team2');
                    const homeTeamSelect = document.getElementById('homeTeam');
                    
                    teams.forEach(team => {
                        const option1 = new Option(team, team);
                        const option2 = new Option(team, team);
                        const option3 = new Option(team, team);
                        
                        team1Select.add(option1);
                        team2Select.add(option2);
                        homeTeamSelect.add(option3);
                    });
                } catch (error) {
                    console.error('Error loading teams:', error);
                }
            }
            
            // Handle form submission
            document.getElementById('predictionForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const predictionData = {
                    team1: formData.get('team1'),
                    team2: formData.get('team2'),
                    game_context: {
                        weather: formData.get('weather'),
                        home_team: formData.get('homeTeam')
                    }
                };
                
                // Show loading
                document.getElementById('results').style.display = 'block';
                document.getElementById('predictionContent').innerHTML = '<div class="loading">Generating prediction...</div>';
                
                try {
                    const response = await fetch('/api/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(predictionData)
                    });
                    
                    if (!response.ok) {
                        throw new Error('Prediction failed');
                    }
                    
                    const prediction = await response.json();
                    displayPrediction(prediction);
                } catch (error) {
                    document.getElementById('predictionContent').innerHTML = 
                        '<div class="error">Error generating prediction: ' + error.message + '</div>';
                }
            });
            
            // Display prediction results
            function displayPrediction(prediction) {
                const content = `
                    <div class="prediction-card">
                        <h3>${prediction.team1} vs ${prediction.team2}</h3>
                        <div class="score">${prediction.predicted_score}</div>
                        <p><strong>Predicted Winner:</strong> ${prediction.predicted_winner}</p>
                        <p><strong>Confidence:</strong> <span class="confidence">${(prediction.confidence * 100).toFixed(1)}%</span></p>
                        <p><strong>Margin:</strong> ${prediction.margin}</p>
                        <p><strong>Total Points:</strong> ${prediction.total_points}</p>
                        <p><strong>Over/Under:</strong> ${prediction.over_under}</p>
                        <p><strong>Weather Impact:</strong> ${prediction.weather_impact}</p>
                        <p><strong>Injury Impact:</strong> ${prediction.injury_impact}</p>
                        <p><strong>Momentum Factor:</strong> ${prediction.momentum_factor}</p>
                        <p><strong>Clutch Performance:</strong> ${prediction.clutch_performance}</p>
                        <p><strong>Key Factors:</strong> <span class="factors">${prediction.key_factors.join(', ')}</span></p>
                    </div>
                `;
                
                document.getElementById('predictionContent').innerHTML = content;
            }
            
            // Initialize page
            loadTeams();
        </script>
    </body>
    </html>
    """

@app.get("/api/teams")
async def get_teams():
    """Get all NFL teams"""
    try:
        teams = list(team_database.get_all_teams().keys())
        return teams
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving teams")

@app.get("/api/teams/{team_name}")
async def get_team_stats(team_name: str):
    """Get detailed stats for a specific team"""
    try:
        team = team_database.get_team(team_name)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return TeamStatsResponse(
            team_name=team.name,
            offensive_efficiency=team.offensive_efficiency,
            defensive_efficiency=team.defensive_efficiency,
            special_teams=team.special_teams,
            coaching=team.coaching,
            injuries=team.injuries,
            home_advantage=team.home_advantage,
            momentum=team.momentum,
            experience=team.experience,
            depth=team.depth,
            clutch_performance=team.clutch_performance,
            playoff_experience=team.playoff_experience,
            quarterback_rating=team.quarterback_rating,
            running_game=team.running_game,
            passing_game=team.passing_game,
            defense_rating=team.defense_rating,
            turnover_margin=team.turnover_margin,
            red_zone_efficiency=team.red_zone_efficiency,
            third_down_conversion=team.third_down_conversion,
            time_of_possession=team.time_of_possession,
            penalty_discipline=team.penalty_discipline,
            current_record=team.current_record,
            recent_form=team.recent_form,
            key_injuries=team.key_injuries
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team stats for {team_name}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving team stats")

@app.post("/api/predict", response_model=GamePredictionResponse)
async def predict_game(request: GamePredictionRequest):
    """Generate game prediction"""
    try:
        # Validate teams exist
        team1 = team_database.get_team(request.team1)
        team2 = team_database.get_team(request.team2)
        
        if not team1:
            raise HTTPException(status_code=404, detail=f"Team '{request.team1}' not found")
        if not team2:
            raise HTTPException(status_code=404, detail=f"Team '{request.team2}' not found")
        
        # Generate prediction
        prediction = await nfl_system.predict_game(
            request.team1,
            request.team2,
            request.game_context or {}
        )
        
        return GamePredictionResponse(
            game_id=prediction.game_id,
            team1=prediction.team1,
            team2=prediction.team2,
            predicted_winner=prediction.predicted_winner,
            predicted_score=prediction.predicted_score,
            confidence=prediction.confidence,
            margin=prediction.margin,
            total_points=prediction.total_points,
            over_under=prediction.over_under,
            key_factors=prediction.key_factors,
            weather_impact=prediction.weather_impact,
            injury_impact=prediction.injury_impact,
            momentum_factor=prediction.momentum_factor,
            clutch_performance=prediction.clutch_performance,
            prediction_timestamp=prediction.prediction_timestamp
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        raise HTTPException(status_code=500, detail="Error generating prediction")

@app.get("/api/predictions/week/{week}")
async def get_weekly_predictions(week: int):
    """Get predictions for all games in a week"""
    try:
        predictions = await nfl_system.get_weekly_predictions(week)
        
        prediction_responses = [
            GamePredictionResponse(
                game_id=pred.game_id,
                team1=pred.team1,
                team2=pred.team2,
                predicted_winner=pred.predicted_winner,
                predicted_score=pred.predicted_score,
                confidence=pred.confidence,
                margin=pred.margin,
                total_points=pred.total_points,
                over_under=pred.over_under,
                key_factors=pred.key_factors,
                weather_impact=pred.weather_impact,
                injury_impact=pred.injury_impact,
                momentum_factor=pred.momentum_factor,
                clutch_performance=pred.clutch_performance,
                prediction_timestamp=pred.prediction_timestamp
            ) for pred in predictions
        ]
        
        return WeeklyPredictionsResponse(
            week=week,
            predictions=prediction_responses,
            total_games=len(prediction_responses),
            generated_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error getting weekly predictions for week {week}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving weekly predictions")

@app.get("/api/predictions/history")
async def get_prediction_history():
    """Get prediction history"""
    try:
        history = nfl_system.get_prediction_history()
        return {
            "total_predictions": len(history),
            "predictions": [
                {
                    "game_id": pred.game_id,
                    "teams": f"{pred.team1} vs {pred.team2}",
                    "predicted_winner": pred.predicted_winner,
                    "confidence": pred.confidence,
                    "timestamp": pred.prediction_timestamp.isoformat()
                } for pred in history
            ]
        }
    except Exception as e:
        logger.error(f"Error getting prediction history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving prediction history")

@app.get("/api/stats/overview")
async def get_stats_overview():
    """Get system statistics overview"""
    try:
        all_teams = team_database.get_all_teams()
        afc_teams = team_database.get_teams_by_conference("AFC")
        nfc_teams = team_database.get_teams_by_conference("NFC")
        
        return {
            "total_teams": len(all_teams),
            "afc_teams": len(afc_teams),
            "nfc_teams": len(nfc_teams),
            "divisions": {
                "AFC": {
                    "East": len(team_database.get_teams_by_division("AFC", "East")),
                    "North": len(team_database.get_teams_by_division("AFC", "North")),
                    "South": len(team_database.get_teams_by_division("AFC", "South")),
                    "West": len(team_database.get_teams_by_division("AFC", "West"))
                },
                "NFC": {
                    "East": len(team_database.get_teams_by_division("NFC", "East")),
                    "North": len(team_database.get_teams_by_division("NFC", "North")),
                    "South": len(team_database.get_teams_by_division("NFC", "South")),
                    "West": len(team_database.get_teams_by_division("NFC", "West"))
                }
            },
            "system_status": "operational",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats overview: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving stats overview")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "nfl_system": "operational",
            "team_database": "operational",
            "cfp_engine": "operational"
        }
    }

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("NFL Prediction System starting up...")
    logger.info("System initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("NFL Prediction System shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
