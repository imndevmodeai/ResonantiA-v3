"""
ArchE Temporal Core - Canonical Datetime System

This module provides the ONLY approved way to handle timestamps in ArchE.
All datetime operations MUST use these functions to ensure temporal accuracy
and consistency across the entire system.

The Temporal Mandate:
- All timestamps are UTC
- All timestamps use timezone-aware datetime objects
- All timestamps serialize to ISO 8601 with 'Z' suffix
- All durations use monotonic time for accuracy
- All temporal ordering is guaranteed correct

Version: 1.0
Status: CANONICAL
"""

from datetime import datetime, timezone, timedelta
from time import monotonic
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CANONICAL TIMESTAMP FUNCTIONS
# ============================================================================

def now() -> datetime:
    """
    Get the current UTC time as a timezone-aware datetime object.
    
    This is the CANONICAL way to get "now" in ArchE.
    
    Returns:
        datetime: Current time in UTC with timezone info
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import now
        >>> current_time = now()
        >>> print(current_time)
        2025-01-15 07:30:45.123456+00:00
    """
    return datetime.now(timezone.utc)


def now_iso() -> str:
    """
    Get the current UTC time as an ISO 8601 string with 'Z' suffix.
    
    This is the CANONICAL way to get a timestamp string for logging, IAR, etc.
    
    Returns:
        str: ISO 8601 formatted timestamp (e.g., "2025-01-15T07:30:45.123456Z")
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import now_iso
        >>> timestamp = now_iso()
        >>> print(timestamp)
        2025-01-15T07:30:45.123456Z
    """
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def from_iso(iso_string: str) -> datetime:
    """
    Parse an ISO 8601 timestamp string into a timezone-aware datetime.
    
    Handles both 'Z' suffix and '+00:00' offset formats.
    
    Args:
        iso_string: ISO 8601 formatted timestamp
        
    Returns:
        datetime: Timezone-aware datetime object in UTC
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import from_iso
        >>> dt = from_iso("2025-01-15T07:30:45.123456Z")
        >>> print(dt)
        2025-01-15 07:30:45.123456+00:00
    """
    # Handle 'Z' suffix (Zulu time = UTC)
    if iso_string.endswith('Z'):
        iso_string = iso_string[:-1] + '+00:00'
    
    # Parse with timezone awareness
    dt = datetime.fromisoformat(iso_string)
    
    # Ensure UTC
    if dt.tzinfo is None:
        logger.warning(f"Parsed naive datetime from '{iso_string}', assuming UTC")
        dt = dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        dt = dt.astimezone(timezone.utc)
    
    return dt


def timestamp_unix() -> float:
    """
    Get the current Unix timestamp (seconds since epoch).
    
    Useful for numeric comparisons and duration calculations.
    
    Returns:
        float: Unix timestamp
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import timestamp_unix
        >>> ts = timestamp_unix()
        >>> print(ts)
        1705305045.123456
    """
    return datetime.now(timezone.utc).timestamp()


def from_unix(unix_timestamp: float) -> datetime:
    """
    Convert Unix timestamp to timezone-aware datetime.
    
    Args:
        unix_timestamp: Seconds since Unix epoch
        
    Returns:
        datetime: Timezone-aware datetime object in UTC
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import from_unix
        >>> dt = from_unix(1705305045.123456)
        >>> print(dt)
        2025-01-15 07:30:45.123456+00:00
    """
    return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)


# ============================================================================
# DURATION MEASUREMENT (MONOTONIC)
# ============================================================================

class Timer:
    """
    High-precision timer using monotonic clock.
    
    Monotonic time is not affected by system clock adjustments and is
    ideal for measuring durations and performance.
    
    Example:
        >>> from Three_PointO_ArchE.temporal_core import Timer
        >>> timer = Timer()
        >>> # ... do work ...
        >>> elapsed_ms = timer.elapsed_ms()
        >>> print(f"Operation took {elapsed_ms:.2f}ms")
    """
    
    def __init__(self):
        """Start the timer."""
        self._start = monotonic()
    
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        return monotonic() - self._start
    
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return (monotonic() - self._start) * 1000
    
    def elapsed_us(self) -> float:
        """Get elapsed time in microseconds."""
        return (monotonic() - self._start) * 1_000_000
    
    def reset(self):
        """Reset the timer to current time."""
        self._start = monotonic()


# ============================================================================
# TEMPORAL ARITHMETIC
# ============================================================================

def ago(minutes: Optional[int] = None, 
        hours: Optional[int] = None, 
        days: Optional[int] = None) -> datetime:
    """
    Get a datetime in the past relative to now.
    
    Args:
        minutes: Minutes ago
        hours: Hours ago
        days: Days ago
        
    Returns:
        datetime: UTC datetime in the past
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import ago
        >>> one_hour_ago = ago(hours=1)
        >>> print(one_hour_ago)
        2025-01-15 06:30:45.123456+00:00
    """
    delta = timedelta(
        minutes=minutes or 0,
        hours=hours or 0,
        days=days or 0
    )
    return datetime.now(timezone.utc) - delta


