#!/bin/bash
# Pull Zepto branch updates for modified files
# This will backup your local changes first

set -e

BRANCH="origin/cursor/abstract-zepto-spr-process-in-dev-mode-3123"
FILES=(
    "Three_PointO_ArchE/action_registry.py"
    "Three_PointO_ArchE/spr_manager.py"
)

echo "=========================================="
echo "Pulling Zepto Updates for Modified Files"
echo "=========================================="
echo ""

# Backup local changes
echo "Step 1: Creating backup of local changes..."
BACKUP_DIR=".zepto_pull_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        backup_path="$BACKUP_DIR/$(dirname "$file")"
        mkdir -p "$backup_path"
        cp "$file" "$BACKUP_DIR/$file"
        echo "  ✓ Backed up: $file"
    fi
done

echo ""
echo "Step 2: Pulling updates from remote branch..."
for file in "${FILES[@]}"; do
    if git checkout "$BRANCH" -- "$file" 2>/dev/null; then
        echo "  ✓ Updated: $file"
    else
        echo "  ✗ Failed: $file"
    fi
done

echo ""
echo "=========================================="
echo "Update Complete"
echo "=========================================="
echo ""
echo "Your local changes are backed up in: $BACKUP_DIR"
echo ""
echo "Review the changes:"
echo "  git diff $BACKUP_DIR/Three_PointO_ArchE/action_registry.py Three_PointO_ArchE/action_registry.py"
echo "  git diff $BACKUP_DIR/Three_PointO_ArchE/spr_manager.py Three_PointO_ArchE/spr_manager.py"
echo ""
echo "If you want to restore your local changes:"
echo "  cp $BACKUP_DIR/Three_PointO_ArchE/action_registry.py Three_PointO_ArchE/action_registry.py"
echo "  cp $BACKUP_DIR/Three_PointO_ArchE/spr_manager.py Three_PointO_ArchE/spr_manager.py"

