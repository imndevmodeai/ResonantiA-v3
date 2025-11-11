# Universal Zepto SPR Processor Abstraction - Documentation

## Overview

The Universal Zepto SPR Processor Abstraction provides a system-wide interface for compressing verbose narratives into hyper-dense Zepto SPR (Sparse Priming Representation) form and decompressing them back. This abstraction enables seamless integration throughout the ResonantiA Protocol system.

## Architecture

### Core Components

1. **`IZeptoSPRProcessor`** (Abstract Interface)
   - Defines the universal contract for all Zepto SPR processors
   - Enables polymorphic usage across the system
   - Implements Universal Abstraction principles: Represent → Compare → Learn → Crystallize

2. **`ZeptoSPRProcessorAdapter`** (Concrete Implementation)
   - Adapts `PatternCrystallizationEngine` to the universal interface
   - Provides seamless integration with existing compression infrastructure
   - Handles Symbol Codex management and compression stage tracking

3. **`ZeptoSPRRegistry`** (Singleton Factory)
   - Provides system-wide access to Zepto SPR processing
   - Manages processor instance lifecycle
   - Supports custom processor registration

### Integration Points

#### Action Registry Integration

Two workflow actions are registered:
- **`compress_to_zepto_spr`**: Compresses narratives to Zepto SPR form
- **`decompress_from_zepto_spr`**: Decompresses Zepto SPR back to narratives

Both actions are IAR-compliant and return structured results with reflection data.

#### SPRManager Integration

New methods added to `SPRManager`:
- **`compress_spr_to_zepto(spr_id, target_stage)`**: Compress an SPR definition to Zepto form
- **`decompress_zepto_to_spr(zepto_spr, codex)`**: Decompress Zepto SPR to narrative
- **`batch_compress_sprs_to_zepto(spr_ids, target_stage)`**: Batch compress multiple SPRs

## Usage Examples

### Direct Function Usage

```python
from Three_PointO_ArchE.zepto_spr_processor import compress_to_zepto, decompress_from_zepto

# Compress a narrative
narrative = "A comprehensive explanation of the ResonantiA Protocol..."
result = compress_to_zepto(narrative, target_stage="Zepto")

print(f"Compression Ratio: {result.compression_ratio:.2f}:1")
print(f"Zepto SPR: {result.zepto_spr}")

# Decompress back
decompressed = decompress_from_zepto(result.zepto_spr, result.new_codex_entries)
print(f"Decompressed: {decompressed.decompressed_text}")
```

### Workflow Action Usage

```json
{
  "action_type": "compress_to_zepto_spr",
  "inputs": {
    "narrative": "{{previous_task.output.text}}",
    "target_stage": "Zepto"
  }
}
```

### SPRManager Integration

```python
from Three_PointO_ArchE.spr_manager import SPRManager

manager = SPRManager("knowledge_graph/spr_definitions_tv.json")

# Compress a specific SPR
result = manager.compress_spr_to_zepto("CognitiveResonance", target_stage="Zepto")
print(f"Zepto SPR: {result['zepto_spr']}")

# Batch compress all SPRs
all_results = manager.batch_compress_sprs_to_zepto()
```

## Compression Stages

The abstraction supports all compression stages defined in Pattern Crystallization Engine:
- **Concise**: Initial summarization
- **Nano**: Further compression
- **Micro**: Symbol introduction
- **Pico**: Increased symbol density
- **Femto**: Advanced symbolization
- **Atto**: Near-maximal compression
- **Zepto**: Final hyper-dense form (target stage)

## Symbol Codex Management

The abstraction automatically manages the Symbol Codex:
- New symbols discovered during compression are added to the codex
- Codex entries include symbol, meaning, frequency, and context
- Decompression uses the codex to expand symbols back to meanings

## Quality Metrics

Compression validation includes:
- **Compression Ratio**: Original length / Zepto length
- **Semantic Preservation**: ≥95% meaning retention (target)
- **Decompression Accuracy**: Round-trip integrity verification
- **Symbol Coverage**: Percentage of narrative represented by symbols

## Error Handling

All methods return structured result objects with error fields:
- `ZeptoSPRResult.error`: Compression error message (if any)
- `ZeptoSPRDecompressionResult.error`: Decompression error message (if any)

Methods gracefully handle:
- Missing dependencies (PatternCrystallizationEngine unavailable)
- Invalid inputs (empty narratives, malformed Zepto SPRs)
- Codex mismatches (missing symbols during decompression)

## Future Enhancements

1. **Custom Processor Implementations**: Support for alternative compression algorithms
2. **Incremental Compression**: Compress only changed portions of narratives
3. **Compression Profiles**: Predefined compression strategies for different use cases
4. **Distributed Codex**: Shared Symbol Codex across multiple ArchE instances
5. **Compression Analytics**: Track compression effectiveness over time

## Protocol Compliance

This abstraction adheres to:
- **ResonantiA Protocol v3.5-GP**: Universal Abstraction principles
- **CRDSP v3.1**: Code-Documentation synchronization
- **IAR Compliance**: All actions generate Integrated Action Reflection data
- **Keyholder Override**: Supports `IMnDEVmode` override capabilities

## Integration Checklist

- [x] Abstract interface defined (`IZeptoSPRProcessor`)
- [x] Concrete adapter implemented (`ZeptoSPRProcessorAdapter`)
- [x] Registry singleton created (`ZeptoSPRRegistry`)
- [x] Action registry integration (`compress_to_zepto_spr`, `decompress_from_zepto_spr`)
- [x] SPRManager integration (compression/decompression methods)
- [x] Workflow example created (`zepto_spr_compression.json`)
- [x] Documentation created (this file)

## Testing

Run the workflow example:
```bash
python -m Three_PointO_ArchE.main workflows/zepto_spr_compression.json -c '{"narrative": "Your test narrative here"}'
```

## References

- `Three_PointO_ArchE/pattern_crystallization_engine.py`: Core compression engine
- `specifications/pattern_crystallization_engine.md`: Detailed specification
- `Three_PointO_ArchE/spr_manager.py`: SPR management integration
- `workflows/zepto_spr_compression.json`: Example workflow
