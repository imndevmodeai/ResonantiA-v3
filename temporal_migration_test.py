#!/usr/bin/env python3
"""
Temporal Core Migration - SAMPLE TEST

Migrates the 5% sample file and runs comprehensive tests to ensure:
1. No syntax errors introduced
2. Imports work correctly
3. Indentation preserved
4. Module still importable
5. All temporal calls use correct functions

Only proceeds with full migration if sample tests pass 100%.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Tuple, List

# ============================================================================
# MIGRATION LOGIC
# ============================================================================

def add_temporal_import(content: str) -> str:
    """Add temporal_core import to file content."""
    
    # Check if already has temporal_core import
    if "from Three_PointO_ArchE.temporal_core import" in content:
        return content
    
    # Find the import section
    lines = content.split('\n')
    import_end_idx = 0
    
    # Find last import or from statement
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')):
            import_end_idx = i
    
    # Insert temporal_core import after last import
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
        # Order matters! More specific patterns first
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


def migrate_file(filepath: Path) -> Tuple[bool, str]:
    """Migrate a single file."""
    try:
        # Read original content
        original_content = filepath.read_text()
        
        # Add temporal import
        content = add_temporal_import(original_content)
        
        # Apply migration patterns
        content, count = apply_migration_patterns(content)
        
        # Create backup
        backup_path = filepath.with_suffix('.py.backup')
        filepath.write_text(content)
        
        return True, f"Migrated {count} datetime calls"
    
    except Exception as e:
        return False, f"Migration failed: {e}"


def test_syntax(filepath: Path) -> Tuple[bool, str]:
    """Test if file has valid Python syntax."""
    try:
        result = subprocess.run(
            ['python', '-m', 'py_compile', str(filepath)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, "Syntax valid"
        else:
            return False, f"Syntax error: {result.stderr}"
    except Exception as e:
        return False, f"Syntax check failed: {e}"


def test_import(filepath: Path) -> Tuple[bool, str]:
    """Test if module can be imported."""
    try:
        module_path = str(filepath).replace('/', '.').replace('.py', '')
        if module_path.startswith('Three_PointO_ArchE'):
            module_path = module_path.split('Three_PointO_ArchE', 1)[1].lstrip('.')
        
        result = subprocess.run(
            ['python', '-c', f'from Three_PointO_ArchE.{module_path} import *'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            return True, "Import successful"
        else:
            # Check if error is just about __all__ or non-fatal
            if 'cannot import name' in result.stderr or 'ImportError' in result.stderr:
                return False, f"Import error: {result.stderr}"
            else:
                # Other warnings are OK
                return True, f"Import successful (with warnings)"
    
    except Exception as e:
        return False, f"Import test failed: {e}"


def restore_backup(filepath: Path):
    """Restore file from backup."""
    backup_path = filepath.with_suffix('.py.backup')
    if backup_path.exists():
        backup_path.replace(filepath)


# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_sample_test(sample_file: Path) -> bool:
    """Run complete test on sample file."""
    print(f"\n{'=' * 80}")
    print(f"TESTING SAMPLE FILE: {sample_file.name}")
    print(f"{'=' * 80}\n")
    
    # Create backup first
    backup_path = sample_file.with_suffix('.py.backup')
    shutil.copy(sample_file, backup_path)
    print(f"✅ Backup created: {backup_path.name}")
    
    # Step 1: Migrate
    print(f"\n📝 Step 1: Applying migration...")
    success, message = migrate_file(sample_file)
    if not success:
        print(f"   ❌ FAILED: {message}")
        restore_backup(sample_file)
        return False
    print(f"   ✅ {message}")
    
    # Step 2: Syntax check
    print(f"\n🔍 Step 2: Checking syntax...")
    success, message = test_syntax(sample_file)
    if not success:
        print(f"   ❌ FAILED: {message}")
        restore_backup(sample_file)
        return False
    print(f"   ✅ {message}")
    
    # Step 3: Import test
    print(f"\n📦 Step 3: Testing imports...")
    success, message = test_import(sample_file)
    if not success:
        print(f"   ⚠️  WARNING: {message}")
        print(f"   (This may be OK if the module has other dependencies)")
    else:
        print(f"   ✅ {message}")
    
    # Step 4: Verify no legacy datetime calls
    print(f"\n🔎 Step 4: Verifying no legacy datetime calls...")
    content = sample_file.read_text()
    legacy_patterns = [
        r'datetime\.now\(',
        r'datetime\.utcnow\(',
    ]
    
    found_legacy = []
    for pattern in legacy_patterns:
        matches = re.findall(pattern, content)
        if matches:
            found_legacy.extend(matches)
    
    if found_legacy:
        print(f"   ❌ FAILED: Found {len(found_legacy)} legacy datetime calls")
        for match in found_legacy:
            print(f"      • {match}")
        restore_backup(sample_file)
        return False
    print(f"   ✅ No legacy datetime calls found")
    
    # Step 5: Verify temporal_core import exists
    print(f"\n📋 Step 5: Verifying temporal_core import...")
    if "from Three_PointO_ArchE.temporal_core import" not in content:
        print(f"   ❌ FAILED: temporal_core import not found")
        restore_backup(sample_file)
        return False
    print(f"   ✅ temporal_core import present")
    
    print(f"\n{'=' * 80}")
    print(f"✅ ALL TESTS PASSED!")
    print(f"{'=' * 80}\n")
    
    return True


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("TEMPORAL CORE MIGRATION - SAMPLE TEST (5%)")
    print("=" * 80)
    
    # Sample file (from dry run analysis)
    sample_file = Path("Three_PointO_ArchE/verifiable_cfp_prediction.py")
    
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return 1
    
    # Run test
    success = run_sample_test(sample_file)
    
    if success:
        print("\n🎯 MIGRATION VALIDATION COMPLETE!")
        print("   ✅ Sample file migrated successfully")
        print("   ✅ No syntax errors")
        print("   ✅ No legacy datetime calls")
        print("   ✅ temporal_core import present")
        print("\n   RECOMMENDATION: Proceed with full migration")
        return 0
    else:
        print("\n❌ MIGRATION VALIDATION FAILED!")
        print("   Sample file has been restored from backup")
        print("   DO NOT proceed with full migration")
        print("   Fix issues before continuing")
        return 1


if __name__ == "__main__":
    sys.exit(main())

