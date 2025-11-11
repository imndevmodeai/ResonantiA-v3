#!/usr/bin/env python3
"""
Verify latest backup:
 - Recompute SHA-256 over payload and compare with manifest
 - Perform Zepto artifact sanity checks (presence + JSON structure)
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def sha256_file(p: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def latest_run_dir(base: Path) -> Path | None:
    if not base.exists():
        return None
    runs = sorted([p for p in base.iterdir() if p.is_dir()], reverse=True)
    return runs[0] if runs else None


def main() -> int:
    cfg = json.loads((PROJECT_ROOT / "ops" / "backup" / "backup_config.json").read_text(encoding="utf-8"))
    backup_dir = PROJECT_ROOT / cfg.get("backup_dir", ".backups")
    run_dir = latest_run_dir(backup_dir)
    if not run_dir:
        print("No backup runs found.")
        return 1

    manifest_path = run_dir / "manifest.json"
    payload_dir = run_dir / "payload"
    if not manifest_path.exists() or not payload_dir.exists():
        print("Manifest or payload missing.")
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files", [])

    # 1) Hash verification
    mismatches = []
    missing = []
    for f in files:
        rel = f["path"]
        expected = f["sha256"]
        p = payload_dir / rel
        if not p.exists():
            missing.append(rel)
            continue
        actual = sha256_file(p)
        if actual != expected:
            mismatches.append((rel, expected, actual))

    if missing:
        print(f"[fail] Missing files: {len(missing)}")
    if mismatches:
        print(f"[fail] Hash mismatches: {len(mismatches)}")
    if missing or mismatches:
        for rel, *rest in mismatches:
            print(f"  - {rel}: mismatch")
        for rel in missing:
            print(f"  - {rel}: missing")
        return 2

    print("[ok] Payload hash verification passed.")

    # 2) Zepto artifact sanity checks
    zepto_json = payload_dir / "zepto_with_spr_context.json"
    zepto_prompt = payload_dir / "zepto_with_spr_context_prompt.txt"
    if not zepto_json.exists() or not zepto_prompt.exists():
        print("[warn] Zepto artifacts not found in payload; skipping decompression checks.")
        return 0
    try:
        data = json.loads(zepto_json.read_text(encoding="utf-8"))
        if "zepto_spr" not in data or not isinstance(data.get("spr_context_zepto", {}), dict):
            print("[fail] Zepto JSON structure invalid: expected 'zepto_spr' and 'spr_context_zepto'.")
            return 3
    except Exception as e:
        print(f"[fail] Unable to parse Zepto JSON: {e}")
        return 3

    print("[ok] Zepto artifacts sanity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


