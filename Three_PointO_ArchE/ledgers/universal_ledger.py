import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

LEDGER_DIRECTORY = "Three_PointO_ArchE/ledgers"
LEDGER_DB_PATH = os.path.join(LEDGER_DIRECTORY, "thought_trail.db")

def initialize_ledger():
    """
    Creates the SQLite database and the `thought_trail` table if they don't exist.
    This function is idempotent and safe to call on every application start.
    """
    try:
        # Ensure the directory for the database exists
        os.makedirs(LEDGER_DIRECTORY, exist_ok=True)

        # Connect to the database (this will create the file if it doesn't exist)
        conn = sqlite3.connect(LEDGER_DB_PATH)
        cursor = conn.cursor()

        # Create the thought_trail table based on the specification
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
        
        # Add an index for faster lookups by entry_id, which will be common
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_entry_id ON thought_trail (entry_id);
        """)

        conn.commit()
        logger.info(f"Universal Ledger initialized successfully at {LEDGER_DB_PATH}")

    except sqlite3.Error as e:
        logger.error(f"Database error during ledger initialization: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during ledger initialization: {e}")
        raise
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == '__main__':
    # Set up basic logging for standalone execution
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    print("Running Universal Ledger initialization as a standalone script...")
    initialize_ledger()
    print("Initialization complete.")
