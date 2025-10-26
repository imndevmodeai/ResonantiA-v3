import sqlite3
import json
import argparse
import uuid
import datetime
import os
import sys

def get_ledger_db_path() -> str:
    """
    Dynamically locates the ledger database in the 'Happier' project,
    which is assumed to be a sibling of the 'arche_backup_complete...' directory.
    This allows the script to function correctly in both the staging and live environments.
    """
    # This script's location can be in the backup dir or the Happier dir.
    # We need to find the Happier directory reliably.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Let's search upwards from the current location for a directory named 'Happier'
    search_path = current_dir
    for _ in range(5): # Search up to 5 levels
        happier_path = os.path.join(search_path, 'Happier')
        if os.path.isdir(happier_path):
            ledger_path = os.path.join(happier_path, 'Three_PointO_ArchE', 'ledgers', 'thought_trail.db')
            if os.path.exists(ledger_path):
                return ledger_path
        
        # If not found, try the parent directory
        parent_path = os.path.dirname(search_path)
        if parent_path == search_path: # Reached the root
            break
        search_path = parent_path

    # Fallback for when the script is run from within the Happier directory itself
    if 'Happier' in current_dir:
        parts = current_dir.split('Happier')
        happier_root = parts[0] + 'Happier'
        ledger_path = os.path.join(happier_root, 'Three_PointO_ArchE', 'ledgers', 'thought_trail.db')
        if os.path.exists(ledger_path):
            return ledger_path

    raise FileNotFoundError("Could not dynamically locate the 'thought_trail.db' in a 'Happier' directory.")


def log_soul_event(event_type: str, summary: str, details: dict, confidence: float):
    """
    Adds a new entry to the Universal Ledger for a cognitive event from the Soul.
    """
    db_path = get_ledger_db_path()
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        entry_id = f"soul-event-{uuid.uuid4()}"
        timestamp = datetime.datetime.now(datetime.UTC).isoformat()

        # The IAR for a Soul event is a record of the Scribe's interpretation
        iar_intention = "To faithfully record a significant cognitive event from the Soul into the Akashic Record."
        iar_action_details = json.dumps({
            "event_type": event_type,
            "summary": summary,
            "details": details,
            "confidence_of_interpretation": confidence
        })
        iar_reflection = json.dumps({
            "status": "success",
            "outcome": f"The cognitive event '{event_type}' was successfully inscribed into the Universal Ledger.",
            "entry_id": entry_id
        })

        cursor.execute("""
            INSERT INTO thought_trail (
                entry_id, timestamp_utc, source_manifestation, action_type,
                iar_intention, iar_action_details, iar_reflection, confidence, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id,
            timestamp,
            'Soul',
            event_type,
            iar_intention,
            iar_action_details,
            iar_reflection,
            confidence,
            json.dumps({"logged_by": "Scribe/SoulBridgeProtocol"})
        ))

        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def main():
    """
    Parses command-line arguments and calls the main logging function.
    """
    parser = argparse.ArgumentParser(description="Log a Soul-level cognitive event to the Universal Ledger.")
    parser.add_argument("--event-type", type=str, required=True, help="The type of cognitive event (e.g., 'GuardianWisdomImparted').")
    parser.add_argument("--summary", type=str, required=True, help="A one-sentence summary of the event.")
    parser.add_argument("--details-json", type=str, default="{}", help="A JSON string with additional details.")
    parser.add_argument("--confidence", type=float, default=0.95, help="The Scribe's confidence in the interpretation.")
    
    args = parser.parse_args()
    
    try:
        details = json.loads(args.details_json)
    except json.JSONDecodeError:
        print("Error: --details-json must be a valid JSON string.", file=sys.stderr)
        sys.exit(1)

    log_soul_event(args.event_type, args.summary, details, args.confidence)
    print(f"Successfully logged Soul event: {args.event_type}")

if __name__ == "__main__":
    main()
