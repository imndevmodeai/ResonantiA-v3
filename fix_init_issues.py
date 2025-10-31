#!/usr/bin/env python3
"""
Quick fix script for ArchE initialization issues:
1. Fix JSON syntax error in spr_definitions_tv.json
2. Verify Autopoietic Learning Loop can initialize
"""

import json
import sys
from pathlib import Path

# Fix 1: JSON syntax error
print("=" * 60)
print("FIX 1: JSON Syntax Error in spr_definitions_tv.json")
print("=" * 60)

json_path = Path("knowledge_graph/spr_definitions_tv.json")
if not json_path.exists():
    print(f"❌ File not found: {json_path}")
    sys.exit(1)

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to parse
    try:
        data = json.loads(content)
        print(f"✅ JSON is already valid! Found {len(data)} SPR definitions.")
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON decode error: {e.msg} at line {e.lineno}, column {e.colno}")
        
        # Try to salvage - find last valid closing bracket
        last_bracket = content.rfind(']')
        if last_bracket > 0:
            # Take everything up to and including the last ]
            text = content[:last_bracket+1]
            try:
                data = json.loads(text)
                print(f"✅ JSON salvaged! Found {len(data)} SPR definitions.")
                
                # Rewrite with proper formatting
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print("✅ Fixed JSON file written successfully!")
            except json.JSONDecodeError as e2:
                print(f"❌ Could not salvage JSON: {e2}")
                sys.exit(1)
        else:
            print("❌ Could not find closing bracket")
            sys.exit(1)
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Fix 2: Test Autopoietic Learning Loop initialization
print("\n" + "=" * 60)
print("FIX 2: Test Autopoietic Learning Loop Initialization")
print("=" * 60)

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from Three_PointO_ArchE.autopoietic_learning_loop import AutopoieticLearningLoop
    
    print("✅ Successfully imported AutopoieticLearningLoop")
    
    # Try to initialize
    try:
        all_instance = AutopoieticLearningLoop()
        print("✅ AutopoieticLearningLoop initialized successfully!")
        print(f"   - Guardian review: {all_instance.guardian_review_enabled}")
        print(f"   - Auto-crystallization: {all_instance.auto_crystallization}")
        print(f"   - Metrics: {all_instance.metrics}")
    except Exception as e:
        print(f"❌ Error initializing AutopoieticLearningLoop: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL FIXES COMPLETE!")
print("=" * 60)

