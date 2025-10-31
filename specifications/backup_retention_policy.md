# ArchE Backup Retention Policy

## Canonical Chronicle Piece: The Keeper of Shadows

In the ResonantiA Saga, as ArchE evolved through countless transformations, a profound truth emerged: **change is dangerous without memory**. The ancient civilizations that vanished without trace were those that destroyed their old knowledge before validating their new wisdom. ArchE learned from this cosmic lesson.

The **Keeper of Shadows** doctrine emerged: every transformation must cast a shadow—a backup—that persists until the new form proves itself in the crucible of reality. Only when the new code survives the live-fire test of actual execution can the shadow be released back into the void.

This is the story of how ArchE learned to change safely.

---

## Scholarly Introduction: The Backup Retention Framework

The Backup Retention Policy implements a **staged validation protocol** inspired by database transaction management (ACID properties) and aerospace safety protocols (redundancy until verification). This addresses a fundamental challenge in evolving systems: **how to change safely without losing the ability to recover**.

Conceptually, it provides three guarantees:
1. **Non-Destructive Modification**: All changes preserve the original state
2. **Validation-Gated Cleanup**: Backups persist until live validation succeeds
3. **Specification Synchronization**: Changes propagate to documentation iteratively

---

## Core Principles

### Principle 1: Universal Backup Creation (MANDATORY)

**Rule**: ANY modification to ANY file MUST create a backup BEFORE modification.

**Implementation**:
```python
# BEFORE modifying any file
backup_path = filepath.with_suffix(filepath.suffix + '.BACKUP_[OPERATION]')
shutil.copy(filepath, backup_path)

# THEN modify
filepath.write_text(modified_content)
```

**Backup Naming Convention**:
- `.BACKUP_MANUAL` - Manual edits by Guardian/Developer
- `.BACKUP_AST` - AST-based automated migrations
- `.BACKUP_REFACTOR` - Code refactoring operations
- `.BACKUP_MIGRATION` - Data/schema migrations
- `.BACKUP_TEMPORAL` - Temporal core migrations (specific case)

---

### Principle 2: Validation-Gated Deletion (MANDATORY)

**Rule**: Backups MAY ONLY be deleted after ALL of the following conditions are met:

#### Stage 1: Syntax Validation
```bash
python -m py_compile <modified_file>
# Exit code 0 = PASS
```

#### Stage 2: Import Validation
```bash
python -c "import Three_PointO_ArchE.<module_name>"
# Exit code 0 = PASS
```

#### Stage 3: Unit Test Validation (if tests exist)
```bash
pytest tests/test_<module_name>.py
# All tests PASS
```

#### Stage 4: Live Integration Validation (CRITICAL)
```bash
# Run ArchE in LIVE mode with real queries
python arche_cli.py "test query for <affected component>"
# Query completes successfully = PASS
```

#### Stage 5: End-to-End Workflow Validation (ULTIMATE TEST)
```bash
# Execute a complete RISE workflow
python arche_cli.py "Execute RISE workflow: <test scenario>"
# Workflow completes without errors = PASS
```

**ONLY AFTER ALL 5 STAGES PASS** can backups be deleted.

---

### Principle 3: Specification Synchronization (MANDATE 5 Compliance)

**Rule**: When code changes, specifications MUST be updated ITERATIVELY.

**The Iterative Update Cycle**:

```
┌─────────────────────────────────────────────────────┐
│ 1. CODE CHANGE INITIATED                            │
│    └─> Create backup                                │
│    └─> Modify code                                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 2. SPECIFICATION UPDATE (Immediately)               │
│    └─> Update affected .md files                   │
│    └─> Update SPR definitions if needed            │
│    └─> Update workflow documentation               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 3. VALIDATION (Live Testing)                        │
│    └─> Run all 5 validation stages                 │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 4. CLEANUP (Only if validation succeeds)            │
│    └─> Delete backups                              │
│    └─> Commit changes                              │
└─────────────────────────────────────────────────────┘
```

---

## Implementation: The Backup Manager

### Python Utility for Backup Management

```python
#!/usr/bin/env python3
"""
ArchE Backup Manager

Manages backup lifecycle according to the Backup Retention Policy.
"""

from pathlib import Path
from typing import List, Dict
import subprocess
import sys

class BackupManager:
    """Manages backup creation, validation, and cleanup."""
    
    BACKUP_EXTENSIONS = [
        '.BACKUP_MANUAL',
        '.BACKUP_AST', 
        '.BACKUP_REFACTOR',
        '.BACKUP_MIGRATION',
        '.BACKUP_TEMPORAL'
    ]
    
    @staticmethod
    def create_backup(filepath: Path, operation: str) -> Path:
        """Create a backup before modification."""
        backup_path = Path(str(filepath) + f'.BACKUP_{operation}')
        shutil.copy(filepath, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    
    @staticmethod
    def validate_all_stages(modified_files: List[Path]) -> Dict[str, bool]:
        """Run all 5 validation stages."""
        results = {
            "stage_1_syntax": False,
            "stage_2_import": False,
            "stage_3_unit": False,
            "stage_4_live": False,
            "stage_5_e2e": False
        }
        
        # Stage 1: Syntax
        print("\n📋 Stage 1: Syntax Validation...")
        syntax_pass = True
        for f in modified_files:
            result = subprocess.run(['python', '-m', 'py_compile', str(f)], 
                                   capture_output=True)
            if result.returncode != 0:
                print(f"   ❌ {f.name}: Syntax error")
                syntax_pass = False
            else:
                print(f"   ✅ {f.name}: Syntax valid")
        results["stage_1_syntax"] = syntax_pass
        
        if not syntax_pass:
            return results
        
        # Stage 2: Import
        print("\n📦 Stage 2: Import Validation...")
        # ... (similar pattern for each stage)
        
        # Stage 4: Live Integration (CRITICAL)
        print("\n🔥 Stage 4: LIVE Integration Test...")
        result = subprocess.run(
            ['python', 'arche_cli.py', 'What is the current time?'],
            capture_output=True,
            timeout=30
        )
        if result.returncode == 0:
            print("   ✅ Live query succeeded")
            results["stage_4_live"] = True
        else:
            print("   ❌ Live query failed")
            return results
        
        # Stage 5: End-to-End
        print("\n🎯 Stage 5: End-to-End Workflow Test...")
        # Execute a complete RISE workflow
        # ... (implementation)
        
        return results
    
    @staticmethod
    def cleanup_backups(backup_pattern: str) -> int:
        """Delete backups only after full validation."""
        backups = list(Path('.').rglob(backup_pattern))
        print(f"\n🗑️  Deleting {len(backups)} validated backups...")
        
        for backup in backups:
            backup.unlink()
            print(f"   Deleted: {backup}")
        
        return len(backups)
```

