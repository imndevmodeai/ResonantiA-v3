# Zepto-Optimized Storage Architecture

## Zepto's Unique Role

**Zepto Characteristics** (from PRIME protocol example):
- **Compression Ratio**: 642:1 (36KB → 57 bytes)
- **Size**: Typically 50-200 bytes per SPR
- **Purpose**: Ultra-fast priming, quick lookups, content-addressable key
- **Decompression**: Requires `symbol_codex` for full reconstruction

## Optimized Storage Strategy for Zepto

### 1. **Zepto as Primary Index Key** (Content-Addressable Storage)

**Key Insight**: Zepto SPR is the perfect content-addressable hash!

```python
# Zepto hash = content identity
zepto_hash = sha256(zepto_spr + symbol_codex_json)

# Same Zepto = Same Content (deduplication)
if zepto_hash in content_store:
    # Reuse existing content, just add new SPR ID reference
    content_store[zepto_hash].referenced_by.append(new_spr_id)
else:
    # New content, store once
    content_store[zepto_hash] = {
        "zepto_spr": zepto_spr,
        "symbol_codex": symbol_codex,
        "narrative_hash": narrative_hash,  # Link to full content
        "referenced_by": [spr_id]
    }
```

### 2. **Hybrid Storage Architecture**

```
knowledge_graph/
├── spr_index.json                    # Lightweight (~2-5MB)
│   └── Contains:
│       • SPR metadata (spr_id, term, category)
│       • Zepto SPR (inline, 50-200 bytes each)
│       • Symbol codex (inline, small)
│       • Content references (hashes)
│
├── content_store/                    # Content-addressable
│   ├── zepto_index.json              # Zepto hash → content mapping
│   │   └── {
│   │       "zepto_hash_abc123": {
│   │           "narrative_hash": "sha256:def456",
│   │           "compression_stages_hash": "sha256:ghi789",
│   │           "referenced_by": ["SPR-001", "SPR-042"]
│   │       }
│   │   }
│   │
│   ├── narratives/                   # Full Narrative layers
│   │   ├── sha256_def456.json        # Individual narrative files
│   │   └── ...
│   │
│   └── compression_stages/          # Other layers (Concise → Atto)
│       ├── sha256_ghi789/
│       │   ├── concise.json
│       │   ├── nano.json
│       │   └── ...
│       └── ...
│
└── kg_metadata.db                   # SQLite for fast queries
    └── Tables:
        • sprs (spr_id, zepto_hash, metadata)
        • zepto_index (zepto_hash, narrative_hash, ref_count)
        • content_files (content_hash, file_path, size)
```

### 3. **Zepto-First Lookup Strategy**

```python
class ZeptoOptimizedSPRManager:
    """
    Zepto-optimized SPR Manager with content-addressable storage.
    """
    
    def __init__(self, index_path: str):
        # Load lightweight index (Zepto inline)
        self.index = self._load_index(index_path)  # ~2-5MB
        self.zepto_index = self._load_zepto_index()  # Zepto hash → content mapping
        self.content_store = ContentStore("content_store/")
        self.db = sqlite3.connect("kg_metadata.db")
    
    def get_spr_by_zepto(self, zepto_spr: str, symbol_codex: Dict) -> Dict:
        """
        Ultra-fast lookup by Zepto SPR (content-addressable).
        This is the PRIMARY lookup method.
        """
        # Compute Zepto hash
        zepto_hash = self._compute_zepto_hash(zepto_spr, symbol_codex)
        
        # Check if we've seen this Zepto before
        if zepto_hash in self.zepto_index:
            # Get all SPRs that share this Zepto
            spr_ids = self.zepto_index[zepto_hash]["referenced_by"]
            
            # Return first SPR (or merge if multiple)
            spr_id = spr_ids[0]
            return self.get_spr(spr_id)
        else:
            # New Zepto - decompress to get SPR metadata
            return self._decompress_zepto(zepto_spr, symbol_codex)
    
    def get_spr(self, spr_id: str, layer: str = "Zepto"):
        """
        Get SPR by ID, with optional layer selection.
        Zepto is always available (inline in index).
        """
        # Load from index (fast - Zepto is inline)
        spr_meta = self.index[spr_id]
        
        if layer == "Zepto":
            # Zepto is already in index - instant return
            return {
                "spr_id": spr_id,
                "zepto_spr": spr_meta["zepto_spr"],
                "symbol_codex": spr_meta["symbol_codex"],
                "metadata": spr_meta["metadata"]
            }
        else:
            # Load other layers on-demand (lazy)
            zepto_hash = self._compute_zepto_hash(
                spr_meta["zepto_spr"],
                spr_meta["symbol_codex"]
            )
            return self.content_store.get_layer(zepto_hash, layer)
    
    def scan_and_prime(self, text: str) -> List[Dict]:
        """
        Scan text for Zepto SPRs (ultra-fast pattern matching).
        """
        # Extract Zepto patterns from text
        zepto_patterns = self._extract_zepto_patterns(text)
        
        # Lookup by Zepto (content-addressable)
        primed_sprs = []
        for zepto_spr, codex in zepto_patterns:
            spr = self.get_spr_by_zepto(zepto_spr, codex)
            primed_sprs.append(spr)
        
        return primed_sprs
```

