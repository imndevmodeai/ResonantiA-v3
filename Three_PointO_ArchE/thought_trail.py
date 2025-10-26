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

            # Prepare data for insertion according to the schema
            sql_data = {
                "entry_id": entry.task_id,
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
            self.logger.debug(f"ThoughtTrail: Persisted entry {entry.task_id} to Universal Ledger.")

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
    
    def get_recent_entries(self, minutes: int = 60) -> List[IAREntry]:
        """
        DEPRECATED: This method will be removed. Query the ledger directly.
        """
        self.logger.warning("`get_recent_entries` is deprecated. Query the SQLite database directly.")
        return []
    
    def query_entries(self, filter_criteria: Dict[str, Any]) -> List[IAREntry]:
        """
        DEPRECATED: This method will be removed. Query the ledger directly.
        """
        self.logger.warning("`query_entries` is deprecated. Query the SQLite database directly.")
        return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        DEPRECATED: This method will be removed. Query the ledger directly.
        """
        self.logger.warning("`get_statistics` is deprecated. Query the SQLite database directly.")
        return {}
    
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