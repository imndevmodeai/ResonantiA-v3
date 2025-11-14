#!/usr/bin/env python3
"""
Enrich recently added lossy-capture SPRs with blueprint_details and example_application.
Creates a timestamped backup before writing.
"""
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "knowledge_graph" / "spr_definitions_tv.json"

ENRICH = {
    "KnowledgeextractoR": {
        "blueprint_details": "Implements lossy signal extraction from verbose LLM outputs; inputs: llm_response, context; outputs: core_principle (universalized), related SPRs, confidence. See analyses/LLM_TO_KNOWLEDGE_GRAPH_MIGRATION.md (Knowledge Extractor).",
        "example_application": "Extracted a universal caching rule from a verbose answer, reduced to 'Use LRU with TTL for hot keys' with links to related SPRs."
    },
    "ZeptopatterncompressoR": {
        "blueprint_details": "Adapter to Zepto abstraction; compresses narrative of the extracted pattern into Zepto SPR; sets zepto_spr, symbol_codex, compression_stages on success.",
        "example_application": "Compressed 'Causal roles extraction' definition into a 48‑char Zepto SPR with a minimal codex."
    },
    "KnowledgegraphintegratoR": {
        "blueprint_details": "Mints new or reuses existing SPRs; updates knowledge_tapestry.json with typed relationships and attaches provenance/metrics.",
        "example_application": "Added 'InvariantmininG' SPR with links to VettingAgenT and UniversalabstractioN; recorded source and excerpt hash."
    },
    "LlmresponseinterceptoR": {
        "blueprint_details": "Post-LLM hook around llm_tool; triggers extract→compress→integrate with confidence and dedup gates.",
        "example_application": "Captured three compact rules from a long policy answer, persisting only high-confidence patterns."
    },
    "KnowledgegraphrouteR": {
        "blueprint_details": "Routes queries to Knowledge Graph first; on hit, decompresses Zepto SPR; on miss, falls back to LLM and triggers capture; tracks autonomy_rate.",
        "example_application": "Answered cache tuning question directly from KG; bypassed LLM and increased autonomy_rate."
    },
    "InvariantmininG": {
        "blueprint_details": "Committee-of-teachers and prompt-perturbation pipeline to mine statements invariant across contexts/providers; outputs consensus principles.",
        "example_application": "Converged on 'Idempotent REST for retry safety' across three providers and perturbations."
    },
    "ExecutiongroundedknowledgE": {
        "blueprint_details": "Admits knowledge only with passing tests/examples/proofs; reproducible artifacts stored alongside SPR.",
        "example_application": "Rejected untestable heuristic; admitted version with pytest-backed example I/O."
    },
    "RoundtripcompressionaudiT": {
        "blueprint_details": "Checks zepto→decompress→recompress idempotence within tolerance; rejects drift-prone patterns.",
        "example_application": "A rule failed round‑trip drift tolerance and remained in quarantine."
    },
    "NoveltyutilitygatinG": {
        "blueprint_details": "Deduplicates via MinHash/embeddings and admits only high-utility patterns (predicted frequency × impact).",
        "example_application": "Skipped a redundant logging tip due to low novelty and utility score."
    },
    "CounterfactualnormalizatioN": {
        "blueprint_details": "Ablation/counterfactual Q&A to minimize conditions and capture robust, context-light rules.",
        "example_application": "Removed 'Linux-only' clause after counterfactual success; kept OS‑agnostic rule."
    },
    "MacroSprSkillbooK": {
        "blueprint_details": "Transforms stable patterns into executable skills/playbooks with pre/post-conditions, parameters, and tests.",
        "example_application": "Added 'Zero‑downtime import' skill with validated steps and roll‑back test."
    },
    "KnowledgequarantinE": {
        "blueprint_details": "Staging area for low-confidence patterns; requires N validated hits, audits, corroboration before promotion.",
        "example_application": "Quarantined 'Spark config tip' until five validated uses across queries."
    },
    "PromotionPolicY": {
        "blueprint_details": "Promotion thresholds and gate checks (round‑trip audit, corroboration, tests) to move from quarantine to canonical.",
        "example_application": "Promoted 'HTTP timeout escalation' after corroboration and successful tests."
    },
    "MultisourcecorroboratioN": {
        "blueprint_details": "Requires independent sources/datasets supporting a pattern before persistence; records provenance hashes.",
        "example_application": "Accepted pagination rule corroborated by vendor docs and production PR notes."
    },
    "ClustrecentroidcompressioN": {
        "blueprint_details": "Clusters similar LLM outputs and compresses the centroid to Zepto to reduce redundancy while retaining coverage.",
        "example_application": "Compressed 14 similar API retry tips into one centroid representation."
    },
    "TokenbudgetmicroprimeR": {
        "blueprint_details": "Injects tiny Zepto primers at inference to seed context and reduce token usage while preserving capability.",
        "example_application": "Injected a 12‑char micro‑primer to bias planning without a long prompt."
    },
    "InferencetimeinvariantchecK": {
        "blueprint_details": "Runtime invariants guard KG answers; on violation, fails closed and routes to LLM fallback; logs event.",
        "example_application": "Guard detected configuration mismatch; routed to LLM for verification."
    },
    "LearningmetricS": {
        "blueprint_details": "Aggregates autonomy_rate, patterns_stored, llm_calls_saved, avg_compression_ratio, avg_confidence; feeds policy decisions.",
        "example_application": "Reported autonomy_rate climbing to 0.32 with 27 LLM calls saved this week."
    }
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_to_list(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [v for _, v in sorted(data.items())]
    raise ValueError("Unsupported SPR format; expected list or dict")


def main():
    sprs = load_json(TARGET)
    spr_list = normalize_to_list(sprs)
    index = {item.get("spr_id"): item for item in spr_list if isinstance(item, dict) and item.get("spr_id")}

    enriched = 0
    for spr_id, fields in ENRICH.items():
        spr = index.get(spr_id)
        if not spr:
            continue
        if "blueprint_details" not in spr or not spr.get("blueprint_details"):
            spr["blueprint_details"] = fields["blueprint_details"]
        if "example_application" not in spr or not spr.get("example_application"):
            spr["example_application"] = fields["example_application"]
        # Ensure metadata exists
        meta = spr.get("metadata") or {}
        meta.setdefault("enriched", True)
        meta["enriched_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        spr["metadata"] = meta
        enriched += 1

    # Backup
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup = TARGET.with_suffix(f".json.enrich_bak_{ts}")
    save_json(backup, spr_list)
    # Save merged
    save_json(TARGET, spr_list)
    print(f"Enriched {enriched} SPRs. Backup: {backup.name}")


if __name__ == "__main__":
    main()


