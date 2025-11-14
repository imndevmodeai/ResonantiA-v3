#!/usr/bin/env python3
"""
Re-compress SPRs using proper symbol substitution from codex.
Ensures zepto_spr contains actual symbols (Ω, Δ, Φ, etc.) not just compressed text.

Usage:
  python scripts/zepto_resymbolize_sprs.py --dry-run
  python scripts/zepto_resymbolize_sprs.py
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "knowledge_graph" / "spr_definitions_tv.json"
CODEX_PATH = ROOT / "knowledge_graph" / "symbol_codex.json"
PROTOCOL_VOCAB_PATH = ROOT / "knowledge_graph" / "protocol_symbol_vocabulary.json"


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
    raise ValueError("Unsupported SPR data format")


def build_narrative(spr: dict) -> str:
    """Build narrative from SPR for compression."""
    term = spr.get("term", spr.get("spr_id", ""))
    definition = spr.get("definition", "")
    blueprint = spr.get("blueprint_details", "")
    example = spr.get("example_application", "")
    return f"{term}\nDefinition: {definition}\nBlueprint: {blueprint}\nExample: {example}"


def has_symbols(zepto_spr: str) -> bool:
    """Check if zepto_spr contains actual symbols (not just text)."""
    if not zepto_spr:
        return False
    
    # Check for protocol symbols
    protocol_symbols = ['Ω', 'Δ', 'Φ', 'Θ', 'Λ', 'Σ', 'Π', 'Æ']
    # Check for mathematical/special symbols
    special_chars = ['→', '⊗', '⊕', 'ℋ', 'ℳ', '‖', '⟩', '𝟙']
    # Check for mandate symbols
    mandate_symbols = ['M₁', 'M₂', 'M₃', 'M₄', 'M₅', 'M₆', 'M₇', 'M₈', 'M₉', 'M₁₀', 'M₁₁', 'M₁₂']
    
    all_symbols = protocol_symbols + special_chars + mandate_symbols
    
    # If zepto_spr contains any of these symbols, it's properly symbolized
    return any(sym in zepto_spr for sym in all_symbols)


def try_resymbolize(adapter, spr_id: str, narrative: str):
    """Re-compress with proper symbol substitution."""
    try:
        result = adapter.compress_to_zepto(
            narrative=narrative,
            target_stage="Zepto",
            context={"spr_id": spr_id, "source": "zepto_resymbolize", "force_symbols": True}
        )
        
        if result and not getattr(result, "error", None):
            # Verify it actually has symbols
            if has_symbols(result.zepto_spr):
                return {
                    "zepto_spr": result.zepto_spr,
                    "symbol_codex": result.new_codex_entries or {},
                    "compression_stages": result.compression_stages or [],
                    "compression_ratio": result.compression_ratio,
                    "has_symbols": True
                }
            else:
                print(f"[warn] {spr_id}: compression didn't produce symbols", file=sys.stderr)
                return None
    except Exception as e:
        print(f"[warn] resymbolization failed for {spr_id}: {e}", file=sys.stderr)
    
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview changes only")
    parser.add_argument("--force-all", action="store_true", help="Re-compress all SPRs, not just non-symbolic ones")
    args = parser.parse_args()

    # Import Zepto adapter
    sys.path.insert(0, str(ROOT))
    try:
        from Three_PointO_ArchE.zepto_spr_processor import ZeptoSPRProcessorAdapter
        adapter = ZeptoSPRProcessorAdapter(
            symbol_codex_path=str(CODEX_PATH),
            protocol_vocabulary_path=str(PROTOCOL_VOCAB_PATH)
        )
        print(f"✓ Loaded symbol codex from {CODEX_PATH}")
        print(f"✓ Loaded protocol vocabulary from {PROTOCOL_VOCAB_PATH}")
    except Exception as e:
        print(f"[error] ZeptoSPRProcessorAdapter unavailable: {e}", file=sys.stderr)
        sys.exit(1)

    data = load_json(TARGET)
    spr_list = normalize_to_list(data)
    index = {spr.get("spr_id"): spr for spr in spr_list if isinstance(spr, dict)}

    # Find SPRs that need re-symbolization
    candidates = []
    for spr_id, spr in index.items():
        if not spr:
            continue
        
        zepto = spr.get("zepto_spr", "")
        if not zepto:
            continue  # Skip if no zepto_spr at all
        
        # Check if it has actual symbols
        if args.force_all or not has_symbols(zepto):
            candidates.append(spr_id)

    print(f"\nSPRs needing re-symbolization: {len(candidates)}")
    if not candidates:
        print("All SPRs already have symbolic zepto_spr!")
        return

    updated = []
    failed = []
    
    for i, spr_id in enumerate(candidates, 1):
        spr = index.get(spr_id)
        if not spr:
            continue
        
        narrative = build_narrative(spr)
        comp = try_resymbolize(adapter, spr_id, narrative)
        
        if comp and comp.get("has_symbols"):
            spr["zepto_spr"] = comp["zepto_spr"]
            if comp.get("symbol_codex"):
                # Merge new codex entries
                existing_codex = spr.get("symbol_codex", {})
                existing_codex.update(comp["symbol_codex"])
                spr["symbol_codex"] = existing_codex
            if comp.get("compression_stages"):
                spr["compression_stages"] = comp["compression_stages"]
            if comp.get("compression_ratio"):
                spr["compression_ratio"] = comp["compression_ratio"]
            updated.append(spr_id)
            print(f"[{i}/{len(candidates)}] ✓ {spr_id}: {len(comp['zepto_spr'])} chars, ratio {comp['compression_ratio']:.1f}:1")
        else:
            failed.append(spr_id)
            print(f"[{i}/{len(candidates)}] ✗ {spr_id}: failed to resymbolize")

    print(f"\n=== Summary ===")
    print(f"Updated with symbols: {len(updated)}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print(f"\nFailed IDs: {', '.join(failed[:10])}{'...' if len(failed) > 10 else ''}")

    if args.dry_run:
        print("\nDry-run: no changes written.")
        return

    if updated:
        # Backup and write
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup = TARGET.with_suffix(f".json.resymbolize_bak_{ts}")
        save_json(backup, spr_list)
        save_json(TARGET, spr_list)
        print(f"\n✓ Saved. Backup: {backup.name}")


if __name__ == "__main__":
    main()

