#!/bin/bash
# Rollback script for Four_PointO_ArchE
# Generated: 2025-09-05T07:22:03.957088

set -e

echo "SAFETY ROLLBACK: Restoring Four_PointO_ArchE from backup"
echo "Backup location: ./Four_PointO_ArchE_backup_20250905_072203"
echo "Target location: Four_PointO_ArchE"

# Verify backup exists
if [ ! -d "./Four_PointO_ArchE_backup_20250905_072203" ]; then
    echo "ERROR: Backup directory not found at ./Four_PointO_ArchE_backup_20250905_072203"
    exit 1
fi

# Create safety checkpoint before rollback
if [ -d "Four_PointO_ArchE" ]; then
    echo "Creating safety checkpoint..."
    cp -r "Four_PointO_ArchE" "Four_PointO_ArchE_pre_rollback_20250905_072203"
fi

# Perform rollback
echo "Performing rollback..."
rm -rf "Four_PointO_ArchE"
cp -r "./Four_PointO_ArchE_backup_20250905_072203" "Four_PointO_ArchE"

# Verify rollback
if [ -d "Four_PointO_ArchE" ]; then
    echo "SUCCESS: Rollback completed successfully"
    echo "Original ArchE capabilities restored"
else
    echo "ERROR: Rollback failed"
    exit 1
fi
