#!/usr/bin/env python3
"""
Merge staged lossy-capture SPR skeletons into the primary SPR set.

Usage:
  python scripts/kg_import_lossy_sprs.py --dry-run
  python scripts/kg_import_lossy_sprs.py

Behavior:
  - Reads knowledge_graph/staging_sprs_lossy_capture.json
  - Reads knowledge_graph/spr_definitions_tv.json (list or dict)
  - Dedupes by spr_id (skips existing)
  - On non-dry run: writes backup then saves merged list (sorted by spr_id)
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "knowledge_graph" / "staging_sprs_lossy_capture.json"
TARGET = ROOT / "knowledge_graph" / "spr_definitions_tv.json"


def load_json_any(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_to_dict(spr_payload):
    """
    Accepts either a list[dict{spr_id,...}] or dict[spr_id]->spr_def.
    Returns dict[spr_id] -> spr_def
    """
    if isinstance(spr_payload, dict):
        return spr_payload
    if isinstance(spr_payload, list):
        out = {}
        for item in spr_payload:
            if not isinstance(item, dict):
                continue
            spr_id = item.get("spr_id")
            if not spr_id:
                continue
            out[spr_id] = item
        return out
    raise ValueError("Unsupported SPR data format; expected list or dict")


def to_sorted_list(spr_map: dict) -> list:
    return [spr_map[k] for k in sorted(spr_map.keys(), key=lambda x: str(x).lower())]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes; show report only")
    args = parser.parse_args()

    try:
        staged = load_json_any(STAGING)
    except Exception as e:
        print(f"ERROR: failed to load staging SPRs: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        target = load_json_any(TARGET)
    except Exception as e:
        print(f"ERROR: failed to load target SPRs: {e}", file=sys.stderr)
        sys.exit(1)

    staged_list = staged if isinstance(staged, list) else []
    staged_map = normalize_to_dict(staged_list)
    target_map = normalize_to_dict(target)

    to_add = {}
    skipped = []
    for spr_id, spr_def in staged_map.items():
        if spr_id in target_map:
            skipped.append(spr_id)
        else:
            to_add[spr_id] = spr_def

    print("=== Lossy-Capture SPR Import Report ===")
    print(f"Staged SPRs          : {len(staged_map)}")
    print(f"Existing (skipped)   : {len(skipped)}")
    print(f"To add               : {len(to_add)}")
    if skipped:
        print(f"Skipped IDs          : {', '.join(sorted(skipped)[:20])}{' ...' if len(skipped) > 20 else ''}")

    if args.dry_run:
        print("\nDry-run: no changes written.")
        sys.exit(0)

    # Merge
    merged = dict(target_map)
    merged.update(to_add)

    # Backup
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = TARGET.with_suffix(f".json.bak_{timestamp}")
    try:
        with backup_path.open("w", encoding="utf-8") as bf:
            # Preserve original structure as list (consistent with workspace usage)
            json.dump(to_sorted_list(target_map), bf, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"ERROR: failed to create backup: {e}", file=sys.stderr)
        sys.exit(1)

    # Write merged
    try:
        with TARGET.open("w", encoding="utf-8") as tf:
            json.dump(to_sorted_list(merged), tf, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"ERROR: failed to write merged SPRs: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nMerged successfully. Backup written to: {backup_path.name}")
    print(f"New total SPRs       : {len(merged)}")
    if to_add:
        print(f"Added IDs            : {', '.join(sorted(to_add.keys())[:20])}{' ...' if len(to_add) > 20 else ''}")


if __name__ == "__main__":
    main()


