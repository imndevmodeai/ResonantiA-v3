# VCD Backup & Recovery - Complete How-To Guide

**Component**: Visual Cognitive Debugger Backup and Recovery System  
**Version**: 1.0  
**Created**: 2025-11-19  
**Last Updated**: 2025-11-19 06:27:10 EST  
**File**: `Three_PointO_ArchE/vcd_backup_recovery.py`

## Overview

The VCD Backup and Recovery System provides automated backup creation, point-in-time recovery, and disaster recovery capabilities for the Visual Cognitive Debugger system. It protects configuration files, SPR definitions, analysis results, and system logs.

## Prerequisites

- Python 3.8+
- Write access to backup directory
- Sufficient disk space for backups
- Optional: Encryption key for secure backups

## Installation

### Step 1: Create Backup Directory

```bash
mkdir -p backups/vcd
chmod 755 backups/vcd
```

### Step 2: Verify Installation

```python
python3 -c "from Three_PointO_ArchE.vcd_backup_recovery import VCDBackupSystem; print('✅ Backup System available')"
```

## Basic Usage

### Creating a Backup

```python
from Three_PointO_ArchE.vcd_backup_recovery import VCDBackupSystem

# Initialize backup system
backup_system = VCDBackupSystem()

# Create incremental backup
backup_metadata = backup_system.create_backup(
    backup_type="incremental",
    scope=["critical", "important"],
    compression=True
)

print(f"Backup ID: {backup_metadata.backup_id}")
print(f"Status: {backup_metadata.status}")
print(f"Size: {backup_metadata.size_bytes / 1024 / 1024:.2f} MB")
print(f"Compression: {backup_metadata.compression_ratio:.2f}:1")
```

### Creating a Full Backup

```python
# Create full backup
backup_metadata = backup_system.create_backup(
    backup_type="full",
    scope=["critical", "important", "optional"],
    compression=True
)
```

### Verifying a Backup

```python
# Verify backup integrity
is_valid, message = backup_system.verify_backup(backup_metadata.backup_id)

if is_valid:
    print(f"✅ Backup verified: {message}")
else:
    print(f"❌ Backup verification failed: {message}")
```

## Advanced Usage

### Restoring from Backup

```python
from Three_PointO_ArchE.vcd_backup_recovery import VCDRecoverySystem

# Initialize recovery system
recovery_system = VCDRecoverySystem()

# Restore entire system
recovery_metadata = recovery_system.restore_system(
    backup_id="vcd_backup_1234567890",
    scope=["critical", "important"]
)

print(f"Recovery ID: {recovery_metadata.recovery_id}")
print(f"Status: {recovery_metadata.status}")
print(f"Files Restored: {len(recovery_metadata.restored_files)}")
print(f"Failed Files: {len(recovery_metadata.failed_files)}")
```

### Restoring Specific Data

```python
# Restore only configuration
recovery_metadata = recovery_system.restore_data(
    data_type="vcd_config",
    backup_id="vcd_backup_1234567890"
)

# Restore only SPR definitions
recovery_metadata = recovery_system.restore_data(
    data_type="spr_definitions",
    backup_id="vcd_backup_1234567890"
)
```

### Automated Backup Scheduling

```python
import schedule
import time

def run_backup():
    backup_system = VCDBackupSystem()
    backup_metadata = backup_system.create_backup(
        backup_type="incremental",
        scope=["critical", "important"]
    )
    print(f"Backup completed: {backup_metadata.backup_id}")

# Schedule daily backup at 2 AM
schedule.every().day.at("02:00").do(run_backup)

# Schedule weekly full backup on Sunday
schedule.every().sunday.at("01:00").do(
    lambda: backup_system.create_backup(backup_type="full")
)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Cleanup Old Backups

```python
# Clean up backups according to retention policy
backup_system.cleanup_old_backups()

