#!/bin/bash
# Safe cleanup script to free space on root partition
# Only deletes files that won't affect system functionality

echo "=========================================="
echo "ROOT PARTITION CLEANUP SCRIPT"
echo "=========================================="
echo ""

# Track total space freed
TOTAL_FREED=0

# 1. Clean APT package cache (safe - can be re-downloaded)
echo "[1] Cleaning APT package cache..."
if [ -d /var/cache/apt/archives ]; then
    SIZE_BEFORE=$(du -sh /var/cache/apt/archives 2>/dev/null | cut -f1)
    sudo apt-get clean
    SIZE_AFTER=$(du -sh /var/cache/apt/archives 2>/dev/null | cut -f1)
    echo "   Before: $SIZE_BEFORE, After: $SIZE_AFTER"
fi

# 2. Clean old journal logs (keeps last 3 days)
echo "[2] Cleaning old journal logs (keeping last 3 days)..."
SIZE_BEFORE=$(journalctl --disk-usage 2>/dev/null | grep -oP '\d+\.\d+G|\d+M')
sudo journalctl --vacuum-time=3d
SIZE_AFTER=$(journalctl --disk-usage 2>/dev/null | grep -oP '\d+\.\d+G|\d+M')
echo "   Before: $SIZE_BEFORE, After: $SIZE_AFTER"

# 3. Clean temporary files
echo "[3] Cleaning /tmp and /var/tmp..."
sudo find /tmp -type f -atime +7 -delete 2>/dev/null
sudo find /var/tmp -type f -atime +7 -delete 2>/dev/null
echo "   Cleaned files older than 7 days"

# 4. Clean pip cache
echo "[4] Cleaning pip cache..."
if [ -d ~/.cache/pip ]; then
    SIZE_BEFORE=$(du -sh ~/.cache/pip 2>/dev/null | cut -f1)
    pip cache purge 2>/dev/null || rm -rf ~/.cache/pip/* 2>/dev/null
    SIZE_AFTER=$(du -sh ~/.cache/pip 2>/dev/null | cut -f1)
    echo "   Before: $SIZE_BEFORE, After: $SIZE_AFTER"
fi

# 5. Clean trash
echo "[5] Cleaning trash..."
if [ -d ~/.local/share/Trash ]; then
    SIZE_BEFORE=$(du -sh ~/.local/share/Trash 2>/dev/null | cut -f1)
    rm -rf ~/.local/share/Trash/* 2>/dev/null
    SIZE_AFTER=$(du -sh ~/.local/share/Trash 2>/dev/null | cut -f1)
    echo "   Before: $SIZE_BEFORE, After: $SIZE_AFTER"
fi

# 6. Clean old snapshots (if using btrfs)
echo "[6] Checking for old snapshots..."
if command -v snapper &> /dev/null; then
    sudo snapper list | grep -v "current\|active" | awk '{print $1}' | xargs -r sudo snapper delete 2>/dev/null
    echo "   Cleaned old snapshots"
fi

# 7. Clean old kernels (keeps current + 1 previous)
echo "[7] Checking for old kernels..."
OLD_KERNELS=$(dpkg -l | grep -E 'linux-image-[0-9]' | grep -v $(uname -r) | awk '{print $2}' | head -n -1)
if [ ! -z "$OLD_KERNELS" ]; then
    echo "   Found old kernels to remove:"
    echo "$OLD_KERNELS" | while read kernel; do
        echo "     - $kernel"
    done
    echo "   Run manually: sudo apt-get purge $OLD_KERNELS"
else
    echo "   No old kernels to remove"
fi

# 8. Clean browser caches
echo "[8] Cleaning browser caches..."
for browser in firefox chromium chrome; do
    if [ -d ~/.cache/$browser ]; then
        SIZE_BEFORE=$(du -sh ~/.cache/$browser 2>/dev/null | cut -f1)
        rm -rf ~/.cache/$browser/* 2>/dev/null
        SIZE_AFTER=$(du -sh ~/.cache/$browser 2>/dev/null | cut -f1)
        echo "   $browser: $SIZE_BEFORE → $SIZE_AFTER"
    fi
done

# 9. Clean npm cache (if exists)
echo "[9] Cleaning npm cache..."
if command -v npm &> /dev/null; then
    npm cache clean --force 2>/dev/null
    echo "   npm cache cleaned"
fi

# 10. Clean Docker (if exists)
echo "[10] Cleaning Docker..."
if command -v docker &> /dev/null; then
    docker system prune -af --volumes 2>/dev/null
    echo "   Docker cleaned"
fi

echo ""
echo "=========================================="
echo "CLEANUP COMPLETE"
echo "=========================================="
echo ""
echo "Current disk usage:"
df -h / | tail -1