### 4. **Zepto Deduplication Benefits**

**Current Problem**: Same content stored multiple times
- SPR-001: "ActioncontexT" → 50KB Narrative
- SPR-042: "ActioncontexT" (duplicate) → 50KB Narrative (duplicate)

**Zepto Solution**: Content-addressable by Zepto hash
- Both SPRs share same Zepto → Store content once
- **Storage Savings**: 50%+ for duplicate/similar SPRs

```python
def add_spr(self, spr: Dict):
    """Add SPR with automatic Zepto deduplication."""
    zepto_hash = self._compute_zepto_hash(
        spr["zepto_spr"],
        spr["symbol_codex"]
    )
    
    if zepto_hash in self.zepto_index:
        # Content already exists - just add SPR reference
        self.zepto_index[zepto_hash]["referenced_by"].append(spr["spr_id"])
        logger.info(f"SPR {spr['spr_id']} shares content with existing Zepto")
    else:
        # New content - store it
        self._store_content(zepto_hash, spr)
        self.zepto_index[zepto_hash] = {
            "narrative_hash": self._store_narrative(spr["narrative"]),
            "compression_stages_hash": self._store_stages(spr["compression_stages"]),
            "referenced_by": [spr["spr_id"]]
        }
```

### 5. **Storage Size Comparison**

| Component | Current (172MB) | Zepto-Optimized | Savings |
|-----------|----------------|-----------------|---------|
| **Index (Zepto inline)** | N/A | 2-5MB | - |
| **Zepto Index** | N/A | 1-2MB | - |
| **Narratives (deduped)** | 49MB | 25-35MB | **30-50%** |
| **Compression Stages** | 155MB | 80-100MB | **35-50%** |
| **Database** | N/A | 2-5MB | - |
| **Total** | 172MB | **110-147MB** | **15-35%** |
| **Memory (startup)** | 172MB | **2-5MB** | **97%** |

### 6. **Zepto as Universal Reference**

**Key Innovation**: Zepto SPR becomes the universal content identifier

```python
# Cross-reference by Zepto
def find_related_sprs(self, zepto_spr: str) -> List[str]:
    """Find all SPRs that share the same Zepto (same content)."""
    zepto_hash = self._compute_zepto_hash(zepto_spr, codex)
    return self.zepto_index[zepto_hash]["referenced_by"]

# Zepto-based relationships
def get_zepto_relationships(self, spr_id: str) -> Dict:
    """Get relationships based on Zepto similarity."""
    spr = self.get_spr(spr_id)
    zepto_hash = self._compute_zepto_hash(spr["zepto_spr"], spr["symbol_codex"])
    
    # Find SPRs with similar Zepto (content similarity)
    similar_zeptos = self._find_similar_zeptos(zepto_hash, threshold=0.8)
    return {
        "identical_content": self.zepto_index[zepto_hash]["referenced_by"],
        "similar_content": [spr_id for _, spr_id in similar_zeptos]
    }
```

### 7. **Migration Strategy**

