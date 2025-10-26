#!/usr/bin/env python3
"""
4D Odds Analysis System
Advanced predictive modeling for optimal betting timing and value extraction
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import json

from odds_provider import OddsProvider
from ev_calculator import EVCalculator
from strike_point_detector import StrikePointDetector

logger = logging.getLogger(__name__)

@dataclass
class FourDOddsAnalysis:
    """4D analysis result for optimal betting"""
    game_id: str
    current_timestamp: str
    predicted_optimal_time: str
    confidence_score: float
    expected_edge_at_optimal: float
    risk_adjusted_return: float
    market_inefficiency_score: float
    timing_recommendation: str
    alternative_scenarios: List[Dict[str, Any]]
    reasoning_factors: List[str]
    historical_correlation: float

@dataclass
class MarketStateVector:
    """Multi-dimensional market state representation"""
    timestamp: str
    time_to_game: float  # hours
    current_odds: float
    odds_volatility_1h: float
    odds_volatility_6h: float
    volume_proxy: float  # betting volume indicator
    spread_movement: float
    total_movement: float
    weather_impact: float
    injury_impact: float
    public_sentiment: float  # -1 to 1, negative = public on other side
    sharpe_ratio_1d: float
    edge_persistence: float  # how long edge typically lasts

class Odds4DAnalyzer:
    """4D predictive analyzer for optimal betting timing"""

    def __init__(self, odds_provider: OddsProvider):
        self.odds_provider = odds_provider
        self.ev_calculator = EVCalculator(odds_provider)
        self.strike_detector = StrikePointDetector(odds_provider)

        # ML models for prediction
        self.edge_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.timing_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.volatility_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)

        # Training data storage
        self.training_data = []
        self.is_trained = False

    def create_market_state_vector(self, game_id: str, current_odds: float,
                                 time_to_game: float) -> MarketStateVector:
        """Create 4D market state representation"""
        # Get historical data for feature calculation
        history = self.odds_provider.get_odds_history(game_id, hours_back=24)

        # Calculate volatility metrics
        volatility_1h = self._calculate_volatility(history, hours=1)
        volatility_6h = self._calculate_volatility(history, hours=6)

        # Calculate movement metrics
        spread_movement = self._calculate_spread_movement(history)
        total_movement = self._calculate_total_movement(history)

        # Volume proxy (simplified)
        volume_proxy = self._calculate_volume_proxy(history)

        # Other factors (placeholders - would integrate with real data)
        weather_impact = 0.0
        injury_impact = 0.0
        public_sentiment = 0.0
        sharpe_ratio_1d = 0.0
        edge_persistence = 0.0

        return MarketStateVector(
            timestamp=datetime.now().isoformat(),
            time_to_game=time_to_game,
            current_odds=current_odds,
            odds_volatility_1h=volatility_1h,
            odds_volatility_6h=volatility_6h,
            volume_proxy=volume_proxy,
            spread_movement=spread_movement,
            total_movement=total_movement,
            weather_impact=weather_impact,
            injury_impact=injury_impact,
            public_sentiment=public_sentiment,
            sharpe_ratio_1d=sharpe_ratio_1d,
            edge_persistence=edge_persistence
        )

    def _calculate_volatility(self, history: List, hours: int) -> float:
        """Calculate odds volatility over specified hours"""
        if len(history) < 2:
            return 0.0

        recent_history = [h for h in history
                         if (datetime.now() - datetime.fromisoformat(h.timestamp)).total_seconds() / 3600 <= hours]

        if len(recent_history) < 2:
            return 0.0

        odds_values = []
        for snapshot in recent_history:
            for market, odds_list in snapshot.odds.items():
                for odds_record in odds_list:
                    odds_values.append(odds_record.get('odds', 0))

        if not odds_values:
            return 0.0

        return np.std(odds_values)

    def _calculate_spread_movement(self, history: List) -> float:
        """Calculate spread line movement"""
        # Placeholder - would extract spread data
        return 0.0

    def _calculate_total_movement(self, history: List) -> float:
        """Calculate over/under line movement"""
        # Placeholder - would extract total data
        return 0.0

    def _calculate_volume_proxy(self, history: List) -> float:
        """Calculate betting volume proxy"""
        # Placeholder - would use actual volume data
        return len(history) / 10.0

    async def analyze_4d_opportunity(self, game_id: str, our_prediction: Dict,
                                   current_odds: float, time_to_game: float) -> FourDOddsAnalysis:
        """Perform complete 4D analysis for optimal betting"""

        # Create current market state
        current_state = self.create_market_state_vector(game_id, current_odds, time_to_game)

        # Get EV calculations
        ev_calculations = await self.ev_calculator.calculate_ev_for_games({game_id: our_prediction})
        game_ev = ev_calculations.get(game_id, [])

        if not game_ev:
            return self._create_default_analysis(game_id)

        # Find best EV opportunity
        best_ev = max(game_ev, key=lambda x: x.expected_value)

        # Predict future edge development
        predicted_edge, confidence = self._predict_edge_evolution(current_state)

        # Calculate optimal timing
        optimal_time = self._calculate_optimal_timing(current_state, predicted_edge, time_to_game)

        # Calculate risk-adjusted return
        risk_adjusted_return = self._calculate_risk_adjusted_return(predicted_edge, confidence)

        # Assess market inefficiency
        inefficiency_score = self._assess_market_inefficiency(current_state, best_ev)

        # Generate timing recommendation
        timing_rec = self._generate_timing_recommendation(
            current_state, optimal_time, time_to_game, predicted_edge
        )

        # Create alternative scenarios
        alternatives = self._generate_alternative_scenarios(current_state, game_id)

        # Historical correlation (placeholder)
        historical_correlation = 0.7

        # Compile reasoning
        reasoning = self._generate_4d_reasoning(
            current_state, best_ev, predicted_edge, confidence, inefficiency_score
        )

        return FourDOddsAnalysis(
            game_id=game_id,
            current_timestamp=datetime.now().isoformat(),
            predicted_optimal_time=optimal_time,
            confidence_score=confidence,
            expected_edge_at_optimal=predicted_edge,
            risk_adjusted_return=risk_adjusted_return,
            market_inefficiency_score=inefficiency_score,
            timing_recommendation=timing_rec,
            alternative_scenarios=alternatives,
            reasoning_factors=reasoning,
            historical_correlation=historical_correlation
        )

    def _predict_edge_evolution(self, state: MarketStateVector) -> Tuple[float, float]:
        """Predict how edge will evolve over time"""
        if not self.is_trained:
            # Conservative prediction without ML
            base_edge = 3.0
            volatility_factor = min(1.0, state.odds_volatility_1h / 10.0)
            return base_edge * (1 - volatility_factor), 0.6

        # Use ML model (placeholder for now)
        features = np.array([[
            state.time_to_game,
            state.odds_volatility_1h,
            state.odds_volatility_6h,
            state.volume_proxy,
            state.public_sentiment
        ]])

        predicted_edge = float(self.edge_predictor.predict(features)[0])
        confidence = 0.7  # Would be calculated from model uncertainty

        return predicted_edge, confidence

    def _calculate_optimal_timing(self, state: MarketStateVector,
                                predicted_edge: float, time_to_game: float) -> str:
        """Calculate optimal time to place bet"""
        # Simple heuristic: bet now if edge is good and time is limited
        if time_to_game < 2:
            return datetime.now().isoformat()
        elif predicted_edge > 5:
            return (datetime.now() + timedelta(hours=min(4, time_to_game - 1))).isoformat()
        else:
            return (datetime.now() + timedelta(hours=min(2, time_to_game - 2))).isoformat()

    def _calculate_risk_adjusted_return(self, edge: float, confidence: float) -> float:
        """Calculate risk-adjusted expected return"""
        return edge * confidence

    def _assess_market_inefficiency(self, state: MarketStateVector, ev_calc) -> float:
        """Assess degree of market inefficiency (0-1 scale)"""
        inefficiency_factors = []

        # High volatility suggests inefficiency
        if state.odds_volatility_1h > 5:
            inefficiency_factors.append(0.3)
        elif state.odds_volatility_1h > 2:
            inefficiency_factors.append(0.2)

        # Large spread movement
        if abs(state.spread_movement) > 2:
            inefficiency_factors.append(0.2)

        # High volume proxy
        if state.volume_proxy > 0.8:
            inefficiency_factors.append(0.1)

        # Strong EV
        if ev_calc.expected_value > 10:
            inefficiency_factors.append(0.2)

        return min(1.0, sum(inefficiency_factors))

    def _generate_timing_recommendation(self, state: MarketStateVector,
                                     optimal_time: str, time_to_game: float,
                                     predicted_edge: float) -> str:
        """Generate specific timing recommendation"""
        optimal_dt = datetime.fromisoformat(optimal_time)
        now = datetime.now()
        time_diff = (optimal_dt - now).total_seconds() / 3600

        if time_diff < 0.5:
            return "BET_IMMEDIATELY"
        elif time_diff < 2:
            return "BET_WITHIN_HOUR"
        elif time_diff < 6:
            return "BET_WITHIN_6_HOURS"
        elif predicted_edge > 5:
            return "WAIT_FOR_BETTER_LINE"
        else:
            return "MONITOR_LINE_MOVEMENT"

    def _generate_alternative_scenarios(self, state: MarketStateVector, game_id: str) -> List[Dict]:
        """Generate alternative betting scenarios"""
        return [
            {
                "scenario": "Conservative",
                "timing": "Now",
                "expected_edge": 2.5,
                "confidence": 0.8,
                "reasoning": "Take current edge to avoid line movement against us"
            },
            {
                "scenario": "Aggressive",
                "timing": "Wait 2-3 hours",
                "expected_edge": 4.0,
                "confidence": 0.6,
                "reasoning": "Wait for potential improvement in edge"
            },
            {
                "scenario": "Market Timing",
                "timing": "Wait for line move",
                "expected_edge": 3.0,
                "confidence": 0.4,
                "reasoning": "Wait for public money to create better edge"
            }
        ]

    def _generate_4d_reasoning(self, state: MarketStateVector, ev_calc,
                             predicted_edge: float, confidence: float,
                             inefficiency_score: float) -> List[str]:
        """Generate comprehensive reasoning for 4D analysis"""
        reasoning = []

        reasoning.append(f"Current market state volatility: {state.odds_volatility_1h".2f"}")

        if state.odds_volatility_1h > 5:
            reasoning.append("High volatility suggests rapid line movement - timing critical")
        elif state.odds_volatility_1h < 1:
            reasoning.append("Low volatility suggests stable line - less timing pressure")

        reasoning.append(f"Expected value: ${ev_calc.expected_value".2f"}")
        reasoning.append(f"Edge prediction: {predicted_edge".1f"}%")
        reasoning.append(f"Market inefficiency score: {inefficiency_score".1%"}")

        if inefficiency_score > 0.5:
            reasoning.append("Market appears inefficient - good opportunity for edge")
        else:
            reasoning.append("Market appears efficient - edge may not persist")

        reasoning.append(f"Model confidence: {confidence".1%"}")

        if confidence > 0.7:
            reasoning.append("High confidence in edge prediction")
        elif confidence < 0.5:
            reasoning.append("Low confidence - consider waiting for more data")

        return reasoning

    def _create_default_analysis(self, game_id: str) -> FourDOddsAnalysis:
        """Create default analysis when data is insufficient"""
        return FourDOddsAnalysis(
            game_id=game_id,
            current_timestamp=datetime.now().isoformat(),
            predicted_optimal_time=datetime.now().isoformat(),
            confidence_score=0.3,
            expected_edge_at_optimal=2.0,
            risk_adjusted_return=0.6,
            market_inefficiency_score=0.2,
            timing_recommendation="BET_WITHIN_HOUR",
            alternative_scenarios=[],
            reasoning_factors=["Limited historical data available"],
            historical_correlation=0.5
        )

    def train_models(self, historical_data: List[Dict]) -> Dict[str, float]:
        """Train ML models with historical data"""
        if len(historical_data) < 50:
            logger.warning("Insufficient historical data for model training")
            return {"status": "insufficient_data"}

        # Prepare training data
        X = []
        y_edge = []
        y_timing = []
        y_volatility = []

        for record in historical_data:
            state = record.get('market_state')
            if not state:
                continue

            features = [
                state['time_to_game'],
                state['odds_volatility_1h'],
                state['odds_volatility_6h'],
                state['volume_proxy'],
                state['public_sentiment']
            ]

            X.append(features)
            y_edge.append(record.get('actual_edge', 0))
            y_timing.append(record.get('optimal_timing_hours', 0))
            y_volatility.append(record.get('volatility_change', 0))

        if len(X) < 20:
            return {"status": "insufficient_clean_data"}

        # Train models
        X_train, X_test, y_edge_train, y_edge_test = train_test_split(
            X, y_edge, test_size=0.2, random_state=42
        )

        self.edge_predictor.fit(X_train, y_edge_train)
        edge_score = r2_score(y_edge_test, self.edge_predictor.predict(X_test))

        X_train, X_test, y_timing_train, y_timing_test = train_test_split(
            X, y_timing, test_size=0.2, random_state=42
        )

        self.timing_predictor.fit(X_train, y_timing_train)
        timing_score = r2_score(y_timing_test, self.timing_predictor.predict(X_test))

        X_train, X_test, y_vol_train, y_vol_test = train_test_split(
            X, y_volatility, test_size=0.2, random_state=42
        )

        self.volatility_predictor.fit(X_train, y_vol_train)
        volatility_score = r2_score(y_vol_test, self.volatility_predictor.predict(X_test))

        self.is_trained = True

        return {
            "status": "trained",
            "edge_model_r2": edge_score,
            "timing_model_r2": timing_score,
            "volatility_model_r2": volatility_score
        }

    async def analyze_multiple_games_4d(self, game_predictions: Dict[str, Any]) -> Dict[str, FourDOddsAnalysis]:
        """Analyze multiple games with 4D analysis"""
        results = {}

        for game_id, prediction in game_predictions.items():
            # Get current odds for the game
            odds_snapshots = await self.ev_calculator.calculate_ev_for_games({game_id: prediction})
            game_ev = odds_snapshots.get(game_id, [])

            if game_ev:
                # Use first available odds record
                first_ev = game_ev[0]
                current_odds = first_ev.market_odds
                time_to_game = 24.0  # Placeholder

                analysis = await self.analyze_4d_opportunity(
                    game_id, prediction, current_odds, time_to_game
                )
                results[game_id] = analysis

        return results

# Global instance
odds_4d_analyzer = Odds4DAnalyzer(odds_provider)

async def analyze_4d_opportunity(game_id: str, our_prediction: Dict,
                               current_odds: float, time_to_game: float) -> FourDOddsAnalysis:
    """Convenience function for 4D analysis"""
    return await odds_4d_analyzer.analyze_4d_opportunity(game_id, our_prediction, current_odds, time_to_game)

async def analyze_multiple_games_4d(game_predictions: Dict[str, Any]) -> Dict[str, FourDOddsAnalysis]:
    """Analyze multiple games with 4D analysis"""
    return await odds_4d_analyzer.analyze_multiple_games_4d(game_predictions)
