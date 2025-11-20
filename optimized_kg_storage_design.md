# Optimized Knowledge Graph Storage Architecture

## Problem Statement
Current KG file: **172MB** (was 17MB)
- All 8 Russian Doll layers stored inline for 3,570 SPRs
- Full code/specs embedded in Narrative layers (50-80KB each)
- Entire file loaded into memory on startup
- No lazy loading or content deduplication

## Proposed Solution: Hybrid Storage Architecture

### Architecture Overview
```
knowledge_graph/
├── spr_definitions_index.json          # Lightweight index (~5-10MB)
├── content_store/                       # Content-addressable storage
│   ├── narratives/                     # Full Narrative layers
│   │   ├── {content_hash}.json        # Individual narrative files
│   │   └── index.json                  # Hash → SPR mapping
│   ├── compression_stages/             # Other layers (Concise → Zepto)
│   │   ├── {spr_id}/                  # Per-SPR directory
│   │   │   ├── concise.json
│   │   │   ├── nano.json
│   │   │   └── ...
│   └── code_specs/                     # External code/specs
│       ├── {file_hash}.py              # Code files
│       └── {file_hash}.md              # Spec files
└── kg_metadata.db                      # SQLite for fast queries
```

### Storage Strategy

#### 1. **Lightweight Index File** (`spr_definitions_index.json`)
**Size: ~2-5MB** (vs 172MB) - **Zepto-Optimized**

Contains:
- SPR metadata (spr_id, term, category, relationships)
- **Zepto SPR (INLINE)** - Ultra-compressed (50-200 bytes each)
- **Symbol codex (INLINE)** - Small, required for decompression
- References to content files (hashes/paths)
- Compression ratios and statistics

**Key Innovation**: Zepto stored inline because it's tiny (642:1 compression ratio)

```json
{
  "spr_id": "ActioncontexT",
  "term": "ActioncontexT",
  "category": "CoreConcept",
  "relationships": {...},
  "zepto_spr": "PRIMEv3.5-GP:V3.5,Auth=B.J.L,ID=Æ,M={LV,PTR,CTA},P={AVBS}",
  "symbol_codex": {},
  "zepto_hash": "sha256:abc123...",
  "content_refs": {
    "narrative": "sha256:def456...",
    "compression_stages": "sha256:ghi789..."
  },
  "metadata": {
    "compression_ratio": 642.5,
    "created": "2025-01-XX",
    "last_updated": "2025-01-XX"
  }
}
```

**Why Zepto Inline?**
- Zepto is **57 bytes** for a 36KB document (642:1 ratio)
- 3,570 SPRs × 100 bytes average = **~350KB** total (negligible)
- Enables **instant Zepto lookups** (no file I/O)
- **Content-addressable** by Zepto hash (deduplication key)

#### 2. **Content-Addressable Storage** (`content_store/`)
**Benefits:**
- **Deduplication**: Same content stored once, referenced multiple times
- **Lazy Loading**: Only load content when needed
- **Efficient Updates**: Update one SPR without rewriting entire file
- **Parallel Access**: Multiple processes can read different SPRs simultaneously

**Structure:**
```
content_store/
├── narratives/
│   ├── sha256_abc123def456.json    # Narrative content
│   ├── sha256_789ghi012jkl345.json  # Another narrative
│   └── index.json                   # Maps SPR IDs → content hashes
│
├── compression_stages/
│   ├── ActioncontexT/
│   │   ├── concise.json
│   │   ├── nano.json
│   │   ├── micro.json
│   │   └── ...
│   └── ActionregistrY/
│       └── ...
│
└── code_specs/
    ├── sha256_file1.py              # Code file (shared across SPRs)
    └── sha256_file2.md              # Spec file (shared across SPRs)
```

#### 3. **SQLite Metadata Database** (`kg_metadata.db`)
**Purpose**: Fast queries without loading JSON

