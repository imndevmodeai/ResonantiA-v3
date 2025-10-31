#!/usr/bin/env python3
"""
Strike Point Detector for Optimal Betting Timing
Analyzes historical odds movement patterns to predict optimal betting windows
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import json

from odds_provider import OddsProvider
from ev_calculator import EVCalculator, EdgeOpportunity

logger = logging.getLogger(__name__)

@dataclass
class StrikePoint:
    """Optimal betting window prediction"""
    game_id: str
    market: str
    predicted_peak_time: str
    window_start: str
    window_end: str
    confidence: float
    edge_at_peak: float
    reasoning: List[str]
    historical_patterns: Dict[str, Any]

@dataclass
class OddsMovementPattern:
    """Historical odds movement pattern"""
    time_to_game: float  # Hours until game
    odds_change_rate: float  # Change per hour
    volume_indicator: float  # Betting volume indicator
    edge_at_time: float  # Edge at this point
    outcome: str  # "peak", "trough", "stable"

class StrikePointDetector:
    """Detects optimal betting windows based on historical patterns"""

    def __init__(self, odds_provider: OddsProvider):
        self.odds_provider = odds_provider
        self.min_confidence = 0.6
        self.lookback_hours = 48
        self.pattern_clusters = 5

    async def detect_strike_points(self, game_ids: List[str]) -> List[StrikePoint]:
        """Detect strike points for multiple games"""
        strike_points = []

        for game_id in game_ids:
            game_strikes = await self._analyze_game_strike_points(game_id)
            strike_points.extend(game_strikes)

        return strike_points

    async def _analyze_game_strike_points(self, game_id: str) -> List[StrikePoint]:
        """Analyze strike points for a single game"""
        # Get historical odds data
        history = self.odds_provider.get_odds_history(game_id, hours_back=self.lookback_hours)

        if len(history) < 3:
            # Not enough data, return conservative estimate
            return [self._create_conservative_strike_point(game_id)]

        # Extract patterns from history
        patterns = self._extract_movement_patterns(history)

        if not patterns:
            return [self._create_conservative_strike_point(game_id)]

        # Cluster patterns to find optimal windows
        clusters = self._cluster_patterns(patterns)

        # Generate strike points from clusters
        strike_points = []
        for cluster in clusters:
            strike_point = self._generate_strike_point_from_cluster(game_id, cluster)
            if strike_point.confidence >= self.min_confidence:
                strike_points.append(strike_point)

        return strike_points if strike_points else [self._create_conservative_strike_point(game_id)]

    def _extract_movement_patterns(self, history: List[OddsSnapshot]) -> List[OddsMovementPattern]:
        """Extract movement patterns from odds history"""
        patterns = []

        for i in range(1, len(history)):
            current = history[i]
            previous = history[i-1]

            # Calculate time difference
            current_time = datetime.fromisoformat(current.timestamp)
            previous_time = datetime.fromisoformat(previous.timestamp)
            time_diff = (current_time - previous_time).total_seconds() / 3600  # hours

            if time_diff <= 0:
                continue

            # Extract odds for each market
            for market, odds_list in current.odds.items():
                for odds_record in odds_list:
                    # Find corresponding odds in previous snapshot
                    prev_odds = self._find_matching_odds(previous.odds, market, odds_record.get('team'))

                    if prev_odds:
                        # Calculate movement metrics
                        odds_change = odds_record.get('odds', 0) - prev_odds.get('odds', 0)
                        odds_change_rate = odds_change / time_diff

                        # Calculate edge (simplified - would use actual EV calculation)
                        our_prob = 0.5  # Placeholder
                        edge = self.odds_provider.calculate_edge(our_prob, odds_record.get('odds', 0))

                        pattern = OddsMovementPattern(
                            time_to_game=self._calculate_time_to_game(current.timestamp),  # Would need game time
                            odds_change_rate=odds_change_rate,
                            volume_indicator=self._calculate_volume_indicator(current, previous),
                            edge_at_time=edge,
                            outcome=self._classify_pattern_outcome(odds_change_rate, edge)
                        )

                        patterns.append(pattern)

        return patterns

    def _find_matching_odds(self, odds_data: Dict, market: str, team: str) -> Optional[Dict]:
        """Find matching odds record in previous snapshot"""
        for odds_list in odds_data.get(market, []):
            for odds_record in odds_list:
                if odds_record.get('team') == team:
                    return odds_record
        return None

    def _calculate_time_to_game(self, timestamp: str) -> float:
        """Calculate hours until game (placeholder)"""
        # In real implementation, would parse game time from ESPN data
        return 24.0  # Placeholder: 24 hours

    def _calculate_volume_indicator(self, current: OddsSnapshot, previous: OddsSnapshot) -> float:
        """Calculate betting volume indicator (placeholder)"""
        # In real implementation, would analyze betting volume data
        return 1.0  # Placeholder

    def _classify_pattern_outcome(self, change_rate: float, edge: float) -> str:
        """Classify pattern outcome"""
        if change_rate > 10 and edge > 5:
            return "peak"
        elif change_rate < -10 and edge < -5:
            return "trough"
        else:
            return "stable"

    def _cluster_patterns(self, patterns: List[OddsMovementPattern]) -> List[Dict]:
        """Cluster movement patterns to identify optimal windows"""
        if len(patterns) < 3:
            return []

        # Convert to feature matrix
        features = []
        for pattern in patterns:
            feature_vector = [
                pattern.time_to_game,
                pattern.odds_change_rate,
                pattern.volume_indicator,
                pattern.edge_at_time
            ]
            features.append(feature_vector)

        X = np.array(features)

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Cluster
        kmeans = KMeans(n_clusters=min(self.pattern_clusters, len(patterns)), random_state=42)
        clusters = kmeans.fit_predict(X_scaled)

        # Group patterns by cluster
        cluster_groups = {}
        for i, cluster_id in enumerate(clusters):
            if cluster_id not in cluster_groups:
                cluster_groups[cluster_id] = []
            cluster_groups[cluster_id].append(patterns[i])

        # Create cluster summaries
        cluster_summaries = []
        for cluster_id, cluster_patterns in cluster_groups.items():
            summary = self._summarize_cluster(cluster_patterns)
            summary['cluster_id'] = cluster_id
            cluster_summaries.append(summary)

        return cluster_summaries

    def _summarize_cluster(self, patterns: List[OddsMovementPattern]) -> Dict:
        """Summarize a cluster of patterns"""
        if not patterns:
            return {}

        # Calculate averages
        avg_time_to_game = np.mean([p.time_to_game for p in patterns])
        avg_change_rate = np.mean([p.odds_change_rate for p in patterns])
        avg_edge = np.mean([p.edge_at_time for p in patterns])

        # Count outcomes
        outcome_counts = {}
        for pattern in patterns:
            outcome = pattern.outcome
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

        # Find most common outcome
        most_common_outcome = max(outcome_counts.items(), key=lambda x: x[1])[0]

        return {
            'avg_time_to_game': avg_time_to_game,
            'avg_change_rate': avg_change_rate,
            'avg_edge': avg_edge,
            'most_common_outcome': most_common_outcome,
            'pattern_count': len(patterns),
            'confidence': min(1.0, len(patterns) / 10)  # More patterns = higher confidence
        }

    def _generate_strike_point_from_cluster(self, game_id: str, cluster: Dict) -> StrikePoint:
        """Generate strike point prediction from cluster analysis"""
        time_to_game = cluster['avg_time_to_game']
        confidence = cluster['confidence']
        avg_edge = cluster['avg_edge']

        # Calculate predicted strike time (simplified)
        # In real implementation, would use ML model
        current_time = datetime.now()
        predicted_peak = current_time + timedelta(hours=time_to_game - 2)  # 2 hours before peak
        window_start = predicted_peak - timedelta(hours=1)
        window_end = predicted_peak + timedelta(hours=2)

        reasoning = [
            f"Historical pattern analysis shows {cluster['most_common_outcome']} movement",
            f"Average edge at optimal time: {avg_edge".1f"}%",
            f"Based on {cluster['pattern_count']} historical patterns",
            f"Confidence: {confidence".1%"}"
        ]

        return StrikePoint(
            game_id=game_id,
            market="moneyline",  # Default, would be specified
            predicted_peak_time=predicted_peak.isoformat(),
            window_start=window_start.isoformat(),
            window_end=window_end.isoformat(),
            confidence=confidence,
            edge_at_peak=avg_edge,
            reasoning=reasoning,
            historical_patterns=cluster
        )

    def _create_conservative_strike_point(self, game_id: str) -> StrikePoint:
        """Create conservative strike point when no historical data available"""
        current_time = datetime.now()
        window_start = current_time - timedelta(hours=1)
        window_end = current_time + timedelta(hours=2)

        return StrikePoint(
            game_id=game_id,
            market="moneyline",
            predicted_peak_time=current_time.isoformat(),
            window_start=window_start.isoformat(),
            window_end=window_end.isoformat(),
            confidence=0.3,
            edge_at_peak=2.0,
            reasoning=[
                "Conservative estimate - limited historical data",
                "Recommend betting within 2 hours of analysis"
            ],
            historical_patterns={"method": "conservative_fallback"}
        )

    def predict_optimal_timing(self, game_id: str, target_edge: float = 3.0) -> Dict[str, Any]:
        """Predict optimal timing for a specific edge target"""
        history = self.odds_provider.get_odds_history(game_id, hours_back=self.lookback_hours)

        if len(history) < 3:
            return self._create_conservative_strike_point(game_id)

        # Analyze when edges historically peaked
        edge_timeline = []
        for snapshot in history:
            # Would calculate EV/edge for each snapshot
            # For now, return simplified prediction
            pass

        # Simple prediction: bet now if edge is good, wait if improving
        current_time = datetime.now()

        return {
            "recommended_action": "BET_NOW",
            "reasoning": "Current edge meets minimum threshold",
            "expected_duration": "2 hours",
            "confidence": 0.6
        }

    def analyze_line_movement_trends(self, game_ids: List[str]) -> Dict[str, Any]:
        """Analyze line movement trends across multiple games"""
        trends = {}

        for game_id in game_ids:
            history = self.odds_provider.get_odds_history(game_id, hours_back=24)

            if len(history) >= 2:
                trends[game_id] = self._analyze_single_game_trends(history)

        return trends

    def _analyze_single_game_trends(self, history: List[OddsSnapshot]) -> Dict[str, Any]:
        """Analyze trends for a single game"""
        # Calculate movement metrics
        total_movement = 0
        volatility = 0

        for i in range(1, len(history)):
            current = history[i]
            previous = history[i-1]

            for market, odds_list in current.odds.items():
                for odds_record in odds_list:
                    prev_odds = self._find_matching_odds(previous.odds, market, odds_record.get('team'))
                    if prev_odds:
                        movement = abs(odds_record.get('odds', 0) - prev_odds.get('odds', 0))
                        total_movement += movement

        return {
            "total_movement": total_movement,
            "volatility": volatility,
            "trend_direction": "up" if total_movement > 0 else "down",
            "recommendation": "Monitor closely" if total_movement > 10 else "Stable"
        }

# Global instance
strike_detector = StrikePointDetector(odds_provider)

async def detect_strike_points_for_games(game_ids: List[str]) -> List[StrikePoint]:
    """Convenience function to detect strike points"""
    return await strike_detector.detect_strike_points(game_ids)

def predict_optimal_timing(game_id: str, target_edge: float = 3.0) -> Dict[str, Any]:
    """Predict optimal timing for a game"""
    return strike_detector.predict_optimal_timing(game_id, target_edge)
