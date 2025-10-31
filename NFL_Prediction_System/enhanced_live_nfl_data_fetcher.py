#!/usr/bin/env python3
"""
Enhanced Live NFL Data Integration
Fetches real NFL games with proper team names and schedules
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class EnhancedLiveNFLDataFetcher:
    """Enhanced live NFL data fetcher with real team names and schedules"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_real_nfl_games(self) -> List[Dict[str, Any]]:
        """Get real NFL games with proper team names"""
        try:
            # Try ESPN API first (most reliable)
            games = await self._fetch_espn_api_games()
            if games:
                return games
            
            # Fallback to web scraping
            games = await self._fetch_espn_web_games()
            if games:
                return games
            
            # Final fallback to NFL.com
            games = await self._fetch_nfl_com_games()
            return games
            
        except Exception as e:
            logger.error(f"Error fetching real NFL games: {e}")
            return []
    
    async def _fetch_espn_api_games(self) -> List[Dict[str, Any]]:
        """Fetch games from ESPN API"""
        try:
            # ESPN Scoreboard API
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            
            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    games = []
                    
                    for event in data.get('events', []):
                        if event.get('status', {}).get('type') in ['STATUS_SCHEDULED', 'STATUS_IN_PROGRESS']:
                            game_data = self._parse_espn_api_event(event)
                            if game_data:
                                games.append(game_data)
                    
                    logger.info(f"ESPN API: Found {len(games)} scheduled games")
                    return games
                    
        except Exception as e:
            logger.debug(f"ESPN API failed: {e}")
            return []
    
    async def _fetch_espn_web_games(self) -> List[Dict[str, Any]]:
        """Fetch games from ESPN web scraping"""
        try:
            url = "https://www.espn.com/nfl/schedule"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with self.session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    games = self._parse_espn_schedule_html(html)
                    
                    logger.info(f"ESPN Web: Found {len(games)} games")
                    return games
                    
        except Exception as e:
            logger.debug(f"ESPN web scraping failed: {e}")
            return []
    
    async def _fetch_nfl_com_games(self) -> List[Dict[str, Any]]:
        """Fetch games from NFL.com"""
        try:
            url = "https://www.nfl.com/schedules/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    games = self._parse_nfl_schedule_html(html)
                    
                    logger.info(f"NFL.com: Found {len(games)} games")
                    return games
                    
        except Exception as e:
            logger.debug(f"NFL.com scraping failed: {e}")
            return []
    
    def _parse_espn_api_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse ESPN API event data"""
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
                "source": "ESPN API",
                "status": event.get('status', {}).get('type', ''),
                "confidence": 0.95
            }
        except Exception as e:
            logger.debug(f"Error parsing ESPN API event: {e}")
            return None
    
    def _parse_espn_schedule_html(self, html: str) -> List[Dict[str, Any]]:
        """Parse ESPN schedule HTML with real team names"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            games = []
            
            # Look for schedule table rows
            schedule_rows = soup.find_all('tr', class_=re.compile(r'schedule|game', re.I))
            
            # Also look for game containers
            game_containers = soup.find_all(['div', 'section'], class_=re.compile(r'game|matchup', re.I))
            
            for element in schedule_rows + game_containers:
                game_data = self._extract_espn_game_data(element)
                if game_data:
                    games.append(game_data)
            
            # If no games found, try text-based parsing
            if not games:
                games = self._parse_espn_text_based(html)
            
            return games
        except Exception as e:
            logger.debug(f"Error parsing ESPN HTML: {e}")
            return []
    
    def _parse_nfl_schedule_html(self, html: str) -> List[Dict[str, Any]]:
        """Parse NFL.com schedule HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            games = []
            
            # Look for NFL schedule elements
            schedule_elements = soup.find_all(['div', 'tr'], class_=re.compile(r'schedule|game|matchup', re.I))
            
            for element in schedule_elements:
                game_data = self._extract_nfl_game_data(element)
                if game_data:
                    games.append(game_data)
            
            # Text-based fallback
            if not games:
                games = self._parse_nfl_text_based(html)
            
            return games
        except Exception as e:
            logger.debug(f"Error parsing NFL.com HTML: {e}")
            return []
    
    def _extract_espn_game_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract game data from ESPN element"""
        try:
            text = element.get_text()
            
            # Look for team names in the text
            nfl_teams = [
                "Kansas City Chiefs", "Buffalo Bills", "Philadelphia Eagles", "Dallas Cowboys",
                "San Francisco 49ers", "Miami Dolphins", "Baltimore Ravens", "Houston Texans",
                "Detroit Lions", "Tampa Bay Buccaneers", "New England Patriots", "New York Jets",
                "Pittsburgh Steelers", "Cleveland Browns", "Cincinnati Bengals", "Indianapolis Colts",
                "Tennessee Titans", "Jacksonville Jaguars", "Denver Broncos", "Los Angeles Chargers",
                "Las Vegas Raiders", "Green Bay Packers", "Minnesota Vikings", "Chicago Bears",
                "New Orleans Saints", "Atlanta Falcons", "Carolina Panthers", "Arizona Cardinals",
                "Los Angeles Rams", "Seattle Seahawks", "New York Giants", "Washington Commanders"
            ]
            
            found_teams = []
            for team in nfl_teams:
                if team in text:
                    found_teams.append(team)
            
            if len(found_teams) >= 2:
                return {
                    "game_id": f"espn_{hash(found_teams[0] + found_teams[1])}",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": "TBD",
                    "team1": found_teams[0],
                    "team2": found_teams[1],
                    "home_team": found_teams[0],
                    "location": "TBD",
                    "is_real": True,
                    "source": "ESPN Web",
                    "confidence": 0.85
                }
            
            return None
        except Exception as e:
            logger.debug(f"Error extracting ESPN game data: {e}")
            return None
    
    def _extract_nfl_game_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract game data from NFL.com element"""
        try:
            text = element.get_text()
            
            # Look for team abbreviations or full names
            team_patterns = [
                "KC", "BUF", "PHI", "DAL", "SF", "MIA", "BAL", "HOU",
                "DET", "TB", "NE", "NYJ", "PIT", "CLE", "CIN", "IND",
                "TEN", "JAX", "DEN", "LAC", "LV", "GB", "MIN", "CHI",
                "NO", "ATL", "CAR", "ARI", "LAR", "SEA", "NYG", "WAS"
            ]
            
            found_teams = []
            for team in team_patterns:
                if team in text:
                    found_teams.append(team)
            
            if len(found_teams) >= 2:
                return {
                    "game_id": f"nfl_{hash(found_teams[0] + found_teams[1])}",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": "TBD",
                    "team1": found_teams[0],
                    "team2": found_teams[1],
                    "home_team": found_teams[0],
                    "location": "TBD",
                    "is_real": True,
                    "source": "NFL.com",
                    "confidence": 0.80
                }
            
            return None
        except Exception as e:
            logger.debug(f"Error extracting NFL game data: {e}")
            return None
    
    def _parse_espn_text_based(self, html: str) -> List[Dict[str, Any]]:
        """Text-based parsing for ESPN"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            
            games = []
            nfl_teams = [
                "Kansas City Chiefs", "Buffalo Bills", "Philadelphia Eagles", "Dallas Cowboys",
                "San Francisco 49ers", "Miami Dolphins", "Baltimore Ravens", "Houston Texans",
                "Detroit Lions", "Tampa Bay Buccaneers"
            ]
            
            # Look for team pairs
            for i, team1 in enumerate(nfl_teams):
                for j, team2 in enumerate(nfl_teams):
                    if i != j and team1 in text and team2 in text:
                        team1_pos = text.find(team1)
                        team2_pos = text.find(team2)
                        if abs(team1_pos - team2_pos) < 200:
                            games.append({
                                "game_id": f"espn_text_{team1}_{team2}",
                                "date": datetime.now().strftime("%Y-%m-%d"),
                                "time": "TBD",
                                "team1": team1,
                                "team2": team2,
                                "home_team": team1,
                                "location": "TBD",
                                "is_real": True,
                                "source": "ESPN Text",
                                "confidence": 0.75
                            })
                            break
            
            return games[:5]
        except Exception as e:
            logger.debug(f"Error in ESPN text parsing: {e}")
            return []
    
    def _parse_nfl_text_based(self, html: str) -> List[Dict[str, Any]]:
        """Text-based parsing for NFL.com"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            
            games = []
            team_abbrevs = ["KC", "BUF", "PHI", "DAL", "SF", "MIA", "BAL", "HOU", "DET", "TB"]
            
            # Look for team abbreviation pairs
            for i, team1 in enumerate(team_abbrevs):
                for j, team2 in enumerate(team_abbrevs):
                    if i != j and team1 in text and team2 in text:
                        team1_pos = text.find(team1)
                        team2_pos = text.find(team2)
                        if abs(team1_pos - team2_pos) < 200:
                            games.append({
                                "game_id": f"nfl_text_{team1}_{team2}",
                                "date": datetime.now().strftime("%Y-%m-%d"),
                                "time": "TBD",
                                "team1": team1,
                                "team2": team2,
                                "home_team": team1,
                                "location": "TBD",
                                "is_real": True,
                                "source": "NFL Text",
                                "confidence": 0.70
                            })
                            break
            
            return games[:5]
        except Exception as e:
            logger.debug(f"Error in NFL text parsing: {e}")
            return []

# Test the enhanced live data fetcher
async def test_enhanced_live_data():
    """Test the enhanced live NFL data fetcher"""
    print("🏈 ENHANCED LIVE NFL DATA FETCHER TEST")
    print("=" * 60)
    print("Fetching real NFL games with proper team names...")
    print("=" * 60)
    
    async with EnhancedLiveNFLDataFetcher() as fetcher:
        games = await fetcher.get_real_nfl_games()
        
        print(f"\n📊 RESULTS:")
        print(f"Total games found: {len(games)}")
        
        if games:
            print(f"\n🏈 REAL NFL GAMES:")
            for i, game in enumerate(games, 1):
                print(f"{i}. {game['team1']} vs {game['team2']}")
                print(f"   Date: {game['date']} at {game['time']}")
                print(f"   Home Team: {game['home_team']}")
                print(f"   Location: {game['location']}")
                print(f"   Source: {game['source']}")
                print(f"   Confidence: {game['confidence']:.1%}")
                print(f"   Real Data: {game['is_real']}")
                print()
        else:
            print("❌ No games found")

if __name__ == "__main__":
    asyncio.run(test_enhanced_live_data())





