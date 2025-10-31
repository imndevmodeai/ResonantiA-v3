#!/usr/bin/env python3
"""
Live Odds Provider Integration
Fetches real-time odds from FanDuel and other sportsbooks for EV calculations
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import aiohttp
import sqlite3
from contextlib import contextmanager
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class OddsRecord:
    """Individual odds record"""
    game_id: str
    timestamp: str
    sportsbook: str
    market: str  # moneyline, spread, total
    team: str
    odds: float
    implied_prob: float
    line: Optional[float] = None  # for spreads/totals
    over_under: Optional[str] = None  # over/under for totals

@dataclass
class OddsSnapshot:
    """Complete odds snapshot for a game"""
    game_id: str
    timestamp: str
    odds: Dict[str, List[OddsRecord]]  # sportsbook -> market -> odds
    ev_data: Dict[str, Any] = None  # Will store EV calculations

class OddsProvider:
    """Main odds provider class"""

    def __init__(self, db_path: str = "data/odds_history.db"):
        self.db_path = db_path
        self.fanduel_api_key = os.getenv('FANDUEL_API_KEY', '')
        self.base_url = "https://api.fanduel.com"
        self.session: Optional[aiohttp.ClientSession] = None
        self._init_db()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={'Authorization': f'Bearer {self.fanduel_api_key}'}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @contextmanager
    def _get_db_connection(self):
        """Get database connection with proper isolation"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initialize odds history database"""
        with self._get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS odds_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    sportsbook TEXT NOT NULL,
                    market TEXT NOT NULL,
                    team TEXT,
                    odds REAL NOT NULL,
                    implied_prob REAL NOT NULL,
                    line REAL,
                    over_under TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS odds_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    odds_data TEXT NOT NULL,  -- JSON
                    ev_data TEXT,  -- JSON
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_bets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    game_id TEXT NOT NULL,
                    bet_type TEXT NOT NULL,  -- moneyline, spread, total
                    team TEXT,
                    odds_locked REAL NOT NULL,
                    stake REAL,
                    timestamp TEXT NOT NULL,
                    status TEXT DEFAULT 'active',  -- active, cashed_out, settled
                    result TEXT,  -- win, loss, push
                    payout REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS strike_points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    market TEXT NOT NULL,
                    predicted_strike_time TEXT,
                    confidence REAL,
                    edge_peak REAL,
                    reasoning TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()

    async def fetch_fanduel_odds(self, game_ids: List[str]) -> Dict[str, Any]:
        """Fetch odds from FanDuel API"""
        if not self.session:
            await self.__aenter__()

        try:
            # FanDuel API endpoint for NFL odds
            url = f"{self.base_url}/sports-data/v1/nfl/odds"

            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_fanduel_response(data, game_ids)
                else:
                    logger.error(f"FanDuel API error: {response.status}")
                    return {}

        except Exception as e:
            logger.error(f"Error fetching FanDuel odds: {e}")
            return {}

    def _parse_fanduel_response(self, data: Dict, game_ids: List[str]) -> Dict[str, Any]:
        """Parse FanDuel API response"""
        odds_by_game = {}

        for game in data.get('games', []):
            game_id = game.get('id')
            if game_id not in game_ids:
                continue

            odds_by_game[game_id] = {
                'markets': {}
            }

            for market in game.get('markets', []):
                market_type = market.get('type', '').lower()

                for selection in market.get('selections', []):
                    team = selection.get('name', '')
                    odds = selection.get('price', 0)

                    if market_type not in odds_by_game[game_id]['markets']:
                        odds_by_game[game_id]['markets'][market_type] = []

                    odds_by_game[game_id]['markets'][market_type].append({
                        'team': team,
                        'odds': odds,
                        'implied_prob': self._odds_to_prob(odds),
                        'line': market.get('line', None),
                        'over_under': market.get('over_under', None)
                    })

        return odds_by_game

    def _odds_to_prob(self, odds: float) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    def _prob_to_odds(self, prob: float) -> float:
        """Convert probability to American odds"""
        if prob >= 0.5:
            return (prob / (1 - prob)) * -100
        else:
            return ((1 - prob) / prob) * 100

    async def get_live_odds(self, game_ids: List[str]) -> Dict[str, OddsSnapshot]:
        """Get live odds for specified games"""
        # Try FanDuel first
        fanduel_odds = await self.fetch_fanduel_odds(game_ids)

        # Fallback to other providers if needed
        # For now, return FanDuel data

        snapshots = {}
        timestamp = datetime.now().isoformat()

        for game_id in game_ids:
            if game_id in fanduel_odds:
                snapshots[game_id] = OddsSnapshot(
                    game_id=game_id,
                    timestamp=timestamp,
                    odds=fanduel_odds[game_id]['markets']
                )

        return snapshots

    def save_odds_snapshot(self, snapshot: OddsSnapshot):
        """Save odds snapshot to database"""
        with self._get_db_connection() as conn:
            # Save individual odds records
            for sportsbook, markets in snapshot.odds.items():
                for market, odds_list in markets.items():
                    for odds_record in odds_list:
                        conn.execute('''
                            INSERT INTO odds_history
                            (game_id, timestamp, sportsbook, market, team, odds, implied_prob, line, over_under)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            snapshot.game_id,
                            snapshot.timestamp,
                            sportsbook,
                            market,
                            odds_record.get('team'),
                            odds_record.get('odds', 0),
                            odds_record.get('implied_prob', 0),
                            odds_record.get('line'),
                            odds_record.get('over_under')
                        ))

            # Save complete snapshot
            conn.execute('''
                INSERT INTO odds_snapshots (game_id, timestamp, odds_data, ev_data)
                VALUES (?, ?, ?, ?)
            ''', (
                snapshot.game_id,
                snapshot.timestamp,
                json.dumps(snapshot.odds),
                json.dumps(snapshot.ev_data) if snapshot.ev_data else None
            ))

            conn.commit()

    def get_odds_history(self, game_id: str, hours_back: int = 24) -> List[OddsSnapshot]:
        """Get odds history for a game"""
        cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()

        with self._get_db_connection() as conn:
            snapshots = []
            for row in conn.execute('''
                SELECT timestamp, odds_data, ev_data
                FROM odds_snapshots
                WHERE game_id = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            ''', (game_id, cutoff_time)):

                odds_data = json.loads(row['odds_data'])
                ev_data = json.loads(row['ev_data']) if row['ev_data'] else None

                snapshot = OddsSnapshot(
                    game_id=game_id,
                    timestamp=row['timestamp'],
                    odds=odds_data,
                    ev_data=ev_data
                )
                snapshots.append(snapshot)

            return snapshots

    def save_user_bet(self, user_id: str, game_id: str, bet_type: str,
                     team: str, odds_locked: float, stake: float):
        """Save user bet for tracking"""
        with self._get_db_connection() as conn:
            conn.execute('''
                INSERT INTO user_bets
                (user_id, game_id, bet_type, team, odds_locked, stake, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, game_id, bet_type, team, odds_locked, stake,
                  datetime.now().isoformat()))

            conn.commit()

    def update_bet_result(self, bet_id: int, result: str, payout: float):
        """Update bet result"""
        with self._get_db_connection() as conn:
            conn.execute('''
                UPDATE user_bets
                SET status = 'settled', result = ?, payout = ?
                WHERE id = ?
            ''', (result, payout, bet_id))

            conn.commit()

    def get_user_portfolio(self, user_id: str) -> List[Dict]:
        """Get user's active bets"""
        with self._get_db_connection() as conn:
            bets = []
            for row in conn.execute('''
                SELECT * FROM user_bets
                WHERE user_id = ? AND status = 'active'
                ORDER BY timestamp DESC
            ''', (user_id,)):
                bets.append(dict(row))

            return bets

    def calculate_ev(self, our_prob: float, market_odds: float) -> float:
        """Calculate Expected Value"""
        if market_odds > 0:
            payout = market_odds
            stake = 100
        else:
            payout = 100
            stake = abs(market_odds)

        ev = (our_prob * payout) - ((1 - our_prob) * stake)
        return ev

    def calculate_edge(self, our_prob: float, market_odds: float) -> float:
        """Calculate edge percentage"""
        implied_prob = self._odds_to_prob(market_odds)
        edge = (our_prob - implied_prob) * 100
        return edge

# Global instance
odds_provider = OddsProvider()

async def get_live_odds_for_games(game_ids: List[str]) -> Dict[str, OddsSnapshot]:
    """Convenience function to get live odds"""
    async with OddsProvider() as provider:
        return await provider.get_live_odds(game_ids)
