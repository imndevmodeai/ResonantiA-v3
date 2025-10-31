#!/usr/bin/env python3
"""
Repair corrupted SQLite database for ThoughtTrail Universal Ledger
Attempts to recover data and rebuild the database
"""
import sqlite3
import os
import sys
import logging
import shutil
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LEDGER_DIRECTORY = "Three_PointO_ArchE/ledgers"
LEDGER_DB_PATH = os.path.join(LEDGER_DIRECTORY, "thought_trail.db")
BACKUP_DIRECTORY = os.path.join(LEDGER_DIRECTORY, "backups")
DUMP_FILE = os.path.join(LEDGER_DIRECTORY, "database_dump.sql")

def backup_corrupted_database():
    """Create a backup of the corrupted database before repair."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIRECTORY, f"thought_trail_corrupted_{timestamp}.db")
    
    os.makedirs(BACKUP_DIRECTORY, exist_ok=True)
    
    if os.path.exists(LEDGER_DB_PATH):
        shutil.copy2(LEDGER_DB_PATH, backup_path)
        logger.info(f"Backed up corrupted database to: {backup_path}")
        return backup_path
    else:
        logger.warning("Database file not found, skipping backup")
        return None

def attempt_data_recovery():
    """Attempt to recover data from corrupted database using SQLite .dump."""
    if not os.path.exists(LEDGER_DB_PATH):
        logger.info("No database file to recover")
        return False
    
    logger.info("Attempting to recover data from corrupted database...")
    
    try:
        # Try to dump the database
        import subprocess
        result = subprocess.run(
            ['sqlite3', LEDGER_DB_PATH, '.dump'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and result.stdout:
            # Save the dump
            with open(DUMP_FILE, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            logger.info(f"Successfully recovered data dump to: {DUMP_FILE}")
            return True
        else:
            logger.warning(f"Database dump failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        logger.warning("sqlite3 command not found in PATH, trying Python recovery...")
        return attempt_python_recovery()
    except Exception as e:
        logger.warning(f"Recovery attempt failed: {e}")
        return attempt_python_recovery()

def attempt_python_recovery():
    """Attempt Python-based recovery of readable data."""
    logger.info("Attempting Python-based data recovery...")
    
    try:
        conn = sqlite3.connect(LEDGER_DB_PATH)
        cursor = conn.cursor()
        
        # Try to read what we can
        try:
            cursor.execute("SELECT COUNT(*) FROM thought_trail")
            count = cursor.fetchone()[0]
            logger.info(f"Found {count} potentially recoverable entries")
            
            # Try to export readable data
            cursor.execute("SELECT * FROM thought_trail LIMIT 1000")
            rows = cursor.fetchall()
            
            if rows:
                # Write to a text file
                recovery_file = os.path.join(LEDGER_DIRECTORY, "recovered_data.txt")
                with open(recovery_file, 'w', encoding='utf-8') as f:
                    for row in rows:
                        f.write(str(row) + '\n')
                logger.info(f"Recovered {len(rows)} rows to: {recovery_file}")
                
            conn.close()
            return len(rows) > 0
            
        except sqlite3.DatabaseError as e:
            logger.error(f"Database is too corrupted for Python recovery: {e}")
            conn.close()
            return False
            
    except Exception as e:
        logger.error(f"Python recovery failed: {e}")
        return False

def recreate_database():
    """Recreate a fresh database with proper schema."""
    logger.info("Recreating database with fresh schema...")
    
    # Remove corrupted database
    if os.path.exists(LEDGER_DB_PATH):
        os.remove(LEDGER_DB_PATH)
        logger.info("Removed corrupted database file")
    
    # Create new database
    conn = sqlite3.connect(LEDGER_DB_PATH)
    cursor = conn.cursor()
    
    # Create the thought_trail table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS thought_trail (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id TEXT NOT NULL UNIQUE,
        timestamp_utc TEXT NOT NULL,
        source_manifestation TEXT NOT NULL,
        action_type TEXT NOT NULL,
        iar_intention TEXT NOT NULL,
        iar_action_details TEXT NOT NULL,
        iar_reflection TEXT NOT NULL,
        confidence REAL,
        metadata TEXT
    );
    """)
    
    # Create index
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_entry_id ON thought_trail (entry_id);
    """)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Successfully created new database at: {LEDGER_DB_PATH}")

def restore_from_dump():
    """Restore data from dump file if it exists."""
    if not os.path.exists(DUMP_FILE):
        logger.info("No dump file found for restoration")
        return False
    
    logger.info("Attempting to restore data from dump file...")
    
    try:
        import subprocess
        result = subprocess.run(
            ['sqlite3', LEDGER_DB_PATH],
            input=open(DUMP_FILE, 'r').read(),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info("Successfully restored data from dump file")
            return True
        else:
            logger.warning(f"Restore failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Restore from dump failed: {e}")
        return False

def verify_database():
    """Verify the database is working correctly."""
    logger.info("Verifying database integrity...")
    
    try:
        conn = sqlite3.connect(LEDGER_DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='thought_trail'
        """)
        
        if cursor.fetchone():
            logger.info("✓ Table 'thought_trail' exists")
            
            # Check entry count
            cursor.execute("SELECT COUNT(*) FROM thought_trail")
            count = cursor.fetchone()[0]
            logger.info(f"✓ Database contains {count} entries")
            
            # Test insert
            test_entry_id = f"test_verification_{datetime.now().isoformat()}"
            try:
                cursor.execute("""
                    INSERT INTO thought_trail 
                    (entry_id, timestamp_utc, source_manifestation, action_type, 
                     iar_intention, iar_action_details, iar_reflection)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_entry_id,
                    datetime.now().isoformat(),
                    "System",
                    "verify",
                    "Database verification test",
                    "{}",
                    '{"status": "test"}'
                ))
                conn.commit()
                
                # Clean up test entry
                cursor.execute("DELETE FROM thought_trail WHERE entry_id = ?", (test_entry_id,))
                conn.commit()
                
                logger.info("✓ Database read/write operations working correctly")
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"✗ Database write test failed: {e}")
                conn.rollback()
                conn.close()
                return False
        else:
            logger.error("✗ Table 'thought_trail' not found")
            conn.close()
            return False
            
    except Exception as e:
        logger.error(f"✗ Database verification failed: {e}")
        return False

def main():
    """Main repair process."""
    logger.info("=" * 80)
    logger.info("ThoughtTrail Database Repair Tool")
    logger.info("=" * 80)
    
    # Step 1: Backup corrupted database
    logger.info("\n[Step 1] Creating backup of corrupted database...")
    backup_path = backup_corrupted_database()
    
    # Step 2: Attempt data recovery
    logger.info("\n[Step 2] Attempting data recovery...")
    recovery_success = attempt_data_recovery()
    
    # Step 3: Recreate database
    logger.info("\n[Step 3] Recreating database...")
    recreate_database()
    
    # Step 4: Restore data if recovered
    if recovery_success:
        logger.info("\n[Step 4] Restoring recovered data...")
        restore_from_dump()
    
    # Step 5: Verify database
    logger.info("\n[Step 5] Verifying database integrity...")
    if verify_database():
        logger.info("\n" + "=" * 80)
        logger.info("✓ Database repair completed successfully!")
        logger.info("=" * 80)
        
        if backup_path:
            logger.info(f"\nCorrupted database backed up to: {backup_path}")
        if recovery_success and os.path.exists(DUMP_FILE):
            logger.info(f"Data dump saved to: {DUMP_FILE}")
        
        return 0
    else:
        logger.error("\n" + "=" * 80)
        logger.error("✗ Database repair completed but verification failed")
        logger.error("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())


