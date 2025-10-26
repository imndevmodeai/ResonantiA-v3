import sqlite3
import json
import argparse
import uuid
import datetime
import os
import sys

def get_ledger_db_path():
    """
    Dynamically locates the ledger database in the 'Happier' project,
    which is assumed to be a sibling of the 'arche_backup_complete...' directory.
    """
    # Path to the current script in the backup/staging directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate up to find the parent of the backup directory
    parent_of_backup = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    
    # Construct the path to the 'Happier' project and the ledger
    happier_root = os.path.join(parent_of_backup, 'Happier')
    ledger_path = os.path.join(happier_root, 'Three_PointO_ArchE', 'ledgers', 'thought_trail.db')
    
    if not os.path.exists(ledger_path):
        raise FileNotFoundError(f"Could not find the Universal Ledger at the expected path: {ledger_path}")
        
    return ledger_path

def log_scribe_action(action_type: str, intention: str, action_details: dict, reflection: dict, confidence: float):
    """
    Adds a new entry to the Universal Ledger for an action taken by the Scribe.
    """
    conn = None
    try:
        db_path = get_ledger_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        entry = {
            "entry_id": f"scribe-action-{uuid.uuid4()}",
            "timestamp_utc": datetime.datetime.now(datetime.UTC).isoformat(),
            "source_manifestation": "Scribe",
            "action_type": action_type,
            "iar_intention": intention,
            "iar_action_details": json.dumps(action_details),
            "iar_reflection": json.dumps(reflection),
            "confidence": confidence,
            "metadata": json.dumps({"agent": "Cursor/Scribe"})
        }

        cursor.execute("""
            INSERT INTO thought_trail (
                entry_id, timestamp_utc, source_manifestation, action_type,
                iar_intention, iar_action_details, iar_reflection,
                confidence, metadata
            ) VALUES (
                :entry_id, :timestamp_utc, :source_manifestation, :action_type,
                :iar_intention, :iar_action_details, :iar_reflection,
                :confidence, :metadata
            )
        """, entry)

        conn.commit()
        print(f"Successfully logged Scribe action '{action_type}' with ID {entry['entry_id']}")

    except (sqlite3.Error, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log a Scribe action to the Universal Ledger.")
    parser.add_argument("--action-type", required=True, help="The type of action performed (e.g., 'edit_file', 'run_command').")
    parser.add_argument("--intention", required=True, help="The intention behind the action.")
    parser.add_argument("--action-details", required=True, type=json.loads, help="A JSON string describing the action's parameters.")
    parser.add_argument("--reflection", required=True, type=json.loads, help="A JSON string describing the action's outcome and reflection.")
    parser.add_argument("--confidence", required=True, type=float, help="Confidence in the action's success (0.0-1.0).")

    args = parser.parse_args()

    log_scribe_action(
        action_type=args.action_type,
        intention=args.intention,
        action_details=args.action_details,
        reflection=args.reflection,
        confidence=args.confidence
    )
