#!/usr/bin/env python3
"""
Run a backup using the manifest:
 - Generates a fresh manifest
 - Copies files into .backups/<timestamp>/payload preserving tree
 - Emits a tar.gz archive of the payload and the manifest
"""
from __future__ import annotations

import json
import os
import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "ops" / "backup" / "backup_config.json"
MANIFEST_SCRIPT = PROJECT_ROOT / "ops" / "backup" / "backup_manifest.py"


def load_config() -> Dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def latest_run_dir(base: Path) -> Path | None:
    if not base.exists():
        return None
    runs = sorted([p for p in base.iterdir() if p.is_dir()], reverse=True)
    return runs[0] if runs else None


def main() -> int:
    # 1) Generate manifest
    os.system(f'"{MANIFEST_SCRIPT}"')  # simple handoff

    # 2) Determine run dir
    config = load_config()
    backup_dir = PROJECT_ROOT / config.get("backup_dir", ".backups")
    run_dir = latest_run_dir(backup_dir)
    if run_dir is None:
        print("No manifest run directory found.")
        return 1

    payload_dir = run_dir / "payload"
    payload_dir.mkdir(parents=True, exist_ok=True)

    with open(run_dir / "manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    files = manifest.get("files", [])

    # 3) Copy files
    for f in files:
        rel = f["path"]
        src = PROJECT_ROOT / rel
        dst = payload_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # 4) Create tar.gz archive
    archive_path = run_dir / "backup.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(run_dir / "manifest.json", arcname="manifest.json")
        tar.add(payload_dir, arcname="payload")

    print(f"Backup complete: {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


