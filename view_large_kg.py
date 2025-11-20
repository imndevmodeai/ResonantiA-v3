#!/usr/bin/env python3
"""
Utility script to view and navigate the large spr_definitions_tv.json file (172MB+)
Provides interactive browsing, searching, and layer-specific viewing.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

KG_PATH = Path("knowledge_graph/spr_definitions_tv.json")

def load_kg() -> List[Dict[str, Any]]:
    """Load the knowledge graph JSON file."""
    if not KG_PATH.exists():
        print(f"ERROR: {KG_PATH} not found!")
        sys.exit(1)
    
    print(f"Loading {KG_PATH} ({KG_PATH.stat().st_size / 1024 / 1024:.1f}MB)...")
    with open(KG_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✓ Loaded {len(data)} SPRs\n")
    return data

def show_stats(data: List[Dict[str, Any]]):
    """Show statistics about the KG."""
    print("=" * 60)
    print("KNOWLEDGE GRAPH STATISTICS")
    print("=" * 60)
    print(f"Total SPRs: {len(data)}")
    
    # Count by category
    categories = {}
    has_compression = 0
    has_narrative = 0
    total_size = 0
    
    for spr in data:
        cat = spr.get('category', 'Uncategorized')
        categories[cat] = categories.get(cat, 0) + 1
        
        if 'compression_stages' in spr:
            has_compression += 1
            stages = spr.get('compression_stages', [])
            for stage in stages:
                if isinstance(stage, dict) and stage.get('stage_name') == 'Narrative':
                    has_narrative += 1
                    break
        
        # Estimate size
        total_size += len(json.dumps(spr))
    
    print(f"\nCategories:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:10]:
        print(f"  {cat}: {count}")
    
    print(f"\nCompression Info:")
    print(f"  SPRs with compression_stages: {has_compression}")
    print(f"  SPRs with Narrative layer: {has_narrative}")
    print(f"  Estimated total content size: {total_size / 1024 / 1024:.1f}MB")
    print("=" * 60)

def search_sprs(data: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Search SPRs by ID, term, or definition."""
    query_lower = query.lower()
    results = []
    
    for spr in data:
        spr_id = spr.get('spr_id', '').lower()
        term = spr.get('term', '').lower()
        definition = spr.get('definition', '').lower()
        
        if query_lower in spr_id or query_lower in term or query_lower in definition:
            results.append(spr)
    
    return results

def view_spr(spr: Dict[str, Any], layer: Optional[str] = None):
    """View a specific SPR, optionally at a specific layer."""
    print("\n" + "=" * 60)
    print(f"SPR: {spr.get('spr_id', 'N/A')}")
    print("=" * 60)
    print(f"Term: {spr.get('term', 'N/A')}")
    print(f"Category: {spr.get('category', 'N/A')}")
    
    if layer:
        # Try to get content from specific layer
        stages = spr.get('compression_stages', [])
        for stage in stages:
            if isinstance(stage, dict) and stage.get('stage_name') == layer:
                content = stage.get('content', '')
                print(f"\n{layer} Layer Content ({len(content)} chars):")
                print("-" * 60)
                # Show first 2000 chars
                if len(content) > 2000:
                    print(content[:2000])
                    print(f"\n... (truncated, {len(content) - 2000} more chars)")
                else:
                    print(content)
                return
        
        print(f"\n⚠ Layer '{layer}' not found in compression_stages")
        print("Showing definition instead:")
    else:
        print("\nDefinition:")
    
    definition = spr.get('definition', 'N/A')
    if len(definition) > 2000:
        print(definition[:2000])
        print(f"\n... (truncated, {len(definition) - 2000} more chars)")
    else:
        print(definition)
    
    # Show compression info
    stages = spr.get('compression_stages', [])
    if stages:
        print(f"\nCompression Stages Available:")
        for stage in stages:
            if isinstance(stage, dict):
                stage_name = stage.get('stage_name', 'Unknown')
                content_len = len(stage.get('content', ''))
                ratio = stage.get('compression_ratio', 1.0)
                print(f"  - {stage_name}: {content_len:,} chars (ratio: {ratio:.2f}x)")

