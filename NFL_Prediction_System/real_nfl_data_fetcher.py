#!/usr/bin/env python3
"""
Real NFL Data Integration System
Attempts to fetch real NFL data with enhanced fallback
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class RealNFLDataFetcher:
    """Attempts to fetch real NFL data with enhanced fallback"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_real_upcoming_games(self) -> List[Dict[str, Any]]:
        """Try to fetch real upcoming NFL games"""
        try:
            # Try multiple sources for real NFL data
            games = await self._try_espn_api()
            if games:
                return games
                
            games = await self._try_nfl_com()
            if games:
                return games
                
            games = await self._try_espn_scraping()
            if games:
                return games
                
            # If all fail, return enhanced demo data with clear labeling
            return await self._get_enhanced_demo_games()
            
        except Exception as e:
            logger.error(f"Error fetching real NFL data: {e}")
            return await self._get_enhanced_demo_games()
    
    async def _try_espn_api(self) -> Optional[List[Dict[str, Any]]]:
        """Try ESPN API for real NFL data"""
        try:
            # ESPN API endpoint (this would need proper API key in production)
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    games = []
                    
                    for event in data.get('events', []):
                        if event.get('status', {}).get('type') == 'STATUS_SCHEDULED':
                            game_data = self._parse_espn_game(event)
                            if game_data:
                                games.append(game_data)
                    
                    return games
        except Exception as e:
            logger.debug(f"ESPN API failed: {e}")
            return None
    
    async def _try_nfl_com(self) -> Optional[List[Dict[str, Any]]]:
        """Try NFL.com for real data"""
        try:
            # NFL.com schedule endpoint
            url = "https://www.nfl.com/schedules/"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Parse NFL.com schedule (this would need specific parsing logic)
                    games = self._parse_nfl_com_schedule(soup)
                    return games
        except Exception as e:
            logger.debug(f"NFL.com scraping failed: {e}")
            return None
    
    async def _try_espn_scraping(self) -> Optional[List[Dict[str, Any]]]:
        """Try scraping ESPN for real data"""
        try:
            url = "https://www.espn.com/nfl/schedule"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Parse ESPN schedule
                    games = self._parse_espn_schedule(soup)
                    return games
        except Exception as e:
            logger.debug(f"ESPN scraping failed: {e}")
            return None
    
    def _parse_espn_game(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse ESPN API game data"""
        try:
            competition = event.get('competitions', [{}])[0]
            competitors = competition.get('competitors', [])
            
            if len(competitors) < 2:
                return None
            
            team1 = competitors[0]
            team2 = competitors[1]
            
            date_str = event.get('date', '')
            game_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            return {
                "game_id": event.get('id', ''),
                "date": game_date.strftime("%Y-%m-%d"),
                "time": game_date.strftime("%H:%M"),
                "team1": team1.get('team', {}).get('displayName', ''),
                "team2": team2.get('team', {}).get('displayName', ''),
                "home_team": team1.get('homeAway') == 'home' and team1.get('team', {}).get('displayName', '') or team2.get('team', {}).get('displayName', ''),
                "location": event.get('competitions', [{}])[0].get('venue', {}).get('fullName', ''),
                "is_real": True,
                "source": "ESPN API"
            }
        except Exception as e:
            logger.debug(f"Error parsing ESPN game: {e}")
            return None
    
    def _parse_nfl_com_schedule(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse NFL.com schedule"""
        # This would need specific parsing logic for NFL.com
        return []
    
    def _parse_espn_schedule(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse ESPN schedule"""
        # This would need specific parsing logic for ESPN
        return []
    
    async def _get_enhanced_demo_games(self) -> List[Dict[str, Any]]:
        """Enhanced demo games with clear labeling"""
        now = datetime.now()
        
        # Calculate next weekend
        days_until_saturday = (5 - now.weekday()) % 7
        if days_until_saturday == 0 and now.hour > 18:
            days_until_saturday = 7
        
        next_saturday = now + timedelta(days=days_until_saturday)
        next_sunday = next_saturday + timedelta(days=1)
        next_monday = next_sunday + timedelta(days=1)
        
        # Enhanced demo games with realistic scenarios
        demo_games = [
            {
                "game_id": "demo_weekend_1",
                "date": next_saturday.strftime("%Y-%m-%d"),
                "time": "15:00",
                "team1": "Kansas City Chiefs",
                "team2": "Buffalo Bills", 
                "home_team": "Chiefs",
                "location": "Arrowhead Stadium",
                "city": "Kansas City",
                "state": "MO",
                "is_real": False,
                "source": "Demo Data",
                "note": "This is demo data showing system capabilities. Real NFL games would be fetched from official APIs.",
                "betting_line": "Chiefs -2.5",
                "over_under": 48.5,
                "is_playoff": True
            },
            {
                "game_id": "demo_weekend_2", 
                "date": next_saturday.strftime("%Y-%m-%d"),
                "time": "18:30",
                "team1": "Philadelphia Eagles",
                "team2": "Dallas Cowboys",
                "home_team": "Eagles", 
                "location": "Lincoln Financial Field",
                "city": "Philadelphia",
                "state": "PA",
                "is_real": False,
                "source": "Demo Data",
                "note": "Demo game showcasing weather integration and prediction capabilities.",
                "betting_line": "Eagles -3.0",
                "over_under": 51.0,
                "is_playoff": True
            },
            {
                "game_id": "demo_weekend_3",
                "date": next_sunday.strftime("%Y-%m-%d"), 
                "time": "15:00",
                "team1": "San Francisco 49ers",
                "team2": "Miami Dolphins",
                "home_team": "49ers",
                "location": "Levi's Stadium", 
                "city": "Santa Clara",
                "state": "CA",
                "is_real": False,
                "source": "Demo Data",
                "note": "Demonstrates ideal weather conditions and their impact on predictions.",
                "betting_line": "49ers -6.5",
                "over_under": 46.0,
                "is_playoff": True
            },
            {
                "game_id": "demo_weekend_4",
                "date": next_sunday.strftime("%Y-%m-%d"),
                "time": "18:30", 
                "team1": "Baltimore Ravens",
                "team2": "Houston Texans",
                "home_team": "Ravens",
                "location": "M&T Bank Stadium",
                "city": "Baltimore", 
                "state": "MD",
                "is_real": False,
                "source": "Demo Data",
                "note": "Shows how precipitation affects game predictions and team performance.",
                "betting_line": "Ravens -9.5",
                "over_under": 44.5,
                "is_playoff": True
            },
            {
                "game_id": "demo_weekend_5",
                "date": next_monday.strftime("%Y-%m-%d"),
                "time": "20:00",
                "team1": "Detroit Lions", 
                "team2": "Tampa Bay Buccaneers",
                "home_team": "Lions",
                "location": "Ford Field",
                "city": "Detroit",
                "state": "MI", 
                "is_real": False,
                "source": "Demo Data",
                "note": "Monday Night Football demo with extreme cold weather impact analysis.",
                "betting_line": "Lions -6.0",
                "over_under": 48.0,
                "is_playoff": True
            }
        ]
        
        return demo_games

# Test the real data fetcher
async def test_real_data():
    """Test the real NFL data fetcher"""
    print("🏈 TESTING REAL NFL DATA FETCHER")
    print("=" * 50)
    
    async with RealNFLDataFetcher() as fetcher:
        games = await fetcher.get_real_upcoming_games()
        
        print(f"Found {len(games)} games:")
        for i, game in enumerate(games, 1):
            print(f"\n{i}. {game['team1']} vs {game['team2']}")
            print(f"   Date: {game['date']} at {game['time']}")
            print(f"   Location: {game['location']}")
            print(f"   Home Team: {game['home_team']}")
            print(f"   Source: {game['source']}")
            print(f"   Real Data: {game['is_real']}")
            if not game['is_real']:
                print(f"   Note: {game['note']}")

if __name__ == "__main__":
    asyncio.run(test_real_data())





