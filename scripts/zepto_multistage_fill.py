#!/usr/bin/env python3
"""
Multi-stage Zepto compression for SPRs:
Runs progressive stages (Concise→Nano→Micro→Pico→Femto→Atto→Zepto) and records
compression_stages history. Final zepto_spr is taken from Zepto stage.

Usage:
  python scripts/zepto_multistage_fill.py --dry-run
  python scripts/zepto_multistage_fill.py
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "knowledge_graph" / "spr_definitions_tv.json"

STAGES = ["Concise", "Nano", "Micro", "Pico", "Femto", "Atto", "Zepto"]


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
    raise ValueError("Unsupported SPR data format; expected list or dict")


def build_narrative(spr: dict) -> str:
    term = spr.get("term", spr.get("spr_id", ""))
    definition = spr.get("definition", "")
    blueprint = spr.get("blueprint_details", "")
    example = spr.get("example_application", "")
    return f"{term}\nDefinition: {definition}\nBlueprint: {blueprint}\nExample: {example}"


def compress_stage(adapter, spr_id: str, narrative: str, stage: str):
    try:
        result = adapter.compress_to_zepto(
            narrative=narrative,
            target_stage=stage,
            context={"spr_id": spr_id, "stage": stage, "source": "zepto_multistage_fill"}
        )
        if result and not getattr(result, "error", None):
            return {
                "stage": stage,
                "zepto_spr": result.zepto_spr,
                "symbol_codex": result.new_codex_entries or {},
                "compression_ratio": result.compression_ratio,
                "zepto_length": result.zepto_length,
                "original_length": result.original_length,
                "compression_stages": result.compression_stages or []
            }
    except Exception as e:
        print(f"[warn] {spr_id} stage {stage} compression failed: {e}", file=sys.stderr)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview only, do not write changes")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of SPRs for this run (0 = all)")
    args = parser.parse_args()

    # Import Zepto adapter
    sys.path.insert(0, str(ROOT))
    try:
        from Three_PointO_ArchE.zepto_spr_processor import ZeptoSPRProcessorAdapter
        adapter = ZeptoSPRProcessorAdapter()
    except Exception as e:
        print(f"[error] ZeptoSPRProcessorAdapter unavailable: {e}", file=sys.stderr)
        sys.exit(1)

    data = load_json(TARGET)
    spr_list = normalize_to_list(data)
    index = {spr.get("spr_id"): spr for spr in spr_list if isinstance(spr, dict)}

    # Candidates: any SPR missing zepto_spr or with empty compression_stages
    candidates = []
    for spr_id, spr in index.items():
        if not spr:
            continue
        if not spr.get("zepto_spr") or not spr.get("compression_stages"):
            candidates.append(spr_id)

    if args.limit and len(candidates) > args.limit:
        candidates = candidates[:args.limit]

    updated = []
    for spr_id in candidates:
        spr = index.get(spr_id)
        if not spr:
            continue
        narrative = build_narrative(spr)

        stage_history = []
        final_zepto = None
        final_codex = {}
        final_ratio = None

        for stage in STAGES:
            result = compress_stage(adapter, spr_id, narrative, stage)
            if not result:
                continue
            # If adapter provides nested compression_stages, merge them; else synthesize a simple entry
            nested = result.get("compression_stages") or []
            if nested:
                for item in nested:
                    item = dict(item)
                    item.setdefault("via_stage", stage)
                    stage_history.append(item)
            else:
                stage_history.append({
                    "stage": stage,
                    "compression_ratio": result.get("compression_ratio"),
                    "symbol_count": len(result.get("zepto_spr") or ""),
                    "via_stage": stage
                })
            # Keep last codex to maximize coverage
            final_codex.update(result.get("symbol_codex") or {})
            if stage == "Zepto":
                final_zepto = result.get("zepto_spr")
                final_ratio = result.get("compression_ratio")

        if final_zepto:
            spr["zepto_spr"] = final_zepto
            spr["compression_ratio"] = final_ratio
        if stage_history:
            spr["compression_stages"] = stage_history
        if final_codex:
            spr["symbol_codex"] = final_codex

        updated.append(spr_id)

    print(f"SPR candidates for multi-stage: {len(candidates)}")
    print(f"Updated multi-stage for       : {len(updated)}")
    if updated:
        preview = ', '.join(sorted(updated)[:40])
        print(f"Updated IDs                   : {preview}{' ...' if len(updated) > 40 else ''}")

    if args.dry_run:
        print("\nDry-run: no changes written.")
        return

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup = TARGET.with_suffix(f".json.zepto_multistage_bak_{ts}")
    save_json(backup, spr_list)
    save_json(TARGET, spr_list)
    print(f"\nSaved. Backup: {backup.name}")


if __name__ == "__main__":
    main()