def from_now(minutes: Optional[int] = None,
             hours: Optional[int] = None,
             days: Optional[int] = None) -> datetime:
    """
    Get a datetime in the future relative to now.
    
    Args:
        minutes: Minutes from now
        hours: Hours from now
        days: Days from now
        
    Returns:
        datetime: UTC datetime in the future
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import from_now
        >>> deadline = from_now(days=7)
        >>> print(deadline)
        2025-01-22 07:30:45.123456+00:00
    """
    delta = timedelta(
        minutes=minutes or 0,
        hours=hours or 0,
        days=days or 0
    )
    return datetime.now(timezone.utc) + delta


def duration_between(start: Union[datetime, str], 
                     end: Union[datetime, str]) -> timedelta:
    """
    Calculate duration between two timestamps.
    
    Args:
        start: Start time (datetime or ISO string)
        end: End time (datetime or ISO string)
        
    Returns:
        timedelta: Duration between timestamps
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import duration_between
        >>> delta = duration_between("2025-01-15T07:00:00Z", "2025-01-15T08:30:00Z")
        >>> print(delta.total_seconds() / 3600)
        1.5
    """
    if isinstance(start, str):
        start = from_iso(start)
    if isinstance(end, str):
        end = from_iso(end)
    
    return end - start


# ============================================================================
# FORMATTING UTILITIES
# ============================================================================

def format_human(dt: Union[datetime, str]) -> str:
    """
    Format datetime for human reading.
    
    Args:
        dt: Datetime object or ISO string
        
    Returns:
        str: Human-readable format (e.g., "2025-01-15 07:30 UTC")
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import format_human
        >>> print(format_human("2025-01-15T07:30:45Z"))
        2025-01-15 07:30 UTC
    """
    if isinstance(dt, str):
        dt = from_iso(dt)
    
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def format_filename() -> str:
    """
    Get timestamp formatted for use in filenames.
    
    Returns:
        str: Filename-safe timestamp (e.g., "20250115_073045")
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import format_filename
        >>> filename = f"log_{format_filename()}.txt"
        >>> print(filename)
        log_20250115_073045.txt
    """
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def format_log() -> str:
    """
    Get timestamp formatted for log entries.
    
    Returns:
        str: Log-formatted timestamp (e.g., "07:30:45")
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import format_log
        >>> print(f"[{format_log()}] System initialized")
        [07:30:45] System initialized
    """
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


# ============================================================================
# VALIDATION
# ============================================================================

def is_valid_iso(iso_string: str) -> bool:
    """
    Check if a string is a valid ISO 8601 timestamp.
    
    Args:
        iso_string: String to validate
        
    Returns:
        bool: True if valid ISO 8601 format
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import is_valid_iso
        >>> print(is_valid_iso("2025-01-15T07:30:45Z"))
        True
        >>> print(is_valid_iso("not a timestamp"))
        False
    """
    try:
        from_iso(iso_string)
        return True
    except (ValueError, AttributeError):
        return False


# ============================================================================
# MIGRATION HELPERS
# ============================================================================

def migrate_timestamp(old_timestamp: Union[str, datetime, float]) -> str:
    """
    Migrate old timestamp formats to canonical ISO 8601 with 'Z'.
    
    This function accepts:
    - ISO strings (with or without 'Z')
    - datetime objects (naive or aware)
    - Unix timestamps (floats)
    
    And converts them all to canonical ISO 8601 UTC with 'Z' suffix.
    
    Args:
        old_timestamp: Timestamp in any format
        
    Returns:
        str: Canonical ISO 8601 timestamp
        
    Example:
        >>> from Three_PointO_ArchE.temporal_core import migrate_timestamp
        >>> print(migrate_timestamp(1705305045.123))
        2025-01-15T07:30:45.123000Z
    """
    try:
        if isinstance(old_timestamp, str):
            # Already a string, parse and re-format
            dt = from_iso(old_timestamp)
            return dt.isoformat().replace('+00:00', 'Z')
        
        elif isinstance(old_timestamp, datetime):
            # Datetime object
            if old_timestamp.tzinfo is None:
                # Naive datetime, assume UTC
                logger.warning("Migrating naive datetime, assuming UTC")
                dt = old_timestamp.replace(tzinfo=timezone.utc)
            else:
                # Convert to UTC
                dt = old_timestamp.astimezone(timezone.utc)
            return dt.isoformat().replace('+00:00', 'Z')
        
        elif isinstance(old_timestamp, (int, float)):
            # Unix timestamp
            dt = from_unix(old_timestamp)
            return dt.isoformat().replace('+00:00', 'Z')
        
        else:
            raise ValueError(f"Unknown timestamp type: {type(old_timestamp)}")
    
    except Exception as e:
        logger.error(f"Failed to migrate timestamp '{old_timestamp}': {e}")
        # Return current time as fallback
        return now_iso()


# ============================================================================
# CONSTANTS
# ============================================================================

# Epoch reference for ArchE (system initialization)
ARCHE_EPOCH = "2024-01-01T00:00:00Z"

# Common duration constants
SECOND = timedelta(seconds=1)
MINUTE = timedelta(minutes=1)
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
WEEK = timedelta(weeks=1)


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

logger.info("⏰ Temporal Core initialized - All timestamps are UTC")
logger.info(f"   Current system time: {now_iso()}")
logger.info(f"   ArchE Epoch: {ARCHE_EPOCH}")

