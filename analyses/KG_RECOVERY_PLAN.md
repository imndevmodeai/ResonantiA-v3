# Mastermind_AI → ArchE KG Recovery Plan

Purpose: Reconstruct the partial Mastermind_AI knowledge graph captured in `past chats/agi.txt` and merge it into ArchE’s current Knowledge Graph (SPR set + Tapestry) with maximal fidelity and determinism.

Artifacts in workspace
- Source (legacy): `past chats/agi.txt` (very large; contains enumerated Nodes and SPR markers)
- Current SPRs (primary): `knowledge_graph/spr_definitions_tv.json` (rich, dict/list hybrid)
- Current Tapestry (graph): `Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json` (nodes + relationships)

Recovery goals
- Parse all Mastermind_AI nodes and map to ArchE SPRs (reuse where possible; mint new where missing)
- Recreate edges/relationships with typed relations
- Generate Zepto SPR stubs for new concepts to support future compression
- Preserve provenance (legacy IDs, text excerpts, source anchors)

High-level pipeline
1) Chunked ingestion of `agi.txt`
   - Read in sliding windows (e.g., 3–5K lines)
   - Extract structures with regex:
     - Node lines: /^\s*Node\s+(\d+):\s+(.+?)$/
     - SPR tag lines (optional): /^\s*SPR:\s*([^,\n]+)\s*,\s*"(.+?)"/ or /^\s*SPR:\s*"(.+?)"/
     - Section markers like "Edges:"; capture subsequent bullet/label pairs when present
   - Capture: {legacy_node_id, label, optional_spr_tag, section_text_block}

2) Canonicalization → SPR mapping
   - Normalize candidate SPR IDs to Guardian pointS (first/last caps) from label or provided tag
   - Fuzzy match to existing `spr_definitions_tv.json` by:
     - Exact spr_id / alias
     - Case-insensitive term match
     - Similarity (>=0.86) on term/definition where available
   - Decision:
     - If match → reuse existing SPR (link legacy_node_id as provenance)
     - If no match → mint new SPR skeleton

3) New SPR skeletons (lossy → Zepto-ready)
   - Fields:
     - spr_id, term, definition (from Node description text), category (default: GeneralConcept if unknown)
     - relationships: empty (to be filled in step 4)
     - zepto_spr: null (optionally produced later via Zepto compression)
     - metadata.provenance: { source: "agi.txt", legacy_node_id, excerpt_sha1 }

4) Relationship extraction → Tapestry edges
   - From each Node’s "Edges:" block, create typed relationships when inferrable (fallback: "related_to")
   - Edge typing heuristics (examples):
     - "part of" → is_a_part_of / has_part
     - "implements" → implements / implemented_by
     - "uses" → uses / used_by
     - "enables" → enables / enabled_by
   - Build/append nodes to `knowledge_tapestry.json` with unique IDs; add edges with confidence

5) Merge & validate
   - Write pending SPR additions to a staging file: `knowledge_graph/staging_sprs_mastermind_ai.json`
   - Write pending Tapestry deltas to: `Three_PointO_ArchE/knowledge_graph/staging_tapestry_mastermind_ai.json`
   - Validation checks:
     - Duplicate spr_id or term collisions
     - Broken references in edges
     - Category sanity

6) Zepto compression pass (optional, batch)
   - For new SPRs, compress definition to Zepto; store `zepto_spr`, `symbol_codex`, `compression_stages`

7) Promotion & commit
   - On pass: merge staging SPRs into `spr_definitions_tv.json`
   - Append nodes/edges to `knowledge_tapestry.json`; update metadata counts
   - Commit with clear provenance message

Deterministic mapping rules (summary)
- Guardian pointS ID builder: CamelCase significant tokens, ensure first/last caps: e.g., "Natural Language Processing" → `NaturallanguageprocessinG`
- Prefer reuse of existing SPR if:
  - Exact match on spr_id OR
  - term case-insensitive match OR
  - similarity ≥ 0.86 on (term|definition) composite

Provenance & audit
- Each added SPR carries: source: "agi.txt", legacy_node_id, excerpt_sha1
- Each edge carries: source: "agi.txt", extraction_confidence

Rollout plan
- Phase 0: Dry-run on first 200 nodes (no writes) → summary report
- Phase 1: Import batch (200–500 nodes) under feature flag → review
- Phase 2: Full import; regenerate counts; produce diff report

Deliverables
- scripts/kg_recover_mastermind_ai.py (parser + mapper + stager)
- knowledge_graph/staging_sprs_mastermind_ai.json (new SPRs)
- Three_PointO_ArchE/knowledge_graph/staging_tapestry_mastermind_ai.json (new nodes/edges)
- analyses/KG_RECOVERY_REPORT.md (summary, counts, collisions, unmapped)

Success criteria
- ≥ 95% of legacy nodes mapped (reused or minted)
- Zero invalid references in Tapestry edges
- No spr_id collisions; aliases preserved
- Provenance attached to all imported items


