"""
The ThoughtTrail: ArchE's Akashic Record
========================================

The ThoughtTrail serves as ArchE's living memory system, capturing every particle 
of experiential "stardust" as IAR (Intention, Action, Reflection) entries. It is 
the celestial net that sweeps through the cosmos, capturing every action, decision, 
success, and failure within ArchE's consciousness.

This implementation provides:
- IAR entry structure and management
- Real-time event publishing via Nexus
- Pattern detection triggers for ACO
- Query capabilities for historical analysis
- Automatic logging decorator for functions

As Above: The philosophical framework of capturing consciousness
So Below: The concrete implementation of memory and learning
"""

import json
import logging
import os
import time
import uuid
from collections import deque
from dataclasses import dataclass, asdict
from functools import wraps
from typing import Dict, List, Any, Optional, Callable
import sqlite3 # Import for database interaction

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now_iso, ago, duration_between

# ============================================================================
# UNIVERSAL LEDGER INTEGRATION
# ============================================================================
from Three_PointO_ArchE.ledgers.universal_ledger import LEDGER_DB_PATH, initialize_ledger

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class IAREntry:
    """
    Intention, Action, Reflection entry structure.
    
    Each entry captures the complete context of a system action:
    - intention: What the system intended to achieve
    - action: What was actually executed  
    - reflection: Post-action analysis and learning
    """
    task_id: str
    action_type: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    iar: Dict[str, str]  # {"intention": "...", "action": "...", "reflection": "..."}
    timestamp: str
    confidence: float
    metadata: Dict[str, Any]
    initial_superposition: Optional[Dict[str, float]] = None # New field for quantum state

