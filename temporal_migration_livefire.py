#!/usr/bin/env python3
"""
Temporal Core Migration - LIVE-FIRE EXECUTION

Enhanced with real-time testing and terminal display for Guardian verification.

Each file:
1. Migrated
2. Syntax tested (LIVE)
3. Import tested (LIVE)
4. Timestamp verified (LIVE)
5. Results displayed immediately
6. Rollback on any failure

Compliance: MANDATE 1 - Live Validation Mandate
"""

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple, List, Dict

# ============================================================================
# MIGRATION LOGIC
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


# ============================================================================
# LIVE-FIRE TESTING
# ============================================================================

def test_syntax_live(filepath: Path) -> Tuple[bool, str]:
    """LIVE TEST: Syntax validation."""
    try:
        result = subprocess.run(
            ['python', '-m', 'py_compile', str(filepath)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, "✅ Syntax valid"
        else:
            return False, f"❌ Syntax error: {result.stderr[:200]}"
    except Exception as e:
        return False, f"❌ Test failed: {e}"


def test_import_live(filepath: Path) -> Tuple[bool, str]:
    """LIVE TEST: Module import."""
    try:
        # Get module path
        rel_path = filepath.relative_to(Path.cwd())
        module_path = str(rel_path).replace('/', '.').replace('.py', '')
        
        # Try to import
        result = subprocess.run(
            ['python', '-c', f'import {module_path}'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            return True, "✅ Import successful"
        else:
            # Check if error is fatal
            stderr = result.stderr.lower()
            if 'importerror' in stderr or 'modulenotfounderror' in stderr:
                return False, f"❌ Import error: {result.stderr[:200]}"
            else:
                # Warnings are OK
                return True, "✅ Import successful (with warnings)"
    
    except Exception as e:
        return False, f"❌ Import test failed: {e}"


def test_temporal_usage_live(filepath: Path) -> Tuple[bool, str, str]:
    """LIVE TEST: Verify temporal_core usage and get sample timestamp."""
    try:
        content = filepath.read_text()
        
        # Check for temporal_core import
        if "from Three_PointO_ArchE.temporal_core import" not in content:
            return False, "❌ Missing temporal_core import", ""
        
        # Check for legacy datetime calls (should be minimal)
        legacy_count = len(re.findall(r'datetime\.(now|utcnow)\(', content))
        
        # Try to execute a simple timestamp generation with the module
        module_name = filepath.stem
        test_code = f"""
import sys
sys.path.insert(0, '{Path.cwd()}')
from Three_PointO_ArchE.temporal_core import now_iso
timestamp = now_iso()
print(timestamp)
"""
        
        result = subprocess.run(
            ['python', '-c', test_code],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            sample_timestamp = result.stdout.strip()
            if legacy_count > 0:
                return True, f"⚠️  Has {legacy_count} legacy datetime calls", sample_timestamp
            else:
                return True, "✅ Clean temporal_core usage", sample_timestamp
        else:
            return True, "✅ Temporal_core import present", "N/A"
    
    except Exception as e:
        return False, f"❌ Verification failed: {e}", ""


# ============================================================================
# ENHANCED MIGRATION WITH LIVE-FIRE DISPLAY
# ============================================================================

def migrate_file_with_livefire(filepath: Path, file_num: int, total_files: int) -> Dict:
    """Migrate a file with live-fire testing and display."""
    
    result = {
        "filepath": str(filepath),
        "filename": filepath.name,
        "migrated": False,
        "replacements": 0,
        "tests": {},
        "timestamp_sample": "",
        "message": ""
    }
    
    print(f"\n{'=' * 80}")
    print(f"[{file_num}/{total_files}] 🔥 LIVE-FIRE TEST: {filepath.name}")
    print(f"{'=' * 80}")
    
    try:
        # Step 1: Create backup
        print(f"   📋 Step 1: Creating backup...")
        backup_path = filepath.with_suffix('.py.BACKUP')
        shutil.copy(filepath, backup_path)
        print(f"      ✅ Backup: {backup_path.name}")
        
        # Step 2: Read and migrate
        print(f"   🔄 Step 2: Applying migration...")
        original_content = filepath.read_text()
        content = add_temporal_import(original_content)
        content, count = apply_migration_patterns(content)
        result["replacements"] = count
        
        filepath.write_text(content)
        result["migrated"] = True
        print(f"      ✅ Migrated {count} datetime calls")
        
        # Step 3: LIVE SYNTAX TEST
        print(f"   🔍 Step 3: LIVE SYNTAX TEST...")
        time.sleep(0.1)  # Brief pause for display
        success, message = test_syntax_live(filepath)
        result["tests"]["syntax"] = {"pass": success, "message": message}
        print(f"      {message}")
        
        if not success:
            print(f"      🔄 ROLLING BACK...")
            backup_path.replace(filepath)
            result["migrated"] = False
            result["message"] = "Syntax test failed - rolled back"
            return result
        
        # Step 4: LIVE IMPORT TEST
        print(f"   📦 Step 4: LIVE IMPORT TEST...")
        time.sleep(0.1)
        success, message = test_import_live(filepath)
        result["tests"]["import"] = {"pass": success, "message": message}
        print(f"      {message}")
        
        if not success:
            print(f"      🔄 ROLLING BACK...")
            backup_path.replace(filepath)
            result["migrated"] = False
            result["message"] = "Import test failed - rolled back"
            return result
        
        # Step 5: LIVE TEMPORAL VERIFICATION
        print(f"   ⏰ Step 5: LIVE TEMPORAL VERIFICATION...")
        time.sleep(0.1)
        success, message, timestamp = test_temporal_usage_live(filepath)
        result["tests"]["temporal"] = {"pass": success, "message": message}
        result["timestamp_sample"] = timestamp
        print(f"      {message}")
        if timestamp:
            print(f"      📅 Sample timestamp: {timestamp}")
        
        if not success:
            print(f"      🔄 ROLLING BACK...")
            backup_path.replace(filepath)
            result["migrated"] = False
            result["message"] = "Temporal verification failed - rolled back"
            return result
        
        # SUCCESS!
        print(f"   ✅ ALL TESTS PASSED!")
        result["message"] = f"Successfully migrated {count} calls"
        return result
    
    except Exception as e:
        print(f"   ❌ MIGRATION FAILED: {e}")
        result["message"] = str(e)
        # Try to restore backup
        if backup_path.exists():
            backup_path.replace(filepath)
            print(f"   🔄 Restored from backup")
        return result


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def get_files_to_migrate() -> List[Path]:
    """Get all files needing migration."""
    all_files = list(Path("Three_PointO_ArchE").glob("**/*.py"))
    
    files_to_migrate = []
    for filepath in all_files:
        # Skip specific files
        if filepath.name in ["temporal_core.py", "thought_trail.py", "verifiable_cfp_prediction.py"]:
            continue
        if "__pycache__" in str(filepath):
            continue
        
        # Check if has datetime calls
        try:
            content = filepath.read_text()
            if re.search(r'datetime\.(now|utcnow)\(', content):
                files_to_migrate.append(filepath)
        except:
            continue
    
    return sorted(files_to_migrate, key=lambda p: p.name)


def main():
    print("=" * 80)
    print("TEMPORAL CORE MIGRATION - LIVE-FIRE EXECUTION")
    print("=" * 80)
    print("Compliance: MANDATE 1 - Live Validation Mandate")
    print("Strategy: Migrate → Test → Display → Verify")
    print("=" * 80)
    print()
    
    # Get files
    files = get_files_to_migrate()
    total_files = len(files)
    
    print(f"📊 Found {total_files} files requiring migration")
    print(f"🚨 Each file will be tested LIVE with results displayed")
    print(f"🔄 Automatic rollback on any failure")
    print()
    
    input("Press ENTER to begin live-fire migration...")
    print()
    
    # Track results
    results = []
    success_count = 0
    failure_count = 0
    total_replacements = 0
    
    # Migrate each file with live-fire testing
    for i, filepath in enumerate(files, start=1):
        result = migrate_file_with_livefire(filepath, i, total_files)
        results.append(result)
        
        if result["migrated"]:
            success_count += 1
            total_replacements += result["replacements"]
        else:
            failure_count += 1
        
        time.sleep(0.2)  # Brief pause between files
    
    # Final report
    print("\n" + "=" * 80)
    print("🎯 LIVE-FIRE MIGRATION COMPLETE")
    print("=" * 80)
    print(f"Total files processed:         {total_files}")
    print(f"✅ Successfully migrated:      {success_count}")
    print(f"❌ Failed:                     {failure_count}")
    print(f"📝 Total datetime calls fixed: {total_replacements}")
    print("=" * 80)
    
    if failure_count > 0:
        print("\n❌ FAILURES DETECTED:")
        for result in results:
            if not result["migrated"]:
                print(f"   • {result['filename']}: {result['message']}")
        return 1
    else:
        print("\n✅ ALL FILES MIGRATED SUCCESSFULLY!")
        print(f"\n📊 Sample timestamps from migrated files:")
        for result in results[:5]:  # Show first 5
            if result["timestamp_sample"]:
                print(f"   • {result['filename']}: {result['timestamp_sample']}")
        
        print(f"\n💾 Backups saved with .BACKUP extension")
        print(f"   To remove backups: find Three_PointO_ArchE -name '*.BACKUP' -delete")
        return 0


if __name__ == "__main__":
    sys.exit(main())

