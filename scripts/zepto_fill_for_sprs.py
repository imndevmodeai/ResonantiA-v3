#!/usr/bin/env python3
"""
Populate zepto_spr for newly added lossy-capture SPRs by compressing their
definition/blueprint/example using ZeptoSPRProcessorAdapter.

Usage:
  python scripts/zepto_fill_for_sprs.py --dry-run
  python scripts/zepto_fill_for_sprs.py
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "knowledge_graph" / "spr_definitions_tv.json"

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
        # convert dict map to list; preserve key order roughly
        return [v for _, v in sorted(data.items())]
    raise ValueError("Unsupported SPR data format; expected list or dict")


def build_narrative(spr: dict) -> str:
    term = spr.get("term", spr.get("spr_id", ""))
    definition = spr.get("definition", "")
    blueprint = spr.get("blueprint_details", "")
    example = spr.get("example_application", "")
    return f"{term}\nDefinition: {definition}\nBlueprint: {blueprint}\nExample: {example}"


def try_compress(adapter, spr_id: str, narrative: str):
    try:
        result = adapter.compress_to_zepto(
            narrative=narrative,
            target_stage="Zepto",
            context={"spr_id": spr_id, "source": "zepto_fill_for_sprs"}
        )
        if result and not getattr(result, "error", None):
            return {
                "zepto_spr": result.zepto_spr,
                "symbol_codex": result.new_codex_entries or {},
                "compression_stages": result.compression_stages or [],
                "compression_ratio": result.compression_ratio,
            }
    except Exception as e:
        print(f"[warn] compression failed for {spr_id}: {e}", file=sys.stderr)
    # Fallback placeholder
    return {
        "zepto_spr": f"SPR:{spr_id}.",
        "symbol_codex": {},
        "compression_stages": [],
        "compression_ratio": 1.0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview changes only")
    args = parser.parse_args()

    # Import Zepto adapter
    sys.path.insert(0, str(ROOT))
    try:
        from Three_PointO_ArchE.zepto_spr_processor import ZeptoSPRProcessorAdapter
        adapter = ZeptoSPRProcessorAdapter()
    except Exception as e:
        print(f"[warn] ZeptoSPRProcessorAdapter unavailable ({e}); will create placeholders.", file=sys.stderr)
        adapter = None

    data = load_json(TARGET)
    spr_list = normalize_to_list(data)
    index = {spr.get("spr_id"): spr for spr in spr_list if isinstance(spr, dict)}

    # Build candidate set: ALL SPRs lacking zepto_spr (including axioms/core principles)
    candidate_ids = []
    for spr_id, spr in index.items():
        if not spr:
            continue
        if spr.get("zepto_spr"):
            continue
        candidate_ids.append(spr_id)

    to_update = []
    for spr_id in candidate_ids:
        spr = index.get(spr_id)
        if not spr:
            continue
        narrative = build_narrative(spr)
        if adapter:
            comp = try_compress(adapter, spr_id, narrative)
        else:
            comp = {
                "zepto_spr": f"SPR:{spr_id}.",
                "symbol_codex": {},
                "compression_stages": [],
                "compression_ratio": 1.0,
            }
        spr["zepto_spr"] = comp["zepto_spr"]
        if comp.get("symbol_codex") is not None:
            spr["symbol_codex"] = comp["symbol_codex"]
        if comp.get("compression_stages") is not None:
            spr["compression_stages"] = comp["compression_stages"]
        if comp.get("compression_ratio") is not None:
            spr["compression_ratio"] = comp["compression_ratio"]
        to_update.append(spr_id)

    print(f"SPR candidates without zepto_spr: {len(candidate_ids)}")
    print(f"Updated zepto_spr for           : {len(to_update)}")
    if to_update:
        ids_preview = ', '.join(sorted(to_update)[:50])
        suffix = ' ...' if len(to_update) > 50 else ''
        print(f"Updated IDs                     : {ids_preview}{suffix}")

    if args.dry_run:
        print("\nDry-run: no changes written.")
        return

    # Backup and write
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup = TARGET.with_suffix(f".json.zepto_fill_bak_{ts}")
    save_json(backup, spr_list)
    save_json(TARGET, spr_list)
    print(f"\nSaved. Backup: {backup.name}")


if __name__ == "__main__":
    main()


