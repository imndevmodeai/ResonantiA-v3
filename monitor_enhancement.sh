#!/bin/bash
# Quick progress monitor for SPR enhancement

echo "📊 SPR Enhancement Progress Monitor"
echo "===================================="
echo ""

# Check if process is running
if pgrep -f "enhance_sprs_russian_doll.py" > /dev/null; then
    echo "✅ Process is RUNNING"
    ps aux | grep "enhance_sprs_russian_doll" | grep python3 | grep -v grep | awk '{print "   PID:", $2, "CPU:", $3"%", "TIME:", $10, $11}'
else
    echo "❌ Process is NOT running"
fi

echo ""

# Check file modification
if [ -f "knowledge_graph/spr_definitions_tv.json" ]; then
    mtime=$(stat -c %Y knowledge_graph/spr_definitions_tv.json)
    now=$(date +%s)
    age=$(( (now - mtime) / 60 ))
    echo "📁 File last modified: $age minutes ago"
fi

echo ""

# Count progress
python3 << 'PYEOF'
import json
from pathlib import Path

spr_file = Path('knowledge_graph/spr_definitions_tv.json')
with open(spr_file, 'r') as f:
    sprs = json.load(f)

narrative_count = sum(1 for s in sprs 
    if any(stage.get('stage_name') == 'Narrative' 
           for stage in s.get('compression_stages', [])))

print(f"📊 Progress: {narrative_count}/{len(sprs)} SPRs ({100*narrative_count/len(sprs):.1f}%)")
print(f"   Remaining: {len(sprs) - narrative_count:,} SPRs")
PYEOF

echo ""
echo "📋 Recent log output:"
tail -5 enhancement_progress.log 2>/dev/null || echo "   (no log yet)"