# Custom retention policy
custom_policy = {
    "incremental": 14,  # Keep 14 days
    "full": 30,         # Keep 30 days
    "monthly": 365      # Keep 1 year
}
backup_system.cleanup_old_backups(retention_policy=custom_policy)
```

## API Reference

### VCDBackupSystem Class

#### `__init__(backup_root=None, encryption_key=None)`
Initialize backup system.

**Parameters:**
- `backup_root`: Root directory for backups (default: `backups/vcd/`)
- `encryption_key`: Optional encryption key

#### `create_backup(backup_type="incremental", scope=None, compression=True) -> BackupMetadata`
Create a backup.

**Parameters:**
- `backup_type`: "full", "incremental", or "monthly"
- `scope`: List of data categories (default: all)
- `compression`: Enable compression (default: True)

**Returns**: `BackupMetadata` object

#### `verify_backup(backup_id) -> Tuple[bool, str]`
Verify backup integrity.

#### `cleanup_old_backups(retention_policy=None)`
Clean up old backups according to retention policy.

### VCDRecoverySystem Class

#### `__init__(backup_root=None)`
Initialize recovery system.

#### `restore_system(backup_id, target_time=None, scope=None) -> RecoveryMetadata`
Restore entire system from backup.

#### `restore_data(data_type, backup_id) -> RecoveryMetadata`
Restore specific data type from backup.

#### `verify_recovery(recovery_id) -> Tuple[bool, str]`
Verify recovery was successful.

## Configuration

### Backup Schedule

The system supports automatic scheduling:

```python
# Daily incremental backup
backup_system.schedule_config["daily"] = {
    "time": "02:00",
    "type": "incremental",
    "retention_days": 30,
    "scope": ["critical", "important"]
}

# Weekly full backup
backup_system.schedule_config["weekly"] = {
    "time": "01:00",
    "day": "sunday",
    "type": "full",
    "retention_days": 84,
    "scope": ["critical", "important", "optional"]
}

# Monthly full backup
backup_system.schedule_config["monthly"] = {
    "time": "00:00",
    "day": "first_sunday",
    "type": "full",
    "compression": True,
    "retention_days": 365,
    "scope": ["critical", "important", "optional"]
}
```

### Data Categories

```python
# Critical data (always backed up)
backup_system.data_categories["critical"] = {
    "vcd_config": ["vcd_config.yaml", "config/vcd_*.yaml"],
    "spr_definitions": ["knowledge_graph/spr_definitions_tv.json"],
    "analysis_results": ["logs/vcd_analysis_*.json"],
    "system_logs": ["logs/vcd_*.log"]
}

# Important data
backup_system.data_categories["important"] = {
    "session_data": ["logs/session_*.json"],
    "performance_metrics": ["logs/performance_*.json"],
    "alert_history": ["logs/iar_anomaly_alerts.jsonl"]
}

# Optional data
backup_system.data_categories["optional"] = {
    "temporary_files": ["tmp/vcd_*"],
    "debug_logs": ["logs/debug_*.log"]
}
```

## Troubleshooting

### Backup Creation Fails

**Problem**: `create_backup()` returns status "failed"

**Solutions**:
1. Check disk space: `df -h backups/`
2. Verify file permissions: `ls -la backups/vcd/`
3. Check for locked files
4. Review error message in `backup_metadata.error_message`

### Backup Verification Fails

**Problem**: `verify_backup()` returns False

**Solutions**:
1. Check backup file exists: `ls backups/vcd/vcd_backup_*.tar.gz`
2. Verify file integrity: `tar -tzf backup_file.tar.gz`
3. Check for corruption
4. Recreate backup if necessary

### Restoration Fails

**Problem**: Files not restored correctly

**Solutions**:
1. Verify backup exists and is valid
2. Check target directory permissions
3. Review `recovery_metadata.failed_files` list
4. Check disk space in target location
5. Verify file paths are correct

### High Backup Size

**Problem**: Backups are very large

**Solutions**:
1. Enable compression: `compression=True`
2. Exclude optional data from scope
3. Clean up old files before backup
4. Use incremental backups more frequently

## Best Practices

1. **Backup Frequency**
   - Daily incremental backups
   - Weekly full backups
   - Monthly archival backups

2. **Retention Policy**
   - Keep 30 days of daily backups
   - Keep 12 weeks of weekly backups
   - Keep 12 months of monthly backups

3. **Verification**
   - Verify all backups after creation
   - Test restoration periodically
   - Monitor backup success rates

4. **Security**
   - Encrypt sensitive backups
   - Store backups off-site
   - Limit access to backup files

## Examples

### Example 1: Automated Daily Backup

```python
from Three_PointO_ArchE.vcd_backup_recovery import VCDBackupSystem
import schedule
import time

