#!/usr/bin/env python3
"""
Migrate Knowledge Graph to Zepto-Optimized Storage Architecture
Converts monolithic 172MB JSON to lightweight, content-addressable structure.
"""

import json
import hashlib
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict
import shutil
from datetime import datetime

project_root = Path(__file__).parent
KG_PATH = project_root / "knowledge_graph" / "spr_definitions_tv.json"
OUTPUT_DIR = project_root / "knowledge_graph" / "optimized"
CONTENT_STORE = OUTPUT_DIR / "content_store"
NARRATIVES_DIR = CONTENT_STORE / "narratives"
COMPRESSION_STAGES_DIR = CONTENT_STORE / "compression_stages"
INDEX_FILE = OUTPUT_DIR / "spr_index.json"
ZEPTO_INDEX_FILE = CONTENT_STORE / "zepto_index.json"
DB_FILE = OUTPUT_DIR / "kg_metadata.db"


def compute_hash(content: str) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def compute_zepto_hash(zepto_spr: str, symbol_codex: Dict) -> str:
    """Compute content-addressable hash for Zepto SPR."""
    combined = json.dumps({"zepto_spr": zepto_spr, "symbol_codex": symbol_codex}, sort_keys=True)
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()


def load_current_kg() -> List[Dict[str, Any]]:
    """Load current knowledge graph."""
    if not KG_PATH.exists():
        print(f"❌ ERROR: KG file not found at {KG_PATH}")
        sys.exit(1)
    
    print(f"📚 Loading KG from {KG_PATH} ({KG_PATH.stat().st_size / 1024 / 1024:.1f}MB)...")
    with open(KG_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        print(f"✅ Loaded {len(data)} SPRs (list format)")
        return data
    elif isinstance(data, dict):
        sprs = [spr for spr in data.values() if isinstance(spr, dict)]
        print(f"✅ Loaded {len(sprs)} SPRs (dict format)")
        return sprs
    else:
        print(f"❌ ERROR: Unknown KG format")
        sys.exit(1)


def extract_zepto_and_codex(spr: Dict[str, Any]) -> tuple:
    """Extract Zepto SPR and symbol codex from SPR."""
    zepto_spr = spr.get('zepto_spr', '')
    symbol_codex = spr.get('symbol_codex', {})
    
    # Try to find Zepto in compression_stages
    if not zepto_spr and 'compression_stages' in spr:
        for stage in spr['compression_stages']:
            if stage.get('stage_name') == 'Zepto':
                zepto_spr = stage.get('content', '')
                break
    
    return zepto_spr, symbol_codex


def extract_narrative(spr: Dict[str, Any]) -> Optional[str]:
    """Extract Narrative layer from SPR."""
    if 'compression_stages' in spr:
        for stage in spr['compression_stages']:
            if stage.get('stage_name') == 'Narrative':
                return stage.get('content', '')
    
    # Fallback to definition
    return spr.get('definition', '')


def create_output_directories():
    """Create output directory structure."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    CONTENT_STORE.mkdir(exist_ok=True)
    NARRATIVES_DIR.mkdir(exist_ok=True)
    COMPRESSION_STAGES_DIR.mkdir(exist_ok=True)
    print(f"✅ Created output directories in {OUTPUT_DIR}")


def migrate_kg():
    """Migrate KG to optimized storage structure."""
    print("=" * 70)
    print("ZEPTO-OPTIMIZED STORAGE MIGRATION")
    print("=" * 70)
    
    # Load current KG
    sprs = load_current_kg()
    
    # Create output directories
    create_output_directories()
    
    # Initialize data structures
    index = {}
    zepto_index = {}
    content_store_narratives = {}
    compression_stages_store = {}
    db_records = []
    
    print(f"\n🔄 Processing {len(sprs)} SPRs...")
    
    for i, spr in enumerate(sprs):
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(sprs)} SPRs...")
        
        spr_id = spr.get('spr_id', f'UNKNOWN_{i}')
        
        # Extract Zepto and codex
        zepto_spr, symbol_codex = extract_zepto_and_codex(spr)
        
        # Extract narrative
        narrative = extract_narrative(spr)
        
        # Build index entry (Zepto inline)
        index_entry = {
            'spr_id': spr_id,
            'term': spr.get('term', ''),
            'category': spr.get('category', ''),
            'definition': spr.get('definition', ''),
            'relationships': spr.get('relationships', {}),
            'metadata': {
                'created': spr.get('created_at', ''),
                'updated': spr.get('updated_at', ''),
                'compression_ratio': spr.get('compression_ratio', 1.0)
            }
        }
        
        # Add Zepto inline if available
        if zepto_spr:
            zepto_hash = compute_zepto_hash(zepto_spr, symbol_codex)
            index_entry['zepto_spr'] = zepto_spr
            index_entry['symbol_codex'] = symbol_codex
            index_entry['zepto_hash'] = zepto_hash
            
            # Add to Zepto index (content-addressable)
            if zepto_hash not in zepto_index:
                # Store narrative if available
                narrative_hash = None
                if narrative:
                    narrative_hash = compute_hash(narrative)
                    content_store_narratives[narrative_hash] = narrative
                
                # Store compression stages if available
                compression_stages_hash = None
                if 'compression_stages' in spr and spr['compression_stages']:
                    stages_json = json.dumps(spr['compression_stages'], sort_keys=True)
                    compression_stages_hash = compute_hash(stages_json)
                    compression_stages_store[compression_stages_hash] = spr['compression_stages']
                
                zepto_index[zepto_hash] = {
                    'narrative_hash': narrative_hash,
                    'compression_stages_hash': compression_stages_hash,
                    'referenced_by': [spr_id]
                }
            else:
                # Duplicate Zepto - just add reference
                zepto_index[zepto_hash]['referenced_by'].append(spr_id)
        else:
            # No Zepto - store narrative directly in index if small
            if narrative and len(narrative.encode('utf-8')) < 1000:  # < 1KB
                index_entry['narrative'] = narrative
            elif narrative:
                # Large narrative - store in content store
                narrative_hash = compute_hash(narrative)
                content_store_narratives[narrative_hash] = narrative
                index_entry['narrative_hash'] = narrative_hash
        
        index[spr_id] = index_entry
        
        # Prepare DB record
        db_records.append({
            'spr_id': spr_id,
            'term': spr.get('term', ''),
            'category': spr.get('category', ''),
            'zepto_hash': index_entry.get('zepto_hash'),
            'narrative_hash': index_entry.get('narrative_hash'),
            'created_at': spr.get('created_at', ''),
            'updated_at': spr.get('updated_at', '')
        })
    
    print(f"✅ Processed all {len(sprs)} SPRs")
    
    # Save index file
    print(f"\n💾 Saving index file ({INDEX_FILE})...")
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    index_size = INDEX_FILE.stat().st_size / 1024 / 1024
    print(f"✅ Index saved: {index_size:.2f} MB ({len(index)} SPRs)")
    
    # Save Zepto index
    print(f"\n💾 Saving Zepto index ({ZEPTO_INDEX_FILE})...")
    with open(ZEPTO_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(zepto_index, f, ensure_ascii=False, indent=2)
    zepto_index_size = ZEPTO_INDEX_FILE.stat().st_size / 1024 / 1024
    print(f"✅ Zepto index saved: {zepto_index_size:.2f} MB ({len(zepto_index)} unique Zepto hashes)")
    
    # Save narratives to content store
    print(f"\n💾 Saving narratives to content store...")
    narratives_saved = 0
    narratives_total_size = 0
    for narrative_hash, narrative_content in content_store_narratives.items():
        narrative_file = NARRATIVES_DIR / f"{narrative_hash}.json"
        with open(narrative_file, 'w', encoding='utf-8') as f:
            json.dump({'content': narrative_content}, f, ensure_ascii=False)
        narratives_saved += 1
        narratives_total_size += narrative_file.stat().st_size
    print(f"✅ Saved {narratives_saved} narratives: {narratives_total_size / 1024 / 1024:.2f} MB")
    
    # Save compression stages to content store
    print(f"\n💾 Saving compression stages to content store...")
    stages_saved = 0
    stages_total_size = 0
    for stages_hash, stages_content in compression_stages_store.items():
        stages_file = COMPRESSION_STAGES_DIR / f"{stages_hash}.json"
        with open(stages_file, 'w', encoding='utf-8') as f:
            json.dump(stages_content, f, ensure_ascii=False, indent=2)
        stages_saved += 1
        stages_total_size += stages_file.stat().st_size
    print(f"✅ Saved {stages_saved} compression stage sets: {stages_total_size / 1024 / 1024:.2f} MB")
    
    # Create SQLite database
    print(f"\n💾 Creating SQLite database ({DB_FILE})...")
    if DB_FILE.exists():
        DB_FILE.unlink()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE sprs (
            spr_id TEXT PRIMARY KEY,
            term TEXT,
            category TEXT,
            zepto_hash TEXT,
            narrative_hash TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE zepto_index (
            zepto_hash TEXT PRIMARY KEY,
            narrative_hash TEXT,
            compression_stages_hash TEXT,
            referenced_by TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE content_files (
            content_hash TEXT PRIMARY KEY,
            file_path TEXT,
            content_type TEXT,
            size_bytes INTEGER
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_spr_term ON sprs(term)")
    cursor.execute("CREATE INDEX idx_spr_category ON sprs(category)")
    cursor.execute("CREATE INDEX idx_zepto_hash ON sprs(zepto_hash)")
    cursor.execute("CREATE INDEX idx_content_type ON content_files(content_type)")
    
    # Insert SPR records
    cursor.executemany("""
        INSERT INTO sprs (spr_id, term, category, zepto_hash, narrative_hash, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        (r['spr_id'], r['term'], r['category'], r['zepto_hash'], r['narrative_hash'], r['created_at'], r['updated_at'])
        for r in db_records
    ])
    
    # Insert Zepto index records
    cursor.executemany("""
        INSERT INTO zepto_index (zepto_hash, narrative_hash, compression_stages_hash, referenced_by)
        VALUES (?, ?, ?, ?)
    """, [
        (h, v.get('narrative_hash'), v.get('compression_stages_hash'), json.dumps(v['referenced_by']))
        for h, v in zepto_index.items()
    ])
    
    # Insert content file records
    for narrative_hash in content_store_narratives.keys():
        file_path = f"content_store/narratives/{narrative_hash}.json"
        file_size = (NARRATIVES_DIR / f"{narrative_hash}.json").stat().st_size
        cursor.execute("""
            INSERT INTO content_files (content_hash, file_path, content_type, size_bytes)
            VALUES (?, ?, ?, ?)
        """, (narrative_hash, file_path, 'narrative', file_size))
    
    for stages_hash in compression_stages_store.keys():
        file_path = f"content_store/compression_stages/{stages_hash}.json"
        file_size = (COMPRESSION_STAGES_DIR / f"{stages_hash}.json").stat().st_size
        cursor.execute("""
            INSERT INTO content_files (content_hash, file_path, content_type, size_bytes)
            VALUES (?, ?, ?, ?)
        """, (stages_hash, file_path, 'compression_stages', file_size))
    
    conn.commit()
    conn.close()
    
    db_size = DB_FILE.stat().st_size / 1024 / 1024
    print(f"✅ Database created: {db_size:.2f} MB")
    
    # Calculate totals
    total_size = (
        INDEX_FILE.stat().st_size +
        ZEPTO_INDEX_FILE.stat().st_size +
        narratives_total_size +
        stages_total_size +
        DB_FILE.stat().st_size
    ) / 1024 / 1024
    
    original_size = KG_PATH.stat().st_size / 1024 / 1024
    memory_savings = (1 - INDEX_FILE.stat().st_size / KG_PATH.stat().st_size) * 100
    
    # Print summary
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"✅ Index file: {index_size:.2f} MB ({len(index)} SPRs)")
    print(f"✅ Zepto index: {zepto_index_size:.2f} MB ({len(zepto_index)} unique Zepto hashes)")
    print(f"✅ Narratives: {narratives_total_size / 1024 / 1024:.2f} MB ({narratives_saved} files)")
    print(f"✅ Compression stages: {stages_total_size / 1024 / 1024:.2f} MB ({stages_saved} files)")
    print(f"✅ Database: {db_size:.2f} MB")
    print(f"✅ Total optimized size: {total_size:.2f} MB")
    print(f"📊 Original size: {original_size:.2f} MB")
    print(f"🎉 Memory savings: {memory_savings:.1f}%")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print("=" * 70)
    
    # Create backup of original
    backup_path = KG_PATH.with_suffix('.json.backup')
    if not backup_path.exists():
        print(f"\n💾 Creating backup of original KG...")
        shutil.copy2(KG_PATH, backup_path)
        print(f"✅ Backup created: {backup_path}")
    
    print("\n✅ Migration complete!")
    print(f"\n📝 Next steps:")
    print(f"  1. Test the optimized storage with: python3 test_zepto_optimized_storage.py")
    print(f"  2. Update SPRManager to use optimized storage")
    print(f"  3. Update workflows to use new structure")
    print(f"  4. Once validated, replace original KG with optimized version")


if __name__ == "__main__":
    try:
        migrate_kg()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

