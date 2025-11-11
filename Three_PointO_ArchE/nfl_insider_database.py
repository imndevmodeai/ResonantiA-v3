#!/usr/bin/env python3
"""
NFL Insider Intelligence Database
Automated tracking of player/coach movements and insider connections
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib

logger = logging.getLogger(__name__)

class NFLInsiderDatabase:
    """
    Database for tracking insider connections and system familiarity
    This is unique data that can't be easily scraped - we build it ourselves
    """
    
    def __init__(self, db_path: str = "data/nfl_insider_intelligence.db"):
        """Initialize database connection"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Player/Coach Movements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                position TEXT,
                from_team TEXT NOT NULL,
                to_team TEXT NOT NULL,
                transaction_date DATE,
                transaction_type TEXT,
                years_with_team INTEGER,
                role TEXT,
                current_status TEXT,
                knowledge_level TEXT,
                specific_knowledge TEXT,  -- JSON array of knowledge areas
                impact_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_name, from_team, to_team, transaction_date)
            )
        """)
        
        # Coaching Staff Movements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coaching_staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coach_name TEXT NOT NULL,
                position TEXT,
                from_team TEXT NOT NULL,
                to_team TEXT NOT NULL,
                start_date DATE,
                end_date DATE,
                years_with_team INTEGER,
                knowledge_level TEXT,
                specific_knowledge TEXT,  -- JSON array
                impact_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(coach_name, from_team, to_team, start_date)
            )
        """)
        
        # Practice Squad Tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS practice_squad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                position TEXT,
                team TEXT NOT NULL,
                previous_teams TEXT,  -- JSON array
                years_on_practice_squad INTEGER,
                current_status TEXT,
                knowledge_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_name, team, created_at)
            )
        """)
        
        # Insider Connections (derived from movements)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insider_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name TEXT NOT NULL,
                role TEXT,
                from_team TEXT NOT NULL,
                to_team TEXT NOT NULL,
                connection_type TEXT,  -- 'player', 'coach', 'practice_squad', 'backup_qb'
                years_with_team INTEGER,
                knowledge_level TEXT,
                specific_knowledge TEXT,
                impact_score REAL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes separately
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_teams ON insider_connections(from_team, to_team)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_active ON insider_connections(is_active)")
        
        # Data Source Tracking (for automation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                source_type TEXT,  -- 'api', 'scraping', 'manual'
                last_updated TIMESTAMP,
                update_frequency TEXT,  -- 'daily', 'weekly', 'real-time'
                status TEXT,  -- 'active', 'inactive', 'error'
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_name)
            )
        """)
        
        # Alerts/Notifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,  -- 'new_connection', 'line_movement', 'injury', 'trade'
                priority TEXT,  -- 'high', 'medium', 'low'
                message TEXT,
                data TEXT,  -- JSON
                sent_at TIMESTAMP,
                acknowledged BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes separately
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON alerts(priority, acknowledged)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created ON alerts(created_at)")
        
        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def add_player_movement(self, player_name: str, from_team: str, to_team: str,
                           transaction_date: str, **kwargs) -> int:
        """Add player movement record"""
        cursor = self.conn.cursor()
        
        # Calculate knowledge level based on role and years
        role = kwargs.get('role', 'player')
        years = kwargs.get('years_with_team', 0)
        
        if role == 'backup_qb':
            knowledge_level = 'high' if years >= 2 else 'medium'
            specific_knowledge = json.dumps(['play calls', 'hand signals', 'audible system', 'red zone plays'])
        elif role == 'coach':
            knowledge_level = 'critical'
            specific_knowledge = json.dumps(['entire system', 'tendencies', 'personnel packages', 'game planning'])
        elif role == 'practice_squad':
            knowledge_level = 'medium' if years >= 1 else 'low'
            specific_knowledge = json.dumps(['route concepts', 'timing'])
        else:
            knowledge_level = 'low'
            specific_knowledge = json.dumps([])
        
        # Determine impact level
        impact_map = {
            'critical': 'critical',
            'high': 'significant',
            'medium': 'moderate',
            'low': 'minimal'
        }
        impact_level = impact_map.get(knowledge_level, 'minimal')
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO player_movements
                (player_name, position, from_team, to_team, transaction_date,
                 transaction_type, years_with_team, role, current_status,
                 knowledge_level, specific_knowledge, impact_level, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                player_name,
                kwargs.get('position'),
                from_team,
                to_team,
                transaction_date,
                kwargs.get('transaction_type', 'trade'),
                years,
                role,
                kwargs.get('current_status', 'active'),
                knowledge_level,
                specific_knowledge,
                impact_level
            ))
            
            movement_id = cursor.lastrowid
            
            # Also add to insider_connections
            self._add_insider_connection(
                player_name, role, from_team, to_team,
                years, knowledge_level, specific_knowledge, impact_level
            )
            
            # Create alert for significant connections
            if impact_level in ['critical', 'significant']:
                self.create_alert(
                    'new_connection',
                    'high' if impact_level == 'critical' else 'medium',
                    f"{player_name} ({role}) moved from {from_team} to {to_team} with {knowledge_level} insider knowledge"
                )
            
            self.conn.commit()
            return movement_id
            
        except sqlite3.IntegrityError:
            logger.warning(f"Duplicate movement: {player_name} from {from_team} to {to_team}")
            return 0
    
    def _add_insider_connection(self, person_name: str, role: str, from_team: str,
                                to_team: str, years: int, knowledge_level: str,
                                specific_knowledge: str, impact_level: str):
        """Add to insider_connections table"""
        cursor = self.conn.cursor()
        
        # Calculate impact score
        base_scores = {'critical': 5.0, 'significant': 3.0, 'moderate': 1.5, 'minimal': 0.5}
        knowledge_mult = {'high': 1.5, 'medium': 1.0, 'low': 0.5}
        role_mult = {'coach': 2.0, 'backup_qb': 1.5, 'player': 1.0, 'practice_squad': 0.7}
        
        base = base_scores.get(impact_level, 1.0)
        know = knowledge_mult.get(knowledge_level, 1.0)
        role_m = role_mult.get(role, 1.0)
        impact_score = base * know * role_m
        
        connection_type = 'backup_qb' if role == 'backup_qb' else role
        
        cursor.execute("""
            INSERT OR REPLACE INTO insider_connections
            (person_name, role, from_team, to_team, connection_type,
             years_with_team, knowledge_level, specific_knowledge,
             impact_score, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            person_name, role, from_team, to_team, connection_type,
            years, knowledge_level, specific_knowledge, impact_score
        ))
    
    def get_insider_connections(self, team1: str, team2: str) -> List[Dict]:
        """Get all insider connections between two teams"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM insider_connections
            WHERE is_active = 1
            AND ((from_team = ? AND to_team = ?) OR (from_team = ? AND to_team = ?))
            ORDER BY impact_score DESC
        """, (team1, team2, team2, team1))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def create_alert(self, alert_type: str, priority: str, message: str, data: Dict = None):
        """Create an alert for review"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts (alert_type, priority, message, data, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            alert_type,
            priority,
            message,
            json.dumps(data) if data else None
        ))
        
        self.conn.commit()
        logger.info(f"Alert created: {priority} - {message}")
    
    def get_pending_alerts(self, priority: str = None) -> List[Dict]:
        """Get unacknowledged alerts"""
        cursor = self.conn.cursor()
        
        if priority:
            cursor.execute("""
                SELECT * FROM alerts
                WHERE acknowledged = 0 AND priority = ?
                ORDER BY created_at DESC
                LIMIT 50
            """, (priority,))
        else:
            cursor.execute("""
                SELECT * FROM alerts
                WHERE acknowledged = 0
                ORDER BY priority DESC, created_at DESC
                LIMIT 50
            """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def acknowledge_alert(self, alert_id: int):
        """Mark alert as acknowledged"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE alerts SET acknowledged = 1 WHERE id = ?
        """, (alert_id,))
        self.conn.commit()
    
    def update_data_source(self, source_name: str, status: str, error_message: str = None):
        """Update data source tracking"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO data_sources
            (source_name, status, error_message, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (source_name, status, error_message))
        
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        self.conn.close()

