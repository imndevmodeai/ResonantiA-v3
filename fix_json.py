#!/usr/bin/env python3
"""Fix JSON syntax error in spr_definitions_tv.json"""

import json
import sys
from pathlib import Path

json_path = Path("knowledge_graph/spr_definitions_tv.json")

# Read the file
with open(json_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File length: {len(content)} characters")

# Try to parse
try:
    data = json.loads(content)
    print(f"✅ JSON is valid! Found {len(data)} SPR definitions.")
    sys.exit(0)
except json.JSONDecodeError as e:
    print(f"❌ JSON error: {e.msg}")
    print(f"   Position: {e.pos}, Line: {e.lineno}, Column: {e.colno}")
    
    # Show context
    lines = content.split('\n')
    if e.lineno <= len(lines):
        print(f"\nContext around error (line {e.lineno}):")
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        for i in range(start, end):
            marker = ">>>" if i == e.lineno - 1 else "   "
            print(f"{marker} {i+1:4d}: {lines[i]}")
    
    # Try repair: find last valid closing bracket
    last_bracket = content.rfind(']')
    if last_bracket < 0:
        print("❌ Could not find closing bracket")
        sys.exit(1)
    
    # Extract content up to last bracket
    test_content = content[:last_bracket+1].rstrip()
    
    # Remove trailing comma before closing bracket if present
    if test_content.rstrip().endswith(','):
        test_content = test_content.rstrip(',').rstrip() + ']'
    
    try:
        data = json.loads(test_content)
        print(f"\n✅ Successfully repaired JSON! Found {len(data)} SPR definitions.")
        
        # Write fixed version
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("✅ Fixed file written successfully!")
        sys.exit(0)
    except json.JSONDecodeError as e2:
        print(f"\n❌ Could not repair: {e2.msg} at line {e2.lineno}, column {e2.colno}")
        sys.exit(1)