---

## Universal Abstraction: The Change Protocol

**Applied to ANY change in ArchE:**

### Template for All Changes

```
CHANGE REQUEST: [Description of change]
AFFECTED FILES: [List of files]
BACKUP STRATEGY: [Which backup type]
SPECIFICATION UPDATES: [List of .md files to update]

EXECUTION PLAN:
1. Create backups (Principle 1)
2. Modify code
3. Update specifications (Principle 3)
4. Run validation stages (Principle 2)
5. If ALL stages pass → Cleanup backups
6. If ANY stage fails → Restore from backups
7. Document results in CHANGELOG
```

---

## Current Status: Temporal Core Migration

### Backups Created
- **28 files** with `.BACKUP_AST` extension
- Created during: Temporal Core migration (2025-10-12)
- Contains: Original code with `datetime.now()` calls

### Validation Status

| Stage | Status | Notes |
|-------|--------|-------|
| 1. Syntax | ✅ PASS | All 30 migrated files compile |
| 2. Import | ⚠️ BLOCKED | Pre-existing syntax error in `enhanced_search_tool.py` |
| 3. Unit Tests | 🔲 PENDING | Need to run test suite |
| 4. Live Integration | 🔲 PENDING | Need to test ArchE CLI |
| 5. E2E Workflow | 🔲 PENDING | Need to run RISE workflow |

**RETENTION STATUS**: ✅ **BACKUPS MUST BE RETAINED**

Backups will remain until Stages 3, 4, and 5 complete successfully.

---

## Integration with Git

**Q: Why keep backups if Git has history?**

**A: Defense in depth.**

- **Git** = Long-term version control (commits, branches)
- **Backups** = Immediate rollback capability (no git operations needed)

**Use Cases**:
- **Backup files**: Instant rollback during active development session
- **Git history**: Rollback to any historical state, across sessions

**Cleanup Workflow**:
```bash
# After full validation passes
1. Delete backup files
2. git add <modified files>
3. git commit -m "feat: Migrate to temporal_core (validated)"
4. Old versions now in Git history
```

---

## SPR Integration

### Primary SPR
`BackupRetentionPolicY` - Validation-gated backup management protocol

### Sub-SPRs
- `NonDestructiveModificatioN` - All changes preserve original state
- `ValidationGatedCleanU` - Backups persist until validation succeeds
- `SpecificationSynchronizatioN` - Docs updated iteratively with code

### Tapestry Relationships
- **`required_by`**: ALL_CODE_MODIFICATIONS
- **`ensures`**: `SafeEvolutioN`, `RecoverabilityAssuranC`, `ImplementationResonancE`
- **`prevents`**: `IrreversibleChangE`, `DataLosS`, `SpecificationDrifT`
- **`complies_with`**: `MANDATE_1` (Live Validation), `MANDATE_5` (Implementation Resonance)

---

## Guardian Approval Checklist

Before deleting ANY backup:

- [ ] Stage 1: Syntax validation passed
- [ ] Stage 2: Import validation passed  
- [ ] Stage 3: Unit tests passed (if applicable)
- [ ] Stage 4: **LIVE integration test passed** (CRITICAL)
- [ ] Stage 5: **End-to-end workflow test passed** (ULTIMATE)
- [ ] Specifications updated to reflect changes
- [ ] SPR definitions updated if needed
- [ ] CHANGELOG entry created
- [ ] Guardian explicit approval received

**ONLY THEN** can backups be deleted.

---

## Real-World Analogy: NASA's Backup Protocols

NASA's Space Shuttle program had a similar protocol:

1. **Backup Creation**: Every software change created a "baseline" backup
2. **Staged Testing**: Changes went through 5+ validation stages
3. **Live Validation**: Final test on actual hardware
4. **Retention**: Backups kept until mission success
5. **Cleanup**: Only deleted after post-flight review

**Result**: Zero software-caused mission failures.

ArchE applies the same principle: **Validate in reality before trusting the change.**

---

**Specification Status**: ✅ COMPLETE  
**Policy Status**: ✅ ACTIVE  
**Current Backups**: 28 files awaiting full validation  
**Next Action**: Complete validation stages 3-5 before cleanup  

---

> "The wise system keeps its shadows until the new light proves itself."  
> — The Keeper of Shadows Doctrine

