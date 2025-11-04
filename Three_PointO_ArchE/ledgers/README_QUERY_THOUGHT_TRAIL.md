# ThoughtTrail Database Query Utility

## Overview

The ThoughtTrail stores all IAR (Intention, Action, Reflection) entries in a SQLite database located at:
```
Three_PointO_ArchE/ledgers/thought_trail.db
```

## Quick Start

### View Last 1000 Entries (Compact Format)
```bash
python3 Three_PointO_ArchE/ledgers/query_thought_trail.py --limit 1000 --compact
```

### View Last 100 Entries (Full Format)
```bash
python3 Three_PointO_ArchE/ledgers/query_thought_trail.py --limit 100
```

### View Statistics
```bash
python3 Three_PointO_ArchE/ledgers/query_thought_trail.py --stats
```

### Export to JSON
```bash
python3 Three_PointO_ArchE/ledgers/query_thought_trail.py --limit 1000 --json > thought_trail_export.json
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--limit N` | Number of entries to retrieve | 100 |
| `--action-type TYPE` | Filter by action type | None |
| `--min-confidence X` | Minimum confidence (0.0-1.0) | None |
| `--max-confidence X` | Maximum confidence (0.0-1.0) | None |
| `--since TIMESTAMP` | Only entries since this ISO timestamp | None |
| `--json` | Output as JSON | False |
| `--verbose` | Show verbose output with metadata | False |
| `--compact` | Show compact one-line format | False |
| `--stats` | Show database statistics only | False |

## Examples

### Filter by Action Type
```bash
python3 Three_PointO_ArchE/ledgers/query_thought_trail.py --action-type "scan_and_prime" --limit 50
```

### Filter by Confidence
```bash
python3 Three_PointO_ArchE/ledgers/query_thought_trail.py --min-confidence 0.9 --limit 100
```

### View Entries Since a Specific Time
```bash
python3 Three_PointO_ArchE/ledgers/query_thought_trail.py --since "2025-11-02T00:00:00" --limit 500
```

### Export Recent Entries to JSON
```bash
python3 Three_PointO_ArchE/ledgers/query_thought_trail.py --limit 1000 --json > recent_entries.json
```

## Database Schema

The `thought_trail` table has the following structure:

```sql
CREATE TABLE thought_trail (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id TEXT NOT NULL UNIQUE,
    timestamp_utc TEXT NOT NULL,
    source_manifestation TEXT NOT NULL,
    action_type TEXT NOT NULL,
    iar_intention TEXT NOT NULL,
    iar_action_details TEXT NOT NULL,  -- JSON
    iar_reflection TEXT NOT NULL,       -- JSON
    confidence REAL,
    metadata TEXT                       -- JSON
);
```

## Programmatic Access

You can also import and use the query functions programmatically:

```python
from Three_PointO_ArchE.ledgers.query_thought_trail import query_entries, get_statistics

# Get last 100 entries
entries = query_entries(limit=100)

# Get entries filtered by action type
entries = query_entries(limit=50, action_type="scan_and_prime")

# Get statistics
stats = get_statistics()
print(f"Total entries: {stats['total_entries']}")
```

## Direct SQLite Access

You can also query the database directly using SQLite:

```bash
sqlite3 Three_PointO_ArchE/ledgers/thought_trail.db

-- View last 100 entries
SELECT event_id, timestamp_utc, action_type, confidence 
FROM thought_trail 
ORDER BY event_id DESC 
LIMIT 100;

-- Count entries by action type
SELECT action_type, COUNT(*) as count 
FROM thought_trail 
GROUP BY action_type 
ORDER BY count DESC;

-- Exit
.quit
```

## Notes

- The database is automatically created when ThoughtTrail is first initialized
- All timestamps are stored in ISO 8601 format (UTC)
- JSON fields (`iar_action_details`, `iar_reflection`, `metadata`) need to be parsed when reading
- The `entry_id` is unique and includes task_id, timestamp, and random suffix to prevent collisions



