#!/usr/bin/env python3
"""
ThoughtTrail Database Query Utility
====================================

This utility allows you to query the ThoughtTrail SQLite database directly,
retrieving IAR entries for analysis and review.

Usage:
    python query_thought_trail.py                    # Last 100 entries (default)
    python query_thought_trail.py --limit 1000       # Last 1000 entries
    python query_thought_trail.py --limit 50 --json  # Last 50 entries as JSON
    python query_thought_trail.py --action-type "scan_and_prime"  # Filter by action type
    python query_thought_trail.py --min-confidence 0.8            # Filter by confidence
    python query_thought_trail.py --stats                          # Show statistics
"""

import sqlite3
import json
import os
import sys
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Three_PointO_ArchE.ledgers.universal_ledger import LEDGER_DB_PATH

def format_timestamp(iso_str: str) -> str:
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return iso_str

def format_entry(entry: Dict[str, Any], verbose: bool = False) -> str:
    """Format a single entry for display."""
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append(f"Event ID: {entry['event_id']}")
    lines.append(f"Entry ID: {entry['entry_id']}")
    lines.append(f"Timestamp: {format_timestamp(entry['timestamp_utc'])}")
    lines.append(f"Action Type: {entry['action_type']}")
    lines.append(f"Confidence: {entry['confidence']:.3f}" if entry['confidence'] else "Confidence: N/A")
    lines.append(f"Source: {entry['source_manifestation']}")
    
    # Intention
    if entry['iar_intention']:
        lines.append(f"\n📋 Intention:")
        lines.append(f"   {entry['iar_intention'][:200]}{'...' if len(entry['iar_intention']) > 200 else ''}")
    
    # Action Details (parse JSON)
    if entry['iar_action_details']:
        try:
            action_data = json.loads(entry['iar_action_details'])
            lines.append(f"\n⚙️  Action Details:")
            if 'inputs' in action_data:
                inputs_str = json.dumps(action_data['inputs'], indent=2)[:300]
                lines.append(f"   Inputs: {inputs_str}{'...' if len(json.dumps(action_data['inputs'])) > 300 else ''}")
            if 'action' in action_data:
                lines.append(f"   Action: {action_data['action']}")
        except json.JSONDecodeError:
            lines.append(f"\n⚙️  Action Details (raw):")
            lines.append(f"   {entry['iar_action_details'][:200]}...")
    
    # Reflection (parse JSON)
    if entry['iar_reflection']:
        try:
            reflection_data = json.loads(entry['iar_reflection'])
            lines.append(f"\n🔍 Reflection:")
            if 'outputs' in reflection_data:
                outputs_str = json.dumps(reflection_data['outputs'], indent=2)[:300]
                lines.append(f"   Outputs: {outputs_str}{'...' if len(json.dumps(reflection_data['outputs'])) > 300 else ''}")
            if 'reflection' in reflection_data:
                reflection_text = reflection_data['reflection']
                lines.append(f"   Reflection: {reflection_text[:300]}{'...' if len(reflection_text) > 300 else ''}")
        except json.JSONDecodeError:
            lines.append(f"\n🔍 Reflection (raw):")
            lines.append(f"   {entry['iar_reflection'][:200]}...")
    
    # Metadata
    if entry['metadata'] and verbose:
        try:
            metadata = json.loads(entry['metadata'])
            if metadata:
                lines.append(f"\n📊 Metadata:")
                for key, value in list(metadata.items())[:5]:  # Show first 5 metadata items
                    lines.append(f"   {key}: {value}")
        except json.JSONDecodeError:
            pass
    
    return "\n".join(lines)

def query_entries(
    limit: int = 100,
    action_type: Optional[str] = None,
    min_confidence: Optional[float] = None,
    max_confidence: Optional[float] = None,
    since_timestamp: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Query entries from the ThoughtTrail database."""
    if not os.path.exists(LEDGER_DB_PATH):
        print(f"❌ Database not found at: {LEDGER_DB_PATH}")
        print(f"   The ThoughtTrail database hasn't been initialized yet.")
        return []
    
    conn = sqlite3.connect(LEDGER_DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    # Build query
    query = "SELECT * FROM thought_trail WHERE 1=1"
    params = []
    
    if action_type:
        query += " AND action_type = ?"
        params.append(action_type)
    
    if min_confidence is not None:
        query += " AND confidence >= ?"
        params.append(min_confidence)
    
    if max_confidence is not None:
        query += " AND confidence <= ?"
        params.append(max_confidence)
    
    if since_timestamp:
        query += " AND timestamp_utc >= ?"
        params.append(since_timestamp)
    
    # Order by event_id DESC (most recent first) and limit
    query += " ORDER BY event_id DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Convert to list of dictionaries
    entries = []
    for row in rows:
        entries.append({
            'event_id': row['event_id'],
            'entry_id': row['entry_id'],
            'timestamp_utc': row['timestamp_utc'],
            'source_manifestation': row['source_manifestation'],
            'action_type': row['action_type'],
            'iar_intention': row['iar_intention'],
            'iar_action_details': row['iar_action_details'],
            'iar_reflection': row['iar_reflection'],
            'confidence': row['confidence'],
            'metadata': row['metadata']
        })
    
    conn.close()
    return entries

def get_statistics() -> Dict[str, Any]:
    """Get statistics about the ThoughtTrail database."""
    if not os.path.exists(LEDGER_DB_PATH):
        return {"error": "Database not found"}
    
    conn = sqlite3.connect(LEDGER_DB_PATH)
    cursor = conn.cursor()
    
    stats = {}
    
    # Total entries
    cursor.execute("SELECT COUNT(*) FROM thought_trail")
    stats['total_entries'] = cursor.fetchone()[0]
    
    # First and last entry timestamps
    cursor.execute("SELECT MIN(timestamp_utc), MAX(timestamp_utc) FROM thought_trail")
    result = cursor.fetchone()
    stats['first_entry'] = result[0]
    stats['last_entry'] = result[1]
    
    # Action type distribution
    cursor.execute("""
        SELECT action_type, COUNT(*) as count 
        FROM thought_trail 
        GROUP BY action_type 
        ORDER BY count DESC
    """)
    stats['action_types'] = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Average confidence
    cursor.execute("SELECT AVG(confidence) FROM thought_trail WHERE confidence IS NOT NULL")
    result = cursor.fetchone()
    stats['avg_confidence'] = result[0] if result[0] else None
    
    # Confidence distribution
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE confidence < 0.3) as low,
            COUNT(*) FILTER (WHERE confidence >= 0.3 AND confidence < 0.7) as medium,
            COUNT(*) FILTER (WHERE confidence >= 0.7) as high
        FROM thought_trail
        WHERE confidence IS NOT NULL
    """)
    result = cursor.fetchone()
    stats['confidence_distribution'] = {
        'low (<0.3)': result[0],
        'medium (0.3-0.7)': result[1],
        'high (>=0.7)': result[2]
    }
    
    conn.close()
    return stats

