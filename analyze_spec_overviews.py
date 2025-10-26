#!/usr/bin/env python3
"""
Script to check all specifications for overview sections and identify missing ones.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any

def check_spec_overview(spec_file: Path) -> Dict[str, Any]:
    """Check if a specification has a proper overview section."""
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for overview patterns
        overview_patterns = [
            r'##\s*Overview',
            r'##\s*Part I:.*Overview',
            r'##\s*Philosophical Mandate',
            r'##\s*Canonical Chronicle Piece',
            r'##\s*Scholarly Introduction',
            r'##\s*Introduction',
            r'##\s*Summary'
        ]
        
        has_overview = any(re.search(pattern, content, re.IGNORECASE) for pattern in overview_patterns)
        
        # Check for content after overview
        overview_content = ""
        if has_overview:
            # Try to extract overview content
            for pattern in overview_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    # Get content after the overview heading
                    start_pos = match.end()
                    # Find next heading
                    next_heading = re.search(r'^##', content[start_pos:], re.MULTILINE)
                    if next_heading:
                        overview_content = content[start_pos:start_pos + next_heading.start()].strip()
                    else:
                        overview_content = content[start_pos:].strip()
                    break
        
        return {
            "file": spec_file.name,
            "has_overview": has_overview,
            "overview_content_length": len(overview_content),
            "overview_content_preview": overview_content[:200] + "..." if len(overview_content) > 200 else overview_content,
            "needs_overview": not has_overview or len(overview_content.strip()) < 100
        }
        
    except Exception as e:
        return {
            "file": spec_file.name,
            "has_overview": False,
            "overview_content_length": 0,
            "overview_content_preview": f"Error reading file: {e}",
            "needs_overview": True
        }

def main():
    """Main function to check all specifications."""
    specs_dir = Path("specifications")
    spec_files = list(specs_dir.glob("*.md"))
    
    print("🔍 CHECKING SPECIFICATION OVERVIEWS")
    print("=" * 60)
    print()
    
    results = []
    missing_overviews = []
    
    for spec_file in spec_files:
        result = check_spec_overview(spec_file)
        results.append(result)
        
        if result["needs_overview"]:
            missing_overviews.append(result)
            print(f"❌ {result['file']}: Missing or insufficient overview")
        else:
            print(f"✅ {result['file']}: Has overview ({result['overview_content_length']} chars)")
    
    print(f"\n📊 SUMMARY:")
    print(f"   • {len(spec_files)} specifications checked")
    print(f"   • {len(spec_files) - len(missing_overviews)} have proper overviews")
    print(f"   • {len(missing_overviews)} need overview sections")
    
    if missing_overviews:
        print(f"\n🚨 SPECIFICATIONS NEEDING OVERVIEWS:")
        for spec in missing_overviews:
            print(f"   • {spec['file']}")
    
    return results, missing_overviews

if __name__ == "__main__":
    main()