```python
# migrate_to_zepto_optimized.py

def migrate_kg():
    """
    Migrate from monolithic 172MB JSON to Zepto-optimized storage.
    """
    # 1. Load current KG
    current_kg = load_json("spr_definitions_tv.json")
    
    # 2. Extract Zepto SPRs (already computed)
    zepto_index = {}
    content_store = {}
    
    for spr in current_kg:
        zepto_spr = spr.get("zepto_spr", "")
        symbol_codex = spr.get("symbol_codex", {})
        
        # Compute Zepto hash
        zepto_hash = compute_zepto_hash(zepto_spr, symbol_codex)
        
        # Check for duplicates
        if zepto_hash in zepto_index:
            # Duplicate - just add SPR reference
            zepto_index[zepto_hash]["referenced_by"].append(spr["spr_id"])
        else:
            # New - store content
            zepto_index[zepto_hash] = {
                "narrative_hash": store_narrative(spr["narrative"]),
                "compression_stages_hash": store_stages(spr["compression_stages"]),
                "referenced_by": [spr["spr_id"]]
            }
    
    # 3. Build lightweight index (Zepto inline)
    index = {}
    for spr in current_kg:
        index[spr["spr_id"]] = {
            "term": spr["term"],
            "category": spr["category"],
            "zepto_spr": spr["zepto_spr"],  # INLINE (small)
            "symbol_codex": spr["symbol_codex"],  # INLINE (small)
            "zepto_hash": compute_zepto_hash(spr["zepto_spr"], spr["symbol_codex"]),
            "metadata": {
                "created": spr.get("created_at"),
                "updated": spr.get("updated_at")
            }
        }
    
    # 4. Save optimized structure
    save_json("spr_index.json", index)  # ~2-5MB
    save_json("content_store/zepto_index.json", zepto_index)  # ~1-2MB
    build_sqlite_db(index, zepto_index)  # ~2-5MB
    
    print(f"Migration complete:")
    print(f"  Index: {get_size('spr_index.json') / 1024 / 1024:.1f} MB")
    print(f"  Content store: {get_dir_size('content_store/') / 1024 / 1024:.1f} MB")
    print(f"  Total: {(get_size('spr_index.json') + get_dir_size('content_store/')) / 1024 / 1024:.1f} MB")
    print(f"  Memory savings: {((172 - (get_size('spr_index.json') + get_dir_size('content_store/')) / 1024 / 1024) / 172 * 100):.1f}%")
```

### 8. **Performance Benefits**

| Operation | Current | Zepto-Optimized | Improvement |
|-----------|---------|-----------------|-------------|
| **Startup** | 2-3s (load 172MB) | 0.1s (load 2-5MB) | **20-30x faster** |
| **Zepto Lookup** | O(n) scan | O(1) hash lookup | **Instant** |
| **Layer Retrieval** | Already in memory | Lazy load (~5KB) | **Memory efficient** |
| **Deduplication** | Manual check | Automatic | **Automatic** |
| **Content Similarity** | O(n²) comparison | O(1) hash comparison | **Massive speedup** |

### 9. **Zepto as Universal Abstraction Key**

**Universal Abstraction Integration**: Zepto is the perfect deterministic key

```python
# Zepto = Universal Abstraction representation
def universal_abstraction_lookup(self, query: str) -> Dict:
    """
    Use Zepto as universal abstraction key for deterministic lookups.
    """
    # Convert query to Zepto pattern (deterministic)
    query_zepto = self._query_to_zepto(query)
    
    # Lookup by Zepto (no LLM needed - deterministic)
    matching_sprs = self._find_by_zepto_pattern(query_zepto)
    
    return {
        "matches": matching_sprs,
        "confidence": self._compute_zepto_similarity(query_zepto, matching_sprs)
    }
```

## Summary: Zepto's Role in Optimized Storage

1. **Primary Index Key**: Zepto stored inline (tiny, fast access)
2. **Content-Addressable Hash**: Same Zepto = same content (deduplication)
3. **Universal Reference**: Cross-reference SPRs by Zepto similarity
4. **Fast Lookup**: O(1) hash lookup vs O(n) scan
5. **Memory Efficient**: 2-5MB startup vs 172MB
6. **Deterministic**: Perfect for Universal Abstraction (no LLM needed)

**Result**: Zepto transforms the KG from a monolithic 172MB file into a lightweight, content-addressable, deduplicated knowledge network with 97% memory savings and 20-30x faster startup.