**Schema:**
```sql
CREATE TABLE sprs (
    spr_id TEXT PRIMARY KEY,
    term TEXT,
    category TEXT,
    definition_hash TEXT,
    narrative_hash TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE compression_stages (
    spr_id TEXT,
    stage_name TEXT,
    content_path TEXT,
    compression_ratio REAL,
    PRIMARY KEY (spr_id, stage_name)
);

CREATE TABLE content_files (
    content_hash TEXT PRIMARY KEY,
    file_path TEXT,
    content_type TEXT,  -- 'narrative', 'code', 'spec'
    size_bytes INTEGER,
    referenced_by TEXT  -- JSON array of SPR IDs
);

CREATE INDEX idx_spr_term ON sprs(term);
CREATE INDEX idx_spr_category ON sprs(category);
CREATE INDEX idx_content_type ON content_files(content_type);
```

### Implementation Benefits

#### 1. **Massive Size Reduction**
- **Index file**: 5-10MB (vs 172MB)
- **Content store**: ~160MB (same total, but distributed)
- **Database**: ~2-5MB (metadata only)
- **Total on-disk**: ~170MB (same, but structured)
- **Memory usage**: **5-10MB** on startup (vs 172MB)

#### 2. **Lazy Loading**
```python
# Before: Loads entire 172MB file
spr_manager = SPRManager("spr_definitions_tv.json")  # 172MB in memory

# After: Loads only index (~5MB)
spr_manager = SPRManager("spr_definitions_index.json")  # 5MB in memory

# Load content on-demand
narrative = spr_manager.get_narrative("ActioncontexT")  # Loads only this SPR's narrative
```

#### 3. **Content Deduplication**
- If 10 SPRs reference the same code file, store it once
- Share compression stages across similar SPRs
- Reduce storage by 20-30% for common content

#### 4. **Fast Queries**
```python
# Before: Scan entire JSON array (slow)
results = [spr for spr in all_sprs if "code" in spr.get("definition", "")]

# After: SQL query (fast)
results = db.execute("SELECT * FROM sprs WHERE category = 'CodeConcept'")
```

#### 5. **Incremental Updates**
```python
# Before: Rewrite entire 172MB file
update_spr("ActioncontexT", new_content)  # Rewrites 172MB

# After: Update only changed files
update_spr("ActioncontexT", new_content)  # Updates 1 narrative file + index entry
```

### Migration Strategy

#### Phase 1: Create Migration Script
```python
# migrate_kg_to_optimized.py
1. Load current spr_definitions_tv.json
2. Extract metadata → index.json
3. Extract narratives → content_store/narratives/
4. Extract compression stages → content_store/compression_stages/
5. Build SQLite database
6. Verify integrity
```

#### Phase 2: Update SPRManager
```python
# spr_manager.py (updated)
class SPRManager:
    def __init__(self, index_path: str):
        # Load lightweight index
        self.index = self._load_index(index_path)  # ~5MB
        self.db = sqlite3.connect("kg_metadata.db")
        self.content_store = ContentStore("content_store/")
    
    def get_spr(self, spr_id: str, layer: str = "Narrative"):
        # Load from index (fast)
        spr_meta = self.index[spr_id]
        
        # Load content on-demand (lazy)
        if layer == "Narrative":
            content = self.content_store.get_narrative(spr_meta["narrative_hash"])
        else:
            content = self.content_store.get_stage(spr_id, layer)
        
        return {**spr_meta, "content": content}
```

#### Phase 3: Backward Compatibility
- Keep old format for migration period
- Provide conversion utilities
- Support both formats during transition

### Performance Comparison

| Operation | Current (172MB JSON) | Optimized (Hybrid) |
|-----------|---------------------|-------------------|
| **Startup time** | ~2-3 seconds | ~0.1 seconds |
| **Memory usage** | 172MB | 5-10MB |
| **Query by ID** | O(n) scan | O(1) hash lookup |
| **Query by term** | O(n) scan | O(log n) SQL index |
| **Update SPR** | Rewrite 172MB | Update 1 file |
| **Load Narrative** | Already in memory | Lazy load (~5KB) |

