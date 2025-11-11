#!/usr/bin/env python3
"""
Automated NFL Data Gatherer
Runs via cron jobs to collect data without user interaction
"""

import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Three_PointO_ArchE.nfl_insider_database import NFLInsiderDatabase
from Three_PointO_ArchE.nfl_insider_intelligence import NFLInsiderIntelligence

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nfl_data_gatherer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedDataGatherer:
    """Automated data gathering system"""
    
    def __init__(self):
        self.db = NFLInsiderDatabase()
        self.insider_intel = NFLInsiderIntelligence()
    
    def gather_transactions(self):
        """Gather player/coach transactions from NFL.com"""
        logger.info("Starting transaction gathering...")
        
        try:
            # This would scrape NFL.com transactions
            # For now, using placeholder logic
            from Three_PointO_ArchE.nfl_transaction_scraper import scrape_nfl_transactions
            
            today = datetime.now()
            transactions = scrape_nfl_transactions(today.year, today.month)
            
            new_count = 0
            for trans in transactions:
                movement_id = self.db.add_player_movement(
                    player_name=trans['player_name'],
                    from_team=trans['from_team'],
                    to_team=trans['to_team'],
                    transaction_date=trans['date'],
                    transaction_type=trans['type'],
                    role=trans.get('role', 'player'),
                    position=trans.get('position'),
                    years_with_team=trans.get('years', 0),
                    current_status=trans.get('status', 'active')
                )
                if movement_id:
                    new_count += 1
            
            self.db.update_data_source('nfl_com_transactions', 'active')
            logger.info(f"Gathered {new_count} new transactions")
            
        except Exception as e:
            logger.error(f"Transaction gathering failed: {e}")
            self.db.update_data_source('nfl_com_transactions', 'error', str(e))
            self.db.create_alert('data_gathering_error', 'high', 
                                f"Transaction gathering failed: {e}")
    
    def gather_betting_lines(self):
        """Gather betting line data"""
        logger.info("Starting betting line gathering...")
        
        try:
            # This would fetch from The Odds API or scrape Vegas Insider
            from Three_PointO_ArchE.nfl_betting_line_fetcher import fetch_betting_lines
            
            lines = fetch_betting_lines()
            
            # Store in database (would need betting_lines table)
            # For now, just log
            logger.info(f"Gathered {len(lines)} betting lines")
            self.db.update_data_source('betting_lines', 'active')
            
        except Exception as e:
            logger.error(f"Betting line gathering failed: {e}")
            self.db.update_data_source('betting_lines', 'error', str(e))
    
    def gather_injury_reports(self):
        """Gather injury reports"""
        logger.info("Starting injury report gathering...")
        
        try:
            from Three_PointO_ArchE.nfl_injury_scraper import scrape_injury_reports
            
            week = self._get_current_week()
            injuries = scrape_injury_reports(week)
            
            # Store injuries (would need injuries table)
            logger.info(f"Gathered {len(injuries)} injury reports")
            self.db.update_data_source('injury_reports', 'active')
            
        except Exception as e:
            logger.error(f"Injury report gathering failed: {e}")
            self.db.update_data_source('injury_reports', 'error', str(e))
    
    def check_for_alerts(self):
        """Check for high-priority alerts and send notifications"""
        alerts = self.db.get_pending_alerts(priority='high')
        
        if alerts:
            logger.warning(f"Found {len(alerts)} high-priority alerts")
            # Send notification (email, Slack, etc.)
            self._send_notification(alerts)
    
    def _get_current_week(self) -> int:
        """Calculate current NFL week"""
        # NFL season typically starts first week of September
        season_start = datetime(2025, 9, 4)  # Adjust for actual season start
        today = datetime.now()
        week = ((today - season_start).days // 7) + 1
        return min(week, 18)  # Max 18 weeks
    
    def _send_notification(self, alerts: list):
        """Send notification about alerts"""
        # Could send email, Slack message, etc.
        # For now, just log
        for alert in alerts:
            logger.warning(f"ALERT [{alert['priority']}]: {alert['message']}")
    
    def run_daily_gathering(self):
        """Run all daily data gathering tasks"""
        logger.info("=" * 60)
        logger.info("Starting daily NFL data gathering")
        logger.info("=" * 60)
        
        self.gather_transactions()
        self.gather_betting_lines()
        self.gather_injury_reports()
        self.check_for_alerts()
        
        logger.info("Daily gathering complete")
    
    def run_weekly_gathering(self):
        """Run weekly data gathering tasks"""
        logger.info("=" * 60)
        logger.info("Starting weekly NFL data gathering")
        logger.info("=" * 60)
        
        # Update practice squad rosters
        # Update coaching staff changes
        # Update advanced metrics
        
        logger.info("Weekly gathering complete")
    
    def close(self):
        """Cleanup"""
        self.db.close()


def main():
    """Main entry point for cron job"""
    gatherer = AutomatedDataGatherer()
    
    try:
        # Determine what to run based on day of week
        today = datetime.now().weekday()
        
        if today == 0:  # Monday - Weekly tasks
            gatherer.run_weekly_gathering()
        else:  # Daily tasks
            gatherer.run_daily_gathering()
            
    except Exception as e:
        logger.error(f"Data gathering failed: {e}", exc_info=True)
        gatherer.db.create_alert('system_error', 'high', f"Data gathering system error: {e}")
    finally:
        gatherer.close()


if __name__ == "__main__":
    main()

