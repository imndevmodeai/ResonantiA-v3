#!/usr/bin/env python3
"""
Create Mobile Sync Package for ArchE
=====================================

Quick script to generate everything needed for mobile ArchE access.
Run this before leaving for work to sync to your phone.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def create_mobile_sync_package():
    """Create complete mobile sync package."""
    print("=" * 60)
    print("ARCHE MOBILE SYNC PACKAGE CREATOR")
    print("=" * 60)
    print()
    
    workspace = Path.cwd()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Output directory
    sync_dir = workspace / "mobile_sync_packages"
    sync_dir.mkdir(exist_ok=True)
    
    package_dir = sync_dir / f"sync_{timestamp}"
    package_dir.mkdir(exist_ok=True)
    
    print(f"📁 Creating package in: {package_dir}")
    print()
    
    # 1. Copy Protocol Document
    print("1️⃣  Copying protocol document...")
    protocol_src = workspace / "PRIME_ARCHE_PROTOCOL_v2_AUTO.md"
    if protocol_src.exists():
        shutil.copy(protocol_src, package_dir / "PRIME_ARCHE_PROTOCOL_v2_AUTO.md")
        print("   ✅ Protocol document copied")
    else:
        print("   ⚠️  Protocol document not found")
    
    # 2. Copy Quick Reference
    print("2️⃣  Copying quick reference...")
    quick_ref_src = workspace / "ARCHE_TERMINOLOGY_QUICK_REFERENCE.md"
    if quick_ref_src.exists():
        shutil.copy(quick_ref_src, package_dir / "ARCHE_MOBILE_QUICK_REFERENCE.md")
        print("   ✅ Quick reference copied")
    else:
        print("   ⚠️  Quick reference not found")
    
    # 3. Create Knowledge Snapshot
    print("3️⃣  Creating knowledge snapshot...")
    snapshot = {
        "created_at": datetime.now().isoformat(),
        "package_type": "arche_mobile_sync",
        "source": "cursor_desktop",
        "version": "1.0"
    }
    
    # Load SPRs
    spr_file = workspace / "knowledge_graph" / "spr_definitions_tv.json"
    if spr_file.exists():
        try:
            with open(spr_file, 'r') as f:
                sprs = json.load(f)
            
            # Get top 20 most important SPRs
            if isinstance(sprs, list):
                snapshot["sprs"] = {
                    "total_count": len(sprs),
                    "included_count": min(20, len(sprs)),
                    "definitions": sprs[:20]
                }
            else:
                spr_defs = sprs.get("spr_definitions", [])
                snapshot["sprs"] = {
                    "total_count": len(spr_defs),
                    "included_count": min(20, len(spr_defs)),
                    "definitions": spr_defs[:20]
                }
            print(f"   ✅ {snapshot['sprs']['total_count']} SPRs found, {snapshot['sprs']['included_count']} included")
        except Exception as e:
            print(f"   ⚠️  Error loading SPRs: {e}")
            snapshot["sprs"] = {"error": str(e)}
    
    # Find recent sessions
    print("4️⃣  Finding recent sessions...")
    recent_sessions = sorted(
        workspace.glob("cursor_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:3]
    
    snapshot["recent_sessions"] = [
        {
            "filename": s.name,
            "size_kb": round(s.stat().st_size / 1024, 1),
            "modified": datetime.fromtimestamp(s.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        }
        for s in recent_sessions
    ]
    print(f"   ✅ {len(snapshot['recent_sessions'])} recent sessions found")
    
    # Save snapshot
    snapshot_file = package_dir / f"knowledge_snapshot_{timestamp}.json"
    with open(snapshot_file, 'w') as f:
        json.dump(snapshot, f, indent=2)
    print(f"   ✅ Snapshot saved: {snapshot_file.name}")
    
    # 4. Create Mobile Quick Start Guide
    print("5️⃣  Creating mobile quick start guide...")
    quick_start = f"""# ArchE Mobile Quick Start