### Additional Optimizations

#### 1. **Compression**
- Gzip compress narrative files (50-80KB → 10-20KB)
- Store compressed, decompress on read
- **Additional savings: 60-70%**

#### 2. **Caching**
- LRU cache for frequently accessed SPRs
- Cache size: 50-100 SPRs (~5-10MB)
- **Hit rate: 80-90%** for common queries

#### 3. **Lazy Compression Stage Loading**
- Only load requested layer (not all 8)
- **Memory savings: 87.5%** (1/8 layers loaded)

#### 4. **Zepto as Content-Addressable Key** ⚡ **KEY INNOVATION**
**Zepto Characteristics** (from PRIME protocol example):
- **Compression Ratio**: 642:1 (36KB → 57 bytes)
- **Size**: Typically 50-200 bytes per SPR
- **Purpose**: Ultra-fast priming, quick lookups, content-addressable key

**Zepto-Optimized Storage Strategy**:

```python
# Zepto hash = content identity (deduplication key)
zepto_hash = sha256(zepto_spr + symbol_codex_json)

# Same Zepto = Same Content (automatic deduplication)
if zepto_hash in zepto_index:
    # Content already exists - just add SPR reference
    zepto_index[zepto_hash]["referenced_by"].append(new_spr_id)
else:
    # New content - store once
    zepto_index[zepto_hash] = {
        "narrative_hash": store_narrative(narrative),
        "compression_stages_hash": store_stages(stages),
        "referenced_by": [spr_id]
    }
```

**Zepto Benefits**:
1. **Inline Storage**: Zepto stored in index (only ~350KB for 3,570 SPRs)
2. **Instant Lookup**: O(1) hash lookup vs O(n) scan
3. **Content Deduplication**: Same Zepto = same content (30-50% storage savings)
4. **Universal Reference**: Cross-reference SPRs by Zepto similarity
5. **Deterministic**: Perfect for Universal Abstraction (no LLM needed)

**Zepto Index Structure**:
```json
{
  "zepto_hash_abc123": {
    "narrative_hash": "sha256:def456",
    "compression_stages_hash": "sha256:ghi789",
    "referenced_by": ["ActioncontexT", "ActioncontextcognitivE"],
    "ref_count": 2
  }
}
```

**Performance Impact**:
- **Zepto Lookup**: Instant (O(1) hash lookup)
- **Content Similarity**: O(1) hash comparison vs O(n²) text comparison
- **Deduplication**: Automatic (30-50% storage savings)
- **Memory**: Only 2-5MB startup (vs 172MB)

### Estimated Final Size (Zepto-Optimized)

| Component | Current | Optimized | Savings |
|-----------|---------|-----------|---------|
| Index file (Zepto inline) | 172MB | 2-5MB | **97%** |
| Zepto index | N/A | 1-2MB | - |
| Content store (deduped) | N/A | 80-100MB | - |
| Database | N/A | 2-5MB | - |
| **Total on-disk** | 172MB | **85-112MB** | **35-50%** |
| **Memory (startup)** | 172MB | **2-5MB** | **97%** |

**Zepto-Specific Savings**:
- **Zepto inline**: Only ~350KB for 3,570 SPRs (negligible)
- **Content deduplication**: 30-50% reduction (same Zepto = same content)
- **Zepto hash lookup**: O(1) vs O(n) scan (instant vs seconds)

### Implementation Priority

1. **High Priority**: Migration script + updated SPRManager
2. **Medium Priority**: SQLite database for queries
3. **Low Priority**: Compression, caching, advanced optimizations

### Next Steps

1. Create migration script
2. Update SPRManager to support hybrid storage
3. Test with existing workflows
4. Migrate production KG
5. Monitor performance improvements