def print_statistics(stats: Dict[str, Any]):
    """Print statistics in a readable format."""
    print("\n" + "=" * 80)
    print("📊 THOUGHTTRAIL DATABASE STATISTICS")
    print("=" * 80)
    
    if 'error' in stats:
        print(f"❌ {stats['error']}")
        return
    
    print(f"\n📈 Total Entries: {stats['total_entries']:,}")
    
    if stats['first_entry']:
        print(f"🕐 First Entry: {format_timestamp(stats['first_entry'])}")
        print(f"🕐 Last Entry:  {format_timestamp(stats['last_entry'])}")
    
    if stats['avg_confidence']:
        print(f"\n🎯 Average Confidence: {stats['avg_confidence']:.3f}")
    
    if stats['confidence_distribution']:
        print(f"\n📊 Confidence Distribution:")
        for level, count in stats['confidence_distribution'].items():
            percentage = (count / stats['total_entries']) * 100 if stats['total_entries'] > 0 else 0
            print(f"   {level:20s}: {count:6,} ({percentage:5.1f}%)")
    
    if stats['action_types']:
        print(f"\n🔧 Top Action Types:")
        sorted_types = sorted(stats['action_types'].items(), key=lambda x: x[1], reverse=True)
        for action_type, count in sorted_types[:10]:
            percentage = (count / stats['total_entries']) * 100 if stats['total_entries'] > 0 else 0
            print(f"   {action_type:40s}: {count:6,} ({percentage:5.1f}%)")
    
    print("\n" + "=" * 80)

def main():
    parser = argparse.ArgumentParser(
        description="Query the ThoughtTrail database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--limit', type=int, default=100,
                       help='Number of entries to retrieve (default: 100)')
    parser.add_argument('--action-type', type=str, default=None,
                       help='Filter by action type (e.g., "scan_and_prime")')
    parser.add_argument('--min-confidence', type=float, default=None,
                       help='Minimum confidence threshold (0.0-1.0)')
    parser.add_argument('--max-confidence', type=float, default=None,
                       help='Maximum confidence threshold (0.0-1.0)')
    parser.add_argument('--since', type=str, default=None,
                       help='Only entries since this timestamp (ISO format)')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON instead of formatted text')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show verbose output including metadata')
    parser.add_argument('--stats', action='store_true',
                       help='Show database statistics only')
    parser.add_argument('--compact', action='store_true',
                       help='Show compact one-line format')
    
    args = parser.parse_args()
    
    # If stats only, show statistics and exit
    if args.stats:
        stats = get_statistics()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print_statistics(stats)
        return
    
    # Query entries
    entries = query_entries(
        limit=args.limit,
        action_type=args.action_type,
        min_confidence=args.min_confidence,
        max_confidence=args.max_confidence,
        since_timestamp=args.since
    )
    
    if not entries:
        print(f"❌ No entries found matching criteria.")
        print(f"   Database path: {LEDGER_DB_PATH}")
        if not os.path.exists(LEDGER_DB_PATH):
            print(f"   Database file does not exist. Run initialization first.")
        return
    
    # Output format
    if args.json:
        # JSON output
        print(json.dumps(entries, indent=2))
    elif args.compact:
        # Compact one-line format
        print(f"\n📋 Last {len(entries)} ThoughtTrail Entries (most recent first):\n")
        for entry in entries:
            timestamp = format_timestamp(entry['timestamp_utc'])
            confidence = f"{entry['confidence']:.2f}" if entry['confidence'] else "N/A"
            print(f"[{entry['event_id']:6d}] {timestamp} | {entry['action_type']:30s} | Conf: {confidence:4s} | {entry['entry_id']}")
    else:
        # Formatted output
        print(f"\n📋 Last {len(entries)} ThoughtTrail Entries (most recent first):\n")
        for entry in entries:
            print(format_entry(entry, verbose=args.verbose))
            print()
    
    print(f"\n✅ Retrieved {len(entries)} entries from ThoughtTrail")
    print(f"   Database: {LEDGER_DB_PATH}")

if __name__ == '__main__':
    main()



