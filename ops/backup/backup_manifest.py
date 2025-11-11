#!/usr/bin/env python3
"""
Generate a cryptographic manifest for backup assets.
 - Loads ops/backup/backup_config.json
 - Expands assets (files/dirs) respecting include/exclude globs
 - Computes SHA-256, size, and mtime for each file
 - Writes manifest to .backups/<timestamp>/manifest.json
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Set

try:
    import fnmatch
except ImportError:
    # Fallback minimal matcher (should not happen in stdlib environments)
    fnmatch = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "ops" / "backup" / "backup_config.json"


@dataclass
class FileEntry:
    path: str
    sha256: str
    size: int
    mtime_iso: str


def load_config() -> Dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def sha256_file(p: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def match_any(path: str, patterns: Iterable[str]) -> bool:
    if not patterns:
        return False
    for pat in patterns:
        if fnmatch.fnmatch(path, pat):
            return True
    return False


def iter_files_for_asset(root: Path, asset: Path, include: List[str], exclude: List[str]) -> Iterable[Path]:
    if asset.is_file():
        rel = str(asset.relative_to(root))
        if (not include or match_any(rel, include)) and not match_any(rel, exclude):
            yield asset
        return
    if asset.is_dir():
        for p in asset.rglob("*"):
            if not p.is_file():
                continue
            rel = str(p.relative_to(root))
            if include and not match_any(rel, include):
                continue
            if match_any(rel, exclude):
                continue
            yield p


def collect_files(config: Dict) -> List[Path]:
    include = config.get("include_globs", [])
    exclude = config.get("exclude_globs", [])
    files: List[Path] = []
    for a in config.get("assets", []):
        ap = (PROJECT_ROOT / a).resolve()
        if not ap.exists():
            continue
        files.extend(iter_files_for_asset(PROJECT_ROOT, ap, include, exclude))
    # De-duplicate while preserving order
    seen: Set[str] = set()
    unique: List[Path] = []
    for f in files:
        k = str(f)
        if k not in seen:
            seen.add(k)
            unique.append(f)
    return unique


def write_manifest(config: Dict, entries: List[FileEntry], manifest_dir: Path) -> Path:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "assets": config.get("assets", []),
        "files": [asdict(e) for e in entries],
    }
    out = manifest_dir / "manifest.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return out


def main() -> int:
    config = load_config()
    backup_dir = PROJECT_ROOT / config.get("backup_dir", ".backups")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = backup_dir / ts

    entries: List[FileEntry] = []
    files = collect_files(config)
    for fp in files:
        try:
            stat = fp.stat()
            entries.append(
                FileEntry(
                    path=str(fp.relative_to(PROJECT_ROOT)),
                    sha256=sha256_file(fp),
                    size=stat.st_size,
                    mtime_iso=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                )
            )
        except Exception as e:
            # Skip unreadable files but continue
            print(f"[warn] Skipping {fp}: {e}", file=sys.stderr)
            continue

    out = write_manifest(config, entries, run_dir)
    print(f"Manifest written: {out}")
    print(f"Files listed: {len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


