"""
Enhanced SPRManager with Zepto-Optimized Storage Support
Supports both legacy (monolithic JSON) and optimized (content-addressable) storage.
"""

import json
import sqlite3
import logging
import re
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from .thought_trail import log_to_thought_trail

logger = logging.getLogger(__name__)


def compute_zepto_hash(zepto_spr: str, symbol_codex: Dict) -> str:
    """Compute content-addressable hash for Zepto SPR."""
    combined = json.dumps({"zepto_spr": zepto_spr, "symbol_codex": symbol_codex}, sort_keys=True)
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()


class OptimizedSPRManager:
    """
    SPRManager with Zepto-optimized storage support.
    Automatically detects and uses optimized storage if available.
    Falls back to legacy format for backward compatibility.
    """
    
    def __init__(self, spr_filepath: str, optimized_dir: Optional[str] = None):
        """
        Initialize SPRManager with optimized storage support.
        
        Args:
            spr_filepath: Path to SPR file (legacy) or index file (optimized)
            optimized_dir: Optional path to optimized storage directory
        """
        self.filepath = Path(spr_filepath).resolve()
        self.sprs: Dict[str, Dict[str, Any]] = {}
        self.spr_pattern: Optional[re.Pattern] = None
        
        # Optimized storage components
        self.optimized_dir: Optional[Path] = None
        self.index_file: Optional[Path] = None
        self.zepto_index: Dict[str, Any] = {}
        self.content_store: Optional[Path] = None
        self.db_conn: Optional[sqlite3.Connection] = None
        self.use_optimized = False
        
        # Cache for lazy-loaded content
        self._content_cache: Dict[str, Any] = {}
        
        # Detect and initialize storage format
        self._detect_storage_format(optimized_dir)
        self._load_sprs()
    
    def _detect_storage_format(self, optimized_dir: Optional[str] = None):
        """Detect if optimized storage is available."""
        # Check if optimized_dir is provided
        if optimized_dir:
            self.optimized_dir = Path(optimized_dir).resolve()
        else:
            # Try to find optimized directory near the file
            possible_dirs = [
                self.filepath.parent / "optimized",
                self.filepath.parent.parent / "knowledge_graph" / "optimized",
            ]
            for opt_dir in possible_dirs:
                if opt_dir.exists() and (opt_dir / "spr_index.json").exists():
                    self.optimized_dir = opt_dir
                    break
        
        # Check if optimized storage is available
        if self.optimized_dir and (self.optimized_dir / "spr_index.json").exists():
            self.index_file = self.optimized_dir / "spr_index.json"
            self.content_store = self.optimized_dir / "content_store"
            zepto_index_file = self.content_store / "zepto_index.json"
            db_file = self.optimized_dir / "kg_metadata.db"
            
            if zepto_index_file.exists() and db_file.exists():
                self.use_optimized = True
                logger.info(f"✅ Using optimized storage from {self.optimized_dir}")
                
                # Load Zepto index
                try:
                    with open(zepto_index_file, 'r', encoding='utf-8') as f:
                        self.zepto_index = json.load(f)
                    logger.info(f"Loaded Zepto index: {len(self.zepto_index)} unique hashes")
                except Exception as e:
                    logger.warning(f"Failed to load Zepto index: {e}")
                
                # Connect to database
                try:
                    self.db_conn = sqlite3.connect(db_file, check_same_thread=False)
                    self.db_conn.row_factory = sqlite3.Row
                    logger.info("Connected to SQLite database")
                except Exception as e:
                    logger.warning(f"Failed to connect to database: {e}")
            else:
                logger.info("Optimized storage directory found but incomplete, using legacy format")
        else:
            logger.info(f"Using legacy storage format from {self.filepath}")
    
    @log_to_thought_trail
    def _load_sprs(self):
        """Load SPRs from either optimized or legacy storage."""
        if self.use_optimized and self.index_file:
            self._load_optimized_sprs()
        else:
            self._load_legacy_sprs()
        
        self._compile_spr_pattern()
    
    def _load_optimized_sprs(self):
        """Load SPRs from optimized index file."""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # Convert index to SPR format (for compatibility)
            for spr_id, index_entry in index_data.items():
                self.sprs[spr_id] = {
                    'spr_id': spr_id,
                    'term': index_entry.get('term', ''),
                    'category': index_entry.get('category', ''),
                    'definition': index_entry.get('definition', ''),
                    'relationships': index_entry.get('relationships', {}),
                    'zepto_spr': index_entry.get('zepto_spr', ''),
                    'symbol_codex': index_entry.get('symbol_codex', {}),
                    'zepto_hash': index_entry.get('zepto_hash'),
                    'narrative_hash': index_entry.get('narrative_hash'),
                    'metadata': index_entry.get('metadata', {}),
                    '_optimized': True  # Flag for optimized storage
                }
            
            logger.info(f"✅ Loaded {len(self.sprs)} SPRs from optimized index ({self.index_file.stat().st_size / 1024 / 1024:.2f} MB)")
        except Exception as e:
            logger.error(f"Failed to load optimized SPRs: {e}")
            logger.info("Falling back to legacy format")
            self.use_optimized = False
            self._load_legacy_sprs()
    
    def _load_legacy_sprs(self):
        """Load SPRs from legacy monolithic JSON file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                spr_data = json.load(f)
            
            if isinstance(spr_data, dict):
                self.sprs = spr_data
            elif isinstance(spr_data, list):
                self.sprs = {spr['spr_id']: spr for spr in spr_data if isinstance(spr, dict) and 'spr_id' in spr}
            else:
                logger.error(f"SPR data format is unrecognized in {self.filepath}")
                self.sprs = {}
            
            logger.info(f"✅ Loaded {len(self.sprs)} SPRs from legacy format ({self.filepath.stat().st_size / 1024 / 1024:.2f} MB)")
        except Exception as e:
            logger.error(f"Failed to load legacy SPRs: {e}")
            self.sprs = {}
    
    def _compile_spr_pattern(self):
        """Compile regex pattern for SPR detection."""
        if not self.sprs:
            self.spr_pattern = None
            return
        
        spr_keys = [re.escape(key) for key in self.sprs.keys()]
        pattern_str = r'\b(' + '|'.join(spr_keys) + r')\b'
        self.spr_pattern = re.compile(pattern_str)
        logger.info(f"Compiled SPR pattern for {len(spr_keys)} keys.")
    
    def _load_content(self, content_hash: str, content_type: str = 'narrative') -> Optional[str]:
        """Lazy load content from content store."""
        if content_hash in self._content_cache:
            return self._content_cache[content_hash]
        
        if not self.content_store:
            return None
        
        try:
            if content_type == 'narrative':
                content_file = self.content_store / "narratives" / f"{content_hash}.json"
            elif content_type == 'compression_stages':
                content_file = self.content_store / "compression_stages" / f"{content_hash}.json"
            else:
                return None
            
            if content_file.exists():
                with open(content_file, 'r', encoding='utf-8') as f:
                    content_data = json.load(f)
                
                if content_type == 'narrative':
                    content = content_data.get('content', '')
                else:
                    content = content_data
                
                # Cache for future use
                self._content_cache[content_hash] = content
                return content
        except Exception as e:
            logger.warning(f"Failed to load content {content_hash}: {e}")
        
        return None
    
    def get_spr(self, spr_id: str, layer: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get SPR by ID, with optional layer selection.
        
        Args:
            spr_id: SPR identifier
            layer: Optional layer name (Narrative, Concise, Nano, etc.)
        
        Returns:
            SPR definition with optional layer-specific content
        """
        if spr_id not in self.sprs:
            return None
        
        spr = self.sprs[spr_id].copy()
        
        # If optimized storage and layer requested, load content
        if self.use_optimized and layer:
            if layer == 'Narrative':
                narrative_hash = spr.get('narrative_hash')
                # If no narrative_hash but has zepto_hash, look it up from Zepto index
                if not narrative_hash and spr.get('zepto_hash'):
                    zepto_hash = spr.get('zepto_hash')
                    if zepto_hash in self.zepto_index:
                        narrative_hash = self.zepto_index[zepto_hash].get('narrative_hash')
                
                if narrative_hash:
                    narrative = self._load_content(narrative_hash, 'narrative')
                    if narrative:
                        spr['narrative'] = narrative
            elif layer in ['Concise', 'Nano', 'Micro', 'Pico', 'Femto', 'Atto', 'Zepto']:
                # Load compression stages
                zepto_hash = spr.get('zepto_hash')
                if zepto_hash and zepto_hash in self.zepto_index:
                    stages_hash = self.zepto_index[zepto_hash].get('compression_stages_hash')
                    if stages_hash:
                        stages = self._load_content(stages_hash, 'compression_stages')
                        if stages:
                            # Find requested layer
                            for stage in stages:
                                if stage.get('stage_name') == layer:
                                    spr['layer_content'] = stage.get('content', '')
                                    break
        
        return spr
    
    def get_spr_by_zepto(self, zepto_spr: str, symbol_codex: Dict) -> Optional[Dict[str, Any]]:
        """
        Get SPR by Zepto hash (content-addressable lookup).
        
        Args:
            zepto_spr: Zepto SPR string
            symbol_codex: Symbol codex dictionary
        
        Returns:
            SPR definition or None
        """
        if not self.use_optimized:
            # Fallback: search all SPRs
            for spr_id, spr in self.sprs.items():
                if spr.get('zepto_spr') == zepto_spr:
                    return spr
            return None
        
        # Compute Zepto hash
        zepto_hash = compute_zepto_hash(zepto_spr, symbol_codex)
        
        # Lookup in Zepto index
        if zepto_hash in self.zepto_index:
            referenced_by = self.zepto_index[zepto_hash].get('referenced_by', [])
            if referenced_by:
                # Return first SPR that references this Zepto
                return self.get_spr(referenced_by[0])
        
        return None
    
    @log_to_thought_trail
    def scan_and_prime(self, text: str, target_layer: Optional[str] = None, auto_select_layer: bool = True) -> List[Dict[str, Any]]:
        """Scan text for SPRs and return definitions."""
        if not self.spr_pattern or not isinstance(text, str):
            return []
        
        found_sprs: Set[str] = set(self.spr_pattern.findall(text))
        
        if found_sprs:
            logger.debug(f"Primed {len(found_sprs)} unique SPRs: {', '.join(sorted(list(found_sprs)))}")
        
        # Auto-select layer if enabled
        if target_layer is None and auto_select_layer:
            try:
                from .russian_doll_retrieval import select_layer_from_query
                target_layer = select_layer_from_query(text)
                logger.debug(f"Auto-selected layer '{target_layer}' for query: {text[:50]}...")
            except Exception as e:
                logger.debug(f"Auto layer selection failed: {e}")
                target_layer = None
        
        # Return SPRs with optional layer content
        return [
            self.get_spr(key, target_layer)
            for key in sorted(list(found_sprs))
            if key in self.sprs
        ]
    
    def query_by_term(self, term: str) -> List[Dict[str, Any]]:
        """Query SPRs by term using SQLite database."""
        if not self.use_optimized or not self.db_conn:
            # Fallback to in-memory search
            return [spr for spr_id, spr in self.sprs.items() if term.lower() in spr.get('term', '').lower()]
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT spr_id FROM sprs WHERE term LIKE ?", (f'%{term}%',))
            results = cursor.fetchall()
            return [self.get_spr(row['spr_id']) for row in results if row['spr_id'] in self.sprs]
        except Exception as e:
            logger.warning(f"Database query failed: {e}, falling back to in-memory search")
            return [spr for spr_id, spr in self.sprs.items() if term.lower() in spr.get('term', '').lower()]
    
    def get_all_sprs(self) -> Dict[str, Dict[str, Any]]:
        """Get all SPRs."""
        return self.sprs
    
    def __del__(self):
        """Cleanup database connection."""
        if self.db_conn:
            self.db_conn.close()

