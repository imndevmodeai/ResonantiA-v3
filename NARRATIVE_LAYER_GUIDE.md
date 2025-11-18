# Getting Full Narrative into Knowledge Graph

## Overview

The **Narrative layer** is the outermost Russian Doll that contains the **complete, uncompressed original content**. This guide explains how to ensure the full narrative is preserved in your Knowledge Graph.

## How It Works

### 1. **Automatic Narrative Layer Creation**

The `PatternCrystallizationEngine` now **automatically creates** the Narrative layer when compressing:

```python
# When you compress, the engine creates all 8 layers:
result = processor.compress_to_zepto(
    narrative=full_narrative,  # Your complete original content
    target_stage="Zepto"
)

# Result includes:
# - Narrative layer (complete original)
# - Concise layer (summarized)
# - Nano → Micro → Pico → Femto → Atto (progressively compressed)
# - Zepto layer (maximum compression)
```

### 2. **Building Full Narrative**

The enhancement script now builds the **complete narrative** from all SPR fields:

```python
def build_full_narrative(spr):
    # Includes:
    # - Term
    # - Definition
    # - Blueprint details
    # - Example application
    # - Category
    # - Relationships
    # - Any other context fields
```

This ensures **nothing is lost** when creating the Narrative layer.

## How to Ensure Full Narrative in KG

### Option 1: Recompress Existing SPRs (Recommended)

Run the enhancement script with recompression to add full Narrative layers:

```bash
cd /mnt/3626C55326C514B1/Happier
source arche_env/bin/activate
python3 enhance_sprs_russian_doll.py --workers 2
```

This will:
1. Build full narrative from all SPR fields
2. Recompress with complete Russian Doll layers
3. Store Narrative layer in `compression_stages`
4. Save to `knowledge_graph/spr_definitions_tv.json`

### Option 2: Verify Narrative Layer Presence

Check if SPRs have Narrative layers:

```python
import json

with open('knowledge_graph/spr_definitions_tv.json', 'r') as f:
    sprs = json.load(f)

narrative_count = 0
for spr in sprs:
    stages = spr.get('compression_stages', [])
    if stages:
        has_narrative = any(s.get('stage_name') == 'Narrative' for s in stages)
        if has_narrative:
            narrative_count += 1
            # Get full narrative
            narrative_stage = next(s for s in stages if s.get('stage_name') == 'Narrative')
            full_narrative = narrative_stage.get('content', '')
            print(f"SPR {spr.get('spr_id')}: {len(full_narrative)} chars")

print(f"SPRs with Narrative layer: {narrative_count}/{len(sprs)}")
```

### Option 3: Retrieve Full Narrative from KG

Once stored, retrieve the full narrative:

```python
from Three_PointO_ArchE.pattern_crystallization_engine import PatternCrystallizationEngine

engine = PatternCrystallizationEngine()

# Load SPR
spr = load_spr_from_kg("ActioncontexT")

# Get full narrative from compression_stages
stages = spr.get('compression_stages', [])
narrative_stage = next(
    (s for s in stages if s.get('stage_name') == 'Narrative'),
    None
)

if narrative_stage:
    full_narrative = narrative_stage['content']
    print(f"Full original content: {full_narrative}")
else:
    # Fallback: build from SPR fields
    full_narrative = build_full_narrative(spr)
```

## What Gets Stored in Narrative Layer

The Narrative layer contains:

1. **Term**: The SPR term/name
2. **Definition**: Complete definition text
3. **Blueprint Details**: Implementation details
4. **Example Application**: Usage examples
5. **Category**: SPR category
6. **Relationships**: All relationship context
7. **Any other fields**: Additional context from the SPR

## Storage Location

The Narrative layer is stored in:

```json
{
  "spr_id": "ActioncontexT",
  "compression_stages": [
    {
      "stage_name": "Narrative",
      "content": "Term: Action Context\n\nDefinition: A dataclass that provides...",
      "compression_ratio": 1.0,
      "symbol_count": 560,
      "timestamp": "2025-11-17T12:10:35.432720Z"
    },
    {
      "stage_name": "Concise",
      "content": "...",
      ...
    },
    ...
  ]
}
```

## Benefits

1. **Complete Preservation**: Full original content never lost
2. **Lossless Retrieval**: Can always get back to original
3. **Progressive Access**: Can retrieve at any detail level
4. **KG-First Routing**: Full narrative available without LLM calls

## Verification

After recompression, verify:

```bash
python3 -c "
import json
with open('knowledge_graph/spr_definitions_tv.json', 'r') as f:
    sprs = json.load(f)

narrative_count = sum(
    1 for spr in sprs 
    if any(s.get('stage_name') == 'Narrative' 
           for s in spr.get('compression_stages', []))
)

print(f'SPRs with Narrative layer: {narrative_count}/{len(sprs)}')
print(f'Coverage: {100*narrative_count/len(sprs):.1f}%')
"
```

## Summary

- ✅ **Narrative layer automatically created** by compression engine
- ✅ **Full narrative built from all SPR fields** by enhancement script
- ✅ **Stored in `compression_stages[0]`** with `stage_name: "Narrative"`
- ✅ **Retrievable without LLM calls** - pure dictionary lookup
- ✅ **Complete original content preserved** - nothing lost

The full narrative is now in your KG! 🎉

