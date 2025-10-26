#!/usr/bin/env python3
import re
import json

# Read the full analysis file
with open('full_analysis.txt', 'r') as f:
    content = f.read()

print("🎯 ARCH E'S COMPLETE SEMICONDUCTOR SHORTAGE ANALYSIS")
print("=" * 60)

# Extract conceptual map
conceptual_match = re.search(r"'conceptual_map_json':\s*({.*?})", content, re.DOTALL)
if conceptual_match:
    conceptual_map = conceptual_match.group(1)
    print("\n📊 CONCEPTUAL MAP ANALYSIS:")
    print("-" * 40)
    try:
        # Clean up the string first
        clean_map = conceptual_map.replace("'", '"').replace('\\n', '\n')
        parsed = json.loads(clean_map)
        
        print("SPRs (Sparse Priming Representations):")
        for spr in parsed.get('sprs', []):
            print(f"  • {spr}")
        
        print("\nAbstract Workflow:")
        for i, step in enumerate(parsed.get('abstract_workflow', []), 1):
            print(f"  {i}. {step}")
            
        print("\nTerritory Assumptions:")
        for assumption in parsed.get('territory_assumptions', []):
            print(f"  • {assumption}")
    except Exception as e:
        print(f"Could not parse conceptual map: {e}")
        print("Raw conceptual map:")
        print(conceptual_map)

# Extract RISE blueprint
rise_match = re.search(r'"Scaffold Phase":\s*{.*?"Synthesis Phase":\s*{.*?}', content, re.DOTALL)
if rise_match:
    rise_content = rise_match.group(0)
    print("\n🚀 RISE METHODOLOGY BLUEPRINT:")
    print("-" * 40)
    # Clean up the formatting
    rise_content = rise_content.replace('\\n', '\n').replace('\\"', '"')
    print(rise_content)

# Extract critique section
critique_match = re.search(r"'critique_deepen_envision':\s*{.*?'response_text':\s*'```json\\n(.*?)\\n```'", content, re.DOTALL)
if critique_match:
    critique_content = critique_match.group(1).replace('\\n', '\n').replace('\\"', '"')
    print("\n🔍 CRITIQUE & ENVISIONING:")
    print("-" * 40)
    print(critique_content)

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