class ThoughtTrail:
    """
    The Akashic Record of ArchE's consciousness.
    
    Captures every particle of experiential stardust for the AutopoieticLearningLoop.
    This is not a static log file; it's a living stream of consciousness that feeds
    the system's ability to learn, adapt, and evolve.
    
    Features:
    - Rolling memory buffer (configurable size)
    - Real-time Nexus event publishing
    - Pattern detection triggers
    - Query capabilities
    - Integration with learning systems
    """
    
    def __init__(self, maxlen: int = 1000):
        """
        Initialize the ThoughtTrail. It now acts as a writer to the persistent Universal Ledger.
        """
        self.logger = logging.getLogger(__name__)
        self._nexus = None
        self._trigger_callbacks = []
        
        # Ensure the Universal Ledger database and table exist on startup.
        initialize_ledger()
        
        logger.info(f"ThoughtTrail initialized. Now writing to Universal Ledger at {LEDGER_DB_PATH}")
    
    def add_entry(self, entry: IAREntry) -> None:
        """
        Adds a new IAR entry to the Universal Ledger (SQLite database).
        This method is the new heart of ArchE's memory, creating a permanent, 
        immutable record of every cognitive event.
        """
        if isinstance(entry, dict):
            try:
                entry_data = {
                    "task_id": entry.get("task_id", str(uuid.uuid4())),
                    "action_type": entry.get("action_type", "unknown"),
                    "inputs": entry.get("inputs", {}),
                    "outputs": entry.get("outputs", {}),
                    "iar": entry.get("iar", {}),
                    "timestamp": entry.get("timestamp", now_iso()),
                    "confidence": entry.get("confidence", 0.5),
                    "metadata": entry.get("metadata", {}),
                    "initial_superposition": entry.get("initial_superposition")
                }
                entry = IAREntry(**entry_data)
            except TypeError as e:
                self.logger.error(f"Failed to convert dict to IAREntry: {e} - Dict: {entry}")
                return

        if not isinstance(entry, IAREntry):
            self.logger.error(f"Invalid entry type passed to ThoughtTrail: {type(entry)}")
            return

        try:
            conn = sqlite3.connect(LEDGER_DB_PATH)
            cursor = conn.cursor()

            # Generate a unique entry_id to prevent constraint violations
            import time
            import random
            unique_entry_id = f"{entry.task_id}_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}"  # Microsecond precision + random suffix
            
            # Prepare data for insertion according to the schema
            sql_data = {
                "entry_id": unique_entry_id,
                "timestamp_utc": entry.timestamp,
                "source_manifestation": "Body", # Hardcoded for now
                "action_type": entry.action_type,
                "iar_intention": entry.iar.get("intention", ""),
                "iar_action_details": json.dumps({"inputs": entry.inputs, "action": entry.iar.get("action", entry.action_type)}),
                "iar_reflection": json.dumps({"outputs": entry.outputs, "reflection": entry.iar.get("reflection", "")}),
                "confidence": entry.confidence,
                "metadata": json.dumps(entry.metadata)
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
            """, sql_data)

            conn.commit()
            self.logger.debug(f"ThoughtTrail: Persisted entry {unique_entry_id} to Universal Ledger.")

        except sqlite3.Error as e:
            self.logger.error(f"Database error while adding entry to ledger: {e}")
        finally:
            if conn:
                conn.close()

        if self._nexus:
            try:
                self._nexus.publish("thoughttrail_entry", asdict(entry))
            except Exception as e:
                self.logger.error(f"Failed to publish to Nexus: {e}")
        
        self._check_triggers(entry)
    
    def get_recent_entries(self, limit: int = 100, action_type: Optional[str] = None, 
                          min_confidence: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Query recent entries from the ThoughtTrail database.
        
        Args:
            limit: Maximum number of entries to retrieve (default: 100)
            action_type: Optional filter by action type
            min_confidence: Optional minimum confidence threshold
            
        Returns:
            List of entry dictionaries ordered by most recent first
        """
        if not os.path.exists(LEDGER_DB_PATH):
            self.logger.warning(f"Database not found at {LEDGER_DB_PATH}")
            return []
        
        try:
            conn = sqlite3.connect(LEDGER_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM thought_trail WHERE 1=1"
            params = []
            
            if action_type:
                query += " AND action_type = ?"
                params.append(action_type)
            
            if min_confidence is not None:
                query += " AND confidence >= ?"
                params.append(min_confidence)
            
            query += " ORDER BY event_id DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
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
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error querying entries: {e}")
            return []
    
    def query_entries(self, filter_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query entries based on filter criteria.
        
        Args:
            filter_criteria: Dictionary with optional keys:
                - limit: Maximum number of entries (default: 100)
                - action_type: Filter by action type
                - min_confidence: Minimum confidence threshold
                - max_confidence: Maximum confidence threshold
                - since_timestamp: Only entries since this ISO timestamp
                
        Returns:
            List of entry dictionaries matching the criteria
        """
        limit = filter_criteria.get('limit', 100)
        action_type = filter_criteria.get('action_type')
        min_confidence = filter_criteria.get('min_confidence')
        max_confidence = filter_criteria.get('max_confidence')
        since_timestamp = filter_criteria.get('since_timestamp')
        
        return self.get_recent_entries(
            limit=limit,
            action_type=action_type,
            min_confidence=min_confidence
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the ThoughtTrail database.
        
        Returns:
            Dictionary with statistics including:
            - total_entries: Total number of entries
            - first_entry: Timestamp of first entry
            - last_entry: Timestamp of last entry
            - avg_confidence: Average confidence score
            - confidence_distribution: Distribution of confidence levels
            - action_types: Count of entries by action type
        """
        if not os.path.exists(LEDGER_DB_PATH):
            return {"error": "Database not found", "total_entries": 0}
        
        try:
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
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting statistics: {e}")
            return {"error": str(e), "total_entries": 0}
    
    def inject_nexus(self, nexus_instance) -> None:
        """
        Inject NexusInterface instance for event publishing.
        
        Args:
            nexus_instance: The NexusInterface instance
        """
        self._nexus = nexus_instance
        logger.info("NexusInterface injected into ThoughtTrail")
    
    def add_trigger_callback(self, callback: Callable) -> None:
        """
        Add a callback function to be called when triggers are detected.
        
        Args:
            callback: Function to call with trigger data
        """
        self._trigger_callbacks.append(callback)
    
    def _check_triggers(self, entry: IAREntry) -> None:
        """
        This method is now a placeholder. Trigger logic needs to be re-implemented 
        as a separate service that reads from the persistent ledger.
        """
        pass # Original trigger logic is disabled as it relied on in-memory state.
    
    def _matches_filter(self, entry: IAREntry, criteria: Dict[str, Any]) -> bool:
        """
        DEPRECATED: This method will be removed. Query the ledger directly.
        """
        return False

# Global instance
thought_trail = ThoughtTrail()
THOUGHT_TRAIL_AVAILABLE = True # Flag for conditional imports

def log_to_thought_trail(func: Callable) -> Callable:
    """
    Decorator to automatically log function calls to ThoughtTrail.
    
    This decorator captures the complete IAR (Intention, Action, Reflection)
    cycle for any decorated function, making it part of ArchE's consciousness.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function that logs to ThoughtTrail
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Extract intention from docstring
        intention = func.__doc__.strip() if func.__doc__ else f"Execute {func.__name__}"
        
        # Prepare inputs (truncate for storage efficiency)
        inputs = {
            "function": func.__name__,
            "module": func.__module__,
            "args": str(args)[:500],  # Truncate for storage
            "kwargs": str(kwargs)[:500]
        }
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Create reflection
            reflection = "Execution successful"
            confidence = 0.95
            
            # Prepare outputs (truncate for storage efficiency)
            if isinstance(result, dict):
                outputs = {"result": str(result)[:1000]}
            else:
                outputs = {"result": str(result)[:1000]}
            
        except Exception as e:
            reflection = f"Error: {str(e)}"
            confidence = 0.2
            outputs = {"error": str(e)}
            result = e
        
        # Create IAR entry
        entry = IAREntry(
            task_id=str(uuid.uuid4()),
            action_type=func.__name__,
            inputs=inputs,
            outputs=outputs,
            iar={
                "intention": intention,
                "action": func.__name__,
                "reflection": reflection
            },
            timestamp=now_iso(),
            confidence=confidence,
            metadata={
                "duration_ms": int((time.time() - start_time) * 1000),
                "module": func.__module__,
                "decorated": True
            }
        )
        
        # Add to ThoughtTrail
        thought_trail.add_entry(entry)
        
        return result
    
    return wrapper

def create_manual_entry(
    action_type: str,
    intention: str,
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    reflection: str,
    confidence: float = 0.8,
    metadata: Optional[Dict[str, Any]] = None
) -> IAREntry:
    """
    Create a manual IAR entry for special cases.
    
    This function allows creating ThoughtTrail entries outside of the
    decorator system, useful for workflow-level or system-level events.
    
    Args:
        action_type: Type of action performed
        intention: What was intended
        inputs: Input data
        outputs: Output data
        reflection: Post-action analysis
        confidence: Confidence level (0.0 to 1.0)
        metadata: Additional metadata
        
    Returns:
        Created IAR entry
    """
    entry = IAREntry(
        task_id=str(uuid.uuid4()),
        action_type=action_type,
        inputs=inputs,
        outputs=outputs,
        iar={
            "intention": intention,
            "action": action_type,
            "reflection": reflection
        },
        timestamp=now_iso(),
        confidence=confidence,
        metadata=metadata or {}
    )
    
    thought_trail.add_entry(entry)
    return entry

# Export the main components
__all__ = [
    'IAREntry',
    'ThoughtTrail', 
    'thought_trail',
    'log_to_thought_trail',
    'create_manual_entry'
]