**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Upload These Files to AI Studio

1. PRIME_ARCHE_PROTOCOL_v2_AUTO.md (ESSENTIAL)
2. knowledge_snapshot_{timestamp}.json (Optional - for full context)

## Start Command

```
Keyy=('IMnDEVmode')
Prime yourself for mobile session.
Load context from knowledge snapshot.
```

## Today's System Status

- SPRs Loaded: {snapshot.get('sprs', {}).get('total_count', 'Unknown')}
- Recent Sessions: {len(snapshot['recent_sessions'])}
- Last Session: {snapshot['recent_sessions'][0]['filename'] if snapshot['recent_sessions'] else 'None'}

## Quick Commands

**Analyze Problem**:
```
Strategic analysis: [problem description]
Apply 4D thinking and CFP concepts.
```

**Capture Insight**:
```
New insight:
- Concept: [name]
- Details: [description]
- For Guardian review on desktop
```

**End Session**:
```
Export session summary for desktop import.
Include: insights, decisions, action items.
```

## Remember

- Mobile = Strategic thinking
- Desktop = Implementation
- Export at end of day for sync

---
Package created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    quick_start_file = package_dir / "QUICK_START.md"
    quick_start_file.write_text(quick_start)
    print(f"   ✅ Quick start guide created")
    
    # 5. Create README
    print("6️⃣  Creating README...")
    readme = f"""# ArchE Mobile Sync Package
**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Contents

1. **PRIME_ARCHE_PROTOCOL_v2_AUTO.md** - Full protocol (UPLOAD THIS FIRST)
2. **knowledge_snapshot_{timestamp}.json** - Current system state
3. **ARCHE_MOBILE_QUICK_REFERENCE.md** - Commands and SPR list
4. **QUICK_START.md** - How to use on phone
5. **README.md** - This file

## Quick Setup

### On Phone (AI Studio):

1. Upload `PRIME_ARCHE_PROTOCOL_v2_AUTO.md`
2. Type: `Keyy=('IMnDEVmode') Prime yourself`
3. Optional: Upload `knowledge_snapshot_{timestamp}.json`
4. Start working!

### At End of Day:

1. Copy your conversation from AI Studio
2. Save as text file
3. Upload to Google Drive
4. Import to desktop ArchE tonight

## Support

See `QUICK_START.md` for detailed instructions.
See `HOW_TO_USE_ARCHE_ON_MOBILE.md` on desktop for full workflow.

---
Generated by create_mobile_sync.py
"""
    
    readme_file = package_dir / "README.md"
    readme_file.write_text(readme)
    print(f"   ✅ README created")
    
    # Summary
    print()
    print("=" * 60)
    print("✨ PACKAGE COMPLETE!")
    print("=" * 60)
    print()
    print(f"📁 Location: {package_dir}")
    print()
    print("📂 Files created:")
    for f in sorted(package_dir.iterdir()):
        size_kb = f.stat().st_size / 1024
        print(f"   - {f.name} ({size_kb:.1f} KB)")
    print()
    print("=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print()
    print("1. Upload this folder to Google Drive:")
    print(f"   {package_dir}")
    print()
    print("2. On your phone, download from Drive")
    print()
    print("3. In AI Studio, upload:")
    print("   - PRIME_ARCHE_PROTOCOL_v2_AUTO.md (MUST)")
    print(f"   - knowledge_snapshot_{timestamp}.json (OPTIONAL)")
    print()
    print("4. Start with:")
    print("   Keyy=('IMnDEVmode') Prime yourself")
    print()
    print("=" * 60)
    print("🚀 MOBILE ARCHE ENABLED!")
    print("=" * 60)
    
    return package_dir

if __name__ == "__main__":
    try:
        package_dir = create_mobile_sync_package()
        print(f"\n✅ Success! Package ready at: {package_dir}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