def list_sprs(data: List[Dict[str, Any]], limit: int = 50):
    """List SPR IDs with basic info."""
    print(f"\nFirst {limit} SPRs:")
    print("-" * 60)
    for i, spr in enumerate(data[:limit]):
        spr_id = spr.get('spr_id', 'N/A')
        term = spr.get('term', 'N/A')
        cat = spr.get('category', 'N/A')
        has_comp = "✓" if spr.get('compression_stages') else "✗"
        print(f"{i+1:4d}. {spr_id:30s} | {term[:30]:30s} | {cat:20s} | Comp: {has_comp}")

def main():
    """Main interactive loop."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "help"
    
    data = load_kg()
    
    if command == "stats":
        show_stats(data)
    
    elif command == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        list_sprs(data, limit)
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python3 view_large_kg.py search <query>")
            sys.exit(1)
        query = sys.argv[2]
        results = search_sprs(data, query)
        print(f"\nFound {len(results)} SPRs matching '{query}':")
        for spr in results[:20]:  # Show first 20
            print(f"  - {spr.get('spr_id', 'N/A')}: {spr.get('term', 'N/A')}")
        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more")
    
    elif command == "view":
        if len(sys.argv) < 3:
            print("Usage: python3 view_large_kg.py view <spr_id> [layer]")
            sys.exit(1)
        spr_id = sys.argv[2]
        layer = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Find SPR
        spr = None
        for s in data:
            if s.get('spr_id', '').lower() == spr_id.lower():
                spr = s
                break
        
        if not spr:
            print(f"ERROR: SPR '{spr_id}' not found!")
            sys.exit(1)
        
        view_spr(spr, layer)
    
    elif command == "layers":
        """Show all available compression layers across all SPRs."""
        all_layers = set()
        for spr in data:
            stages = spr.get('compression_stages', [])
            for stage in stages:
                if isinstance(stage, dict):
                    all_layers.add(stage.get('stage_name', 'Unknown'))
        print("\nAvailable Compression Layers:")
        for layer in sorted(all_layers):
            print(f"  - {layer}")
    
    elif command == "export":
        """Export specific SPR(s) to a smaller file."""
        if len(sys.argv) < 3:
            print("Usage: python3 view_large_kg.py export <spr_id1> [spr_id2] ...")
            sys.exit(1)
        
        spr_ids = sys.argv[2:]
        exported = []
        for spr_id in spr_ids:
            for spr in data:
                if spr.get('spr_id', '').lower() == spr_id.lower():
                    exported.append(spr)
                    break
        
        output_file = "exported_sprs.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(exported, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported {len(exported)} SPRs to {output_file}")
        print(f"  Size: {Path(output_file).stat().st_size / 1024:.1f}KB")
    
    else:
        print("""
KNOWLEDGE GRAPH VIEWER - Usage:

  python3 view_large_kg.py stats
    Show statistics about the KG

  python3 view_large_kg.py list [limit]
    List SPRs (default: 50)

  python3 view_large_kg.py search <query>
    Search SPRs by ID, term, or definition

  python3 view_large_kg.py view <spr_id> [layer]
    View a specific SPR (optionally at a specific layer)
    Layers: Narrative, Concise, Nano, Micro, Pico, Femto, Atto, Zepto

  python3 view_large_kg.py layers
    Show all available compression layers

  python3 view_large_kg.py export <spr_id1> [spr_id2] ...
    Export specific SPRs to a smaller JSON file

Examples:
  python3 view_large_kg.py stats
  python3 view_large_kg.py search "CFP"
  python3 view_large_kg.py view "ComparativE FluxuaL ProcessinG" Narrative
  python3 view_large_kg.py list 100
        """)

if __name__ == "__main__":
    main()

