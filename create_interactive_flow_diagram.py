#!/usr/bin/env python3
"""
Create interactive data flow diagram for Zepto-optimized storage process
"""

import json
from pathlib import Path

def create_ascii_flow_diagram():
    """Create ASCII art diagram of the data flow."""
    
    diagram = """
╔══════════════════════════════════════════════════════════════════════════════╗
║           ZEPTO-OPTIMIZED STORAGE: DATA FLOW PROCESS                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                          STARTUP PROCESS                                    │
└─────────────────────────────────────────────────────────────────────────────┘

    [User Initializes OptimizedSPRManager]
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  Detect Storage Format                │
    │  • Check for optimized/ directory     │
    │  • Check for spr_index.json           │
    │  • Check for kg_metadata.db           │
    └───────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
    [Optimized]            [Legacy]
        │                       │
        ▼                       ▼
    Load Index          Load Full File
    (6.56 MB)           (171.5 MB)
        │                       │
        └───────────┬───────────┘
                    ▼
    ┌───────────────────────────────────────┐
    │  SPR Index in Memory                   │
    │  • 3,589 SPR metadata entries          │
    │  • Zepto SPRs (inline)                 │
    │  • Content hash references             │
    │  • Memory: 6.56 MB (96.2% reduction)   │
    └───────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          QUERY PROCESS                                       │
└─────────────────────────────────────────────────────────────────────────────┘

    [User Query: "Using Cognitive resonancE for analysis"]
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  scan_and_prime(text)                  │
    │  • Compile regex pattern (3,589 keys)  │
    │  • Pattern matching: O(n) scan          │
    │  • Find: "Cognitive resonancE"         │
    └───────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  Index Lookup (In-Memory)              │
    │  • Hash lookup: O(1)                   │
    │  • Return SPR metadata                 │
    │  • Zepto SPR available immediately     │
    └───────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
    [Metadata Only]        [Layer Requested]
        │                       │
        │                       ▼
        │           ┌───────────────────────────┐
        │           │  get_spr(id, layer)       │
        │           │  • Check cache first      │
        │           │  • Lookup content hash    │
        │           └───────────────────────────┘
        │                       │
        │                       ▼
        │           ┌───────────────────────────┐
        │           │  Lazy Load from Store      │
        │           │  • narratives/{hash}.json  │
        │           │  • compression_stages/     │
        │           │  • Load ~5KB on-demand     │
        │           └───────────────────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
    ┌───────────────────────────────────────┐
    │  Return SPR Definition                 │
    │  • Metadata (from index)               │
    │  • Zepto SPR (inline)                  │
    │  • Content (lazy loaded if requested)  │
    └───────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          ZEPTO LOOKUP PROCESS                               │
└─────────────────────────────────────────────────────────────────────────────┘

    [Zepto SPR + Symbol Codex]
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  Compute Zepto Hash                    │
    │  • SHA256(zepto_spr + symbol_codex)   │
    │  • Content-addressable identifier      │
    └───────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  Lookup in zepto_index.json           │
    │  • Hash lookup: O(1)                  │
    │  • Find all SPRs with this Zepto      │
    │  • Get referenced_by list             │
    └───────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  Return SPR(s)                         │
    │  • Multiple SPRs can share Zepto      │
    │  • Content deduplication achieved     │
    └───────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          TERM QUERY PROCESS                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    [Query: "Action"]
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  query_by_term(term)                  │
    │  • SQLite database query              │
    │  • Indexed search: O(log n)           │
    │  • SQL: SELECT spr_id FROM sprs       │
    │         WHERE term LIKE '%Action%'     │
    └───────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  Database Returns SPR IDs             │
    │  • 291 SPRs found                     │
    │  • Fast indexed search                │
    └───────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  Load SPR Definitions                 │
    │  • From in-memory index                │
    │  • Lazy load content if needed        │
    └───────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  Return List of SPRs                  │
    │  • 291 SPR definitions                 │
    └───────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║                          PERFORMANCE METRICS                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────┬──────────────────┬──────────────────┬─────────────────┐
│ Operation           │ Before (Legacy)   │ After (Optimized)│ Improvement     │
├─────────────────────┼──────────────────┼──────────────────┼─────────────────┤
│ Startup Memory      │ 171.5 MB         │ 6.56 MB          │ 96.2% ↓         │
│ Index Load Time     │ ~2-3 seconds     │ ~0.1 seconds     │ 20-30x faster   │
│ Lookup by ID        │ O(n) scan        │ O(1) hash        │ Instant         │
│ Query by Term       │ O(n) scan        │ O(log n) SQL     │ Fast indexed    │
│ Content Similarity  │ O(n²) text       │ O(1) hash        │ Massive speedup │
│ Update SPR          │ Rewrite 171.5 MB │ Update 1 file   │ Incremental     │
│ Load Narrative      │ Already loaded   │ Lazy load ~5KB   │ On-demand only  │
└─────────────────────┴──────────────────┴──────────────────┴─────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║                          STORAGE STRUCTURE                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

knowledge_graph/optimized/
│
├── spr_index.json (6.56 MB)
│   └── Lightweight index with Zepto inline (3,589 SPRs)
│
├── kg_metadata.db (2.90 MB)
│   └── SQLite database
│       ├── sprs table (3,589 rows)
│       ├── zepto_hashes table (1,511 rows)
│       └── content_files table (3,001 rows)
│
└── content_store/
    ├── zepto_index.json (0.55 MB)
    │   └── Content-addressable Zepto hash mapping
    │       └── 1,511 unique Zepto hashes
    │
    ├── narratives/ (21.36 MB)
    │   └── 1,508 unique narrative files
    │       └── Named by content hash (SHA256)
    │
    └── compression_stages/ (68.24 MB)
        └── 1,493 unique compression stage sets
            └── Named by content hash (SHA256)

╔══════════════════════════════════════════════════════════════════════════════╗
║                          KEY INNOVATIONS                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. CONTENT-ADDRESSABLE STORAGE
   • Files named by SHA256 hash of content
   • Automatic deduplication (same content = same hash)
   • 1,508 unique narratives shared across 3,589 SPRs

2. LAZY LOADING
   • Only load content when requested
   • Startup: 6.56 MB (index only)
   • On-demand: ~5KB per narrative load

3. ZEPTO INLINE STORAGE
   • Zepto SPRs stored in index (50-200 bytes each)
   • Enables instant Zepto lookups (no file I/O)
   • Content-addressable by Zepto hash

4. SQLITE INDEXING
   • Fast term queries: O(log n) vs O(n)
   • Indexed columns for rapid searches
   • 291 SPRs found for "Action" in milliseconds

5. INCREMENTAL UPDATES
   • Update single files instead of rewriting 171.5 MB
   • Only affected content files updated
   • Index updated with new hash references
"""
    
    return diagram

if __name__ == "__main__":
    output_dir = Path("visualizations")
    output_dir.mkdir(exist_ok=True)
    
    # Create ASCII diagram
    ascii_diagram = create_ascii_flow_diagram()
    
    ascii_file = output_dir / "zepto_process_flow.txt"
    with open(ascii_file, 'w', encoding='utf-8') as f:
        f.write(ascii_diagram)
    
    print(f"✅ ASCII diagram created: {ascii_file}")
    print("\n" + "="*80)
    print(ascii_diagram)
    print("="*80)
