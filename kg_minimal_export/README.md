# Minimal Knowledge Graph Export

**Exported**: 2025-11-18T18:17:50.918974

## Contents

- `spr_index.json` - Complete SPR index with Zepto SPRs inline (6.56 MB)
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
kg_context = "Knowledge Graph Context:\n"
kg_context += "Total SPRs: " + str(len(kg_data)) + "\n\nKey SPRs:\n"
for spr_id, spr in list(kg_data.items())[:50]:  # First 50 as example
    kg_context += f"- {spr_id}: {spr.get('term', '')} - {spr.get('definition', '')[:100]}...\n"

# Use in prompt
prompt = kg_context + "\n\nUser query: ..."
```

## File Sizes

- `spr_index.json`: 6.56 MB
- `symbol_codex.json`: 0.01 MB if exists
- `protocol_symbol_vocabulary.json`: 0.01 MB if exists
- **Total**: ~6.58 MB

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
