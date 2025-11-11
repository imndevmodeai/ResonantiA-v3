# Objective Generation Codex Reference

**Location**: `knowledge_graph/symbol_codex.json`  
**Documentation**: `specifications/objective_generation_engine_crystallized.md`

---

## Decoding: ⟦1067⟧→⦅2T2D⦆→Δ⦅2⦆→⊢HCC→⊨M6→⊧547→⟧

### Symbol Breakdown

| Symbol | Meaning | Stage | Description |
|--------|---------|-------|-------------|
| `⟦1067⟧` | Query Intake | Stage 1 | Query ID 1067 - raw user query |
| `→` | Flow Arrow | - | Process flow separator |
| `⦅2T2D⦆` | Feature Vector | Stage 2 | **2T** = 2 Temporal markers, **2D** = 2 Domain keywords |
| `Δ⦅2⦆` | Temporal Scope | Stage 2 | **2** = 2 temporal dimensions/scopes identified |
| `⊢HCC` | SPR Activation | Stage 3 | **HCC** = HistoricalContextualizatioN (or similar SPR) |
| `⊨M6` | Mandate Selection | Stage 4 | **M6** = Mandate 6: Temporal Resonance |
| `⊧547` | Template Assembly | Stage 5 | **547** = Template ID 547 (or template hash) |
| `⟧` | Final Assembly | Stage 7 | Complete objective/problem description |

---

## Complete Symbol Codex

### Core Symbols

```json
{
  "⟦": {
    "meaning": "Query Intake - raw user query",
    "context": "Objective Generation Stage 1",
    "usage": "⟦query_id⟧ or ⟦query_text⟧"
  },
  "⦅": {
    "meaning": "Feature Extraction - pattern matching",
    "context": "Objective Generation Stage 2",
    "usage": "⦅temporal_markers⦆, ⦅domain_keywords⦆"
  },
  "⦆": {
    "meaning": "Feature Vector - structured data",
    "context": "Objective Generation Stage 2",
    "usage": "⦅features⦆"
  },
  "Δ": {
    "meaning": "Temporal Scope - temporal dimension building",
    "context": "Objective Generation Stage 2",
    "usage": "Δ⦅temporal_scope⦆"
  },
  "⊢": {
    "meaning": "SPR Activation - keyword lookup",
    "context": "Objective Generation Stage 3",
    "usage": "⊢HistoricalContextualizatioN, ⊢TemporalDynamiX"
  },
  "⊨": {
    "meaning": "Mandate Selection / Domain Customization",
    "context": "Objective Generation Stage 4 & 6",
    "usage": "⊨M₆, ⊨M₉, ⊨domain_explanation"
  },
  "⊧": {
    "meaning": "Template Assembly - string substitution",
    "context": "Objective Generation Stage 5",
    "usage": "⊧template_id or ⊧template_fill"
  },
  "⟧": {
    "meaning": "Final Assembly - complete objective",
    "context": "Objective Generation Stage 7",
    "usage": "⟧problem_description⟧"
  },
  "→": {
    "meaning": "Process Flow - stage separator",
    "context": "All stages",
    "usage": "Separates stages in Zepto SPR format"
  }
}
```

### SPR Abbreviations

| Abbreviation | Full SPR Name |
|-------------|---------------|
| **H** | HistoricalContextualizatioN |
| **T** | TemporalDynamiX |
| **F** | FutureStateAnalysiS |
| **C** | CausalLagDetectioN |
| **E** | EmergenceOverTimE |
| **Tr** | TrajectoryComparisoN |
| **HCC** | HistoricalContextualizatioN (or compound) |

### Mandate References

| Symbol | Mandate Number | Mandate Name |
|--------|----------------|--------------|
| **M₆** or **M6** | 6 | Temporal Resonance |
| **M₉** or **M9** | 9 | Complex System Visioning |
| **Ω** | Universal | Cognitive Resonance (always included) |

### Feature Vector Notation

| Notation | Meaning |
|---------|---------|
| **2T** | 2 Temporal markers detected |
| **2D** | 2 Domain keywords detected |
| **⦅2T2D⦆** | Feature vector with 2 temporal + 2 domain features |

---

## Codex File Location

**Primary Codex**: `knowledge_graph/symbol_codex.json`

This file contains the complete symbol dictionary used for:
- Zepto SPR compression
- Objective generation
- Pattern crystallization
- Symbol decompression

---

## Usage Example

### Encoding a Query

```
Original Query: "Analyze historical trends in AI development from 2020-2025"

Zepto SPR: ⟦1067⟧→⦅2T2D⦆→Δ⦅2⦆→⊢HCC→⊨M6→⊧547→⟧
```

### Decoding Process

1. **⟦1067⟧**: Query ID 1067
2. **⦅2T2D⦆**: 2 temporal markers (2020, 2025) + 2 domain keywords (AI, development)
3. **Δ⦅2⦆**: 2 temporal scopes identified (explicit: 2020-2025, implicit: trend analysis)
4. **⊢HCC**: Activate HistoricalContextualizatioN SPR
5. **⊨M6**: Apply Mandate 6 (Temporal Resonance)
6. **⊧547**: Use template ID 547 for assembly
7. **⟧**: Final problem description assembled

---

## Related Files

1. **`specifications/objective_generation_engine_crystallized.md`** - Complete documentation
2. **`knowledge_graph/symbol_codex.json`** - Symbol dictionary (large file)
3. **`Three_PointO_ArchE/zepto_spr_processor.py`** - Implementation
4. **`Three_PointO_ArchE/pattern_crystallization_engine.py`** - Compression engine

---

## Quick Reference

**To decode a Zepto SPR**:
```python
from Three_PointO_ArchE.zepto_spr_processor import ZeptoSPRProcessor

processor = ZeptoSPRProcessor()
codex = processor.get_codex()

# Decode
zepto_spr = "⟦1067⟧→⦅2T2D⦆→Δ⦅2⦆→⊢HCC→⊨M6→⊧547→⟧"
decompressed = processor.decompress_zepto_to_spr(zepto_spr, codex)
```

**To view the codex**:
```python
from Three_PointO_ArchE.zepto_spr_processor import ZeptoSPRProcessor

processor = ZeptoSPRProcessor()
codex = processor.get_codex()
print(codex)  # Full symbol dictionary
```

---

**Last Updated**: 2025-11-09  
**Status**: Active codex system in use

