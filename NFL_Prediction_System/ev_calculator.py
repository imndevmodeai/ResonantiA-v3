#!/usr/bin/env python3
"""
EV Calculator for Sports Betting
Calculates real-time expected value and edge against live odds
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import numpy as np
from datetime import datetime, timedelta

from odds_provider import OddsProvider, OddsSnapshot, get_live_odds_for_games

logger = logging.getLogger(__name__)

@dataclass
class EVCalculation:
    """Expected Value calculation result"""
    game_id: str
    our_probability: float
    market_odds: float
    implied_probability: float
    expected_value: float
    edge_percentage: float
    bet_type: str
    team: str
    timestamp: str
    recommendation: str  # "BET", "PASS", "WAIT"
    confidence: float

@dataclass
class EdgeOpportunity:
    """Edge opportunity with EV data"""
    game_id: str
    team: str
    bet_type: str
    current_odds: float
    our_prob: float
    edge: float
    ev: float
    kelly_criterion: float  # Optimal bet size
    strike_window: Dict[str, Any]  # When to bet
    reasoning: List[str]

class EVCalculator:
    """Calculates real-time EV and edge opportunities"""

    def __init__(self, odds_provider: OddsProvider):
        self.odds_provider = odds_provider
        self.min_edge_threshold = 3.0  # Minimum edge % to consider
        self.max_edge_threshold = 15.0  # Maximum edge % (outlier filter)
        self.kelly_fraction = 0.25  # Conservative Kelly betting

    async def calculate_ev_for_games(self, game_predictions: Dict[str, Any]) -> Dict[str, List[EVCalculation]]:
        """Calculate EV for all games with predictions"""
        game_ids = list(game_predictions.keys())

        # Get live odds
        odds_snapshots = await get_live_odds_for_games(game_ids)

        ev_results = {}

        for game_id, prediction in game_predictions.items():
            if game_id not in odds_snapshots:
                continue

            snapshot = odds_snapshots[game_id]
            game_ev = []

            # Calculate EV for each available market
            for sportsbook, markets in snapshot.odds.items():
                for market_type, odds_list in markets.items():
                    for odds_record in odds_list:
                        ev_calc = self._calculate_single_ev(
                            game_id, prediction, odds_record, market_type
                        )
                        if ev_calc:
                            game_ev.append(ev_calc)

            ev_results[game_id] = game_ev

        return ev_results

    def _calculate_single_ev(self, game_id: str, prediction: Dict, odds_record: Dict,
                           market_type: str) -> Optional[EVCalculation]:
        """Calculate EV for a single odds record"""
        our_prob = prediction.get('confidence', 0.5)
        market_odds = odds_record.get('odds', 0)

        if market_odds == 0:
            return None

        # Calculate expected value and edge
        ev = self.odds_provider.calculate_ev(our_prob, market_odds)
        edge = self.odds_provider.calculate_edge(our_prob, market_odds)
        implied_prob = self.odds_provider._odds_to_prob(market_odds)

        # Determine recommendation
        recommendation = self._get_recommendation(ev, edge, our_prob)

        return EVCalculation(
            game_id=game_id,
            our_probability=our_prob,
            market_odds=market_odds,
            implied_probability=implied_prob,
            expected_value=ev,
            edge_percentage=edge,
            bet_type=market_type,
            team=odds_record.get('team', ''),
            timestamp=datetime.now().isoformat(),
            recommendation=recommendation,
            confidence=prediction.get('confidence', 0.5)
        )

    def _get_recommendation(self, ev: float, edge: float, our_prob: float) -> str:
        """Get betting recommendation based on EV and edge"""
        if ev > 5 and edge > self.min_edge_threshold:
            return "BET"
        elif ev > 0 and edge > 1.0:
            return "CONSIDER"
        elif edge < -self.min_edge_threshold:
            return "FADE"  # Bet against our model
        else:
            return "PASS"

    async def find_edge_opportunities(self, game_predictions: Dict[str, Any],
                                     min_edge: float = 2.0) -> List[EdgeOpportunity]:
        """Find games with significant edge opportunities"""
        ev_results = await self.calculate_ev_for_games(game_predictions)

        opportunities = []

        for game_id, ev_calculations in ev_results.items():
            for ev_calc in ev_calculations:
                if abs(ev_calc.edge_percentage) >= min_edge:
                    # Calculate Kelly criterion
                    kelly = self._calculate_kelly_criterion(
                        ev_calc.our_probability,
                        ev_calc.market_odds
                    )

                    # Get strike window prediction
                    strike_window = await self._predict_strike_window(game_id, ev_calc)

                    opportunity = EdgeOpportunity(
                        game_id=game_id,
                        team=ev_calc.team,
                        bet_type=ev_calc.bet_type,
                        current_odds=ev_calc.market_odds,
                        our_prob=ev_calc.our_probability,
                        edge=ev_calc.edge_percentage,
                        ev=ev_calc.expected_value,
                        kelly_criterion=kelly,
                        strike_window=strike_window,
                        reasoning=self._generate_reasoning(ev_calc)
                    )

                    opportunities.append(opportunity)

        # Sort by edge (highest first)
        opportunities.sort(key=lambda x: abs(x.edge), reverse=True)
        return opportunities

    def _calculate_kelly_criterion(self, our_prob: float, market_odds: float) -> float:
        """Calculate optimal bet size using Kelly Criterion"""
        if market_odds > 0:
            payout = market_odds / 100  # Convert to decimal
            stake_base = 100
        else:
            payout = 100 / abs(market_odds)  # Convert to decimal
            stake_base = abs(market_odds)

        # Kelly formula: f* = (bp - q) / b
        # where b = odds-1, p = our prob, q = 1-p
        b = payout - 1
        p = our_prob
        q = 1 - p

        if b <= 0:
            return 0

        kelly_fraction = (b * p - q) / b
        return max(0, kelly_fraction * self.kelly_fraction)  # Conservative fraction

    async def _predict_strike_window(self, game_id: str, ev_calc: EVCalculation) -> Dict[str, Any]:
        """Predict optimal betting window based on historical patterns"""
        # Get odds history
        history = self.odds_provider.get_odds_history(game_id, hours_back=24)

        if len(history) < 2:
            # No history, suggest now
            return {
                "recommended_time": datetime.now().isoformat(),
                "window_start": (datetime.now() - timedelta(hours=1)).isoformat(),
                "window_end": (datetime.now() + timedelta(hours=2)).isoformat(),
                "confidence": 0.5,
                "reasoning": "Limited historical data"
            }

        # Analyze edge patterns (simplified)
        edge_trend = self._analyze_edge_trend(history, ev_calc)

        return {
            "recommended_time": edge_trend.get('peak_time'),
            "window_start": edge_trend.get('window_start'),
            "window_end": edge_trend.get('window_end'),
            "confidence": edge_trend.get('confidence', 0.5),
            "reasoning": edge_trend.get('reasoning', 'Based on historical patterns')
        }

    def _analyze_edge_trend(self, history: List[OddsSnapshot],
                           ev_calc: EVCalculation) -> Dict[str, Any]:
        """Analyze historical edge trends to predict optimal timing"""
        # This is a simplified version - in production would use ML models
        # For now, return conservative estimate based on time to game

        return {
            "peak_time": datetime.now().isoformat(),
            "window_start": (datetime.now() - timedelta(hours=2)).isoformat(),
            "window_end": (datetime.now() + timedelta(hours=4)).isoformat(),
            "confidence": 0.6,
            "reasoning": "Conservative estimate - place bet within 2 hours"
        }

    def _generate_reasoning(self, ev_calc: EVCalculation) -> List[str]:
        """Generate reasoning for the edge opportunity"""
        reasoning = []

        edge = ev_calc.edge_percentage
        ev = ev_calc.expected_value

        if edge > 10:
            reasoning.append(f"Strong edge of {edge".1f"}% detected")
        elif edge > 5:
            reasoning.append(f"Good edge of {edge".1f"}% detected")
        elif edge > 2:
            reasoning.append(f"Moderate edge of {edge".1f"}% detected")

        if ev > 10:
            reasoning.append(f"High expected value: ${ev".2f"}")
        elif ev > 5:
            reasoning.append(f"Positive expected value: ${ev".2f"}")

        if ev_calc.our_probability > 0.6:
            reasoning.append(f"High confidence in our prediction: {ev_calc.our_probability".1%"}")
        elif ev_calc.our_probability > 0.5:
            reasoning.append(f"Moderate confidence: {ev_calc.our_probability".1%"}")

        reasoning.append(f"Market odds: {ev_calc.market_odds}")
        reasoning.append(f"Implied probability: {ev_calc.implied_probability".1%"}")

        return reasoning

    def calculate_portfolio_ev(self, user_bets: List[Dict], live_odds: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate EV for user's current portfolio"""
        total_ev = 0
        total_stake = 0
        recommendations = []

        for bet in user_bets:
            game_id = bet['game_id']

            if game_id in live_odds:
                live_odds_data = live_odds[game_id]

                # Find matching odds
                for market_type, odds_list in live_odds_data.items():
                    if market_type == bet['bet_type']:
                        for odds_record in odds_list:
                            if odds_record.get('team') == bet['team']:
                                # Calculate current EV
                                our_prob = 0.5  # Would use our model probability
                                current_ev = self.odds_provider.calculate_ev(our_prob, odds_record['odds'])

                                total_ev += current_ev * bet['stake']
                                total_stake += bet['stake']

                                # Generate recommendation
                                if current_ev > bet['stake'] * 0.05:  # 5% of stake
                                    recommendations.append({
                                        "bet_id": bet['id'],
                                        "recommendation": "HOLD",
                                        "reasoning": f"Positive EV remaining: ${current_ev".2f"}"
                                    })
                                elif current_ev < 0:
                                    recommendations.append({
                                        "bet_id": bet['id'],
                                        "recommendation": "CONSIDER_CASH_OUT",
                                        "reasoning": f"Negative EV: ${current_ev".2f"} - consider cashing out"
                                    })
                                break

        return {
            "total_ev": total_ev,
            "total_stake": total_stake,
            "net_ev": total_ev - total_stake,
            "recommendations": recommendations,
            "roi": (total_ev / total_stake - 1) * 100 if total_stake > 0 else 0
        }

# Global instance
ev_calculator = EVCalculator(odds_provider)

async def calculate_ev_for_predictions(game_predictions: Dict[str, Any]) -> Dict[str, List[EVCalculation]]:
    """Convenience function to calculate EV for game predictions"""
    return await ev_calculator.calculate_ev_for_games(game_predictions)

async def find_edge_opportunities(game_predictions: Dict[str, Any], min_edge: float = 2.0) -> List[EdgeOpportunity]:
    """Find games with edge opportunities"""
    return await ev_calculator.find_edge_opportunities(game_predictions, min_edge)
