#!/usr/bin/env python3
"""
Temporal Core Migration - DRY RUN ANALYSIS

This script analyzes all datetime calls in ArchE and creates a migration plan
WITHOUT modifying any files. It tests the migration logic on a sample set
to ensure accuracy before executing the full migration.

Usage:
    python temporal_migration_dryrun.py
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# ============================================================================
# MIGRATION PATTERNS
# ============================================================================

MIGRATION_PATTERNS = {
    # Pattern 1: datetime.now().isoformat() → now_iso()
    "now_isoformat": {
        "regex": r'datetime\.now\(\)\.isoformat\(\)',
        "replacement": "now_iso()",
        "needs_import": "now_iso"
    },
    
    # Pattern 2: datetime.utcnow().isoformat() → now_iso()
    "utcnow_isoformat": {
        "regex": r'datetime\.utcnow\(\)\.isoformat\(\)',
        "replacement": "now_iso()",
        "needs_import": "now_iso"
    },
    
    # Pattern 3: datetime.utcnow().isoformat() + "Z" → now_iso()
    "utcnow_isoformat_z": {
        "regex": r'datetime\.utcnow\(\)\.isoformat\(\)\s*\+\s*["\']Z["\']',
        "replacement": "now_iso()",
        "needs_import": "now_iso"
    },
    
    # Pattern 4: datetime.now().strftime(...) → format_log(), format_filename(), etc.
    "now_strftime_hms": {
        "regex": r'datetime\.now\(\)\.strftime\(["\']%H:%M:%S["\']\)',
        "replacement": "format_log()",
        "needs_import": "format_log"
    },
    
    "now_strftime_filename": {
        "regex": r'datetime\.now\(\)\.strftime\(["\']%Y%m%d_%H%M%S["\']\)',
        "replacement": "format_filename()",
        "needs_import": "format_filename"
    },
    
    "now_strftime_date": {
        "regex": r'datetime\.now\(\)\.strftime\(["\']%Y-%m-%d["\']\)',
        "replacement": "now_iso()[:10]",
        "needs_import": "now_iso",
        "note": "Extracts YYYY-MM-DD from ISO timestamp"
    },
    
    # Pattern 5: datetime.now() - timedelta(...) → ago(...)
    "now_minus_timedelta_minutes": {
        "regex": r'datetime\.now\(\)\s*-\s*timedelta\(minutes=(\w+)\)',
        "replacement": r"ago(minutes=\1)",
        "needs_import": "ago"
    },
    
    "now_minus_timedelta_hours": {
        "regex": r'datetime\.now\(\)\s*-\s*timedelta\(hours=(\w+)\)',
        "replacement": r"ago(hours=\1)",
        "needs_import": "ago"
    },
    
    "now_minus_timedelta_days": {
        "regex": r'datetime\.now\(\)\s*-\s*timedelta\(days=(\w+)\)',
        "replacement": r"ago(days=\1)",
        "needs_import": "ago"
    },
    
    # Pattern 6: datetime.now() + timedelta(...) → from_now(...)
    "now_plus_timedelta_days": {
        "regex": r'datetime\.now\(\)\s*\+\s*timedelta\(days=(\w+)\)',
        "replacement": r"from_now(days=\1)",
        "needs_import": "from_now"
    },
    
    # Pattern 7: datetime.utcnow() (bare) → now()
    "utcnow_bare": {
        "regex": r'datetime\.utcnow\(\)(?!\.)',
        "replacement": "now()",
        "needs_import": "now"
    },
    
    # Pattern 8: datetime.now() (bare) → now()
    "now_bare": {
        "regex": r'datetime\.now\(\)(?![\.\+\-])',
        "replacement": "now()",
        "needs_import": "now"
    },
}

# ============================================================================
# FILE ANALYSIS
# ============================================================================

def analyze_file(filepath: Path) -> Dict:
    """Analyze a single file for datetime patterns."""
    try:
        content = filepath.read_text()
        lines = content.split('\n')
        
        matches = []
        for pattern_name, pattern_info in MIGRATION_PATTERNS.items():
            regex = re.compile(pattern_info["regex"])
            for line_num, line in enumerate(lines, start=1):
                for match in regex.finditer(line):
                    matches.append({
                        "line_num": line_num,
                        "pattern_name": pattern_name,
                        "original": match.group(0),
                        "replacement": re.sub(pattern_info["regex"], pattern_info["replacement"], match.group(0)),
                        "line_content": line.strip(),
                        "needs_import": pattern_info["needs_import"],
                        "note": pattern_info.get("note", "")
                    })
        
        return {
            "filepath": str(filepath),
            "total_matches": len(matches),
            "matches": matches,
            "has_temporal_import": "from Three_PointO_ArchE.temporal_core import" in content,
            "has_datetime_import": "from datetime import" in content or "import datetime" in content
        }
    except Exception as e:
        return {
            "filepath": str(filepath),
            "error": str(e)
        }

def analyze_codebase(root_dir: Path) -> List[Dict]:
    """Analyze entire codebase."""
    results = []
    
    python_files = list(root_dir.glob("Three_PointO_ArchE/**/*.py"))
    
    # Exclude temporal_core.py itself
    python_files = [f for f in python_files if f.name != "temporal_core.py"]
    
    for filepath in python_files:
        analysis = analyze_file(filepath)
        if analysis.get("total_matches", 0) > 0:
            results.append(analysis)
    
    return results

# ============================================================================
# SAMPLE TESTING (5% of total)
# ============================================================================

def select_sample_files(analyses: List[Dict], sample_pct: float = 0.05) -> List[Dict]:
    """Select 5% sample for testing."""
    total_files = len(analyses)
    sample_count = max(1, int(total_files * sample_pct))
    
    # Prioritize high-impact files
    sorted_analyses = sorted(analyses, key=lambda x: x["total_matches"], reverse=True)
    
    return sorted_analyses[:sample_count]

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 80)
    print("TEMPORAL CORE MIGRATION - DRY RUN ANALYSIS")
    print("=" * 80)
    print()
    
    root_dir = Path(__file__).parent
    
    print("📊 Phase 1: Analyzing codebase...")
    analyses = analyze_codebase(root_dir)
    
    total_files = len(analyses)
    total_matches = sum(a["total_matches"] for a in analyses)
    
    print(f"   ✅ Found {total_matches} datetime calls in {total_files} files")
    print()
    
    print("📋 Phase 2: Top 10 files requiring migration:")
    print("-" * 80)
    sorted_analyses = sorted(analyses, key=lambda x: x["total_matches"], reverse=True)
    for i, analysis in enumerate(sorted_analyses[:10], start=1):
        filepath = Path(analysis["filepath"]).name
        count = analysis["total_matches"]
        print(f"   {i:2}. {filepath:50} ({count:3} calls)")
    print()
    
    print("🧪 Phase 3: Sample Testing (5% of files)...")
    sample_files = select_sample_files(analyses, sample_pct=0.05)
    print(f"   Selected {len(sample_files)} files for validation:")
    print()
    
    for sample in sample_files:
        filepath = Path(sample["filepath"]).name
        print(f"   📄 {filepath}")
        print(f"      Total matches: {sample['total_matches']}")
        print(f"      Has temporal_core import: {sample['has_temporal_import']}")
        print(f"      Needs import addition: {not sample['has_temporal_import']}")
        print()
        
        # Show first 3 matches as examples
        for i, match in enumerate(sample["matches"][:3], start=1):
            print(f"      Example {i}:")
            print(f"         Line {match['line_num']}: {match['original']}")
            print(f"         →  {match['replacement']}")
            print(f"         Import needed: {match['needs_import']}")
            if match['note']:
                print(f"         Note: {match['note']}")
            print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files to migrate:       {total_files}")
    print(f"Total datetime calls:         {total_matches}")
    print(f"Sample size for testing:      {len(sample_files)} files")
    print(f"Files already migrated:       {sum(1 for a in analyses if a['has_temporal_import'])}")
    print(f"Files needing import:         {sum(1 for a in analyses if not a['has_temporal_import'])}")
    print()
    
    print("🎯 MIGRATION STRATEGY:")
    print("   1. Test sample files first (listed above)")
    print("   2. Add temporal_core imports to each file")
    print("   3. Apply regex replacements in order")
    print("   4. Run syntax checks with python -m py_compile")
    print("   5. Run import tests with python -c 'import module'")
    print("   6. If all pass, proceed with full migration")
    print()
    
    print("=" * 80)
    print("DRY RUN COMPLETE - NO FILES MODIFIED")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

