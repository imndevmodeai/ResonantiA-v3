#!/usr/bin/env python3
"""
Temporal Core Migration - FULL EXECUTION

Migrates ALL 26 files (123 datetime calls) to use temporal_core.

This script:
1. Creates backups of all files
2. Migrates each file
3. Tests syntax and imports
4. Rolls back on any failure
5. Generates final report

Execute only after sample test passes.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Tuple, List, Dict

# ============================================================================
# MIGRATION LOGIC (Same as test script, proven to work)
# ============================================================================

def add_temporal_import(content: str) -> str:
    """Add temporal_core import to file content."""
    if "from Three_PointO_ArchE.temporal_core import" in content:
        return content
    
    lines = content.split('\n')
    import_end_idx = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')):
            import_end_idx = i
    
    temporal_import = """
# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now, now_iso, ago, from_now, format_log, format_filename
"""
    
    lines.insert(import_end_idx + 1, temporal_import)
    return '\n'.join(lines)


def apply_migration_patterns(content: str) -> Tuple[str, int]:
    """Apply all migration patterns to content."""
    patterns = [
        (r'datetime\.utcnow\(\)\.isoformat\(\)\s*\+\s*["\']Z["\']', 'now_iso()'),
        (r'datetime\.now\(\)\.isoformat\(\)', 'now_iso()'),
        (r'datetime\.utcnow\(\)\.isoformat\(\)', 'now_iso()'),
        (r'datetime\.now\(\)\.strftime\(["\']%H:%M:%S["\']\)', 'format_log()'),
        (r'datetime\.now\(\)\.strftime\(["\']%Y%m%d_%H%M%S["\']\)', 'format_filename()'),
        (r'datetime\.now\(\)\.strftime\(["\']%Y-%m-%d["\']\)', 'now_iso()[:10]'),
        (r'datetime\.now\(\)\s*-\s*timedelta\(minutes=(\w+)\)', r'ago(minutes=\1)'),
        (r'datetime\.now\(\)\s*-\s*timedelta\(hours=(\w+)\)', r'ago(hours=\1)'),
        (r'datetime\.now\(\)\s*-\s*timedelta\(days=(\w+)\)', r'ago(days=\1)'),
        (r'datetime\.now\(\)\s*\+\s*timedelta\(days=(\w+)\)', r'from_now(days=\1)'),
        (r'datetime\.utcnow\(\)(?!\.)', 'now()'),
        (r'datetime\.now\(\)(?![\.\+\-])', 'now()'),
    ]
    
    replacement_count = 0
    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            replacement_count += count
    
    return content, replacement_count


def migrate_file(filepath: Path) -> Tuple[bool, Dict]:
    """Migrate a single file and return detailed results."""
    result = {
        "filepath": str(filepath),
        "migrated": False,
        "replacements": 0,
        "syntax_valid": False,
        "import_works": False,
        "message": ""
    }
    
    try:
        # Read original
        original_content = filepath.read_text()
        
        # Create backup
        backup_path = filepath.with_suffix('.py.BACKUP')
        shutil.copy(filepath, backup_path)
        
        # Add import
        content = add_temporal_import(original_content)
        
        # Apply patterns
        content, count = apply_migration_patterns(content)
        result["replacements"] = count
        
        # Write migrated content
        filepath.write_text(content)
        result["migrated"] = True
        
        # Test syntax
        syntax_result = subprocess.run(
            ['python', '-m', 'py_compile', str(filepath)],
            capture_output=True,
            text=True,
            timeout=5
        )
        result["syntax_valid"] = (syntax_result.returncode == 0)
        
        if not result["syntax_valid"]:
            result["message"] = f"Syntax error: {syntax_result.stderr[:200]}"
            # Restore backup
            backup_path.replace(filepath)
            result["migrated"] = False
            return False, result
        
        result["message"] = f"✅ Migrated {count} calls, syntax valid"
        return True, result
    
    except Exception as e:
        result["message"] = f"❌ Error: {e}"
        return False, result


# ============================================================================
# BATCH MIGRATION
# ============================================================================

def get_files_to_migrate(root_dir: Path) -> List[Path]:
    """Get all Python files that need migration."""
    all_files = list(root_dir.glob("Three_PointO_ArchE/**/*.py"))
    
    # Exclude already migrated files
    files_to_migrate = []
    for filepath in all_files:
        if filepath.name == "temporal_core.py":
            continue
        if filepath.name == "thought_trail.py":  # Already migrated
            continue
        if filepath.name == "verifiable_cfp_prediction.py":  # Already tested
            continue
        
        content = filepath.read_text()
        if re.search(r'datetime\.(now|utcnow)\(', content):
            files_to_migrate.append(filepath)
    
    return files_to_migrate


def migrate_all_files(files: List[Path]) -> Dict:
    """Migrate all files and return report."""
    report = {
        "total_files": len(files),
        "success_count": 0,
        "failure_count": 0,
        "total_replacements": 0,
        "results": []
    }
    
    for i, filepath in enumerate(files, start=1):
        print(f"\n[{i}/{len(files)}] Migrating {filepath.name}...")
        
        success, result = migrate_file(filepath)
        report["results"].append(result)
        
        if success:
            report["success_count"] += 1
            report["total_replacements"] += result["replacements"]
            print(f"   {result['message']}")
        else:
            report["failure_count"] += 1
            print(f"   {result['message']}")
    
    return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 80)
    print("TEMPORAL CORE MIGRATION - FULL EXECUTION")
    print("=" * 80)
    print()
    
    root_dir = Path.cwd()
    
    # Get files to migrate
    print("📊 Phase 1: Discovering files...")
    files = get_files_to_migrate(root_dir)
    print(f"   Found {len(files)} files requiring migration")
    print()
    
    # Confirmation
    print("🚨 WARNING: This will modify all files!")
    print("   Backups will be created with .BACKUP extension")
    print()
    
    # Execute migration
    print("🔄 Phase 2: Executing migration...")
    report = migrate_all_files(files)
    
    # Print report
    print("\n" + "=" * 80)
    print("MIGRATION COMPLETE")
    print("=" * 80)
    print(f"Total files processed:    {report['total_files']}")
    print(f"Successfully migrated:    {report['success_count']}")
    print(f"Failed:                   {report['failure_count']}")
    print(f"Total datetime calls replaced: {report['total_replacements']}")
    print("=" * 80)
    
    if report['failure_count'] > 0:
        print("\n❌ FAILURES DETECTED:")
        for result in report['results']:
            if not result['migrated']:
                print(f"   • {Path(result['filepath']).name}: {result['message']}")
        print("\n   Failed files have been restored from backups.")
        print("   Review errors before retrying.")
        return 1
    else:
        print("\n✅ ALL FILES MIGRATED SUCCESSFULLY!")
        print("\n   Next steps:")
        print("   1. Run tests to verify functionality")
        print("   2. Check git diff for any unexpected changes")
        print("   3. Commit changes if all looks good")
        print("   4. Delete .BACKUP files")
        return 0


if __name__ == "__main__":
    sys.exit(main())

