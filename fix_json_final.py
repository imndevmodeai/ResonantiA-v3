#!/usr/bin/env python3
"""Fix JSON by parsing and reformatting"""

import json
import re

# Read file
with open('knowledge_graph/spr_definitions_tv.json', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original file length: {len(content)} characters")

# Try to parse - if it fails, try to repair
try:
    data = json.loads(content)
    print(f"✅ JSON is already valid! Found {len(data)} SPR definitions.")
except json.JSONDecodeError as e:
    print(f"⚠️  JSON error: {e.msg} at line {e.lineno}, column {e.colno}")
    
    # Try to repair by fixing common issues
    print("Attempting repair...")
    
    # Remove any content after the last ]
    last_bracket = content.rfind(']')
    if last_bracket > 0:
        content = content[:last_bracket + 1].rstrip()
    
    # Remove trailing commas before ] or }
    content = re.sub(r',\s*\]', r']', content)
    content = re.sub(r',\s*}', r'}', content)
    
    try:
        data = json.loads(content)
        print(f"✅ Successfully repaired! Found {len(data)} SPR definitions.")
    except json.JSONDecodeError as e2:
        print(f"❌ Could not repair: {e2.msg} at line {e2.lineno}")
        
        # Last resort: try to parse incrementally to find the exact issue
        lines = content.split('\n')
        print(f"\nChecking structure around line {e2.lineno}:")
        start = max(0, e2.lineno - 5)
        end = min(len(lines), e2.lineno + 3)
        for i in range(start, end):
            marker = ">>>" if i == e2.lineno - 1 else "   "
            print(f"{marker} {i+1:5d}: {lines[i]}")
        
        raise

# Write back with proper formatting
with open('knowledge_graph/spr_definitions_tv.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ File successfully rewritten with proper formatting and indentation!")
