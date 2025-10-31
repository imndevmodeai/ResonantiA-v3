# --- START OF FILE Three_PointO_ArchE/token_cache_manager.py ---
# ResonantiA Protocol v3.0 - Token Cache Manager
# Provides intelligent caching for LLM API calls to optimize performance and reduce costs.

import hashlib
import json
import time
import os
import pickle
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
import gzip

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Represents a cached LLM response with metadata."""
    query_hash: str
    query_text: str
    model: str
    response: str
    tokens_used: int
    cost_estimate: float
    timestamp: float
    ttl: float  # Time to live in seconds
    cache_type: str  # 'exact', 'semantic', 'partial'
    confidence: float
    metadata: Dict[str, Any]

class TokenCacheManager:
    """
    Intelligent token caching system for LLM API calls.
    
    Features:
    - Multi-level caching (exact, semantic, partial matches)
    - Cost tracking and optimization
    - TTL-based expiration
    - Thread-safe operations
    - Compression for large responses
    - Cache statistics and analytics
    """
    
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 1000, 
                 enable_compression: bool = True, enable_semantic_cache: bool = True):
        """
        Initialize the token cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            max_size_mb: Maximum cache size in megabytes
            enable_compression: Whether to compress cached responses
            enable_semantic_cache: Whether to enable semantic similarity caching
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.enable_compression = enable_compression
        self.enable_semantic_cache = enable_semantic_cache
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'saves': 0,
            'evictions': 0,
            'total_tokens_saved': 0,
            'total_cost_saved': 0.0,
            'cache_size_bytes': 0
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize cache storage
        self._init_cache_storage()
        
        # Background cleanup thread
        self._cleanup_thread = None
        self._start_cleanup_thread()
        
        logger.info(f"TokenCacheManager initialized with max size: {max_size_mb}MB")

    def _init_cache_storage(self):
        """Initialize cache storage (SQLite database)."""
        self.db_path = self.cache_dir / "token_cache.db"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    query_hash TEXT PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    model TEXT NOT NULL,
                    response_compressed BLOB,
                    tokens_used INTEGER,
                    cost_estimate REAL,
                    timestamp REAL,
                    ttl REAL,
                    cache_type TEXT,
                    confidence REAL,
                    metadata TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_model ON cache_entries(model)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON cache_entries(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_type ON cache_entries(cache_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_access_count ON cache_entries(access_count)")
            
            conn.commit()

    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # Run every 5 minutes
                    self._cleanup_expired_entries()
                    self._enforce_size_limit()
                except Exception as e:
                    logger.error(f"Cleanup thread error: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def _generate_query_hash(self, query: str, model: str, **kwargs) -> str:
        """Generate a hash for the query and parameters."""
        # Create a deterministic string representation
        cache_key = {
            'query': query,
            'model': model,
            'parameters': sorted(kwargs.items())
        }
        
        # Generate SHA-256 hash
        hash_input = json.dumps(cache_key, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

    def _compress_response(self, response: str) -> bytes:
        """Compress response text."""
        if not self.enable_compression:
            return response.encode('utf-8')
        
        return gzip.compress(response.encode('utf-8'))

    def _decompress_response(self, compressed_data: bytes) -> str:
        """Decompress response text."""
        if not self.enable_compression:
            return compressed_data.decode('utf-8')
        
        return gzip.decompress(compressed_data).decode('utf-8')

    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """Calculate semantic similarity between two queries."""
        # Simple implementation using word overlap
        # In production, this could use embeddings or more sophisticated NLP
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    def get(self, query: str, model: str, **kwargs) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Get cached response for a query.
        
        Args:
            query: The input query
            model: The model used
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (response, metadata) if found, None otherwise
        """
        with self._lock:
            query_hash = self._generate_query_hash(query, model, **kwargs)
            
            # Try exact match first
            exact_match = self._get_exact_match(query_hash)
            if exact_match:
                self.stats['hits'] += 1
                return exact_match
            
            # Try semantic match if enabled
            if self.enable_semantic_cache:
                semantic_match = self._get_semantic_match(query, model, **kwargs)
                if semantic_match:
                    self.stats['hits'] += 1
                    return semantic_match
            
            # Try partial match
            partial_match = self._get_partial_match(query, model, **kwargs)
            if partial_match:
                self.stats['hits'] += 1
                return partial_match
            
            self.stats['misses'] += 1
            return None

    def _get_exact_match(self, query_hash: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get exact match from cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT response_compressed, tokens_used, cost_estimate, 
                       cache_type, confidence, metadata, timestamp, ttl
                FROM cache_entries 
                WHERE query_hash = ? AND timestamp + ttl > ?
            """, (query_hash, time.time()))
            
            row = cursor.fetchone()
            if row:
                response_compressed, tokens_used, cost_estimate, cache_type, \
                confidence, metadata, timestamp, ttl = row
                
                # Update access statistics
                conn.execute("""
                    UPDATE cache_entries 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE query_hash = ?
                """, (time.time(), query_hash))
                
                response = self._decompress_response(response_compressed)
                metadata_dict = json.loads(metadata) if metadata else {}
                
                return response, {
                    'tokens_used': tokens_used,
                    'cost_estimate': cost_estimate,
                    'cache_type': cache_type,
                    'confidence': confidence,
                    'metadata': metadata_dict,
                    'timestamp': timestamp,
                    'ttl': ttl
                }
        
        return None

    def _get_semantic_match(self, query: str, model: str, **kwargs) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get semantic match from cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT query_text, response_compressed, tokens_used, cost_estimate,
                       cache_type, confidence, metadata, timestamp, ttl
                FROM cache_entries 
                WHERE model = ? AND timestamp + ttl > ?
                ORDER BY access_count DESC, last_accessed DESC
                LIMIT 100
            """, (model, time.time()))
            
            best_match = None
            best_similarity = 0.8  # Minimum similarity threshold
            
            for row in cursor:
                cached_query, response_compressed, tokens_used, cost_estimate, \
                cache_type, confidence, metadata, timestamp, ttl = row
                
                similarity = self._calculate_similarity(query, cached_query)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = {
                        'response': self._decompress_response(response_compressed),
                        'tokens_used': tokens_used,
                        'cost_estimate': cost_estimate,
                        'cache_type': 'semantic',
                        'confidence': confidence * similarity,  # Adjust confidence by similarity
                        'metadata': json.loads(metadata) if metadata else {},
                        'timestamp': timestamp,
                        'ttl': ttl,
                        'similarity': similarity
                    }
            
            if best_match:
                return best_match['response'], best_match
            return None

    def _get_partial_match(self, query: str, model: str, **kwargs) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get partial match from cache (for sub-queries)."""
        # Extract key terms from query
        query_terms = query.lower().split()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT query_text, response_compressed, tokens_used, cost_estimate,
                       cache_type, confidence, metadata, timestamp, ttl
                FROM cache_entries 
                WHERE model = ? AND timestamp + ttl > ?
                ORDER BY access_count DESC, last_accessed DESC
                LIMIT 50
            """, (model, time.time()))
            
            best_match = None
            best_overlap = 0.6  # Minimum overlap threshold
            
            for row in cursor:
                cached_query, response_compressed, tokens_used, cost_estimate, \
                cache_type, confidence, metadata, timestamp, ttl = row
                
                cached_terms = cached_query.lower().split()
                overlap = len(set(query_terms) & set(cached_terms)) / len(set(query_terms))
                
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_match = {
                        'response': self._decompress_response(response_compressed),
                        'tokens_used': tokens_used,
                        'cost_estimate': cost_estimate,
                        'cache_type': 'partial',
                        'confidence': confidence * overlap,  # Adjust confidence by overlap
                        'metadata': json.loads(metadata) if metadata else {},
                        'timestamp': timestamp,
                        'ttl': ttl,
                        'overlap': overlap
                    }
            
            if best_match:
                return best_match['response'], best_match
            return None

    def put(self, query: str, model: str, response: str, tokens_used: int, 
            cost_estimate: float, ttl: float = 3600, cache_type: str = 'exact',
            confidence: float = 1.0, metadata: Optional[Dict[str, Any]] = None):
        """
        Store a response in the cache.
        
        Args:
            query: The input query
            model: The model used
            response: The response to cache
            tokens_used: Number of tokens used
            cost_estimate: Estimated cost
            ttl: Time to live in seconds
            cache_type: Type of cache entry
            confidence: Confidence in the response
            metadata: Additional metadata
        """
        with self._lock:
            query_hash = self._generate_query_hash(query, model)
            compressed_response = self._compress_response(response)
            metadata_json = json.dumps(metadata) if metadata else None
            timestamp = time.time()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache_entries 
                    (query_hash, query_text, model, response_compressed, tokens_used,
                     cost_estimate, timestamp, ttl, cache_type, confidence, metadata,
                     access_count, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                """, (query_hash, query, model, compressed_response, tokens_used,
                      cost_estimate, timestamp, ttl, cache_type, confidence,
                      metadata_json, timestamp))
                
                conn.commit()
            
            self.stats['saves'] += 1
            self.stats['total_tokens_saved'] += tokens_used
            self.stats['total_cost_saved'] += cost_estimate
            
            logger.debug(f"Cached response for query: {query[:50]}... (tokens: {tokens_used})")

    def _cleanup_expired_entries(self):
        """Remove expired cache entries."""
        with self._lock:
            current_time = time.time()
            
            with sqlite3.connect(self.db_path) as conn:
                # Get expired entries
                cursor = conn.execute("""
                    SELECT query_hash, tokens_used, cost_estimate
                    FROM cache_entries 
                    WHERE timestamp + ttl < ?
                """, (current_time,))
                
                expired_entries = cursor.fetchall()
                
                # Remove expired entries
                conn.execute("DELETE FROM cache_entries WHERE timestamp + ttl < ?", (current_time,))
                conn.commit()
                
                # Update statistics
                for _, tokens_used, cost_estimate in expired_entries:
                    self.stats['evictions'] += 1
                    self.stats['total_tokens_saved'] -= tokens_used
                    self.stats['total_cost_saved'] -= cost_estimate
            
            logger.debug(f"Cleaned up {len(expired_entries)} expired cache entries")

    def _enforce_size_limit(self):
        """Enforce maximum cache size by removing least recently used entries."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Calculate current cache size
                cursor = conn.execute("""
                    SELECT SUM(LENGTH(response_compressed) + LENGTH(query_text))
                    FROM cache_entries
                """)
                current_size = cursor.fetchone()[0] or 0
                
                if current_size > self.max_size_bytes:
                    # Remove least recently used entries
                    cursor = conn.execute("""
                        SELECT query_hash, tokens_used, cost_estimate
                        FROM cache_entries 
                        ORDER BY last_accessed ASC
                    """)
                    
                    entries_to_remove = []
                    size_to_remove = current_size - self.max_size_bytes
                    current_removed_size = 0
                    
                    for row in cursor:
                        query_hash, tokens_used, cost_estimate = row
                        entries_to_remove.append((query_hash, tokens_used, cost_estimate))
                        
                        # Estimate size of this entry (approximate)
                        entry_size = 1000  # Rough estimate
                        current_removed_size += entry_size
                        
                        if current_removed_size >= size_to_remove:
                            break
                    
                    # Remove entries
                    for query_hash, tokens_used, cost_estimate in entries_to_remove:
                        conn.execute("DELETE FROM cache_entries WHERE query_hash = ?", (query_hash,))
                        self.stats['evictions'] += 1
                        self.stats['total_tokens_saved'] -= tokens_used
                        self.stats['total_cost_saved'] -= cost_estimate
                    
                    conn.commit()
                    logger.debug(f"Removed {len(entries_to_remove)} entries to enforce size limit")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
                total_entries = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT SUM(LENGTH(response_compressed) + LENGTH(query_text))
                    FROM cache_entries
                """)
                current_size = cursor.fetchone()[0] or 0
                
                hit_rate = 0
                if self.stats['hits'] + self.stats['misses'] > 0:
                    hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])
                
                return {
                    **self.stats,
                    'total_entries': total_entries,
                    'current_size_bytes': current_size,
                    'current_size_mb': current_size / (1024 * 1024),
                    'hit_rate': hit_rate,
                    'max_size_mb': self.max_size_bytes / (1024 * 1024)
                }

    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache_entries")
                conn.commit()
            
            # Reset statistics
            self.stats = {
                'hits': 0,
                'misses': 0,
                'saves': 0,
                'evictions': 0,
                'total_tokens_saved': 0,
                'total_cost_saved': 0.0,
                'cache_size_bytes': 0
            }
            
            logger.info("Cache cleared")

    def export_cache(self, filepath: str):
        """Export cache to file."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT query_hash, query_text, model, response_compressed,
                           tokens_used, cost_estimate, timestamp, ttl, cache_type,
                           confidence, metadata, access_count, last_accessed
                    FROM cache_entries
                """)
                
                entries = []
                for row in cursor:
                    entry = {
                        'query_hash': row[0],
                        'query_text': row[1],
                        'model': row[2],
                        'response': self._decompress_response(row[3]),
                        'tokens_used': row[4],
                        'cost_estimate': row[5],
                        'timestamp': row[6],
                        'ttl': row[7],
                        'cache_type': row[8],
                        'confidence': row[9],
                        'metadata': json.loads(row[10]) if row[10] else None,
                        'access_count': row[11],
                        'last_accessed': row[12]
                    }
                    entries.append(entry)
                
                with open(filepath, 'w') as f:
                    json.dump(entries, f, indent=2)
                
                logger.info(f"Exported {len(entries)} cache entries to {filepath}")

    def import_cache(self, filepath: str):
        """Import cache from file."""
        with self._lock:
            with open(filepath, 'r') as f:
                entries = json.load(f)
            
            with sqlite3.connect(self.db_path) as conn:
                for entry in entries:
                    compressed_response = self._compress_response(entry['response'])
                    metadata_json = json.dumps(entry['metadata']) if entry['metadata'] else None
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO cache_entries 
                        (query_hash, query_text, model, response_compressed, tokens_used,
                         cost_estimate, timestamp, ttl, cache_type, confidence, metadata,
                         access_count, last_accessed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (entry['query_hash'], entry['query_text'], entry['model'],
                          compressed_response, entry['tokens_used'], entry['cost_estimate'],
                          entry['timestamp'], entry['ttl'], entry['cache_type'],
                          entry['confidence'], metadata_json, entry['access_count'],
                          entry['last_accessed']))
                
                conn.commit()
            
            logger.info(f"Imported {len(entries)} cache entries from {filepath}")

# Global cache instance
_global_cache = None

def get_global_cache() -> TokenCacheManager:
    """Get the global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = TokenCacheManager()
    return _global_cache

def clear_global_cache():
    """Clear the global cache."""
    global _global_cache
    if _global_cache:
        _global_cache.clear()

# --- END OF FILE Three_PointO_ArchE/token_cache_manager.py --- 