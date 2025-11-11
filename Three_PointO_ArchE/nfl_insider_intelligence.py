#!/usr/bin/env python3
"""
NFL Insider Intelligence Module
Tracks player/coach movement, insider knowledge, and betting line intelligence

This module identifies:
1. Players/coaches who moved between teams (insider knowledge)
2. Backup QBs who know the opponent's system
3. Practice squad players with system familiarity
4. Betting line shading (public vs sharp money)
5. Travel/venue factors affecting lines
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

@dataclass
class InsiderConnection:
    """Connection between teams through player/coach movement"""
    person_name: str
    role: str  # "player", "coach", "practice_squad", "backup_qb"
    from_team: str
    to_team: str
    years_with_team: int
    knowledge_level: str  # "high", "medium", "low"
    specific_knowledge: List[str]  # e.g., ["play calls", "hand signals", "system"]
    impact_level: str  # "critical", "significant", "moderate", "minimal"
    current_status: str  # "active", "inactive", "coach", "cut"
    
@dataclass
class BettingLineIntelligence:
    """Analysis of betting line and public vs sharp money"""
    public_line: float  # The published spread
    sharp_line: float  # The "real" line (adjusted for public betting)
    line_shading: float  # How much the line is shaded (public_line - sharp_line)
    public_money_percentage: float  # % of bets on favorite
    sharp_money_percentage: float  # % of sharp money on favorite
    travel_factor: float  # Points added/subtracted for travel/venue
    team_popularity_factor: float  # Points added for popular teams (Cowboys, etc.)
    real_matchup_line: float  # What the line "should" be based on talent
    edge_opportunity: str  # "fade_public", "follow_sharp", "neutral"
    
@dataclass
class SystemFamiliarity:
    """Analysis of who knows whose system"""
    team1_knows_team2_system: List[InsiderConnection]
    team2_knows_team1_system: List[InsiderConnection]
    advantage: str  # "team1", "team2", "neutral"
    confidence: float
    key_insights: List[str]


class NFLInsiderIntelligence:
    """
    Tracks insider knowledge and betting line intelligence
    """
    
    def __init__(self):
        # This would be populated from a database of player/coach movements
        # For now, using example data structure
        self.insider_connections: List[InsiderConnection] = []
        self._load_insider_database()
    
    def _load_insider_database(self):
        """
        Load database of player/coach movements between teams
        This would be populated from:
        - NFL transaction logs
        - Team roster changes
        - Coaching staff changes
        - Practice squad movements
        """
        # Example data - would be from real database
        # In production, this would query:
        # - NFL.com transactions
        # - Team websites
        # - News articles about trades/cuts
        # - Coaching staff announcements
        
        self.insider_connections = [
            # Example: Backup QB who was on opponent's sideline
            InsiderConnection(
                person_name="Backup QB Example",
                role="backup_qb",
                from_team="Team A",
                to_team="Team B",
                years_with_team=3,
                knowledge_level="high",
                specific_knowledge=["play calls", "hand signals", "audible system", "red zone plays"],
                impact_level="significant",
                current_status="active"
            ),
            # Example: Coach who moved teams
            InsiderConnection(
                person_name="Offensive Coordinator",
                role="coach",
                from_team="Team A",
                to_team="Team B",
                years_with_team=2,
                knowledge_level="critical",
                specific_knowledge=["entire offensive system", "tendencies", "personnel packages"],
                impact_level="critical",
                current_status="coach"
            ),
            # Example: Practice squad player
            InsiderConnection(
                person_name="Practice Squad WR",
                role="practice_squad",
                from_team="Team A",
                to_team="Team B",
                years_with_team=1,
                knowledge_level="medium",
                specific_knowledge=["route concepts", "timing"],
                impact_level="moderate",
                current_status="cut"
            )
        ]
    
    def analyze_insider_connections(self, team1: str, team2: str) -> SystemFamiliarity:
        """
        Analyze insider connections between two teams
        
        Looks for:
        - Players who were on team1 and now on team2 (or vice versa)
        - Coaches who moved between teams
        - Backup QBs who know the system
        - Practice squad players with knowledge
        """
        team1_to_team2 = [
            conn for conn in self.insider_connections
            if conn.from_team == team1 and conn.to_team == team2
        ]
        
        team2_to_team1 = [
            conn for conn in self.insider_connections
            if conn.from_team == team2 and conn.to_team == team1
        ]
        
        # Calculate advantage
        team1_advantage_score = sum(
            self._connection_impact_score(conn) for conn in team2_to_team1
        )
        team2_advantage_score = sum(
            self._connection_impact_score(conn) for conn in team1_to_team2
        )
        
        if team1_advantage_score > team2_advantage_score + 2:
            advantage = "team1"
            confidence = min(0.9, 0.6 + (team1_advantage_score - team2_advantage_score) * 0.1)
        elif team2_advantage_score > team1_advantage_score + 2:
            advantage = "team2"
            confidence = min(0.9, 0.6 + (team2_advantage_score - team1_advantage_score) * 0.1)
        else:
            advantage = "neutral"
            confidence = 0.5
        
        # Generate key insights
        key_insights = []
        for conn in team1_to_team2 + team2_to_team1:
            if conn.impact_level in ["critical", "significant"]:
                key_insights.append(
                    f"{conn.person_name} ({conn.role}) moved from {conn.from_team} to "
                    f"{conn.to_team} with {conn.knowledge_level} knowledge of "
                    f"{', '.join(conn.specific_knowledge)}"
                )
        
        return SystemFamiliarity(
            team1_knows_team2_system=team1_to_team2,
            team2_knows_team1_system=team2_to_team1,
            advantage=advantage,
            confidence=confidence,
            key_insights=key_insights
        )
    
    def _connection_impact_score(self, conn: InsiderConnection) -> float:
        """Calculate impact score for an insider connection"""
        base_scores = {
            "critical": 5.0,
            "significant": 3.0,
            "moderate": 1.5,
            "minimal": 0.5
        }
        
        knowledge_multipliers = {
            "high": 1.5,
            "medium": 1.0,
            "low": 0.5
        }
        
        role_multipliers = {
            "coach": 2.0,  # Coaches have most knowledge
            "backup_qb": 1.5,  # Backup QBs know the system
            "player": 1.0,
            "practice_squad": 0.7
        }
        
        base = base_scores.get(conn.impact_level, 1.0)
        knowledge = knowledge_multipliers.get(conn.knowledge_level, 1.0)
        role = role_multipliers.get(conn.role, 1.0)
        
        return base * knowledge * role
    
    def analyze_betting_line(self, team1: str, team2: str, public_line: float,
                            favorite: str, venue: str = "neutral") -> BettingLineIntelligence:
        """
        Analyze betting line for shading and edge opportunities
        
        Key factors:
        1. Public money (moves line toward popular teams)
        2. Travel factor (road teams get extra points)
        3. Team popularity (Cowboys, Packers, etc. get shaded)
        4. Sharp money (professional bettors)
        """
        # Popular teams that get extra shading
        popular_teams = {
            "Dallas Cowboys": 1.5,
            "Green Bay Packers": 1.0,
            "Pittsburgh Steelers": 1.0,
            "New England Patriots": 0.5,
            "Kansas City Chiefs": 0.5
        }
        
        # Travel factors (road teams typically get 2-3 points)
        travel_factor = 2.5 if venue != "home" else 0.0
        
        # Team popularity shading
        team1_popularity = popular_teams.get(team1, 0.0)
        team2_popularity = popular_teams.get(team2, 0.0)
        
        # If favorite is popular team, line is shaded in their favor
        if favorite == team1:
            popularity_shading = team1_popularity
        elif favorite == team2:
            popularity_shading = team2_popularity
        else:
            popularity_shading = 0.0
        
        # Calculate "real" line (remove shading)
        # Public typically bets 60-70% on favorite
        public_money_pct = 0.65  # Would be from real betting data
        
        # Sharp money typically fades public (bets against public)
        sharp_money_pct = 1.0 - public_money_pct
        
        # Line shading = how much the line moved due to public betting
        total_shading = travel_factor + popularity_shading
        
        # Real matchup line (what it should be based on talent)
        sharp_line = public_line - total_shading
        
        # Determine edge opportunity
        if sharp_money_pct > 0.6:
            edge = "follow_sharp"  # Sharp money is heavy on one side
        elif public_money_pct > 0.7:
            edge = "fade_public"  # Public is too heavy, fade them
        else:
            edge = "neutral"
        
        return BettingLineIntelligence(
            public_line=public_line,
            sharp_line=sharp_line,
            line_shading=total_shading,
            public_money_percentage=public_money_pct,
            sharp_money_percentage=sharp_money_pct,
            travel_factor=travel_factor,
            team_popularity_factor=popularity_shading,
            real_matchup_line=sharp_line,
            edge_opportunity=edge
        )
    
    def search_insider_connections(self, team1: str, team2: str) -> List[InsiderConnection]:
        """
        Search for all insider connections between two teams
        
        This would search:
        - NFL transaction database
        - Team roster history
        - Coaching staff history
        - Practice squad rosters
        - News articles about trades/cuts
        """
        connections = []
        
        # Search for players who moved between teams
        # (In production, this would query real databases)
        for conn in self.insider_connections:
            if (conn.from_team == team1 and conn.to_team == team2) or \
               (conn.from_team == team2 and conn.to_team == team1):
                connections.append(conn)
        
        return connections
    
    def get_backup_qb_insights(self, team1: str, team2: str) -> List[Dict[str, Any]]:
        """
        Find backup QBs who were on opponent's sideline
        
        These players have intimate knowledge of:
        - Play calls
        - Hand signals
        - Audible system
        - Red zone tendencies
        - Two-minute drill plays
        """
        insights = []
        
        for conn in self.insider_connections:
            if conn.role == "backup_qb":
                if (conn.from_team == team1 and conn.to_team == team2) or \
                   (conn.from_team == team2 and conn.to_team == team1):
                    insights.append({
                        "player": conn.person_name,
                        "current_team": conn.to_team,
                        "former_team": conn.from_team,
                        "years_knowledge": conn.years_with_team,
                        "knowledge_areas": conn.specific_knowledge,
                        "impact": conn.impact_level,
                        "insight": f"{conn.person_name} spent {conn.years_with_team} years on {conn.from_team}'s "
                                  f"sideline and knows their {', '.join(conn.specific_knowledge)}"
                    })
        
        return insights
    
    def get_coaching_staff_insights(self, team1: str, team2: str) -> List[Dict[str, Any]]:
        """
        Find coaching staff members who moved between teams
        
        These have the most valuable insider knowledge:
        - Entire offensive/defensive system
        - Tendencies and play-calling patterns
        - Personnel preferences
        - Game planning strategies
        """
        insights = []
        
        for conn in self.insider_connections:
            if conn.role == "coach":
                if (conn.from_team == team1 and conn.to_team == team2) or \
                   (conn.from_team == team2 and conn.to_team == team1):
                    insights.append({
                        "coach": conn.person_name,
                        "current_team": conn.to_team,
                        "former_team": conn.from_team,
                        "years_knowledge": conn.years_with_team,
                        "knowledge_areas": conn.specific_knowledge,
                        "impact": conn.impact_level,
                        "insight": f"{conn.person_name} was on {conn.from_team}'s coaching staff for "
                                  f"{conn.years_with_team} years and knows their {', '.join(conn.specific_knowledge)}"
                    })
        
        return insights


def analyze_insider_intelligence(team1: str, team2: str, public_line: float,
                                 favorite: str, venue: str = "neutral") -> Dict[str, Any]:
    """
    Comprehensive insider intelligence analysis
    
    Returns:
        - System familiarity analysis
        - Betting line intelligence
        - Backup QB insights
        - Coaching staff insights
        - Edge opportunities
    """
    intelligence = NFLInsiderIntelligence()
    
    # Analyze insider connections
    system_familiarity = intelligence.analyze_insider_connections(team1, team2)
    
    # Analyze betting line
    line_intelligence = intelligence.analyze_betting_line(team1, team2, public_line, favorite, venue)
    
    # Get specific insights
    backup_qb_insights = intelligence.get_backup_qb_insights(team1, team2)
    coaching_insights = intelligence.get_coaching_staff_insights(team1, team2)
    
    # Determine edge opportunities
    edge_opportunities = []
    
    if system_familiarity.advantage != "neutral":
        edge_opportunities.append({
            "type": "insider_knowledge",
            "team": team1 if system_familiarity.advantage == "team1" else team2,
            "advantage": f"{system_familiarity.advantage} has insider knowledge advantage",
            "confidence": system_familiarity.confidence,
            "insights": system_familiarity.key_insights
        })
    
    if line_intelligence.edge_opportunity != "neutral":
        edge_opportunities.append({
            "type": "betting_line",
            "opportunity": line_intelligence.edge_opportunity,
            "public_line": public_line,
            "sharp_line": line_intelligence.sharp_line,
            "shading": line_intelligence.line_shading,
            "recommendation": f"Line is shaded by {line_intelligence.line_shading:.1f} points. "
                            f"Real matchup line: {line_intelligence.sharp_line:.1f}"
        })
    
    return {
        "system_familiarity": {
            "advantage": system_familiarity.advantage,
            "confidence": system_familiarity.confidence,
            "team1_knows_team2": len(system_familiarity.team1_knows_team2_system),
            "team2_knows_team1": len(system_familiarity.team2_knows_team1_system),
            "key_insights": system_familiarity.key_insights
        },
        "betting_line_intelligence": {
            "public_line": line_intelligence.public_line,
            "sharp_line": line_intelligence.sharp_line,
            "line_shading": line_intelligence.line_shading,
            "travel_factor": line_intelligence.travel_factor,
            "popularity_factor": line_intelligence.team_popularity_factor,
            "real_matchup_line": line_intelligence.real_matchup_line,
            "edge_opportunity": line_intelligence.edge_opportunity,
            "public_money_pct": line_intelligence.public_money_percentage,
            "sharp_money_pct": line_intelligence.sharp_money_percentage
        },
        "backup_qb_insights": backup_qb_insights,
        "coaching_staff_insights": coaching_insights,
        "edge_opportunities": edge_opportunities
    }

