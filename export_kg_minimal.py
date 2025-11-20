#!/usr/bin/env python3
"""
Minimal KG Export: Just the index file + codex
Perfect for transferring to another LLM - everything needed in ~7MB
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def export_minimal_kg(output_dir: str = "kg_minimal_export"):
    """
    Export minimal KG package: index file + symbol codex.
    This is all another LLM needs to use the Zepto-optimized KG.
    """
    print("📦 Creating minimal KG export (index + codex)...")
    
    kg_root = Path("knowledge_graph")
    optimized_dir = kg_root / "optimized"
    
    if not optimized_dir.exists():
        print("❌ Optimized storage not found!")
        return None
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 1. Copy the index file (6.56 MB with Zepto SPRs inline)
    index_file = optimized_dir / "spr_index.json"
    if not index_file.exists():
        print(f"❌ Index file not found: {index_file}")
        return None
    
    print(f"  Copying index file ({index_file.stat().st_size / (1024*1024):.2f} MB)...")
    shutil.copy(index_file, output_path / "spr_index.json")
    
    # 2. Copy symbol codex files
    codex_files = [
        kg_root / "symbol_codex.json",
        kg_root / "protocol_symbol_vocabulary.json"
    ]
    
    codex_copied = []
    for codex_file in codex_files:
        if codex_file.exists():
            print(f"  Copying codex: {codex_file.name}...")
            shutil.copy(codex_file, output_path / codex_file.name)
            codex_copied.append(codex_file.name)
        else:
            print(f"  ⚠️  Codex file not found: {codex_file} (may not be needed)")
    
    # 3. Create README with usage instructions
    index_size_mb = index_file.stat().st_size / (1024*1024)
    codex_size = (output_path / "symbol_codex.json").stat().st_size / (1024*1024) if (output_path / "symbol_codex.json").exists() else 0
    vocab_size = (output_path / "protocol_symbol_vocabulary.json").stat().st_size / (1024*1024) if (output_path / "protocol_symbol_vocabulary.json").exists() else 0
    total_size_mb = sum(f.stat().st_size for f in output_path.glob('*.json')) / (1024*1024)
    
    readme = """# Minimal Knowledge Graph Export

**Exported**: """ + datetime.now().isoformat() + """

## Contents

- `spr_index.json` - Complete SPR index with Zepto SPRs inline (""" + f"{index_size_mb:.2f}" + """ MB)
- `symbol_codex.json` - Symbol codex for Zepto decompression
- `protocol_symbol_vocabulary.json` - Protocol-specific symbols

## What's Included

✅ **3,589 SPR definitions** with:
- Metadata (spr_id, term, category, relationships)
- **Zepto SPRs inline** (ultra-compressed, 50-200 bytes each)
- Symbol codex references

## What's NOT Included

❌ Content store (narratives, compression stages) - not needed for basic SPR operations
❌ SQLite database - optional, for fast term queries only

## Usage with Another LLM

### Option 1: Use with OptimizedSPRManager (Recommended)

```python
from Three_PointO_ArchE.spr_manager_optimized import OptimizedSPRManager

# Initialize with minimal package
manager = OptimizedSPRManager(
    spr_filepath="spr_index.json",
    optimized_dir=None  # No content store needed
)

# All SPRs available immediately
sprs = manager.get_all_sprs()
print(f"Loaded {len(sprs)} SPRs")

# Scan text for SPRs
primed = manager.scan_and_prime("Using Cognitive resonancE for analysis")
for spr in primed:
    print(f"Found: {{spr['spr_id']}}")
    print(f"Zepto: {{spr.get('zepto_spr', 'N/A')}}")
```

### Option 2: Direct JSON Access

```python
import json

# Load index
with open("spr_index.json", 'r') as f:
    kg_index = json.load(f)

# Access SPRs
for spr_id, spr_data in kg_index.items():
    print(f"{{spr_id}}: {{spr_data.get('term', '')}}")
    print(f"Zepto SPR: {{spr_data.get('zepto_spr', '')}}")
    
    # Decompress Zepto if needed (requires codex)
    if spr_data.get('zepto_spr'):
        from Three_PointO_ArchE.pattern_crystallization_engine import PatternCrystallizationEngine
        
        engine = PatternCrystallizationEngine(
            symbol_codex_path="symbol_codex.json",
            protocol_vocabulary_path="protocol_symbol_vocabulary.json"
        )
        
        # Decompress Zepto SPR to full narrative
        decompressed = engine.decompress_spr(
            spr_data['zepto_spr'],
            spr_data.get('symbol_codex', {{}})
        )
        print(f"Decompressed: {{decompressed[:100]}}...")
```

### Option 3: Prompt Injection

You can also include the index directly in prompts (though it's large):

```python
import json

with open("spr_index.json", 'r') as f:
    kg_data = json.load(f)

# Format for prompt
kg_context = "Knowledge Graph Context:\\n"
kg_context += "Total SPRs: " + str(len(kg_data)) + "\\n\\nKey SPRs:\\n"
for spr_id, spr in list(kg_data.items())[:50]:  # First 50 as example
    kg_context += f"- {spr_id}: {spr.get('term', '')} - {spr.get('definition', '')[:100]}...\\n"

# Use in prompt
prompt = kg_context + "\\n\\nUser query: ..."
```

## File Sizes

- `spr_index.json`: """ + f"{index_size_mb:.2f}" + """ MB
- `symbol_codex.json`: """ + f"{codex_size:.2f}" + """ MB if exists
- `protocol_symbol_vocabulary.json`: """ + f"{vocab_size:.2f}" + """ MB if exists
- **Total**: ~""" + f"{total_size_mb:.2f}" + """ MB

## Advantages

✅ **Minimal size**: Only essential files (~7 MB vs 99.6 MB full package)
✅ **Complete SPR access**: All 3,589 SPRs with Zepto compression
✅ **Self-contained**: Everything needed for SPR operations
✅ **Fast transfer**: Small enough for easy sharing
✅ **No dependencies**: Works with just JSON files

## Limitations

⚠️ **No lazy loading**: All SPRs loaded into memory (but only 6.56 MB)
⚠️ **No term queries**: SQLite database not included (can search in-memory)
⚠️ **No narratives**: Full narrative content not included (Zepto only)

## Notes

- The index file contains Zepto SPRs inline, which are ultra-compressed representations
- To get full narratives, you'd need the content store (adds ~90 MB)
- For most use cases, Zepto SPRs + metadata are sufficient
- Symbol codex is needed to decompress Zepto SPRs back to full text
"""
    
    with open(output_path / "README.md", 'w') as f:
        f.write(readme)
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in output_path.glob('*') if f.is_file()) / (1024 * 1024)
    
    print(f"\n✅ Minimal KG export created: {output_path}")
    print(f"   Total size: {total_size:.2f} MB")
    print(f"   Files:")
    print(f"     - spr_index.json ({index_file.stat().st_size / (1024*1024):.2f} MB)")
    for codex in codex_copied:
        codex_size = (output_path / codex).stat().st_size / (1024*1024)
        print(f"     - {codex} ({codex_size:.2f} MB)")
    print(f"\n   📋 See README.md for usage instructions")
    
    return {
        'output_dir': str(output_path),
        'total_size_mb': total_size,
        'files': ['spr_index.json'] + codex_copied,
        'exported_at': datetime.now().isoformat()
    }

if __name__ == "__main__":
    import sys
    
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "kg_minimal_export"
    result = export_minimal_kg(output_dir)
    
    if result:
        print(f"\n🎉 Ready to share! Package location: {result['output_dir']}")
