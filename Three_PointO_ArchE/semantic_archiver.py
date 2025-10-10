"""
SemanticArchiver Integration: Long-term Memory for ThoughtTrail
==============================================================

The SemanticArchiver serves as ArchE's long-term memory system, compressing
and storing ThoughtTrail entries for future analysis and retrieval.

This implementation provides:
- Periodic compression of ThoughtTrail entries
- Semantic indexing for efficient retrieval
- Integration with ThoughtTrail for automatic archiving
- Query capabilities for historical analysis
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from Three_PointO_ArchE.nexus_interface import NexusInterface
from Three_PointO_ArchE.thought_trail import thought_trail, IAREntry

logger = logging.getLogger(__name__)

class SemanticArchiver:
    """
    The Librarian of Time - ArchE's long-term memory system.
    
    Compresses and stores ThoughtTrail entries for future analysis,
    ensuring that the system's complete history is preserved in a
    queryable format while preventing memory overflow.
    """
    
    def __init__(self, archive_dir: str = "archives", compression_interval: int = 3600):
        """
        Initialize the SemanticArchiver.
        
        Args:
            archive_dir: Directory to store archived entries
            compression_interval: Seconds between compression cycles
        """
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(exist_ok=True)
        self.compression_interval = compression_interval
        self.last_compression = datetime.now()
        self.nexus = None
        
        # Archive statistics
        self.stats = {
            'total_archived': 0,
            'compression_cycles': 0,
            'last_compression_time': None,
            'archive_files': []
        }
        
        logger.info(f"[SemanticArchiver] Initialized with archive_dir={archive_dir}")
    
    def inject_nexus(self, nexus_instance: NexusInterface) -> None:
        """Inject NexusInterface for event communication."""
        self.nexus = nexus_instance
        logger.info("[SemanticArchiver] NexusInterface injected")
    
    def compress_thoughttrail(self) -> Dict[str, Any]:
        """
        Compress recent ThoughtTrail entries into semantic representations.
        
        This is the core archiving process that transforms raw IAR entries
        into compressed, searchable semantic representations.
        
        Returns:
            Dict containing compression results
        """
        try:
            # Get entries that haven't been archived yet
            recent_entries = thought_trail.get_recent_entries(minutes=60)
            
            if not recent_entries:
                logger.info("[SemanticArchiver] No new entries to compress")
                return {'status': 'no_entries', 'compressed': 0}
            
            # Create semantic representations
            semantic_entries = []
            for entry in recent_entries:
                semantic_entry = self._create_semantic_representation(entry)
                semantic_entries.append(semantic_entry)
            
            # Save to archive file
            archive_file = self._save_to_archive(semantic_entries)
            
            # Update statistics
            self.stats['total_archived'] += len(semantic_entries)
            self.stats['compression_cycles'] += 1
            self.stats['last_compression_time'] = datetime.now().isoformat()
            self.stats['archive_files'].append(archive_file)
            
            # Publish compression event
            if self.nexus:
                self.nexus.publish("semantic_archiver_compression", {
                    'entries_compressed': len(semantic_entries),
                    'archive_file': archive_file,
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"[SemanticArchiver] Compressed {len(semantic_entries)} entries to {archive_file}")
            
            return {
                'status': 'success',
                'compressed': len(semantic_entries),
                'archive_file': archive_file
            }

        except Exception as e:
            logger.error(f"[SemanticArchiver] Error during compression: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _create_semantic_representation(self, entry: IAREntry) -> Dict[str, Any]:
        """
        Create a semantic representation of an IAR entry.
        
        This transforms the raw entry into a compressed, searchable format
        that preserves the essential information while reducing storage size.
        """
        # Extract key semantic elements
        intention = entry.iar.get('intention', '')
        action = entry.iar.get('action', '')
        reflection = entry.iar.get('reflection', '')
        
        # Create semantic summary
        semantic_summary = self._generate_semantic_summary(intention, action, reflection)
        
        # Extract key terms and concepts
        key_terms = self._extract_key_terms(intention + ' ' + reflection)
        
        # Determine semantic category
        category = self._categorize_entry(entry)
        
        return {
            'original_task_id': entry.task_id,
            'timestamp': entry.timestamp,
            'action_type': entry.action_type,
            'confidence': entry.confidence,
            'semantic_summary': semantic_summary,
            'key_terms': key_terms,
            'category': category,
            'intention': intention[:200],  # Truncate for storage
            'reflection': reflection[:200],  # Truncate for storage
            'metadata': {
                'duration_ms': entry.metadata.get('duration_ms', 0),
                'module': entry.metadata.get('module', 'unknown'),
                'decorated': entry.metadata.get('decorated', False)
            }
        }
    
    def _generate_semantic_summary(self, intention: str, action: str, reflection: str) -> str:
        """Generate a semantic summary of the entry."""
        # Simple semantic summarization
        if 'error' in reflection.lower():
            return f"Error in {action}: {reflection[:100]}"
        elif 'success' in reflection.lower():
            return f"Successful {action}: {intention[:100]}"
        else:
            return f"{action}: {intention[:100]}"
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text."""
        # Simple key term extraction
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        key_terms = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Return unique terms
        return list(set(key_terms))[:10]  # Limit to 10 terms
    
    def _categorize_entry(self, entry: IAREntry) -> str:
        """Categorize the entry based on its characteristics."""
        action_type = entry.action_type
        confidence = entry.confidence
        reflection = entry.iar.get('reflection', '').lower()
        
        if 'error' in reflection:
            return 'error'
        elif confidence > 0.9:
            return 'high_confidence'
        elif confidence < 0.7:
            return 'low_confidence'
        elif 'execute' in action_type:
            return 'execution'
        elif 'generate' in action_type:
            return 'generation'
        elif 'search' in action_type:
            return 'search'
        else:
            return 'general'
    
    def _save_to_archive(self, semantic_entries: List[Dict[str, Any]]) -> str:
        """Save semantic entries to archive file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"thoughttrail_archive_{timestamp}.json"
        
        archive_data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'entries_count': len(semantic_entries),
                'compression_version': '1.0'
            },
            'entries': semantic_entries
        }
        
        with open(archive_file, 'w') as f:
            json.dump(archive_data, f, indent=2)
        
        return str(archive_file)
    
    def query_archives(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query archived entries based on criteria.
        
        Args:
            criteria: Query criteria (category, key_terms, date_range, etc.)
            
        Returns:
            List of matching archived entries
        """
        try:
        results = []
            
            # Search through all archive files
            for archive_file in self.archive_dir.glob("thoughttrail_archive_*.json"):
                with open(archive_file, 'r') as f:
                    archive_data = json.load(f)
                
                for entry in archive_data.get('entries', []):
                    if self._matches_archive_criteria(entry, criteria):
                        results.append(entry)
            
            logger.info(f"[SemanticArchiver] Query returned {len(results)} results")
        return results

        except Exception as e:
            logger.error(f"[SemanticArchiver] Error querying archives: {e}")
            return []
    
    def _matches_archive_criteria(self, entry: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if archived entry matches query criteria."""
        for key, value in criteria.items():
            if key == 'category' and entry.get('category') != value:
                return False
            elif key == 'action_type' and entry.get('action_type') != value:
                return False
            elif key == 'key_terms':
                if isinstance(value, list):
                    if not any(term in entry.get('key_terms', []) for term in value):
                        return False
                elif value not in entry.get('key_terms', []):
                    return False
            elif key == 'date_range':
                entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                start_time = datetime.fromisoformat(value.get('start', '1970-01-01'))
                end_time = datetime.fromisoformat(value.get('end', '2100-01-01'))
                if not (start_time <= entry_time <= end_time):
                    return False
            elif key == 'confidence_range':
                confidence = entry.get('confidence', 0)
                min_conf = value.get('min', 0)
                max_conf = value.get('max', 1)
                if not (min_conf <= confidence <= max_conf):
                    return False
        
        return True
    
    def get_archive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive archive statistics."""
        archive_files = list(self.archive_dir.glob("thoughttrail_archive_*.json"))
        
        total_entries = 0
        categories = {}
        action_types = {}
        
        for archive_file in archive_files:
            try:
                with open(archive_file, 'r') as f:
                    archive_data = json.load(f)
                
                entries = archive_data.get('entries', [])
                total_entries += len(entries)
                
                for entry in entries:
                    category = entry.get('category', 'unknown')
                    action_type = entry.get('action_type', 'unknown')
                    
                    categories[category] = categories.get(category, 0) + 1
                    action_types[action_type] = action_types.get(action_type, 0) + 1
                    
            except Exception as e:
                logger.error(f"Error reading archive file {archive_file}: {e}")
        
        return {
            'total_archived_entries': total_entries,
            'archive_files_count': len(archive_files),
            'categories': categories,
            'action_types': action_types,
            'compression_stats': self.stats,
            'archive_directory': str(self.archive_dir)
        }
    
    def should_compress(self) -> bool:
        """Check if it's time to compress ThoughtTrail entries."""
        now = datetime.now()
        time_since_last = (now - self.last_compression).total_seconds()
        return time_since_last >= self.compression_interval
    
    def update_compression_time(self) -> None:
        """Update the last compression time."""
        self.last_compression = datetime.now()

# Global SemanticArchiver instance
semantic_archiver = SemanticArchiver()

def initialize_semantic_archiver(nexus_instance: NexusInterface) -> None:
    """
    Initialize SemanticArchiver integration.
    
    Args:
        nexus_instance: The NexusInterface instance
    """
    semantic_archiver.inject_nexus(nexus_instance)
    logger.info("[SemanticArchiver] Integration initialized")

def periodic_compression_worker():
    """
    Background worker for periodic ThoughtTrail compression.
    This should be run in a separate thread or asyncio task.
    """
    while True:
        try:
            if semantic_archiver.should_compress():
                result = semantic_archiver.compress_thoughttrail()
                semantic_archiver.update_compression_time()
                
                if result['status'] == 'success':
                    logger.info(f"[SemanticArchiver] Periodic compression completed: {result['compressed']} entries")
                else:
                    logger.warning(f"[SemanticArchiver] Periodic compression failed: {result}")
            
            # Sleep for 5 minutes before checking again
            time.sleep(300)
            
        except Exception as e:
            logger.error(f"[SemanticArchiver] Error in compression worker: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

__all__ = [
    'SemanticArchiver',
    'semantic_archiver',
    'initialize_semantic_archiver',
    'periodic_compression_worker'
]