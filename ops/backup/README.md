# aRCHe Backup (Backup Mandate Implementation)

This folder implements the Backup Mandate with runnable scripts and config.

## Objectives
- RPO: ≤ 15m for registries/knowledge; ≤ 24h for static code/docs
- RTO: ≤ 2h (node) / ≤ 8h (site)
- Integrity: SHA-256 manifest; immutable offsite (recommend object-lock)
- Verification: daily file-level; monthly full drill

## Contents
- `backup_config.json`: assets, include/exclude globs, backup dir
- `backup_manifest.py`: generate cryptographic manifest
- `backup_run.py`: manifest + copy payload + tar.gz archive
- `verify_restore.py`: verify payload hashes and Zepto artifact sanity

## Quickstart
From project root (`Happier/`):
```bash
python3 ops/backup/backup_run.py
python3 ops/backup/verify_restore.py
```

Artifacts:
```
.backups/<UTC_TIMESTAMP>/
  ├─ manifest.json
  ├─ payload/             # tree-preserved copy of assets
  └─ backup.tar.gz        # manifest + payload archive
```

## Scheduling (examples)
- Incremental: run `backup_run.py` every 15 minutes for hot JSON/registries.
- Nightly: daily full snapshot via `backup_run.py`.
- Weekly: copy `backup.tar.gz` offsite (e.g., `rclone copy`, S3 object-lock).

## Verification
```bash
python3 ops/backup/verify_restore.py
```
Pass conditions:
- All payload file hashes match manifest.
- `zepto_with_spr_context.json` parses and contains `zepto_spr` and `spr_context_zepto`.

## Restore (runbook high level)
1) Select a backup under `.backups/<UTC_TIMESTAMP>/`.
2) Validate with `verify_restore.py`.
3) Restore order:
   - knowledge: `knowledge_graph/spr_definitions_tv.json`
   - workflows: `workflows/`
   - Zepto: `zepto_with_spr_context.json`, `zepto_with_spr_context_prompt.txt`
   - core code: `Three_PointO_ArchE/`, key scripts (`compress_with_spr_context.py`, `api/mcp_api_server.py`)
   - registries/logical state: `arche_registry.json`
   - docs: `cleanup.md`, READMEs
4) Service bring-up as per environment.

## Notes
- Offsite retention and encryption are environment-specific; implement via your storage tool (S3 + KMS/Object-Lock, GCS Autoclass, etc.).
- Update `backup_config.json` when onboarding new critical assets.
- Record drill outcomes (RPO/RTO, hash parity) in ops log.


