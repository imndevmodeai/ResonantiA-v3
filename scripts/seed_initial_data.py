#!/usr/bin/env python3
"""
Seed initial NFL insider intelligence database
Adds known player/coach movements for testing
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Three_PointO_ArchE.nfl_insider_database import NFLInsiderDatabase

def seed_initial_data():
    """Seed database with initial known connections"""
    db = NFLInsiderDatabase()
    
    # Example: Known significant trades/movements
    # These would be replaced with real historical data
    
    initial_data = [
        {
            'player_name': 'Example Backup QB',
            'from_team': 'Kansas City Chiefs',
            'to_team': 'Baltimore Ravens',
            'transaction_date': '2025-10-15',
            'transaction_type': 'trade',
            'role': 'backup_qb',
            'position': 'QB',
            'years_with_team': 3,
            'current_status': 'active'
        },
        {
            'player_name': 'Example Coach',
            'from_team': 'Philadelphia Eagles',
            'to_team': 'Dallas Cowboys',
            'transaction_date': '2025-03-01',
            'transaction_type': 'coaching_change',
            'role': 'coach',
            'position': 'Offensive Coordinator',
            'years_with_team': 2,
            'current_status': 'coach'
        }
    ]
    
    print("Seeding initial data...")
    for data in initial_data:
        try:
            db.add_player_movement(**data)
            print(f"✅ Added: {data['player_name']}")
        except Exception as e:
            print(f"⚠️  Error adding {data['player_name']}: {e}")
    
    # Check for alerts
    alerts = db.get_pending_alerts()
    print(f"\n📊 Created {len(alerts)} alerts")
    
    db.close()
    print("\n✅ Initial data seeding complete!")

if __name__ == "__main__":
    seed_initial_data()