backup_system = VCDBackupSystem()

def daily_backup():
    metadata = backup_system.create_backup(
        backup_type="incremental",
        scope=["critical", "important"],
        compression=True
    )
    
    # Verify backup
    is_valid, message = backup_system.verify_backup(metadata.backup_id)
    
    if is_valid:
        print(f"✅ Daily backup successful: {metadata.backup_id}")
    else:
        print(f"❌ Backup verification failed: {message}")

# Schedule daily at 2 AM
schedule.every().day.at("02:00").do(daily_backup)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Example 2: Disaster Recovery Procedure

```python
from Three_PointO_ArchE.vcd_backup_recovery import VCDRecoverySystem

def disaster_recovery(backup_id):
    recovery_system = VCDRecoverySystem()
    
    # Verify backup exists
    is_valid, message = recovery_system.backup_system.verify_backup(backup_id)
    if not is_valid:
        print(f"❌ Backup invalid: {message}")
        return False
    
    # Restore system
    recovery_metadata = recovery_system.restore_system(
        backup_id=backup_id,
        scope=["critical", "important", "optional"]
    )
    
    if recovery_metadata.status == "success":
        print(f"✅ Recovery successful: {recovery_metadata.recovery_id}")
        print(f"   Restored {len(recovery_metadata.restored_files)} files")
        return True
    else:
        print(f"❌ Recovery failed: {recovery_metadata.error_message}")
        return False

# Execute recovery
disaster_recovery("vcd_backup_1234567890")
```

### Example 3: Backup Health Check

```python
from Three_PointO_ArchE.vcd_backup_recovery import VCDBackupSystem
from pathlib import Path
import json

def backup_health_check():
    backup_system = VCDBackupSystem()
    
    # Check backup index
    index_path = backup_system.backup_root / "backup_index.json"
    if not index_path.exists():
        print("⚠️ No backup index found")
        return False
    
    with open(index_path, 'r') as f:
        index = json.load(f)
    
    backups = index.get("backups", [])
    print(f"Total backups: {len(backups)}")
    
    # Check recent backups
    recent_backups = [b for b in backups if b["status"] == "success"][-5:]
    print(f"Recent successful backups: {len(recent_backups)}")
    
    # Verify most recent
    if recent_backups:
        latest = recent_backups[-1]
        is_valid, message = backup_system.verify_backup(latest["backup_id"])
        print(f"Latest backup valid: {is_valid}")
    
    return True

backup_health_check()
```

## Related Components

- **VCD Configuration Management**: Backs up configuration files
- **VCD Health Dashboard**: Monitors backup system health
- **VCD Testing Suite**: Tests backup and recovery procedures

## Support

For issues or questions:
1. Check backup logs: `logs/vcd_backup_*.log`
2. Review backup index: `backups/vcd/backup_index.json`
3. Verify disk space: `df -h`
4. Test restoration in test environment first

---

**Previous Guide**: [VCD Health Dashboard Guide](03_VCD_Health_Dashboard_Guide.md)  
**Next Guide**: [VCD Configuration Management Guide](05_VCD_Configuration_Management_Guide.md)

