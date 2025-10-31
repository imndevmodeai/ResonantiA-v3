#!/usr/bin/env python3
"""
Enhanced NFL Prediction API with Real Games and Weather
Updated FastAPI with upcoming games and accurate weather integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime, timedelta
import logging
import numpy as np

# Import our enhanced components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from enhanced_nfl_system import EnhancedNFLPredictionSystem, UpcomingGame, WeatherForecast
from data.nfl_team_database import NFLTeamDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced NFL Prediction System",
    description="Real upcoming games with accurate weather and CFP analysis",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize enhanced components
enhanced_system = EnhancedNFLPredictionSystem()
team_database = NFLTeamDatabase()

# Pydantic models
class UpcomingGameResponse(BaseModel):
    game_id: str
    week: int
    date: str
    time: str
    team1: str
    team2: str
    location: str
    stadium: str
    city: str
    state: str
    home_team: str
    is_playoff: bool
    betting_line: Optional[str]
    over_under: Optional[float]
    weather: Dict[str, Any]
    prediction: Dict[str, Any]

class WeatherResponse(BaseModel):
    temperature: float
    condition: str
    wind_speed: float
    wind_direction: str
    humidity: float
    precipitation_chance: float
    visibility: float
    game_impact: str
    forecast_confidence: float

# Enhanced web interface with real games
@app.get("/", response_class=HTMLResponse)
async def root():
    """Enhanced web interface with real upcoming games"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced NFL Prediction System</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; padding: 20px; 
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                color: white; 
                min-height: 100vh;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            .header { 
                text-align: center; margin-bottom: 30px; 
                background: linear-gradient(45deg, #00ff00, #00cc00);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .header h1 { font-size: 3em; margin: 0; font-weight: bold; }
            .header p { font-size: 1.3em; color: #ccc; margin: 10px 0; }
            
            .tabs {
                display: flex;
                margin-bottom: 30px;
                background: #2a2a2a;
                border-radius: 10px;
                padding: 5px;
            }
            .tab {
                flex: 1;
                padding: 15px;
                text-align: center;
                cursor: pointer;
                border-radius: 8px;
                transition: all 0.3s;
                font-weight: bold;
            }
            .tab.active {
                background: #00ff00;
                color: black;
            }
            .tab:hover:not(.active) {
                background: #333;
            }
            
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            
            .games-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .game-card {
                background: linear-gradient(145deg, #2a2a2a, #333);
                padding: 25px;
                border-radius: 15px;
                border-left: 5px solid #00ff00;
                box-shadow: 0 8px 25px rgba(0, 255, 0, 0.1);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .game-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 255, 0, 0.2);
            }
            
            .game-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            .game-title {
                font-size: 1.4em;
                font-weight: bold;
                color: #00ff00;
            }
            .game-date {
                color: #ccc;
                font-size: 0.9em;
            }
            
            .teams {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 20px 0;
                font-size: 1.2em;
                font-weight: bold;
            }
            .team {
                text-align: center;
                flex: 1;
            }
            .vs {
                color: #00ff00;
                font-size: 1.5em;
                margin: 0 20px;
            }
            
            .weather-section {
                background: #1a1a1a;
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
            }
            .weather-title {
                color: #00ff00;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .weather-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }
            .weather-item {
                display: flex;
                justify-content: space-between;
                padding: 5px 0;
                border-bottom: 1px solid #333;
            }
            .weather-label {
                color: #ccc;
            }
            .weather-value {
                color: white;
                font-weight: bold;
            }
            
            .prediction-section {
                background: #1a1a1a;
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
            }
            .prediction-title {
                color: #00ff00;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .predicted-winner {
                font-size: 1.3em;
                font-weight: bold;
                color: #00ff00;
                margin: 10px 0;
            }
            .predicted-score {
                font-size: 1.5em;
                font-weight: bold;
                margin: 10px 0;
            }
            .confidence {
                background: linear-gradient(45deg, #00ff00, #00cc00);
                color: black;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
                margin: 10px 0;
            }
            
            .factors {
                margin-top: 15px;
            }
            .factor {
                background: #333;
                padding: 8px 12px;
                border-radius: 5px;
                margin: 5px 0;
                font-size: 0.9em;
                color: #ccc;
            }
            
            .custom-prediction {
                background: #2a2a2a;
                padding: 30px;
                border-radius: 15px;
                margin-top: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #00ff00;
                font-weight: bold;
            }
            .form-group select, .form-group input {
                width: 100%;
                padding: 12px;
                border: 2px solid #555;
                border-radius: 8px;
                background: #333;
                color: white;
                font-size: 1em;
            }
            .form-group select:focus, .form-group input:focus {
                border-color: #00ff00;
                outline: none;
            }
            .btn {
                background: linear-gradient(45deg, #00ff00, #00cc00);
                color: black;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                font-size: 1.1em;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 255, 0, 0.3);
            }
            
            .loading {
                text-align: center;
                color: #00ff00;
                font-size: 1.2em;
                padding: 20px;
            }
            .error {
                color: #ff4444;
                background: #2a1111;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
            }
            
            .refresh-btn {
                background: #333;
                color: white;
                border: 2px solid #00ff00;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                margin-bottom: 20px;
            }
            .refresh-btn:hover {
                background: #00ff00;
                color: black;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏈 Enhanced NFL Prediction System</h1>
                <p>Real Upcoming Games • Accurate Weather • Quantum-Inspired CFP Analysis</p>
            </div>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('upcoming')">📅 Upcoming Games</div>
                <div class="tab" onclick="showTab('custom')">🎯 Custom Prediction</div>
                <div class="tab" onclick="showTab('stats')">📊 Team Stats</div>
            </div>
            
            <div id="upcoming" class="tab-content active">
                <button class="refresh-btn" onclick="loadUpcomingGames()">🔄 Refresh Games</button>
                <div id="upcomingGames" class="games-grid">
                    <div class="loading">Loading upcoming games...</div>
                </div>
            </div>
            
            <div id="custom" class="tab-content">
                <div class="custom-prediction">
                    <h2>Custom Game Prediction</h2>
                    <form id="customPredictionForm">
                        <div class="form-group">
                            <label for="customTeam1">Team 1:</label>
                            <select id="customTeam1" name="team1" required>
                                <option value="">Select Team 1</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="customTeam2">Team 2:</label>
                            <select id="customTeam2" name="team2" required>
                                <option value="">Select Team 2</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="customWeather">Weather Conditions:</label>
                            <select id="customWeather" name="weather">
                                <option value="normal">Normal</option>
                                <option value="cold">Cold</option>
                                <option value="windy">Windy</option>
                                <option value="rainy">Rainy</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="customHomeTeam">Home Team:</label>
                            <select id="customHomeTeam" name="homeTeam">
                                <option value="">Neutral</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <button type="submit" class="btn">Generate Custom Prediction</button>
                        </div>
                    </form>
                    <div id="customResults"></div>
                </div>
            </div>
            
            <div id="stats" class="tab-content">
                <h2>Team Statistics</h2>
                <div id="teamStats"></div>
            </div>
        </div>

        <script>
            // Tab switching
            function showTab(tabName) {
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                
                // Remove active class from all tabs
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show selected tab content
                document.getElementById(tabName).classList.add('active');
                
                // Add active class to clicked tab
                event.target.classList.add('active');
                
                // Load content based on tab
                if (tabName === 'upcoming') {
                    loadUpcomingGames();
                } else if (tabName === 'stats') {
                    loadTeamStats();
                }
            }
            
            // Load upcoming games
            async function loadUpcomingGames() {
                try {
                    document.getElementById('upcomingGames').innerHTML = '<div class="loading">Loading upcoming games...</div>';
                    
                    const response = await fetch('/api/upcoming-games');
                    const games = await response.json();
                    
                    displayUpcomingGames(games);
                } catch (error) {
                    document.getElementById('upcomingGames').innerHTML = 
                        '<div class="error">Error loading games: ' + error.message + '</div>';
                }
            }
            
            // Display upcoming games
            function displayUpcomingGames(games) {
                const container = document.getElementById('upcomingGames');
                
                if (games.length === 0) {
                    container.innerHTML = '<div class="error">No upcoming games found</div>';
                    return;
                }
                
                container.innerHTML = games.map(game => `
                    <div class="game-card">
                        <div class="game-header">
                            <div class="game-title">${game.team1} vs ${game.team2}</div>
                            <div class="game-date">${game.date} at ${game.time}</div>
                        </div>
                        
                        <div class="teams">
                            <div class="team">${game.team1}</div>
                            <div class="vs">VS</div>
                            <div class="team">${game.team2}</div>
                        </div>
                        
                        <div class="weather-section">
                            <div class="weather-title">🌤️ Weather Forecast</div>
                            <div class="weather-grid">
                                <div class="weather-item">
                                    <span class="weather-label">Temperature:</span>
                                    <span class="weather-value">${game.weather.temperature}°F</span>
                                </div>
                                <div class="weather-item">
                                    <span class="weather-label">Condition:</span>
                                    <span class="weather-value">${game.weather.condition.replace('_', ' ').toUpperCase()}</span>
                                </div>
                                <div class="weather-item">
                                    <span class="weather-label">Wind:</span>
                                    <span class="weather-value">${game.weather.wind_speed} mph ${game.weather.wind_direction}</span>
                                </div>
                                <div class="weather-item">
                                    <span class="weather-label">Humidity:</span>
                                    <span class="weather-value">${game.weather.humidity}%</span>
                                </div>
                                <div class="weather-item">
                                    <span class="weather-label">Precipitation:</span>
                                    <span class="weather-value">${game.weather.precipitation_chance}%</span>
                                </div>
                                <div class="weather-item">
                                    <span class="weather-label">Confidence:</span>
                                    <span class="weather-value">${(game.weather.forecast_confidence * 100).toFixed(0)}%</span>
                                </div>
                            </div>
                            <div style="margin-top: 10px; color: #ccc; font-size: 0.9em;">
                                ${game.weather.game_impact}
                            </div>
                        </div>
                        
                        <div class="prediction-section">
                            <div class="prediction-title">🎯 Prediction</div>
                            <div class="predicted-winner">Winner: ${game.prediction.predicted_winner}</div>
                            <div class="predicted-score">${game.prediction.predicted_score}</div>
                            <div class="confidence">Confidence: ${(game.prediction.confidence * 100).toFixed(1)}%</div>
                            <div style="margin: 10px 0; color: #ccc;">
                                <strong>Margin:</strong> ${game.prediction.margin}<br>
                                <strong>Total Points:</strong> ${game.prediction.total_points}<br>
                                <strong>Weather Impact:</strong> ${game.prediction.weather_impact}
                            </div>
                            <div class="factors">
                                <strong>Key Factors:</strong>
                                ${game.prediction.key_factors.map(factor => 
                                    `<div class="factor">• ${factor}</div>`
                                ).join('')}
                            </div>
                        </div>
                        
                        <div style="margin-top: 15px; padding: 10px; background: #1a1a1a; border-radius: 8px; font-size: 0.9em;">
                            <strong>📍 Location:</strong> ${game.stadium}, ${game.city}, ${game.state}<br>
                            <strong>🏠 Home Team:</strong> ${game.home_team}<br>
                            <strong>💰 Betting Line:</strong> ${game.betting_line || 'N/A'}<br>
                            <strong>📊 Over/Under:</strong> ${game.over_under || 'N/A'}
                        </div>
                    </div>
                `).join('');
            }
            
            // Load teams for custom prediction
            async function loadTeams() {
                try {
                    const response = await fetch('/api/teams');
                    const teams = await response.json();
                    
                    const team1Select = document.getElementById('customTeam1');
                    const team2Select = document.getElementById('customTeam2');
                    const homeTeamSelect = document.getElementById('customHomeTeam');
                    
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
            
            // Custom prediction form
            document.getElementById('customPredictionForm').addEventListener('submit', async (e) => {
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
                
                document.getElementById('customResults').innerHTML = '<div class="loading">Generating prediction...</div>';
                
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
                    displayCustomPrediction(prediction);
                } catch (error) {
                    document.getElementById('customResults').innerHTML = 
                        '<div class="error">Error generating prediction: ' + error.message + '</div>';
                }
            });
            
            // Display custom prediction
            function displayCustomPrediction(prediction) {
                const content = `
                    <div class="game-card">
                        <div class="prediction-section">
                            <div class="prediction-title">🎯 Custom Prediction</div>
                            <div class="predicted-winner">Winner: ${prediction.predicted_winner}</div>
                            <div class="predicted-score">${prediction.predicted_score}</div>
                            <div class="confidence">Confidence: ${(prediction.confidence * 100).toFixed(1)}%</div>
                            <div style="margin: 10px 0; color: #ccc;">
                                <strong>Margin:</strong> ${prediction.margin}<br>
                                <strong>Total Points:</strong> ${prediction.total_points}<br>
                                <strong>Over/Under:</strong> ${prediction.over_under}<br>
                                <strong>Weather Impact:</strong> ${prediction.weather_impact}<br>
                                <strong>Injury Impact:</strong> ${prediction.injury_impact}<br>
                                <strong>Momentum Factor:</strong> ${prediction.momentum_factor}<br>
                                <strong>Clutch Performance:</strong> ${prediction.clutch_performance}
                            </div>
                            <div class="factors">
                                <strong>Key Factors:</strong>
                                ${prediction.key_factors.map(factor => 
                                    `<div class="factor">• ${factor}</div>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                `;
                
                document.getElementById('customResults').innerHTML = content;
            }
            
            // Load team stats
            async function loadTeamStats() {
                try {
                    const response = await fetch('/api/stats/overview');
                    const stats = await response.json();
                    
                    document.getElementById('teamStats').innerHTML = `
                        <div class="game-card">
                            <h3>System Overview</h3>
                            <p><strong>Total Teams:</strong> ${stats.total_teams}</p>
                            <p><strong>AFC Teams:</strong> ${stats.afc_teams}</p>
                            <p><strong>NFC Teams:</strong> ${stats.nfc_teams}</p>
                            <p><strong>System Status:</strong> ${stats.system_status}</p>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('teamStats').innerHTML = 
                        '<div class="error">Error loading stats: ' + error.message + '</div>';
                }
            }
            
            // Initialize page
            loadTeams();
            loadUpcomingGames();
        </script>
    </body>
    </html>
    """

# API Routes
@app.get("/api/upcoming-games")
async def get_upcoming_games():
    """Get upcoming games with predictions and weather"""
    try:
        games_with_predictions = await enhanced_system.get_upcoming_games_with_predictions()
        
        return [
            UpcomingGameResponse(
                game_id=game["game_id"],
                week=game["week"],
                date=game["date"],
                time=game["time"],
                team1=game["team1"],
                team2=game["team2"],
                location=game["location"],
                stadium=game["stadium"],
                city=game["city"],
                state=game["state"],
                home_team=game["home_team"],
                is_playoff=game["is_playoff"],
                betting_line=game["betting_line"],
                over_under=game["over_under"],
                weather=game["weather"],
                prediction=game["prediction"]
            ) for game in games_with_predictions
        ]
    except Exception as e:
        logger.error(f"Error getting upcoming games: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving upcoming games")

@app.get("/api/teams")
async def get_teams():
    """Get all NFL teams"""
    try:
        teams = list(team_database.get_all_teams().keys())
        return teams
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving teams")

@app.get("/api/stats/overview")
async def get_stats_overview():
    """Get system statistics overview"""
    try:
        teams = team_database.get_all_teams()
        afc_teams = sum(1 for team in teams.values() if team.get('conference') == 'AFC')
        nfc_teams = sum(1 for team in teams.values() if team.get('conference') == 'NFC')
        
        return {
            "total_teams": len(teams),
            "afc_teams": afc_teams,
            "nfc_teams": nfc_teams,
            "system_status": "operational",
            "last_updated": datetime.now().isoformat(),
            "features": [
                "Real upcoming games",
                "Accurate weather forecasts", 
                "CFP analysis integration",
                "Enhanced web interface"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting stats overview: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": [
            "Real upcoming games",
            "Accurate weather forecasts",
            "CFP analysis integration",
            "Enhanced web interface"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
